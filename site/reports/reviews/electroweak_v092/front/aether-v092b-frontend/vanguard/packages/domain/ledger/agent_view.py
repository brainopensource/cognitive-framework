"""Deterministic event-derived AgentView projection for M-5a.

AgentView is a projection, never a second source of truth. It can be rebuilt
from a file-backed event sequence in a fresh process and therefore contains no
runtime handles, clocks, caches, or authority decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Iterable, Mapping

from ..canonicalisation.digest import digest_of
from .events import EventEnvelope, READABLE_KINDS
from .reducer import ReducerError

__all__ = [
    "AGENT_VIEW_REDUCER_VERSION",
    "AgentView",
    "AgentViewCheckpoint",
    "fold_agent_view",
]

AGENT_VIEW_REDUCER_VERSION = "m5a.agent_view/1"
_TERMINAL_KINDS = frozenset({"EpisodeCompleted", "RunCompleted", "RunAborted", "RunRecovered"})
_EFFECT_KINDS = frozenset({"EffectCompleted", "EffectFailed", "EffectRejected", "EffectReconciled"})
_BUDGET_KINDS = frozenset({"BudgetCommitted", "BudgetExhausted"})


@dataclass(frozen=True, slots=True)
class AgentView:
    lineage_id: str
    goal: str | None = None
    plan_revisions: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    attempts: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    settled_effects: Mapping[str, str] = field(default_factory=dict)
    budget_consumed: Mapping[str, int] = field(default_factory=dict)
    strategy: str | None = None
    progress_log: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    context_epoch: int = 0
    children: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    terminal: str | None = None
    covered_through: str = ""
    reducer_version: str = AGENT_VIEW_REDUCER_VERSION

    def to_canonical_dict(self) -> dict[str, Any]:
        """Return the stable JSON-shaped projection used by RF-96."""

        return {
            "lineageId": self.lineage_id,
            "goal": self.goal,
            "planRevisions": [dict(item) for item in self.plan_revisions],
            "attempts": [dict(item) for item in self.attempts],
            "settledEffects": dict(sorted(self.settled_effects.items())),
            "budgetConsumed": dict(sorted(self.budget_consumed.items())),
            "strategy": self.strategy,
            "progressLog": [dict(item) for item in self.progress_log],
            "contextEpoch": self.context_epoch,
            "children": [dict(item) for item in self.children],
            "terminal": self.terminal,
            "coveredThrough": self.covered_through,
            "reducerVersion": self.reducer_version,
        }

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())

    @classmethod
    def empty(cls, lineage_id: str = "") -> "AgentView":
        """Construct an initial empty AgentView."""
        return cls(lineage_id=lineage_id)

    @staticmethod
    def fold(
        events: Iterable[EventEnvelope],
        checkpoint: AgentViewCheckpoint | None = None,
    ) -> "AgentView":
        """Deterministic fold of events into an AgentView."""
        return fold_agent_view(checkpoint, events)


@dataclass(frozen=True, slots=True)
class AgentViewCheckpoint:
    """Runtime-neutral checkpoint value consumed by a future CheckpointManager."""

    view: AgentView
    state_digest: str
    covered_through_event_id: str
    covered_through_seq: str
    reducer_version: str = AGENT_VIEW_REDUCER_VERSION


def _kind(event: EventEnvelope) -> str:
    return str(event.payload.get("kind") or event.mhf_kind or "")


def _lineage(event: EventEnvelope) -> str:
    return str(event.principal_id or event.payload.get("lineageId") or event.principal)


def _effect_key(payload: Mapping[str, Any]) -> str | None:
    return payload.get("idempotencyKey") or payload.get("idempotency_key") or payload.get("descriptorDigest")


def _copy_payload(payload: Mapping[str, Any], *, event: EventEnvelope) -> dict[str, Any]:
    """Copy only JSON values and bind the event identity without raw context."""

    return {
        "eventId": event.event_id,
        "seq": event.seq,
        **{str(key): value for key, value in payload.items() if key != "kind"},
    }


def fold_agent_view(
    checkpoint: AgentViewCheckpoint | None,
    events: Iterable[EventEnvelope],
) -> AgentView:
    """Fold one lineage deterministically, optionally from a trusted checkpoint.

    A checkpoint is only a starting projection. Events at or before its covered
    sequence are ignored; all later events are validated and folded. A caller
    must verify blob bytes and reducer pins before constructing the checkpoint.
    """

    if checkpoint is not None:
        if checkpoint.reducer_version != AGENT_VIEW_REDUCER_VERSION:
            raise ReducerError("AgentView checkpoint reducer version is not current")
        view = checkpoint.view
        covered_seq = int(checkpoint.covered_through_seq)
        last_seq = covered_seq
    else:
        view = AgentView(lineage_id="")
        last_seq = -1

    plans = list(view.plan_revisions)
    attempts = [dict(item) for item in view.attempts]
    settled = dict(view.settled_effects)
    budget = {key: int(value) for key, value in view.budget_consumed.items()}
    progress = list(view.progress_log)
    children = [dict(item) for item in view.children]
    goal = view.goal
    strategy = view.strategy
    context_epoch = view.context_epoch
    terminal = view.terminal
    covered_through = view.covered_through
    lineage_id = view.lineage_id

    for event in events:
        seq = int(event.seq)
        if seq <= last_seq:
            continue
        if lineage_id and _lineage(event) != lineage_id:
            raise ReducerError(
                f"event {event.event_id} belongs to lineage {_lineage(event)!r}, "
                f"expected {lineage_id!r}"
            )
        if not lineage_id:
            lineage_id = _lineage(event)
        kind = _kind(event)
        if kind not in READABLE_KINDS:
            raise ReducerError(f"event kind is not readable: {kind!r}")
        payload = event.payload

        if kind == "GoalDeclared":
            goal = payload.get("goalDigest") or payload.get("goalArtifact")
        elif kind == "PlanRevised":
            plans.append(_copy_payload(payload, event=event))
        elif kind == "StrategyChanged":
            strategy = payload.get("to") or payload.get("toStrategy")
        elif kind == "ProgressAssessed":
            progress.append(_copy_payload(payload, event=event))
        elif kind == "ContextCompacted":
            context_epoch += 1
        elif kind == "ProposalProduced":
            attempts.append({
                "eventId": event.event_id,
                "operationId": payload.get("operationId") or event.event_id,
                # Production `/2` events use `action`; older readable history
                # used `verb` or `operatorId`.
                "verb": payload.get("action") or payload.get("verb") or payload.get("operatorId") or "unknown",
                "status": "proposed",
            })
        elif kind == "EffectStarted":
            attempts.append({
                "eventId": event.event_id,
                "operationId": payload.get("operationId") or payload.get("descriptorDigest") or event.event_id,
                "verb": payload.get("action") or payload.get("verb") or "effect",
                "status": "dispatched",
            })
        elif kind in _EFFECT_KINDS:
            key = _effect_key(payload)
            status = str(payload.get("status") or payload.get("outcome") or {
                "EffectCompleted": "settled",
                "EffectFailed": "failed",
                "EffectRejected": "rejected",
                "EffectReconciled": "reconciled",
            }[kind])
            if key:
                settled[key] = status
            operation_id = payload.get("operationId") or key
            if operation_id:
                attempts.append({
                    "eventId": event.event_id,
                    "operationId": operation_id,
                    "verb": payload.get("action") or payload.get("verb") or "effect",
                    "status": status,
                })
        elif kind in _BUDGET_KINDS:
            for key, value in (payload.get("debits") or payload.get("settlement") or payload.get("dimensions") or {}).items():
                if key in {"usd_micros", "millis", "tokens", "bytes"}:
                    budget[key] = budget.get(key, 0) + int(value)
        elif kind == "ChildSpawned":
            child_id = payload.get("childEpisodeId") or payload.get("childLineageId") or payload.get("childId")
            if child_id:
                children.append({"childId": child_id, "status": "open", **_copy_payload(payload, event=event)})
        elif kind == "ChildReturned":
            child_id = payload.get("childEpisodeId") or payload.get("childLineageId") or payload.get("childId")
            for index, child in enumerate(children):
                if child.get("childId") == child_id:
                    children[index] = {**child, "status": payload.get("status") or payload.get("outcome") or "returned", **_copy_payload(payload, event=event)}
        elif kind in _TERMINAL_KINDS:
            terminal = str(payload.get("outcome") or payload.get("status") or kind)

        last_seq = seq
        covered_through = event.event_id

    if not lineage_id:
        raise ReducerError("cannot construct AgentView from an empty event sequence")
    return replace(
        view,
        lineage_id=lineage_id,
        goal=goal,
        plan_revisions=tuple(plans),
        attempts=tuple(attempts),
        settled_effects=dict(sorted(settled.items())),
        budget_consumed=dict(sorted(budget.items())),
        strategy=strategy,
        progress_log=tuple(progress),
        context_epoch=context_epoch,
        children=tuple(children),
        terminal=terminal,
        covered_through=covered_through,
        reducer_version=AGENT_VIEW_REDUCER_VERSION,
    )
