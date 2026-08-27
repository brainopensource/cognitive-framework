"""Exterior M-6.5 meta-control contract.

The controller is a pure policy plugin. It cannot emit, access stores, call a
model, or bypass ordinary proposal and kernel authorization paths.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence

from ..domain.ledger.agent_view import AgentView
from ..domain.ledger.progress import ConfidenceRecord, ProgressView

__all__ = ["DIRECTIVE_KINDS", "MetaController", "StrategyDirective"]

DIRECTIVE_KINDS = frozenset({
    "revise_plan", "request_context", "abandon_hypothesis",
    "change_verification", "delegate", "conclude",
})


@dataclass(frozen=True, slots=True)
class StrategyDirective:
    kind: str
    controller_id: str
    reason: str
    brief: str | None = None
    scope_slice: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.kind not in DIRECTIVE_KINDS:
            raise ValueError("unsupported strategy directive")
        if not self.controller_id or not self.reason:
            raise ValueError("controller_id and reason are required")
        if self.kind == "delegate" and not self.brief:
            raise ValueError("delegate directive requires a brief")


class MetaController(Protocol):
    """Pure between-turn consultation; no authority or side effects."""

    controller_id: str

    def assess(
        self,
        view: AgentView,
        progress: ProgressView,
        confidence: Sequence[ConfidenceRecord],
    ) -> StrategyDirective | None: ...
