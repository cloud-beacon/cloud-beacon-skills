"""
_xpp_xml.py — helpers for D365 F&O metadata XML files.

Two jobs:
  1. extract_xpp(xml_text) — concatenate the X++ source from all <![CDATA[…]]>
     blocks so a diff reads as code instead of XML scaffolding (reused from
     tfvc-fetch).
  2. is_metadata_xml(path) — quick filename test.

Conflict resolution itself stays in the orchestrator; this module just gives
the building blocks for surfacing X++-level diffs to the human (or to Claude
when running interactively).
"""

import re

CDATA_RE = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.DOTALL)

# D365 metadata extensions we care about for X++/metadata conflict reporting.
_METADATA_SUFFIXES = (
    ".xml",
    ".axclass",
    ".axtable",
    ".axform",
    ".axenum",
    ".axquery",
    ".axview",
    ".axmenu",
    ".axmenuitem",
    ".axsecurityrole",
    ".axsecurityduty",
    ".axsecurityprivilege",
)


def is_metadata_xml(path: str) -> bool:
    p = path.lower()
    return p.endswith(_METADATA_SUFFIXES)


def extract_xpp(xml_text: str) -> str:
    """Concatenate all CDATA blocks. Returns '' if no CDATA in the file."""
    blocks = CDATA_RE.findall(xml_text or "")
    if not blocks:
        return ""
    return "\n".join(b.strip("\n") for b in blocks).strip("\n")


def read_xml(path: str) -> str:
    """Read a metadata file as text, tolerant of UTF-8 BOM and encoding errors."""
    with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
        return fh.read()
