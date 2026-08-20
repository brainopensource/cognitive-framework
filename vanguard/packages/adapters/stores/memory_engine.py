"""Transactional file/SQLite IMemoryEngine (SPEC §2.2)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import ClassVar

from ...domain.wire.result import Ok, Result
from ...domain.wire.types_gen import (
    ClaimRef,
    ConsolidationReport,
    MemoryHit,
    MemoryId,
    MemoryQuery,
    MemoryRecord,
)

__all__ = ["LocalFileMemoryAdapter"]


class LocalFileMemoryAdapter:
    spi_version: ClassVar[str] = "1.0"

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)
        self._path = self._root / "memory.sqlite"
        self._db = sqlite3.connect(str(self._path))
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=FULL")
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS memory ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "kind TEXT NOT NULL,"
            "text TEXT NOT NULL,"
            "metadata TEXT NOT NULL,"
            "invalidated INTEGER NOT NULL DEFAULT 0"
            ")"
        )
        self._db.commit()

    def write(self, record: MemoryRecord) -> Result[MemoryId]:
        try:
            self._db.execute("BEGIN IMMEDIATE")
            cursor = self._db.execute(
                "INSERT INTO memory(kind, text, metadata) VALUES (?, ?, ?)",
                (record.kind, record.text, json.dumps(dict(record.metadata))),
            )
            self._db.commit()
        except sqlite3.Error:
            self._db.rollback()
            raise
        return Ok(str(cursor.lastrowid))

    def recall(self, query: MemoryQuery, budget_tokens: int) -> Result[tuple[MemoryHit, ...]]:
        _ = budget_tokens
        sql = "SELECT id, text FROM memory WHERE invalidated = 0 AND text LIKE ?"
        args: list[object] = [f"%{query.text}%"]
        if query.kind:
            sql += " AND kind = ?"
            args.append(query.kind)
        sql += " ORDER BY id DESC"
        if query.limit:
            sql += " LIMIT ?"
            args.append(int(query.limit))
        rows = self._db.execute(sql, args).fetchall()
        hits = tuple(MemoryHit(id=str(row[0]), text=str(row[1]), score=1.0) for row in rows)
        return Ok(hits)

    def consolidate(self, since: int) -> Result[ConsolidationReport]:
        _ = since
        return Ok(ConsolidationReport(merged=0, dropped=0))

    def invalidate(self, claim: ClaimRef, reason: str) -> Result[None]:
        _ = reason
        self._db.execute("BEGIN IMMEDIATE")
        self._db.execute(
            "UPDATE memory SET invalidated = 1 WHERE id = ? OR text LIKE ?",
            (claim.claim_id, f"%{claim.claim_id}%"),
        )
        self._db.commit()
        return Ok(None)

    def capabilities(self) -> frozenset[str]:
        return frozenset({"kv"})
