"""LDA-backed repository index adapter (T-75 / IDX-01 / S10-A-03).

Structural adapter over `.lda/index.db` implementing `IndexPort`.
Returns value-only symbols, dependency edges, callers, and test associations.
Missing or stale indexes fail deterministically without a partial map (preserving T-45 fallback).
Ranking never enters the port or adapter.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path
import sqlite3
from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of
from ...ports.event_store import Result
from ...ports.index import (
    DependencyEdge,
    IndexPort,
    RepositoryMap,
    Symbol,
    TestAssociation,
)

__all__ = ["LdaRepoIndex"]

_IGNORED = {
    ".git", ".vanguard", ".pytest_cache", "__pycache__", "node_modules",
    ".venv", "dist", "build", ".cursor", ".lda",
}


def _query_path(value: str) -> str:
    if value == "":
        return ""
    candidate = Path(value.replace("\\", "/"))
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"path query must be workspace-relative: {value!r}")
    return candidate.as_posix()


def _read_head_sha(root: Path) -> str | None:
    """Read resolved git HEAD commit SHA in pure Python without subprocess."""
    git_dir = root / ".git"
    if not git_dir.exists():
        return None
    try:
        if git_dir.is_file():
            content = git_dir.read_text(encoding="utf-8").strip()
            if content.startswith("gitdir:"):
                actual = content[7:].strip()
                git_dir = (root / actual).resolve()
        head_file = git_dir / "HEAD"
        if not head_file.is_file():
            return None
        ref = head_file.read_text(encoding="utf-8").strip()
        if not ref.startswith("ref:"):
            return ref if len(ref) >= 40 else None
        ref_path = ref[4:].strip()
        target = git_dir / ref_path
        if target.is_file():
            return target.read_text(encoding="utf-8").strip()
        packed = git_dir / "packed-refs"
        if packed.is_file():
            for line in packed.read_text(encoding="utf-8").splitlines():
                if line.startswith(("#", "^")):
                    continue
                parts = line.split()
                if len(parts) == 2 and parts[1] == ref_path:
                    return parts[0]
    except OSError:
        return None
    return None


def _hashed_tree(content_digests: Mapping[str, str]) -> str:
    return digest_of({"tree": dict(sorted(content_digests.items()))})


def _index_snapshot_digest(
    files: Sequence[str],
    symbols: Sequence[Symbol],
    dependencies: Sequence[DependencyEdge],
    tests: Sequence[TestAssociation],
) -> str:
    return digest_of({
        "files": list(files),
        "symbols": [{"name": item.name, "kind": item.kind, "path": item.path, "line": item.line}
                    for item in symbols],
        "dependencies": [{"source": item.source, "target": item.target, "kind": item.kind}
                         for item in dependencies],
        "tests": [{"testPath": item.test_path, "sourcePath": item.source_path} for item in tests],
    })


def _bounded_map(files: Sequence[str], symbols: Sequence[Symbol],
                 dependencies: Sequence[DependencyEdge], tests: Sequence[TestAssociation],
                 adapter_id: str, revision: str, token_budget: int,
                 tree_hash: str, index_digest: str) -> RepositoryMap:
    capacity = token_budget * 4
    used = 0
    kept_files: list[str] = []
    for path in files:
        cost = len(path) + 1
        if used + cost > capacity:
            break
        kept_files.append(path)
        used += cost
    kept_symbols = tuple(symbols[:max(0, capacity - used) // 12])
    used += sum(len(item.name) + len(item.path) + 8 for item in kept_symbols)
    kept_edges = tuple(dependencies[:max(0, capacity - used) // 16])
    used += sum(len(item.source) + len(item.target) + 8 for item in kept_edges)
    kept_tests = tuple(tests[:max(0, capacity - used) // 16])
    truncated = (len(kept_files) < len(files) or len(kept_symbols) < len(symbols)
                 or len(kept_edges) < len(dependencies) or len(kept_tests) < len(tests))
    return RepositoryMap(tuple(kept_files), kept_symbols, kept_edges, kept_tests,
                         adapter_id, revision, truncated=truncated,
                         token_estimate=max(1, used // 4) if used else 0,
                         tree_hash=tree_hash, index_digest=index_digest)


def _live_content_digests(root: Path, *, max_files: int) -> dict[str, str] | None:
    try:
        base = root.resolve()
    except OSError:
        return None
    if not base.is_dir():
        return None
    digests: dict[str, str] = {}
    for path in sorted(base.rglob("*")):
        if set(path.parts) & _IGNORED:
            continue
        if path.is_symlink():
            try:
                resolved = path.resolve()
                if not resolved.is_relative_to(base):
                    return None
            except OSError:
                return None
            continue
        if not path.is_file():
            continue
        if len(digests) >= max_files:
            break
        relative = path.relative_to(base).as_posix()
        try:
            digests[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            continue
    return digests


class LdaRepoIndex:
    """IndexPort adapter backed by `.lda/index.db`.
    
    Adheres strictly to the IndexPort protocol. Fails deterministically if
    the database is missing or stale without serving an incomplete or empty map.
    """

    def __init__(
        self,
        root: str | Path | None = None,
        *,
        db_path: str | Path | None = None,
        max_files: int = 10_000,
        max_symbols: int = 20_000,
        max_edges: int = 20_000,
        max_tests: int = 20_000,
    ) -> None:
        if any(v <= 0 for v in (max_files, max_symbols, max_edges, max_tests)):
            raise ValueError("index limits must be positive integers")
        self.max_files = max_files
        self.max_symbols = max_symbols
        self.max_edges = max_edges
        self.max_tests = max_tests
        self._root: Path | None = Path(root).resolve() if root is not None else None
        self._db_path: Path | None = Path(db_path).resolve() if db_path is not None else (
            self._root / ".lda" / "index.db" if self._root is not None else None
        )
        self._files: tuple[str, ...] = ()
        self._symbols: tuple[Symbol, ...] = ()
        self._dependencies: tuple[DependencyEdge, ...] = ()
        self._tests: tuple[TestAssociation, ...] = ()
        self._revision: str = ""
        self._indexed_tree_hash: str = ""

        if self._root is not None:
            self.index(str(self._root))

    def _connect(self) -> sqlite3.Connection | None:
        if self._db_path is None or not self._db_path.is_file():
            return None
        try:
            uri = f"file:{self._db_path.as_posix()}?mode=ro"
            con = sqlite3.connect(uri, uri=True)
            return con
        except sqlite3.Error:
            try:
                con = sqlite3.connect(str(self._db_path))
                return con
            except sqlite3.Error:
                return None

    def _verify_freshness(self) -> Result[sqlite3.Connection]:
        """Verify database existence, schema completeness, and git HEAD binding."""
        if self._root is None:
            return Result.fail("invalid_request", "index() has not been called")
        if self._db_path is None or not self._db_path.is_file():
            return Result.fail("unavailable", f"no LDA index database found at {self._db_path}")

        con = self._connect()
        if con is None:
            return Result.fail("unavailable", f"cannot connect to LDA database at {self._db_path}")

        cur = con.cursor()
        try:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cur.fetchall()}
            required_tables = {"files", "symbols", "relations", "index_runs"}
            if not required_tables.issubset(tables):
                con.close()
                return Result.fail("stale_index", f"LDA database missing required tables: {required_tables - tables}")

            cur.execute("SELECT head_sha FROM index_runs ORDER BY completed_at DESC LIMIT 1")
            run_row = cur.fetchone()
            if run_row is None:
                con.close()
                return Result.fail("stale_index", "LDA index has no completed index runs")
            index_head = str(run_row[0] or "").strip()

            ws_head = _read_head_sha(self._root)
            if ws_head and index_head and ws_head != index_head:
                con.close()
                return Result.fail("stale_index", f"index HEAD {index_head} != git HEAD {ws_head}")

            cur.execute("SELECT count(*) FROM files")
            count_row = cur.fetchone()
            if count_row is None or count_row[0] == 0:
                con.close()
                return Result.fail("stale_index", "LDA database has 0 files indexed")

            return Result.success(con)
        except sqlite3.Error as exc:
            con.close()
            return Result.fail("unavailable", f"SQLite query error: {exc}")

    def index(self, root: str) -> Result[int]:
        """Validate and bind the LDA index for root."""
        base = Path(root).resolve()
        if not base.is_dir():
            return Result.fail("not_found", f"not a directory: {root}")
        self._root = base
        self._db_path = base / ".lda" / "index.db"

        verified = self._verify_freshness()
        if not verified.ok or verified.value is None:
            error = verified.error
            return Result.fail(error.kind if error else "unavailable",
                               error.message if error else "index validation failed")
        con = verified.value
        cur = con.cursor()
        try:
            cur.execute("SELECT path, content_hash FROM files ORDER BY path ASC LIMIT ?", (self.max_files,))
            file_rows = cur.fetchall()
            files = [row[0] for row in file_rows]
            content_digests = {row[0]: row[1] for row in file_rows}

            cur.execute(
                "SELECT name, kind, file_path, start_line FROM symbols "
                "ORDER BY file_path ASC, start_line ASC, name ASC LIMIT ?",
                (self.max_symbols,)
            )
            symbols = [Symbol(name=r[0], kind=r[1], path=r[2], line=r[3]) for r in cur.fetchall()]

            cur.execute(
                "SELECT DISTINCT source_path, target_id, kind FROM relations "
                "WHERE kind = 'imports' ORDER BY source_path ASC, target_id ASC LIMIT ?",
                (self.max_edges,)
            )
            dependencies = [DependencyEdge(source=r[0], target=r[1], kind=r[2]) for r in cur.fetchall()]

            cur.execute(
                """
                SELECT DISTINCT r.source_path, s.file_path
                FROM relations r
                JOIN symbols s ON r.target_id = s.id
                WHERE r.kind IN ('tests', 'falsifies')
                ORDER BY r.source_path ASC, s.file_path ASC
                LIMIT ?
                """,
                (self.max_tests,)
            )
            tests = [TestAssociation(test_path=r[0], source_path=r[1]) for r in cur.fetchall()]

            cur.execute("SELECT head_sha FROM index_runs ORDER BY completed_at DESC LIMIT 1")
            head_row = cur.fetchone()
            revision = head_row[0] if head_row and head_row[0] else "sha256:" + hashlib.sha256(b"").hexdigest()

            self._files = tuple(files)
            self._symbols = tuple(symbols)
            self._dependencies = tuple(dependencies)
            self._tests = tuple(tests)
            self._revision = revision
            self._indexed_tree_hash = _hashed_tree(content_digests)
            return Result.success(len(files))
        except sqlite3.Error as exc:
            return Result.fail("unavailable", f"failed reading index data: {exc}")
        finally:
            con.close()

    def files(self, *, prefix: str = "") -> Result[Sequence[str]]:
        verified = self._verify_freshness()
        if not verified.ok or verified.value is None:
            return Result.fail(verified.error.kind if verified.error else "unavailable",
                               verified.error.message if verified.error else "freshness failed")
        verified.value.close()
        try:
            prefix = _query_path(prefix)
        except ValueError as exc:
            return Result.fail("invalid_request", str(exc))
        return Result.success(tuple(p for p in self._files if p.startswith(prefix)))

    def symbols(self, *, name: str = "", path: str = "") -> Result[Sequence[Symbol]]:
        verified = self._verify_freshness()
        if not verified.ok or verified.value is None:
            return Result.fail(verified.error.kind if verified.error else "unavailable",
                               verified.error.message if verified.error else "freshness failed")
        con = verified.value
        cur = con.cursor()
        try:
            path = _query_path(path)
        except ValueError as exc:
            con.close()
            return Result.fail("invalid_request", str(exc))
        try:
            query = "SELECT name, kind, file_path, start_line FROM symbols WHERE 1=1"
            params: list[Any] = []
            if name:
                query += " AND (name = ? OR qualified_name = ?)"
                params.extend([name, name])
            if path:
                query += " AND file_path LIKE ?"
                params.append(f"{path}%")
            query += " ORDER BY file_path ASC, start_line ASC, name ASC LIMIT ?"
            params.append(self.max_symbols)
            cur.execute(query, params)
            results = [Symbol(name=r[0], kind=r[1], path=r[2], line=r[3]) for r in cur.fetchall()]
            return Result.success(tuple(results))
        except sqlite3.Error as exc:
            return Result.fail("unavailable", f"symbol query error: {exc}")
        finally:
            con.close()

    def callers(self, *, symbol: str = "") -> Result[Sequence[Symbol]]:
        verified = self._verify_freshness()
        if not verified.ok or verified.value is None:
            return Result.fail(verified.error.kind if verified.error else "unavailable",
                               verified.error.message if verified.error else "freshness failed")
        if not symbol:
            verified.value.close()
            return Result.success(())
        con = verified.value
        cur = con.cursor()
        try:
            sql = """
            SELECT DISTINCT s.name, s.kind, s.file_path, s.start_line
            FROM relations r
            JOIN symbols s ON r.source_id = s.id
            WHERE r.kind = 'calls' AND (
                r.target_id = ? OR r.target_id = ?
                OR r.target_id IN (SELECT id FROM symbols WHERE name = ? OR qualified_name = ?)
            )
            ORDER BY s.file_path ASC, s.start_line ASC, s.name ASC
            LIMIT ?
            """
            cur.execute(sql, (symbol, f"name:{symbol}", symbol, symbol, self.max_symbols))
            results = [Symbol(name=r[0], kind=r[1], path=r[2], line=r[3]) for r in cur.fetchall()]
            return Result.success(tuple(results))
        except sqlite3.Error as exc:
            return Result.fail("unavailable", f"callers query error: {exc}")
        finally:
            con.close()

    def get_callers(self, symbol: str) -> Result[Sequence[Symbol]]:
        return self.callers(symbol=symbol)

    def dependencies(self, *, path: str = "") -> Result[Sequence[DependencyEdge]]:
        verified = self._verify_freshness()
        if not verified.ok or verified.value is None:
            return Result.fail(verified.error.kind if verified.error else "unavailable",
                               verified.error.message if verified.error else "freshness failed")
        con = verified.value
        cur = con.cursor()
        try:
            path = _query_path(path)
        except ValueError as exc:
            con.close()
            return Result.fail("invalid_request", str(exc))
        try:
            sql = "SELECT DISTINCT source_path, target_id, kind FROM relations WHERE kind = 'imports'"
            params: list[Any] = []
            if path:
                sql += " AND source_path LIKE ?"
                params.append(f"{path}%")
            sql += " ORDER BY source_path ASC, target_id ASC LIMIT ?"
            params.append(self.max_edges)
            cur.execute(sql, params)
            results = [DependencyEdge(source=r[0], target=r[1], kind=r[2]) for r in cur.fetchall()]
            return Result.success(tuple(results))
        except sqlite3.Error as exc:
            return Result.fail("unavailable", f"dependencies query error: {exc}")
        finally:
            con.close()

    def tests(self, *, path: str = "") -> Result[Sequence[TestAssociation]]:
        verified = self._verify_freshness()
        if not verified.ok or verified.value is None:
            return Result.fail(verified.error.kind if verified.error else "unavailable",
                               verified.error.message if verified.error else "freshness failed")
        con = verified.value
        cur = con.cursor()
        try:
            path = _query_path(path)
        except ValueError as exc:
            con.close()
            return Result.fail("invalid_request", str(exc))
        try:
            sql = """
            SELECT DISTINCT r.source_path, s.file_path
            FROM relations r
            JOIN symbols s ON r.target_id = s.id
            WHERE r.kind IN ('tests', 'falsifies')
            """
            params: list[Any] = []
            if path:
                sql += " AND (r.source_path LIKE ? OR s.file_path LIKE ?)"
                params.extend([f"{path}%", f"{path}%"])
            sql += " ORDER BY r.source_path ASC, s.file_path ASC LIMIT ?"
            params.append(self.max_tests)
            cur.execute(sql, params)
            results = [TestAssociation(test_path=r[0], source_path=r[1]) for r in cur.fetchall()]
            return Result.success(tuple(results))
        except sqlite3.Error as exc:
            return Result.fail("unavailable", f"tests query error: {exc}")
        finally:
            con.close()

    def repo_map(self, *, token_budget: int = 4000) -> Result[RepositoryMap]:
        if self._root is None:
            return Result.fail("invalid_request", "index() has not been called")
        if token_budget < 0:
            return Result.fail("invalid_request", "token_budget must be non-negative")

        verified = self._verify_freshness()
        if not verified.ok or verified.value is None:
            return Result.fail(verified.error.kind if verified.error else "unavailable",
                               verified.error.message if verified.error else "freshness failed")
        verified.value.close()

        live = _live_content_digests(self._root, max_files=self.max_files)
        if live is None:
            return Result.fail("invalid_request", "tree hash unbound")
        tree_hash = _hashed_tree(live)
        index_digest = _index_snapshot_digest(
            self._files, self._symbols, self._dependencies, self._tests
        )
        if not tree_hash or not index_digest:
            return Result.fail("invalid_request", "WorkspaceEpoch digest unbound")
        mapped = _bounded_map(self._files, self._symbols, self._dependencies,
                              self._tests, "lda-repo-index/1", self._revision,
                              token_budget, tree_hash, index_digest)
        if self._indexed_tree_hash and tree_hash != self._indexed_tree_hash:
            mapped = replace(mapped, truncated=True)
        return Result.success(mapped)
