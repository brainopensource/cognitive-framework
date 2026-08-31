"""Shared application result contracts for API and CLI clients."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

__all__ = ["RunResult", "StatusResult", "EvidenceResult", "CostResult"]


@dataclass(frozen=True, slots=True)
class RunResult:
    """One result shape used by the Python API, CLI, and Coding Max facade.

    Optional measurements stay ``None`` and are named in ``missing``.  This
    prevents an absent provider report from being serialized as a fabricated
    zero-cost or zero-token run.
    """

    run_id: str
    outcome: str
    phase: str
    turns: int
    plan_digest: str | None
    detail: str
    projections: tuple[Mapping[str, Any], ...] = ()
    episode_id: str | None = None
    task_digest: str | None = None
    composition_digest: str | None = None
    terminal_state: str | None = None
    next_action: str | None = None
    todo_state: tuple[Mapping[str, Any], ...] = ()
    verification_identity: Mapping[str, Any] | None = None
    model_route: Mapping[str, Any] | None = None
    token_usage: Mapping[str, int] | None = None
    observed_cost: int | None = None
    artifact_refs: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "episodeId": self.episode_id,
            "outcome": self.outcome,
            "phase": self.phase,
            "terminalState": self.terminal_state,
            "turns": self.turns,
            "planDigest": self.plan_digest,
            "taskDigest": self.task_digest,
            "compositionDigest": self.composition_digest,
            "nextAction": self.next_action,
            "todoState": [dict(item) for item in self.todo_state],
            "verificationIdentity": dict(self.verification_identity) if self.verification_identity else None,
            "modelRoute": dict(self.model_route) if self.model_route else None,
            "tokenUsage": dict(self.token_usage) if self.token_usage else None,
            "observedCost": self.observed_cost,
            "artifactRefs": list(self.artifact_refs),
            "missing": list(self.missing),
            "detail": self.detail,
            "projections": list(self.projections),
        }


@dataclass(frozen=True, slots=True)
class StatusResult:
    run_id: str
    status: str
    event_count: int
    as_of_seq: int
    manifest_path: str | None
    repo_path: str | None
    detail: str = ""
    episode_id: str | None = None
    task_digest: str | None = None
    composition_digest: str | None = None
    terminal_state: str | None = None
    next_action: str | None = None
    todo_state: tuple[Mapping[str, Any], ...] = ()
    verification_identity: Mapping[str, Any] | None = None
    model_route: Mapping[str, Any] | None = None
    missing: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "episodeId": self.episode_id,
            "status": self.status,
            "terminalState": self.terminal_state,
            "eventCount": self.event_count,
            "asOfSeq": self.as_of_seq,
            "manifestPath": self.manifest_path,
            "repoPath": self.repo_path,
            "taskDigest": self.task_digest,
            "compositionDigest": self.composition_digest,
            "nextAction": self.next_action,
            "todoState": [dict(item) for item in self.todo_state],
            "verificationIdentity": dict(self.verification_identity) if self.verification_identity else None,
            "modelRoute": dict(self.model_route) if self.model_route else None,
            "missing": list(self.missing),
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class EvidenceResult:
    """Durable evidence projection for one run.

    CLI and API serialize from this single shape.  Absent trajectory evidence
    is named in ``missing`` rather than fabricated.
    """

    run_id: str
    status: str
    event_count: int
    trajectory: Mapping[str, Any] | None
    event_digests: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "status": self.status,
            "events": self.event_count,
            "trajectory": self.trajectory,
            "eventDigests": list(self.event_digests),
            "missing": list(self.missing),
        }


@dataclass(frozen=True, slots=True)
class CostResult:
    """Observed budget settlement for one run.

    Absent settlement dimensions stay absent: an unobserved cost is reported
    through ``missing``, never as a placeholder zero.
    """

    run_id: str
    observed: bool
    observed_cost: int | None
    settlement: Mapping[str, int] = field(default_factory=dict)
    missing: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "observed": self.observed,
            "observedCost": self.observed_cost,
            "settlement": dict(self.settlement),
            "missing": list(self.missing),
        }
