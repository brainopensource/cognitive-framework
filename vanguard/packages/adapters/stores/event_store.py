"""Append-only, transactional EventStore implementations.

Owning contract: VG-04 §12.3 / `CT-40`..`CT-43`, GTS-13C T3.1 / T3.3, ICD §4.

Invariants:
- Single writer, monotonic sequence enforcement (`seq`).
- Transactional append: batches commit atomically or rollback completely on failure.
- Crash safe: WAL mode for SQLite with sync; state reconstructible from disk.
- Digest calculation: deterministic sha256 cumulative digest of canonical events.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Optional, Sequence, Union

from ...domain.canonicalisation.digest import digest_of
from ...domain.ledger.events import EventEnvelope, parse_event_envelope
from ...ports.event_store import EventRange, EventStorePort, PortFailure, Result

__all__ = [
    "InMemoryEventStore",
    "SqliteEventStore",
]


class InMemoryEventStore(EventStorePort):
    """Deterministic in-memory transactional EventStore for fakes, tests, and pure replay."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._events: list[EventEnvelope] = []
        self._by_run: dict[str, list[EventEnvelope]] = {}

    def append(self, events: Sequence[EventEnvelope]) -> Result[None]:
        """Atomically append an ordered sequence of event envelopes."""
        if not events:
            return Result.success(None)

        with self._lock:
            # Validate monotonicity and integrity across all incoming events before committing any
            last_global_seq = int(self._events[-1].seq) if self._events else -1
            run_last_seqs: dict[str, int] = {}
            for r_id, r_events in self._by_run.items():
                if r_events:
                    run_last_seqs[r_id] = int(r_events[-1].seq)

            # Check incoming batch for internal and external monotonicity
            current_batch_run_seqs = dict(run_last_seqs)
            for idx, event in enumerate(events):
                seq_int = int(event.seq)
                r_id = event.run_id or "__global__"
                prior_seq = current_batch_run_seqs.get(r_id, -1)
                if seq_int <= prior_seq:
                    return Result.fail(
                        kind="conflict",
                        message=(
                            f"Non-monotonic sequence in run {r_id!r}: event {event.event_id} has "
                            f"seq {event.seq} ({seq_int}) <= prior seq {prior_seq}"
                        ),
                    )
                current_batch_run_seqs[r_id] = seq_int

            # All validated: atomic commit
            for event in events:
                self._events.append(event)
                r_id = event.run_id or "__global__"
                if r_id not in self._by_run:
                    self._by_run[r_id] = []
                self._by_run[r_id].append(event)

            return Result.success(None)

    def read(self, range_query: Optional[EventRange] = None) -> Result[Sequence[EventEnvelope]]:
        """Read ordered sequence of event envelopes matching range query."""
        with self._lock:
            if range_query is None:
                return Result.success(list(self._events))

            source = self._events
            if range_query.run_id is not None:
                source = self._by_run.get(range_query.run_id, [])

            filtered: list[EventEnvelope] = []
            after_seq_int = int(range_query.after_seq) if range_query.after_seq is not None else -1

            for event in source:
                if range_query.run_id is not None and event.run_id != range_query.run_id:
                    continue
                if range_query.episode_id is not None and event.episode_id != range_query.episode_id:
                    continue
                if range_query.scope is not None and event.scope != range_query.scope:
                    continue
                if int(event.seq) <= after_seq_int:
                    continue

                filtered.append(event)
                if range_query.limit is not None and len(filtered) >= range_query.limit:
                    break

            return Result.success(filtered)

    def digest(self, run_id: Optional[str] = None) -> Result[str]:
        """Compute the cumulative sha256 digest of stored events."""
        with self._lock:
            source = self._by_run.get(run_id, []) if run_id is not None else self._events
            canonical_dicts = [e.to_dict() for e in source]
            return Result.success(digest_of(canonical_dicts))

    def count(self, run_id: Optional[str] = None) -> int:
        """Return the number of stored events."""
        with self._lock:
            if run_id is not None:
                return len(self._by_run.get(run_id, []))
            return len(self._events)


class SqliteEventStore(EventStorePort):
    """Embedded transactional EventStore with Write-Ahead Logging (WAL) and crash safety (CT-40)."""

    def __init__(self, db_path: Union[str, Path] = ":memory:", synchronous: str = "FULL") -> None:
        self.db_path = str(db_path)
        self._synchronous = synchronous
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            isolation_level=None,  # Manual transaction management
        )
        self._init_db()

    def _init_db(self) -> None:
        with self._lock:
            cur = self._conn.cursor()
            if self.db_path != ":memory:":
                cur.execute("PRAGMA journal_mode = WAL;")
            cur.execute(f"PRAGMA synchronous = {self._synchronous};")
            cur.execute("PRAGMA foreign_keys = ON;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
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
            cur.execute("CREATE INDEX IF NOT EXISTS idx_events_run_seq ON events(run_id, seq);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_events_scope ON events(scope);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_events_episode ON events(episode_id);")

    def append(self, events: Sequence[EventEnvelope]) -> Result[None]:
        """Atomically append an ordered sequence of event envelopes within a transaction."""
        if not events:
            return Result.success(None)

        with self._lock:
            cur = self._conn.cursor()
            try:
                cur.execute("BEGIN IMMEDIATE;")

                for event in events:
                    seq_int = int(event.seq)
                    r_id = event.run_id or "__global__"

                    # Verify sequence monotonicity within the run in the database
                    cur.execute(
                        "SELECT seq FROM events WHERE (run_id = ? OR (run_id IS NULL AND ? = '__global__')) ORDER BY seq DESC LIMIT 1;",
                        (event.run_id, r_id),
                    )
                    row = cur.fetchone()
                    if row is not None and seq_int <= row[0]:
                        cur.execute("ROLLBACK;")
                        return Result.fail(
                            kind="conflict",
                            message=(
                                f"Non-monotonic sequence in run {event.run_id!r}: event {event.event_id} has "
                                f"seq {event.seq} ({seq_int}) <= prior seq {row[0]}"
                            ),
                        )

                    envelope_dict = event.to_dict()
                    envelope_json = json.dumps(envelope_dict, separators=(",", ":"), ensure_ascii=False)
                    envelope_digest = event.digest()

                    cur.execute(
                        """
                        INSERT INTO events (
                            event_id, seq, seq_str, run_id, episode_id, scope,
                            occurred_at, recorded_at, principal, tenant_id, owner_id,
                            confidentiality, retention_class, trainability, redaction_status,
                            envelope_json, envelope_digest
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            event.event_id,
                            seq_int,
                            event.seq,
                            event.run_id,
                            event.episode_id,
                            event.scope,
                            event.occurred_at,
                            event.recorded_at,
                            event.principal,
                            event.tenant_id,
                            event.owner_id,
                            event.confidentiality,
                            event.retention_class,
                            event.trainability,
                            event.redaction_status,
                            envelope_json,
                            envelope_digest,
                        ),
                    )

                cur.execute("COMMIT;")
                return Result.success(None)

            except sqlite3.IntegrityError as exc:
                cur.execute("ROLLBACK;")
                return Result.fail(kind="conflict", message=f"Database integrity error: {exc}")
            except Exception as exc:
                cur.execute("ROLLBACK;")
                return Result.fail(kind="instrument_error", message=f"Storage error during append: {exc}")

    def read(self, range_query: Optional[EventRange] = None) -> Result[Sequence[EventEnvelope]]:
        """Read ordered sequence of event envelopes from database."""
        with self._lock:
            cur = self._conn.cursor()
            query = "SELECT envelope_json FROM events WHERE 1=1"
            params: list[Any] = []

            if range_query is not None:
                if range_query.run_id is not None:
                    query += " AND run_id = ?"
                    params.append(range_query.run_id)
                if range_query.episode_id is not None:
                    query += " AND episode_id = ?"
                    params.append(range_query.episode_id)
                if range_query.scope is not None:
                    query += " AND scope = ?"
                    params.append(range_query.scope)
                if range_query.after_seq is not None:
                    query += " AND seq > ?"
                    params.append(int(range_query.after_seq))

            query += " ORDER BY global_id ASC"

            if range_query is not None and range_query.limit is not None:
                query += " LIMIT ?"
                params.append(range_query.limit)

            try:
                cur.execute(query, params)
                rows = cur.fetchall()
                envelopes = [parse_event_envelope(json.loads(row[0])) for row in rows]
                return Result.success(envelopes)
            except Exception as exc:
                return Result.fail(kind="instrument_error", message=f"Storage read error: {exc}")

    def digest(self, run_id: Optional[str] = None) -> Result[str]:
        """Compute the cumulative sha256 digest of stored events."""
        with self._lock:
            cur = self._conn.cursor()
            if run_id is not None:
                cur.execute("SELECT envelope_json FROM events WHERE run_id = ? ORDER BY global_id ASC;", (run_id,))
            else:
                cur.execute("SELECT envelope_json FROM events ORDER BY global_id ASC;")
            rows = cur.fetchall()
            canonical_dicts = [json.loads(row[0]) for row in rows]
            return Result.success(digest_of(canonical_dicts))

    def count(self, run_id: Optional[str] = None) -> int:
        """Return the count of stored events."""
        with self._lock:
            cur = self._conn.cursor()
            if run_id is not None:
                cur.execute("SELECT COUNT(*) FROM events WHERE run_id = ?;", (run_id,))
            else:
                cur.execute("SELECT COUNT(*) FROM events;")
            return int(cur.fetchone()[0])

    def close(self) -> None:
        """Close SQLite connection."""
        with self._lock:
            self._conn.close()
