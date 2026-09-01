"""Pack-owned context projection for bounded DIMACS tasks."""

from __future__ import annotations

from pathlib import Path


class FormalSatContextPolicy:
    """Admit only the task formula and bounded witness instructions."""

    def select(self, workspace: Path | str, formula: str = "problem.cnf") -> tuple[str, ...]:
        root = Path(workspace).resolve()
        target = (root / formula).resolve()
        target.relative_to(root)
        return (target.read_text(encoding="utf-8"),)
