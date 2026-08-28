#!/usr/bin/env python3
"""Validate the two-lane canonical execution boards."""

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

    active = (EXECUTION / "sprint_active.md").read_text(encoding="utf-8")
    current_rows = CURRENT_ROW.findall(active)
    if len(current_rows) != 2 or {lane for lane, _, _ in current_rows} != {"Lane A", "Lane B"}:
        errors.append("sprint_active.md must contain exactly one current package per lane")
    current_ids = [package for _, package, _ in current_rows]
    if len(current_ids) != len(set(current_ids)):
        errors.append("sprint_active.md contains duplicate current package IDs")
    if any(state in {"NOT_STARTED", "BLOCKED"} for _, _, state in current_rows):
        errors.append("sprint_active.md current package cannot be NOT_STARTED or BLOCKED")

    for milestone in ("M-4", "M-5a", "M-5b", "M-6", "M-6.5", "M-7", "M-8"):
        if not re.search(rf"^\| {re.escape(milestone)} \|", active, re.MULTILINE):
            errors.append(f"sprint_active.md lacks canonical milestone row {milestone}")
    milestone_predicates = dict(MILESTONE_ROW.findall(active))
    for milestone in ("M-4", "M-5a", "M-5b", "M-6", "M-6.5", "M-7", "M-8"):
        if not milestone_predicates.get(milestone):
            errors.append(f"sprint_active.md lacks a machine predicate for {milestone}")

    ledger_start = active.find("## Package state ledger")
    ledger_end = active.find("\n## ", ledger_start + 1)
    ledger_text = active[ledger_start:] if ledger_end == -1 else active[ledger_start:ledger_end]
    for retired in ("C1-GATE", "Leadership", "Dev C", "Director", "human review"):
        if retired in ledger_text:
            errors.append(f"sprint_active.md package ledger contains retired process term {retired!r}")

    milestones = (EXECUTION / "milestones.md").read_text(encoding="utf-8")
    if STATE.search(milestones):
        errors.append("milestones.md duplicates volatile bold state; state belongs in sprint_active.md")

    upcoming = (EXECUTION / "sprint_upcoming.md").read_text(encoding="utf-8")
    if "**IN_PROGRESS**" in upcoming or "**ACCEPTED**" in upcoming:
        errors.append("sprint_upcoming.md may not claim active or accepted work")

    backlog = (EXECUTION / "backlog.md").read_text(encoding="utf-8")
    backlog_states = dict(PACKAGE_ROW.findall(backlog))
    board_states = dict(PACKAGE_ROW.findall(active))
    if set(board_states) != set(backlog_states):
        errors.append("sprint_active.md package ledger must contain exactly the backlog package IDs")
    board_states.update(UPCOMING_ROW.findall(upcoming))
    for package, expected in sorted(backlog_states.items()):
        actual = board_states.get(package)
        if actual != expected:
            errors.append(
                f"package state drift for {package}: backlog={expected}, board={actual or 'MISSING'}"
            )
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
