"""
_ado.py — Azure DevOps REST helpers for tfvc-merge.

Adapted from tfvc-fetch/scripts/tfvc_review.py so behavior stays consistent
across Alta Beacon skills. Python 3 stdlib only.
"""

import base64
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

API_VERSION = "7.1"
TIMEOUT = 60

TAG_RE = re.compile(r"<[^>]+>")


def load_profile(path):
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def resolve_base_url(profile, override=None):
    base = override or profile.get("ado_base_url")
    if not base:
        sys.exit("error: no ado_base_url (set in profile or pass --org-base-url)")
    return base.rstrip("/")


def resolve_pat(profile, env_override=None):
    """Resolve the PAT with this precedence:

      1. --pat-env override (env var) — CLI beats everything.
      2. profile 'pat_file'          — an explicit path in the profile wins
                                        over ambient env so nightly runs stay
                                        pinned to a known secret file.
      3. profile 'pat_env' env var   — named env var if pat_file isn't set.
      4. default AZDO_PAT env var    — last-ditch fallback.
    """
    if env_override:
        pat = os.environ.get(env_override)
        if pat:
            return pat.strip()
        sys.exit(f"error: --pat-env {env_override!r} but that env var is empty")

    pat_file = profile.get("pat_file")
    if pat_file:
        path = os.path.expanduser(os.path.expandvars(pat_file))
        try:
            with open(path, "r", encoding="utf-8") as fh:
                # First non-blank, non-comment line is the active PAT.
                # Lines starting with '#' are ignored so you can keep
                # rotated PATs commented in the same file.
                for raw in fh:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    return line
        except OSError as e:
            sys.exit(f"error: cannot read pat_file {path!r}: {e}")
        sys.exit(f"error: pat_file {path!r} has no active (uncommented) PAT")

    env_name = profile.get("pat_env") or "AZDO_PAT"
    pat = os.environ.get(env_name)
    if pat:
        return pat.strip()

    sys.exit(f"error: PAT not found — set profile 'pat_file', "
             f"env var {env_name!r}, or pass --pat-env")


def strip_html(s):
    if not s:
        return ""
    s = TAG_RE.sub(" ", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


class Client:
    def __init__(self, base, pat, api_version=API_VERSION):
        self.base = base
        self.api_version = api_version
        token = base64.b64encode(f":{pat}".encode("utf-8")).decode("ascii")
        self.auth = f"Basic {token}"

    def _request(self, method, path, params=None, body=None, accept="application/json",
                 content_type=None):
        params = dict(params or {})
        params.setdefault("api-version", self.api_version)
        url = f"{self.base}{path}?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}"
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, method=method, data=data)
        req.add_header("Authorization", self.auth)
        req.add_header("Accept", accept)
        if content_type:
            req.add_header("Content-Type", content_type)
        elif data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            payload = e.read().decode("utf-8", "ignore")[:1000]
            raise AdoError(f"HTTP {e.code} on {method} {path}: {payload}") from e
        except urllib.error.URLError as e:
            raise AdoError(f"cannot reach {self.base} ({e.reason})") from e

    def get_json(self, path, params=None):
        raw = self._request("GET", path, params=params)
        return json.loads(raw.decode("utf-8", "ignore"))

    def patch_json(self, path, body, params=None, content_type="application/json-patch+json"):
        raw = self._request("PATCH", path, params=params, body=body, content_type=content_type)
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8", "ignore"))
        except json.JSONDecodeError:
            return {}


class AdoError(Exception):
    pass


# --------------------------------------------------------------------------- #
# Changesets / work items
# --------------------------------------------------------------------------- #
def get_changeset(client, cs_id):
    """Return one TFVC changeset (id, author, createdDate, comment)."""
    return client.get_json(f"/_apis/tfvc/changesets/{cs_id}",
                           {"includeDetails": "true"})


def get_changeset_workitems(client, cs_id):
    """Return list of work-item dicts associated with a TFVC changeset."""
    data = client.get_json(f"/_apis/tfvc/changesets/{cs_id}/workItems")
    return data.get("value", []) if isinstance(data, dict) else []


def get_workitem(client, wi_id):
    data = client.get_json(f"/_apis/wit/workitems/{wi_id}", {"$expand": "relations"})
    f = data.get("fields", {})
    return {
        "id": int(wi_id),
        "type": f.get("System.WorkItemType", ""),
        "title": f.get("System.Title", ""),
        "state": f.get("System.State", ""),
        "url": data.get("_links", {}).get("html", {}).get("href", ""),
        "raw": data,
    }


def link_workitem_to_changeset(client, wi_id, changeset_id, project_uri=None,
                               comment="Integrated by tfvc-merge"):
    """Add a 'Fixed in Changeset' artifact link from a work item to a TFVC changeset.

    The link uses vstfs:///VersionControl/Changeset/<id> URI. If project_uri is
    given it's prefixed; ADO accepts the bare form for org-scoped TFVC.
    """
    artifact_url = f"vstfs:///VersionControl/Changeset/{changeset_id}"
    if project_uri:
        # Some on-prem servers want the project's collection in the URI.
        artifact_url = f"vstfs:///VersionControl/Changeset/{changeset_id}"
    patch = [{
        "op": "add",
        "path": "/relations/-",
        "value": {
            "rel": "ArtifactLink",
            "url": artifact_url,
            "attributes": {
                "name": "Fixed in Changeset",
                "comment": comment,
            },
        },
    }]
    return client.patch_json(f"/_apis/wit/workitems/{wi_id}", patch)
