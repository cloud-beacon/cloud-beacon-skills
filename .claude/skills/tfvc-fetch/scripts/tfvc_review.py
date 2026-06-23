#!/usr/bin/env python3
"""
tfvc_review.py  (v2 — shelveset-first)

Fetch a TFVC *shelveset* (the artifact behind an Azure DevOps "Code Review"
request) from the REST API and emit a clean, review-ready Markdown diff for
Claude Code to analyze. Also resolves the linked work item as the spec.

Zero external dependencies — Python standard library only.

What changed from v1: the review unit is a shelveset (pre-check-in), identified
by name + owner taken from the CR-request email, fetched directly over REST.
The old changeset path and the --difffile fallback remain available.

Typical use (driven by the /cr-review command or the scheduled task):

    python3 tfvc_review.py \
        --profile clients/buddig.json \
        --shelveset "ADO868_FixLegalEntityField_20260616_0030;ohuerta@cloudbeacon.dev" \
        --cr-id 2471 \
        --out review-input-2471.md

The work item is auto-discovered from the shelveset if --workitem is omitted.
The PAT is read from the env var named by the profile's `pat_env` (default
AZDO_PAT), never passed on the command line.

API: Azure DevOps TFVC REST 7.1
  GET {base}/_apis/tfvc/shelvesets/changes?shelvesetId={name};{owner}
  GET {base}/_apis/tfvc/items?path={p}&versionType={Shelveset|Changeset|Latest}&version={v}
  GET {base}/_apis/tfvc/shelvesets/workitems?shelvesetId={name};{owner}
  GET {base}/_apis/wit/workitems/{id}?$expand=fields
"""

import argparse
import base64
import difflib
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

API_VERSION = "7.1"   # default; override per profile (api_version) or --api-version
TIMEOUT = 60

# Metadata XML elements whose CDATA holds X++ source.
CDATA_RE = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")


# --------------------------------------------------------------------------- #
# Config / profile
# --------------------------------------------------------------------------- #
def load_profile(path):
    """Load a client profile JSON. Returns the dict (may be empty)."""
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def resolve_base_url(args, profile):
    base = args.org_base_url or profile.get("ado_base_url")
    if not base:
        sys.exit("error: no base URL (pass --org-base-url or a --profile with ado_base_url)")
    return base.rstrip("/")


def resolve_pat(args, profile):
    env_name = args.pat_env or profile.get("pat_env") or "AZDO_PAT"
    pat = os.environ.get(env_name)
    if pat:
        return pat.strip()
    pat_file = profile.get("pat_file")
    if pat_file:
        path = os.path.expanduser(os.path.expandvars(pat_file))
        try:
            with open(path, "r", encoding="utf-8") as fh:
                first = fh.readline().strip()
        except OSError as e:
            sys.exit(f"error: cannot read pat_file {path!r}: {e}")
        if first:
            return first
    sys.exit(f"error: PAT not found — set env var {env_name!r} or a profile 'pat_file'")


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
class Client:
    def __init__(self, base, pat, api_version=API_VERSION):
        self.base = base
        self.api_version = api_version
        token = base64.b64encode(f":{pat}".encode("utf-8")).decode("ascii")
        self.auth = f"Basic {token}"

    def _get(self, path, params=None, accept="application/json"):
        params = dict(params or {})
        params.setdefault("api-version", self.api_version)
        url = f"{self.base}{path}?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}"
        req = urllib.request.Request(url, method="GET")
        req.add_header("Authorization", self.auth)
        req.add_header("Accept", accept)
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")[:500]
            sys.exit(f"error: HTTP {e.code} on {path}\n{body}")
        except urllib.error.URLError as e:
            sys.exit(f"error: cannot reach {self.base} ({e.reason})")
        return raw

    def get_json(self, path, params=None):
        return json.loads(self._get(path, params, "application/json").decode("utf-8", "ignore"))

    def get_text(self, path, params=None):
        """Fetch item content. Ask for text/plain; if the server returns JSON
        metadata anyway, dig the content out of it."""
        raw = self._get(path, params, "text/plain")
        text = raw.decode("utf-8", "ignore")
        stripped = text.lstrip()
        if stripped[:1] in "{[":
            try:
                obj = json.loads(text)
                if isinstance(obj, dict) and "content" in obj:
                    return obj["content"]
            except json.JSONDecodeError:
                pass
        return text


# --------------------------------------------------------------------------- #
# Shelveset fetch
# --------------------------------------------------------------------------- #
def get_changes(client, shelveset_id):
    data = client.get_json("/_apis/tfvc/shelvesets/changes",
                           {"shelvesetId": shelveset_id})
    return data.get("value", [])


def get_shelveset(client, shelveset_id):
    """Fetch the deep shelveset to get its check-in comment (Category 9 input)."""
    try:
        data = client.get_json("/_apis/tfvc/shelvesets",
                               {"shelvesetId": shelveset_id, "maxCommentLength": "2000"})
    except SystemExit:
        return {}
    if isinstance(data, dict) and "value" in data:
        vals = data.get("value", [])
        data = vals[0] if vals else {}
    return data if isinstance(data, dict) else {}


def get_item_content(client, path, version_type, version=None):
    """Return (text, is_binary) for a TFVC item at a given version.
    For non-existent sides (adds/deletes) callers pass None and skip."""
    params = {"path": path, "versionType": version_type}
    if version is not None:
        params["version"] = str(version)
    text = client.get_text("/_apis/tfvc/items", params)
    if "\x00" in text[:8000]:
        return "", True
    return text, False


def get_linked_workitems(client, shelveset_id):
    try:
        data = client.get_json("/_apis/tfvc/shelvesets/workitems",
                               {"shelvesetId": shelveset_id})
    except SystemExit:
        return []
    ids = []
    for wi in data.get("value", []):
        wid = wi.get("id") or wi.get("workItem", {}).get("id")
        if wid:
            ids.append(int(wid))
    return ids


def get_workitem_spec(client, wi_id):
    data = client.get_json(f"/_apis/wit/workitems/{wi_id}", {"$expand": "fields"})
    f = data.get("fields", {})
    return {
        "id": wi_id,
        "type": f.get("System.WorkItemType", ""),
        "title": f.get("System.Title", ""),
        "description": strip_html(f.get("System.Description", "")),
        "acceptance": strip_html(f.get("Microsoft.VSTS.Common.AcceptanceCriteria", "")),
        "repro": strip_html(f.get("Microsoft.VSTS.TCM.ReproSteps", "")),
    }


# --------------------------------------------------------------------------- #
# Text helpers
# --------------------------------------------------------------------------- #
def strip_html(s):
    if not s:
        return ""
    s = TAG_RE.sub(" ", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def extract_xpp(xml_text):
    """Concatenate all CDATA blocks (Declaration + method SourceCode) so the
    diff runs on X++ rather than XML scaffolding. Returns '' if no CDATA."""
    blocks = CDATA_RE.findall(xml_text or "")
    if not blocks:
        return ""
    return "\n".join(b.strip("\n") for b in blocks).strip("\n")


def change_tokens(change_type):
    return {t.strip().lower() for t in (change_type or "").split(",") if t.strip()}


def unified(before, after, path, label_before="base", label_after="shelved"):
    b = (before or "").splitlines()
    a = (after or "").splitlines()
    diff = difflib.unified_diff(b, a, fromfile=f"{path} ({label_before})",
                                tofile=f"{path} ({label_after})", lineterm="")
    return "\n".join(diff)


# --------------------------------------------------------------------------- #
# Per-file rendering
# --------------------------------------------------------------------------- #
def render_file(client, shelveset_id, change):
    item = change.get("item", {})
    path = item.get("path", "")
    base_version = item.get("version")
    toks = change_tokens(change.get("changeType", ""))
    is_add = "add" in toks
    is_delete = "delete" in toks

    # after = shelved content (empty for delete)
    if is_delete:
        after, after_bin = "", False
    else:
        after, after_bin = get_item_content(client, path, "Shelveset", shelveset_id)

    # before = base content (empty for add)
    if is_add:
        before, before_bin = "", False
    elif base_version is not None:
        before, before_bin = get_item_content(client, path, "Changeset", base_version)
    else:
        before, before_bin = get_item_content(client, path, "Latest")

    header = f"### {path}\n*change:* `{change.get('changeType','')}`"

    if before_bin or after_bin:
        return f"{header}\n\n_Binary file — diff skipped._\n"

    is_meta_xml = path.lower().endswith(".xml") and (
        "<![CDATA[" in before or "<![CDATA[" in after
    )

    out = [header, ""]
    if is_meta_xml:
        xpp_diff = unified(extract_xpp(before), extract_xpp(after), path)
        if xpp_diff.strip():
            out += ["**X++ source**", "```diff", xpp_diff, "```", ""]
        else:
            out += ["_No X++ source change (metadata-only edit)._", ""]
        raw_diff = unified(before, after, path)
        if raw_diff.strip():
            out += ["<details><summary>Full metadata XML diff</summary>", "",
                    "```diff", raw_diff, "```", "", "</details>", ""]
    else:
        raw_diff = unified(before, after, path)
        out += ["```diff", raw_diff if raw_diff.strip() else "(no textual change)", "```", ""]

    return "\n".join(out)


# --------------------------------------------------------------------------- #
# Report assembly
# --------------------------------------------------------------------------- #
def render_spec(spec):
    lines = [f"## Spec — Work item {spec['id']} ({spec['type']}): {spec['title']}", ""]
    if spec["description"]:
        lines += ["**Description**", spec["description"], ""]
    if spec["acceptance"]:
        lines += ["**Acceptance criteria**", spec["acceptance"], ""]
    if spec["repro"]:
        lines += ["**Repro steps**", spec["repro"], ""]
    return "\n".join(lines)


def build_report(client, shelveset_id, cr_id, workitem_id):
    name, _, owner = shelveset_id.partition(";")
    changes = get_changes(client, shelveset_id)
    shelveset = get_shelveset(client, shelveset_id)
    comment = (shelveset.get("comment") or "").strip()

    head = [f"# Review input — {('CR ' + cr_id) if cr_id else 'Shelveset review'}",
            "",
            f"- **Shelveset:** `{name}`",
            f"- **Owner:** {owner}",
            f"- **Check-in comment:** {comment if comment else '_(none)_'}",
            f"- **Files changed:** {len(changes)}", ""]

    # spec resolution: explicit --workitem, else first linked work item
    wi_ids = [workitem_id] if workitem_id else get_linked_workitems(client, shelveset_id)
    spec_md = ""
    if wi_ids:
        spec = get_workitem_spec(client, wi_ids[0])
        head.append(f"- **Spec work item:** {spec['id']} — {spec['title']}")
        spec_md = "\n" + render_spec(spec)
        if len(wi_ids) > 1:
            head.append(f"- _Other linked work items:_ {', '.join(map(str, wi_ids[1:]))}")
    else:
        head.append("- **Spec work item:** none linked — framework-only review")
    head.append("")

    files_md = ["## Changes", ""]
    for ch in changes:
        files_md.append(render_file(client, shelveset_id, ch))

    return "\n".join(head) + spec_md + "\n\n" + "\n".join(files_md)


# --------------------------------------------------------------------------- #
# --difffile fallback (offline, pre-fetched local diff)
# --------------------------------------------------------------------------- #
def build_from_difffile(diff_path, cr_id):
    with open(diff_path, "r", encoding="utf-8") as fh:
        diff = fh.read()
    title = f"CR {cr_id}" if cr_id else "Local diff review"
    return (f"# Review input — {title}\n\n_Source: local diff file "
            f"`{os.path.basename(diff_path)}`_\n\n## Changes\n\n```diff\n{diff}\n```\n")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv=None):
    p = argparse.ArgumentParser(description="Fetch a TFVC shelveset as a review-ready Markdown diff.")
    p.add_argument("--profile", help="client profile JSON (ado_base_url, pat_env)")
    p.add_argument("--org-base-url", help="e.g. https://buddigd365.visualstudio.com")
    p.add_argument("--pat-env", help="env var holding the PAT (default from profile / AZDO_PAT)")
    p.add_argument("--api-version", help="ADO REST api-version (default from profile api_version, else 7.1)")
    p.add_argument("--shelveset", help='shelveset id as "name;owner"')
    p.add_argument("--shelveset-name")
    p.add_argument("--shelveset-owner")
    p.add_argument("--cr-id", help="code-review id for labeling the report")
    p.add_argument("--workitem", type=int, help="spec work item id (else auto-discovered)")
    p.add_argument("--difffile", help="offline fallback: pre-generated unified diff")
    p.add_argument("--out", help="write report here (default: stdout)")
    args = p.parse_args(argv)

    if args.difffile:
        report = build_from_difffile(args.difffile, args.cr_id)
    else:
        profile = load_profile(args.profile)
        shelveset_id = args.shelveset
        if not shelveset_id and args.shelveset_name and args.shelveset_owner:
            shelveset_id = f"{args.shelveset_name};{args.shelveset_owner}"
        if not shelveset_id:
            sys.exit("error: provide --shelveset \"name;owner\" (or --difffile)")
        api_version = args.api_version or profile.get("api_version") or API_VERSION
        client = Client(resolve_base_url(args, profile), resolve_pat(args, profile), api_version)
        report = build_report(client, shelveset_id, args.cr_id, args.workitem)

    if args.out:
        out_dir = os.path.dirname(os.path.abspath(args.out))
        os.makedirs(out_dir, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"wrote {args.out} ({len(report)} bytes)")
    else:
        sys.stdout.write(report)


if __name__ == "__main__":
    main()
