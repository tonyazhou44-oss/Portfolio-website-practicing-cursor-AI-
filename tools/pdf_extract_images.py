"""
Extract embedded images from PDFs into images/_extracted/<slug>/.
Uses pypdf only (no Pillow). Run from project root:

  python3 tools/pdf_extract_images.py path/to/file1.pdf path/to/file2.pdf --out images/_extracted
"""

import os
import re
import struct
import zlib
from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

from pypdf import PdfReader


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "pdf"


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(chunk_type)
    crc = zlib.crc32(data, crc) & 0xFFFFFFFF
    return struct.pack("!I", len(data)) + chunk_type + data + struct.pack("!I", crc)


def write_png(
    out_path: str,
    width: int,
    height: int,
    channels: int,
    bit_depth: int,
    raw: bytes,
) -> None:
    if bit_depth != 8:
        raise ValueError(f"Unsupported bit depth: {bit_depth}")
    if channels not in (1, 3, 4):
        raise ValueError(f"Unsupported channels: {channels}")

    color_type = {1: 0, 3: 2, 4: 6}[channels]
    stride = width * channels
    expected = stride * height
    if len(raw) < expected:
        raise ValueError(f"Raw buffer too small: {len(raw)} < {expected}")
    raw = raw[:expected]

    scanlines = bytearray()
    offset = 0
    for _ in range(height):
        scanlines.append(0)
        scanlines.extend(raw[offset : offset + stride])
        offset += stride

    compressed = zlib.compress(bytes(scanlines), level=9)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack("!IIBBBBB", width, height, bit_depth, color_type, 0, 0, 0)
    data = (
        sig
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", compressed)
        + _png_chunk(b"IEND", b"")
    )

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(data)


def _name_from_filter(filters: Iterable[str]) -> str:
    if any("DCTDecode" in f for f in filters):
        return "jpg"
    if any("JPXDecode" in f for f in filters):
        return "jp2"
    return "png"


def _extract_filters(xobj) -> Tuple[str, ...]:
    flt = xobj.get("/Filter")
    if flt is None:
        return tuple()
    if isinstance(flt, list):
        return tuple(str(x) for x in flt)
    return (str(flt),)


def _channels_from_colorspace(cs) -> Optional[int]:
    s = str(cs)
    if "DeviceRGB" in s:
        return 3
    if "DeviceGray" in s:
        return 1
    if "DeviceCMYK" in s:
        return 4
    return None


@dataclass
class ExtractedImage:
    page_index: int
    image_index: int
    path: str
    ext: str


def extract_images(pdf_path: str, out_dir: str) -> list:
    reader = PdfReader(pdf_path)
    results = []

    base = os.path.splitext(os.path.basename(pdf_path))[0]
    slug = slugify(base)

    for page_i, page in enumerate(reader.pages):
        resources = page.get("/Resources") or {}
        xobjects = resources.get("/XObject") or {}
        if not xobjects:
            continue

        img_i = 0
        for name, obj in xobjects.items():
            try:
                xobj = obj.get_object()
            except Exception:
                continue
            if xobj.get("/Subtype") != "/Image":
                continue

            img_i += 1
            filters = _extract_filters(xobj)
            ext = _name_from_filter(filters)

            out_path = os.path.join(
                out_dir,
                slug,
                f"page-{page_i+1:02d}-img-{img_i:02d}.{ext}",
            )

            try:
                if ext in ("jpg", "jp2"):
                    data = xobj.get_data()
                    os.makedirs(os.path.dirname(out_path), exist_ok=True)
                    with open(out_path, "wb") as f:
                        f.write(data)
                else:
                    width = int(xobj.get("/Width"))
                    height = int(xobj.get("/Height"))
                    bpc = int(xobj.get("/BitsPerComponent") or 8)
                    cs = xobj.get("/ColorSpace")
                    channels = _channels_from_colorspace(cs) if cs is not None else None
                    if channels is None:
                        continue
                    raw = xobj.get_data()
                    write_png(out_path, width, height, channels, bpc, raw)
            except Exception:
                continue

            results.append(
                ExtractedImage(
                    page_index=page_i,
                    image_index=img_i,
                    path=out_path,
                    ext=ext,
                )
            )

    return results


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Extract images from PDFs (no Pillow).")
    parser.add_argument("pdf", nargs="+", help="PDF paths")
    parser.add_argument("--out", default="images/_extracted", help="Output directory")
    parser.add_argument("--manifest", default="images/_extracted/manifest.json", help="Write JSON manifest")
    args = parser.parse_args()

    all_results = {}
    for pdf_path in args.pdf:
        res = extract_images(pdf_path, args.out)
        all_results[pdf_path] = [r.__dict__ for r in res]

    os.makedirs(os.path.dirname(args.manifest), exist_ok=True)
    with open(args.manifest, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"Wrote manifest to {args.manifest}")


if __name__ == "__main__":
    main()
