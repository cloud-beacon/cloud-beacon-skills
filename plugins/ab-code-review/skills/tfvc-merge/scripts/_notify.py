"""
_notify.py — send the completion email.

Two send paths:

1. **M365 MCP (preferred)** — when the orchestrator is invoked from a Claude
   Code session (interactive or headless via Claude Code Remote), the actual
   send is performed by Claude calling the `mcp__ms365__send-mail` tool with
   the payload this module emits to a JSON sidecar file. This module writes
   the payload + recipient list and prints the path; the Claude session reads
   the file and issues the MCP call.

2. **SMTP fallback** — pure-stdlib `smtplib`, configured via env vars. Used by
   plain Task Scheduler entries where there's no Claude in the loop.

Choosing between them is the caller's responsibility (orchestrator decides
based on the `notify_via` profile key or `--notify-via` flag).
"""

import json
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from typing import List, Optional


def write_mcp_payload(payload_path: str, *, to: List[str], subject: str,
                      html_body: str, text_body: str,
                      cc: Optional[List[str]] = None) -> str:
    """Write the JSON sidecar for the M365 MCP sender to pick up.

    Schema (read by the orchestrator's calling Claude session):
      {
        "to":      ["user@example.com", ...],
        "cc":      [...],            (optional)
        "subject": "...",
        "html":    "<!doctype html>...",
        "text":    "...plain text fallback..."
      }
    """
    obj = {"to": to, "subject": subject, "html": html_body, "text": text_body}
    if cc:
        obj["cc"] = cc
    os.makedirs(os.path.dirname(os.path.abspath(payload_path)), exist_ok=True)
    with open(payload_path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2)
    return payload_path


def send_smtp(*, to: List[str], subject: str, html_body: str, text_body: str,
              host: Optional[str] = None, port: Optional[int] = None,
              user_env: str = "SMTP_USER", pass_env: str = "SMTP_PASS",
              from_addr_env: str = "SMTP_FROM",
              starttls: bool = True) -> None:
    """Send via SMTP. Env vars carry credentials; never accept them on the CLI.

    Defaults work for Microsoft 365 SMTP submission:
      host = smtp.office365.com, port = 587, STARTTLS, AUTH LOGIN.
    """
    host = host or os.environ.get("SMTP_HOST", "smtp.office365.com")
    port = port or int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get(user_env)
    pw = os.environ.get(pass_env)
    sender = os.environ.get(from_addr_env, user)
    if not (user and pw and sender):
        sys.exit(f"error: SMTP fallback needs env vars {user_env}, {pass_env}, "
                 f"and {from_addr_env}")

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = ", ".join(to)
    msg["Subject"] = subject
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    ctx = ssl.create_default_context()
    with smtplib.SMTP(host, port, timeout=60) as srv:
        srv.ehlo()
        if starttls:
            srv.starttls(context=ctx)
            srv.ehlo()
        srv.login(user, pw)
        srv.send_message(msg)
