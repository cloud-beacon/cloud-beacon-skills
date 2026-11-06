"""
_report.py — build the HTML email body summarizing a tfvc-merge run.

Sections:
  - Header: client, merge name (e.g. dev-to-test), wall time, target changeset URL (if checked in)
  - Merged table: changeset id, author, work item(s), comment line
  - Skipped table: changeset id, reason ("conflicts in N file(s)"), conflict file list
  - Warnings: dependency hints (skipped changeset's WI also appears in a later merged one),
              empty-merge note, pending-changes-on-arrival note
  - Footer: command line, run log path

Plain-text fallback rendered alongside so SMTP/text-only clients still get the
gist.
"""

import html
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ChangesetRow:
    id: int
    author: str = ""
    comment: str = ""
    work_items: List[dict] = field(default_factory=list)   # [{"id":..., "title":..., "url":...}]
    conflict_files: List[str] = field(default_factory=list)
    skip_reason: str = ""


@dataclass
class RunSummary:
    client: str
    merge_name: str
    source_branch: str
    target_branch: str
    cutover_description: str
    started_at: str
    finished_at: str
    duration_seconds: float
    merged: List[ChangesetRow] = field(default_factory=list)
    skipped: List[ChangesetRow] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    target_changeset_id: Optional[int] = None
    target_changeset_url: Optional[str] = None
    error: Optional[str] = None              # set when the run hard-failed
    run_log_dir: Optional[str] = None
    command_line: Optional[str] = None


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def build_subject(s: RunSummary) -> str:
    if s.error:
        return f"[tfvc-merge] {s.client} {s.merge_name}: FAILED"
    parts = [f"{len(s.merged)} merged"]
    if s.skipped:
        parts.append(f"{len(s.skipped)} skipped")
    if s.target_changeset_id:
        parts.append(f"-> C{s.target_changeset_id}")
    return f"[tfvc-merge] {s.client} {s.merge_name}: {', '.join(parts)}"


def build_html(s: RunSummary) -> str:
    rows_merged = _rows_merged_html(s.merged)
    rows_skipped = _rows_skipped_html(s.skipped)
    warnings_html = _warnings_html(s.warnings)
    error_html = _error_html(s.error)
    header_html = _header_html(s)
    footer_html = _footer_html(s)
    return _PAGE.format(
        title=html.escape(build_subject(s)),
        header=header_html,
        error=error_html,
        rows_merged=rows_merged,
        rows_skipped=rows_skipped,
        warnings=warnings_html,
        footer=footer_html,
    )


def build_text(s: RunSummary) -> str:
    lines = [build_subject(s), ""]
    lines.append(f"Client:      {s.client}")
    lines.append(f"Merge:       {s.merge_name}")
    lines.append(f"Source:      {s.source_branch}")
    lines.append(f"Target:      {s.target_branch}")
    lines.append(f"Cutover:     {s.cutover_description}")
    lines.append(f"Started:     {s.started_at}")
    lines.append(f"Finished:    {s.finished_at}  ({s.duration_seconds:.1f}s)")
    if s.target_changeset_id:
        url = f" — {s.target_changeset_url}" if s.target_changeset_url else ""
        lines.append(f"Result:      checked in as C{s.target_changeset_id}{url}")
    if s.error:
        lines += ["", f"ERROR: {s.error}"]

    lines += ["", f"--- Merged ({len(s.merged)}) ---"]
    for r in s.merged:
        wi = ", ".join(_wi_brief(w) for w in r.work_items) or "(no WI)"
        comment = r.comment.replace("\n", " ")[:120]
        lines.append(f"  C{r.id}  {r.author or '?'}  [{wi}]  {comment}")

    if s.skipped:
        lines += ["", f"--- Skipped ({len(s.skipped)}) ---"]
        for r in s.skipped:
            lines.append(f"  C{r.id}  {r.author or '?'}  reason: {r.skip_reason}")
            for f_ in r.conflict_files:
                lines.append(f"      conflict: {f_}")

    if s.warnings:
        lines += ["", "--- Warnings ---"]
        for w in s.warnings:
            lines.append(f"  * {w}")

    if s.run_log_dir:
        lines += ["", f"Run log: {s.run_log_dir}"]
    if s.command_line:
        lines.append(f"Command: {s.command_line}")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# Internals
# --------------------------------------------------------------------------- #
def _wi_brief(w: dict) -> str:
    wid = w.get("id")
    title = w.get("title", "")
    return f"#{wid} {title}" if title else f"#{wid}"


def _header_html(s: RunSummary) -> str:
    target_line = ""
    if s.target_changeset_id:
        if s.target_changeset_url:
            target_line = (f"<p><b>Result:</b> checked in as "
                           f"<a href=\"{html.escape(s.target_changeset_url)}\">"
                           f"C{s.target_changeset_id}</a></p>")
        else:
            target_line = f"<p><b>Result:</b> checked in as C{s.target_changeset_id}</p>"
    return f"""
<table cellpadding="4">
  <tr><td><b>Client</b></td><td>{html.escape(s.client)}</td></tr>
  <tr><td><b>Merge</b></td><td>{html.escape(s.merge_name)}</td></tr>
  <tr><td><b>Source -> Target</b></td><td>{html.escape(s.source_branch)} -> {html.escape(s.target_branch)}</td></tr>
  <tr><td><b>Cutover</b></td><td>{html.escape(s.cutover_description)}</td></tr>
  <tr><td><b>Started</b></td><td>{html.escape(s.started_at)}</td></tr>
  <tr><td><b>Finished</b></td><td>{html.escape(s.finished_at)} ({s.duration_seconds:.1f}s)</td></tr>
</table>
{target_line}
"""


def _error_html(err):
    if not err:
        return ""
    return (f"<div style=\"background:#fde;padding:8px;border:1px solid #c44;\">"
            f"<b>Hard failure:</b> {html.escape(err)}</div>")


def _rows_merged_html(rows: List[ChangesetRow]) -> str:
    if not rows:
        return "<p><i>No changesets merged.</i></p>"
    out = ["<table cellpadding=\"4\" border=\"1\" style=\"border-collapse:collapse;\">",
           "<tr><th>Changeset</th><th>Author</th><th>Work items</th><th>Comment</th></tr>"]
    for r in rows:
        wi = "<br>".join(_wi_link_html(w) for w in r.work_items) or "<i>(none)</i>"
        out.append(
            f"<tr><td>C{r.id}</td><td>{html.escape(r.author)}</td>"
            f"<td>{wi}</td><td>{html.escape(r.comment)}</td></tr>"
        )
    out.append("</table>")
    return "\n".join(out)


def _rows_skipped_html(rows: List[ChangesetRow]) -> str:
    if not rows:
        return ""
    out = ["<h3>Skipped changesets</h3>",
           "<table cellpadding=\"4\" border=\"1\" style=\"border-collapse:collapse;\">",
           "<tr><th>Changeset</th><th>Author</th><th>Reason</th><th>Conflicting files</th></tr>"]
    for r in rows:
        files = "<br>".join(html.escape(f_) for f_ in r.conflict_files) or "<i>(none listed)</i>"
        out.append(
            f"<tr><td>C{r.id}</td><td>{html.escape(r.author)}</td>"
            f"<td>{html.escape(r.skip_reason)}</td><td>{files}</td></tr>"
        )
    out.append("</table>")
    return "\n".join(out)


def _wi_link_html(w: dict) -> str:
    wid = w.get("id")
    title = html.escape(w.get("title", ""))
    url = w.get("url", "")
    label = f"#{wid} {title}" if title else f"#{wid}"
    if url:
        return f"<a href=\"{html.escape(url)}\">{label}</a>"
    return label


def _warnings_html(warnings: List[str]) -> str:
    if not warnings:
        return ""
    items = "".join(f"<li>{html.escape(w)}</li>" for w in warnings)
    return f"<h3>Warnings</h3><ul>{items}</ul>"


def _footer_html(s: RunSummary) -> str:
    parts = []
    if s.run_log_dir:
        parts.append(f"<p style=\"color:#666;font-size:11px\">Run log: "
                     f"<code>{html.escape(s.run_log_dir)}</code></p>")
    if s.command_line:
        parts.append(f"<p style=\"color:#666;font-size:11px\">Command: "
                     f"<code>{html.escape(s.command_line)}</code></p>")
    return "\n".join(parts)


_PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>{title}</title></head>
<body style="font-family:Segoe UI,Arial,sans-serif;color:#222">
<h2>{title}</h2>
{header}
{error}
<h3>Merged changesets</h3>
{rows_merged}
{rows_skipped}
{warnings}
<hr>
{footer}
</body></html>
"""
