"""Thin recursive episode coordinator. Depth is telemetry, not a class tree.

One `EpisodeCoordinator` opens child episodes with attenuated budgets and
records depth labels in `lam.sqlite` (ADR-0010). Biological names
(Atom → Body) are emergent labels of integer depth, never subclasses.
"""

from __future__ import annotations

import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Mapping, Optional

DEPTH_LABELS = ("Atom", "Molecule", "Polymer", "Cell")


class BudgetExceeded(ValueError):
    """A consume or spawn would increase total spend past the parent ceiling."""


def depth_label(depth: int) -> str:
    if depth >= 4:
        return "Body"
    if depth < 0:
        return DEPTH_LABELS[0]
    return DEPTH_LABELS[depth]


class EpisodeCoordinator:
    """Single recursive coordinator for all coordination depths."""

    def __init__(self, db_path: Path | str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
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
                """
            )
            conn.commit()

    def open_episode(
        self,
        *,
        task_id: str,
        budget_tokens: int,
        parent_id: Optional[str] = None,
        episode_id: Optional[str] = None,
    ) -> dict[str, Any]:
        if budget_tokens < 0:
            raise BudgetExceeded("episode budget cannot be negative")
        depth = 0
        if parent_id is not None:
            parent = self.get_episode(parent_id)
            depth = int(parent["depth"]) + 1
            if budget_tokens > int(parent["remaining_tokens"]):
                raise BudgetExceeded("child budget exceeds parent remaining")
        eid = episode_id or str(uuid.uuid4())
        row = {
            "episode_id": eid,
            "parent_id": parent_id,
            "task_id": task_id,
            "depth": depth,
            "depth_label": depth_label(depth),
            "budget_tokens": int(budget_tokens),
            "remaining_tokens": int(budget_tokens),
            "tokens_used": 0,
            "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO episodes (
                    episode_id, parent_id, task_id, depth, depth_label,
                    budget_tokens, remaining_tokens, tokens_used, recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["episode_id"],
                    row["parent_id"],
                    row["task_id"],
                    row["depth"],
                    row["depth_label"],
                    row["budget_tokens"],
                    row["remaining_tokens"],
                    row["tokens_used"],
                    row["recorded_at"],
                ),
            )
            if parent_id is not None:
                conn.execute(
                    """
                    UPDATE episodes
                    SET remaining_tokens = remaining_tokens - ?
                    WHERE episode_id = ?
                    """,
                    (int(budget_tokens), parent_id),
                )
            conn.commit()
        return row

    def spawn(
        self,
        parent_id: str,
        *,
        task_id: str,
        requested_tokens: int,
        episode_id: Optional[str] = None,
    ) -> dict[str, Any]:
        parent = self.get_episode(parent_id)
        remaining = int(parent["remaining_tokens"])
        child_budget = min(max(int(requested_tokens), 0), remaining)
        return self.open_episode(
            task_id=task_id,
            budget_tokens=child_budget,
            parent_id=parent_id,
            episode_id=episode_id,
        )

    def consume(self, episode_id: str, tokens: int) -> Mapping[str, Any]:
        if tokens < 0:
            raise BudgetExceeded("token consume cannot be negative")
        ep = self.get_episode(episode_id)
        remaining = int(ep["remaining_tokens"])
        if tokens > remaining:
            raise BudgetExceeded(
                f"consume {tokens} exceeds remaining {remaining} on {episode_id}"
            )
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE episodes
                SET remaining_tokens = remaining_tokens - ?,
                    tokens_used = tokens_used + ?
                WHERE episode_id = ?
                """,
                (int(tokens), int(tokens), episode_id),
            )
            conn.commit()
        return self.get_episode(episode_id)

    def get_episode(self, episode_id: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM episodes WHERE episode_id = ?",
                (episode_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"unknown episode {episode_id}")
        return dict(row)
