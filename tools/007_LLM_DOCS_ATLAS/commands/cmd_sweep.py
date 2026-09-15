"""Implementation of `lda sweep`."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..core.orchestrator import RepositoryOrchestrator


def handle_sweep(repo_root: Path, budget: int = 4000) -> Dict[str, Any]:
    orch = RepositoryOrchestrator(repo_root)
    return orch.sweep(budget=budget)
