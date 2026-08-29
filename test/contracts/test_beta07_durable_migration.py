"""BETA-07: durable database lifecycle -- fresh creation, schema migration,
corrupt/incompatible failure behavior, and interrupted-transaction recovery.

Owning contract: VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md BETA-07.

A durable product configuration must never silently drop into ephemeral
in-memory behavior, and a store that cannot be opened must say so with a
typed identity a caller can branch on -- never a raw `sqlite3` exception.
"""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.stores.event_store import (
    EventStoreCorruptError,
    EventStoreIncompatibleError,
    SqliteEventStore,
)
from vanguard.packages.domain.ledger.events import EventEnvelope, parse_event_envelope
from vanguard.packages.ports.event_store import EventRange


def _envelope(seq: int, run_id: str = "run-1") -> EventEnvelope:
    return parse_event_envelope({
        "schema_version": "mhf.event/1",
        "event_id": f"evt-{run_id}-{seq:04d}",
        "kind": "TestEvent",
        "seq": seq,
        "run_id": run_id,
        "episode_id": "ep-1",
        "project_id": "proj-1",
        "scope": "episode",
        "occurred_at": f"2026-08-28T00:00:{seq:02d}.000Z",
        "recorded_at": f"2026-08-28T00:00:{seq:02d}.100Z",
        "principal": "tester",
        "tenant_id": "t1",
        "owner_id": "o1",
        "confidentiality": "internal",
        "retention_class": "operational",
        "trainability": "unspecified",
        "redaction_status": "unredacted",
        "payload": {"n": seq},
        "prev_digest": "sha256:" + "0" * 64,
    })


class FreshDatabaseCreation(unittest.TestCase):
    def test_a_new_path_is_created_and_stamped_with_the_current_schema_version(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "events.sqlite3"
            self.assertFalse(path.exists())
            store = SqliteEventStore(path)
            self.assertTrue(path.exists())
            version = store._conn.execute("PRAGMA user_version;").fetchone()[0]
            self.assertEqual(version, SqliteEventStore._SCHEMA_VERSION)
            self.assertTrue(store.durable)


class SupportedSchemaMigration(unittest.TestCase):
    def test_a_store_created_before_versioning_existed_is_migrated_in_place(self) -> None:
        """Simulate a pre-BETA-07 store: table exists, `user_version` is 0."""
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "legacy.sqlite3"
            conn = sqlite3.connect(str(path))
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("""
                CREATE TABLE events (
                    global_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    seq INTEGER NOT NULL,
                    seq_str TEXT NOT NULL,
                    run_id TEXT,
                    episode_id TEXT,
                    scope TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    recorded_at TEXT NOT NULL,
                    principal TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    owner_id TEXT NOT NULL,
                    confidentiality TEXT NOT NULL,
                    retention_class TEXT NOT NULL,
                    trainability TEXT NOT NULL,
                    redaction_status TEXT NOT NULL,
                    envelope_json TEXT NOT NULL,
                    envelope_digest TEXT NOT NULL
                );
                """)
            conn.commit()
            conn.close()

            store = SqliteEventStore(path)
            columns = {row[1] for row in store._conn.execute("PRAGMA table_info(events);").fetchall()}
            self.assertIn("project_id", columns)
            version = store._conn.execute("PRAGMA user_version;").fetchone()[0]
            self.assertEqual(version, SqliteEventStore._SCHEMA_VERSION)

            result = store.append([_envelope(1)])
            self.assertTrue(result.ok, result.error)

    def test_reopening_an_already_migrated_store_does_not_error_or_reapply(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "events.sqlite3"
            SqliteEventStore(path).append([_envelope(1)])
            store2 = SqliteEventStore(path)
            events = store2.read(EventRange(run_id="run-1"))
            self.assertTrue(events.ok)
            self.assertEqual(len(events.value), 1)


class CorruptDatabaseFailsClosed(unittest.TestCase):
    def test_a_non_sqlite_file_raises_a_typed_corruption_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "garbage.sqlite3"
            path.write_bytes(b"not a sqlite database, just noise 0123456789")
            with self.assertRaises(EventStoreCorruptError):
                SqliteEventStore(path)

    def test_a_truncated_file_is_caught_by_open_or_by_integrity_check(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "truncated.sqlite3"
            store = SqliteEventStore(path)
            store.append([_envelope(1)])
            store.close()
            for sidecar in (Path(str(path) + "-wal"), Path(str(path) + "-shm")):
                sidecar.unlink(missing_ok=True)
            # Chop the file to less than SQLite's 100-byte header: no valid
            # page can be described, so the file is unreadable rather than
            # merely missing recent writes.
            path.write_bytes(path.read_bytes()[:50])
            try:
                store = SqliteEventStore(path)
            except EventStoreCorruptError:
                return  # caught at open -- the strongest possible answer
            # Some truncations still open (SQLite defers page validation);
            # the store's own integrity_check must not report them healthy.
            result = store.integrity_check()
            healthy = result.ok and bool(result.value.get("ok"))
            self.assertFalse(healthy, "a truncated database must not be reported as intact")


class IncompatibleSchemaFailsClosed(unittest.TestCase):
    def test_a_newer_schema_version_is_refused_not_reinterpreted(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "future.sqlite3"
            SqliteEventStore(path)
            conn = sqlite3.connect(str(path))
            conn.execute(f"PRAGMA user_version = {SqliteEventStore._SCHEMA_VERSION + 1};")
            conn.commit()
            conn.close()
            with self.assertRaises(EventStoreIncompatibleError):
                SqliteEventStore(path)


class InterruptedTransactionRecovery(unittest.TestCase):
    def test_a_transaction_never_committed_leaves_no_partial_row_after_reopen(self) -> None:
        """WAL mode: a writer that dies mid-`BEGIN IMMEDIATE` leaves the
        journal uncommitted. A fresh connection to the same file must see
        only the fully-committed prefix, never a half-applied batch."""
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "events.sqlite3"
            store = SqliteEventStore(path)
            self.assertTrue(store.append([_envelope(1)]).ok)

            # Simulate a writer that started a transaction and never
            # committed (process killed between BEGIN and COMMIT) by opening
            # a second raw connection, starting a write, and closing without
            # committing or rolling back.
            raw = sqlite3.connect(str(path), isolation_level=None)
            raw.execute("BEGIN IMMEDIATE;")
            raw.execute(
                "INSERT INTO events (event_id, seq, seq_str, run_id, episode_id, project_id, "
                "scope, occurred_at, recorded_at, principal, tenant_id, owner_id, confidentiality, "
                "retention_class, trainability, redaction_status, envelope_json, envelope_digest) "
                "VALUES ('evt-orphan', 2, '2', 'run-1', 'ep-1', 'proj-1', 'episode', "
                "'2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z', 'tester', 't1', 'o1', "
                "'internal', 'standard', 'excluded', 'none', '{}', 'sha256:0');"
            )
            raw.close()  # no COMMIT: SQLite rolls the incomplete transaction back

            reopened = SqliteEventStore(path)
            events = reopened.read(EventRange(run_id="run-1"))
            self.assertTrue(events.ok)
            self.assertEqual(len(events.value), 1, "the uncommitted insert must not be visible")
            self.assertEqual(events.value[0].event_id, "evt-run-1-0001")

            # And the store remains fully writable afterward.
            result = reopened.append([_envelope(2)])
            self.assertTrue(result.ok, result.error)
            events2 = reopened.read(EventRange(run_id="run-1"))
            self.assertEqual(len(events2.value), 2)


if __name__ == "__main__":
    unittest.main()
