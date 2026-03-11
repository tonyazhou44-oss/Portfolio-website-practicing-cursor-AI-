# Personal Portfolio — PDF-Based Projects

A cinematic-style portfolio site. Each project tile is an **entry button** that opens a dedicated project page built from your PDF content, with extracted images displayed in galleries.

## Files

- **index.html** — Homepage with hero, works grid, about, contact.
- **styles.css** — Full styling (header, hero, cards, case pages, galleries).
- **script.js** — Footer year, smooth scrolling, card tilt effect.
- **assets.js** — Loads `images/_extracted/manifest.json` and per-project `arrangement.json` to fill galleries. Supports reordering and custom/uploaded images per section.
- **projects/*.html** — Five project case studies (Gary Doug's House Defense, Oblivisci, Digital in Reality, Rubik's Cube — Inverse World, Pressgrow).
- **tools/pdf_extract_images.py** — Extracts embedded images from PDFs (no Pillow required for JPG/PNG).

## Viewing the site

Use a **local web server** (required for images to load):

```bash
cd /Users/zhoutonya
python3 -m http.server 8000
```


Then open **http://localhost:8000/** in your browser. Click any project to open its page; galleries are filled from each project’s **arrangement** (see below).

## Editing image order and uploading photos

Each project’s gallery is driven by **images/_extracted/&lt;slug&gt;/arrangement.json**. You can:

1. **Change order** — Edit the `images` array in the section you care about; the order in the array is the order shown on the page.
2. **Replace or add images** — Put new image files (e.g. PNG/JPG) in **images/_extracted/&lt;slug&gt/** and add their filenames to the right section’s `images` array in **arrangement.json**. You can remove or reorder existing filenames to swap in new photos.

Example: for “Digital in Reality” the file is **images/_extracted/digital-in-reality/arrangement.json**. Sections have ids like `digital-world`, `optical-variations`, `textures-motif`, `installation-design`. Reorder or add filenames under each section’s `images` list; any file in that folder can be referenced by name.

Slug folder names: `gary-doug-s-house-defense`, `oblivisci`, `digital-in-reality`, `rubik-s-cube-inverse-world`, `the-game-pressgrow`.

## Extracted images

Images are read from **images/_extracted/** using the manifest at **images/_extracted/manifest.json**. If you need to re-extract from your PDFs:

```bash
python3 tools/pdf_extract_images.py \
  "path/to/Gary Doug's House Defense.pdf" \
  "path/to/Oblivisci.pdf" \
  "path/to/Digital in Reality.pdf" \
  "path/to/Rubik's Cube-Inverse World.pdf" \
  "path/to/The Game Pressgrow.pdf" \
  --out images/_extracted \
  --manifest images/_extracted/manifest.json
```

Run from the project root (`/Users/zhoutonya`). Requires **pypdf** (`pip install pypdf`).

## Customize

- Edit **index.html** and each **projects/*.html** to replace “Your Name”, taglines, about/contact text, and links.
- Adjust colors, fonts, and layout in **styles.css**.

## Deploy

Upload the whole folder (index.html, styles.css, script.js, assets.js, projects/, images/_extracted/) to any static host (GitHub Pages, Netlify, Vercel, etc.).
