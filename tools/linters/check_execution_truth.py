#!/usr/bin/env python3
"""Validate the canonical execution boards' status vocabulary and ownership."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXECUTION = ROOT / "docs" / "03_execution"
FILES = (
    EXECUTION / "milestones.md",
    EXECUTION / "backlog.md",
    EXECUTION / "sprint_active.md",
    EXECUTION / "sprint_upcoming.md",
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
ACTIVE_ROW = re.compile(r"^\| (WP-[AB][0-9]|C1-GATE) \|", re.MULTILINE)


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

    active = (EXECUTION / "sprint_active.md").read_text(encoding="utf-8")
    ids = ACTIVE_ROW.findall(active)
    if len(ids) != len(set(ids)):
        errors.append("sprint_active.md contains duplicate active package IDs")
    if set(ids) != {"WP-A1", "WP-B1", "C1-GATE"}:
        errors.append(f"sprint_active.md active IDs drifted: {sorted(ids)}")
    if "**NOT_STARTED**" in active:
        errors.append("sprint_active.md contains non-started work; move it to sprint_upcoming.md")

    upcoming = (EXECUTION / "sprint_upcoming.md").read_text(encoding="utf-8")
    if "**IN_PROGRESS**" in upcoming or "**ACCEPTED**" in upcoming:
        errors.append("sprint_upcoming.md may not claim active or accepted work")
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
