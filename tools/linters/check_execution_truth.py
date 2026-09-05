#!/usr/bin/env python3
"""Validate the five-file canonical execution runway.

The former ``active.md`` board was retired when execution state moved to the
flat task runway. Keeping a hard read of that deleted compatibility file made
the verification gate fail before it could inspect the current documents.

The old validator read every **BOLD** token in the file as a board state.
That held for the two-lane board, where bold meant status and nothing else.
On the five-file runway bold also carries milestone names (MS-**TRUTH**),
evidence grades (**MECHANISM**), context layers (**L3**) and table markers,
so a blanket read reports scores of false positives.

The answer is to narrow the check, not to delete it: milestone status is a
closed vocabulary and is still validated in the one column that holds it.
A gate that passes because it stopped looking is worse than no gate.
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
#: The milestone board's closed status vocabulary. `MECHANISM` asserts the
#: mechanism is wired and falsified; `CLOSED` additionally asserts empirical
#: evidence. Anything outside this set is an unreviewed status.
ALLOWED = {
    "OPEN",
    "BLOCKED",
    "MECHANISM",
    "CLOSED",
    "ACCEPTED",
}
#: `| **MS-NAME** | target | acceptance | STATUS | evidence |`
MILESTONE_ROW = re.compile(
    r"^\| \*\*(MS-[A-Z0-9-]+)\*\* \|[^|]*\|[^|]*\|([^|]*)\|",
    re.MULTILINE,
)
#: The leading token of that column, ignoring trailing qualifiers such as
#: ``(gated on ...)`` or a ``[PROPOSAL]`` marker.
STATUS_TOKEN = re.compile(r"`([A-Z_]+)`")
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

    milestones = (EXECUTION / "milestones.md").read_text(encoding="utf-8")
    for name, column in MILESTONE_ROW.findall(milestones):
        token = STATUS_TOKEN.search(column)
        if token is None:
            errors.append(f"milestones.md {name} has no status token in its Status column")
        elif token.group(1) not in ALLOWED:
            errors.append(f"milestones.md {name} uses unsupported status {token.group(1)}")

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
