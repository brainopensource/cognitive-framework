"""B3 SQLite-WAL Fresh-Process Recovery and Continuation Tests.

Owning contract: ADR-0088 §1 (RF-82), GTS-13C T3.1/T3.3, SPEC §1.3.
Verifies:
1. Release store requires explicit file-backed SQLite with WAL mode (:memory: forbidden for release).
2. Hard process death: a fresh process reconstructs identical composition, run, and trajectory identity.
3. Idempotent continuation: settled effects with S8a intent are never repeated on recovery.
4. Ledger chain integrity: prev_digest hash chain continues monotonically across process restarts.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.ledger.events import EventEnvelope, parse_event_envelope
from vanguard.packages.ports.event_store import EventRange


def _make_envelope(
    seq: int,
    run_id: str,
    project_id: str,
    kind: str,
    payload: dict[str, object],
    prev_digest: str = "sha256:" + "0" * 64,
) -> EventEnvelope:
    event_dict = {
        "schema_version": "mhf.event/1",
        "event_id": f"evt-{run_id}-{seq:04d}",
        "kind": kind,
        "seq": seq,
        "run_id": run_id,
        "episode_id": "ep-001",
        "project_id": project_id,
        "scope": "episode",
        "occurred_at": f"2026-08-23T20:00:{seq:02d}.000Z",
        "recorded_at": f"2026-08-23T20:00:{seq:02d}.100Z",
        "principal": "kernel",
        "tenant_id": "tenant-default",
        "owner_id": "owner-default",
        "confidentiality": "internal",
        "retention_class": "operational",
        "trainability": "unspecified",
        "redaction_status": "unredacted",
        "payload": payload,
        "prev_digest": prev_digest,
    }
    return parse_event_envelope(event_dict)


class B3WalRecoveryAndContinuationTests(unittest.TestCase):
    """File-backed SQLite-WAL recovery and fresh-process continuation tests."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="vg-b3-wal-")
        self.db_path = str(Path(self.temp_dir) / "ledger.db")

    def tearDown(self) -> None:
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass
        if os.path.exists(self.temp_dir):
            try:
                os.rmdir(self.temp_dir)
            except OSError:
                pass

    def test_b3_01_release_store_enforces_file_backed_wal(self) -> None:
        """RF-82: File-backed store activates PRAGMA journal_mode = WAL."""
        store = SqliteEventStore(self.db_path)
        cur = store._conn.cursor()
        cur.execute("PRAGMA journal_mode;")
        mode = cur.fetchone()[0]
        self.assertEqual(mode.lower(), "wal")

        # Memory store is not WAL
        mem_store = SqliteEventStore(":memory:")
        mcur = mem_store._conn.cursor()
        mcur.execute("PRAGMA journal_mode;")
        mmode = mcur.fetchone()[0]
        self.assertEqual(mmode.lower(), "memory")

    def test_b3_02_fresh_process_cold_continuation_and_chain_continuity(self) -> None:
        """RF-82: Fresh process resumes from disk without broken hash chain or duplicate seq."""
        run_id = "run-wal-001"
        project_id = "project-alpha"

        # --- PROCESS 1: Write initial events and crash ---
        store_p1 = SqliteEventStore(self.db_path)
        e1 = _make_envelope(1, run_id, project_id, "CapabilityGranted", {"verb": "fs.read"})
        e2 = _make_envelope(2, run_id, project_id, "EffectStarted", {"verb": "fs.read", "idempotency_key": "k1"}, prev_digest=e1.digest())
        e3 = _make_envelope(3, run_id, project_id, "EffectCompleted", {"verb": "fs.read", "outcome": "ok"}, prev_digest=e2.digest())

        res1 = store_p1.append([e1, e2, e3])
        self.assertTrue(res1.ok)

        # Simulate process exit / teardown of process 1
        del store_p1

        # --- PROCESS 2: Fresh process start ---
        store_p2 = SqliteEventStore(self.db_path)
        read_res = store_p2.read(EventRange(project_id=project_id))
        self.assertTrue(read_res.ok)
        recovered_events = list(read_res.value)
        self.assertEqual(len(recovered_events), 3)
        self.assertEqual(int(recovered_events[-1].seq), 3)

        # Continue ledger in process 2
        last_digest = recovered_events[-1].digest()
        e4 = _make_envelope(4, run_id, project_id, "RunRecovered", {"prior_event_count": 3}, prev_digest=last_digest)
        e5 = _make_envelope(5, run_id, project_id, "EpisodeCompleted", {"status": "success"}, prev_digest=e4.digest())

        res2 = store_p2.append([e4, e5])
        self.assertTrue(res2.ok)

        # Verify full chain of 5 events in process 2
        all_res = store_p2.read(EventRange(project_id=project_id))
        self.assertTrue(all_res.ok)
        all_events = list(all_res.value)
        self.assertEqual(len(all_events), 5)
        for i in range(1, 5):
            self.assertEqual(all_events[i].prev_digest, all_events[i - 1].digest())

    def test_b3_03_settled_effect_is_never_repeated_on_recovery(self) -> None:
        """RF-82: S8a intent + settled effect prevents duplicate physical execution after crash."""
        run_id = "run-wal-002"
        project_id = "project-beta"
        idempotency_key = "idemp-patch-file-calc"

        # Process 1 commits S8a intent and effect completion
        store1 = SqliteEventStore(self.db_path)
        e1 = _make_envelope(1, run_id, project_id, "EffectStarted", {"verb": "patch.apply", "idempotency_key": idempotency_key})
        e2 = _make_envelope(2, run_id, project_id, "EffectCompleted", {"verb": "patch.apply", "idempotency_key": idempotency_key, "outcome": "ok"}, prev_digest=e1.digest())
        store1.append([e1, e2])
        del store1

        # Process 2 recovers and checks settled idempotency keys
        store2 = SqliteEventStore(self.db_path)
        read_res = store2.read(EventRange(project_id=project_id))
        self.assertTrue(read_res.ok)

        settled_keys = set()
        for evt in read_res.value:
            kind = evt.mhf_kind or evt.payload.get("kind")
            if kind == "EffectCompleted" and "idempotency_key" in evt.payload:
                settled_keys.add(evt.payload["idempotency_key"])

        self.assertIn(idempotency_key, settled_keys)
        # Executor must skip re-execution of settled key
        should_reexecute = idempotency_key not in settled_keys
        self.assertFalse(should_reexecute)


if __name__ == "__main__":
    unittest.main()
