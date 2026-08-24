"""Derive the M-3C foundation bundle from canonical runtime artifacts."""

from __future__ import annotations

from typing import Any, Mapping

from ..domain.canonicalisation.digest import digest_of
from ..domain.evidence.foundation import (
    FoundationEvidence,
    EvidenceRow,
    build_foundation_evidence,
    derived,
)
from ..ports.event_store import EventRange
from .authority_audit import audit_runtime_authority


def derive_foundation_bundle(
    *, run_plan: Any, result: Any, store: Any,
) -> FoundationEvidence:
    """Build derived rows where canonical sources exist; leave all gaps absent."""
    read = store.read(EventRange(run_id=run_plan.run_id))
    envelopes = list(read.value) if read.ok and read.value else []
    trajectory = dict(result.trajectory or {})
    rows: list[EvidenceRow] = []

    routes = list(trajectory.get("model_routes_used") or ())
    if routes:
        route = dict(routes[0])
        turns = list(trajectory.get("turns") or ())
        usage = _usage(turns)
        source = {
            "row": 1, "run_id": run_plan.run_id,
            "provider": route.get("provider"), "model": route.get("model"),
            "fingerprint": route.get("model_fingerprint"),
            "measurement_status": usage["measurement_status"],
            "evidence_label": f"live-{route.get('provider')}", **usage,
        }
        rows.append(derived(1, source, source))

    trace = audit_runtime_authority()
    trace_source = {
        "row": 9, "run_id": run_plan.run_id,
        "runtime_path": trace.public_boundary,
        "layer0_used": False,
        "canonical_trace_verified": trace.passed,
        "alternate_runtime_detected": not trace.passed,
        "trace_digest": trace.trace_digest,
        "files": list(trace.files), "violations": list(trace.violations),
    }
    rows.append(derived(9, trace_source, trace_source))

    if trajectory:
        receipt_digests = [
            digest_of({"verb": r.verb, "descriptor": r.descriptor_digest,
                       "outcome": r.outcome}) for r in result.receipts
        ]
        source = {
            "row": 8, "run_id": run_plan.run_id,
            "schema": trajectory.get("schema"),
            "cost_conserved": _cost_conserved(trajectory),
            "harness_digest": trajectory.get("harness_digest"),
            "state_digest": trajectory.get("state_digest"),
            "execution_digest": trajectory.get("run_digest"),
            "turns_count": len(trajectory.get("turns") or ()),
            "receipts": receipt_digests,
            "trajectory_digest": digest_of(trajectory),
        }
        rows.append(derived(8, source, source))

    if envelopes and bool(run_plan.store.get("durable")):
        kinds = [e.payload.get("kind") for e in envelopes]
        source = {
            "row": 6, "run_id": run_plan.run_id,
            "event_count": len(envelopes),
            "hash_chain_valid": _chain_valid(envelopes),
            "event_range": {"first": int(envelopes[0].seq),
                            "last": int(envelopes[-1].seq)},
            "chain_digest": envelopes[-1].content_digest or envelopes[-1].digest(),
            "durable_intent_present": "EffectStarted" in kinds,
            "wal_mode": run_plan.store.get("journal_mode"),
            "run_digest": run_plan.run_digest,
        }
        rows.append(derived(6, source, source))

    event_range = {
        "first_seq": int(envelopes[0].seq) if envelopes else None,
        "last_seq": int(envelopes[-1].seq) if envelopes else None,
        "count": len(envelopes),
    }
    terminal = (
        envelopes[-1].content_digest or envelopes[-1].digest() if envelopes else ""
    )
    return build_foundation_evidence(
        lineage=run_plan.lineage(), task_digest=run_plan.task_digest,
        oracle=run_plan.oracle, event_range=event_range,
        terminal_chain_digest=terminal, rows=rows,
    )


def _usage(turns: list[Mapping[str, Any]]) -> dict[str, Any]:
    prompt = completion = total = 0
    measured = bool(turns)
    for turn in turns:
        cost = turn.get("cost") or {}
        total += int(cost.get("tokens") or 0)
        statuses = cost.get("measurement_status") or {}
        measured = measured and (statuses.get("tokens") or {}).get("status") == "measured"
    return {"prompt_tokens": prompt, "completion_tokens": completion,
            "total_tokens": total,
            "measurement_status": "measured" if measured else "unavailable"}


def _cost_conserved(trajectory: Mapping[str, Any]) -> bool:
    turns = list(trajectory.get("turns") or ())
    total = trajectory.get("cost") or {}
    return all(
        int(total.get(dim) or 0) == sum(int((t.get("cost") or {}).get(dim) or 0) for t in turns)
        for dim in ("usd_micros", "tokens", "bytes", "millis")
    )


def _chain_valid(envelopes: list[Any]) -> bool:
    return all(
        envelopes[index].prev_digest == (
            envelopes[index - 1].content_digest or envelopes[index - 1].digest()
        ) for index in range(1, len(envelopes))
    )
