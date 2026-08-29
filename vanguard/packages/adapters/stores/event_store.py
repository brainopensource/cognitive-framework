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
import os
import sqlite3
import tempfile
import threading
from pathlib import Path
from typing import Any, Optional, Sequence, Union

from ...domain.canonicalisation.digest import digest_of
from ...domain.ledger.events import EventEnvelope, parse_event_envelope
from ...ports.event_store import EventRange, EventStorePort, PortFailure, Result

__all__ = [
    "InMemoryEventStore",
    "SqliteEventStore",
    "EventStoreCorruptError",
    "EventStoreIncompatibleError",
]


class EventStoreCorruptError(RuntimeError):
    """The database file exists but is not a readable SQLite database (BETA-07).

    Raised instead of letting a raw `sqlite3.DatabaseError` escape the
    constructor: a corrupt store is a fail-closed condition the caller must
    handle explicitly (e.g. refuse to start, or offer cold-fold recovery from
    the ledger elsewhere), never a crash with no typed identity.
    """


class EventStoreIncompatibleError(RuntimeError):
    """The database's schema is newer than this build understands (BETA-07).

    `user_version` ahead of `_SCHEMA_VERSION` means a later Vanguard build
    wrote this store. There is no destructive implicit downgrade: opening it
    with an older build fails closed rather than silently reinterpreting
    unknown columns.
    """


class InMemoryEventStore(EventStorePort):
    """Deterministic in-memory transactional EventStore for fakes, tests, and pure replay."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._events: list[EventEnvelope] = []
        self._by_run: dict[str, list[EventEnvelope]] = {}
        self._by_project: dict[str, list[EventEnvelope]] = {}

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
            project_last_seqs: dict[str, int] = {}
            for p_id, p_events in self._by_project.items():
                if p_events:
                    project_last_seqs[p_id] = int(p_events[-1].seq)

            current_batch_run_seqs = dict(run_last_seqs)
            current_batch_project_seqs = dict(project_last_seqs)
            for idx, event in enumerate(events):
                seq_int = int(event.seq)
                if event.project_id:
                    prior_seq = current_batch_project_seqs.get(event.project_id, -1)
                    if seq_int <= prior_seq:
                        return Result.fail(
                            kind="conflict",
                            message=(
                                f"Non-monotonic sequence in project {event.project_id!r}: "
                                f"event {event.event_id} has seq {event.seq} ({seq_int}) "
                                f"<= prior seq {prior_seq}"
                            ),
                        )
                    current_batch_project_seqs[event.project_id] = seq_int
                else:
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
                if event.project_id:
                    self._by_project.setdefault(event.project_id, []).append(event)

            return Result.success(None)

    def read(self, range_query: Optional[EventRange] = None) -> Result[Sequence[EventEnvelope]]:
        """Read ordered sequence of event envelopes matching range query."""
        with self._lock:
            if range_query is None:
                return Result.success(list(self._events))

            source = self._events
            if range_query.run_id is not None:
                source = self._by_run.get(range_query.run_id, [])
            if range_query.project_id is not None:
                source = self._by_project.get(range_query.project_id, [])

            filtered: list[EventEnvelope] = []
            after_seq_int = int(range_query.after_seq) if range_query.after_seq is not None else -1

            for event in source:
                if range_query.run_id is not None and event.run_id != range_query.run_id:
                    continue
                if range_query.project_id is not None and event.project_id != range_query.project_id:
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

    #: Bumped whenever `_MIGRATIONS` gains a step. Stored in `PRAGMA user_version`
    #: so a fresh open can tell "never initialized" (0), "needs N more steps"
    #: (0 < version < current), and "written by a newer build" (version > current)
    #: apart, without inferring any of that from column presence.
    _SCHEMA_VERSION = 1

    def __init__(self, db_path: Union[str, Path] = ":memory:", synchronous: str = "FULL") -> None:
        self.db_path = str(db_path)
        self._synchronous = synchronous
        self._lock = threading.RLock()
        try:
            self._conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                isolation_level=None,  # Manual transaction management
            )
            self._init_db()
        except sqlite3.DatabaseError as exc:
            # Covers "file is not a database" and header/page corruption alike:
            # sqlite3 raises the same exception class for both, and neither is
            # a state this constructor can repair.
            raise EventStoreCorruptError(
                f"{self.db_path!r} is not a readable SQLite database: {exc}"
            ) from exc

    def _init_db(self) -> None:
        with self._lock:
            cur = self._conn.cursor()
            if self.db_path != ":memory:":
                cur.execute("PRAGMA journal_mode = WAL;")
            cur.execute(f"PRAGMA synchronous = {self._synchronous};")
            cur.execute("PRAGMA foreign_keys = ON;")

            version = int(cur.execute("PRAGMA user_version;").fetchone()[0])
            if version > self._SCHEMA_VERSION:
                raise EventStoreIncompatibleError(
                    f"{self.db_path!r} has schema version {version}, newer than the "
                    f"{self._SCHEMA_VERSION} this build understands; refusing to open it"
                )
            for step in self._MIGRATIONS[version:]:
                step(cur)
            cur.execute(f"PRAGMA user_version = {self._SCHEMA_VERSION};")

    @staticmethod
    def _migration_0_initial_schema(cur: sqlite3.Cursor) -> None:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
                global_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                seq INTEGER NOT NULL,
                seq_str TEXT NOT NULL,
                run_id TEXT,
                episode_id TEXT,
                project_id TEXT,
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

        # Pre-dates `PRAGMA user_version` tracking: a store created by an
        # older build has this table but may be missing `project_id`. Kept
        # column-guarded (rather than folded into a version bump) so an
        # already-migrated-by-column-check database still opens at version 0
        # without re-running a no-op ALTER.
        columns = {row[1] for row in cur.execute("PRAGMA table_info(events);").fetchall()}
        if "project_id" not in columns:
            cur.execute("ALTER TABLE events ADD COLUMN project_id TEXT;")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_events_run_seq ON events(run_id, seq);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_events_scope ON events(scope);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_events_episode ON events(episode_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_events_project_seq ON events(project_id, seq);")

    #: Ordered migration steps; step `i` takes a database at version `i` to
    #: version `i + 1`. `_init_db` runs `_MIGRATIONS[version:]` and stamps
    #: `_SCHEMA_VERSION` on completion, so adding a migration means appending
    #: here and incrementing `_SCHEMA_VERSION` -- never rewriting a past step.
    _MIGRATIONS: tuple[Any, ...] = (_migration_0_initial_schema,)

    @property
    def journal_mode(self) -> str:
        """Report SQLite's effective mode; never infer WAL from the path."""
        with self._lock:
            return str(self._conn.execute("PRAGMA journal_mode;").fetchone()[0]).lower()

    @property
    def durable(self) -> bool:
        return self.db_path != ":memory:" and self.journal_mode == "wal"

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
                    if event.project_id:
                        cur.execute(
                            "SELECT seq FROM events WHERE project_id = ? ORDER BY seq DESC LIMIT 1;",
                            (event.project_id,),
                        )
                        row = cur.fetchone()
                        if row is not None and seq_int <= row[0]:
                            cur.execute("ROLLBACK;")
                            return Result.fail(
                                kind="conflict",
                                message=(
                                    f"Non-monotonic sequence in project {event.project_id!r}: "
                                    f"event {event.event_id} has seq {event.seq} ({seq_int}) "
                                    f"<= prior seq {row[0]}"
                                ),
                            )
                    else:
                        r_id = event.run_id or "__global__"
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

                    envelope_dict = event.wire_dict()
                    envelope_json = json.dumps(envelope_dict, separators=(",", ":"), ensure_ascii=False)
                    envelope_digest = event.digest()

                    cur.execute(
                        """
                        INSERT INTO events (
                            event_id, seq, seq_str, run_id, episode_id, project_id, scope,
                            occurred_at, recorded_at, principal, tenant_id, owner_id,
                            confidentiality, retention_class, trainability, redaction_status,
                            envelope_json, envelope_digest
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            event.event_id,
                            seq_int,
                            str(event.seq),
                            event.run_id,
                            event.episode_id,
                            event.project_id,
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
                if range_query.project_id is not None:
                    query += " AND project_id = ?"
                    params.append(range_query.project_id)
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

    def integrity_check(self) -> Result[dict[str, Any]]:
        """Verify SQLite integrity and every stored envelope digest.

        SQLite's own check does not validate the content-addressed envelope
        bytes.  Release and recovery tooling need both answers, and a corrupt
        database must be reported as a typed failure rather than reconstructed
        from a partial read.
        """
        with self._lock:
            try:
                sqlite_result = str(
                    self._conn.execute("PRAGMA integrity_check").fetchone()[0]
                )
                rows = self._conn.execute(
                    "SELECT envelope_json, envelope_digest FROM events ORDER BY global_id ASC"
                ).fetchall()
                invalid = 0
                for row in rows:
                    envelope = parse_event_envelope(json.loads(row[0]))
                    if envelope.digest() != str(row[1]):
                        invalid += 1
                report = {
                    "sqlite": sqlite_result,
                    "envelopes": len(rows),
                    "invalid_envelopes": invalid,
                    "ok": sqlite_result.lower() == "ok" and invalid == 0,
                }
                return Result.success(report)
            except Exception as exc:
                return Result.fail("instrument_error", f"integrity check failed: {exc}")

    def backup(self, destination: str | Path) -> Path:
        """Create an atomic SQLite backup after a verified checkpoint.

        The destination must not already exist.  This makes an accidental
        overwrite impossible and gives release tooling a recoverable artifact
        whose bytes can be independently checked before restore.
        """
        target = Path(destination)
        if target.exists():
            raise FileExistsError(f"backup destination already exists: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{target.name}.", dir=target.parent))
        staged_db = staging / "events.sqlite3"
        try:
            with self._lock:
                if self.db_path != ":memory:":
                    self._conn.execute("PRAGMA wal_checkpoint(FULL)")
                with sqlite3.connect(str(staged_db)) as backup_conn:
                    self._conn.backup(backup_conn)
            os.replace(staged_db, target)
            staging.rmdir()
            return target
        except Exception:
            if staging.exists():
                for child in staging.iterdir():
                    child.unlink(missing_ok=True)
                staging.rmdir()
            raise

    @classmethod
    def restore_backup(
        cls, backup: str | Path, destination: str | Path,
        *, synchronous: str = "FULL",
    ) -> "SqliteEventStore":
        """Restore a verified backup into a new file-backed event store."""
        source, target = Path(backup), Path(destination)
        if not source.is_file():
            raise ValueError(f"event-store backup is missing: {source}")
        if target.exists():
            raise FileExistsError(f"restore destination already exists: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{target.name}.", dir=target.parent))
        staged_db = staging / "events.sqlite3"
        try:
            with sqlite3.connect(str(source)) as source_conn:
                check = str(source_conn.execute("PRAGMA integrity_check").fetchone()[0])
                if check.lower() != "ok":
                    raise ValueError(f"event-store backup failed integrity check: {check}")
                with sqlite3.connect(str(staged_db)) as target_conn:
                    source_conn.backup(target_conn)
            os.replace(staged_db, target)
            staging.rmdir()
            restored = cls(target, synchronous=synchronous)
            report = restored.integrity_check()
            if not report.ok or not report.value or not report.value["ok"]:
                restored.close()
                target.unlink(missing_ok=True)
                raise ValueError("restored event store failed envelope integrity check")
            return restored
        except Exception:
            if staging.exists():
                for child in staging.iterdir():
                    child.unlink(missing_ok=True)
                staging.rmdir()
            raise

    def close(self) -> None:
        """Close SQLite connection."""
        with self._lock:
            try:
                self._conn.execute("PRAGMA wal_checkpoint(FULL);")
            except sqlite3.Error:
                pass
            self._conn.close()
