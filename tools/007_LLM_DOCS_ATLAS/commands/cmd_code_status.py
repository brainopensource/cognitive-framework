"""Implementation of `lda code-status`."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from ..core.orchestrator import RepositoryOrchestrator


def handle_code_status(
    repo_root: Path,
    task_id: Optional[str] = None,
    target_files: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    orch = RepositoryOrchestrator(repo_root)
    return orch.code_status(task_id=task_id, target_files=target_files)
