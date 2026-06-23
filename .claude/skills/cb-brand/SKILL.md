---
name: cb-brand
description: Cloud Beacon's visual brand identity — colors (navy/teal/gold palette), typography (Inter, JetBrains Mono), spacing, layout, and component patterns (headers, footers, section badges, tables, callouts, lists). Use this whenever designing, generating, or styling any Cloud Beacon-branded output — HTML pages, marketing sites, slide decks, Figma designs, SwiftUI views, CSS/Tailwind config, email templates, social graphics, internal tooling UIs, PDF/DOCX/PPTX deliverables, or anywhere the question "what color/font/component should I use here" comes up for a CB-facing artifact. Also trigger when asked to "match CB branding", "apply our colors", "use our brand", "make this look like Cloud Beacon", or when generating design tokens / Tailwind themes / CSS variables for any Cloud Beacon project.
---

# Cloud Beacon Brand Identity

The authoritative reference for visual identity across all Cloud Beacon deliverables. Use the exact values below — do not approximate or substitute.

## Color palette

### Primary (navy)

| Token        | Hex       | Usage                                                         |
| ------------ | --------- | ------------------------------------------------------------- |
| `navy`       | `#002B45` | Headers, primary backgrounds, headings, body text emphasis    |
| `navyDark`   | `#002C46` | Logo background, deep accent areas                            |

### Accent

| Token        | Hex       | Usage                                                              |
| ------------ | --------- | ------------------------------------------------------------------ |
| `teal`       | `#2DD4BF` | CTAs, highlights, checkmarks, accent borders, interactive elements |
| `tealHover`  | `#22D3EE` | Hover state for teal interactive elements                          |
| `gold`       | `#FCD19C` | Section numbers, labels, warm accents, badges                      |

### UI (dark surfaces)

| Token        | Hex       | Usage                                  |
| ------------ | --------- | -------------------------------------- |
| `inputBg`    | `#023E61` | Form input backgrounds on dark surfaces |
| `border`     | `#0B4A6F` | Form borders and dividers on dark surfaces |

### Neutrals

`white #FFFFFF` · `gray50 #F9FAFB` · `gray100 #F3F4F6` · `gray200 #E5E7EB` · `gray300 #D1D5DB` · `gray400 #9CA3AF` · `gray500 #6B7280` · `gray600 #4B5563` · `gray700 #374151` · `gray800 #1F2937` · `gray900 #111827`

## Typography

| Role        | Family            | Fallback              | Usage                                              |
| ----------- | ----------------- | --------------------- | -------------------------------------------------- |
| Body        | `Inter`           | `system-ui, sans-serif` | All body text, headings, UI elements             |
| Code        | `JetBrains Mono`  | `monospace`           | Code blocks, technical identifiers, monospace data |

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
- Background: `navyDark #002C46`
- Text: white
- Accent text (taglines, metadata): `gold #FCD19C`
- Layout: white Cloud Beacon logo (left), document title (right)

### Section heading
- Gold numbered badge (`#FCD19C` bg, `#002B45` text)
- Heading text: `navy #002B45`, uppercase, tracking-wide

### Footer
- Background: `gray50 #F9FAFB`
- Top border: `teal #2DD4BF`, **4px** width
- Contains company address and website

### Tables
- Header row: `navy #002B45` bg, white text
- Stripe rows: alternating white / `gray50 #F9FAFB`
- Borders: `gray200 #E5E7EB`

### Lists
- Bullet/check color: `teal #2DD4BF` (use checkmarks, not dots, for branded lists)

### Callouts / cards
- Background: `gray100 #F3F4F6`
- Border: `gray200 #E5E7EB`
- Border radius: `0.75rem`

### Code blocks
- Language badge: `navy #002B45` background
- Block background: `gray50 #F9FAFB`
- Font: `JetBrains Mono`

### Blockquotes
- Left border: `teal #2DD4BF`, 4px
- Background: `gray50 #F9FAFB`
- Style: italic

## Application rules

1. **Use the exact hex values** — never approximate. The brand depends on consistency across deliverables.
2. **Navy is structural, teal is interactive, gold is decorative.** Don't swap roles (e.g., don't make CTAs gold).
3. **Inter for everything readable, JetBrains Mono only for code/identifiers.** No third typeface.
4. **Headers always carry the logo + title pattern.** Don't strip the logo to "save space."
5. **Section numbering uses gold badges + navy uppercase text.** This is the signature CB section style — don't substitute solid backgrounds or sentence-case headings on numbered sections.
6. **Teal-checkmark bullets on featured lists.** Plain dots are fine for dense list content; checkmarks signal a curated/branded list.

## Generating tokens for a new project

When asked to produce a Tailwind config, CSS variables, design token JSON, Figma styles, or SwiftUI color/font constants, derive from the values above verbatim. Preserve the token names (`navy`, `teal`, `gold`, `navyDark`, etc.) so they're recognizable across Cloud Beacon codebases.
