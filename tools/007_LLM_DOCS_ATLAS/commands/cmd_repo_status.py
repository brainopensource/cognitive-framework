"""Implementation of `lda repo-status`."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..core.orchestrator import RepositoryOrchestrator


def handle_repo_status(repo_root: Path) -> Dict[str, Any]:
    orch = RepositoryOrchestrator(repo_root)
    return orch.repo_status()
