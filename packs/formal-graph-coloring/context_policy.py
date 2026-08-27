"""Pack-owned context projection for bounded graph coloring tasks."""

from __future__ import annotations

from pathlib import Path


class FormalGraphColoringContextPolicy:
    """Admit only the task graph and bounded witness instructions."""

    def select(self, workspace: Path | str, graph: str = "problem.graph.json") -> tuple[str, ...]:
        root = Path(workspace).resolve()
        target = (root / graph).resolve()
        target.relative_to(root)
        return (target.read_text(encoding="utf-8"),)
