"""SQLite + FTS5 Fact Graph and Universal Repository Intelligence Storage."""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .ir import (
    ConfidenceTier,
    EntityKind,
    IRDocSection,
    IRDocument,
    IREntity,
    IRRelation,
    IRSymbol,
    RelationKind,
)


class FactGraphStorage:
    """Embedded SQLite and FTS5 fact store for repository intelligence."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._con: Optional[sqlite3.Connection] = None
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        if self._con is None:
            self._con = sqlite3.connect(str(self.db_path), timeout=30.0)
            self._con.row_factory = sqlite3.Row
            self._con.execute("PRAGMA journal_mode=WAL")
            self._con.execute("PRAGMA synchronous=NORMAL")
            self._con.execute("PRAGMA foreign_keys=ON")
        return self._con

    def close(self):
        if self._con is not None:
            try:
                self._con.close()
            except Exception:
                pass
            self._con = None

    def _init_db(self):
        con = self.get_connection()
        with con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS repositories (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                root_path TEXT NOT NULL,
                metadata_json TEXT DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS files (
                path TEXT PRIMARY KEY,
                repo_id TEXT NOT NULL,
                language TEXT,
                content_hash TEXT NOT NULL,
                mtime REAL NOT NULL,
                size_bytes INTEGER NOT NULL,
                git_blob_sha TEXT,
                updated_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                repo_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                name TEXT NOT NULL,
                locator TEXT NOT NULL,
                authority TEXT,
                confidence_tier INTEGER NOT NULL,
                metadata_json TEXT DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS symbols (
                id TEXT PRIMARY KEY,
                entity_id TEXT NOT NULL,
                name TEXT NOT NULL,
                qualified_name TEXT NOT NULL,
                kind TEXT NOT NULL,
                language TEXT NOT NULL,
                file_path TEXT NOT NULL,
                signature TEXT,
                docstring TEXT,
                start_line INTEGER DEFAULT 1,
                end_line INTEGER DEFAULT 1,
                metadata_json TEXT DEFAULT '{}',
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                entity_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                title TEXT NOT NULL,
                canonical_id TEXT,
                authority TEXT,
                summary TEXT,
                estimated_tokens INTEGER DEFAULT 0,
                metadata_json TEXT DEFAULT '{}',
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS doc_sections (
                id TEXT PRIMARY KEY,
                doc_id TEXT NOT NULL,
                heading TEXT NOT NULL,
                level INTEGER NOT NULL,
                anchor TEXT NOT NULL,
                content TEXT NOT NULL,
                estimated_tokens INTEGER DEFAULT 0,
                start_line INTEGER DEFAULT 1,
                end_line INTEGER DEFAULT 1,
                FOREIGN KEY (doc_id) REFERENCES documents(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS relations (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                confidence_tier INTEGER NOT NULL,
                evidence TEXT,
                source_path TEXT,
                location_json TEXT
            );

            CREATE TABLE IF NOT EXISTS index_runs (
                id TEXT PRIMARY KEY,
                repo_id TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                files_indexed INTEGER NOT NULL,
                symbols_found INTEGER NOT NULL,
                relations_found INTEGER NOT NULL,
                is_incremental INTEGER DEFAULT 0,
                indexer_version TEXT NOT NULL
            );

            -- Indexes for high-speed relational queries
            CREATE INDEX IF NOT EXISTS idx_files_hash ON files(content_hash);
            CREATE INDEX IF NOT EXISTS idx_entities_kind ON entities(kind);
            CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name);
            CREATE INDEX IF NOT EXISTS idx_symbols_qual ON symbols(qualified_name);
            CREATE INDEX IF NOT EXISTS idx_symbols_file ON symbols(file_path);
            CREATE INDEX IF NOT EXISTS idx_docs_path ON documents(file_path);
            CREATE INDEX IF NOT EXISTS idx_docs_canon ON documents(canonical_id);
            CREATE INDEX IF NOT EXISTS idx_doc_sec_doc ON doc_sections(doc_id);
            CREATE INDEX IF NOT EXISTS idx_rel_src ON relations(source_id);
            CREATE INDEX IF NOT EXISTS idx_rel_tgt ON relations(target_id);
            CREATE INDEX IF NOT EXISTS idx_rel_kind ON relations(kind);
            CREATE INDEX IF NOT EXISTS idx_rel_src_tgt ON relations(source_id, target_id, kind);
            """)

            # Create FTS5 virtual table for full-text keyword retrieval
            try:
                con.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS fts_search USING fts5(
                    entity_id UNINDEXED,
                    title,
                    name,
                    content,
                    kind UNINDEXED,
                    locator UNINDEXED,
                    tokenize='porter unicode61'
                );
                """)
            except sqlite3.OperationalError:
                pass

    # --------------------------------------------------------------------------
    # Incremental File State Management
    # --------------------------------------------------------------------------
    def get_file_state(self, path: str) -> Optional[Dict[str, Any]]:
        con = self.get_connection()
        cur = con.execute(
            "SELECT path, content_hash, mtime, size_bytes, git_blob_sha FROM files WHERE path = ?",
            (path,)
        )
        row = cur.fetchone()
        if row:
            return dict(row)
        return None

    def get_all_file_states(self) -> Dict[str, Dict[str, Any]]:
        con = self.get_connection()
        cur = con.execute("SELECT path, content_hash, mtime, size_bytes, git_blob_sha FROM files")
        return {r["path"]: dict(r) for r in cur.fetchall()}

    def record_file(self, repo_id: str, path: str, language: str, content_hash: str, mtime: float, size_bytes: int, git_blob_sha: Optional[str] = None):
        con = self.get_connection()
        with con:
            con.execute(
                """
                INSERT INTO files (path, repo_id, language, content_hash, mtime, size_bytes, git_blob_sha, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    repo_id=excluded.repo_id,
                    language=excluded.language,
                    content_hash=excluded.content_hash,
                    mtime=excluded.mtime,
                    size_bytes=excluded.size_bytes,
                    git_blob_sha=excluded.git_blob_sha,
                    updated_at=excluded.updated_at
                """,
                (path, repo_id, language, content_hash, mtime, size_bytes, git_blob_sha, time.time())
            )

    def delete_file_facts(self, path: str):
        """Cleanly purge all facts originating from a modified or deleted file."""
        con = self.get_connection()
        with con:
            con.execute("DELETE FROM files WHERE path = ?", (path,))
            
            # Find entities located at this path
            cur = con.execute("SELECT id FROM entities WHERE locator LIKE ? OR locator = ?", (f"{path}%", path))
            entity_ids = [r["id"] for r in cur.fetchall()]

            if entity_ids:
                placeholders = ",".join("?" for _ in entity_ids)
                con.execute(f"DELETE FROM symbols WHERE entity_id IN ({placeholders})", entity_ids)
                
                # Find documents
                d_cur = con.execute(f"SELECT id FROM documents WHERE entity_id IN ({placeholders})", entity_ids)
                doc_ids = [r["id"] for r in d_cur.fetchall()]
                if doc_ids:
                    d_placeholders = ",".join("?" for _ in doc_ids)
                    con.execute(f"DELETE FROM doc_sections WHERE doc_id IN ({d_placeholders})", doc_ids)
                    con.execute(f"DELETE FROM documents WHERE id IN ({d_placeholders})", doc_ids)

                con.execute(f"DELETE FROM relations WHERE source_id IN ({placeholders}) OR target_id IN ({placeholders})", entity_ids + entity_ids)
                con.execute(f"DELETE FROM entities WHERE id IN ({placeholders})", entity_ids)
                
                try:
                    con.execute(f"DELETE FROM fts_search WHERE entity_id IN ({placeholders})", entity_ids)
                except Exception:
                    pass

            # Section-level FTS rows carry the file path inside the locator
            # (entity_id is the section id, which may no longer be resolvable
            # above), so purge them by locator prefix.
            try:
                con.execute("DELETE FROM fts_search WHERE locator LIKE ?", (f"{path}%",))
            except Exception:
                pass

            con.execute("DELETE FROM relations WHERE source_path = ?", (path,))

    # --------------------------------------------------------------------------
    # Insertion APIs
    # --------------------------------------------------------------------------
    def insert_entity(self, entity: IREntity):
        con = self.get_connection()
        with con:
            kind_value = entity.kind.value if isinstance(entity.kind, EntityKind) else str(entity.kind)
            con.execute(
                """
                INSERT INTO entities (id, repo_id, kind, name, locator, authority, confidence_tier, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    kind=excluded.kind,
                    name=excluded.name,
                    locator=excluded.locator,
                    authority=excluded.authority,
                    confidence_tier=excluded.confidence_tier,
                    metadata_json=excluded.metadata_json
                """,
                (
                    entity.id,
                    "default",
                    kind_value,
                    entity.name,
                    entity.locator,
                    entity.authority,
                    int(entity.provenance.confidence_tier),
                    json.dumps(entity.metadata or {})
                )
            )
            # Index into FTS5 (same normalized kind value as the entities table:
            # rankers branch on literal kinds like "symbol"/"document")
            try:
                con.execute(
                    "INSERT INTO fts_search (entity_id, title, name, content, kind, locator) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.id, entity.name, entity.name, json.dumps(entity.metadata or {}), kind_value, entity.locator)
                )
            except Exception:
                pass

    def insert_symbol(self, symbol: IRSymbol):
        con = self.get_connection()
        with con:
            loc = symbol.location
            s_line = loc.start_line if loc else 1
            e_line = loc.end_line if loc else 1
            con.execute(
                """
                INSERT INTO symbols (id, entity_id, name, qualified_name, kind, language, file_path, signature, docstring, start_line, end_line, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    entity_id=excluded.entity_id,
                    name=excluded.name,
                    qualified_name=excluded.qualified_name,
                    kind=excluded.kind,
                    language=excluded.language,
                    file_path=excluded.file_path,
                    signature=excluded.signature,
                    docstring=excluded.docstring,
                    start_line=excluded.start_line,
                    end_line=excluded.end_line,
                    metadata_json=excluded.metadata_json
                """,
                (
                    symbol.symbol_id,
                    symbol.symbol_id,
                    symbol.name,
                    symbol.qualified_name,
                    symbol.kind,
                    symbol.language,
                    symbol.file_path,
                    symbol.signature or "",
                    symbol.docstring or "",
                    s_line,
                    e_line,
                    json.dumps(symbol.metadata or {})
                )
            )
            try:
                content = f"{symbol.signature or ''} {symbol.docstring or ''}"
                con.execute(
                    "INSERT INTO fts_search (entity_id, title, name, content, kind, locator) VALUES (?, ?, ?, ?, ?, ?)",
                    (symbol.symbol_id, symbol.qualified_name, symbol.name, content, "symbol", f"{symbol.file_path}#L{s_line}")
                )
            except Exception:
                pass

    def insert_document(self, doc: IRDocument, sections: Optional[List[IRDocSection]] = None):
        con = self.get_connection()
        with con:
            con.execute(
                """
                INSERT INTO documents (id, entity_id, file_path, title, canonical_id, authority, summary, estimated_tokens, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    file_path=excluded.file_path,
                    title=excluded.title,
                    canonical_id=excluded.canonical_id,
                    authority=excluded.authority,
                    summary=excluded.summary,
                    estimated_tokens=excluded.estimated_tokens,
                    metadata_json=excluded.metadata_json
                """,
                (
                    doc.id,
                    doc.id,
                    doc.file_path,
                    doc.title,
                    doc.canonical_id,
                    doc.authority,
                    doc.summary or "",
                    doc.estimated_tokens,
                    json.dumps(doc.metadata or {})
                )
            )
            if sections:
                for sec in sections:
                    con.execute(
                        """
                        INSERT INTO doc_sections (id, doc_id, heading, level, anchor, content, estimated_tokens, start_line, end_line)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            heading=excluded.heading,
                            level=excluded.level,
                            anchor=excluded.anchor,
                            content=excluded.content,
                            estimated_tokens=excluded.estimated_tokens,
                            start_line=excluded.start_line,
                            end_line=excluded.end_line
                        """,
                        (
                            sec.id,
                            doc.id,
                            sec.heading,
                            sec.level,
                            sec.anchor,
                            sec.content,
                            sec.estimated_tokens,
                            sec.start_line,
                            sec.end_line
                        )
                    )
            try:
                con.execute(
                    "INSERT INTO fts_search (entity_id, title, name, content, kind, locator) VALUES (?, ?, ?, ?, ?, ?)",
                    (doc.id, doc.title, doc.canonical_id or doc.title, doc.summary or "", "document", doc.file_path)
                )
                # Section-level FTS: agents zoom into matching sections, not
                # whole documents. entity_id is the section id (joinable to
                # doc_sections); locator carries the file path for incremental
                # purge and provenance.
                for sec in sections:
                    if not sec.content:
                        continue
                    con.execute(
                        "INSERT INTO fts_search (entity_id, title, name, content, kind, locator) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            sec.id,
                            sec.heading,
                            sec.heading,
                            sec.content,
                            "doc_section",
                            f"{doc.file_path}#L{sec.start_line}-L{sec.end_line}",
                        )
                    )
            except Exception:
                pass

    def insert_relation(self, rel: IRRelation):
        con = self.get_connection()
        with con:
            loc_str = json.dumps(rel.location.to_reference()) if rel.location else None
            con.execute(
                """
                INSERT INTO relations (id, source_id, target_id, kind, confidence_tier, evidence, source_path, location_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    confidence_tier=excluded.confidence_tier,
                    evidence=excluded.evidence,
                    source_path=excluded.source_path,
                    location_json=excluded.location_json
                """,
                (
                    rel.id,
                    rel.source_id,
                    rel.target_id,
                    rel.kind.value if isinstance(rel.kind, RelationKind) else str(rel.kind),
                    int(rel.confidence_tier),
                    rel.evidence,
                    rel.source_path,
                    loc_str
                )
            )

    # --------------------------------------------------------------------------
    # Query & Retrieval APIs
    # --------------------------------------------------------------------------
    def search_fts(self, query: str, limit: int = 30) -> List[Dict[str, Any]]:
        con = self.get_connection()
        # Sanitize terms: hyphens, dots, and other punctuation are FTS5 MATCH
        # syntax characters and would raise (silently degrading to a useless
        # LIKE fallback). Strip them, then build an OR-of-prefixes expression.
        terms = [
            cleaned
            for cleaned in (
                "".join(ch for ch in t if ch.isalnum() or ch == "_")
                for t in query.replace('"', "").replace("'", "").split()
            )
            if len(cleaned) > 1
        ]
        if not terms:
            return []
        match_expr = " OR ".join(f"\"{t}\"*" for t in terms)
        
        try:
            cur = con.execute(
                """
                SELECT entity_id, title, name, kind, locator, rank
                FROM fts_search
                WHERE fts_search MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (match_expr, limit)
            )
            return [dict(r) for r in cur.fetchall()]
        except Exception:
            # Fallback to standard LIKE
            pat = f"%{query}%"
            cur = con.execute(
                """
                SELECT id as entity_id, name as title, name, kind, locator, 1.0 as rank
                FROM entities
                WHERE name LIKE ? OR locator LIKE ?
                LIMIT ?
                """,
                (pat, pat, limit)
            )
            return [dict(r) for r in cur.fetchall()]

    def get_symbol(self, query: str) -> List[Dict[str, Any]]:
        con = self.get_connection()
        cur = con.execute(
            """
            SELECT s.*, e.authority, e.confidence_tier
            FROM symbols s
            JOIN entities e ON s.entity_id = e.id
            WHERE s.id = ? OR s.name = ? OR s.qualified_name LIKE ?
            """,
            (query, query, f"%{query}")
        )
        return [dict(r) for r in cur.fetchall()]

    def get_callers(self, symbol_id: str) -> List[Dict[str, Any]]:
        con = self.get_connection()
        cur = con.execute(
            """
            SELECT r.id as relation_id, r.source_id, r.kind, r.confidence_tier, r.evidence, r.source_path, r.location_json,
                   s.name as caller_name, s.qualified_name as caller_qualified, s.file_path, s.start_line
            FROM relations r
            LEFT JOIN symbols s ON r.source_id = s.id
            WHERE r.target_id = ? AND r.kind = 'calls'
            ORDER BY r.confidence_tier DESC
            """,
            (symbol_id,)
        )
        return [dict(r) for r in cur.fetchall()]

    def get_callees(self, symbol_id: str) -> List[Dict[str, Any]]:
        con = self.get_connection()
        cur = con.execute(
            """
            SELECT r.id as relation_id, r.target_id, r.kind, r.confidence_tier, r.evidence, r.source_path,
                   s.name as callee_name, s.qualified_name as callee_qualified, s.file_path, s.start_line
            FROM relations r
            LEFT JOIN symbols s ON r.target_id = s.id
            WHERE r.source_id = ? AND r.kind = 'calls'
            ORDER BY r.confidence_tier DESC
            """,
            (symbol_id,)
        )
        return [dict(r) for r in cur.fetchall()]

    def get_references(self, symbol_id: str) -> List[Dict[str, Any]]:
        con = self.get_connection()
        cur = con.execute(
            """
            SELECT r.*, e.name as referencer_name, e.locator as referencer_locator
            FROM relations r
            LEFT JOIN entities e ON r.source_id = e.id
            WHERE r.target_id = ? AND r.kind IN ('references', 'imports', 'calls')
            ORDER BY r.confidence_tier DESC
            """,
            (symbol_id,)
        )
        return [dict(r) for r in cur.fetchall()]

    def get_tests_for_symbol(self, symbol_id: str) -> List[Dict[str, Any]]:
        con = self.get_connection()
        cur = con.execute(
            """
            SELECT r.*, e.name as test_name, e.locator as test_locator
            FROM relations r
            JOIN entities e ON r.source_id = e.id
            WHERE r.target_id = ? AND r.kind = 'tests'
            """,
            (symbol_id,)
        )
        return [dict(r) for r in cur.fetchall()]

    def get_docs_for_symbol(self, symbol_id: str) -> List[Dict[str, Any]]:
        con = self.get_connection()
        cur = con.execute(
            """
            SELECT r.*, d.title, d.file_path, d.canonical_id, d.authority
            FROM relations r
            JOIN documents d ON r.source_id = d.id
            WHERE r.target_id = ? AND r.kind IN ('documents', 'specified_by')
            """,
            (symbol_id,)
        )
        return [dict(r) for r in cur.fetchall()]

    def search_sections(self, query: str, limit: int = 15) -> List[Dict[str, Any]]:
        """BM25 search over document *section* content (not just metadata).

        Returns section rows joined with their parent document's file path and
        authority so rankers can build zoomed, provenance-bound candidates.
        """
        con = self.get_connection()
        terms = [
            cleaned
            for cleaned in (
                "".join(ch for ch in t if ch.isalnum() or ch == "_")
                for t in query.replace('"', "").replace("'", "").split()
            )
            if len(cleaned) > 1
        ]
        if not terms:
            return []
        match_expr = " OR ".join(f'"{t}"*' for t in terms)
        try:
            cur = con.execute(
                """
                SELECT f.entity_id AS section_id, f.title AS heading, f.locator AS locator,
                       f.rank AS rank,
                       d.id AS doc_id, d.file_path AS file_path, d.title AS doc_title,
                       d.authority AS authority, d.canonical_id AS canonical_id,
                       s.content AS content, s.estimated_tokens AS estimated_tokens,
                       s.start_line AS start_line, s.end_line AS end_line
                FROM fts_search f
                JOIN doc_sections s ON s.id = f.entity_id
                JOIN documents d ON d.id = s.doc_id
                WHERE f.kind = 'doc_section' AND fts_search MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (match_expr, limit)
            )
            return [dict(r) for r in cur.fetchall()]
        except Exception:
            return []

    def get_all_sections(self) -> List[Dict[str, Any]]:
        """All document sections with parent file paths (dense indexing source)."""
        con = self.get_connection()
        cur = con.execute(
            """
            SELECT s.id, s.heading, s.content, s.estimated_tokens,
                   s.start_line, s.end_line, d.file_path, d.authority
            FROM doc_sections s
            JOIN documents d ON d.id = s.doc_id
            """
        )
        return [dict(r) for r in cur.fetchall()]

    def get_file_symbols(self, file_path: str) -> List[Dict[str, Any]]:
        con = self.get_connection()
        cur = con.execute(
            "SELECT * FROM symbols WHERE file_path = ? ORDER BY start_line",
            (file_path,)
        )
        return [dict(r) for r in cur.fetchall()]

    def get_all_symbols(self) -> List[Dict[str, Any]]:
        con = self.get_connection()
        cur = con.execute("SELECT * FROM symbols")
        return [dict(r) for r in cur.fetchall()]

    def get_all_relations(self) -> List[Dict[str, Any]]:
        con = self.get_connection()
        cur = con.execute("SELECT * FROM relations")
        return [dict(r) for r in cur.fetchall()]

    def get_topology_map(self) -> Dict[str, Any]:
        con = self.get_connection()
        cur = con.execute("SELECT language, COUNT(*) as file_count, SUM(size_bytes) as total_bytes FROM files GROUP BY language")
        lang_stats = [dict(r) for r in cur.fetchall()]

        cur2 = con.execute("SELECT kind, COUNT(*) as count FROM entities GROUP BY kind")
        entity_stats = [dict(r) for r in cur2.fetchall()]

        cur3 = con.execute("SELECT kind, COUNT(*) as count FROM relations GROUP BY kind")
        relation_stats = [dict(r) for r in cur3.fetchall()]

        return {
            "languages": lang_stats,
            "entities": entity_stats,
            "relations": relation_stats
        }

    def get_stats(self) -> Dict[str, Any]:
        con = self.get_connection()
        files = con.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        entities = con.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        symbols = con.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
        docs = con.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        relations = con.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
        return {
            "files": files,
            "entities": entities,
            "symbols": symbols,
            "documents": docs,
            "relations": relations
        }
# --------------------------------------------------------------------------
    # Hygiene & coverage diagnostics (used by `lda check` / healthcheck)
    # --------------------------------------------------------------------------

    def purge_all(self) -> None:
        """Wipe every indexed fact. Used by `lda index --rebuild` so stale rows
        (e.g. entities whose files were deleted) cannot leak into search."""
        con = self.get_connection()
        with con:
            try:
                con.execute("DELETE FROM fts_search")
            except Exception:
                pass
            con.execute("DELETE FROM doc_sections")
            con.execute("DELETE FROM documents")
            con.execute("DELETE FROM symbols")
            con.execute("DELETE FROM relations")
            con.execute("DELETE FROM entities")
            con.execute("DELETE FROM files")
            con.execute("DELETE FROM index_runs")

    def coverage_by_language(self) -> Dict[str, Any]:
        """Per-language file, symbol, and relation counts for the fact graph."""
        con = self.get_connection()
        files: Dict[str, int] = {r["language"]: r["n"] for r in con.execute(
            "SELECT language, COUNT(*) AS n FROM files GROUP BY language ORDER BY n DESC")}
        symbols: Dict[str, int] = {r["language"]: r["n"] for r in con.execute(
            "SELECT language, COUNT(*) AS n FROM symbols GROUP BY language ORDER BY n DESC")}
        relations: Dict[str, int] = {r["kind"]: r["n"] for r in con.execute(
            "SELECT kind, COUNT(*) AS n FROM relations GROUP BY kind ORDER BY n DESC")}
        return {"files": files, "symbols": symbols, "relations": relations}

    def count_orphan_fts(self) -> int:
        """FTS rows whose entity no longer exists (set, not text, table)."""
        con = self.get_connection()
        try:
            return int(con.execute(
                "SELECT COUNT(*) FROM fts_search WHERE entity_id NOT IN (SELECT id FROM entities)"
            ).fetchone()[0])
        except Exception:
            return -1

    def sample_symbol_paths(self, limit: int = 300) -> tuple[str, ...]:
        con = self.get_connection()
        rows = con.execute(
            "SELECT file_path FROM symbols GROUP BY file_path LIMIT ?", (limit,)).fetchall()
        return tuple(str(r[0]) for r in rows)

    def record_index_run(self, *, files: int, symbols: int, relations: int, incremental: bool) -> None:
        import time as _time

        con = self.get_connection()
        id_ = f"idx-{_time.time_ns()}"
        with con:
            con.execute(
                "INSERT INTO index_runs (id, repo_id, started_at, completed_at, files_indexed, symbols_found, relations_found, is_incremental, indexer_version) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (id_, "default", str(_time.time()), str(_time.time()), int(files), int(symbols), int(relations), int(incremental), "1.0.0"),
            )

    def latest_index_run(self) -> Optional[Dict[str, Any]]:
        con = self.get_connection()
        rows = con.execute(
            "SELECT * FROM index_runs ORDER BY started_at DESC LIMIT 1").fetchall()
        return dict(rows[0]) if rows else None
