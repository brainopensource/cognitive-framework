"""Implementation of `lda tasks`."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.orchestrator import RepositoryOrchestrator


def handle_tasks(
    repo_root: Path,
    task_id: Optional[str] = None,
    owner: Optional[str] = None,
    ready_only: bool = False,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    orch = RepositoryOrchestrator(repo_root)
    return orch.tasks(task_id=task_id, owner=owner, ready_only=ready_only, limit=limit)
