---
name: cb-image-intake
description: Intake pipeline for putting images onto Cloud Beacon web properties — download from a URL (or a repo drop), inspect visually, crop/extend with sharp, emit responsive self-hosted variants, and wire srcSet. Use whenever the user provides an image URL or file for a website/portal ("use this image for X", "can you find images for the blog posts", customer logos/photos, favicons). Also covers sourcing stock imagery and the licensing flags to raise.
---

# cb-image-intake — images onto Cloud Beacon sites

## Ground rules

1. **Self-host.** Never hotlink customer/product images. Download → optimize → commit under `public/` (website convention: `public/customers/` for client imagery). Stock Unsplash hotlinks are the one established exception.
2. **Look at every image before using it.** Read the downloaded file (and any stock-photo ID you picked from memory — IDs are frequently wrong). Never wire an image sight-unseen.
3. **Flag provenance.** Note when a source is not the brand's official site (replica/fan sites), looks AI-generated, or is a press/third-party asset — in your reply AND the commit message. The user decides; you surface.
4. Chat-pasted images reach the agent as pixels, not files — ask for a URL or have the user drop the file into the repo (`updates/` works).

## Download

`Invoke-WebRequest` often gets 403'd. Use curl with browser headers (+ referer for hotlink protection):

```powershell
curl.exe -sSL -o "$scratch\img" -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36" -e "https://<source-site>/" "<image-url>"
```

To discover image URLs on a page, WebFetch it asking for img src / og:image / srcset URLs.

## Process with sharp

sharp lives in the website repo's node_modules; from a scratchpad script resolve it explicitly:
`const sharp = require('c:/.../Cloud-Beacon-Website/node_modules/sharp')`.

**Gotcha:** within a single sharp pipeline, `trim` runs BEFORE `extract` regardless of call order — use two passes (extract → buffer → trim) when cropping then trimming.

Standard recipes:

```js
// Responsive variants (quality 78–82, mozjpeg):
for (const w of [400, 600, 800, 1200]) 
  await sharp(src).resize(Math.min(w, meta.width)).jpeg({ quality: 78, mozjpeg: true })
    .toFile(`public/customers/<slug>-${w}.jpg`);   // never upscale past native width

// Crop a region (e.g. "use the right half"):
sharp(src).extract({ left: 960, top: 0, width: 960, height: 545 })

// Extend to an aspect ratio instead of cropping (white-background product shots):
sharp(src).extend({ top, bottom, background: { r:255,g:255,b:255 } })  // compute pads for 4:3

// Recolor a single-color mark (e.g. white version of the logo): iterate raw RGBA,
// set RGB to target, keep alpha for antialiasing.
```

Naming: `<slug>-<width>.jpg` under `public/customers/`. Wire as
`image: '/customers/<slug>-600.jpg'` + explicit `imageSrcSet` listing each variant with `Nw` descriptors. Above-the-fold images: `fetchPriority="high"`; below: `loading="lazy" decoding="async"`.

## Stock imagery (blog headers, heroes)

- Unsplash URLs in the site's established format: `https://images.unsplash.com/photo-<id>?w=1200&q=80&auto=format&fit=crop`; the site's `unsplashSrcSet`/`responsiveSrcSet` helpers (components/utils/image.ts) rewrite `w=`.
- Download each candidate at `w=400` and VIEW it — assign to topics only after seeing them.

## Favicons / app icons

Canonical Cloud Beacon icon set lives in `cloud-beacon-tools/portal/app/` (navy square, white mark: icon.png, apple-icon.png, favicon.ico). Copy those files; derive sizes with sharp resize (32 tab, 192 android, 180 apple-touch). Don't design new variants. Remind the user that favicons cache hard (hard refresh / private window after deploy).
