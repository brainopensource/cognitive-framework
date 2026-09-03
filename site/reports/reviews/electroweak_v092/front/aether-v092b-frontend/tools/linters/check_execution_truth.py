#!/usr/bin/env python3
"""Validate the two-lane canonical execution boards."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXECUTION = ROOT / "docs" / "execution"
FILES = (
    EXECUTION / "milestones.md",
    EXECUTION / "active.md",
)
ALLOWED = {
    "NOT_STARTED",
    "IN_PROGRESS",
    "BLOCKED",
    "PACKAGE_READY",
    "EVIDENCE_READY",
    "ACCEPTED",
}
BANNED = re.compile(r"\*\*(?:DONE|CLOSED|COMPLETE|WAIVED)(?:[^*]*)\*\*")
STATE = re.compile(r"\*\*([A-Z][A-Z0-9_]*)\*\*")
CURRENT_ROW = re.compile(
    r"^\| (Lane A|Lane B) \| (WP-[ABC][0-9]) \|.*?\*\*([A-Z][A-Z0-9_]*)\*\*",
    re.MULTILINE,
)
PACKAGE_ROW = re.compile(
    r"^\| (WP-[ABC][0-9]) \|.*?\*\*([A-Z][A-Z0-9_]*)\*\*",
    re.MULTILINE,
)
MILESTONE_ROW = re.compile(
    r"^\| (M-[0-9]+(?:\.[0-9]+)?[a-z]?) \| `([^`]+)` \|",
    re.MULTILINE,
)
UPCOMING_ROW = re.compile(
    r"^\| C[0-9]+ \| [0-9]+ \| (WP-[AB][0-9])\b.*?\*\*([A-Z][A-Z0-9_]*)\*\*",
    re.MULTILINE,
)


def validate() -> list[str]:
    errors: list[str] = []
    for path in FILES:
        if not path.is_file():
            errors.append(f"missing canonical execution document: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for match in BANNED.finditer(text):
            errors.append(f"{path.relative_to(ROOT)} uses obsolete status {match.group(0)}")
        for value in STATE.findall(text):
            if value not in ALLOWED:
                errors.append(f"{path.relative_to(ROOT)} uses unsupported bold state {value}")

    active = (EXECUTION / "active.md").read_text(encoding="utf-8")
    milestones = (EXECUTION / "milestones.md").read_text(encoding="utf-8")
    if STATE.search(milestones):
        errors.append("milestones.md duplicates volatile bold state; state belongs in active.md")

    return errors


def main() -> int:
    errors = validate()
    for error in errors:
        print(f"EXECUTION TRUTH FAIL: {error}")
    if errors:
        return 1
    print("EXECUTION TRUTH PASS: canonical boards use one supported state model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
