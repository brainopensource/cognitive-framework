"""Contract and property test suite for Event Store & State Ledger (T3.1–T3.8).

Owning contracts:
- GTS-13C T3.1..T3.8
- VG-04 §12 (Event envelope, minimum event set, storage rules CT-40..CT-50)
- VG-01 §2, §4 (Pure reducer invariants, cassette replay)
- ICD §4 (EventStore and storage ports)
"""

from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.ledger import (
    EVENT_KINDS,
    ApprovalRecord,
    ArtifactRecord,
    BudgetLeaseState,
    EffectRecord,
    EpisodeState,
    EventEnvelope,
    EvidenceRecord,
    LedgerState,
    ReducerError,
    compute_state_digest,
    initial_state,
    parse_event_envelope,
    reconstruct_state,
    reduce_batch,
    reduce_event,
)
from vanguard.packages.adapters.models import (
    Cassette,
    CassettePlayer,
    CassetteRecorder,
)
from vanguard.packages.adapters.stores import (
    InMemoryEventStore,
    RedactionPolicy,
    SqliteEventStore,
    export_jsonl,
    import_jsonl,
    redact_envelope,
)
from vanguard.packages.domain.ledger.reconciliation import EffectReconciler
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.ledger import (
    ArtifactRegistryProjection,
    AuditProjection,
    BudgetProjection,
    RecoveryScanner,
    RunSummaryProjection,
    rebuild_projection,
)


def _make_envelope(
    seq: str,
    kind: str,
    payload_fields: dict[str, Any],
    run_id: str = "run-001",
    episode_id: str = "ep-001",
    scope: str = "episode",
    occurred_at: str = "2026-08-15T00:00:00.000Z",
    confidentiality: str = "internal",
    event_id: str = "018f1234-5678-7000-8000-000000000001",
) -> EventEnvelope:
    payload = {"kind": kind, **payload_fields}
    raw = {
        "schemaVersion": "vg.4",
        "eventId": event_id,
        "scope": scope,
        "runId": run_id,
        "episodeId": episode_id if scope == "episode" else None,
        "seq": seq,
        "occurredAt": occurred_at,
        "recordedAt": occurred_at,
        "principal": "agent-alpha",
        "tenantId": "tenant-corp",
        "ownerId": "owner-alice",
        "confidentiality": confidentiality,
        "retentionClass": "standard",
        "trainability": "prohibited",
        "redactionStatus": "none",
        "traceId": "trace-xyz",
        "spanId": "span-123",
        "payload": payload,
    }
    if raw["episodeId"] is None:
        del raw["episodeId"]
    return parse_event_envelope(raw)


class TestT3_1_EventStore(unittest.TestCase):
    """T3.1: Transactional append-only store, single writer, monotonic sequence, crash-safe."""

    def test_in_memory_store_lifecycle_and_monotonicity(self) -> None:
        store = InMemoryEventStore()
        e0 = _make_envelope("0", "EpisodeStarted", {"taskSpec": {"name": "fix_bug"}}, event_id="018f1111-1111-7000-8000-000000000001")
        e1 = _make_envelope("1", "ObservationProduced", {"contentDigest": "sha256:" + "a" * 64, "provenanceLabel": "repo"}, event_id="018f1111-1111-7000-8000-000000000002")
        e2 = _make_envelope("2", "EpisodeCompleted", {"outcome": "resolved"}, event_id="018f1111-1111-7000-8000-000000000003")

        # Atomic append batch
        res = store.append([e0, e1])
        self.assertTrue(res.ok)
        self.assertEqual(store.count("run-001"), 2)

        # Monotonicity check: appending duplicate or lower seq must fail
        e_dup = _make_envelope("1", "ObservationProduced", {"contentDigest": "sha256:" + "a" * 64, "provenanceLabel": "repo"}, event_id="018f1111-1111-7000-8000-000000000004")
        res_dup = store.append([e_dup])
        self.assertFalse(res_dup.ok)
        self.assertEqual(res_dup.error.kind, "conflict")
        # Store count remained 2 (atomic, didn't append)
        self.assertEqual(store.count("run-001"), 2)

        # Append valid next sequence
        res_next = store.append([e2])
        self.assertTrue(res_next.ok)
        self.assertEqual(store.count("run-001"), 3)

        # Read range
        read_all = store.read(EventRange(run_id="run-001"))
        self.assertTrue(read_all.ok)
        self.assertEqual(len(read_all.value), 3)

        # Read with after_seq
        read_after = store.read(EventRange(run_id="run-001", after_seq="0", limit=1))
        self.assertTrue(read_after.ok)
        self.assertEqual(len(read_after.value), 1)
        self.assertEqual(read_after.value[0].seq, "1")

        # Digest
        digest_res = store.digest("run-001")
        self.assertTrue(digest_res.ok)
        self.assertTrue(digest_res.value.startswith("sha256:"))

    def test_sqlite_event_store_wal_transactions_and_crash_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "ledger.db"
            store = SqliteEventStore(db_file)

            e0 = _make_envelope("0", "EpisodeStarted", {"taskSpec": {"name": "eval"}}, event_id="018f2222-1111-7000-8000-000000000001")
            e1 = _make_envelope("1", "CapabilityGranted", {"grantId": "g-1", "descriptorDigest": "sha256:" + "b" * 64, "actions": ["fs.read"]}, event_id="018f2222-1111-7000-8000-000000000002")
            e2 = _make_envelope("2", "EpisodeCompleted", {"outcome": "resolved"}, event_id="018f2222-1111-7000-8000-000000000003")

            # Append transaction
            res = store.append([e0, e1])
            self.assertTrue(res.ok)
            self.assertEqual(store.count("run-001"), 2)

            # Atomic transaction rollback on conflict inside batch
            e_bad1 = _make_envelope("3", "ObservationProduced", {"contentDigest": "sha256:" + "c" * 64}, event_id="018f2222-1111-7000-8000-000000000004")
            e_bad2 = _make_envelope("1", "ObservationProduced", {"contentDigest": "sha256:" + "d" * 64}, event_id="018f2222-1111-7000-8000-000000000005")  # conflict
            res_bad = store.append([e_bad1, e_bad2])
            self.assertFalse(res_bad.ok)
            # Verify rollback: e_bad1 was not committed
            self.assertEqual(store.count("run-001"), 2)

            # Append e2
            store.append([e2])
            self.assertEqual(store.count("run-001"), 3)

            # Close and reopen database to prove persistence / crash-safety
            store.close()
            store2 = SqliteEventStore(db_file)
            self.assertEqual(store2.count("run-001"), 3)

            events = store2.read(EventRange(run_id="run-001")).value
            self.assertEqual(len(events), 3)
            self.assertEqual(events[0].payload["kind"], "EpisodeStarted")
            self.assertEqual(events[1].payload["kind"], "CapabilityGranted")
            self.assertEqual(events[2].payload["kind"], "EpisodeCompleted")
            store2.close()


class TestT3_2_PureReducer(unittest.TestCase):
    """T3.2: Pure reducer (State, Event) -> State in domain/, zero I/O. Property test: associative over batches."""

    def test_associativity_over_batches(self) -> None:
        """Associative law: reduce(reduce(s, B1), B2) == reduce(s, B1 + B2)."""
        e0 = _make_envelope("0", "EpisodeStarted", {"taskSpec": {"name": "test"}}, event_id="018f3333-1111-7000-8000-000000000001")
        e1 = _make_envelope("1", "BudgetReserved", {"leaseId": "l-1", "dimensions": {"tokens": 1000, "usd_micros": 50000}}, event_id="018f3333-1111-7000-8000-000000000002")
        e2 = _make_envelope("2", "CapabilityGranted", {"grantId": "g-1", "descriptorDigest": "sha256:" + "1" * 64, "actions": ["edit"]}, event_id="018f3333-1111-7000-8000-000000000003")
        e3 = _make_envelope("3", "EffectStarted", {"descriptorDigest": "sha256:" + "1" * 64, "sinkClass": "privileged", "grantId": "g-1"}, event_id="018f3333-1111-7000-8000-000000000004")
        e4 = _make_envelope("4", "EffectCompleted", {"descriptorDigest": "sha256:" + "1" * 64, "receiptDigest": "sha256:" + "2" * 64, "outcome": "ok", "resultDigest": "sha256:" + "3" * 64}, event_id="018f3333-1111-7000-8000-000000000005")
        e5 = _make_envelope("5", "BudgetCommitted", {"leaseId": "l-1", "debits": {"tokens": 450, "usd_micros": 20000}}, event_id="018f3333-1111-7000-8000-000000000006")
        e6 = _make_envelope("6", "BudgetReleased", {"leaseId": "l-1", "unused": {"tokens": 550, "usd_micros": 30000}}, event_id="018f3333-1111-7000-8000-000000000007")
        e7 = _make_envelope("7", "EpisodeCompleted", {"outcome": "resolved"}, event_id="018f3333-1111-7000-8000-000000000008")

        all_events = [e0, e1, e2, e3, e4, e5, e6, e7]

        # Partition into batches of various sizes
        batch1 = all_events[:3]
        batch2 = all_events[3:6]
        batch3 = all_events[6:]

        state_one_shot = reduce_batch(initial_state(), all_events)

        state_step1 = reduce_batch(initial_state(), batch1)
        state_step2 = reduce_batch(state_step1, batch2)
        state_partitioned = reduce_batch(state_step2, batch3)

        self.assertEqual(state_one_shot.to_canonical_dict(), state_partitioned.to_canonical_dict())
        self.assertEqual(state_one_shot.digest(), state_partitioned.digest())

    def test_minimum_event_set_handling(self) -> None:
        """Ensure all standard events in the minimum event set update state correctly."""
        events = [
            _make_envelope("0", "EpisodeStarted", {"taskSpec": {"name": "full"}}, event_id="018f4444-1111-7000-8000-000000000001"),
            _make_envelope("1", "ObservationProduced", {"snapshot": {"id": "s1"}, "contentDigest": "sha256:" + "a" * 64, "provenanceLabel": "env"}, event_id="018f4444-1111-7000-8000-000000000002"),
            _make_envelope("2", "ProposalProduced", {"operatorId": "op-1", "proposalDigest": "sha256:" + "b" * 64, "toolCalls": [{"name": "write"}]}, event_id="018f4444-1111-7000-8000-000000000003"),
            _make_envelope("3", "AuthorizationDenied", {"reason": "Out of budget", "requested": {"action": "write"}}, event_id="018f4444-1111-7000-8000-000000000004"),
            _make_envelope("4", "ApprovalRequested", {"approvalId": "app-1", "reason": "Elevated action", "riskTier": "high"}, event_id="018f4444-1111-7000-8000-000000000005"),
            _make_envelope("5", "ApprovalResolved", {"approvalId": "app-1", "resolution": "approved", "reviewer": "human-lead"}, event_id="018f4444-1111-7000-8000-000000000006"),
            _make_envelope("6", "ArtifactCreated", {"artifactId": "art-1", "artifactKind": "M", "version": "1.0.0", "contentDigest": "sha256:" + "c" * 64}, event_id="018f4444-1111-7000-8000-000000000007"),
            _make_envelope("7", "ActivationChanged", {"artifactId": "art-1", "toStatus": "quarantined"}, event_id="018f4444-1111-7000-8000-000000000008"),
            _make_envelope("8", "EvidenceClaimProduced", {"claimId": "claim-1", "subject": "art-1", "predicate": "valid", "value": True}, event_id="018f4444-1111-7000-8000-000000000009"),
            _make_envelope("9", "ConflictDetected", {"resource": "file:///workspace/a.txt", "conflictingRuns": ["run-002"]}, event_id="018f4444-1111-7000-8000-000000000010"),
            _make_envelope("10", "EpisodeCompleted", {"outcome": "resolved"}, event_id="018f4444-1111-7000-8000-000000000011"),
        ]

        state = reconstruct_state(events)
        self.assertEqual(state.episode.status, "completed")
        self.assertEqual(len(state.observations), 1)
        self.assertEqual(len(state.proposals), 1)
        self.assertEqual(len(state.denials), 1)
        self.assertEqual(state.approvals["app-1"].status, "approved")
        self.assertEqual(state.approvals["app-1"].reviewer, "human-lead")
        self.assertEqual(state.artifacts["art-1"].status, "quarantined")
        self.assertEqual(state.evidence_claims["claim-1"].subject, "art-1")
        self.assertEqual(len(state.conflicts), 1)

    def test_ct44_unknown_event_preservation(self) -> None:
        """CT-44: unknown event kinds are preserved without crashing."""
        e0 = _make_envelope("0", "EpisodeStarted", {"taskSpec": {"name": "test"}}, event_id="018f5555-1111-7000-8000-000000000001")
        e_unknown = _make_envelope("1", "FutureNovelEventKind_v5", {"novelField": 12345}, event_id="018f5555-1111-7000-8000-000000000002")
        e2 = _make_envelope("2", "EpisodeCompleted", {"outcome": "resolved"}, event_id="018f5555-1111-7000-8000-000000000003")

        state = reconstruct_state([e0, e_unknown, e2])
        self.assertEqual(state.event_count, 3)
        self.assertEqual(len(state.unknown_events), 1)
        self.assertEqual(state.unknown_events[0]["kind"], "FutureNovelEventKind_v5")
        self.assertEqual(state.episode.status, "completed")

    def test_monotonic_sequence_enforcement(self) -> None:
        """Reducer rejects out-of-order or duplicate sequences."""
        e0 = _make_envelope("5", "EpisodeStarted", {"taskSpec": {}}, event_id="018f6666-1111-7000-8000-000000000001")
        e1 = _make_envelope("3", "EpisodeCompleted", {"outcome": "resolved"}, event_id="018f6666-1111-7000-8000-000000000002")

        state = reduce_event(initial_state(), e0)
        with self.assertRaises(ReducerError):
            reduce_event(state, e1)


class TestT3_3_StateReconstruction(unittest.TestCase):
    """T3.3: State reconstruction: replay yields an identical state digest."""

    def test_replay_yields_identical_digest(self) -> None:
        events = [
            _make_envelope("0", "EpisodeStarted", {"taskSpec": {"goal": "reproduce"}}, event_id="018f7777-1111-7000-8000-000000000001"),
            _make_envelope("1", "BudgetReserved", {"leaseId": "l-99", "dimensions": {"tokens": 5000}}, event_id="018f7777-1111-7000-8000-000000000002"),
            _make_envelope("2", "CapabilityGranted", {"grantId": "g-99", "descriptorDigest": "sha256:" + "9" * 64, "actions": ["git.commit"]}, event_id="018f7777-1111-7000-8000-000000000003"),
            _make_envelope("3", "EffectStarted", {"descriptorDigest": "sha256:" + "9" * 64, "sinkClass": "privileged"}, event_id="018f7777-1111-7000-8000-000000000004"),
            _make_envelope("4", "EffectCompleted", {"descriptorDigest": "sha256:" + "9" * 64, "receiptDigest": "sha256:" + "8" * 64, "outcome": "ok", "resultDigest": "sha256:" + "7" * 64}, event_id="018f7777-1111-7000-8000-000000000005"),
            _make_envelope("5", "EpisodeCompleted", {"outcome": "resolved"}, event_id="018f7777-1111-7000-8000-000000000006"),
        ]

        # Compute state incrementally (as in online execution)
        online_state = initial_state()
        for ev in events:
            online_state = reduce_event(online_state, ev)
        online_digest = compute_state_digest(online_state)

        # Reconstruct from scratch (as in offline audit / crash replay)
        replayed_state = reconstruct_state(events)
        replayed_digest = compute_state_digest(replayed_state)

        self.assertEqual(online_digest, replayed_digest)
        self.assertEqual(online_state.to_canonical_dict(), replayed_state.to_canonical_dict())


class TestT3_4_Projections(unittest.TestCase):
    """T3.4: Projections rebuildable from zero. A projection is a cache, never a source of truth."""

    def test_rebuilding_projections_from_zero(self) -> None:
        store = InMemoryEventStore()
        events = [
            _make_envelope("0", "EpisodeStarted", {"taskSpec": {"name": "proj"}}, event_id="018f8888-1111-7000-8000-000000000001"),
            _make_envelope("1", "BudgetReserved", {"leaseId": "l-1", "dimensions": {"tokens": 2000}}, event_id="018f8888-1111-7000-8000-000000000002"),
            _make_envelope("2", "CapabilityGranted", {"grantId": "g-1", "descriptorDigest": "sha256:" + "a" * 64, "actions": ["fs.read"]}, event_id="018f8888-1111-7000-8000-000000000003"),
            _make_envelope("3", "AuthorizationDenied", {"reason": "unauthorized path"}, event_id="018f8888-1111-7000-8000-000000000004"),
            _make_envelope("4", "ArtifactCreated", {"artifactId": "art-1", "kind": "R", "version": "0.1.0", "contentDigest": "sha256:" + "d" * 64}, event_id="018f8888-1111-7000-8000-000000000005"),
            _make_envelope("5", "EpisodeCompleted", {"outcome": "resolved"}, event_id="018f8888-1111-7000-8000-000000000006"),
        ]
        store.append(events)

        # Incremental projection
        inc_summary = RunSummaryProjection()
        inc_budget = BudgetProjection()
        inc_audit = AuditProjection()
        inc_artifacts = ArtifactRegistryProjection()
        for ev in events:
            inc_summary.apply(ev)
            inc_budget.apply(ev)
            inc_audit.apply(ev)
            inc_artifacts.apply(ev)

        # Rebuilt from store (from zero)
        rebuilt_summary = rebuild_projection(store, RunSummaryProjection(), run_id="run-001")
        rebuilt_budget = rebuild_projection(store, BudgetProjection(), run_id="run-001")
        rebuilt_audit = rebuild_projection(store, AuditProjection(), run_id="run-001")
        rebuilt_artifacts = rebuild_projection(store, ArtifactRegistryProjection(), run_id="run-001")

        self.assertEqual(inc_summary.to_dict(), rebuilt_summary.to_dict())
        self.assertEqual(inc_summary.digest(), rebuilt_summary.digest())

        self.assertEqual(inc_budget.to_dict(), rebuilt_budget.to_dict())
        self.assertEqual(inc_budget.digest(), rebuilt_budget.digest())

        self.assertEqual(inc_audit.to_dict(), rebuilt_audit.to_dict())
        self.assertEqual(inc_audit.digest(), rebuilt_audit.digest())

        self.assertEqual(inc_artifacts.to_dict(), rebuilt_artifacts.to_dict())
        self.assertEqual(inc_artifacts.digest(), rebuilt_artifacts.digest())


class TestT3_5_ExportAndRedaction(unittest.TestCase):
    """T3.5: Line-delimited JSON export with redaction, correlation preserved."""

    def test_jsonl_export_with_redaction(self) -> None:
        events = [
            _make_envelope(
                "0", "EpisodeStarted", {"taskSpec": {"name": "export_test"}},
                confidentiality="public",
                event_id="018f9999-1111-7000-8000-000000000001",
            ),
            _make_envelope(
                "1", "ObservationProduced", {"contentDigest": "sha256:" + "0" * 64, "secret": "topsecret123"},
                confidentiality="restricted",
                event_id="018f9999-1111-7000-8000-000000000002",
            ),
        ]

        buffer = io.StringIO()
        count = export_jsonl(events, buffer, redact=True)
        self.assertEqual(count, 2)

        buffer.seek(0)
        imported = import_jsonl(buffer)
        self.assertEqual(len(imported), 2)

        # Public event unredacted
        self.assertEqual(imported[0].confidentiality, "public")
        self.assertEqual(imported[0].redaction_status, "none")
        self.assertEqual(imported[0].payload["taskSpec"]["name"], "export_test")

        # Restricted event redacted, but correlation preserved (CT-42 / CT-16)
        self.assertEqual(imported[1].confidentiality, "restricted")
        self.assertEqual(imported[1].redaction_status, "complete")
        self.assertEqual(imported[1].seq, "1")
        self.assertEqual(imported[1].trace_id, "trace-xyz")
        self.assertEqual(imported[1].span_id, "span-123")
        self.assertEqual(imported[1].principal, "agent-alpha")
        self.assertEqual(imported[1].tenant_id, "tenant-corp")
        self.assertEqual(imported[1].payload["[redacted]"], True)
        self.assertNotIn("secret", imported[1].payload)


class TestT3_6_RecoveryScanner(unittest.TestCase):
    """T3.6: Run lease + heartbeat + recovery scanner outside the dying process."""

    def test_recovery_scanner_writes_terminal_event_from_outside(self) -> None:
        store = InMemoryEventStore()
        # Active episode with a heartbeat at 00:00:00
        e0 = _make_envelope("0", "EpisodeStarted", {"taskSpec": {}}, occurred_at="2026-08-15T00:00:00.000Z", event_id="018faaaa-1111-7000-8000-000000000001")
        e1 = _make_envelope("1", "Heartbeat", {"leaseId": "l-1", "seqNum": 1, "timestamp": "2026-08-15T00:00:00.000Z"}, occurred_at="2026-08-15T00:00:00.000Z", event_id="018faaaa-1111-7000-8000-000000000002")
        store.append([e0, e1])

        scanner = RecoveryScanner(controller_principal="external-recovery-scanner")

        # Current time within 5000ms lease: should not terminate
        rec_none = scanner.scan_and_recover_run(
            store=store,
            run_id="run-001",
            current_time_iso="2026-08-15T00:00:04.000Z",
            lease_timeout_ms=5000,
        )
        self.assertIsNone(rec_none)
        self.assertEqual(store.count("run-001"), 2)

        # Current time past 5000ms lease (10 seconds later): scanner intervenes
        rec = scanner.scan_and_recover_run(
            store=store,
            run_id="run-001",
            current_time_iso="2026-08-15T00:00:10.000Z",
            lease_timeout_ms=5000,
            action="recovered",
            reason="Corpse timed out",
        )
        self.assertIsNotNone(rec)
        self.assertEqual(rec.action, "recovered")
        self.assertEqual(rec.terminal_seq, "2")
        self.assertEqual(store.count("run-001"), 3)

        # Reconstruct state and verify terminal recovery event
        all_events = store.read(EventRange(run_id="run-001")).value
        state = reconstruct_state(all_events)
        self.assertEqual(state.episode.status, "recovered")
        self.assertEqual(state.episode.outcome, "recovered")
        self.assertIsNotNone(state.terminal_recovery)
        self.assertEqual(state.terminal_recovery["recoveredBy"], "external-recovery-scanner")


class TestT3_7_EffectReconciliation(unittest.TestCase):
    """T3.7: Effect reconciliation by idempotency key. Where occurrence cannot be determined, record says undeterminable and stays that way."""

    def test_reconciliation_undeterminable_invariant(self) -> None:
        # Inconclusive/undeterminable case
        verdict = EffectReconciler.reconcile(
            descriptor_digest="sha256:" + "e" * 64,
            idempotency_key="idemp-key-123",
            is_definitively_confirmed=False,
            uncertainty_reason="Process crashed while effect was in-flight",
        )
        self.assertEqual(verdict.status, "undeterminable")
        self.assertIsNotNone(verdict.uncertainty)
        self.assertEqual(verdict.uncertainty["scope"], "effect_occurrence")

        payload = EffectReconciler.build_reconciled_payload(verdict)
        self.assertEqual(payload["kind"], "EffectReconciled")
        self.assertEqual(payload["status"], "undeterminable")

        # Reduce into state and verify outcome stays undeterminable
        e0 = _make_envelope("0", "EpisodeStarted", {"taskSpec": {}}, event_id="018fbbbb-1111-7000-8000-000000000001")
        e1 = _make_envelope("1", "EffectStarted", {"descriptorDigest": "sha256:" + "e" * 64, "sinkClass": "privileged"}, event_id="018fbbbb-1111-7000-8000-000000000002")
        e2 = _make_envelope("2", "EffectReconciled", payload, event_id="018fbbbb-1111-7000-8000-000000000003")

        state = reconstruct_state([e0, e1, e2])
        effect_rec = state.effects["sha256:" + "e" * 64]
        self.assertEqual(effect_rec.status, "reconciled")
        self.assertEqual(effect_rec.outcome, "undeterminable")
        self.assertEqual(effect_rec.reconciliation_status, "undeterminable")

    def test_reconciliation_confirmed_case(self) -> None:
        verdict = EffectReconciler.reconcile(
            descriptor_digest="sha256:" + "f" * 64,
            idempotency_key="idemp-key-456",
            external_receipt_digest="sha256:" + "1" * 64,
            is_definitively_confirmed=True,
        )
        self.assertEqual(verdict.status, "confirmed")
        self.assertIsNone(verdict.uncertainty)
        payload = EffectReconciler.build_reconciled_payload(verdict)
        self.assertEqual(payload["status"], "confirmed")


class TestT3_8_CassetteRecorderAndPlayer(unittest.TestCase):
    """T3.8: Cassette recorder/player for the model port. Record writes; replay serves."""

    def test_cassette_record_and_byte_identical_playback(self) -> None:
        recorder = CassetteRecorder()
        context = {"system": "You are an agent", "history": ["User: hello"]}
        tools = [{"name": "read_file", "schema": {"type": "object"}}]
        sampling = {"temperature": 0.0, "maxTokens": 1000}
        proposal1 = {"text": "I will read the file", "toolCalls": [{"name": "read_file", "arguments": {"path": "a.txt"}}]}
        proposal2 = {"text": "Task finished", "toolCalls": []}

        recorder.record_interaction(context, tools, sampling, proposal1, recorded_at="2026-08-15T01:00:00.000Z")
        recorder.record_interaction(context, tools, sampling, proposal2, recorded_at="2026-08-15T01:01:00.000Z")

        # Serialize cassette to JSON
        cassette_json = recorder.cassette.to_json()
        loaded_cassette = Cassette.from_json(cassette_json)

        # Equal digests
        self.assertEqual(recorder.cassette.digest(), loaded_cassette.digest())

        # Playback via CassettePlayer
        player = CassettePlayer(loaded_cassette, match_mode="tape")
        p1 = player.propose(context, tools, sampling)
        self.assertTrue(p1.ok)
        self.assertEqual(p1.value, proposal1)

        p2 = player.propose(context, tools, sampling)
        self.assertTrue(p2.ok)
        self.assertEqual(p2.value, proposal2)

        # Cassette exhausted returns typed instrument error (CT-33)
        p3 = player.propose(context, tools, sampling)
        self.assertFalse(p3.ok)
        self.assertEqual(p3.error.kind, "instrument_error")


if __name__ == "__main__":
    unittest.main()
