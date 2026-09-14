"""Contract tests for LdaRepoIndex (T-75 / IDX-01 / S10-A-03).

Verifies:
1. IndexPort protocol conformance.
2. Pure value objects returned (no ranked lists, no mutation).
3. Observation-only contract (A-05: no propose, rank, select, etc.).
4. Deterministic failure on missing database, missing tables, empty files, or stale git HEAD.
5. Callers, dependencies, tests, symbols, files, and repo_map queries.
"""

from __future__ import annotations

from pathlib import Path
import sqlite3
import tempfile
import unittest

from vanguard.packages.adapters.stores.lda_index import LdaRepoIndex
from vanguard.packages.ports.index import (
    DependencyEdge,
    IndexPort,
    RepositoryMap,
    Symbol,
    TestAssociation,
)


class TestLdaRepoIndexContract(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _create_sqlite_lda(
        self,
        *,
        head_sha: str = "deadbeefcafebabe000011112222333344445555",
        files: list[tuple[str, str]] | None = None,
        symbols: list[tuple[str, str, str, str, int, int]] | None = None,
        relations: list[tuple[str, str, str, str]] | None = None,
    ) -> Path:
        lda_dir = self.root / ".lda"
        lda_dir.mkdir(parents=True, exist_ok=True)
        db_path = lda_dir / "index.db"
        con = sqlite3.connect(str(db_path))
        cur = con.cursor()
        cur.executescript("""
            CREATE TABLE files (
                path TEXT PRIMARY KEY,
                content_hash TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                language TEXT NOT NULL,
                indexed_at TEXT NOT NULL
            );
            CREATE TABLE symbols (
                id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                name TEXT NOT NULL,
                qualified_name TEXT NOT NULL,
                kind TEXT NOT NULL,
                start_line INTEGER NOT NULL,
                end_line INTEGER NOT NULL,
                signature TEXT,
                docstring TEXT
            );
            CREATE TABLE relations (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                source_path TEXT NOT NULL,
                target_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                confidence REAL NOT NULL
            );
            CREATE TABLE index_runs (
                id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                head_sha TEXT NOT NULL,
                git_branch TEXT,
                files_indexed INTEGER NOT NULL,
                symbols_indexed INTEGER NOT NULL,
                relations_indexed INTEGER NOT NULL,
                duration_ms INTEGER NOT NULL,
                is_full INTEGER NOT NULL
            );
        """)

        # Mock git head
        git_dir = self.root / ".git"
        git_dir.mkdir(parents=True, exist_ok=True)
        (git_dir / "HEAD").write_text(head_sha, encoding="utf-8")

        # Insert index_run
        cur.execute(
            "INSERT INTO index_runs VALUES ('run1', '2026-09-01T00:00:00Z', '2026-09-01T00:01:00Z', ?, 'main', 10, 20, 30, 100, 1)",
            (head_sha,)
        )

        # Insert files
        file_list = files if files is not None else [("pkg/core.py", "hash1"), ("pkg/util.py", "hash2")]
        for p, h in file_list:
            (self.root / p).parent.mkdir(parents=True, exist_ok=True)
            (self.root / p).write_text("# content\n", encoding="utf-8")
            cur.execute(
                "INSERT INTO files VALUES (?, ?, 10, 'python', '2026-09-01T00:00:00Z')",
                (p, h)
            )

        # Insert symbols
        sym_list = symbols if symbols is not None else [
            ("s1", "pkg/core.py", "CoreService", "pkg.core.CoreService", "class", 10, 50),
            ("s2", "pkg/core.py", "execute", "pkg.core.CoreService.execute", "method", 20, 30),
            ("s3", "pkg/util.py", "helper", "pkg.util.helper", "function", 5, 15),
        ]
        for s_id, fp, name, qn, kind, sl, el in sym_list:
            cur.execute(
                "INSERT INTO symbols VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL)",
                (s_id, fp, name, qn, kind, sl, el)
            )

        # Insert relations
        rel_list = relations if relations is not None else [
            ("r1", "s2", "pkg/core.py", "s3", "calls"),
            ("r2", "s2", "pkg/core.py", "pkg/util.py", "imports"),
            ("r3", "tests/test_core.py", "tests/test_core.py", "s1", "tests"),
        ]
        for r_id, sid, sp, tid, kind in rel_list:
            cur.execute(
                "INSERT INTO relations VALUES (?, ?, ?, ?, ?, 1.0)",
                (r_id, sid, sp, tid, kind)
            )

        con.commit()
        con.close()
        return db_path

    def test_satisfies_index_port_protocol(self) -> None:
        self._create_sqlite_lda()
        index = LdaRepoIndex(self.root)
        self.assertIsInstance(index, IndexPort)

    def test_observation_only_contract(self) -> None:
        """A-05: it answers queries; it never proposes, ranks, or suggests."""
        index = LdaRepoIndex()
        for forbidden in ("propose", "rank", "select", "suggest", "dispatch", "execute"):
            self.assertFalse(hasattr(index, forbidden), f"{forbidden!r} violates observation-only contract")

    def test_missing_lda_database_fails_deterministically(self) -> None:
        index = LdaRepoIndex()
        result = index.index(str(self.root))
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "unavailable")

    def test_missing_required_tables_fails_deterministically(self) -> None:
        lda_dir = self.root / ".lda"
        lda_dir.mkdir(parents=True, exist_ok=True)
        db_path = lda_dir / "index.db"
        con = sqlite3.connect(str(db_path))
        con.execute("CREATE TABLE files (path TEXT PRIMARY KEY);")
        con.commit()
        con.close()

        index = LdaRepoIndex()
        result = index.index(str(self.root))
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "stale_index")

    def test_empty_files_table_fails_deterministically(self) -> None:
        self._create_sqlite_lda(files=[])
        index = LdaRepoIndex()
        result = index.index(str(self.root))
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "stale_index")

    def test_stale_git_head_fails_deterministically(self) -> None:
        self._create_sqlite_lda(head_sha="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        # Mutate git HEAD to something else
        (self.root / ".git" / "HEAD").write_text("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", encoding="utf-8")
        index = LdaRepoIndex()
        result = index.index(str(self.root))
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "stale_index")
        self.assertIn("index HEAD", result.error.message)

    def test_files_listing_and_filtering(self) -> None:
        self._create_sqlite_lda()
        index = LdaRepoIndex(self.root)
        files_res = index.files()
        self.assertTrue(files_res.ok)
        self.assertEqual(list(files_res.value), ["pkg/core.py", "pkg/util.py"])

        filtered = index.files(prefix="pkg/c")
        self.assertTrue(filtered.ok)
        self.assertEqual(list(filtered.value), ["pkg/core.py"])

    def test_symbols_query(self) -> None:
        self._create_sqlite_lda()
        index = LdaRepoIndex(self.root)
        all_syms = index.symbols()
        self.assertTrue(all_syms.ok)
        self.assertEqual(len(all_syms.value), 3)

        by_name = index.symbols(name="CoreService")
        self.assertTrue(by_name.ok)
        self.assertEqual(len(by_name.value), 1)
        self.assertEqual(by_name.value[0].name, "CoreService")
        self.assertEqual(by_name.value[0].kind, "class")
        self.assertEqual(by_name.value[0].path, "pkg/core.py")
        self.assertEqual(by_name.value[0].line, 10)

        by_path = index.symbols(path="pkg/util.py")
        self.assertTrue(by_path.ok)
        self.assertEqual(len(by_path.value), 1)
        self.assertEqual(by_path.value[0].name, "helper")

    def test_callers_query(self) -> None:
        self._create_sqlite_lda()
        index = LdaRepoIndex(self.root)
        # s2 calls s3 ("helper")
        callers_res = index.callers(symbol="helper")
        self.assertTrue(callers_res.ok)
        self.assertEqual(len(callers_res.value), 1)
        self.assertEqual(callers_res.value[0].name, "execute")
        self.assertEqual(callers_res.value[0].path, "pkg/core.py")

        # get_callers alias
        alias_res = index.get_callers("helper")
        self.assertTrue(alias_res.ok)
        self.assertEqual(alias_res.value, callers_res.value)

        # non-existent symbol returns empty tuple
        empty_res = index.callers(symbol="nonexistent")
        self.assertTrue(empty_res.ok)
        self.assertEqual(empty_res.value, ())

    def test_dependencies_and_tests_query(self) -> None:
        self._create_sqlite_lda()
        index = LdaRepoIndex(self.root)

        deps_res = index.dependencies()
        self.assertTrue(deps_res.ok)
        self.assertEqual(len(deps_res.value), 1)
        self.assertEqual(deps_res.value[0].source, "pkg/core.py")
        self.assertEqual(deps_res.value[0].target, "pkg/util.py")

        tests_res = index.tests()
        self.assertTrue(tests_res.ok)
        self.assertEqual(len(tests_res.value), 1)
        self.assertEqual(tests_res.value[0].test_path, "tests/test_core.py")
        self.assertEqual(tests_res.value[0].source_path, "pkg/core.py")

    def test_repo_map_bounded_digest(self) -> None:
        self._create_sqlite_lda()
        index = LdaRepoIndex(self.root)
        repomap_res = index.repo_map(token_budget=1000)
        self.assertTrue(repomap_res.ok)
        repomap = repomap_res.value
        self.assertIsInstance(repomap, RepositoryMap)
        self.assertEqual(repomap.adapter_id, "lda-repo-index/1")
        self.assertEqual(repomap.files, ("pkg/core.py", "pkg/util.py"))
        self.assertTrue(repomap.tree_hash.startswith("sha256:"))
        self.assertTrue(repomap.index_digest.startswith("sha256:"))

    def test_real_workspace_lda_database(self) -> None:
        """Verify LdaRepoIndex against the actual cognitive-framework repo .lda/index.db."""
        real_root = Path.cwd()
        lda_db = real_root / ".lda" / "index.db"
        if not lda_db.is_file():
            self.skipTest("No .lda/index.db found in current repository")

        index = LdaRepoIndex(real_root)
        files = index.files()
        if not files.ok:
            # If repo index is stale compared to git HEAD, it should fail with stale_index
            self.assertIn(files.error.kind, ("stale_index", "unavailable"))
            return

        self.assertTrue(files.ok)
        self.assertGreater(len(files.value), 100)

        syms = index.symbols(name="LdaRepoIndex")
        self.assertTrue(syms.ok)
        self.assertGreaterEqual(len(syms.value), 1)
        self.assertEqual(syms.value[0].name, "LdaRepoIndex")


if __name__ == "__main__":
    unittest.main()
