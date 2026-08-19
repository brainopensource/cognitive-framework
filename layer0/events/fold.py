"""Cold ledger fold: fold(events) -> State. Pure, no I/O, no clock, no randomness."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Iterable, Mapping

from layer0.spi.types_gen import EventEnvelope, EventKind, Reservation

__all__ = ["FoldState", "fold", "initial_state"]


@dataclass(frozen=True, slots=True)
class FoldState:
    run_id: str | None = None
    episode_id: str | None = None
    branch_id: str = "main"
    last_seq: int | None = None
    fsm: str = "idle"
    grants: Mapping[str, Mapping[str, object]] = field(default_factory=dict)
    revoked: tuple[str, ...] = ()
    budget: Mapping[str, int] = field(default_factory=dict)
    approvals: tuple[Mapping[str, object], ...] = ()
    effects: Mapping[str, str] = field(default_factory=dict)
    plugins: Mapping[str, str] = field(default_factory=dict)
    turns: int = 0
    aborted: bool = False
    recovered: bool = False
    trajectory_digest: str | None = None
    open_intents: tuple[str, ...] = ()
    event_count: int = 0


def initial_state() -> FoldState:
    return FoldState(
        budget=Reservation(0, 0, 0, 0, 0, 0).as_map(),
    )


def fold(events: Iterable[EventEnvelope], start: FoldState | None = None) -> FoldState:
    state = start or initial_state()
    for envelope in events:
        state = _reduce(state, envelope)
    return state


def _reduce(state: FoldState, envelope: EventEnvelope) -> FoldState:
    if state.last_seq is not None and envelope.seq <= state.last_seq:
        raise ValueError(
            f"non-monotonic seq: {envelope.seq} <= {state.last_seq}"
        )
    kind = envelope.kind.value if isinstance(envelope.kind, EventKind) else str(envelope.kind)
    payload = dict(envelope.payload)
    grants = dict(state.grants)
    revoked = list(state.revoked)
    budget = dict(state.budget)
    approvals = list(state.approvals)
    effects = dict(state.effects)
    plugins = dict(state.plugins)
    intents = list(state.open_intents)
    fsm = state.fsm
    turns = state.turns
    aborted = state.aborted
    recovered = state.recovered
    trajectory = state.trajectory_digest

    if kind == "RunStarted":
        fsm = "running"
    elif kind == "EpisodeStarted":
        fsm = "episode"
    elif kind == "TurnStarted":
        turns += 1
        fsm = "turn"
    elif kind == "EpisodeCompleted":
        fsm = "episode_completed"
        trajectory = str(payload.get("trajectory_digest") or trajectory)
    elif kind == "RunCompleted":
        fsm = "completed"
    elif kind == "RunAborted":
        fsm = "aborted"
        aborted = True
    elif kind == "RunRecovered":
        fsm = "recovered"
        recovered = True
    elif kind == "CapabilityGranted":
        grant_id = str(payload.get("grantId") or payload.get("grant_id") or "")
        if grant_id:
            grants[grant_id] = dict(payload)
    elif kind == "CapabilityRevoked":
        grant_id = str(payload.get("grantId") or payload.get("grant_id") or "")
        if grant_id:
            revoked.append(grant_id)
            grants.pop(grant_id, None)
    elif kind == "BudgetReserved":
        reserved = payload.get("reserved")
        if isinstance(reserved, dict):
            for dim, amount in reserved.items():
                budget[str(dim)] = budget.get(str(dim), 0) + int(amount)
    elif kind == "BudgetCommitted":
        settlement = payload.get("settlement")
        if isinstance(settlement, dict):
            for dim, amount in settlement.items():
                # settlement is reserved - actual; spent is implied by actual.
                _ = amount
    elif kind == "BudgetExhausted":
        fsm = "budget_exhausted"
    elif kind == "ApprovalRequested":
        approvals.append({"status": "requested", **payload})
    elif kind == "ApprovalResolved":
        approvals.append({"status": "resolved", **payload})
    elif kind == "EffectStarted":
        digest = str(payload.get("descriptorDigest") or "")
        effects[digest] = "started"
        if digest:
            intents.append(digest)
    elif kind in {"EffectCompleted", "EffectFailed", "EffectRejected", "EffectReconciled"}:
        digest = str(payload.get("descriptorDigest") or "")
        effects[digest] = kind
        if digest in intents:
            intents.remove(digest)
    elif kind == "PluginResolved":
        plugins[str(payload.get("plugin_id") or "")] = "resolved"
    elif kind == "PluginActivated":
        plugins[str(payload.get("plugin_id") or "")] = "activated"
    elif kind == "PluginQuiesced":
        plugins[str(payload.get("plugin_id") or "")] = "quiesced"
    elif kind == "PluginRetired":
        plugins[str(payload.get("plugin_id") or "")] = "retired"
    elif kind == "PluginFaulted":
        plugins[str(payload.get("plugin_id") or "")] = "faulted"

    return replace(
        state,
        run_id=state.run_id or envelope.run_id,
        episode_id=state.episode_id or envelope.episode_id,
        branch_id=envelope.branch_id,
        last_seq=envelope.seq,
        fsm=fsm,
        grants=grants,
        revoked=tuple(revoked),
        budget=budget,
        approvals=tuple(approvals),
        effects=effects,
        plugins=plugins,
        turns=turns,
        aborted=aborted,
        recovered=recovered,
        trajectory_digest=trajectory,
        open_intents=tuple(intents),
        event_count=state.event_count + 1,
    )
