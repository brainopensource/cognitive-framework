"""Transactional file/SQLite IMemoryEngine (SPEC §2.2)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Callable, ClassVar, Mapping

from ...domain.wire.result import Ok, Result
from ...domain.wire.types_gen import (
    ClaimRef,
    ConsolidationReport,
    MemoryHit,
    MemoryId,
    MemoryQuery,
    MemoryRecord,
)
from ...runtime.memory import MemoryAccess, MemoryResult, RetrievalProvenance, validate_retrieval
from .blob_store import FileBlobStore
from ...domain.canonicalisation.digest import digest_of

__all__ = ["LocalFileMemoryAdapter", "DurableMemoryPort"]


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


class DurableMemoryPort:
    """Single-host ADR-0100 memory adapter with SQLite-WAL metadata and CAS blobs."""

    def __init__(self, root: str | Path, category: str, *, fact_emitter: Callable[[Mapping[str, Any]], None] | None = None, ranker: Callable[[str, list[tuple[str, str, str]]], list[tuple[str, str, str]]] | None = None) -> None:
        if category not in {"knowledge", "experience", "project", "skills"}:
            raise ValueError("unknown memory category")
        self.category = category
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(self._root / "memory.sqlite3"), isolation_level=None)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=FULL")
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS memory_records ("
            "record_id TEXT PRIMARY KEY, category TEXT NOT NULL, tenant TEXT NOT NULL, "
            "project TEXT NOT NULL, blob_digest TEXT NOT NULL, metadata TEXT NOT NULL, "
            "invalidated INTEGER NOT NULL DEFAULT 0, quarantined INTEGER NOT NULL DEFAULT 0, "
            "legal_hold INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL)"
        )
        self._blobs = FileBlobStore(self._root / "blobs")
        self._fact_emitter = fact_emitter
        self._ranker = ranker

    @staticmethod
    def _authorized(access: MemoryAccess, category: str, action: str) -> None:
        if not access.permitted() or action not in access.actions:
            raise PermissionError("memory capability denied or revoked")
        requested = access.selector.get("category")
        if requested is not None and requested != category:
            raise PermissionError("memory category is outside the authorized selector")

    def write(self, value: Mapping[str, Any], access: MemoryAccess) -> str:
        self._authorized(access, self.category, "write")
        text = value.get("text")
        if not isinstance(text, str) or not text:
            raise ValueError("memory records require non-empty text")
        blob = self._blobs.put(text.encode("utf-8"))
        if not blob.ok:
            raise IOError(blob.error)
        digest = str(blob.value)
        record_id = f"{self.category}:{digest[7:19]}"
        metadata = {"tenant": access.tenant, "project": access.project, **dict(value)}
        self._db.execute("BEGIN IMMEDIATE")
        try:
            self._db.execute(
                "INSERT OR IGNORE INTO memory_records(record_id,category,tenant,project,blob_digest,metadata,created_at) VALUES(?,?,?,?,?,?,datetime('now'))",
                (record_id, self.category, access.tenant, access.project, digest, json.dumps(metadata, sort_keys=True)),
            )
            self._db.execute("COMMIT")
        except sqlite3.Error:
            self._db.execute("ROLLBACK")
            raise
        if self._fact_emitter:
            self._fact_emitter({"kind": "ClaimRecorded", "recordId": record_id, "digest": digest, "category": self.category})
        return record_id

    def recall(self, query: str, access: MemoryAccess, limit: int = 20) -> MemoryResult:
        validate_retrieval(query, access, limit)
        self._authorized(access, self.category, "read")
        # Authorization and tenant/category filtering happen before any blob read or ranking.
        rows = self._db.execute(
            "SELECT record_id,blob_digest,metadata FROM memory_records WHERE category=? AND tenant=? AND project=? AND invalidated=0 AND quarantined=0",
            (self.category, access.tenant, access.project),
        ).fetchall()
        needle = query.casefold()
        matches: list[tuple[str, str, str]] = []
        for record_id, blob_digest, metadata_raw in rows:
            payload = json.loads(metadata_raw)
            data = self._blobs.get(blob_digest)
            if not data.ok:
                continue
            text = bytes(data.value).decode("utf-8")
            if needle in text.casefold():
                matches.append((record_id, text, blob_digest))
        if self._ranker is not None:
            matches = list(self._ranker(query, matches))
        else:
            matches.sort(key=lambda row: (row[1].casefold().find(needle), row[0]))
        selected, dropped = matches[:limit], matches[limit:]
        provenance = RetrievalProvenance(
            query_digest=digest_of({"query": query, "tenant": access.tenant, "project": access.project}),
            policy_identity="m8-durable-lexical/1",
            source_record_digests=tuple(digest_of({"id": r, "blob": b}) for r, _, b in matches),
            selected_ids=tuple(r for r, _, _ in selected), dropped_ids=tuple(r for r, _, _ in dropped),
            cache_identity=None, context_selection_digest=None, redacted=False,
        )
        return MemoryResult(tuple(r for r, _, _ in selected), provenance)

    def invalidate(self, record_id: str, access: MemoryAccess) -> None:
        self._authorized(access, self.category, "invalidate")
        row = self._db.execute(
            "SELECT tenant,project FROM memory_records WHERE record_id=? AND category=?", (record_id, self.category)
        ).fetchone()
        if row is None or row[0] != access.tenant or row[1] != access.project:
            raise PermissionError("memory record is outside the project scope")
        self._db.execute("UPDATE memory_records SET invalidated=1 WHERE record_id=?", (record_id,))

    def set_legal_hold(self, record_id: str, access: MemoryAccess, enabled: bool = True) -> None:
        self._authorized(access, self.category, "retain")
        row = self._db.execute("SELECT tenant,project FROM memory_records WHERE record_id=? AND category=?", (record_id, self.category)).fetchone()
        if row is None or row[0] != access.tenant or row[1] != access.project:
            raise PermissionError("memory record is outside the project scope")
        self._db.execute("UPDATE memory_records SET legal_hold=? WHERE record_id=?", (int(enabled), record_id))

    def quarantine(self, record_id: str, access: MemoryAccess) -> None:
        """Hide a suspect record without deleting its immutable blob."""
        self._authorized(access, self.category, "invalidate")
        row = self._db.execute("SELECT tenant,project FROM memory_records WHERE record_id=? AND category=?", (record_id, self.category)).fetchone()
        if row is None or row[0] != access.tenant or row[1] != access.project:
            raise PermissionError("memory record is outside the project scope")
        self._db.execute("UPDATE memory_records SET quarantined=1 WHERE record_id=?", (record_id,))

    def gc(self, access: MemoryAccess) -> int:
        """Delete only invalidated, non-held metadata; CAS sweep is intentionally separate."""
        self._authorized(access, self.category, "retain")
        cursor = self._db.execute(
            "DELETE FROM memory_records WHERE category=? AND tenant=? AND project=? AND invalidated=1 AND legal_hold=0",
            (self.category, access.tenant, access.project),
        )
        return int(cursor.rowcount)
