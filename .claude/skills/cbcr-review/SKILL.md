---
name: cbcr-review
description: Submit the developer's working changes to Cloud Beacon's pre-submit review endpoint (cr.cloudbeacon.com) for automated X++ code review against the xpp-code-review framework. Accepts either a raw diff (git or TFVC) OR a named TFVC shelveset (fetched from Azure DevOps and reviewed against the client's profile). The report arrives by email in 1-2 minutes. Trigger on `/cbcr-review`, `/cbcr`, or when the user asks for a pre-submit review, self-review, "review my changes before I submit", "review shelveset FooChange", "run this by the CR bot", or similar phrasing about getting feedback on working changes *before* opening a formal code-review request in Azure DevOps.
---

# /cbcr-review — pre-submit code review

Submits the developer's changes to `https://cr.cloudbeacon.com/review` for
review before they formalize a code-review request in ADO. Two submission
modes: **diff** (raw unified diff from stdin — git or TFVC working state)
and **shelveset** (name+owner reference; the endpoint fetches from ADO
using the client's stored PAT). Report emails back to the developer whose
token was used. Format matches `/cr-review` (verdict, spec conformance
if applicable, findings by severity, what looks good).

## When to invoke

- User runs `/cbcr-review` or `/cbcr`.
- User asks for a pre-submit review, self-review, or feedback on their
  working diff *before* they open a formal Azure DevOps code-review request.
- User pastes a diff and says "review this before I submit" or similar.

## When NOT to invoke

- The user wants the CR-request-driven pipeline (that's `/cr-review` in the
  Cloud-Beacon-CR repo — different skill, driven by ADO email triggers).
- The user just wants inline in-chat feedback on a snippet of X++ (do that
  directly — apply the `xpp-code-review` skill yourself and answer here,
  no endpoint round-trip needed).
- The user is reviewing someone *else's* shelveset (that also goes through
  `/cr-review`, not this endpoint).

## Steps

1. **Confirm the caller has Azure CLI signed in to Cloud Beacon.** Run
   `az account show --query '{tenant:tenantDefaultDomain, user:user.name}' -o tsv`.
   If it exits non-zero, tell the user to `az login --tenant cloudbeacon.dev`
   and stop. If the tenant domain isn't `cloudbeacon.dev`, tell them to
   `az account set --subscription <cloudbeacon-sub>` and stop.

2. **Decide the submission mode.**

   **Shelveset mode** — use when the user names a specific TFVC shelveset:
   phrases like "review shelveset FooChange", "review shelveset FooChange
   owned by cbcdev@buddig.com", "review my pending Buddig shelveset". The
   endpoint fetches the shelveset from Azure DevOps and applies the
   client's naming/framework profile.
   - Need three inputs: shelveset name, shelveset owner (defaults to the
     user's ADO identity if not given), client id (defaults to the profile
     that matches the current repo if unambiguous — e.g. `buddig` if the
     repo is `Buddig D365 FSC`). Ask the user to clarify anything you can't
     infer confidently.
   - Confirm inputs back to the user before submitting.

   **Diff mode** — use when the user has working changes and no shelveset:
   - If the user pasted a diff in-chat, use it verbatim.
   - Otherwise detect the VCS in the current working directory:
     - **Git**: `git diff HEAD` (staged + unstaged vs HEAD). If empty, try
       `git diff origin/HEAD` (branch vs main). If still empty, stop and
       tell the user "no diff to review".
     - **TFVC** without a specific shelveset in mind: `tf.exe diff
       /format:unified /recursive` from the workspace root. If empty, stop.
     - **Neither**: ask the user to paste a unified diff, `cd` into a repo
       with pending changes, or provide a shelveset name.

3. **Sanity-check the scope (diff mode only).** Show a one-line summary:
   `Diff: N files, +X/-Y lines. Submit?` If N is 0, stop. If the diff is
   >1 MB, warn about size and confirm. Otherwise proceed automatically.
   (Shelveset mode has no local scope check — the endpoint fetches
   whatever's in the named shelveset.)

4. **Submit.** `${CLAUDE_PLUGIN_ROOT}` is set by Claude Code to this
   skill's directory; fall back to `~/.claude/skills/cbcr-review` if
   unset. Add `--wait` if the user asked for synchronous behavior ("wait
   for the report", "poll until done").

   **Diff mode:**
   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/submit.sh" [--wait]
   ```
   piping the collected diff to stdin.

   **Shelveset mode:**
   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/submit.sh" \
     --shelveset "<name>;<owner>" \
     --client <client-id> [--wait]
   ```
   The shelveset spec is a single `name;owner` string (semicolon-joined).

5. **Report back.** Parse `submit.sh`'s output:
   - Success (exit 0): show the developer the job id and note
     "Report emails to you in ~1-2 minutes. Reply-to is the pipeline; the
     email lands in your inbox."
   - Failure (non-zero exit): surface the stderr verbatim. Common cases:
     - "token acquisition failed" → tell them to `az login`
     - "server returned 401" → the tenant policy may have changed;
       ping Chad
     - "server returned 5xx" → the endpoint has a problem; ping Chad
     - "empty diff" → they had no changes staged/unstaged

## Auth model (for context, not action)

The `cr.cloudbeacon.com` endpoint validates Entra ID bearer tokens issued
for the `cbcr-service` app (app id `357ad426-0779-493a-a55f-e0bb3894d4b1`,
scope `Review.Submit`). Azure CLI is pre-authorized on that app, so
`az account get-access-token` works silently for any signed-in Cloud
Beacon user. No client secret, no PAT, no interactive prompt after the
initial `az login`. When the token drifts (Azure CLI refreshes it silently
for weeks; interactive re-auth needed only after ~90 days of inactivity),
`submit.sh` surfaces the error and the user re-runs `az login`.

## Privacy

The diff you submit is sent over TLS to `cr.cloudbeacon.com`, reviewed by
Claude Code on the VM, and mailed back to you. Nothing is retained beyond
the review-lifecycle job files on the VM (`~/Cloud-Beacon-CR/.cr/jobs/` +
`~/Cloud-Beacon-CR/.cr/reports/`), which are `chmod 600` and only readable
by the pipeline's operator. Don't submit diffs containing production
credentials or PII — same policy as any code review.
