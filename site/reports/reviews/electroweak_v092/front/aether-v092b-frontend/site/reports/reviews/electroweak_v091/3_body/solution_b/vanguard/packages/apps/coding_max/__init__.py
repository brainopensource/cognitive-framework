"""AETHER Coding Max harness — an outer-layer composition over the Vanguard substrate.

Nothing in this package holds authority. Effects are proposed and dispatched
through `Kernel.dispatch` exactly as any other agent's are (`spec §40`); this
package supplies classification, retrieval, planning, verification, and
recovery *policy* around that unchanged path.
"""

from __future__ import annotations

from .errors import CodingMaxError
from .profile import RepoSignals, TaskClassifier, TaskProfile, TaskType, WorkflowKind
from .repo_map import RepositoryMap, build_repository_map

__all__ = [
    "CodingMaxError", "RepoSignals", "RepositoryMap", "TaskClassifier",
    "TaskProfile", "TaskType", "WorkflowKind", "build_repository_map",
]
