#!/usr/bin/env python3
"""
Make white/near-white backgrounds transparent in images under images/_extracted/.
Saves as PNG (overwrites .png, converts .jpg to .png and updates manifest).
Requires: pip install Pillow
"""

import json
import os
import sys

try:
    from PIL import Image
except ImportError:
    print("Please install Pillow: pip install Pillow", file=sys.stderr)
    sys.exit(1)

EXTRACTED_DIR = os.path.join(os.path.dirname(__file__), "..", "images", "_extracted")
MANIFEST_PATH = os.path.join(EXTRACTED_DIR, "manifest.json")

# Pixels with R,G,B all >= this become transparent (0-255)
WHITE_THRESHOLD = 250
# Or use a fuzz: consider (R,G,B) as white if sum of distances from 255 is small
FUZZ = 15  # max (255-R) + (255-G) + (255-B) to treat as white


def is_white(pixel, threshold=WHITE_THRESHOLD):
    if len(pixel) == 4:
        r, g, b, a = pixel
    else:
        r, g, b = pixel
    return r >= threshold and g >= threshold and b >= threshold


def make_white_transparent(img):
    img = img.convert("RGBA")
    data = img.getdata()
    new_data = []
    for item in data:
        if is_white(item):
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    return img


def main():
    if not os.path.isdir(EXTRACTED_DIR):
        print(f"Not found: {EXTRACTED_DIR}", file=sys.stderr)
        sys.exit(1)

    manifest_changed = False
    manifest = {}
    if os.path.isfile(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)

    count = 0
    for root, _dirs, files in os.walk(EXTRACTED_DIR):
        for name in files:
            low = name.lower()
            if not (low.endswith(".jpg") or low.endswith(".jpeg") or low.endswith(".png")):
                continue
            path = os.path.join(root, name)
            try:
                img = Image.open(path)
                if img.mode == "P" and "transparency" in img.info:
                    # Already has transparency
                    continue
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                out_path = os.path.splitext(path)[0] + ".png"
                made = make_white_transparent(img)
                made.save(out_path, "PNG")
                if path != out_path:
                    os.remove(path)
                    manifest_changed = True
                else:
                    manifest_changed = True  # we still may need to update ext in manifest
                count += 1
            except Exception as e:
                print(f"Skip {path}: {e}", file=sys.stderr)

    if manifest_changed and manifest:
        for key in manifest:
            entries = manifest[key]
            for ent in entries:
                if ent.get("path", "").endswith(".jpg") or ent.get("path", "").endswith(".jpeg"):
                    ent["path"] = ent["path"][: ent["path"].rfind(".")] + ".png"
                    ent["ext"] = "png"
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print("Updated manifest to .png paths")

    print(f"Processed {count} images; white backgrounds set to transparent, saved as PNG.")


if __name__ == "__main__":
    main()
