"""Wave F falsifiers: packet `omitted`, `lda identity`, `lda diff`, `lda metrics`,
and the index-run HEAD binding."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from importlib import import_module
from pathlib import Path

atlas_mod = import_module("tools.007_LLM_DOCS_ATLAS.atlas")
identity_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.identity")
metrics_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.metrics")
repodiff_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.repodiff")
models_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.models")


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", "user.email=lda@test", "-c", "user.name=lda", *args],
        cwd=repo, text=True, capture_output=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {result.stderr}")
    return result.stdout.strip()


def _make_git_repo(**extra: str) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="lda-wavef-"))
    _write(tmp / "pyproject.toml", '[project]\nname = "fixture"\nrequires-python = ">=3.10"\n')
    _write(tmp / "src" / "app.py", 'def spawn_child():\n    """Spawn an attenuated child."""\n    ...\n')
    for rel, content in extra.items():
        _write(tmp / rel, content)
    _git(tmp, "init")
    _git(tmp, "add", "-A")
    _git(tmp, "commit", "-m", "init")
    return tmp


class TestOmittedField(unittest.TestCase):
    def test_packet_carries_bounded_omissions(self):
        repo = _make_git_repo(**{
            "docs/guide.md": "# Guide\n\n## Delegation\n\nDelegation topology and spawn behavior.\n",
            "docs/extra.md": "## Alpha Topic\n\nAlpha beta gamma delta epsilon.\n",
        })
        try:
            atlas_mod.index_repository(repo, rebuild=True)
            packet = atlas_mod.compile_task_context(
                repo, "delegation topology spawn", budget=400, strategy="fts5_bm25"
            )
            self.assertIsInstance(packet.omitted, list)
            self.assertLessEqual(len(packet.omitted), 12)
            self.assertEqual(packet.token_accounting.get("omitted_count"), len(packet.omitted))
            for entry in packet.omitted:
                self.assertEqual(entry["reason"], "budget_exhausted")
        finally:
            shutil.rmtree(repo, ignore_errors=True)


class TestIdentity(unittest.TestCase):
    def test_identity_snapshot_fresh_binding(self):
        repo = _make_git_repo()
        try:
            atlas_mod.index_repository(repo, rebuild=True)
            identity = identity_mod.repo_identity(repo, atlas_mod.get_storage(repo))
            self.assertTrue(identity["head_sha"])
            self.assertFalse(identity["dirty"])
            self.assertEqual(identity["submodules"], 0)
            systems = {b["system"] for b in identity["build_systems"]}
            self.assertIn("python", systems)
            hints = next(b for b in identity["build_systems"] if b["system"] == "python")
            self.assertEqual(hints["requires-python"], ">=3.10")
            self.assertEqual(identity["index"]["freshness_vs_head"], "FRESH")
            self.assertEqual(identity["index"]["index_head_sha"], identity["head_sha"][:12])
        finally:
            shutil.rmtree(repo, ignore_errors=True)

    def test_identity_reports_stale_after_commit(self):
        repo = _make_git_repo()
        try:
            atlas_mod.index_repository(repo, rebuild=True)
            _write(repo / "src" / "app.py", "def new_child():\n    ...\n")
            _git(repo, "add", "-A")
            _git(repo, "commit", "-m", "change")
            identity = identity_mod.repo_identity(repo, atlas_mod.get_storage(repo))
            self.assertEqual(identity["index"]["freshness_vs_head"], "STALE")
            self.assertIn("lda index", identity["action_hint"])
        finally:
            shutil.rmtree(repo, ignore_errors=True)


class TestDiff(unittest.TestCase):
    def test_workspace_vs_index_detects_all_change_classes(self):
        repo = _make_git_repo(**{"docs/guide.md": "# Guide\n\nStale doc.\n"})
        try:
            atlas_mod.index_repository(repo, rebuild=True)
            _write(repo / "src" / "app.py", "def changed_child():\n    ...\n")   # modified
            _write(repo / "src" / "newmod.py", "def brand_new():\n    ...\n")   # added
            (repo / "docs" / "guide.md").unlink()                               # deleted

            diff = repodiff_mod.compute_diff(repo, atlas_mod.get_storage(repo))
            self.assertEqual(diff["mode"], "workspace_vs_index")
            self.assertIn("src/app.py", diff["modified_files"])
            self.assertIn("src/newmod.py", diff["added_files"])
            self.assertIn("docs/guide.md", diff["deleted_files"])
            self.assertGreaterEqual(diff["stale_fact_files"], 2)
            self.assertIn("incremental", diff["action_hint"])
        finally:
            shutil.rmtree(repo, ignore_errors=True)

    def test_git_since_mode(self):
        repo = _make_git_repo()
        try:
            atlas_mod.index_repository(repo, rebuild=True)
            first_sha = _git(repo, "rev-parse", "HEAD")
            _write(repo / "src" / "extra.py", "def extra():\n    ...\n")
            _git(repo, "add", "-A")
            _git(repo, "commit", "-m", "add extra")
            diff = repodiff_mod.compute_diff(repo, atlas_mod.get_storage(repo), since=first_sha)
            self.assertEqual(diff["mode"], "git_since")
            self.assertIn("src/extra.py", diff["added_files"])
        finally:
            shutil.rmtree(repo, ignore_errors=True)


class TestMetrics(unittest.TestCase):
    def test_cycles_fan_and_doc_ratio(self):
        repo = _make_git_repo(**{
            "src/alpha/mod_a.py": "def fa():\n    ...\n",
            "src/beta/mod_b.py": "def fb():\n    ...\n",
        })
        try:
            atlas_mod.index_repository(repo, rebuild=True)
            storage = atlas_mod.get_storage(repo)
            con = storage.get_connection()
            a_id = con.execute("SELECT id FROM symbols WHERE name='fa'").fetchone()[0]
            b_id = con.execute("SELECT id FROM symbols WHERE name='fb'").fetchone()[0]
            with con:
                con.execute(
                    "INSERT INTO relations (id, source_id, target_id, kind, confidence_tier) VALUES ('r1', ?, ?, 'imports', 80)",
                    (a_id, b_id),
                )
                con.execute(
                    "INSERT INTO relations (id, source_id, target_id, kind, confidence_tier) VALUES ('r2', ?, ?, 'imports', 80)",
                    (b_id, a_id),
                )
            m = metrics_mod.compute_metrics(storage)
            self.assertGreaterEqual(m["import_cycle_count"], 1)
            self.assertEqual(len(m["import_cycles"][0]["modules"]), 2)
            self.assertGreater(m["totals"]["relations"], 0)
            self.assertLessEqual(m["totals"]["documentation_ratio"], 1.0)
        finally:
            shutil.rmtree(repo, ignore_errors=True)


class TestIndexHeadBinding(unittest.TestCase):
    def test_index_run_records_head(self):
        repo = _make_git_repo()
        try:
            atlas_mod.index_repository(repo, rebuild=True)
            run = atlas_mod.get_storage(repo).latest_index_run()
            self.assertTrue(run.get("head_sha"), "index runs must record the HEAD they indexed")
        finally:
            shutil.rmtree(repo, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
