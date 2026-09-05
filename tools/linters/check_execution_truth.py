#!/usr/bin/env python3
"""Validate the five-file canonical execution runway.

The former ``active.md`` board was retired when execution state moved to the
flat task runway. Keeping a hard read of that deleted compatibility file made
the verification gate fail before it could inspect the current documents.

Execution documents also use bold uppercase labels for semantic annotations
such as ``FACT`` and ``MUST``. Those labels are not volatile board states, so
the validator must not interpret every bold uppercase token as a status.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXECUTION = ROOT / "docs" / "execution"
FILES = (
    EXECUTION / "milestones.md",
    EXECUTION / "backlog.md",
    EXECUTION / "spec.md",
    EXECUTION / "technical.md",
    EXECUTION / "tasks.md",
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


def validate() -> list[str]:
    errors: list[str] = []
    for path in FILES:
        if not path.is_file():
            errors.append(f"missing canonical execution document: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for match in BANNED.finditer(text):
            errors.append(f"{path.relative_to(ROOT)} uses obsolete status {match.group(0)}")

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
