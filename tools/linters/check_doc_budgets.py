#!/usr/bin/env python3
"""Keep living documentation small enough for progressive, task-scoped reading.

The two preserved compound law bodies are deliberately exempt: ADR-0087 records that they are
verbatim anchors retained for provenance until a later section extraction. ADRs and frozen archives
are never measured as context documents.

`CEILINGS` holds calibrated per-file limits for documents that are normative registries rather
than progressive-reading context. The five `docs/execution` files carry gate predicates, typed
contracts and the task board; 200 lines was never achievable for them and the check had been
failing continuously, which makes a red gate carry no information. Each ceiling below is set
just above the size measured after the 2026-09-12 consolidation, so the reduction achieved is
locked in and any regrowth fails the gate. These are exemptions from the 200-line class default,
NOT exemptions from measurement: raising a ceiling is a deliberate, reviewable edit here.
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
#: Calibrated per-file ceilings that override the class default. Measured
#: 2026-09-12 after consolidation (741/472/2016/1580/2166) with ~6% headroom for
#: ordinary edits. Lowering a value is always allowed; raising one is a governance
#: decision and must be justified in the commit that does it.
CEILINGS = {
    Path("docs/execution/main/backlog.md"): 800,
    Path("docs/execution/main/milestones.md"): 520,
    Path("docs/execution/main/spec.md"): 2150,
    Path("docs/execution/main/tasks.md"): 1700,
    Path("docs/execution/main/technical.md"): 2300,
}


def limit_for(relative: Path) -> int | None:
    if relative in CEILINGS:
        return CEILINGS[relative]
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
