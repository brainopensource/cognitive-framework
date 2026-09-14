"""T-75 / DIR-I5: production LDA selection, recorded fallback, and freshness.

Hermetic fixture matrix. Never rebuilds the developer's `.lda/index.db`.
Disabling selection or freshness rejection must make the corresponding oracle fail.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vanguard.packages.adapters.bindings.code import (
    CodeBindingProvider,
    REPO_OBSERVATION_LIMIT,
)
from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.lda_index import LdaRepoIndex
from vanguard.packages.adapters.stores.repo_index import FileRepoIndex
from vanguard.packages.ports.environment import ObservationRequest
from vanguard.packages.ports.index import IndexSelection
from vanguard.packages.runtime.bootstrap import (
    ProductionIndexBinding,
    RuntimeBootstrap,
    select_production_index,
)


HEAD_A = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
HEAD_B = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

_CORE = (
    "class CoreService:\n"
    "    def execute(self):\n"
    "        return helper()\n"
)
_UTIL = (
    "def helper():\n"
    "    return 42\n"
)
_TEST = (
    "from pkg.core import CoreService\n"
    "def test_execute():\n"
    "    assert CoreService().execute() == 42\n"
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = text.encode("utf-8")
    path.write_bytes(raw)
    return _sha(raw)


def _git_head(root: Path, sha: str) -> None:
    git = root / ".git"
    git.mkdir(parents=True, exist_ok=True)
    (git / "HEAD").write_text(sha, encoding="utf-8")


def _create_lda(
    root: Path,
    *,
    head_sha: str = HEAD_A,
    files: dict[str, str] | None = None,
    include_calls: bool = True,
    extra_file_row: str | None = None,
    drop_columns: bool = False,
) -> Path:
    contents = files if files is not None else {
        "pkg/core.py": _CORE,
        "pkg/util.py": _UTIL,
        "tests/test_core.py": _TEST,
    }
    hashes: dict[str, str] = {}
    for rel, text in contents.items():
        hashes[rel] = _write(root / rel, text)
    if extra_file_row is not None:
        hashes[extra_file_row] = "dead" * 16

    _git_head(root, head_sha)
    lda_dir = root / ".lda"
    lda_dir.mkdir(parents=True, exist_ok=True)
    db_path = lda_dir / "index.db"
    con = sqlite3.connect(str(db_path))
    cur = con.cursor()
    if drop_columns:
        cur.executescript(
            """
            CREATE TABLE files (path TEXT PRIMARY KEY);
            CREATE TABLE symbols (id TEXT PRIMARY KEY);
            CREATE TABLE relations (id TEXT PRIMARY KEY);
            CREATE TABLE index_runs (id TEXT PRIMARY KEY);
            """
        )
        con.commit()
        con.close()
        return db_path

    cur.executescript(
        """
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
        """
    )
    cur.execute(
        "INSERT INTO index_runs VALUES ('run1', '2026-09-13T00:00:00Z', "
        "'2026-09-13T00:01:00Z', ?, 'main', ?, ?, 3, 100, 1)",
        (head_sha, len(hashes), 3),
    )
    for path, digest in hashes.items():
        cur.execute(
            "INSERT INTO files VALUES (?, ?, 10, 'python', '2026-09-13T00:00:00Z')",
            (path, digest),
        )
    symbols = [
        ("s1", "pkg/core.py", "CoreService", "pkg.core.CoreService", "class", 1, 4),
        ("s2", "pkg/core.py", "execute", "pkg.core.CoreService.execute", "method", 2, 3),
        ("s3", "pkg/util.py", "helper", "pkg.util.helper", "function", 1, 2),
    ]
    for row in symbols:
        if row[1] in hashes:
            cur.execute(
                "INSERT INTO symbols VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL)",
                row,
            )
    if include_calls and "pkg/core.py" in hashes and "pkg/util.py" in hashes:
        cur.execute(
            "INSERT INTO relations VALUES ('r1', 's2', 'pkg/core.py', 's3', 'calls', 1.0)"
        )
        cur.execute(
            "INSERT INTO relations VALUES ('r2', 's2', 'pkg/core.py', 'pkg/util.py', 'imports', 1.0)"
        )
        if "tests/test_core.py" in hashes:
            cur.execute(
                "INSERT INTO relations VALUES "
                "('r3', 'tests/test_core.py', 'tests/test_core.py', 's1', 'tests', 1.0)"
            )
    con.commit()
    con.close()
    return db_path


class ProductionIndexSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def test_healthy_current_lda_is_selected_with_source_identity(self) -> None:
        _create_lda(self.root)
        result = select_production_index(self.root)
        self.assertTrue(result.ok, result.error)
        binding = result.value
        self.assertIsInstance(binding, ProductionIndexBinding)
        self.assertIsInstance(binding.port, LdaRepoIndex)
        self.assertIsInstance(binding.selection, IndexSelection)
        self.assertEqual(binding.selection.backend, "lda")
        self.assertEqual(binding.selection.health_verdict, "healthy_current")
        self.assertIsNone(binding.selection.degradation_reason)
        self.assertFalse(binding.selection.unresolved_coverage)
        identity = binding.selection.source_identity
        self.assertTrue(identity.tree_hash.startswith("sha256:"))
        self.assertTrue(identity.index_digest.startswith("sha256:"))
        self.assertEqual(identity.source_revision, HEAD_A)
        names = {item.name for item in binding.port.symbols().value or ()}
        self.assertIn("helper", names)
        self.assertIn("CoreService", names)

    def test_optional_lda_absent_binds_file_with_recorded_fallback(self) -> None:
        _write(self.root / "pkg" / "core.py", _CORE)
        result = select_production_index(self.root)
        self.assertTrue(result.ok, result.error)
        binding = result.value
        self.assertIsInstance(binding.port, FileRepoIndex)
        self.assertEqual(binding.selection.backend, "file")
        self.assertEqual(binding.selection.health_verdict, "optional_absent")
        self.assertIsNotNone(binding.selection.degradation_reason)
        self.assertIn("absent", binding.selection.degradation_reason.lower())
        self.assertTrue(binding.selection.unresolved_coverage)
        names = {item.name for item in binding.port.symbols().value or ()}
        self.assertIn("CoreService", names)

    def test_present_invalid_states_reject_lda_and_record_cause(self) -> None:
        for label in ("stale", "empty", "unresolved", "unsupported", "corrupt"):
            with self.subTest(label=label):
                workspace = Path(tempfile.mkdtemp(dir=self.root))
                if label == "stale":
                    _create_lda(workspace, head_sha=HEAD_A)
                    _git_head(workspace, HEAD_B)
                elif label == "empty":
                    _create_lda(workspace, files={})
                    _write(workspace / "pkg" / "core.py", _CORE)
                elif label == "unresolved":
                    _create_lda(workspace, extra_file_row="pkg/deleted.py")
                elif label == "unsupported":
                    _create_lda(workspace, drop_columns=True)
                    _write(workspace / "pkg" / "core.py", _CORE)
                else:
                    (workspace / ".lda").mkdir(parents=True, exist_ok=True)
                    (workspace / ".lda" / "index.db").write_bytes(b"not-a-sqlite")
                    _write(workspace / "pkg" / "core.py", _CORE)

                result = select_production_index(workspace)
                self.assertTrue(result.ok, f"{label}: {result.error}")
                binding = result.value
                self.assertIsInstance(binding.port, FileRepoIndex)
                self.assertEqual(binding.selection.backend, "file")
                self.assertEqual(binding.selection.health_verdict, "present_invalid")
                self.assertIsNotNone(binding.selection.degradation_reason)
                self.assertTrue(binding.selection.unresolved_coverage)
                lda = LdaRepoIndex()
                lda_result = lda.index(str(workspace))
                self.assertFalse(lda_result.ok)
                names = {item.name for item in binding.port.symbols().value or ()}
                self.assertNotIn("deleted", names)

    def test_required_missing_or_unusable_is_unbound_without_retry_or_empty_graph(self) -> None:
        result = select_production_index(self.root, required=True)
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "INDEX_REQUIRED_UNBOUND")
        self.assertFalse(result.error.retryable)
        self.assertIsNone(result.value)

        _create_lda(self.root, files={})
        stale = select_production_index(self.root, required=True)
        self.assertFalse(stale.ok)
        self.assertEqual(stale.error.kind, "INDEX_REQUIRED_UNBOUND")
        self.assertFalse(stale.error.retryable)
        self.assertIsNone(stale.value)

    def test_workspace_mutation_refuses_stale_as_current_then_refresh_is_current(self) -> None:
        _create_lda(self.root)
        first = select_production_index(self.root)
        self.assertTrue(first.ok)
        self.assertEqual(first.value.selection.backend, "lda")

        (self.root / "pkg" / "util.py").unlink()
        blocked = select_production_index(self.root, prior=first.value.selection)
        self.assertFalse(blocked.ok)
        self.assertEqual(blocked.error.kind, "INDEX_SUBJECT_CHANGED")
        self.assertFalse(blocked.error.retryable)

        stale_lda = LdaRepoIndex()
        self.assertFalse(stale_lda.index(str(self.root)).ok)
        stale_query = LdaRepoIndex(self.root).symbols(name="helper")
        self.assertFalse(stale_query.ok)

        refreshed = select_production_index(
            self.root, prior=first.value.selection, refresh=True
        )
        self.assertTrue(refreshed.ok, refreshed.error)
        names = {item.name for item in refreshed.value.port.symbols().value or ()}
        self.assertNotIn("helper", names)
        self.assertIn("CoreService", names)
        self.assertEqual(refreshed.value.selection.backend, "file")
        self.assertEqual(refreshed.value.selection.health_verdict, "present_invalid")

    def test_rename_and_edit_do_not_serve_deleted_or_stale_symbols(self) -> None:
        _create_lda(self.root)
        selected = select_production_index(self.root)
        self.assertTrue(selected.ok)

        core = self.root / "pkg" / "core.py"
        core.rename(self.root / "pkg" / "renamed.py")
        renamed = select_production_index(self.root, refresh=True)
        self.assertTrue(renamed.ok)
        names = {item.name for item in renamed.value.port.symbols().value or ()}
        paths = {item.path for item in renamed.value.port.symbols().value or ()}
        self.assertNotIn("pkg/core.py", paths)
        self.assertIn("pkg/renamed.py", paths)
        self.assertIn("CoreService", names)

        _write(self.root / "pkg" / "renamed.py", "def added_after_edit():\n    return 1\n")
        edited = select_production_index(self.root, refresh=True)
        self.assertTrue(edited.ok)
        edited_names = {item.name for item in edited.value.port.symbols().value or ()}
        self.assertIn("added_after_edit", edited_names)
        self.assertNotIn("execute", edited_names)

    def test_refresh_and_restart_agree_on_repository_identity(self) -> None:
        _create_lda(self.root)
        first = select_production_index(self.root)
        restart = select_production_index(self.root)
        self.assertTrue(first.ok and restart.ok)
        a = first.value.selection.source_identity
        b = restart.value.selection.source_identity
        self.assertEqual(a.tree_hash, b.tree_hash)
        self.assertEqual(a.index_digest, b.index_digest)
        self.assertEqual(a.source_revision, b.source_revision)
        refreshed = select_production_index(self.root, prior=first.value.selection, refresh=True)
        self.assertTrue(refreshed.ok)
        c = refreshed.value.selection.source_identity
        self.assertEqual(c.tree_hash, a.tree_hash)
        self.assertEqual(c.index_digest, a.index_digest)
        self.assertEqual(c.source_revision, a.source_revision)

    def test_disabling_selection_fails_healthy_lda_oracle(self) -> None:
        _create_lda(self.root)
        healthy = select_production_index(self.root)
        self.assertEqual(healthy.value.selection.backend, "lda")
        disabled = select_production_index(self.root, selection_enabled=False)
        self.assertTrue(disabled.ok)
        self.assertNotEqual(disabled.value.selection.backend, "lda")

    def test_disabling_freshness_rejection_fails_stale_oracle(self) -> None:
        _create_lda(self.root, head_sha=HEAD_A)
        _git_head(self.root, HEAD_B)
        rejected = select_production_index(self.root)
        self.assertEqual(rejected.value.selection.health_verdict, "present_invalid")
        self.assertEqual(rejected.value.selection.backend, "file")
        accepted = select_production_index(self.root, reject_unusable=False)
        self.assertTrue(accepted.ok)
        self.assertEqual(accepted.value.selection.backend, "lda")
        self.assertEqual(accepted.value.selection.health_verdict, "healthy_current")

    def test_bootstrap_selects_index_without_changing_profile_or_sandbox(self) -> None:
        _create_lda(self.root)
        deps = RuntimeBootstrap.build(
            profile_id="product",
            repo_path=self.root,
            model=FakeModel([]),
            host_qualifies=False,
        )
        try:
            self.assertEqual(deps.profile.requested.process_backend, "host")
            self.assertEqual(deps.profile.requested.persistence_mode, "sqlite-wal")
            self.assertIsInstance(deps.index, LdaRepoIndex)
            self.assertEqual(deps.index_selection.backend, "lda")
            self.assertIsNone(deps.index_error)
        finally:
            deps.cleanup()

    def test_four_repo_verbs_are_bounded_with_explicit_omissions(self) -> None:
        _create_lda(self.root)
        binding = select_production_index(self.root).value
        provider = CodeBindingProvider()
        verbs = (
            ("repo.search_symbols", {"name": "helper"}),
            ("repo.get_callers", {"symbol": "helper"}),
            ("repo.get_dependencies", {"path": "pkg/core.py"}),
            ("repo.get_tests", {"path": "pkg/core.py"}),
        )
        for verb, args in verbs:
            adapter = provider.create_adapter(verb, None, index=binding.port)
            outcome = adapter.execute(ObservationRequest(action=verb.split(".")[-1], args=args))
            self.assertEqual(outcome.status, "ok", outcome.detail)
            payload = json.loads(outcome.detail)
            self.assertIn("items", payload)
            self.assertIn("omissions", payload)
            self.assertIn("truncated", payload)
            self.assertIsInstance(payload["omissions"], list)
            self.assertLessEqual(len(payload["items"]), REPO_OBSERVATION_LIMIT)

        with patch(
            "vanguard.packages.adapters.bindings.code.REPO_OBSERVATION_LIMIT",
            1,
        ):
            adapter = provider.create_adapter(
                "repo.search_symbols", None, index=binding.port
            )
            outcome = adapter.execute(
                ObservationRequest(action="search_symbols", args={})
            )
            payload = json.loads(outcome.detail)
            self.assertTrue(payload["truncated"])
            self.assertEqual(payload["omissions"][0]["reason"], "truncated")
            self.assertEqual(len(payload["items"]), 1)

        callers = json.loads(
            provider.create_adapter(
                "repo.get_callers", None, index=binding.port
            ).execute(
                ObservationRequest(action="get_callers", args={"symbol": "helper"})
            ).detail
        )
        self.assertEqual(callers["items"][0]["name"], "execute")
        file_binding = select_production_index(self.root, selection_enabled=False).value
        file_callers = json.loads(
            provider.create_adapter(
                "repo.get_callers", None, index=file_binding.port
            ).execute(
                ObservationRequest(action="get_callers", args={"symbol": "helper"})
            ).detail
        )
        reasons = {item["reason"] for item in file_callers["omissions"]}
        self.assertIn("unresolved_coverage", reasons)


if __name__ == "__main__":
    unittest.main()
