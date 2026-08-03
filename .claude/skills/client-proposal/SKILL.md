---
name: client-proposal
description: Build and deploy a client-branded, single-page web proposal in Cloud Beacon's editorial house style (LCA-inspired — numbered narrative sections, italic serif accents in the client's brand color, scroll-reveal). Takes a scope source (client email, meeting notes, or SOW draft), skins the page in the client's own branding pulled from their website, and ships it to Vercel at <client>-cloudbeacon-proposal.vercel.app. Trigger on "create a proposal for <client>", "build a web proposal", "proposal page like the Shamrock one", or when the user wants to turn a scope email into a sendable proposal link.
---

# Client Proposal — branded web proposal generator

Bundled asset: `assets/reference-proposal.html` — the finished Shamrock Foods proposal
(August 2026), which is the **reference implementation**. Do not invent a new layout:
copy this file, keep its CSS/token system and section skeleton verbatim, and replace
only the content and the brand tokens. The design decisions in it are deliberate and
client-tested.

First shipped result: https://shamrock-cloudbeacon-proposal.vercel.app

## Why this format

The structure is modeled on LCA's proposal style (the Greg Isenberg video): a narrative
the buyer *reads* instead of a deck they skim. Two separable layers:

1. **Structure** (always keep): sticky logo lockup header + scroll progress bar, hero with
   big headline, meta strip (Prepared for / Engagement / Start / Focus), then numbered
   sections 01–07: Opportunity → Engagement → Plan → Team → Why Cloud Beacon →
   Investment → Next steps. Dark brand footer with contacts.
2. **Skin** (always the client's): the page is themed in the *client's* brand colors, not
   Cloud Beacon's. That is the LCA move — their Spotify proposal is Spotify green.
   It makes the proposal feel bespoke; Cloud Beacon presence is carried by the logo,
   the "Why Cloud Beacon" section, and the footer.

## Inputs to collect before building

- **Scope source** — the client email / meeting notes / work item describing the need.
  Every workstream, hour estimate, and constraint in the proposal must trace to it.
  Do not pad scope the client didn't ask for.
- **Client branding** — fetch the client's website: logo URL(s), favicon link tags,
  and 2 brand colors (dominant + secondary; extract from the logo PNG palette if the
  CSS doesn't state them). Also grab their formal legal name and the contact's
  name/title for the footer.
- **Commercials** — rate(s), estimated hours per workstream, envelope (min–max hours).
  Confirm with the user if not stated; never invent a rate.
- **Cloud Beacon boilerplate** — billing is **biweekly** in arrears (T&M, detailed
  timesheets, reporting vs estimate) — note some older SOWs say monthly; biweekly is
  current. Footer address
  `4741 Central St Ste 500, Kansas City, MO 64112`, `www.cloudbeacon.com`,
  contacts `cdalton@cloudbeacon.com` (escalations) and `accounting@cloudbeacon.com`
  (billing). Stats for "Why Cloud Beacon": 20+ **average** years in D365/AX (not "20 years"),
  80+ projects, 100% go-live success, F&B home industry. Delivery-model language comes
  from the "Cloud Beacon F&B Customer Success" deck: "Accountability stays. Capacity
  scales.", nearshore = Central & South America on client business hours, honesty
  principle. If the client has seen that deck, echo its exact phrases.

## How to theme (token swap only)

All color lives in CSS custom properties defined in four blocks: `:root` (light),
`@media (prefers-color-scheme: dark)`, `:root[data-theme="light"]`, and
`:root[data-theme="dark"]` (the data-theme blocks must mirror the first two — they let
a host page's theme toggle win). Never hardcode color in components. To re-skin:

- `--navy` → client's *dark* brand shade (headings, plan numbers, strong text).
  Despite the name it is "the serious color", whatever hue that is.
- `--green` → client's primary accent (italic serif phrases, eyebrow numbers, hours).
- `--green-lt` → client's secondary/brighter accent (bullets, checkmarks, progress bar).
- `--ink` / `--muted` / `--rule` → neutrals *tinted toward the client hue* (never pure grey).
- `--footer-bg` → very dark version of the client color.
- Derive the dark theme the same way (dark tinted ground, lightened heading color);
  don't naively invert.
- Keep `--paper:#fbfaf7` warm off-white unless the client brand demands otherwise.

Typography stays: Plus Jakarta Sans → Segoe UI stack for body, Georgia italic for the
serif accents, monospace uppercase for eyebrows/labels. No webfont downloads.

## Copy rules

- Headlines: statement + italic serif accent phrase in client color
  (`One payment run, <span class="serif">one transmission path</span>.`).
- Short, confident, concrete sentences. Every claim traceable to the scope source or
  the customer-success deck. Name the client's actual risk in section 01 — the hook
  should be *their* problem restated sharply, not generic value language.
- The Plan section maps 1:1 to the client's stated workstreams with their hours and a
  running total. Sequence to de-risk and say why the order matters.
- Investment: big rate figure, small table (estimate + envelope with dollar math),
  checkmark grid of what's included, fine print with billing terms, "Formal terms
  follow in a Statement of Work."
- Client-facing names lead: "<Client> × Cloud Beacon" in title/h1, client logo first
  in every lockup.

## Assets (logos / favicon)

Hotlink the client's logo and favicon from their own site (pixel-identical, zero upload)
and the Cloud Beacon logo from `https://dynamicschad.com/assets/logo.png`. Add the
client's real favicon `<link rel="icon">` tags copied from their homepage head. If the
user wants the page self-contained, inline the images as base64 data URIs instead —
but see the deploy warning below.

## Deploy

- **Vercel** (the sendable link): `deploy_to_vercel` on the Cloud Beacon team
  (`team_XqdjZfw1jhtAmsXBR9yDzRoG`), project `<client>-cloudbeacon-proposal`,
  target `production` → `https://<client>-cloudbeacon-proposal.vercel.app`.
  Verify with `get_deployment` (READY) plus a `curl` for HTTP 200.
  ⚠️ The tool takes file contents inline; large base64 logo files can silently truncate
  the file list — this is why hotlinking is the default. If you must ship binaries,
  deploy them in a separate call or verify every file landed.
- **Claude artifact** (private preview for the user before sending): publish an inline-
  logo variant (data URIs — artifact CSP blocks external hosts) with an emoji favicon.
- Redeploys to the same project name keep the same URL. Keep the working copy in the
  project repo (`proposals/vercel/index.html` pattern) so edits are surgical.

## Per-proposal checklist

1. Scope, hours, rate, start window confirmed against source. Dollar math checked.
2. Client logo first in lockups; client-first naming everywhere; client favicon.
3. All four token blocks re-skinned (light + dark + both data-theme mirrors).
4. Footer: CB address/contacts + "Prepared for" with the client contact's name & title.
5. Deployment READY and URL returns 200; hard-refresh note for favicon caching.
6. Anything the client already saw (deck, prior email) echoed, not contradicted.
