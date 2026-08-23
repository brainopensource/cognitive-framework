"""M-6 delegation reservation.

This module deliberately contains no child creation path.  It makes the
future contract executable as a fail-closed seam while M-3/M-4/M-5 remain the
governance gate for activating ``agent.spawn``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

M6_SPAWN_ACTIVE = False


class SpawnPreparationError(PermissionError):
    pass


@dataclass(frozen=True, slots=True)
class SpawnRequest:
    target_harness_digest: str
    selector: Mapping[str, Any]
    turns: int
    depth: int
    budget: Mapping[str, int]


def prepare_spawn(request: SpawnRequest, *, grant: Mapping[str, Any] | None,
                  parent_ceiling: Mapping[str, Any] | None) -> None:
    """Refuse every spawn until M-6 opens; no subprocess or ledger side effect."""
    if not M6_SPAWN_ACTIVE:
        raise SpawnPreparationError("agent.spawn not implemented before M-6")
    if grant is None or parent_ceiling is None:
        raise SpawnPreparationError("agent.spawn requires an explicit grant and parent ceiling")
    raise SpawnPreparationError("agent.spawn activation is governed and unavailable")


__all__ = ["M6_SPAWN_ACTIVE", "SpawnPreparationError", "SpawnRequest", "prepare_spawn"]
