"""
_tf.py — thin wrapper around tf.exe (Visual Studio Team Explorer command line).

Returns structured TfResult objects rather than raw stdout strings. Designed to
be called from the orchestrator; failures raise TfError so callers can decide
whether to skip the changeset, abort the run, or report.

Discovery commands are read-only. Write commands (merge, resolve, checkin, undo)
mutate the local workspace and TFVC server respectively. Caller is responsible
for sequencing.
"""

import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional


DEFAULT_TIMEOUT = 600  # 10 min per tf call; long checkins on big merges need room


@dataclass
class TfResult:
    cmd: List[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class TfError(Exception):
    def __init__(self, result: TfResult, message: str = ""):
        self.result = result
        super().__init__(message or f"tf {' '.join(result.cmd[1:])} failed (rc={result.returncode}): {result.stderr.strip() or result.stdout.strip()}")


def find_tf_exe(override: Optional[str] = None) -> str:
    """Locate tf.exe. Honors override, $TF_EXE, then PATH, then standard VS install paths."""
    if override:
        if os.path.isfile(override):
            return override
        raise TfError(TfResult(cmd=[override], returncode=-1, stdout="", stderr=""),
                      f"tf_exe override {override!r} not found")
    env = os.environ.get("TF_EXE")
    if env and os.path.isfile(env):
        return env
    on_path = shutil.which("tf") or shutil.which("tf.exe")
    if on_path:
        return on_path
    # Common VS 2019 / 2022 install locations.
    candidates = [
        r"C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\tf.exe",
        r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\tf.exe",
        r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\tf.exe",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\tf.exe",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\tf.exe",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    raise TfError(TfResult(cmd=["tf.exe"], returncode=-1, stdout="", stderr=""),
                  "tf.exe not found — install Visual Studio with Team Explorer, set $TF_EXE, or pass tf_exe in the profile")


class Tf:
    """Wraps either Visual Studio's ``tf.exe`` or Team Explorer Everywhere's
    ``tf.cmd`` (TEE-CLC). Selects the right command dialect automatically:

      * **VS dialect** — ``tf vc <cmd> /flag:value`` (subcommand prefix ``vc``,
        Windows-style slash switches).
      * **TEE dialect** — ``tf <cmd> -flag:value`` (no ``vc`` prefix,
        Unix-style dash switches).

    Detection is by executable filename (``tf.cmd`` / ``tf.bat`` → TEE, else
    VS) or an explicit ``dialect='tee'`` / ``'vs'`` override from the profile.

    When ``pat`` is provided and ``use_pat_login`` is True, every command is
    decorated with ``/login:.,<PAT>`` (or ``-login:.,<PAT>`` in TEE dialect).
    VS Team Explorer's ``tf.exe`` often rejects PAT ``/login`` against ADO
    Services and expects VS-cached OAuth; TEE-CLC accepts the PAT reliably
    and is the recommended path for unattended automation.
    """

    _DIALECTS = ("vs", "tee")

    def __init__(self, tf_exe: str, cwd: Optional[str] = None,
                 collection_url: Optional[str] = None,
                 pat: Optional[str] = None,
                 use_pat_login: bool = False,
                 dialect: Optional[str] = None,
                 pat_username: Optional[str] = None,
                 env: Optional[dict] = None):
        self.tf_exe = tf_exe
        self.cwd = cwd
        self.collection_url = collection_url
        self.pat = pat
        self.use_pat_login = use_pat_login
        # Username used with /login:<user>,<PAT>. TEE-CLC rejects "." as a
        # placeholder username with "argument error"; a real UPN or the
        # conventional "PersonalAccessToken" string is required.
        self.pat_username = pat_username or "PersonalAccessToken"
        # Extra env for the subprocess (e.g. JAVA_HOME for TEE-CLC on Windows).
        self.env = env
        if dialect and dialect not in self._DIALECTS:
            raise ValueError(f"unknown tf dialect {dialect!r}; expected one of {self._DIALECTS}")
        self.dialect = dialect or self._auto_detect_dialect(tf_exe)

    @staticmethod
    def _auto_detect_dialect(tf_exe: str) -> str:
        name = os.path.basename(tf_exe).lower()
        if name in ("tf.cmd", "tf.bat") or "tee" in tf_exe.lower():
            return "tee"
        return "vs"

    def _translate(self, args) -> list:
        """Translate a VS-style args list to the active dialect.

        VS dialect: pass through unchanged.
        TEE dialect on Windows: drop the leading ``vc`` subcommand prefix;
        keep ``/flag`` slash switches (TEE-CLC's Windows launcher uses
        the same slash syntax as VS tf.exe).
        """
        if self.dialect == "vs":
            return list(args)
        out = []
        for i, a in enumerate(args):
            if i == 0 and a == "vc":
                continue
            out.append(a)
        return out

    def run(self, *args: str, cwd: Optional[str] = None,
            check: bool = True, timeout: int = DEFAULT_TIMEOUT) -> TfResult:
        args = self._translate(args)
        cmd = [self.tf_exe, *args]
        if (self.use_pat_login and self.pat
                and not any(a.startswith(("/login", "-login")) for a in args)):
            cmd.append(f"/login:{self.pat_username},{self.pat}")
        if (self.collection_url
                and not any(a.startswith(("/collection", "-collection")) for a in args)):
            cmd.append(f"/collection:{self.collection_url}")
        run_env = None
        if self.env:
            run_env = os.environ.copy()
            run_env.update(self.env)
        try:
            proc = subprocess.run(
                cmd,
                cwd=cwd or self.cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                env=run_env,
            )
        except subprocess.TimeoutExpired as e:
            result = TfResult(cmd=cmd, returncode=-1,
                              stdout=e.stdout or "", stderr=e.stderr or f"timeout after {timeout}s")
            raise TfError(result, f"tf timed out after {timeout}s: {' '.join(cmd[1:])}")
        result = TfResult(cmd=cmd, returncode=proc.returncode,
                          stdout=proc.stdout or "", stderr=proc.stderr or "")
        if check and not result.ok:
            raise TfError(result)
        return result

    # ----- read-only ----- #
    def workspaces(self) -> TfResult:
        return self.run("vc", "workspaces", "/format:detailed", check=False)

    def status(self, scope: str = ".", recursive: bool = True) -> TfResult:
        args = ["vc", "status", scope, "/format:detailed"]
        if recursive:
            args.append("/recursive")
        return self.run(*args, check=False)

    def merge_candidates(self, source_branch: str, target_branch: str) -> TfResult:
        return self.run("vc", "merge", "/candidate", "/recursive",
                        "/format:detailed", source_branch, target_branch, check=False)

    # ----- write ----- #
    def get_latest(self, local_path: str) -> TfResult:
        return self.run("vc", "get", local_path, "/recursive", "/noprompt", "/overwrite")

    def merge_changeset(self, source_branch: str, target_branch: str,
                        changeset_id: int) -> TfResult:
        return self.run(
            "vc", "merge",
            f"/version:C{changeset_id}~C{changeset_id}",
            "/recursive", "/noprompt",
            source_branch, target_branch,
            check=False,
        )

    def auto_resolve(self, scope: str = ".") -> TfResult:
        return self.run("vc", "resolve", scope, "/auto:AutoMerge", "/recursive",
                        "/noprompt", check=False)

    def list_conflicts(self, scope: str = ".") -> TfResult:
        return self.run("vc", "resolve", scope, "/preview", "/recursive", check=False)

    def undo(self, scope) -> TfResult:
        """scope can be a single path or a list of paths."""
        if isinstance(scope, str):
            scopes = [scope]
        else:
            scopes = list(scope)
        return self.run("vc", "undo", *scopes, "/recursive", "/noprompt", check=False)

    def checkin(self, local_path: str, comment: str) -> TfResult:
        return self.run("vc", "checkin", local_path,
                        f"/comment:{comment}",
                        "/recursive", "/noprompt", check=False)


# --------------------------------------------------------------------------- #
# Parsers — tf.exe text output → structured data
# --------------------------------------------------------------------------- #
_CANDIDATE_LINE = re.compile(
    r"^\s*(?P<id>\d+)\s+(?P<user>\S+)\s+(?P<date>\d{1,2}/\d{1,2}/\d{4})",
)


def parse_candidates(stdout: str) -> List[dict]:
    """Parse `tf vc merge /candidate /format:detailed` output.

    Detailed format produces blocks like:

        Changeset: 12345
        User:      DOMAIN\\user
        Date:      6/16/2026 4:32:11 PM

        Comment:
          The check-in comment, possibly multiline.

        Items:
          merge, edit $/Project/Dev/path/File.xml

    We extract id, user, date, comment. (Date kept as raw string — orchestrator
    cross-references ADO REST for the authoritative timestamp.)
    """
    blocks = re.split(r"\n(?=Changeset:\s*\d+)", stdout)
    out = []
    for block in blocks:
        m = re.search(r"^Changeset:\s*(\d+)", block, re.MULTILINE)
        if not m:
            continue
        cs_id = int(m.group(1))
        user = _field(block, "User")
        date = _field(block, "Date")
        comment = _multiline_field(block, "Comment")
        out.append({
            "id": cs_id,
            "user": user,
            "date_raw": date,
            "comment": comment,
        })
    out.sort(key=lambda r: r["id"])
    return out


def _field(block: str, label: str) -> str:
    m = re.search(rf"^{re.escape(label)}:\s*(.+)$", block, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _multiline_field(block: str, label: str) -> str:
    """Capture an indented multi-line block, e.g.:

        Comment:
          line one
          line two
        NextField:
    """
    m = re.search(rf"^{re.escape(label)}:\s*\n((?:[ \t]+.+\n?)+)",
                  block, re.MULTILINE)
    if not m:
        # Single-line variant: "Comment: foo"
        single = re.search(rf"^{re.escape(label)}:\s*(.+)$", block, re.MULTILINE)
        return single.group(1).strip() if single else ""
    lines = [ln.strip() for ln in m.group(1).splitlines() if ln.strip()]
    return "\n".join(lines)


# Conflict preview output is short; one path per line under a header.
def parse_conflicts(stdout: str) -> List[str]:
    """Parse `tf vc resolve /preview` output → list of conflicted local paths."""
    out = []
    for line in stdout.splitlines():
        line = line.rstrip()
        if not line:
            continue
        # Lines that look like absolute Windows paths or $/server paths.
        if re.match(r"^[A-Za-z]:[\\/]", line) or line.startswith("$/"):
            out.append(line.strip())
            continue
        # "version: C123  source: ..."-style trailing detail lines — ignore.
    return out


def changeset_id_from_checkin(stdout: str) -> Optional[int]:
    """Find 'Changeset #NNN checked in.' in tf checkin output."""
    m = re.search(r"Changeset\s*#?(\d+)\s+checked in", stdout, re.IGNORECASE)
    return int(m.group(1)) if m else None
