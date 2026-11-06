---
name: tfvc-merge
description: Unattended TFVC merge for Alta Beacon clients — promote changesets from a lower branch (dev) into a higher branch (test, main) with auto-resolve, skip-and-continue on conflicts, ADO work-item linking, and an email summary on completion. Use whenever the user wants to merge, promote, forward-integrate, or "move code up" from a dev branch into a test/main branch in TFVC (e.g. "merge dev to test for Buddig", "promote everything since Friday from Dev to Test", "run the nightly merge for Acme"). Read-write — it performs real tf.exe merges and check-ins. Conflict policy is skip-and-continue: changesets that cannot auto-resolve are left in the source branch and reported, the rest still promote.
---

# tfvc-merge — unattended dev→test TFVC merge

Bundled scripts (Python 3, standard library only — no `pip install`):

- `scripts/tfvc_merge.py` — orchestrator with three subcommands: `candidates` (dry run), `run` (perform the merge), `report` (re-render the email from a past run).
- `scripts/_ado.py`, `scripts/_tf.py`, `scripts/_xpp_xml.py`, `scripts/_report.py`, `scripts/_notify.py` — helpers; not invoked directly.
- `scripts/scheduled/run_merge.ps1` — PowerShell entry point for Windows Task Scheduler.

This skill **performs real check-ins** in TFVC. For read-only retrieval, use `tfvc-fetch`.

## Interpreter

Invoke with this machine's Python 3 launcher: `python` / `py -3` on Windows. Shown as `<python>` below.

## Inputs

Provide a client profile JSON (extends the tfvc-fetch shape with `workspace_root` and `merges[]`):

```json
{
  "client": "acme",
  "ado_base_url": "https://acmed365.visualstudio.com",
  "pat_env": "AZDO_PAT_ACME",
  "api_version": "7.1",
  "workspace_root": "C:/tfs/acme",
  "tf_exe": "C:/Program Files/.../tf.exe",
  "notify_via": "mcp",
  "merges": [
    {
      "name": "dev-to-test",
      "source_branch": "$/AcmeProject/Dev",
      "target_branch": "$/AcmeProject/Test",
      "target_local_path": "C:/tfs/acme/Test",
      "cutover": { "mode": "since_last_run" },
      "notify_recipients": ["cdalton@cloudbeacon.com", "lead@acme.example"]
    }
  ]
}
```

**PAT scopes:** Code (Read & Write), Work Items (Read & Write). PAT is read from the env var named by `pat_env` (default `AZDO_PAT`), or from `pat_file` if set. Never pass it on the command line.

**Cutover modes:**

- `{"mode": "all"}` — every candidate changeset.
- `{"mode": "since_date", "date": "2026-06-20"}` — changesets created on/after the ISO date.
- `{"mode": "since_last_run"}` — since the timestamp recorded by the last successful run (stored in `~/.tfvc-merge/state/`).

`--since YYYY-MM-DD` on the command line overrides the profile's cutover for a single run.

## Common invocations

**Dry run — what's eligible?**

```
<python> scripts/tfvc_merge.py candidates --profile clients/acme.json --merge dev-to-test
```

Prints one line per candidate with author, ADO-resolved created date, linked work items, and comment.

**Perform the merge end-to-end:**

```
<python> scripts/tfvc_merge.py run --profile clients/acme.json --merge dev-to-test
```

Steps the orchestrator runs:

1. Verify `tf.exe` resolves, profile loads, target workspace has no pending changes.
2. `tf get` latest of the target's local path.
3. `tf merge /candidate` against source→target, cross-reference each candidate with ADO REST for created-date, author, comment, and linked work items.
4. Filter by `cutover` rule.
5. **Per-changeset loop, chronological order:** `tf merge /version:C~C` → `tf resolve /auto:AutoMerge` → if conflicts remain, `tf undo` and record as skipped; otherwise keep the pending merge.
6. `tf checkin` the accumulated successful merges with a generated comment (`Merge dev → test: N changeset(s)` + one line per merged C#).
7. For each work item touched by a merged changeset, POST a "Fixed in Changeset N" artifact link on the new target changeset.
8. Write run artifacts (`summary.json`, `report.html`, `report.txt`, `email.json`) under `~/.tfvc-merge/runs/<client>.<merge>.<timestamp>/`.
9. Emit the email — see **Notifications** below.

**Re-render the email from a past run dir:**

```
<python> scripts/tfvc_merge.py report ~/.tfvc-merge/runs/acme.dev-to-test.20260630-014500
```

## Notifications

Two send paths, picked per profile (`notify_via`) or per CLI (`--notify-via`):

- **`mcp` (default, recommended for Claude-driven runs).** The orchestrator writes a sidecar `email.json` in the run log directory containing `{to, subject, html, text}`. The calling Claude session (interactive or headless via Claude Code Remote) then calls the **`mcp__ms365__send-mail`** tool from the M365 MCP server with that payload. The orchestrator prints `MCP_PAYLOAD=<path>` so Claude knows where to look.
- **`smtp` (fallback for pure Task Scheduler with no Claude in the loop).** Pure-stdlib `smtplib`; requires `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM` env vars (default host `smtp.office365.com:587`, STARTTLS).

Recipients are resolved CLI > merge-spec `notify_recipients` > profile-level `notify_recipients`.

## Scheduled (unattended) runs

The bundled PowerShell wrapper logs to `<RunsDir>/_logs/<profile>.<merge>.<stamp>.log` and propagates the orchestrator's exit code (0 success / 2 hard failure) so Task Scheduler reflects it.

Example action (Run whether user is logged on or not):

```
Program: powershell.exe
Args:    -NoProfile -ExecutionPolicy Bypass
         -File "C:\Users\ChadDalton\source\repos\cloud-beacon-skills\plugins\ab-code-review\skills\tfvc-merge\scripts\scheduled\run_merge.ps1"
         -Profile "C:\path\to\clients\acme.json"
         -Merge dev-to-test
         -PythonExe "C:\Python313\python.exe"
         -NotifyVia smtp
```

For Claude-in-the-loop scheduled runs (preferred while iterating), use Claude Code Remote's scheduling and have it invoke the skill, then send via the M365 MCP tool from the same session.

## Output

For each run:

- `~/.tfvc-merge/runs/<client>.<merge>.<stamp>/summary.json` — structured run record.
- `report.html` / `report.txt` — what gets emailed (also saved locally).
- `email.json` — MCP send payload (when `notify_via=mcp`).
- `~/.tfvc-merge/state/<profile-basename>.<merge>.json` — last-run timestamp (for `since_last_run`).

Stdout from `candidates` is a plain table; `run` emits progress + the `MCP_PAYLOAD=` line on success.

## Which tf client?

Two supported clients, chosen via profile:

- **Team Explorer Everywhere (`tf.cmd`, TEE-CLC)** — Microsoft's Java-based standalone TFVC client. **Recommended for unattended automation.** Accepts PAT `/login:.,<PAT>` reliably against ADO Services, has no VS-cache dependency, works headless. Install: download `TEE-CLC-14.x.x` from https://github.com/microsoft/team-explorer-everywhere/releases, extract, set `"tf_exe": "C:/Tools/TEE-CLC/tf.cmd"` and `"tf_dialect": "tee"` in the profile (dialect is auto-detected from the `.cmd` extension too).
- **Visual Studio's `tf.exe`** — default when nothing else is configured. Fine for interactive testing on a developer laptop where VS is already signed in. Often rejects PAT `/login` against ADO Services (TF30063); on Services orgs, prefer TEE.

The skill auto-picks the command dialect (`tf vc dir` for VS vs `tf dir` for TEE, `/flag` vs `-flag`) — you only need to point `tf_exe` at the right binary.

## Troubleshooting

- **`TF30063: You are not authorized`** — the pre-flight surfaces this instead of silently returning 0 candidates. On ADO Services with VS's `tf.exe`, switch to TEE-CLC (see above). If you're already on TEE, verify the PAT owner has project Contributor access via ADO web UI (Project Settings → Permissions).
- **`tf.exe not found`** — install Visual Studio with Team Explorer, install TEE-CLC (recommended), set `$env:TF_EXE`, or add `tf_exe` to the profile pointing at the absolute path.
- **`workspace has pending changes`** — the target local path already has uncommitted work. Resolve or shelve those before running.
- **HTTP 401/403 on ADO** — PAT missing / expired / wrong scope. tfvc-merge needs **Code (Read & Write)** + **Work Items (Read & Write)** — broader than tfvc-fetch.
- **`checkin produced no changeset id`** — usually means `tf checkin` rejected the comment, a check-in policy blocked it, or there were no pending changes after the loop. The summary captures the raw `tf` output for inspection.
- **A changeset was skipped that you wanted merged** — the conflict file list in the email points at the X++ metadata file that couldn't auto-merge. Open the source and target sides in Visual Studio, hand-merge, then re-run; once that source changeset's WI shows a target-branch integration link the next nightly run won't pick it up again.
- **Dependency warning fired** — a skipped changeset and a later merged changeset share a work item. Check whether the merged piece is incomplete without the skipped one.

## Related skills

- [tfvc-fetch](../tfvc-fetch/SKILL.md) — read-only diff retrieval. Use to inspect a candidate changeset before deciding to run a merge.
- [xpp-code-review](../xpp-code-review/SKILL.md) — apply Alta Beacon's 19-category X++ review framework to the merged result before letting it ride to production.
