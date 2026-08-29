"""EVO-10: `SqliteEventStore.append` issues at most one seq lookup per
distinct run/project key per batch, not one per event.

Owning contract: VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md EVO-10.

Preserves monotonicity, atomicity, uniqueness, crash recovery, and
concurrent-writer correctness exactly as before -- `BEGIN IMMEDIATE`
already takes the write lock before the first lookup, so no concurrent
writer can move a key's last-committed seq during the transaction, which is
what makes caching it in-memory for the rest of the batch safe.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.ledger.events import parse_event_envelope
from vanguard.packages.ports.event_store import EventRange


def _envelope(seq: int, run_id: str = "run-1", project_id: str | None = None):
    body = {
        "schema_version": "mhf.event/1",
        "event_id": f"evt-{run_id}-{project_id}-{seq:04d}",
        "kind": "TestEvent",
        "seq": seq,
        "run_id": run_id,
        "episode_id": "ep-1",
        "scope": "episode",
        "occurred_at": f"2026-08-29T00:00:{seq % 60:02d}.000Z",
        "recorded_at": f"2026-08-29T00:00:{seq % 60:02d}.100Z",
        "principal": "tester",
        "tenant_id": "t1",
        "owner_id": "o1",
        "confidentiality": "internal",
        "retention_class": "operational",
        "trainability": "unspecified",
        "redaction_status": "unredacted",
        "payload": {"n": seq},
        "prev_digest": "sha256:" + "0" * 64,
    }
    if project_id is not None:
        body["project_id"] = project_id
    return parse_event_envelope(body)


class QueryCountIsBoundedByDistinctKeysNotEventCount(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "events.sqlite3"
        self.store = SqliteEventStore(self.path)
        self.selects: list[str] = []
        self.store._conn.set_trace_callback(
            lambda sql: self.selects.append(sql) if sql.strip().upper().startswith("SELECT") else None
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_one_run_many_events_costs_at_most_one_seq_lookup(self) -> None:
        batch = [_envelope(i, run_id="run-x") for i in range(1, 51)]
        self.selects.clear()
        result = self.store.append(batch)
        self.assertTrue(result.ok, result.error)
        seq_lookups = [s for s in self.selects if "ORDER BY seq DESC" in s]
        self.assertLessEqual(
            len(seq_lookups), 1,
            f"50 events for one run should cost at most 1 seq lookup, got {len(seq_lookups)}: {seq_lookups}",
        )

    def test_events_split_across_two_projects_costs_at_most_two_seq_lookups(self) -> None:
        batch = [_envelope(i, run_id="run-x", project_id="proj-a" if i % 2 else "proj-b")
                for i in range(1, 41)]
        self.selects.clear()
        result = self.store.append(batch)
        self.assertTrue(result.ok, result.error)
        seq_lookups = [s for s in self.selects if "ORDER BY seq DESC" in s]
        self.assertLessEqual(len(seq_lookups), 2)

    def test_a_second_append_call_still_sees_the_first_calls_committed_seq(self) -> None:
        """The in-memory cache is per-`append()`-call only -- it must never
        let a later call believe an earlier call's writes didn't happen."""
        first = self.store.append([_envelope(1, run_id="run-y"), _envelope(2, run_id="run-y")])
        self.assertTrue(first.ok, first.error)
        # A conflicting seq (<=2) in a fresh append() call must still be
        # rejected using the true on-disk state, not a stale empty cache.
        conflict = self.store.append([_envelope(2, run_id="run-y")])
        self.assertFalse(conflict.ok)
        self.assertEqual(conflict.error.kind, "conflict")
        ok = self.store.append([_envelope(3, run_id="run-y")])
        self.assertTrue(ok.ok, ok.error)


class MonotonicityIsStillEnforcedWithinAndAcrossBatches(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "events.sqlite3"
        self.store = SqliteEventStore(self.path)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_a_non_monotonic_event_mid_batch_rolls_back_the_whole_batch(self) -> None:
        batch = [_envelope(1, run_id="run-z"), _envelope(2, run_id="run-z"),
                 _envelope(1, run_id="run-z")]  # seq 1 again -- violates monotonicity
        result = self.store.append(batch)
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "conflict")
        # Rolled back entirely: none of the batch's events are visible.
        read = self.store.read(EventRange(run_id="run-z"))
        self.assertEqual(len(read.value), 0)

    def test_project_scoped_monotonicity_is_independent_of_run_scoped(self) -> None:
        result = self.store.append([
            _envelope(1, run_id="run-a", project_id="proj-shared"),
            _envelope(2, run_id="run-b", project_id="proj-shared"),
        ])
        self.assertTrue(result.ok, result.error)
        # Same project, lower seq than the project's last -- rejected even
        # though it is a different run_id.
        conflict = self.store.append([_envelope(1, run_id="run-c", project_id="proj-shared")])
        self.assertFalse(conflict.ok)

    def test_two_unrelated_runs_do_not_share_a_seq_space(self) -> None:
        result = self.store.append([
            _envelope(5, run_id="run-alpha"),
            _envelope(1, run_id="run-beta"),  # lower seq, but a different run -- fine
        ])
        self.assertTrue(result.ok, result.error)


if __name__ == "__main__":
    unittest.main()
