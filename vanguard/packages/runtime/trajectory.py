"""Assemble `mhf.trajectory/1` at episode completion (1.3-D, F-12)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ..domain.canonicalisation.digest import digest_of
from ..kernel.model import Event

_ZERO_COST = {"usd_micros": 0, "tokens": 0, "bytes": 0, "millis": 0}


def signed_verdict_object(verdict: Any) -> Mapping[str, Any] | None:
    binding = getattr(verdict, "binding", None)
    signature = getattr(verdict, "signature", None)
    if not binding or not signature:
        return None
    return {**dict(binding), "signature": signature}


def assemble_trajectory(
    *,
    task: Any,
    harness_digest: str,
    terminal: str,
    receipts: Sequence[Any],
    contexts: Sequence[Mapping[str, Any]],
    events: Sequence[Event],
    verdict: Any,
) -> dict[str, Any]:
    turns: list[dict[str, Any]] = []
    proposals = [e for e in events if e.kind == "ProposalProduced"]
    for index, proposal in enumerate(proposals):
        ctx = contexts[index] if index < len(contexts) else {}
        context_digest = digest_of(dict(ctx) if ctx else {"turn": index})
        turn_receipts = []
        if index < len(receipts):
            rec = receipts[index]
            outcome = rec.outcome if rec.outcome in (
                "completed", "failed", "rejected", "undeterminable",
            ) else ("completed" if rec.outcome == "ok" else "failed")
            turn_receipts.append({
                "request_digest": rec.descriptor_digest or digest_of({"turn": index}),
                "outcome": outcome,
                "grant_digest": rec.grant_digest,
                "lease_id": rec.lease_id,
            })
        turns.append({
            "turn": index,
            "context_digest": context_digest,
            "proposal": dict(proposal.payload),
            "receipts": turn_receipts,
            "cost": dict(_ZERO_COST),
        })
    outcome_map = {
        "completed": "completed",
        "abandoned": "aborted",
        "budget_exhausted": "budget_exhausted",
        "runtime_error": "instrument_error",
        "cancelled": "aborted",
        "escalated": "aborted",
        "abstained": "completed",
    }
    terminal_name = getattr(terminal, "value", str(terminal)).lower()
    return {
        "schema": "mhf.trajectory/1",
        "project_id": task.project_id,
        "run_id": task.run_id,
        "episode_id": task.episode_id,
        "parent_episode_id": task.parent_episode_id,
        "principal_id": task.principal,
        "harness_digest": harness_digest,
        "turns": turns,
        "verdict": signed_verdict_object(verdict),
        "cost": dict(_ZERO_COST),
        "outcome": outcome_map.get(terminal_name, "aborted"),
    }


class DelayedTerminalEmitter:
    """Hold `EpisodeCompleted` until the trajectory (and verdict) are known."""

    def __init__(self, inner: Any) -> None:
        self._inner = inner
        self.pending: Event | None = None

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def emit(self, event: Event) -> Any:
        if event.kind == "EpisodeCompleted":
            self.pending = event
            return None
        return self._inner.emit(event)

    def append_intent(self, event: Event) -> None:
        return self._inner.append_intent(event)

    def flush(self, trajectory: Mapping[str, Any]) -> None:
        if self.pending is None:
            return
        payload = {**dict(self.pending.payload), "trajectory": dict(trajectory)}
        flushed = Event(
            kind=self.pending.kind,
            reason=self.pending.reason,
            at=self.pending.at,
            run_id=self.pending.run_id,
            principal=self.pending.principal,
            payload=payload,
            alertable=self.pending.alertable,
        )
        self._inner.emit(flushed)
        self.pending = None
