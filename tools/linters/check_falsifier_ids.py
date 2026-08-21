#!/usr/bin/env python3
"""Enforce the ratified RF-* allocation registry (ADR-0082 / RF-72)."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable

_ROOT = Path(__file__).resolve().parents[2]
_REGISTER = _ROOT / "docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md"
_CITATION_FILES = (
    _ROOT / "docs/SPEC.md",
    _ROOT / "docs/03_sprints/sprint_active.md",
    *sorted((_ROOT / "docs/05_adr").glob("[0-9][0-9][0-9][0-9]-*.md")),
)
_TOKEN = re.compile(r"RF-(\d+)(?:\s*[–-]\s*(?:RF-)?(\d+))?")
_ROW = re.compile(r"^\|\s*`([^`]*RF-[^`]*)`\s*\|\s*([^|]+)\|\s*([^|]+)\|", re.MULTILINE)


def expand_ids(text: str) -> tuple[int, ...]:
    """Expand RF-23 and inclusive RF-28–RF-33 spellings."""
    expanded: list[int] = []
    for match in _TOKEN.finditer(text):
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if end < start:
            raise ValueError(f"descending RF range: {match.group(0)}")
        expanded.extend(range(start, end + 1))
    return tuple(expanded)


def allocations(register_text: str) -> tuple[dict[int, tuple[str, str]], list[str]]:
    """Return canonical allocations and conflicting-row errors."""
    found: dict[int, tuple[str, str]] = {}
    errors: list[str] = []
    for match in _ROW.finditer(register_text):
        label, owner, subject = (part.strip() for part in match.groups())
        identity = (owner, subject)
        for number in expand_ids(label):
            prior = found.get(number)
            if prior is not None and prior != identity:
                errors.append(
                    f"RF-{number} is allocated twice: {prior!r} and {identity!r}"
                )
            found[number] = identity
    return found, errors


def cited_ids(paths: Iterable[Path]) -> dict[int, set[str]]:
    cited: dict[int, set[str]] = {}
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for number in expand_ids(text):
            cited.setdefault(number, set()).add(str(path.relative_to(_ROOT)))
    return cited


def check() -> list[str]:
    register_text = _REGISTER.read_text(encoding="utf-8")
    allocated, errors = allocations(register_text)
    if not allocated:
        errors.append("the canonical register contains no RF-* allocation rows")
        return errors
    for number, paths in sorted(cited_ids(_CITATION_FILES).items()):
        if number not in allocated:
            errors.append(
                f"RF-{number} is cited but unallocated: {', '.join(sorted(paths))}"
            )
    if "| `F-12` | `RF-23` |" not in register_text:
        errors.append("the sole historical lineage F-12 -> RF-23 is missing")
    return errors


def main() -> int:
    errors = check()
    if errors:
        for error in errors:
            print(f"RF ID FAIL: {error}")
        return 1
    print("RF ID PASS: allocations are unique and all canonical citations are allocated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
