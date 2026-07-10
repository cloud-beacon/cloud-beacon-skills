---
name: deck-to-page
description: Turn a Cloud Beacon methodology PowerPoint deck into a Cloud-Beacon-Website Approach-style page (or refresh an existing one). Use whenever the user adds a .pptx to the website repo's updates/ folder and asks to incorporate it into a page — e.g. "I added Cloud_Beacon_X_Methodology to updates, please add it to the Y page". Covers text extraction, rendering slides to images for visual reference, and the proven mapping onto the ApproachContent data shape (spine accordion steps, capsule deliverables diagram, quote band, comparison panels, engagement layout).
---

# deck-to-page — PPTX methodology deck → Approach page

Used five times to build the live Approach pages (Rescue Projects, Managed Services ×2 tabs, Continuous Improvement + Value Realization, New Implementation). Follow this recipe; don't improvise the mapping.

## 1. Extract the deck

A .pptx is a zip. From Git Bash, into the session scratchpad (never the repo):

```bash
cd "$SCRATCHPAD" && mkdir -p pptx && cp "<repo>/updates/<Deck>.pptx" d.zip && unzip -o -q d.zip -d deck
cd deck/ppt/slides
for f in $(ls slide*.xml | sort -V); do echo "===== $f ====="; \
  sed -e 's/<a:br\/>/\n/g' -e 's/<\/a:p>/\n/g' "$f" | \
  grep -o '<a:t>[^<]*</a:t>' | sed -e 's/<a:t>//g' -e 's/<\/a:t>//g'; echo; done
```

When the SLIDE'S VISUAL matters (diagrams you're asked to reproduce), render it via PowerPoint COM and Read the PNG:

```powershell
$pp = New-Object -ComObject PowerPoint.Application
$pres = $pp.Presentations.Open("<full path>.pptx", $true, $false, $false)
$pres.Slides.Item(<n>).Export("$scratch\slide<n>.png", "PNG", 1920, 1080)
$pres.Close(); $pp.Quit()
```

Never guess a slide's design from its text — the capsule deliverables diagram was only right because the slide was rendered and looked at.

## 2. Map slides onto ApproachContent (constants.ts)

All content is data-driven: `APPROACH_PAGES` in `constants.ts`, rendered by `components/ApproachPage.tsx`. Typical deck anatomy → data:

| Deck slide | Data target | Renders as |
|---|---|---|
| Title slide tagline | `hero.subheading` | Teal line under the H1 |
| "What is X" / context slide | `whyItMatters` (heading + `body` paragraphs) | White section after hero |
| Us-vs-them comparison | `whyItMatters.contrast` (✗/✓ default) | Two navy panels |
| Two-valid-options comparison | `contrast` with `tone: 'versus'` | Yellow checks both sides + VS badge |
| 6-card "difference"/intro grid | `whyItMatters.cards` (+ `cardsClosing`) | Navy icon cards in the intro section |
| Phase-overview diagram | `whatWeDo` heading/intro + per-phase `highlights` (the mini-lines under each phase) + `quote` (the diagram's pull-quote) + `loopNote` (any ↺ annotation) | Spine accordion header lines, navy quote band, loop pill |
| One slide per phase/step/pillar | `whatWeDo.phases[]`: `name`, `shortName` (if long), `body`, `activities[]` (title/body/`icon` key into ACTIVITY_ICONS) | Accordion cards with icon rows |
| Engagement model / framework slide (numbered steps ± included list) | `engagement` (steps, optional includedHeading/included, `badge`, `note`) | Numbered list + optional navy panel |
| Deliverables summary slide | per-phase `deliverables[]` (this slide is CANONICAL when per-phase slides disagree) + `outcomes` intro/footnote | Capsule diagram in "What you walk away with" |
| Differentiators slide | **OMIT** — removed on every page per Chad; note the omission in your summary |
| Closing quote/mantra | `whatWeDo.quote` or `outcomes.footnote` | Navy band / diagram caption |

## 3. House conventions

- **US spelling** (prioritise→prioritize, realise→realize, stabilise→stabilize, organisation→organization).
- Voice: keep the deck's language nearly verbatim (it's Chad-approved), light grammar cleanup only; adapt third person to second person ("the client brings" → "you bring"). Implementer verbs only — never imply Cloud Beacon built D365 itself.
- `shortName` when a phase name is long (used by capsules and selectors).
- Per-step "principle" quotes exist in the type but are NOT rendered (removed by Chad) — you may store them, don't add a renderer.
- Steps default to all collapsed; panels stay in SSR HTML for SEO.
- Icons: pick per-activity keys from `ACTIVITY_ICONS` in ApproachPage.tsx; add new lucide imports + map entries if needed.
- Two pages sharing one framework → hoist shared sections into a named const (see `VALUE_FRAMEWORK_WHAT_WE_DO`) so they can't drift.
- Page needs interactivity (accordion/tabs) → add `client:idle` to `<ApproachPage>` in the .astro page. Compact-grid pages ship zero JS.
- Note the source in a comment: `// Content source: updates/<deck>.pptx`.
- If renaming a page: slug/type union, path, navLabel, headline, seoTitle, page-file `git mv`, llms.txt entry, vercel.json permanent redirect, and grep for internal links (blog posts link to approach pages).

## 4. Verify before shipping

Build, then grep `dist/<page>/index.html` for: each step name, a deliverable from the last phase (proves capsules), the quote, and confirm other Approach pages unchanged. Then follow the website repo's `ship` skill.
