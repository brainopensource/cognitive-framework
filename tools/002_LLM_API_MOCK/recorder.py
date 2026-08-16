"""Append-only SQLite provenance recorder for mock LLM selections."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, Optional


class MockRecorder:
    def __init__(self, db_path: Path | str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mock_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    request_sha256 TEXT NOT NULL,
                    scenario_key TEXT NOT NULL,
                    tier INTEGER NOT NULL,
                    requested_turn INTEGER NOT NULL,
                    returned_turn INTEGER NOT NULL,
                    reply_sha256 TEXT NOT NULL,
                    source_label TEXT,
                    run_id TEXT,
                    prompt_snippet TEXT,
                    response_snippet TEXT
                )
                """
            )
            conn.commit()

    def record_call(
        self,
        request_sha256: str,
        scenario_key: str,
        tier: int,
        requested_turn: int,
        returned_turn: int,
        reply_sha256: str,
        source_label: str = "",
        run_id: str = "",
        prompt: str = "",
        response: str = "",
    ) -> None:
        created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO mock_calls (
                    created_at, request_sha256, scenario_key, tier,
                    requested_turn, returned_turn, reply_sha256,
                    source_label, run_id, prompt_snippet, response_snippet
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    request_sha256,
                    scenario_key,
                    tier,
                    requested_turn,
                    returned_turn,
                    reply_sha256,
                    source_label,
                    run_id,
                    prompt[:200],
                    response[:200],
                ),
            )
            conn.commit()
