"""Coding-harness session log: a projection of the episode ledger.

Owning contract: VG-04 §12 (ledger is memory); harvest P2-1 (no second session DB).
Alfa's W11-A exporter should emit this shape. Compact / cache-miss fields are
counted when present on envelopes; absence is zero, never invented.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .events import EventEnvelope
from .reducer import compute_state_digest, reconstruct_state

__all__ = ["project_coding_session"]

_SESSION_SCHEMA = "vg.coding-session.v1"
_COMPACT_KINDS = frozenset({"ContextCompacted", "DialogueCompacted", "ObservationEvicted"})


def _verb_names(tool_calls: Any) -> list[str]:
    names: list[str] = []
    if not isinstance(tool_calls, list):
        return names
    for call in tool_calls:
        if not isinstance(call, Mapping):
            continue
        name = call.get("name") or call.get("verb") or call.get("action")
        if isinstance(name, str) and name:
            names.append(name)
    return names


def _as_str_list(value: Any) -> list[str]:
    if isinstance(value, str) and value:
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item]
    return []


def project_coding_session(envelopes: Sequence[EventEnvelope]) -> dict[str, Any]:
    """Reduce envelopes to the measurement surface for a coding episode.

    Turns = ``ProposalProduced`` count (same as ``HarnessSession.turns_consumed``).
    Verbs come from proposal ``toolCalls``. Receipts come from completed effects.
    """
    state = reconstruct_state(envelopes)
    turns: list[dict[str, Any]] = []
    for index, proposal in enumerate(state.proposals, start=1):
        turns.append({
            "turn": index,
            "seq": proposal.get("seq"),
            "verbs": _verb_names(proposal.get("toolCalls")),
            "proposalDigest": proposal.get("proposalDigest"),
        })

    effects = [
        {
            "descriptorDigest": record.descriptor_digest,
            "status": record.status,
            "outcome": record.outcome,
            "receiptDigest": record.receipt_digest,
        }
        for record in state.effects.values()
    ]

    cache_miss_count = 0
    compact_count = 0
    dead_ends: list[str] = []
    for envelope in envelopes:
        payload = envelope.payload
        kind = payload.get("kind", "")
        if payload.get("cacheMiss") is True or payload.get("cache_miss") is True:
            cache_miss_count += 1
        if kind in _COMPACT_KINDS or "elided" in payload:
            compact_count += 1
        dead_ends.extend(_as_str_list(payload.get("deadEnds")))
        dead_ends.extend(_as_str_list(payload.get("dead_ends")))

    approvals = [
        {"approvalId": rec.approval_id, "status": rec.status, "riskTier": rec.risk_tier}
        for rec in state.approvals.values()
    ]

    return {
        "schema": _SESSION_SCHEMA,
        "episodeId": state.episode_id,
        "runId": state.run_id,
        "status": state.episode.status,
        "outcome": state.episode.outcome,
        "turnCount": len(state.proposals),
        "turns": turns,
        "effects": effects,
        "denialCount": len(state.denials),
        "denials": list(state.denials),
        "approvals": approvals,
        "budgetDebits": dict(state.cumulative_budget_debits),
        "cacheMissCount": cache_miss_count,
        "compactCount": compact_count,
        "deadEnds": dead_ends,
        "stateDigest": compute_state_digest(state),
    }
