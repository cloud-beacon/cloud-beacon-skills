---
name: proposal-update
description: Change an existing client proposal and make the change live. Works for any proposal in the Alta Beacon proposals collection (WellBoss, Liquid I.V., Shamrock, Olly & SmartyPants, Rave Aerospace and newer ones). Use for requests like "update the WellBoss proposal", "change the rate on the Liquid I.V. proposal", "the client asked us to remove X", "fix the wording in section 2", "add Caroline to the team section", "publish the change", "make it live", or "why isn't my change showing". To build a brand-new proposal use client-proposal instead.
---

# Proposal Update: change a proposal and make it live

Every proposal lives in the private GitHub repo **`cloud-beacon/Proposals`**, one folder per
customer. Most have already been sent, so each page is a record of what the client holds.
Anyone with access can change one and publish it: when the change is saved to the repo,
GitHub publishes it to the live link and checks the live page matches.

## How to talk to the user

The people using this are often in sales or consulting, not engineering. Say "save",
"publish", "make it live", "the live link" and "your copy of the proposals". Don't
say pull request, merge, branch, commit, push or rebase unless they use those words
first. Run the git and gh commands yourself; don't ask them to. Report results in
plain words ("It's live at ... and matches what we saved").

## Step 0: check access (always do this first)

Run these yourself and stop at the first failure. Don't start work the user can't save.

1. `gh --version`. If it's missing, install it for them if you can
   (`winget install --id GitHub.cli -e` on Windows, `brew install gh` on Mac). Otherwise
   tell them to install the GitHub CLI.
2. `gh auth status`. If they aren't signed in, ask them to type `! gh auth login`
   and follow the prompts in the browser.
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
   one: `gh repo clone cloud-beacon/Proposals ~/source/repos/Proposals`.
5. `git status --short`. If there are changes the user didn't make in this session, ask
   before touching them; they may be someone's unfinished work. Then
   `git switch main` and `git pull --rebase`.
6. Read `CONTRIBUTING.md` in the repo. `node --version` must work (the check script
   needs Node); if it doesn't, install Node LTS or tell them to.

## Step 1: understand the proposal before editing

1. Find the folder from the README table (match on client name; ask if two could fit).
2. **Read `<folder>/NOTES.md` in full.** It holds the agreed terms, superseded numbers
   that must never come back, wording we were asked to remove, and sources we must not
   use. If the requested change contradicts it, say so and ask before going ahead.
3. Read `<folder>/proposal.json`: brand, live URL, and whether it auto-deploys.
4. Read the parts of `index.html` you're changing, plus anything that repeats the same
   fact. Rates, hours, dates and names usually appear in several places: the meta strip,
   Plan, Investment, the fine print, Next steps.

## Step 2: make the change

- **Surgical edits only.** Change what was asked. Don't restyle, reword, reorder or
  "improve" the rest of a sent proposal, and don't rebrand older Cloud Beacon or VuAlta
  pages to Alta Beacon.
- Keep every instance of a changed fact consistent across the page, and redo any dollar
  math it feeds.
- **Never invent a rate, hours, a date or a term.** If the request needs a number you
  don't have, ask. If it's genuinely unknown, use `<span class="ph">TBD</span>` and flag it.
- Keep the design system. Use only the components the page already uses (plan steps, team
  cards, terms table, included grid, and so on; the `client-proposal` skill lists them
  all), copying the markup of an existing block. Add `reveal` to new blocks. Color comes
  only from the CSS tokens. One serif accent (`<span class="serif">`) per headline. New
  images are saved as local files in the folder, not hot-linked. If you add or remove a
  section, renumber the rest.
- American English in every client-facing word.
- If the change sets or alters a term, a content rule, or answers an "Open" item, update
  `NOTES.md` in the same change. Superseded terms go under "Superseded, never reintroduce".

## Step 3: check

1. `node scripts/check.mjs <folder>`. Fix errors. Errors in text you didn't touch are
   pre-existing; mention them, and fix them only if the user agrees (the publish step
   runs the same checks and won't publish while errors remain).
2. Screenshot the page at desktop and phone width (the `client-proposal` skill has the
   headless Chrome commands) and look at the part you changed. Nothing should overflow,
   and new blocks should match the ones around them.

## Step 4: publish

1. Show the user what will go live, in plain words (before and after for the key
   sentences and numbers). Ask: **"Ready to publish this? The client's link will show it in about a minute."** Wait for a yes.
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
