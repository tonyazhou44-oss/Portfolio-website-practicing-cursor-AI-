/** Base path for GitHub Pages project site (e.g. /Portfolio-website-practicing-cursor-AI-). Empty when local or at repo root. */
function getBasePath() {
  if (typeof location === "undefined" || !location.pathname) return "";
  const segs = location.pathname.split("/").filter(Boolean);
  if (segs.length >= 1 && segs[0] && segs[0] !== "projects") return "/" + segs[0];
  return "";
}

async function loadPdfManifest(manifestPath) {
  const res = await fetch(manifestPath, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to load manifest: ${res.status}`);
  return res.json();
}

async function loadArrangement(slug) {
  const base = getBasePath();
  const path = base ? `${base}/images/_extracted/${slug}/arrangement.json` : `../images/_extracted/${slug}/arrangement.json`;
  const res = await fetch(path, { cache: "no-store" });
  if (!res.ok) return null;
  return res.json();
}

function parsePageAndIndex(filePath) {
  const m = filePath.match(/page-(\d+)-img-(\d+)\./i);
  if (!m) return { page: 0, index: 0 };
  return { page: Number(m[1]), index: Number(m[2]) };
}

function buildImageFigure(src, caption) {
  const fig = document.createElement("figure");
  const img = document.createElement("img");
  img.loading = "lazy";
  img.decoding = "async";
  img.src = src;
  img.alt = caption || "Project image";
  fig.appendChild(img);
  if (caption) {
    const cap = document.createElement("figcaption");
    cap.textContent = caption;
    fig.appendChild(cap);
  }
  return fig;
}

function sortPathsInPdfOrder(paths) {
  return paths.slice().sort((a, b) => {
    const pa = parsePageAndIndex(a);
    const pb = parsePageAndIndex(b);
    return pa.page - pb.page || pa.index - pb.index || a.localeCompare(b);
  });
}

function renderInlineGallery(container, relPaths) {
  const wrap = document.createElement("div");
  wrap.className = "case-gallery case-gallery-inline";
  for (const rel of relPaths) {
    wrap.appendChild(buildImageFigure(rel, ""));
  }
  container.appendChild(wrap);
}

function renderGroupedGallery(container, relPaths) {
  const sorted = sortPathsInPdfOrder(relPaths);
  const groups = new Map();
  for (const rel of sorted) {
    const { page } = parsePageAndIndex(rel);
    if (!groups.has(page)) groups.set(page, []);
    groups.get(page).push(rel);
  }
  const pages = Array.from(groups.keys()).sort((a, b) => a - b);
  for (const page of pages) {
    const section = document.createElement("section");
    section.className = "pdf-page";
    const title = document.createElement("h4");
    title.className = "pdf-page-title";
    title.textContent = page ? `PDF page ${page}` : "PDF images";
    section.appendChild(title);
    const grid = document.createElement("div");
    grid.className = "case-gallery";
    for (const rel of groups.get(page)) {
      grid.appendChild(buildImageFigure(rel, ""));
    }
    section.appendChild(grid);
    container.appendChild(section);
  }
}

/** Render one section from arrangement.json: images only (no heading) */
function renderArrangementSection(container, slug, section) {
  if (!section || !section.images || section.images.length === 0) return;
  const base = getBasePath();
  const baseUrl = base ? `${base}/images/_extracted/${slug}/` : `../images/_extracted/${slug}/`;
  const wrap = document.createElement("div");
  wrap.className = "case-gallery case-gallery-inline";
  for (const filename of section.images) {
    const src = baseUrl + filename;
    wrap.appendChild(buildImageFigure(src, ""));
  }
  container.appendChild(wrap);
}

document.addEventListener("DOMContentLoaded", async () => {
  const containers = document.querySelectorAll("[data-pdf-gallery-slug]");
  if (!containers.length) return;

  const manifestPath =
    document.documentElement.getAttribute("data-manifest-path") ||
    (getBasePath() ? getBasePath() + "/images/_extracted/manifest.json" : "../images/_extracted/manifest.json");

  let manifest;
  try {
    manifest = await loadPdfManifest(manifestPath);
  } catch (e) {
    containers.forEach((c) => {
      c.textContent = "Could not load images. Run with a local server (e.g. python3 -m http.server 8000).";
    });
    return;
  }

  const allOutPaths = [];
  for (const key of Object.keys(manifest)) {
    const entries = manifest[key] || [];
    for (const entry of entries) {
      if (entry && entry.path) allOutPaths.push(String(entry.path));
    }
  }

  for (const container of containers) {
    const slug = container.getAttribute("data-pdf-gallery-slug");
    if (!slug) continue;

    const useArrangement = container.getAttribute("data-pdf-arrangement") === "true";
    const sectionId = container.getAttribute("data-pdf-section");

    if (useArrangement && sectionId) {
      const arrangement = await loadArrangement(slug);
      if (arrangement && arrangement.sections) {
        const section = arrangement.sections.find((s) => s.id === sectionId);
        renderArrangementSection(container, slug, section);
        continue;
      }
    }

    let relPaths = allOutPaths
      .filter((abs) => abs.includes(`/images/_extracted/${slug}/`))
      .map((abs) => {
        const after = abs.replace(/^.*\/images\//, "");
        return getBasePath() ? getBasePath() + "/images/" + after : "../images/" + after;
      });

    if (!relPaths.length) {
      container.textContent = "No images for this project.";
      continue;
    }

    relPaths = sortPathsInPdfOrder(relPaths);

    const startAttr = container.getAttribute("data-pdf-start");
    const endAttr = container.getAttribute("data-pdf-end");
    const start = startAttr != null ? parseInt(startAttr, 10) : null;
    const end = endAttr != null ? parseInt(endAttr, 10) : null;

    if (start != null && !isNaN(start)) {
      const oneBasedStart = Math.max(1, start);
      const oneBasedEnd = end != null && !isNaN(end) ? Math.min(relPaths.length, end) : relPaths.length;
      const slice = relPaths.slice(oneBasedStart - 1, oneBasedEnd);
      if (slice.length) renderInlineGallery(container, slice);
    } else {
      renderGroupedGallery(container, relPaths);
    }
  }
});
