---
name: cbcr-review
description: Submit the developer's current working diff to Cloud Beacon's pre-submit review endpoint (cr.cloudbeacon.com) for automated X++ code review against the xpp-code-review framework. The report arrives by email in 1-2 minutes. Trigger on `/cbcr-review`, `/cbcr`, or when the user asks for a pre-submit review, self-review, "review my changes before I submit", "run this by the CR bot", or similar phrasing about getting feedback on their working diff *before* opening a formal code-review request in Azure DevOps.
---

# /cbcr-review — pre-submit code review

Submits the developer's current diff to `https://cr.cloudbeacon.com/review`.
The endpoint validates the caller's Entra ID token, enqueues the diff, and
emails the report back to the developer whose token was used. Report format
matches `/cr-review` (verdict, findings by severity, what looks good).

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

2. **Collect the diff.** In priority order:
   - If the user pasted a diff in-chat, use it verbatim.
   - Otherwise, detect the VCS in the current working directory:
     - **Git**: `git diff HEAD` (staged + unstaged vs HEAD). If that's
       empty, try `git diff origin/HEAD` (branch vs main). If still empty,
       stop and tell the user "no diff to review".
     - **TFVC** (`tf.exe` on PATH, or a metadata folder that looks like
       AX/D365 tooling): `tf.exe diff /format:unified /recursive` from the
       workspace root. If empty, stop.
     - **Neither**: ask the user to paste a unified diff or `cd` into a
       repo with pending changes.

3. **Sanity-check the scope.** Show the user a one-line summary:
   `Diff: N files, +X/-Y lines. Submit?` If N is 0, stop. If the diff is
   >1 MB, warn about size and confirm. Otherwise proceed automatically.

4. **Submit.** Run:
   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/submit.sh"
   ```
   piping the diff to stdin. Add `--wait` if the user asked for
   synchronous behavior (e.g., "wait for the report", "poll until done").
   `${CLAUDE_PLUGIN_ROOT}` is set by Claude Code to this skill's directory;
   fall back to `~/.claude/skills/cbcr-review` if it's not set.

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
