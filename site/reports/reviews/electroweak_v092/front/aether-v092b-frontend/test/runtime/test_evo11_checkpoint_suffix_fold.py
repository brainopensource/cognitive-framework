"""Contract test for EVO-11: Checkpoint Delta Suffix Decoding (Lazy Replay).

Owning contract: EVO-11, GTS-13C Ch.11, ADR-0098 Decision 6.
Invariants:
- Checkpointed restoration queries strictly delta events with seq > checkpoint.last_seq.
- Lazy suffix replay yields identical state digest to full cold fold.
- Corrupted/tampered checkpoints fail closed to cold fold from seq=0 without data loss.
"""

from __future__ import annotations

import json
import unittest

from vanguard.packages.adapters.stores.blob_store import InMemoryBlobStore
from vanguard.packages.adapters.stores.event_store import InMemoryEventStore
from vanguard.packages.domain.ledger.events import EventEnvelope
from vanguard.packages.domain.ledger.reducer import initial_state, reduce_batch
from vanguard.packages.runtime.checkpoints import CheckpointManager


def _make_event(run_id: str, seq: int, kind: str = "TurnCompleted", **kwargs) -> EventEnvelope:
    payload = {"kind": kind, "action": "fs.read", "note": f"event_{seq}", **kwargs}
    return EventEnvelope(
        schema_version="mhf.event/2",
        event_id=f"0192f0a0-0000-7000-8000-{seq:012d}",
        scope="episode",
        seq=str(seq),
        occurred_at="2026-08-28T12:00:00.000Z",
        recorded_at="2026-08-28T12:00:00.000Z",
        principal="test-operator",
        principal_role="episode",
        tenant_id="tenant-default",
        owner_id="owner-platform",
        confidentiality="internal",
        retention_class="extended",
        trainability="prohibited",
        redaction_status="none",
        payload=payload,
        run_id=run_id,
        episode_id=f"ep-{run_id}",
    )


class TestEvo11CheckpointSuffixFold(unittest.TestCase):
    def setUp(self) -> None:
        self.blobs = InMemoryBlobStore()
        self.event_store = InMemoryEventStore()
        self.manager = CheckpointManager(blobs=self.blobs)
        self.run_id = "run-evo11-001"

    def test_lazy_delta_replay_queries_only_k_events(self) -> None:
        """Prove that restore_latest queries only delta suffix (K events) instead of N total events."""
        # Append 100 events
        total_events = 100
        checkpoint_at_seq = 80

        events = [_make_event(self.run_id, i) for i in range(1, total_events + 1)]
        self.event_store.append(events)

        # Fold up to checkpoint_at_seq and capture checkpoint
        prefix_state = reduce_batch(initial_state(), events[:checkpoint_at_seq])
        checkpoint = self.manager.capture(prefix_state)
        self.assertIsNotNone(checkpoint)
        self.assertEqual(checkpoint.last_seq, checkpoint_at_seq)

        # Restore latest with checkpoint
        restored_state, replayed_count = self.manager.restore_latest(
            run_id=self.run_id,
            event_store=self.event_store,
            checkpoint=checkpoint,
            verify=False,
        )

        # Verify only 20 delta events were replayed (K = 20 instead of N = 100)
        expected_delta_count = total_events - checkpoint_at_seq
        self.assertEqual(replayed_count, expected_delta_count)

        # Verify state parity against full cold fold
        full_cold_state = reduce_batch(initial_state(), events)
        self.assertIsNotNone(restored_state)
        self.assertEqual(restored_state.digest(), full_cold_state.digest())
        self.assertEqual(restored_state.event_count, total_events)

    def test_corrupted_checkpoint_fails_closed_to_full_cold_fold(self) -> None:
        """Prove that corrupted/truncated checkpoint triggers cold-fold fallback from seq=0."""
        total_events = 50
        checkpoint_at_seq = 30

        events = [_make_event(self.run_id, i) for i in range(1, total_events + 1)]
        self.event_store.append(events)

        prefix_state = reduce_batch(initial_state(), events[:checkpoint_at_seq])
        checkpoint = self.manager.capture(prefix_state)
        self.assertIsNotNone(checkpoint)

        # Corrupt the blob payload in blob store
        bad_bytes = b'{"schemaVersion": "mhf.checkpoint/1", "state": {"corrupted": true}}'
        self.blobs.put(bad_bytes)  # Puts under its own digest
        # Overwrite the blob at the pinned digest with corrupt data
        self.blobs._blobs[checkpoint.blob_digest] = bad_bytes

        # Attempt restore - should fail closed to cold-fold and read all 50 events
        restored_state, replayed_count = self.manager.restore_latest(
            run_id=self.run_id,
            event_store=self.event_store,
            checkpoint=checkpoint,
        )

        self.assertEqual(replayed_count, total_events)
        full_cold_state = reduce_batch(initial_state(), events)
        self.assertIsNotNone(restored_state)
        self.assertEqual(restored_state.digest(), full_cold_state.digest())


if __name__ == "__main__":
    unittest.main()
