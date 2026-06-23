---
name: docx-survival
description: Hard-won gotchas for the `docx` npm package (v9.x) when generating Word documents from Node or browser. Use this whenever code imports from `docx` (`import { Document, Paragraph, TextRun, ImageRun, ... } from 'docx'`), builds or modifies .docx export logic, embeds images or SVGs into Word documents, sets hyperlinks/underlines/styles in DOCX, or debugs "Word found unreadable content" / "The file is corrupt and cannot be opened" / corrupted-file errors after generating a .docx. Also trigger when the user is writing a DOCX exporter, converting markdown/HTML/IR to DOCX, or hits OOXML validation errors and isn't sure where to start.
---

# DOCX Survival Guide (`docx` npm v9.x)

The `docx` library produces OOXML, which Word validates strictly. Bugs here mean "Word found unreadable content" with no useful error. These rules come from incident debugging — follow them exactly.

## 1. `ImageRun` requires a `type` field

**Symptom:** Generated `.docx` opens with "unreadable content." Inspecting the file shows media stored with `.undefined` extension.

**Rule:** Every `ImageRun` MUST include `type` — one of `"png" | "jpg" | "gif" | "bmp"`. There is no default; omitting it produces invalid OOXML.

```ts
// WRONG — produces unreadable .docx
new ImageRun({
  data: imageBytes,
  transformation: { width: 400, height: 300 },
});

// RIGHT
new ImageRun({
  type: 'png',                          // ← required
  data: imageBytes,
  transformation: { width: 400, height: 300 },
});
```

If the source is a data URL, detect the type from the MIME prefix (`data:image/png;...` → `'png'`).

## 2. SVG → PNG must go through a data URL, not a Blob URL

**Symptom:** Tainted canvas `SecurityError` when calling `canvas.toBlob()` or `canvas.toDataURL()` after drawing an SVG image.

**Rule:** Load SVG into the canvas via a `data:image/svg+xml` URL, not `URL.createObjectURL(blob)`. Blob URLs taint the canvas under the SVG image element's CORS rules.

```ts
// WRONG — taints canvas, throws SecurityError on export
const blobUrl = URL.createObjectURL(new Blob([svgString], { type: 'image/svg+xml' }));
img.src = blobUrl;

// RIGHT
const dataUrl =
  'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgString);
img.src = dataUrl;
```

## 3. Never spread an existing `TextRun` into a new `TextRun`

**Symptom:** Generated file fails OOXML validation; opens with "unreadable content" or shows duplicated/garbled formatting.

**Rule:** `TextRun` instances carry internal compiled properties that are not safe to copy. Always construct a fresh `TextRun` from raw values.

```ts
// WRONG — copies internal compiled properties → invalid XML
const boldRun = new TextRun({ ...existingRun, bold: true });

// RIGHT — extract raw values, build a new instance
const boldRun = new TextRun({
  text: existingText,
  bold: true,
  italics: existingItalic,
  color: existingColor,
});
```

## 4. Don't use `style: 'Hyperlink'` on a `TextRun`

**Symptom:** Generated file is corrupt. Known docx library bug ([#3220](https://github.com/dolanmiu/docx/issues/3220)) — emits XML elements in the wrong order.

**Rule:** Style hyperlinks explicitly with `color` and `underline` instead of relying on the named style.

```ts
// WRONG — emits invalid OOXML element order
new TextRun({ text: 'click here', style: 'Hyperlink' });

// RIGHT
new TextRun({
  text: 'click here',
  color: '0563C1',
  underline: { type: UnderlineType.SINGLE },
});
```

## 5. Use the `UnderlineType` enum, not the string `'single'`

**Symptom:** Underline silently dropped, or runtime warning.

**Rule:** Import `UnderlineType` and use the enum member. Don't pass the string literal.

```ts
import { UnderlineType } from 'docx';

// WRONG
underline: { type: 'single' }

// RIGHT
underline: { type: UnderlineType.SINGLE }
```

## Quick checklist before shipping a DOCX exporter

- [ ] Every `ImageRun` has a `type` field matching the bytes.
- [ ] SVG sources are loaded via `data:` URLs, not `blob:` URLs.
- [ ] No spread of existing `TextRun` instances — always fresh construction.
- [ ] No `style: 'Hyperlink'` on `TextRun`. Manual color + underline instead.
- [ ] `UnderlineType` enum used everywhere underlines are set.
- [ ] Test the output by **actually opening it in Word** — `unzip -l file.docx` won't catch validation errors that only Word surfaces.

## Debugging "unreadable content"

When Word reports unreadable content, in order:

1. Rename `.docx` → `.zip` and `unzip -l` it. Look for `.undefined` extensions in the media folder — that's the `ImageRun` type bug.
2. Open `word/document.xml` and look for hyperlink-related elements with unusual nesting order — that's the `style: 'Hyperlink'` bug.
3. Diff a known-good run against the failing one to localize which `TextRun` is malformed — likely a spread-from-existing somewhere.
