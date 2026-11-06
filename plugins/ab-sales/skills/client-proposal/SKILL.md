---
name: client-proposal
description: Create a NEW client proposal web page in Alta Beacon's house style, themed in the client's own brand colors, and publish it as a shareable link. Takes a client email, meeting notes, call transcript or SOW draft as the starting point. Use for requests like "create a proposal for <client>", "write up a proposal from this email", "build a proposal page like the WellBoss one", or "I need a proposal link to send <client>". To change a proposal that already exists, use proposal-update instead.
---

# Client Proposal: create a new branded web proposal

Proposals live in the private GitHub repo **`cloud-beacon/Proposals`**, one folder per
customer. Anyone with access can create one and publish it: when it's saved to the repo,
GitHub publishes it to its live link and checks the live page matches. Nobody needs Vercel.
The repo's `CONTRIBUTING.md` is the source of truth for that process.

## How to talk to the user

The people using this are often in sales or consulting, not engineering. Say "save",
"publish", "make it live", "the live link" and "your copy of the proposals". Don't
say pull request, merge, branch, commit, push or rebase unless they use those words
first. Run the git and gh commands yourself; don't ask them to. Report results in
plain words ("It's live at ... and matches what we saved").

## Step 0: check access (always do this first)

Run these yourself and stop at the first failure. Don't start work the user can't save.

1. `git --version`, `gh --version` and `node --version`. For anything missing, install it
   for them if you can (Windows: `winget install --id Git.Git -e`,
   `winget install --id GitHub.cli -e`, `winget install --id OpenJS.NodeJS.LTS -e`;
   Mac: `brew install git gh node`). Newly installed tools may need the app restarted
   before they're found. If you're running inside Cowork, stop: this workflow needs the
   Code tab of the desktop app (or Claude Code in a terminal), because Cowork's sandbox
   doesn't have their GitHub sign-in.
2. `gh auth status`. If they aren't signed in, have them run `gh auth login` in
   PowerShell (or type `! gh auth login` here in a terminal session) and follow the
   prompts in the browser. Then run `gh auth setup-git` yourself so git can push
   without prompting.
3. `gh repo view cloud-beacon/Proposals --json name,viewerPermission`
   - **It fails ("Could not resolve to a Repository") or `viewerPermission` is `READ`**:
     they don't have access yet. If they have several GitHub accounts, try
     `gh auth switch` once and re-check. Then get their username with
     `gh api user --jq .login` and stop with this message, filled in:

     > You don't have access to the Alta Beacon proposals yet. Send this to Chad Dalton
     > (cdalton@altabeacon.com) to ask for it:
     >
     > *Subject: Access to the Proposals repo*
     > *Hi Chad, could you give me access to the cloud-beacon/Proposals repo on GitHub so I
     > can work on client proposals? My GitHub username is **<login>**. Thanks!*
     >
     > Once he adds you, accept the invitation from GitHub (it arrives by email), then ask
     > me again.

     If an email tool is connected (Outlook or Gmail), offer to create that as a **draft**
     for them. Never send it. Don't work around missing access (for example by editing a
     downloaded copy of the live page).
   - `WRITE`, `MAINTAIN` or `ADMIN`: continue.
4. Find their copy: `~/source/repos/Proposals`, otherwise ask where it is. If there isn't
   one: `gh repo clone cloud-beacon/Proposals ~/source/repos/Proposals`. If this session
   isn't opened on that folder, work in it by absolute path.
5. `git status --short`. If there are changes the user didn't make in this session, ask
   before touching them; they may be someone's unfinished work. Then
   `git switch main` and `git pull --rebase`.
6. Read `CONTRIBUTING.md` in the repo.

## Step 1: collect the inputs

- **Scope source**: the client email, meeting notes, transcript or work item. Every
  workstream, hour estimate and constraint must trace to it. Don't pad scope the client
  didn't ask for. Ask the user which sources are in bounds. Some clients have documents
  we were told not to use.
- **Who it's from**: Alta Beacon for all new work. (VuAlta-branded proposals exist for
  partner deals; only make one if the user says so.)
- **Client branding**: fetch the client's website for the logo (download it into the
  folder), the favicon, and 2 brand colors (dominant + secondary; take them from the logo
  if the CSS doesn't state them). Get their formal name and the contact's name and title.
- **Commercials**: rate(s), hours per workstream, envelope, billing cadence, start date.
  **Never invent a number.** If one is missing, ask; if the user wants to go ahead anyway,
  use a visible placeholder `<span class="ph">TBD</span>` and point it out to the user before publishing.

## Step 2: build the page

**Start from the newest Alta Beacon proposal in the repo**, not from a blank page and not
from memory. Today that's `wellboss/` (check the README table for anything newer).

```
mkdir <repo>/<customer-kebab>
cp <repo>/wellboss/index.html <repo>/wellboss/alta-beacon.svg <repo>/<customer-kebab>/
```

Keep its CSS, token system and section skeleton verbatim. Replace the content, the logos
and the brand tokens. Copy the Alta Beacon footer (address, contacts) as-is from that page
unless the user gives different contacts.

### Structure (always keep)

Sticky logo-lockup header with scroll-progress bar → hero (mono kicker, big headline with an
italic serif accent, lede) → meta strip (Prepared for / Engagement / Start / Focus) →
numbered sections: Opportunity → Engagement → Plan → Team → Why Alta Beacon → Investment →
Next steps (add a section such as Licensing only when the scope needs it, and renumber) →
dark footer with contacts.

### Skin (always the client's)

The page is themed in the **client's** colors, not Alta Beacon's. That makes it feel
bespoke. Alta Beacon shows up in the logo lockup (client logo first), the "Why Alta Beacon"
section and the footer.

All color is in CSS custom properties, defined in **four** blocks: `:root`,
`@media (prefers-color-scheme: dark)`, `:root[data-theme="light"]`,
`:root[data-theme="dark"]`. The data-theme blocks mirror the first two. Re-skin all four;
never hardcode a color in a component.

- `--navy` → the client's dark shade (headings, strong text). The name is legacy; it means
  "the serious color".
- `--green` → the client's primary accent (serif accents, eyebrow numbers, hours).
- `--green-lt` / `--teal` → the secondary, brighter accent (bullets, checkmarks, progress bar).
- `--ink` / `--muted` / `--rule` → neutrals tinted toward the client's hue (never pure gray).
- `--footer-bg` → a very dark version of the client's color.
- Dark theme: a dark tinted background and a lightened heading color. Don't just invert.
- Keep `--paper:#fbfaf7` unless the client's brand demands otherwise.

Typography stays: Plus Jakarta Sans → Segoe UI stack for body, Georgia italic for serif
accents, monospace uppercase for eyebrows and labels. No webfont downloads.

Keep `<meta name="robots" content="noindex, nofollow">` in the head.

### Design system: the building blocks

Every proposal is built from the same components, already styled in the template. Use
them; don't invent new layouts, add CSS for one-off looks, or set colors inline. If the
content doesn't fit a component, rework the content first.

| Component | Markup (from the template) | Use for |
|---|---|---|
| Section opener | `.eyebrow` (`.n` number + `.t` title) then `h2` with one `<span class="serif">` accent | Every numbered section |
| Lede | `p.lede` | The first, larger paragraph of the hero or a section |
| Meta strip | `.meta` with four `div`s (`.k` label, `.v` value, `.s` sub-line) | Prepared for / Engagement / Start / Focus, in the hero only |
| Two columns | `.twins` with two `div`s (`.k` label + `p.muted`) | Before/after, phase outcomes, "By January 1 / By March" |
| Plan | `.plan` > `.step` (`.num`, `h3` with a serif accent, `p`, `.hrs` with `<small>`) + `.plan-total` | The phased plan with hours |
| Team | `.team` > `.member` (`.role`, `.tag`, `p`) | Roles, including a "Your side" card for the client's people |
| Stats | `.stats` with `<span><b>20+</b>&nbsp;label</span>` | The four proof points in Why Alta Beacon |
| Cards | `.why` > `.card` (`.n`, `h3`, `p`) | The four Why Alta Beacon reasons |
| Rate | `.rate-line` (`.big` with `<em>/hour</em>`, `.after`) | The headline rate in Investment |
| Terms table | `table.terms`, last row `tr.total` | Tiers or workstreams with hours and dollars |
| Included grid | `.inv-grid` of short `div`s | What the rate includes (checkmarks are automatic) |
| Fine print | `p.fine` | Billing terms and "Formal terms follow in…" |
| Next steps | `ol.next` with `<strong>` lead-ins | The closing section |

Rules that keep pages consistent:
- Add `reveal` to each block-level element, as the template does (it drives the scroll-in).
- One serif accent per headline, on the phrase that carries the meaning; never on a
  whole headline.
- Section numbers run 01, 02, 03… with no gaps after you add or remove a section.
  Keep the HTML comments (`<!-- 03 PLAN -->`) in step.
- Logos: client logo first. Use the template's heights (header 38 / 24, hero 64 / 36)
  and adjust only to balance visual weight. The client logo must read on the off-white
  page. If they only have a white logo, ask for a dark version instead of adding a
  background plate. Alta Beacon logo: `alta-beacon.svg` on light backgrounds; the
  `cb-brand` skill (ab-marketing plugin) has the full logo rules.
- Colors: the check script measures the client's colors against the page. If the
  client's main color is light (yellow, light green, sky blue), use a darker shade of it
  for `--green` and `--navy`, and keep the bright one for `--green-lt`.
- Tone: if the ab-marketing plugin is installed, its `cb-voice` skill applies to the copy.

### Look at it before publishing

Take screenshots and look at them; don't publish a page you haven't seen. With Chrome
(use a throwaway profile; works on Windows and Mac):

```
chrome --headless=new --disable-gpu --user-data-dir="$TMP/pp-chrome" --hide-scrollbars   --force-prefers-reduced-motion --window-size=1280,6000   --screenshot="$TMP/desktop.png" "file:///<repo>/<folder>/index.html"
chrome ...same flags... --window-size=500,9000 --screenshot="$TMP/narrow.png" ...
chrome ...same flags... --force-dark-mode --blink-settings=preferredColorScheme=0   --window-size=1280,6000 --screenshot="$TMP/dark.png" ...
```

`chrome` is `"C:\Program Files\Google\Chrome\Application\chrome.exe"` on Windows,
`"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"` on Mac.
`--force-prefers-reduced-motion` matters: without it the scroll-in animation hasn't run
and most of the page screenshots as faded-out. Use 500px for the narrow check: headless
Chrome won't render narrower, so a 390px shot looks cut off even when the page is fine.

Check: logos sharp and balanced, nothing overflowing at 500px, the plan hours and table
aligned, no empty or placeholder text you didn't intend, headings and the client logo
readable in dark mode.

### Copy rules

- Headline: a statement plus an italic serif accent phrase in the client's color
  (`One payment run, <span class="serif">one transmission path</span>.`).
- Short, confident, concrete sentences. Section 01 restates *their* problem sharply, in
  their words from the source. No generic value language.
- Plan maps 1:1 to the client's workstreams with hours and a running total. Say why the
  order de-risks the work.
- Investment: big rate figure, a small table (estimate and envelope with the dollar math
  checked), a checkmark grid of what's included, fine print on billing, and "Formal terms
  follow in a services agreement" (or Statement of Work, per the deal).
- Alta Beacon defaults (confirm per deal): time and materials, **invoiced every two weeks
  in arrears** on actual hours, with monthly reporting against the estimate.
- "Why Alta Beacon" stats: 20+ **average** years in D365/AX (never "20 years"), 80+
  projects, 100% go-live success. Food & beverage is a specialty, never "our entire
  practice".
- "Alta Beacon" is always two words. "Cloud Beacon" never appears on new work.
- Client-first naming: "<Client> × Alta Beacon" in the title and h1, client logo first.
- **American English, always**, even if the client or source uses British forms
  (recognize, behavior, fulfillment, license, canceled, gray, center). The repo's check
  script enforces it.

## Step 3: record and check

1. Write `<customer>/proposal.json`:
   ```json
   {
     "client": "<Client name as on the page>",
     "brand": "Alta Beacon",
     "status": "draft",
     "url": "https://<customer>-altabeacon-proposal.vercel.app",
     "vercel": { "project": "<customer>-altabeacon-proposal", "scope": "cloud-beacons-projects" },
     "build": "copy",
     "autoDeploy": true
   }
   ```
2. Write `<customer>/NOTES.md`: client and contact, the sources used, agreed or proposed
   terms, content rules the user gave you, and open items. The next editor relies on this.
   Look at `wellboss/NOTES.md` for the shape.
3. Add a row to the README customer table.
4. `node scripts/check.mjs <customer>`. Fix every error. Report the warnings.
   Set `"status": "sent"` in proposal.json once the user says it went to the client.
5. Screenshot it (desktop, phone, dark) as in "Look at it before publishing" and look
   at the images. Check logos, the favicon and the dollar math.

## Step 4: publish

1. Show the user what will go live, in plain words (before and after for the key
   sentences and numbers). Ask: **"Ready to publish this? It gets its own link in about a minute, and nobody sees it until you share that link."** Wait for a yes.
2. Commit with a message that says what changed for the client
   (e.g. "WellBoss: invoice every two weeks"). If NOTES.md changed, include it.
3. `git pull --rebase`, then `git push`. If the push is rejected, pull again and retry.
   If someone else changed the same lines, stop and explain it in plain words.
4. Watch the publish: find the run with
   `gh run list --workflow "Deploy proposals" --limit 1` and follow it with
   `gh run watch <id> --exit-status`.
   - **Success**: tell them it's live at the `url` from `proposal.json` and matches what
     was saved. Suggest a hard refresh (Ctrl+F5) if they still see the old version.
   - **The checks failed**: the page was not published. Fix the errors, then publish again.
   - **"VERCEL_TOKEN secret is not set"** or any other failure: the change is saved but not
     live. Tell them to let Chad know, and paste the error.
   - **`autoDeploy` is `false`** for this proposal (Shamrock, for example): it is saved but
     not published automatically. Explain why (from NOTES.md) and that Chad publishes it
     by hand.

Never run `vercel deploy` yourself, and never email the client. If the client should hear
about the change, offer to draft a short note for the user to send.

Before the user shares the link with the client, close with this reminder:

> **Book the walkthrough before this goes out.** Proposals are presented in a scheduled
> working session, never emailed cold for review. Send an agenda, present it, take
> objections live, agree the decision date, then send the link so they can circulate it.

## Checklist

1. Access checked; started from an up-to-date copy.
2. Scope, hours, rates and dates trace to the source; dollar math checked; no invented numbers.
3. Client logo first; client-first naming; client favicon; logos are local files in the folder.
4. All four token blocks re-skinned (light, dark, both data-theme mirrors).
5. Footer: Alta Beacon contacts; "Prepared for" names the client contact and title.
6. `proposal.json`, `NOTES.md` and the README row written.
7. `scripts/check.mjs` clean (including the color-contrast check); screenshots checked at
   desktop and phone width, light and dark; only template components used.
8. Published with the user's yes; live link verified; nothing sent to the client.
