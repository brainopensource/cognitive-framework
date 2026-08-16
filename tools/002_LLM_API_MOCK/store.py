"""SQLite storage engine for rich harness pipeline metadata, traces, model ceilings, and budget events."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "lam.sqlite"


class LamStore:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS scenarios (
                    id TEXT PRIMARY KEY,
                    tier INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    atoms_used TEXT NOT NULL,
                    n_files INTEGER NOT NULL,
                    n_turns INTEGER NOT NULL,
                    created_from TEXT NOT NULL,
                    content_hash TEXT
                );

                CREATE TABLE IF NOT EXISTS traces (
                    trace_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_id TEXT NOT NULL,
                    backend TEXT NOT NULL,
                    model TEXT NOT NULL,
                    model_tier INTEGER DEFAULT 1,
                    scenario_tier INTEGER DEFAULT 1,
                    passed INTEGER NOT NULL,
                    llm_calls INTEGER NOT NULL,
                    prompt_tokens INTEGER NOT NULL,
                    completion_tokens INTEGER NOT NULL,
                    usd REAL NOT NULL,
                    wall_s REAL NOT NULL,
                    context_bytes INTEGER DEFAULT 0,
                    compression_ratio REAL DEFAULT 1.0,
                    memory_turns INTEGER DEFAULT 0,
                    skills_used TEXT DEFAULT '[]',
                    harness_version TEXT DEFAULT 'v0.4.1',
                    is_downgrade INTEGER DEFAULT 0,
                    recorded_at TEXT NOT NULL,
                    blob_path TEXT,
                    harness TEXT,
                    cascade TEXT,
                    episode_id TEXT,
                    parent_id TEXT,
                    task_id TEXT,
                    depth INTEGER,
                    FOREIGN KEY(scenario_id) REFERENCES scenarios(id)
                );

                CREATE TABLE IF NOT EXISTS episodes (
                    episode_id TEXT PRIMARY KEY,
                    parent_id TEXT,
                    task_id TEXT NOT NULL,
                    depth INTEGER NOT NULL,
                    depth_label TEXT NOT NULL,
                    budget_tokens INTEGER NOT NULL,
                    remaining_tokens INTEGER NOT NULL,
                    tokens_used INTEGER NOT NULL DEFAULT 0,
                    recorded_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS model_ceilings (
                    model TEXT PRIMARY KEY,
                    band TEXT NOT NULL,
                    ceiling_tier INTEGER NOT NULL,
                    evidence_trace_id INTEGER,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS budget_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    calls_delta INTEGER NOT NULL,
                    usd_delta REAL NOT NULL,
                    note TEXT NOT NULL
                );
            """)
            # Auto-migrate schema additions if table existed prior to update
            cur = conn.execute("PRAGMA table_info(traces);")
            existing_cols = {row["name"] for row in cur.fetchall()}
            if "is_downgrade" not in existing_cols:
                conn.execute("ALTER TABLE traces ADD COLUMN is_downgrade INTEGER DEFAULT 0;")
            if "model_tier" not in existing_cols:
                conn.execute("ALTER TABLE traces ADD COLUMN model_tier INTEGER DEFAULT 1;")
            if "scenario_tier" not in existing_cols:
                conn.execute("ALTER TABLE traces ADD COLUMN scenario_tier INTEGER DEFAULT 1;")
            for col, decl in (
                ("harness", "TEXT"),
                ("cascade", "TEXT"),
                ("episode_id", "TEXT"),
                ("parent_id", "TEXT"),
                ("task_id", "TEXT"),
                ("depth", "INTEGER"),
            ):
                if col not in existing_cols:
                    conn.execute(f"ALTER TABLE traces ADD COLUMN {col} {decl};")

    def upsert_scenario(
        self,
        scenario_id: str,
        tier: int,
        title: str,
        atoms: List[str],
        n_files: int,
        n_turns: int,
        created_from: str = "hand",
        content_hash: Optional[str] = None,
    ) -> None:
        atoms_str = json.dumps(sorted(list(set(atoms))))
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO scenarios (id, tier, title, atoms_used, n_files, n_turns, created_from, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    tier=excluded.tier,
                    title=excluded.title,
                    atoms_used=excluded.atoms_used,
                    n_files=excluded.n_files,
                    n_turns=excluded.n_turns,
                    created_from=excluded.created_from,
                    content_hash=excluded.content_hash;
            """,
                (scenario_id, tier, title, atoms_str, n_files, n_turns, created_from, content_hash),
            )

    def insert_trace(
        self,
        scenario_id: str,
        backend: str,
        model: str,
        passed: bool,
        llm_calls: int,
        prompt_tokens: int,
        completion_tokens: int,
        usd: float,
        wall_s: float,
        model_tier: int = 1,
        scenario_tier: int = 1,
        context_bytes: int = 0,
        compression_ratio: float = 1.0,
        memory_turns: int = 0,
        skills_used: Optional[List[str]] = None,
        harness_version: str = "v0.4.1",
        is_downgrade: bool = False,
        blob_path: Optional[str] = None,
        harness: Optional[str] = None,
        cascade: Optional[List[str]] = None,
        episode_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        depth: Optional[int] = None,
    ) -> int:
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        skills_json = json.dumps(skills_used or [])
        with self._get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO traces (
                    scenario_id, backend, model, model_tier, scenario_tier, passed, llm_calls,
                    prompt_tokens, completion_tokens, usd, wall_s, context_bytes, compression_ratio,
                    memory_turns, skills_used, harness_version, is_downgrade, recorded_at, blob_path,
                    harness, cascade, episode_id, parent_id, task_id, depth
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
                (
                    scenario_id,
                    backend,
                    model,
                    model_tier,
                    scenario_tier,
                    1 if passed else 0,
                    llm_calls,
                    prompt_tokens,
                    completion_tokens,
                    usd,
                    wall_s,
                    context_bytes,
                    compression_ratio,
                    memory_turns,
                    skills_json,
                    harness_version,
                    1 if is_downgrade else 0,
                    ts,
                    blob_path,
                    harness,
                    json.dumps(cascade or []),
                    episode_id,
                    parent_id,
                    task_id,
                    depth,
                ),
            )
            trace_id = cur.lastrowid or 0

        # Update model ceiling if passed
        if passed:
            self.update_model_ceiling(model, scenario_tier, trace_id)

        return trace_id

    def update_model_ceiling(self, model: str, tier: int, evidence_trace_id: int) -> None:
        band = "free" if ":free" in model or "lam/" in model or "ollama/" in model else "paid"
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self._get_connection() as conn:
            cur = conn.execute("SELECT ceiling_tier FROM model_ceilings WHERE model = ?;", (model,))
            row = cur.fetchone()
            if not row or tier > row["ceiling_tier"]:
                conn.execute(
                    """
                    INSERT INTO model_ceilings (model, band, ceiling_tier, evidence_trace_id, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(model) DO UPDATE SET
                        ceiling_tier=excluded.ceiling_tier,
                        evidence_trace_id=excluded.evidence_trace_id,
                        updated_at=excluded.updated_at;
                """,
                    (model, band, tier, evidence_trace_id, ts),
                )

    def get_summary_kpis(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            n_scenarios = conn.execute("SELECT COUNT(*) FROM scenarios;").fetchone()[0]
            n_traces = conn.execute("SELECT COUNT(*) FROM traces;").fetchone()[0]
            total_calls = conn.execute("SELECT SUM(llm_calls) FROM traces;").fetchone()[0] or 0
            total_tokens = conn.execute("SELECT SUM(prompt_tokens + completion_tokens) FROM traces;").fetchone()[0] or 0
            total_usd = conn.execute("SELECT SUM(usd) FROM traces;").fetchone()[0] or 0.0
            avg_wall = conn.execute("SELECT AVG(wall_s) FROM traces;").fetchone()[0] or 0.0
            downgrade_passes = conn.execute("SELECT COUNT(*) FROM traces WHERE is_downgrade=1 AND passed=1;").fetchone()[0]
            downgrade_attempts = conn.execute("SELECT COUNT(*) FROM traces WHERE is_downgrade=1;").fetchone()[0]
            ceilings = [dict(r) for r in conn.execute("SELECT * FROM model_ceilings ORDER BY ceiling_tier DESC;").fetchall()]
            live_pass_count = conn.execute(
                "SELECT COUNT(*) FROM traces WHERE passed=1 AND backend != 'lam';"
            ).fetchone()[0]
            lam_replay_pass_count = conn.execute(
                "SELECT COUNT(*) FROM traces WHERE passed=1 AND backend = 'lam';"
            ).fetchone()[0]

        return {
            "total_scenarios": n_scenarios,
            "total_traces": n_traces,
            "total_calls": total_calls,
            "total_tokens": total_tokens,
            "total_usd": total_usd,
            "avg_wall_s": round(avg_wall, 4),
            "downgrade_pass_rate": round(downgrade_passes / downgrade_attempts, 2) if downgrade_attempts else 0.0,
            "model_ceilings": ceilings,
            "live_pass_count": live_pass_count,
            "lam_replay_pass_count": lam_replay_pass_count,
        }
