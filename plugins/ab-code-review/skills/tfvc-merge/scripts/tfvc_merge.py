#!/usr/bin/env python3
"""
tfvc_merge.py — orchestrate an unattended TFVC merge from a lower branch to a
higher one for an Alta Beacon client. Python 3 stdlib only.

Subcommands:
  candidates   List changesets eligible to promote, with WI titles (dry run).
  run          Perform the merge end-to-end and emit run artifacts.
  report       Re-render the email from a previous run directory.

Designed to run BOTH:
  • Interactively from a Claude Code session (the skill walks the user
    through invocation, then Claude reads the JSON sidecar and calls the M365
    MCP tool to send the email).
  • Unattended from Windows Task Scheduler (PowerShell wrapper in
    scripts/scheduled/run_merge.ps1; SMTP fallback path in _notify.py).

See SKILL.md for invocation examples and profile schema.
"""

import argparse
import datetime as dt
import json
import os
import sys
import time
import traceback
from typing import List, Optional

# Allow running as `python tfvc_merge.py` (script dir on sys.path).
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import _ado
import _tf
import _xpp_xml
import _report
import _notify


# --------------------------------------------------------------------------- #
# Profile resolution
# --------------------------------------------------------------------------- #
def resolve_merge_spec(profile: dict, merge_name: str) -> dict:
    merges = profile.get("merges") or []
    for m in merges:
        if m.get("name") == merge_name:
            return m
    sys.exit(f"error: merge {merge_name!r} not found in profile. "
             f"available: {[m.get('name') for m in merges]}")


def resolve_workspace_root(profile: dict, merge_spec: dict, override: Optional[str]) -> str:
    return (override
            or merge_spec.get("workspace_root")
            or profile.get("workspace_root")
            or "")


# --------------------------------------------------------------------------- #
# Cutover (which candidates qualify)
# --------------------------------------------------------------------------- #
def cutover_description(cutover: dict, state: dict) -> str:
    mode = (cutover or {}).get("mode", "all")
    if mode == "all":
        return "all candidate changesets"
    if mode == "since_date":
        return f"since {cutover.get('date')}"
    if mode == "since_last_run":
        last = state.get("last_run_at")
        return f"since last run ({last})" if last else "since last run (first run — all)"
    return mode


def filter_candidates_by_cutover(candidates: List[dict], cutover: dict,
                                 state: dict) -> List[dict]:
    """`candidates` items must include a parsed ISO 'created' if cutover is date-based."""
    mode = (cutover or {}).get("mode", "all")
    if mode == "all":
        return list(candidates)
    if mode == "since_date":
        threshold = _parse_iso(cutover["date"])
    elif mode == "since_last_run":
        last = state.get("last_run_at")
        threshold = _parse_iso(last) if last else None
    else:
        sys.exit(f"error: unknown cutover.mode {mode!r}")
    if threshold is None:
        return list(candidates)
    out = []
    for c in candidates:
        created = c.get("created")
        if not created:
            out.append(c)  # no date info — keep, surfaced in the report
            continue
        try:
            if _parse_iso(created) >= threshold:
                out.append(c)
        except ValueError:
            out.append(c)
    return out


def _parse_iso(s: str) -> dt.datetime:
    # Accept "YYYY-MM-DD", "YYYY-MM-DDTHH:MM:SS", and the trailing-Z form ADO returns.
    if not s:
        raise ValueError("empty date")
    s = s.rstrip("Z")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"unparseable date {s!r}")


# --------------------------------------------------------------------------- #
# Candidate discovery
# --------------------------------------------------------------------------- #
def _tf_env(profile: dict) -> Optional[dict]:
    """Build the env-var overlay TEE-CLC needs at runtime.

    TEE-CLC's tf.cmd on Windows requires ``java`` on PATH and (usually)
    ``JAVA_HOME`` set. When the profile supplies ``java_home``, we add it
    to PATH and set JAVA_HOME for the subprocess. This lets scheduled
    tasks work without polluting the machine's system PATH.
    """
    java_home = profile.get("java_home")
    if not java_home:
        return None
    java_home = os.path.expanduser(os.path.expandvars(java_home))
    java_bin = os.path.join(java_home, "bin")
    parent_path = os.environ.get("PATH", "")
    return {
        "JAVA_HOME": java_home,
        "PATH": f"{java_bin}{os.pathsep}{parent_path}" if java_bin not in parent_path else parent_path,
    }


def preflight_auth(tf: _tf.Tf, merge_spec: dict) -> None:
    """Fail loudly if tf.exe/tf.cmd can't authenticate to the collection.

    Silent 0-candidate results are almost always TF30063 — the merge_candidates
    call returns a nonzero exit code but our parser produces 0 blocks. That
    looks identical to a legitimate "nothing to merge". Do a quick server-
    touching read here so an auth failure is surfaced as an exception before
    the run continues.
    """
    src = merge_spec["source_branch"]
    res = tf.run("vc", "dir", src, check=False)
    body = (res.stdout + "\n" + res.stderr)
    if "TF30063" in body or "Access denied connecting to TFS" in body:
        raise _tf.TfError(res,
            "tf could not authenticate to the TFVC collection. "
            "For ADO Services, use TEE-CLC's tf.cmd with tf_use_pat_login: true. "
            "If TEE also fails with 'Access denied', the PAT likely can't be used "
            "for TFVC — check whether the PAT owner is a guest AAD user (guest "
            "PAT-for-TFVC is often blocked by tenant policy) or ask for a PAT "
            "issued by a native-tenant service account.")
    if not res.ok and "not found" in body.lower():
        raise _tf.TfError(res,
            f"tf could not resolve the source branch {src!r}. "
            "Check source_branch/target_branch server paths in the profile.")


def discover_candidates(tf: _tf.Tf, client: _ado.Client,
                        merge_spec: dict) -> List[dict]:
    """Return list of candidate dicts:
       {id, user, comment, created (ISO), work_items:[{id,title,url}]}.
    """
    src = merge_spec["source_branch"]
    tgt = merge_spec["target_branch"]
    res = tf.merge_candidates(src, tgt)
    if not res.ok and res.stdout.strip().lower().startswith("no changes to merge"):
        return []
    if not res.ok and "no changes" in (res.stdout + res.stderr).lower():
        return []
    candidates = _tf.parse_candidates(res.stdout)

    enriched = []
    for cand in candidates:
        cs_id = cand["id"]
        # ADO REST gives us authoritative createdDate + comment.
        try:
            cs = _ado.get_changeset(client, cs_id)
            cand["created"] = cs.get("createdDate", "")
            if not cand.get("comment"):
                cand["comment"] = cs.get("comment", "") or ""
            cand["author"] = ((cs.get("author") or {}).get("displayName")
                              or (cs.get("checkedInBy") or {}).get("displayName")
                              or cand.get("user", ""))
        except _ado.AdoError as e:
            cand["created"] = ""
            cand["author"] = cand.get("user", "")
            cand.setdefault("warnings", []).append(f"ADO changeset lookup failed: {e}")

        try:
            wis = _ado.get_changeset_workitems(client, cs_id)
        except _ado.AdoError:
            wis = []
        cand["work_items"] = []
        for wi in wis:
            wid = wi.get("id") or (wi.get("workItem") or {}).get("id")
            if not wid:
                continue
            try:
                w = _ado.get_workitem(client, wid)
                cand["work_items"].append({
                    "id": w["id"], "title": w["title"], "url": w["url"],
                    "type": w["type"], "state": w["state"],
                })
            except _ado.AdoError:
                cand["work_items"].append({"id": int(wid), "title": "", "url": "", "type": "", "state": ""})
        enriched.append(cand)
    return enriched


# --------------------------------------------------------------------------- #
# Per-changeset merge loop
# --------------------------------------------------------------------------- #
def merge_one(tf: _tf.Tf, merge_spec: dict, cand: dict) -> dict:
    """Attempt to merge a single changeset. Returns a dict:
       {id, status: 'merged'|'skipped'|'empty', conflict_files: [...], detail: '...'}

    On 'skipped' the workspace is rolled back via `tf undo` on the affected paths
    so subsequent merges aren't polluted by half-applied state.
    """
    src = merge_spec["source_branch"]
    tgt = merge_spec["target_branch"]
    cs_id = cand["id"]

    merge_res = tf.merge_changeset(src, tgt, cs_id)
    out = (merge_res.stdout + "\n" + merge_res.stderr)

    if "no changes to merge" in out.lower() or "already merged" in out.lower():
        return {"id": cs_id, "status": "empty", "conflict_files": [],
                "detail": "no changes to merge for this changeset"}

    # Try to auto-merge anything tf says is mergeable.
    tf.auto_resolve(merge_spec.get("target_local_path") or ".")

    conflicts_res = tf.list_conflicts(merge_spec.get("target_local_path") or ".")
    conflicts = _tf.parse_conflicts(conflicts_res.stdout)

    if conflicts:
        # Roll back this changeset's pending merge and skip.
        tf.undo(merge_spec.get("target_local_path") or ".")
        return {"id": cs_id, "status": "skipped",
                "conflict_files": conflicts,
                "detail": f"{len(conflicts)} unresolved conflict(s) after AutoMerge"}

    if not merge_res.ok and "conflict" not in out.lower():
        # Genuine tf error (not a conflict). Roll back and mark skipped with the
        # tf stderr as the reason.
        tf.undo(merge_spec.get("target_local_path") or ".")
        return {"id": cs_id, "status": "skipped",
                "conflict_files": [],
                "detail": (merge_res.stderr or merge_res.stdout).strip()[:200] or "tf merge failed"}

    return {"id": cs_id, "status": "merged", "conflict_files": [], "detail": "clean"}


# --------------------------------------------------------------------------- #
# Check-in
# --------------------------------------------------------------------------- #
def build_checkin_comment(merge_spec: dict, merged_rows: List[_report.ChangesetRow]) -> str:
    header = f"Merge {merge_spec.get('source_branch_short') or merge_spec['source_branch']} -> " \
             f"{merge_spec.get('target_branch_short') or merge_spec['target_branch']}: " \
             f"{len(merged_rows)} changeset(s)"
    lines = [header, ""]
    for r in merged_rows:
        wi = ", ".join(f"WI {w['id']}" for w in r.work_items) or "no WI"
        first_line = (r.comment or "").splitlines()[0] if r.comment else ""
        lines.append(f"C{r.id} [{wi}] {first_line}".rstrip())
    return "\n".join(lines)


def detect_dependency_warnings(merged: List[_report.ChangesetRow],
                               skipped: List[_report.ChangesetRow]) -> List[str]:
    """Flag any skipped changeset whose work-item IDs also appear on a later
    merged changeset — almost always a sign you should hand-merge the skipped
    one to keep the WI coherent."""
    warnings = []
    skipped_wi_to_cs = {}
    for r in skipped:
        for w in r.work_items:
            skipped_wi_to_cs.setdefault(w["id"], []).append(r.id)

    for r in merged:
        for w in r.work_items:
            if w["id"] in skipped_wi_to_cs:
                hits = ", ".join(f"C{c}" for c in skipped_wi_to_cs[w["id"]])
                warnings.append(
                    f"Work item #{w['id']} appears on merged C{r.id} but a related "
                    f"changeset was skipped ({hits}). Manual review recommended."
                )
    return warnings


# --------------------------------------------------------------------------- #
# Run state (for since_last_run cutover)
# --------------------------------------------------------------------------- #
def load_state(profile_path: str, merge_name: str) -> dict:
    state_path = _state_path(profile_path, merge_name)
    if not os.path.isfile(state_path):
        return {}
    try:
        with open(state_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(profile_path: str, merge_name: str, state: dict) -> None:
    p = _state_path(profile_path, merge_name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)


def _state_path(profile_path: str, merge_name: str) -> str:
    base = os.path.splitext(os.path.basename(profile_path or "default"))[0]
    return os.path.join(os.path.expanduser("~"), ".tfvc-merge", "state",
                        f"{base}.{merge_name}.json")


# --------------------------------------------------------------------------- #
# Subcommands
# --------------------------------------------------------------------------- #
def cmd_candidates(args):
    profile = _ado.load_profile(args.profile)
    merge_spec = resolve_merge_spec(profile, args.merge)
    pat = _ado.resolve_pat(profile, args.pat_env)
    client = _ado.Client(_ado.resolve_base_url(profile, args.org_base_url),
                         pat,
                         profile.get("api_version") or _ado.API_VERSION)
    tf = _tf.Tf(_tf.find_tf_exe(profile.get("tf_exe")),
                cwd=resolve_workspace_root(profile, merge_spec, args.workspace_root),
                pat=pat, use_pat_login=bool(profile.get("tf_use_pat_login")),
                dialect=profile.get("tf_dialect"),
                pat_username=profile.get("pat_username"),
                env=_tf_env(profile))
    preflight_auth(tf, merge_spec)
    cands = discover_candidates(tf, client, merge_spec)

    cutover = merge_spec.get("cutover", {"mode": "all"})
    if args.since:
        cutover = {"mode": "since_date", "date": args.since}
    state = load_state(args.profile, args.merge)
    filtered = filter_candidates_by_cutover(cands, cutover, state)

    print(f"# candidates: {merge_spec['source_branch']} -> {merge_spec['target_branch']}")
    print(f"# cutover: {cutover_description(cutover, state)}")
    print(f"# total before filter: {len(cands)} / after filter: {len(filtered)}")
    print()
    for c in filtered:
        wis = ", ".join(f"#{w['id']} {w['title']}" for w in c["work_items"]) or "(no WI)"
        first = (c.get("comment") or "").splitlines()[0]
        print(f"C{c['id']:>7}  {c.get('created', '?'):<28}  {c.get('author', '?'):<24}  "
              f"[{wis}]  {first}")


def cmd_run(args):
    started = dt.datetime.now()
    started_iso = started.isoformat(timespec="seconds")
    t0 = time.monotonic()

    profile = _ado.load_profile(args.profile)
    merge_spec = resolve_merge_spec(profile, args.merge)
    ws_root = resolve_workspace_root(profile, merge_spec, args.workspace_root)
    client_name = (profile.get("client") or
                   os.path.splitext(os.path.basename(args.profile or "client"))[0])

    run_log_dir = _new_run_log_dir(args.runs_dir, client_name, args.merge, started)
    os.makedirs(run_log_dir, exist_ok=True)

    summary = _report.RunSummary(
        client=client_name,
        merge_name=args.merge,
        source_branch=merge_spec["source_branch"],
        target_branch=merge_spec["target_branch"],
        cutover_description="",        # filled in below
        started_at=started_iso,
        finished_at="",                # filled in at the end
        duration_seconds=0,
        run_log_dir=run_log_dir,
        command_line=" ".join(sys.argv),
    )

    try:
        pat = _ado.resolve_pat(profile, args.pat_env)
        client = _ado.Client(_ado.resolve_base_url(profile, args.org_base_url),
                             pat,
                             profile.get("api_version") or _ado.API_VERSION)
        tf = _tf.Tf(_tf.find_tf_exe(profile.get("tf_exe")), cwd=ws_root, pat=pat,
                    use_pat_login=bool(profile.get("tf_use_pat_login")),
                    dialect=profile.get("tf_dialect"),
                    pat_username=profile.get("pat_username"),
                    env=_tf_env(profile))
        preflight_auth(tf, merge_spec)

        # Pre-flight: workspace has no pending changes in the target tree.
        target_local = merge_spec.get("target_local_path") or ws_root
        status = tf.status(target_local)
        if "There are no matching pending changes." not in status.stdout and status.stdout.strip():
            raise RuntimeError(
                f"workspace has pending changes under {target_local}; resolve "
                "or shelve them before running tfvc-merge.\n\n" + status.stdout[:1500])

        # Get latest of target.
        tf.get_latest(target_local)

        # Discover and filter candidates.
        cands = discover_candidates(tf, client, merge_spec)
        cutover = merge_spec.get("cutover", {"mode": "all"})
        if args.since:
            cutover = {"mode": "since_date", "date": args.since}
        state = load_state(args.profile, args.merge)
        summary.cutover_description = cutover_description(cutover, state)
        cands_in_scope = filter_candidates_by_cutover(cands, cutover, state)

        if not cands_in_scope:
            summary.warnings.append("No candidate changesets in scope — nothing to merge.")
        else:
            # Per-changeset loop, chronological order.
            for cand in cands_in_scope:
                result = merge_one(tf, merge_spec, cand)
                row = _report.ChangesetRow(
                    id=cand["id"],
                    author=cand.get("author", ""),
                    comment=cand.get("comment", ""),
                    work_items=cand.get("work_items", []),
                )
                if result["status"] == "merged":
                    summary.merged.append(row)
                elif result["status"] == "empty":
                    summary.warnings.append(
                        f"C{cand['id']}: empty merge (already merged or no changes).")
                else:
                    row.conflict_files = result["conflict_files"]
                    row.skip_reason = result["detail"]
                    summary.skipped.append(row)

            # Check in the accumulated successful merges.
            if summary.merged:
                comment = build_checkin_comment(merge_spec, summary.merged)
                checkin = tf.checkin(target_local, comment)
                new_id = _tf.changeset_id_from_checkin(checkin.stdout or "")
                if checkin.ok and new_id:
                    summary.target_changeset_id = new_id
                    summary.target_changeset_url = _changeset_url(client.base, new_id)
                    # Link each source WI → new changeset.
                    for r in summary.merged:
                        for w in r.work_items:
                            try:
                                _ado.link_workitem_to_changeset(
                                    client, w["id"], new_id,
                                    comment=f"Integrated by tfvc-merge ({args.merge})")
                            except _ado.AdoError as e:
                                summary.warnings.append(
                                    f"Could not link WI #{w['id']} to C{new_id}: {e}")
                else:
                    summary.warnings.append(
                        "tf checkin did not report a new changeset id — "
                        "pending changes may still be in the workspace.\n" +
                        (checkin.stderr or checkin.stdout)[:500])
                    summary.error = "checkin produced no changeset id"

        summary.warnings.extend(detect_dependency_warnings(summary.merged, summary.skipped))

    except (_tf.TfError, _ado.AdoError, RuntimeError) as e:
        summary.error = str(e)
        summary.warnings.append("Run aborted; see error.")
    except Exception:
        summary.error = "Unhandled exception:\n" + traceback.format_exc()

    finished = dt.datetime.now()
    summary.finished_at = finished.isoformat(timespec="seconds")
    summary.duration_seconds = time.monotonic() - t0

    _persist_run(run_log_dir, summary)

    # Update state so the next since_last_run picks up here.
    if not summary.error:
        save_state(args.profile, args.merge,
                   {"last_run_at": summary.finished_at,
                    "last_target_changeset": summary.target_changeset_id})

    # Recipients: CLI > merge spec > profile-level.
    recipients = (args.notify or
                  merge_spec.get("notify_recipients") or
                  profile.get("notify_recipients") or [])
    if not recipients:
        print("note: no notify recipients configured; skipping email.", file=sys.stderr)
        return 0 if not summary.error else 2

    subject = _report.build_subject(summary)
    html_body = _report.build_html(summary)
    text_body = _report.build_text(summary)

    notify_via = (args.notify_via or
                  merge_spec.get("notify_via") or
                  profile.get("notify_via") or "mcp")
    if notify_via == "smtp":
        _notify.send_smtp(to=recipients, subject=subject,
                          html_body=html_body, text_body=text_body)
        print(f"sent SMTP email to {len(recipients)} recipient(s).")
    else:
        payload_path = os.path.join(run_log_dir, "email.json")
        _notify.write_mcp_payload(payload_path, to=recipients,
                                  subject=subject, html_body=html_body,
                                  text_body=text_body)
        print(f"MCP_PAYLOAD={payload_path}")

    return 0 if not summary.error else 2


def cmd_report(args):
    """Re-render the email body from a previous run's summary.json."""
    summary_path = os.path.join(args.run_dir, "summary.json")
    with open(summary_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    summary = _summary_from_dict(data)
    if args.text:
        sys.stdout.write(_report.build_text(summary))
    else:
        sys.stdout.write(_report.build_html(summary))


# --------------------------------------------------------------------------- #
# Persistence
# --------------------------------------------------------------------------- #
def _new_run_log_dir(base: str, client: str, merge_name: str, started: dt.datetime) -> str:
    base = base or os.path.join(os.path.expanduser("~"), ".tfvc-merge", "runs")
    stamp = started.strftime("%Y%m%d-%H%M%S")
    return os.path.join(base, f"{client}.{merge_name}.{stamp}")


def _persist_run(run_log_dir: str, summary: _report.RunSummary) -> None:
    os.makedirs(run_log_dir, exist_ok=True)
    with open(os.path.join(run_log_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(_summary_to_dict(summary), fh, indent=2, default=str)
    with open(os.path.join(run_log_dir, "report.html"), "w", encoding="utf-8") as fh:
        fh.write(_report.build_html(summary))
    with open(os.path.join(run_log_dir, "report.txt"), "w", encoding="utf-8") as fh:
        fh.write(_report.build_text(summary))


def _summary_to_dict(s: _report.RunSummary) -> dict:
    return {
        "client": s.client, "merge_name": s.merge_name,
        "source_branch": s.source_branch, "target_branch": s.target_branch,
        "cutover_description": s.cutover_description,
        "started_at": s.started_at, "finished_at": s.finished_at,
        "duration_seconds": s.duration_seconds,
        "target_changeset_id": s.target_changeset_id,
        "target_changeset_url": s.target_changeset_url,
        "error": s.error, "warnings": s.warnings,
        "run_log_dir": s.run_log_dir, "command_line": s.command_line,
        "merged": [_row_to_dict(r) for r in s.merged],
        "skipped": [_row_to_dict(r) for r in s.skipped],
    }


def _row_to_dict(r: _report.ChangesetRow) -> dict:
    return {"id": r.id, "author": r.author, "comment": r.comment,
            "work_items": r.work_items, "conflict_files": r.conflict_files,
            "skip_reason": r.skip_reason}


def _summary_from_dict(d: dict) -> _report.RunSummary:
    s = _report.RunSummary(
        client=d.get("client", ""), merge_name=d.get("merge_name", ""),
        source_branch=d.get("source_branch", ""), target_branch=d.get("target_branch", ""),
        cutover_description=d.get("cutover_description", ""),
        started_at=d.get("started_at", ""), finished_at=d.get("finished_at", ""),
        duration_seconds=float(d.get("duration_seconds", 0) or 0),
        target_changeset_id=d.get("target_changeset_id"),
        target_changeset_url=d.get("target_changeset_url"),
        error=d.get("error"), warnings=list(d.get("warnings") or []),
        run_log_dir=d.get("run_log_dir"), command_line=d.get("command_line"),
    )
    for r in d.get("merged", []):
        s.merged.append(_row_from_dict(r))
    for r in d.get("skipped", []):
        s.skipped.append(_row_from_dict(r))
    return s


def _row_from_dict(d: dict) -> _report.ChangesetRow:
    return _report.ChangesetRow(
        id=d["id"], author=d.get("author", ""), comment=d.get("comment", ""),
        work_items=list(d.get("work_items") or []),
        conflict_files=list(d.get("conflict_files") or []),
        skip_reason=d.get("skip_reason", ""),
    )


def _changeset_url(base_url: str, cs_id: int) -> str:
    return f"{base_url}/_versionControl/changeset/{cs_id}"


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv=None):
    p = argparse.ArgumentParser(description="Alta Beacon TFVC merge orchestrator.")
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--profile", required=True,
                        help="client profile JSON (ado_base_url, pat_env, merges[])")
    common.add_argument("--merge", required=True,
                        help="merge name (matches profile.merges[].name)")
    common.add_argument("--org-base-url", help="override profile.ado_base_url")
    common.add_argument("--pat-env", help="override profile.pat_env")
    common.add_argument("--workspace-root", help="override profile.workspace_root")
    common.add_argument("--since",
                        help="ISO date — override cutover to since_date for this run")

    pc = sub.add_parser("candidates", parents=[common],
                        help="list candidates only (no merge, no checkin)")
    pc.set_defaults(func=cmd_candidates)

    pr = sub.add_parser("run", parents=[common],
                        help="perform the merge end-to-end")
    pr.add_argument("--runs-dir",
                    help="root directory for run logs (default ~/.tfvc-merge/runs)")
    pr.add_argument("--notify", action="append",
                    help="email recipient (repeat for multiple); overrides profile")
    pr.add_argument("--notify-via", choices=["mcp", "smtp"],
                    help="email send path (default: profile.notify_via or 'mcp')")
    pr.set_defaults(func=cmd_run)

    pp = sub.add_parser("report", help="re-render the email from a past run dir")
    pp.add_argument("run_dir", help="path to a run log directory containing summary.json")
    pp.add_argument("--text", action="store_true",
                    help="emit plain text instead of HTML")
    pp.set_defaults(func=cmd_report)

    args = p.parse_args(argv)
    rc = args.func(args)
    sys.exit(int(rc) if rc is not None else 0)


if __name__ == "__main__":
    main()
