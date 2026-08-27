"""SQLite WAL-backed command inbox, event outbox, and sequence allocator.

Owning contract: REQ-CLI-002, S6B-SA-001, DEC-6B-013, DEC-6B-014.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Mapping, Sequence


class ServiceInboxStore:
    """Transactional SQLite store for RuntimeService commands and events."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self.db_path = str(db_path)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        with self._conn:
            self._conn.execute("PRAGMA journal_mode = WAL;")
            self._conn.execute("PRAGMA synchronous = NORMAL;")
            self._conn.execute("PRAGMA foreign_keys = ON;")
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS command_inbox (
                    command_id TEXT PRIMARY KEY,
                    idempotency_key TEXT UNIQUE,
                    name TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    actor TEXT,
                    payload_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    receipt_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS event_outbox (
                    run_id TEXT NOT NULL,
                    seq INTEGER NOT NULL,
                    event_id TEXT NOT NULL,
                    event_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (run_id, seq)
                );
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS active_runs (
                    run_id TEXT PRIMARY KEY,
                    manifest_path TEXT NOT NULL,
                    repo_path TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )

    def record_command(
        self,
        command_id: str,
        idempotency_key: str,
        name: str,
        run_id: str,
        payload: Mapping[str, Any],
        actor: str = "operator",
        now: str = "",
    ) -> tuple[bool, Mapping[str, Any] | None]:
        """Record command in inbox. Returns (is_new, prior_receipt)."""
        with self._conn:
            cur = self._conn.cursor()
            cur.execute(
                "SELECT status, receipt_json FROM command_inbox WHERE idempotency_key = ?",
                (idempotency_key,),
            )
            row = cur.fetchone()
            if row is not None:
                receipt = json.loads(row["receipt_json"]) if row["receipt_json"] else None
                return False, receipt

            cur.execute(
                """
                INSERT INTO command_inbox (
                    command_id, idempotency_key, name, run_id, actor,
                    payload_json, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'accepted', ?, ?)
                """,
                (
                    command_id,
                    idempotency_key,
                    name,
                    run_id,
                    actor,
                    json.dumps(payload),
                    now,
                    now,
                ),
            )
            return True, None

    def complete_command(
        self,
        command_id: str,
        status: str,
        receipt: Mapping[str, Any],
        now: str = "",
    ) -> None:
        with self._conn:
            self._conn.execute(
                """
                UPDATE command_inbox
                SET status = ?, receipt_json = ?, updated_at = ?
                WHERE command_id = ?
                """,
                (status, json.dumps(receipt), now, command_id),
            )

    def append_event(
        self,
        run_id: str,
        event_envelope: Mapping[str, Any],
        now: str = "",
    ) -> int:
        """Assign next sequential seq for the run and persist."""
        with self._conn:
            cur = self._conn.cursor()
            cur.execute(
                "SELECT COALESCE(MAX(seq), 0) + 1 FROM event_outbox WHERE run_id = ?",
                (run_id,),
            )
            next_seq = cur.fetchone()[0]
            event_copy = dict(event_envelope)
            event_copy["seq"] = str(next_seq)
            cur.execute(
                """
                INSERT INTO event_outbox (run_id, seq, event_id, event_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    next_seq,
                    event_copy.get("eventId", f"evt-{next_seq}"),
                    json.dumps(event_copy),
                    now,
                ),
            )
            return next_seq

    def get_events(self, run_id: str, after_seq: int = 0) -> list[dict[str, Any]]:
        with self._conn:
            cur = self._conn.cursor()
            cur.execute(
                """
                SELECT event_json FROM event_outbox
                WHERE run_id = ? AND seq > ?
                ORDER BY seq ASC
                """,
                (run_id, after_seq),
            )
            return [json.loads(row["event_json"]) for row in cur.fetchall()]

    def set_run_state(
        self,
        run_id: str,
        manifest_path: str,
        repo_path: str,
        status: str,
        now: str = "",
    ) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO active_runs (run_id, manifest_path, repo_path, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    status = excluded.status,
                    updated_at = excluded.updated_at
                """,
                (run_id, manifest_path, repo_path, status, now, now),
            )

    def list_runs(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        with self._conn:
            cur = self._conn.cursor()
            cur.execute(
                """
                SELECT run_id, manifest_path, repo_path, status, created_at, updated_at
                FROM active_runs
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )
            return [dict(row) for row in cur.fetchall()]

    def get_run_state(self, run_id: str) -> dict[str, Any] | None:
        with self._conn:
            cur = self._conn.cursor()
            cur.execute("SELECT * FROM active_runs WHERE run_id = ?", (run_id,))
            row = cur.fetchone()
            if row is None:
                return None
            return dict(row)

    def get_latest_seq(self, run_id: str) -> int:
        with self._conn:
            cur = self._conn.cursor()
            cur.execute("SELECT COALESCE(MAX(seq), 0) FROM event_outbox WHERE run_id = ?", (run_id,))
            row = cur.fetchone()
            return int(row[0]) if row else 0

    def close(self) -> None:
        self._conn.close()

