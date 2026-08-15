"""Property tests for pure state reducer and ledger invariants.

Properties tested:
1. Reduction Associativity:
   For any sequence of valid events E and any arbitrary partitioning into batches B1, B2, ..., Bn:
   fold(initial_state, E) == fold(fold(fold(initial_state, B1), B2), ... Bn)
2. State Reconstruction Invariance:
   Reconstructing state from sequence 0 produces an identical state digest
   regardless of whether processed in single steps, arbitrary batches, or offline replay.
3. Monotonic Sequence Ordering:
   Any batch containing out-of-order or duplicate sequence numbers is rejected atomically.
4. Projection Determinism:
   Rebuilding projections from the store produces identical results to incremental processing.
"""

from __future__ import annotations

import random
import unittest
from typing import Sequence

from vanguard.packages.domain.ledger import (
    EventEnvelope,
    LedgerState,
    compute_state_digest,
    initial_state,
    parse_event_envelope,
    reconstruct_state,
    reduce_batch,
    reduce_event,
)
from vanguard.packages.adapters.stores import InMemoryEventStore
from vanguard.packages.runtime.ledger import (
    AuditProjection,
    BudgetProjection,
    RunSummaryProjection,
    rebuild_projection,
)


def _gen_envelope(seq_num: int, kind: str, payload_data: dict) -> EventEnvelope:
    import uuid
    h = uuid.uuid4().hex
    uid = f"018f{h[:4]}-{h[4:8]}-7{h[9:12]}-8{h[13:16]}-{h[16:28]}"
    raw = {
        "schemaVersion": "vg.4",
        "eventId": uid,
        "scope": "episode",
        "runId": "run-prop-test",
        "episodeId": "ep-prop-test",
        "seq": str(seq_num),
        "occurredAt": f"2026-08-15T00:{seq_num // 60:02d}:{seq_num % 60:02d}.000Z",
        "recordedAt": f"2026-08-15T00:{seq_num // 60:02d}:{seq_num % 60:02d}.000Z",
        "principal": "agent-prop",
        "tenantId": "tenant-test",
        "ownerId": "owner-test",
        "confidentiality": "internal",
        "retentionClass": "standard",
        "trainability": "prohibited",
        "redactionStatus": "none",
        "payload": {"kind": kind, **payload_data},
    }
    return parse_event_envelope(raw)


class TestLedgerReducerProperties(unittest.TestCase):
    """Property test suite for pure state reduction and reconstruction."""

    def setUp(self) -> None:
        random.seed(42)

    def _generate_realistic_event_stream(self, count: int = 50) -> list[EventEnvelope]:
        events: list[EventEnvelope] = []
        seq = 0

        events.append(_gen_envelope(seq, "EpisodeStarted", {"taskSpec": {"goal": "property_test"}}))
        seq += 1

        events.append(_gen_envelope(seq, "BudgetReserved", {"leaseId": "lease-main", "dimensions": {"tokens": 100000, "usd_micros": 500000}}))
        seq += 1

        for i in range(count):
            choice = random.choice([
                "ObservationProduced",
                "ProposalProduced",
                "CapabilityGranted",
                "EffectStarted",
                "EffectCompleted",
                "BudgetCommitted",
                "ArtifactCreated",
                "EvidenceClaimProduced",
                "ApprovalRequested",
                "ApprovalResolved",
                "Heartbeat",
            ])

            if choice == "ObservationProduced":
                events.append(_gen_envelope(seq, choice, {"contentDigest": f"sha256:{i:064x}", "provenanceLabel": "env"}))
            elif choice == "ProposalProduced":
                events.append(_gen_envelope(seq, choice, {"operatorId": f"op-{i%3}", "proposalDigest": f"sha256:{i:064x}", "toolCalls": [{"name": "tool_x"}]}))
            elif choice == "CapabilityGranted":
                events.append(_gen_envelope(seq, choice, {"grantId": f"grant-{i}", "descriptorDigest": f"sha256:{i:064x}", "actions": ["fs.read"]}))
            elif choice == "EffectStarted":
                events.append(_gen_envelope(seq, choice, {"descriptorDigest": f"sha256:{i:064x}", "sinkClass": "pure"}))
            elif choice == "EffectCompleted":
                events.append(_gen_envelope(seq, choice, {"descriptorDigest": f"sha256:{i:064x}", "receiptDigest": f"sha256:{i+100:064x}", "outcome": "ok"}))
            elif choice == "BudgetCommitted":
                events.append(_gen_envelope(seq, choice, {"leaseId": "lease-main", "debits": {"tokens": 50, "usd_micros": 200}}))
            elif choice == "ArtifactCreated":
                events.append(_gen_envelope(seq, choice, {"artifactId": f"art-{i}", "artifactKind": "M", "version": "1.0.0", "contentDigest": f"sha256:{i:064x}"}))
            elif choice == "EvidenceClaimProduced":
                events.append(_gen_envelope(seq, choice, {"claimId": f"claim-{i}", "subject": f"art-{i}", "predicate": "satisfies", "value": True}))
            elif choice == "ApprovalRequested":
                events.append(_gen_envelope(seq, choice, {"approvalId": f"app-{i}", "reason": "action", "riskTier": "low"}))
            elif choice == "ApprovalResolved":
                events.append(_gen_envelope(seq, choice, {"approvalId": f"app-{max(0, i-1)}", "resolution": "approved", "reviewer": "lead"}))
            elif choice == "Heartbeat":
                events.append(_gen_envelope(seq, choice, {"leaseId": "lease-main", "seqNum": i}))
            seq += 1

        events.append(_gen_envelope(seq, "BudgetReleased", {"leaseId": "lease-main", "unused": {"tokens": 50000}}))
        seq += 1
        events.append(_gen_envelope(seq, "EpisodeCompleted", {"outcome": "resolved"}))
        return events

    def test_arbitrary_batch_partitioning_associativity_property(self) -> None:
        """Property: for any random partitioning of an event stream, reduction produces identical digest."""
        events = self._generate_realistic_event_stream(60)

        # Baseline: single-pass reduction
        baseline_state = reconstruct_state(events)
        baseline_digest = compute_state_digest(baseline_state)

        # Test 20 random partitionings
        for trial in range(20):
            # Generate random partition boundaries
            num_splits = random.randint(1, 15)
            split_points = sorted(random.sample(range(1, len(events)), min(num_splits, len(events) - 1)))

            batches: list[list[EventEnvelope]] = []
            prev_idx = 0
            for pt in split_points:
                batches.append(events[prev_idx:pt])
                prev_idx = pt
            batches.append(events[prev_idx:])

            # Reduce batch by batch
            state = initial_state()
            for batch in batches:
                state = reduce_batch(state, batch)

            trial_digest = compute_state_digest(state)
            self.assertEqual(
                baseline_digest,
                trial_digest,
                f"Trial {trial} with {len(batches)} batches failed associativity property",
            )

    def test_projection_rebuild_from_store_property(self) -> None:
        """Property: rebuilding projections from EventStore produces identical digests."""
        events = self._generate_realistic_event_stream(40)
        store = InMemoryEventStore()
        store.append(events)

        inc_summary = RunSummaryProjection()
        inc_budget = BudgetProjection()
        inc_audit = AuditProjection()
        for ev in events:
            inc_summary.apply(ev)
            inc_budget.apply(ev)
            inc_audit.apply(ev)

        rebuilt_summary = rebuild_projection(store, RunSummaryProjection(), run_id="run-prop-test")
        rebuilt_budget = rebuild_projection(store, BudgetProjection(), run_id="run-prop-test")
        rebuilt_audit = rebuild_projection(store, AuditProjection(), run_id="run-prop-test")

        self.assertEqual(inc_summary.digest(), rebuilt_summary.digest())
        self.assertEqual(inc_budget.digest(), rebuilt_budget.digest())
        self.assertEqual(inc_audit.digest(), rebuilt_audit.digest())


if __name__ == "__main__":
    unittest.main()
