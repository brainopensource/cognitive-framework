#!/usr/bin/env python3
"""Keep living documentation small enough for progressive, task-scoped reading.

The two preserved compound law bodies are deliberately exempt: ADR-0087 records that they are
verbatim anchors retained for provenance until a later section extraction. ADRs and frozen archives
are never measured as context documents.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIMITS = {
    "docs/execution": 200,
    "docs/architecture": 200,
    "docs/backend": 200,
    "docs/frontend": 200,
    "docs/product": 200,
    "docs/theory": 200,
}
EXEMPT = {
    Path("docs/01_law/RUNTIME.md"),
    Path("docs/01_law/DISPATCH.md"),
}


def limit_for(relative: Path) -> int | None:
    key = str(relative)
    if key in LIMITS:
        return LIMITS[key]
    for directory, limit in LIMITS.items():
        if relative.is_relative_to(Path(directory)):
            return limit
    return None


def check() -> list[str]:
    errors: list[str] = []
    for path in sorted((ROOT / "docs").rglob("*.md")):
        relative = path.relative_to(ROOT)
        if "_archive" in relative.parts or "05_adr" in relative.parts or "02_decisions" in relative.parts:
            continue
        if relative in EXEMPT:
            continue
        limit = limit_for(relative)
        if limit is None:
            continue
        lines = len(path.read_text(encoding="utf-8").splitlines())
        if lines > limit:
            errors.append(f"{relative}: {lines} lines exceeds budget {limit}")
    return errors


def main() -> int:
    errors = check()
    if errors:
        for error in errors:
            print(f"DOC BUDGET FAIL: {error}")
        return 1
    print("DOC BUDGET PASS: living context documents respect their class budgets; compound law anchors are explicitly exempt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
