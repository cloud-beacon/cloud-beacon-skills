---
name: cb-photo-background
description: Replace or recolor a photo's background (headshots, product shots) to a flat brand color using ML person/subject segmentation — the technique that put Caroline's founder headshot on cb-teal to match Chad's. Use when the user asks to change/match/remove an image background ("recolor the background", "make the backgrounds match", "put this on brand navy"). Color-threshold hacks are NOT reliable for portraits; go straight to segmentation.
---

# cb-photo-background — flat brand-color backgrounds via segmentation

## When and why

Matching founder headshots / product photos to a flat brand color
(cb-teal `#00cad1` = rgb(0,202,209), cb-navy `#002c47`). Proven on the
website founder photos: Chad's headshot came with flat #00cad1; Caroline's
off-white background was replaced to match.

**Do not try color-threshold / flood-fill keying on portraits.** Both failure
modes were hit in practice:
- Local-continuity flood fill leaks through smooth skin/hair gradients
  (98% of the image masked as "background").
- Global color gates (cool-vs-warm tint, low chroma) eat clothing that
  shares the background's tint and leave ragged unfilled islands.
Fabric, shadow gradients, and hair wisps make thresholds a losing game —
segmentation gets it right the first time.

## Recipe (Node, no Python needed)

This machine has no Python/rembg. Use `@imgly/background-removal-node`
in a **scratchpad** npm project (never install it into a website repo):

```powershell
Set-Location $scratchpad
npm init -y | Out-Null
npm install @imgly/background-removal-node --no-audit --no-fund
# first run downloads the ONNX model (~40 MB) automatically
```

```js
const { removeBackground } = require('@imgly/background-removal-node');
const sharp = require('sharp'); // scratchpad-local copy — see gotcha 1
const fs = require('fs');

const SRC = 'c:/.../public/team/Photo.jpg';
const BRAND = { r: 0, g: 202, b: 209 }; // cb-teal

(async () => {
  // gotcha 2: pass a Blob — a Windows path is parsed as a URL ("Unsupported protocol: c:")
  const srcBlob = new Blob([fs.readFileSync(SRC)], { type: 'image/jpeg' });
  const blob = await removeBackground(srcBlob, { output: { format: 'image/png' } });
  const cutout = Buffer.from(await blob.arrayBuffer());
  const { width, height } = await sharp(cutout).metadata();
  await sharp({ create: { width, height, channels: 3, background: BRAND } })
    .composite([{ input: cutout }])
    .jpeg({ quality: 92 })
    .toFile('out.jpg');
})();
```

## Gotchas (each cost a failed run)

1. **sharp DLL conflict.** Requiring the website repo's sharp from a process
   that also loads imgly's own sharp fails with `ERR_DLOPEN_FAILED`. Use the
   scratchpad-local `require('sharp')` (imgly brings it as a dependency).
2. **Blob input on Windows.** `removeBackground('c:/path.jpg')` throws
   `Unsupported protocol: c:` — the path is URL-parsed. Always pass a Blob.
3. **Verify visually before shipping.** Read the output image and check the
   three usual casualties: hair wisps (halo), clothing edges, jewelry.
   Compare side-by-side against the photo it must match.
4. **Same filename = cached.** If the output overwrites an existing site
   asset, tell the user a hard refresh / private window is needed to see it.

## Sampling the target color

Don't guess the brand color from memory — sample the reference photo's
corner pixels first (`sharp(ref).raw()`, read a few edge offsets). Chad's
headshot measured exactly rgb(0,202,209) = cb-teal, which is what made the
match exact.

## Related

- `cb-image-intake` — download/inspect/responsive-variant pipeline; this
  skill is the background-replacement step within that flow.
- Brand palette: `cloud-beacon-brand` skill (cb-teal #00cad1, cb-navy #002c47,
  cb-yellow #ffcc61).
