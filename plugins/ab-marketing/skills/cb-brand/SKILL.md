---
name: cb-brand
description: Alta Beacon's visual brand identity — colors (navy/teal/gold palette), typography (Plus Jakarta Sans, JetBrains Mono), logo lockups, spacing, layout, and component patterns (headers, footers, section badges, tables, callouts, lists). Use this whenever designing, generating, or styling any Alta Beacon-branded output — HTML pages, marketing sites, slide decks, Figma designs, SwiftUI views, CSS/Tailwind config, email templates, social graphics, internal tooling UIs, PDF/DOCX/PPTX deliverables, or anywhere the question "what color/font/component should I use here" comes up for a client-facing or internal artifact. Also trigger when asked to "match our branding", "apply our colors", "use our brand", "make this look like Alta Beacon", or when generating design tokens / Tailwind themes / CSS variables for any Alta Beacon project.
---

# Alta Beacon Brand Identity

The authoritative reference for visual identity across all Alta Beacon deliverables. Use the exact values below — do not approximate or substitute.

**The company is Alta Beacon** (formerly Cloud Beacon). The legal entity is **Alta Beacon LLC**, a Delaware LLC. Tagline: **D365 Done Right**.

Write the name as **two words — "Alta Beacon"** in all prose, headings, and document text. "AltaBeacon" as one word is only acceptable inside identifiers that cannot take a space (a slug, a handle, a filename). The live site currently mixes both; two words is correct.

> **Related skill — read both.** `alta-beacon-brand` is the **web layer**: the live
> site's component vocabulary (navy cards, icon-on-glass, journey spine, capsule
> diagrams), interaction language, and the canonical CTA. This skill is the
> **identity layer**: name, logo, palette, type, and the print/document system
> (A4, margins, header banners, tables). They must not disagree on a value. Where
> they ever do, the live site wins, because that is the brand as shipped.
>
> **Note on the skill id.** This skill is still called `cb-brand`, and sibling skills keep their `cb-` prefixes. Those are internal identifiers referenced across agent definitions, deliberately left alone so cross-references don't break. They are not brand surfaces.

## Logo

Five full lockups ship in `assets/`, all horizontal, plus two mark-only files. There is no stacked lockup — do not fabricate one by re-stacking the wordmark. There is no purpose-built square app icon; see the note below.

| File | Background it goes on | Wordmark | Plate |
| ---- | --------------------- | -------- | ----- |
| `alta-beacon.svg` / `.png` | Light — white or `gray50` pages | Navy "Alta" + teal "Beacon", navy peak | none (transparent) |
| `alta-beacon-reversed.svg` / `.png` | **Any** dark surface — navy, photographic, a client's dark brand color | White "Alta" + teal "Beacon", white peak | none (transparent) |
| `alta-beacon-reversed-on-navy.svg` / `.png` | Use when you want the navy plate baked in, tight crop | White + teal | solid navy `#002C47` |
| `alta-beacon-on-navy.svg` / `.png` | Same, with generous padding around the lockup | White + teal | solid navy `#002C47` |
| `alta-beacon-on-white.svg` / `.png` | A white plate baked in, generous padding | Navy + teal | solid white |

**Mark only — no wordmark.** Use where the name already appears beside the logo (a nav
bar whose title reads "Alta Beacon Tools", a sign-in heading above the mark), or where a
full lockup is too wide to stay legible. These were extracted from the official artwork
as vector paths, so the geometry is the designer's — not a crop of a raster.

| File | Background it goes on | Colors |
| ---- | --------------------- | ------ |
| `alta-beacon-mark.svg` / `.png` | Light | Navy `#002C47` peak, teal peak, gold sun |
| `alta-beacon-mark-reversed.svg` / `.png` | Dark | White peak, teal peak, gold sun |

Both are `327 × 252`, very slightly wider than tall. Set width and height to that ratio
or the peaks skew. On navy, the dark variant's navy peak disappears — use the reversed one.

**Only the first two are transparent.** The three plated files carry a full-bleed background rect, so dropping `alta-beacon-on-navy` onto anything that is not `#002C47` shows a navy block. Check which you need before placing.

`alta-beacon-logo-sheet.pdf` is the full sheet. The `.ai` source lives in the website repo under `updates/Final/`.

**Square app icons.** There is still no purpose-built square icon, but the mark files
above are the correct basis for one: center `alta-beacon-mark-reversed.svg` on a navy
`#002C47` square, or `alta-beacon-mark.svg` on white, with even padding. Do not crop a
*lockup* to fake an icon, and do not recolor or re-proportion the mark to make it fill
a square.

The mark is two mountain peaks (navy and teal) under a gold sun. **Never recolor the mark, re-space the wordmark, or separate the peaks from the sun.** Pick the lockup whose background matches — putting the transparent reversed logo on a white page renders it invisible.

## Color palette

Taken from the final logo artwork and the live site. These are the real values.

### Primary (navy)

| Token  | Hex       | Usage                                                      |
| ------ | --------- | ---------------------------------------------------------- |
| `navy` | `#002C47` | Headers, primary backgrounds, headings, body text emphasis |

### Accent

| Token      | Hex       | Usage                                                              |
| ---------- | --------- | ------------------------------------------------------------------ |
| `teal`     | `#00CAD1` | CTAs, highlights, checkmarks, accent borders, interactive elements |
| `tealDeep` | `#006F74` | Teal **text** on light backgrounds, and hover states                |
| `gold`     | `#FFCC61` | Section numbers, labels, warm accents, badges                       |

**Contrast rule:** `teal #00CAD1` is a bright cyan — roughly 2.1:1 on white, so it **fails contrast as text on light backgrounds**. It is fine as a fill, border, icon, or checkmark. When teal must carry words on white, use `tealDeep #006F74`. On navy, `teal` measures ~7.4:1 and is correct for text. `gold #FFCC61` is worse still (~1.5:1 on white) — gold text belongs on a navy pill or chip, never bare on white.

**One approved exception (Chad, 2026-07-07):** large bold *display headlines* on white may use bright `teal` for brand fidelity, accepting the contrast miss. Never extend this to body text, links, labels, or eyebrows.

### UI (dark surfaces)

| Token     | Hex       | Usage                                       |
| --------- | --------- | ------------------------------------------- |
| `inputBg` | `#023E61` | Form input backgrounds on dark surfaces     |
| `border`  | `#0B4A6F` | Form borders and dividers on dark surfaces  |

### Neutrals

`white #FFFFFF` · `gray50 #F9FAFB` · `gray100 #F3F4F6` · `gray200 #E5E7EB` · `gray300 #D1D5DB` · `gray400 #9CA3AF` · `gray500 #6B7280` · `gray600 #4B5563` · `gray700 #374151` · `gray800 #1F2937` · `gray900 #111827`

## Typography

| Role | Family                 | Fallback                        | Usage                                              |
| ---- | ---------------------- | ------------------------------- | -------------------------------------------------- |
| Body | `Plus Jakarta Sans`    | `ui-sans-serif, system-ui`      | All body text, headings, UI elements               |
| Code | `JetBrains Mono`       | `monospace`                     | Code blocks, technical identifiers, monospace data |

**Plus Jakarta Sans is the brand face.** Self-host the variable font via
`@fontsource-variable/plus-jakarta-sans` — never link it from Google Fonts.
Use `Inter` only as a substitute in a pipeline that genuinely cannot embed
Plus Jakarta Sans (some DOCX/PPTX toolchains); it is a fallback, not the brand.

**Weights:** light 300 · regular 400 · medium 500 · semibold 600 · bold 700

**Scale (Tailwind-aligned):**
- `xs` 0.75rem / 1rem
- `sm` 0.875rem / 1.25rem
- `base` 1rem / 1.5rem
- `lg` 1.125rem / 1.75rem
- `xl` 1.25rem / 1.75rem
- `2xl` 1.5rem / 2rem
- `3xl` 1.875rem / 2.25rem
- `4xl` 2.25rem / 2.5rem

## Spacing & layout

- **Page margin:** `15mm`
- **Section gap:** `3rem`
- **Paragraph gap:** `1rem`
- **List item gap:** `0.75rem`
- **Header padding:** `3rem`
- **Content padding:** `15mm`
- **Max content width:** `210mm` (A4)
- **Page size:** A4
- **Print margin:** `8mm`

## Component patterns

### Header banner
- Background: `navy #002C47`
- Text: white
- Accent text (taglines, metadata): `gold #FFCC61`
- Layout: `alta-beacon-reversed.svg` (left), document title (right)

### Section heading
- Gold numbered badge (`#FFCC61` bg, `#002C47` text)
- Heading text: `navy #002C47`, uppercase, tracking-wide

### Footer
- Background: `gray50 #F9FAFB`
- Top border: `teal #00CAD1`, **4px** width
- Contains company address and website

### Tables
- Header row: `navy #002C47` bg, white text
- Stripe rows: alternating white / `gray50 #F9FAFB`
- Borders: `gray200 #E5E7EB`

### Lists
- Bullet/check color: `teal #00CAD1` (use checkmarks, not dots, for branded lists)

### Callouts / cards
- Background: `gray100 #F3F4F6`
- Border: `gray200 #E5E7EB`
- Border radius: `0.75rem`

### Code blocks
- Language badge: `navy #002C47` background
- Block background: `gray50 #F9FAFB`
- Font: `JetBrains Mono`

### Blockquotes
- Left border: `teal #00CAD1`, 4px
- Background: `gray50 #F9FAFB`
- Style: italic

## Application rules

1. **Use the exact hex values** — never approximate. The brand depends on consistency across deliverables.
2. **Navy is structural, teal is interactive, gold is decorative.** Don't swap roles (e.g., don't make CTAs gold).
3. **Teal text on light backgrounds uses `tealDeep`** — except the approved display-headline exception above. This is the single easiest way to ship something that looks wrong.
4. **Plus Jakarta Sans for everything readable, JetBrains Mono only for code/identifiers.** No third typeface.
5. **Headers always carry the logo + title pattern.** Don't strip the logo to "save space," and match the lockup to its background.
6. **Section numbering uses gold badges + navy uppercase text.** This is the signature section style — don't substitute solid backgrounds or sentence-case headings on numbered sections.
7. **Teal-checkmark bullets on featured lists.** Plain dots are fine for dense list content; checkmarks signal a curated/branded list.
8. **The name is "Alta Beacon," two words.** Never "Cloud Beacon" on anything new.

## Generating tokens for a new project

When asked to produce a Tailwind config, CSS variables, design token JSON, Figma styles, or SwiftUI color/font constants, derive from the values above verbatim. Preserve the token names (`navy`, `teal`, `tealDeep`, `gold`, etc.) so they're recognizable across Alta Beacon codebases.
