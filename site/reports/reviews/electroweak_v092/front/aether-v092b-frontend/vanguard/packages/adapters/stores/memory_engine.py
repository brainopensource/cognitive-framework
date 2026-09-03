"""Transactional file/SQLite IMemoryEngine (SPEC §2.2)."""

from __future__ import annotations

import json
import hashlib
import os
import re
import shutil
import sqlite3
import tempfile
from datetime import datetime
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
from ...ports.memory import (
    MemoryAccess,
    MemoryResult,
    RetrievalProvenance,
    authorize_memory_action,
    validate_retrieval,
)
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
    """Single-host ADR-0100 memory port backed by SQLite-WAL and a CAS.

    Metadata, the lexical inverted index, and the causal ``ClaimRecorded`` fact
    are committed together.  Blobs are deliberately written first: if the
    metadata transaction is interrupted the orphan is harmless and is removed
    by the reviewed sweep.  No product path uses :class:`InMemoryMemoryPort`.
    """

    SCHEMA_VERSION = 2
    POLICY_IDENTITY = "m8-durable-lexical/2"
    TOKENIZER_IDENTITY = "unicode-word/1"
    DEFAULT_TIMESTAMP = "2026-08-27T00:00:00.000Z"
    _TOKEN = re.compile(r"[\w]+", re.UNICODE)
    _NETWORK_FS = frozenset({"nfs", "nfs4", "cifs", "smb3", "sshfs", "fuse.sshfs"})

    def __init__(
        self,
        root: str | Path,
        category: str,
        *,
        fact_emitter: Callable[[Mapping[str, Any]], None] | None = None,
        ranker: Callable[[str, list[tuple[str, str, str]]], list[tuple[str, str, str]]] | None = None,
        clock: Callable[[], str] | None = None,
        quarantine_seconds: int = 86_400,
        allow_network_fs: bool = False,
    ) -> None:
        if category not in {"knowledge", "experience", "project", "skills"}:
            raise ValueError("unknown memory category")
        self.category = category
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)
        self._fact_emitter = fact_emitter
        self._ranker = ranker
        self._clock = clock
        if quarantine_seconds < 0:
            raise ValueError("quarantine interval must not be negative")
        self._quarantine_seconds = quarantine_seconds
        if not allow_network_fs and self._on_network_fs(self._root):
            raise OSError("SQLite-WAL memory storage refuses network filesystems")
        self._db_path = self._root / "memory.sqlite3"
        try:
            self._db = sqlite3.connect(str(self._db_path), isolation_level=None)
            self._db.row_factory = sqlite3.Row
            self._db.execute("PRAGMA journal_mode=WAL")
            self._db.execute("PRAGMA synchronous=FULL")
            self._db.execute("PRAGMA foreign_keys=ON")
            self._migrate()
            self._recover()
        except sqlite3.DatabaseError as exc:
            raise RuntimeError("memory database is corrupt and cannot be opened") from exc
        self._blobs = FileBlobStore(self._root / "blobs")

    @classmethod
    def _on_network_fs(cls, path: Path) -> bool:
        """Refuse known network mounts; local filesystems remain supported."""
        mounts = Path("/proc/mounts")
        if not mounts.is_file():
            return False
        resolved = path.resolve()
        best: tuple[int, str] | None = None
        try:
            for line in mounts.read_text(encoding="utf-8").splitlines():
                fields = line.split()
                if len(fields) < 3:
                    continue
                mount = Path(fields[1].replace("\\040", " "))
                try:
                    length = len(mount.resolve().parts)
                    if resolved == mount.resolve() or mount.resolve() in resolved.parents:
                        if best is None or length > best[0]:
                            best = (length, fields[2])
                except OSError:
                    continue
        except OSError:
            return False
        return bool(best and best[1] in cls._NETWORK_FS)

    def _migrate(self) -> None:
        """Create or upgrade the store idempotently, refusing unknown versions."""
        version = int(self._db.execute("PRAGMA user_version").fetchone()[0])
        if version > self.SCHEMA_VERSION:
            raise RuntimeError(f"unsupported memory schema version {version}")
        try:
            self._db.executescript(
                """
                CREATE TABLE IF NOT EXISTS memory_records (
                    record_id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    tenant TEXT NOT NULL,
                    project TEXT NOT NULL,
                    blob_digest TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    invalidated INTEGER NOT NULL DEFAULT 0,
                    quarantined INTEGER NOT NULL DEFAULT 0,
                    legal_hold INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    quarantined_at TEXT
                );
                CREATE INDEX IF NOT EXISTS memory_scope_idx
                    ON memory_records(category, tenant, project, invalidated, quarantined);
                CREATE TABLE IF NOT EXISTS memory_terms (
                    record_id TEXT NOT NULL REFERENCES memory_records(record_id) ON DELETE CASCADE,
                    term TEXT NOT NULL,
                    PRIMARY KEY(record_id, term)
                );
                CREATE INDEX IF NOT EXISTS memory_term_idx ON memory_terms(term, record_id);
                CREATE TABLE IF NOT EXISTS memory_facts (
                    fact_id TEXT PRIMARY KEY,
                    record_id TEXT NOT NULL REFERENCES memory_records(record_id) ON DELETE CASCADE,
                    fact_kind TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    payload_digest TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS memory_retrievals (
                    retrieval_id TEXT PRIMARY KEY,
                    tenant TEXT NOT NULL,
                    project TEXT NOT NULL,
                    category TEXT NOT NULL,
                    provenance TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS memory_gc_receipts (
                    receipt_id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    tenant TEXT NOT NULL,
                    project TEXT NOT NULL,
                    dry_run INTEGER NOT NULL,
                    deleted_records INTEGER NOT NULL,
                    deleted_blobs INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS memory_store_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
            columns = {str(row[1]) for row in self._db.execute("PRAGMA table_info(memory_records)")}
            if "quarantined_at" not in columns:
                self._db.execute("ALTER TABLE memory_records ADD COLUMN quarantined_at TEXT")
            if version < self.SCHEMA_VERSION:
                # Legacy DurableMemoryPort rows predate the local causal-fact
                # table.  Migrate only rows whose CAS blob still exists; rows
                # without content remain quarantined by _recover().
                legacy_rows = self._db.execute(
                    "SELECT record_id, category, tenant, project, blob_digest, metadata, created_at "
                    "FROM memory_records"
                ).fetchall()
                for row in legacy_rows:
                    if self._blob_path(str(row["blob_digest"])).is_file():
                        payload = {
                            "kind": "ClaimRecorded",
                            "schema": "memory.recorded/1",
                            "recordId": str(row["record_id"]),
                            "category": str(row["category"]),
                            "tenant": str(row["tenant"]),
                            "project": str(row["project"]),
                            "blobDigest": str(row["blob_digest"]),
                            "metadataDigest": digest_of(json.loads(str(row["metadata"]))),
                        }
                        payload_digest = digest_of(payload)
                        self._db.execute(
                            "INSERT OR IGNORE INTO memory_facts "
                            "(fact_id,record_id,fact_kind,payload,payload_digest,created_at) VALUES(?,?,?,?,?,?)",
                            (f"fact:{payload_digest[7:]}", str(row["record_id"]), "ClaimRecorded",
                             json.dumps(payload, sort_keys=True, separators=(",", ":")), payload_digest,
                             str(row["created_at"])),
                        )
            self._db.execute(f"PRAGMA user_version = {self.SCHEMA_VERSION}")
            self._db.execute(
                "INSERT INTO memory_store_meta(key,value) VALUES('schema_version',?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (str(self.SCHEMA_VERSION),),
            )
        except Exception:
            if self._db.in_transaction:
                self._db.execute("ROLLBACK")
            raise

    def _recover(self) -> None:
        """Quarantine metadata whose immutable content or causal fact is absent."""
        rows = self._db.execute(
            "SELECT record_id, blob_digest FROM memory_records WHERE quarantined=0"
        ).fetchall()
        for row in rows:
            fact = self._db.execute(
                "SELECT payload, payload_digest FROM memory_facts WHERE record_id=?",
                (row["record_id"],),
            ).fetchone()
            valid_fact = False
            if fact is not None:
                try:
                    payload = json.loads(str(fact["payload"]))
                    valid_fact = (
                        isinstance(payload, Mapping)
                        and str(payload.get("recordId")) == str(row["record_id"])
                        and str(payload.get("blobDigest")) == str(row["blob_digest"])
                        and str(fact["payload_digest"]) == digest_of(payload)
                    )
                except (TypeError, ValueError, json.JSONDecodeError):
                    valid_fact = False
            if not valid_fact or not self._blob_path(str(row["blob_digest"])).is_file():
                self._db.execute(
                    "UPDATE memory_records SET quarantined=1, quarantined_at=COALESCE(quarantined_at, ?) WHERE record_id=?",
                    (self._now(), row["record_id"]),
                )

    def _now(self) -> str:
        if self._clock is not None:
            value = self._clock()
            if not isinstance(value, str) or not value:
                raise RuntimeError("memory clock returned an invalid timestamp")
            return value
        # Deterministic fallback for hermetic callers. Product composition
        # injects its ClockPort; silent reads from the process wall clock are
        # forbidden by the determinism invariant.
        return self.DEFAULT_TIMESTAMP

    def _blob_path(self, digest: str) -> Path:
        hexed = digest[7:] if digest.startswith("sha256:") else ""
        if len(hexed) != 64 or any(char not in "0123456789abcdef" for char in hexed):
            return self._root / "blobs" / "__invalid__"
        return self._root / "blobs" / hexed[:2] / hexed[2:]

    @classmethod
    def _terms(cls, text: str) -> tuple[str, ...]:
        return tuple(sorted(set(match.group(0).casefold() for match in cls._TOKEN.finditer(text))))

    def _record(self, record_id: str, access: MemoryAccess) -> sqlite3.Row:
        row = self._db.execute(
            "SELECT * FROM memory_records WHERE record_id=? AND category=? AND tenant=? AND project=?",
            (record_id, self.category, access.tenant, access.project),
        ).fetchone()
        if row is None:
            # Do not disclose whether an ID exists in another scope.
            raise PermissionError("memory record is outside the project scope")
        return row

    _authorized = staticmethod(authorize_memory_action)

    def write(self, value: Mapping[str, Any], access: MemoryAccess) -> str:
        self._authorized(access, self.category, "write")
        if not isinstance(value, Mapping):
            raise ValueError("memory value must be a mapping")
        if value.get("category", self.category) != self.category:
            raise ValueError("memory category mismatch")
        text = value.get("text")
        if not isinstance(text, str) or not text:
            raise ValueError("memory records require non-empty text")
        metadata = dict(value)
        metadata["category"] = self.category
        metadata["tenant"] = access.tenant
        metadata["project"] = access.project
        try:
            metadata_json = json.dumps(metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            raise ValueError("memory metadata must be JSON-serializable") from exc
        blob = self._blobs.put(text.encode("utf-8"))
        if not blob.ok:
            raise IOError(blob.error)
        digest = str(blob.value)
        record_id = f"{self.category}:{digest_of({'category': self.category, 'tenant': access.tenant, 'project': access.project, 'blob': digest, 'metadata': metadata})[7:]}"
        now = self._now()
        fact_payload = {
            "kind": "ClaimRecorded",
            "schema": "memory.recorded/1",
            "recordId": record_id,
            "category": self.category,
            "tenant": access.tenant,
            "project": access.project,
            "blobDigest": digest,
            "digest": digest,
            "metadataDigest": digest_of(metadata),
        }
        fact_json = json.dumps(fact_payload, sort_keys=True, separators=(",", ":"))
        fact_digest = digest_of(fact_payload)
        try:
            self._db.execute("BEGIN IMMEDIATE")
            self._db.execute(
                "INSERT OR IGNORE INTO memory_records(record_id,category,tenant,project,blob_digest,metadata,created_at) VALUES(?,?,?,?,?,?,?)",
                (record_id, self.category, access.tenant, access.project, digest, metadata_json, now),
            )
            self._db.executemany(
                "INSERT OR IGNORE INTO memory_terms(record_id,term) VALUES(?,?)",
                ((record_id, term) for term in self._terms(text)),
            )
            self._db.execute(
                "INSERT OR IGNORE INTO memory_facts(fact_id,record_id,fact_kind,payload,payload_digest,created_at) VALUES(?,?,?,?,?,?)",
                (f"fact:{fact_digest[7:]}", record_id, "ClaimRecorded", fact_json, fact_digest, now),
            )
            self._db.execute("COMMIT")
        except Exception:
            self._db.execute("ROLLBACK")
            raise
        if self._fact_emitter is not None:
            try:
                self._fact_emitter(fact_payload)
            except Exception as exc:
                # The local fact is durable, but an unavailable canonical
                # notifier makes the record unsafe for product retrieval.
                self._db.execute(
                    "UPDATE memory_records SET quarantined=1, quarantined_at=? WHERE record_id=?",
                    (self._now(), record_id),
                )
                raise IOError("causal memory fact could not be published") from exc
        return record_id

    def recall(self, query: str, access: MemoryAccess, limit: int = 20) -> MemoryResult:
        self._authorized(access, self.category, "read")
        validate_retrieval(query, access, limit)
        terms = self._terms(query)
        if not terms:
            matches: list[tuple[str, str, str]] = []
        else:
            placeholders = ",".join("?" for _ in terms)
            rows = self._db.execute(
                f"""SELECT r.record_id, r.blob_digest FROM memory_records r
                    JOIN memory_terms t ON t.record_id=r.record_id
                    WHERE r.category=? AND r.tenant=? AND r.project=?
                      AND r.invalidated=0 AND r.quarantined=0 AND t.term IN ({placeholders})
                    GROUP BY r.record_id, r.blob_digest HAVING COUNT(DISTINCT t.term)=?
                    ORDER BY r.record_id""",
                (self.category, access.tenant, access.project, *terms, len(terms)),
            ).fetchall()
            needle = query.casefold()
            matches = []
            for row in rows:
                data = self._blobs.get(str(row["blob_digest"]))
                if not data.ok:
                    continue
                text = bytes(data.value).decode("utf-8")
                if needle in text.casefold():
                    matches.append((str(row["record_id"]), text, str(row["blob_digest"])))
        if self._ranker is not None:
            matches = list(self._ranker(query, matches))
        else:
            needle = query.casefold()
            matches.sort(key=lambda row: (row[1].casefold().find(needle), row[0]))
        selected, dropped = matches[:limit], matches[limit:]
        provenance = RetrievalProvenance(
            query_digest=digest_of({"query": query, "category": self.category, "tenant": access.tenant, "project": access.project}),
            policy_identity=f"{self.POLICY_IDENTITY};index={self.SCHEMA_VERSION};tokenizer={self.TOKENIZER_IDENTITY}",
            source_record_digests=tuple(digest_of({"id": r, "blob": b}) for r, _, b in matches),
            selected_ids=tuple(r for r, _, _ in selected),
            dropped_ids=tuple(r for r, _, _ in dropped),
            cache_identity=None,
            context_selection_digest=digest_of({"ids": [r for r, _, _ in selected], "texts": [t for _, t, _ in selected]}),
            redacted=False,
        )
        retrieval_payload = {"query": query, "provenance": provenance.digest(), "selected": provenance.selected_ids}
        retrieval_json = json.dumps({
            "query": query,
            "provenance": {
                "digest": provenance.digest(),
                "queryDigest": provenance.query_digest,
                "policyIdentity": provenance.policy_identity,
                "sourceRecordDigests": provenance.source_record_digests,
                "selectedIds": provenance.selected_ids,
                "droppedIds": provenance.dropped_ids,
                "cacheIdentity": provenance.cache_identity,
                "contextSelectionDigest": provenance.context_selection_digest,
                "redacted": provenance.redacted,
            },
        }, sort_keys=True)
        self._db.execute("BEGIN IMMEDIATE")
        try:
            ordinal = int(self._db.execute("SELECT COUNT(*) FROM memory_retrievals").fetchone()[0])
            retrieval_id = f"retrieval:{digest_of({'payload': retrieval_payload, 'ordinal': ordinal})[7:]}"
            self._db.execute(
                "INSERT INTO memory_retrievals VALUES(?,?,?,?,?,?)",
                (retrieval_id, access.tenant, access.project, self.category, retrieval_json, self._now()),
            )
            self._db.execute("COMMIT")
        except Exception:
            self._db.execute("ROLLBACK")
            raise
        return MemoryResult(tuple(r for r, _, _ in selected), provenance, tuple(text for _, text, _ in selected))

    def invalidate(self, record_id: str, access: MemoryAccess) -> None:
        self._authorized(access, self.category, "invalidate")
        self._record(record_id, access)
        self._db.execute("UPDATE memory_records SET invalidated=1 WHERE record_id=?", (record_id,))

    def set_legal_hold(self, record_id: str, access: MemoryAccess, enabled: bool = True) -> None:
        self._authorized(access, self.category, "retain")
        self._record(record_id, access)
        self._db.execute("UPDATE memory_records SET legal_hold=? WHERE record_id=?", (int(enabled), record_id))

    def quarantine(self, record_id: str, access: MemoryAccess) -> None:
        """Hide a suspect record without deleting its immutable blob."""
        self._authorized(access, self.category, "invalidate")
        self._record(record_id, access)
        self._db.execute(
            "UPDATE memory_records SET quarantined=1, quarantined_at=COALESCE(quarantined_at, ?) WHERE record_id=?",
            (self._now(), record_id),
        )

    def rebuild_index(self) -> int:
        """Rebuild the derived lexical index from durable record/blob truth."""
        self._db.execute("BEGIN IMMEDIATE")
        try:
            self._db.execute("DELETE FROM memory_terms")
            count = 0
            rows = self._db.execute("SELECT record_id, blob_digest FROM memory_records").fetchall()
            for row in rows:
                data = self._blobs.get(str(row["blob_digest"]))
                if not data.ok:
                    continue
                text = bytes(data.value).decode("utf-8")
                self._db.executemany("INSERT INTO memory_terms(record_id,term) VALUES(?,?)",
                                     ((row["record_id"], term) for term in self._terms(text)))
                count += 1
            self._db.execute("COMMIT")
            return count
        except Exception:
            self._db.execute("ROLLBACK")
            raise

    def gc(self, access: MemoryAccess, *, dry_run: bool = False, now: str | None = None) -> int:
        """Reviewed mark/sweep; legal holds and the quarantine interval dominate deletion."""
        self._authorized(access, self.category, "retain")
        at = now or self._now()
        threshold = None
        try:
            threshold = datetime.fromisoformat(at.replace("Z", "+00:00")).timestamp() - self._quarantine_seconds
        except ValueError as exc:
            raise ValueError("GC timestamp is invalid") from exc
        rows = self._db.execute(
            "SELECT record_id,blob_digest,quarantined_at FROM memory_records "
            "WHERE category=? AND tenant=? AND project=? AND invalidated=1 AND legal_hold=0",
            (self.category, access.tenant, access.project),
        ).fetchall()
        deletable = []
        for row in rows:
            if row["quarantined_at"]:
                try:
                    if datetime.fromisoformat(str(row["quarantined_at"]).replace("Z", "+00:00")).timestamp() > threshold:
                        continue
                except ValueError:
                    continue
            deletable.append(row)
        if not dry_run and deletable:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                self._db.executemany("DELETE FROM memory_records WHERE record_id=?", ((r["record_id"],) for r in deletable))
                self._db.execute("COMMIT")
            except Exception:
                self._db.execute("ROLLBACK")
                raise
        referenced = {str(row[0]) for row in self._db.execute("SELECT blob_digest FROM memory_records")}
        removed_blobs = 0
        for path in sorted((self._root / "blobs").glob("[0-9a-f][0-9a-f]/*")):
            digest = "sha256:" + path.parent.name + path.name
            if digest not in referenced and not dry_run:
                path.unlink(missing_ok=True)
                removed_blobs += 1
        receipt = {"category": self.category, "tenant": access.tenant, "project": access.project,
                   "dryRun": dry_run, "records": len(deletable), "blobs": removed_blobs, "at": at}
        self._db.execute(
            "INSERT INTO memory_gc_receipts VALUES(?,?,?,?,?,?,?,?)",
            (f"gc:{digest_of(receipt)[7:]}", self.category, access.tenant, access.project,
             int(dry_run), len(deletable), removed_blobs, at),
        )
        return len(deletable)

    def backup(self, destination: str | Path) -> Path:
        """Create a checksum-manifested, atomic copy of DB and CAS blobs."""
        destination = Path(destination)
        if destination.exists():
            raise FileExistsError(f"backup destination already exists: {destination}")
        parent = destination.parent
        parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{destination.name}.", dir=parent))
        try:
            self._db.execute("PRAGMA wal_checkpoint(FULL)")
            db_copy = staging / "memory.sqlite3"
            with sqlite3.connect(str(db_copy)) as target:
                self._db.backup(target)
            blobs_copy = staging / "blobs"
            if (self._root / "blobs").exists():
                shutil.copytree(self._root / "blobs", blobs_copy)
            db_digest = "sha256:" + hashlib.sha256(db_copy.read_bytes()).hexdigest()
            manifest = {"schemaVersion": self.SCHEMA_VERSION, "category": self.category,
                        "databaseDigest": db_digest,
                        "blobCount": sum(1 for p in blobs_copy.glob("[0-9a-f][0-9a-f]/*")) if blobs_copy.exists() else 0}
            (staging / "backup.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            os.replace(staging, destination)
            return destination
        except Exception:
            shutil.rmtree(staging, ignore_errors=True)
            raise

    @classmethod
    def restore_backup(cls, backup: str | Path, destination: str | Path, category: str, *, replace: bool = False) -> "DurableMemoryPort":
        """Verify a backup manifest/checksum before restoring it to a new store."""
        backup, destination = Path(backup), Path(destination)
        manifest_path = backup / "backup.json"
        db_source = backup / "memory.sqlite3"
        if not manifest_path.is_file() or not db_source.is_file():
            raise ValueError("memory backup is incomplete")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = str(manifest.get("databaseDigest", ""))
        actual = "sha256:" + hashlib.sha256(db_source.read_bytes()).hexdigest()
        if (expected != actual
                or int(manifest.get("schemaVersion", -1)) != cls.SCHEMA_VERSION
                or manifest.get("category") != category):
            raise ValueError("memory backup checksum or schema version is invalid")
        if destination.exists():
            if not replace:
                raise FileExistsError(f"restore destination already exists: {destination}")
            raise ValueError("destructive restore requires an explicit empty destination")
        staging = Path(tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent))
        try:
            shutil.copy2(db_source, staging / "memory.sqlite3")
            if (backup / "blobs").exists():
                shutil.copytree(backup / "blobs", staging / "blobs")
            os.replace(staging, destination)
            return cls(destination, category)
        except Exception:
            shutil.rmtree(staging, ignore_errors=True)
            raise

    restore_from_backup = restore_backup

    def health(self) -> dict[str, Any]:
        """Return a non-authorizing durability/index status snapshot."""
        integrity = str(self._db.execute("PRAGMA integrity_check").fetchone()[0])
        return {"schema_version": self.SCHEMA_VERSION, "journal_mode": "wal",
                "integrity": integrity, "index_records": int(self._db.execute("SELECT COUNT(*) FROM memory_terms").fetchone()[0]),
                "quarantined_records": int(self._db.execute("SELECT COUNT(*) FROM memory_records WHERE quarantined=1").fetchone()[0])}

    def close(self) -> None:
        self._db.close()
