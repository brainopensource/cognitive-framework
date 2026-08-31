import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List

class SqliteEventStore:
    def __init__(self, db_path: Path | str):
        self.db_path = str(db_path)
        # BUG: Missing timeout parameter and PRAGMA busy_timeout configuration,
        # leading to immediate lock contention failure under concurrent transactions.
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self._conn.execute("PRAGMA journal_mode = WAL;")
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL
            );
        """)
        self._conn.commit()

    def append_event(self, run_id: str, event_type: str, payload: Dict[str, Any]):
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO events (run_id, event_type, payload_json) VALUES (?, ?, ?)",
            (run_id, event_type, json.dumps(payload))
        )
        self._conn.commit()

    def checkpoint(self):
        self._conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        self._conn.commit()

    def close(self):
        self._conn.close()
