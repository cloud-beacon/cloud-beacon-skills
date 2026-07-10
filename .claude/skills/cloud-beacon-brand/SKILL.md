---
name: cloud-beacon-brand
description: Cloud Beacon's design system, palette, component motifs, and copy voice — distilled from the cloudbeacon.com build (July 2026). Use whenever creating or restyling ANY Cloud Beacon-branded artifact — web pages, dashboards, claude.ai artifacts, slide decks, documents, portal tools, emails, diagrams — so it matches the website's look, feel, and voice. Read BEFORE picking colors, styling components, or writing marketing copy for anything Cloud Beacon.
---

# Cloud Beacon Brand System

Canonical reference: the live site (https://www.dynamicschad.com, production cloudbeacon.com) and the Cloud-Beacon-Website repo (`src/styles/global.css` for tokens, `CLAUDE.md` for repo-specific rules).

## Palette

| Token | Hex | Role |
|---|---|---|
| `cb-navy` | `#002c47` | Primary brand. Section backgrounds, cards, headings on light. |
| `cb-teal` | `#00cad1` | Bright accent. Interactive text hover, icons/accents ON NAVY, subheadings on navy. |
| `cb-teal-dark` | `#006f74` | Derived (not a logo color). Small teal text on white/light backgrounds. |
| `cb-yellow` | `#ffcc61` | Emphasis. CTA buttons, icons, step numbers, spine/nodes. |
| `cb-light` | `#f8fafc` | Light section background (alternates with white). |
| white / slate-300 / slate-600 | — | Text: white headings + slate-300 body on navy; cb-navy headings + slate-600 body on light. |

### Contrast laws (non-negotiable except where noted)
- **Bright teal and yellow FAIL contrast as text on white/light** (~2.1:1 and ~1.5:1). On light backgrounds: small text, links, labels, eyebrows use `cb-teal-dark`; yellow text must sit on a navy pill/chip.
- On navy, `cb-teal` (~7.4:1) and `cb-yellow` pass — use them freely there.
- **One approved exception** (Chad, 2026-07-07): large bold display headlines on white may use bright `cb-teal` for brand fidelity, accepting the contrast miss. Never extend this to body text or links.
- Body text floors: `slate-300` on navy, `slate-600` on white. Never lighter.

## Typography

- **Plus Jakarta Sans** (variable), self-hosted via `@fontsource-variable/plus-jakarta-sans`. Never load from Google Fonts.
- Headings: bold, `tracking-tight` at display sizes. Section h2 ≈ text-3xl/4xl; page h1 ≈ text-3xl→5xl responsive.
- Small uppercase eyebrows/labels: `text-xs/sm font-bold tracking-widest uppercase`.

## Interaction language

- **Teal = interactive.** Text links hover to teal (`hover:text-cb-teal` on navy, `text-cb-teal-dark` at rest on light).
- **Yellow = brand emphasis** and the one exception: dropdown/menu items hover yellow.
- Canonical CTA button: `bg-cb-yellow text-cb-navy rounded-full font-bold px-8 py-4`, hover `bg-white` (on navy contexts) — never hover to navy on a navy card. Universal CTA label: **"Book a Free Strategy session"** (lowercase "session"), linking to `/contact`.

## Component motifs (the site's visual vocabulary)

- **Navy card**: `bg-cb-navy rounded-2xl/3xl shadow-md`, white heading, `slate-300` body. This is the signature — closing CTAs, step cards, feature cards all use it.
- **Icon-on-glass**: icon tile `bg-white/10 rounded-lg/xl` with a `text-cb-yellow` lucide icon; title in `text-cb-teal`, body `slate-300 text-sm`. (On light backgrounds: tile `bg-cb-teal/10`, icon `text-cb-teal-dark`, title `text-cb-navy`.)
- **Journey spine**: vertical yellow line (`bg-cb-yellow`, ~2px) with solid yellow numbered circles (`bg-cb-yellow text-cb-navy`, ring/halo `ring-cb-yellow ring-offset` + slight scale on the active one); navy accordion cards to the right, teal left-accent bar on the open card.
- **Capsule diagram** (deliverables): tall stadium shapes (`rounded-full`, height > width), solid navy, yellow "STEP 01" label, centered white title (fixed two-line title block so lists align), teal CheckCircle list in white text.
- **Pill tab control**: white/`cb-light` rounded-full container `p-1.5/2`, active segment `bg-cb-navy text-white shadow-md`, inactive `text-slate-600`. Widen to equal halves (`grid grid-cols-2 max-w-2xl`) for prominent choices.
- **Navy pull-quote band**: full-width `bg-cb-navy` strip, centered italic white quote, soft blurred orbs (`bg-cb-teal/10`, `bg-cb-yellow/10`, `blur-3xl`) in the corners.
- **Comparison panels**: two navy cards; them-vs-us tone = slate `XCircle` vs yellow `CheckCircle`; **versus tone** (two valid options) = identical yellow checkmarks both sides + a yellow "VS" disc between panels.
- **Stats band**: navy section, huge `cb-yellow` numbers (count-up on scroll), `white/80` uppercase labels.
- Section rhythm: alternate white / `cb-light` / navy; break long light stretches with a navy band or navy cards.

## Motion

- Scroll reveals: fade + 24px rise, staggered ~100ms across card grids; entrance `hero-rise` for hero/panel content.
- **Always honor `prefers-reduced-motion`**: disable CSS animations, pause autoplay video, keep auto-scrolling content user-scrollable instead of frozen.
- No scroll-jacking / pinned scrollytelling — tried and rejected (Chad, 2026-07). No auto-advance timers on content-heavy sliders.

## Logo & favicon

- Use the brand **PNG** wordmark (website: `public/assets/logo.png`); the original SVG has a malformed "a" glyph — never resurrect it. White-on-dark via CSS `brightness-0 invert`.
- The circular "CB" mark can be cropped from the wordmark's left ~400px (trim transparent edges).
- Favicon/app icon across ALL Cloud Beacon tooling: **navy square, white mark** — canonical files in `cloud-beacon-tools/portal/app/` (icon.png 256, apple-icon.png 180, favicon.ico). Copy those; don't regenerate variants.
- Third-party brand marks (LinkedIn etc.) keep their official colors (e.g. LinkedIn `#0A66C2`) — the cb-token rule doesn't apply to other companies' logos.

## Voice & copy

- **Implementer verbs, always**: Cloud Beacon *implemented / configured / tailored / tuned* D365. Never copy implying Cloud Beacon *built/created* D365 itself. ("A plan built around your business" is fine — the plan is ours; the platform is Microsoft's.)
- Tone: listen-first, plain-spoken, no jargon walls. Signature constructions: "X, not Y" ("Root cause, not band-aids", "with your team, not ahead of them"), and honest-partner lines ("A client who needs us less is a client we've done our job for").
- US spelling (normalize British source material: prioritise→prioritize, etc.).
- Company facts: Kansas City, MO, serving nationwide · info@cloudbeacon.com · +1 (626) 325-8662 · industries: Food & Beverage, Retail, Manufacturing · LinkedIn: linkedin.com/company/cloudbeacond365.
- Don't run broad "you gain this" voice rewrites unprompted — copy voice changes go line-by-line with Chad.

## Accessibility conventions

- Icon-only controls need `aria-label`; decorative icons `aria-hidden="true"`.
- Heading order strictly h1→h2→h3 (one h1 per page; card titles inside sections are h3 or bold `<p>`, never h4+).
- Visible focus: `focus-visible:ring-2 ring-cb-teal` replaces suppressed outlines.
- Proper ARIA patterns for tabs (`tablist/tab/tabpanel`) and accordions (`aria-expanded`/`aria-controls`, heading-wrapped buttons); keep hidden panel content in the DOM for crawlers.
