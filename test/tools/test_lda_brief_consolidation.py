"""Phase B/C falsifiers: briefing, consolidation, drift, knowledge health, and
the adopted ``repo_report`` plugin."""
from __future__ import annotations

import shutil
import tempfile
import unittest
from importlib import import_module
from pathlib import Path

atlas_mod = import_module("tools.007_LLM_DOCS_ATLAS.atlas")
briefing_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.briefing")
consolidation_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.consolidation")
drift_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.drift")
health_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.healthcheck")
config_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.config")


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_repo(**extra: str) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="lda-brief-"))
    _write(tmp / "docs" / "guide.md", "# Guide\n\nDelegation topology and spawn behavior.\n")
    _write(tmp / "src" / "app.py", "def spawn_child():\n    \"\"\"Spawn an attenuated child.\"\"\"\n    ...\n")
    for rel, content in extra.items():
        _write(tmp / rel, content)
    return tmp


class TestBriefing(unittest.TestCase):
    def test_brief_compiles_with_markdown_and_provenance(self):
        repo = _make_repo(**{
            "docs/spec.md": "# Spec\n\n## Spawn Budgets\n\nSpawn budgets are monotonic and typed.\n",
        })
        try:
            atlas_mod.index_repository(repo, rebuild=True)
            brief = briefing_mod.compile_brief(repo, "implement spawn budget checks", budget=3000)
            self.assertEqual(brief["intent"], "feature")
            self.assertIn("source_head_sha", brief["provenance"])
            md = brief["brief_markdown"]
            for heading in ("# LDA Task Briefing", "## Authority map", "## Key documents", "## Key code"):
                self.assertIn(heading, md)
            self.assertIn("implement spawn budget checks", md)
        finally:
            shutil.rmtree(repo, ignore_errors=True)


class TestConsolidation(unittest.TestCase):
    def test_duplicate_documents_detected(self):
        repo = _make_repo(**{
            "docs/a.md": "# Topic\n\nAlpha beta gamma delta epsilon zeta eta theta iota kappa.\n",
            "docs/b.md": "# Topic\n\nAlpha beta gamma delta epsilon zeta eta theta iota kappa.\n",
        })
        try:
            atlas_mod.index_repository(repo, rebuild=True)
            result = consolidation_mod.run_consolidation(atlas_mod.get_storage(repo))
            self.assertTrue(result["duplicate_documents"], "identical docs must be detected")
            self.assertEqual(result["status"], "NEEDS_CONSOLIDATION")
        finally:
            shutil.rmtree(repo, ignore_errors=True)

    def test_clean_repo_reports_healthy(self):
        repo = _make_repo()
        try:
            atlas_mod.index_repository(repo, rebuild=True)
            result = consolidation_mod.run_consolidation(atlas_mod.get_storage(repo))
            self.assertEqual(result["status"], "HEALTHY")
        finally:
            shutil.rmtree(repo, ignore_errors=True)


class TestDrift(unittest.TestCase):
    def test_stale_symbol_path_detected(self):
        repo = _make_repo()
        try:
            atlas_mod.index_repository(repo, rebuild=True)
            (repo / "src" / "app.py").unlink()
            result = drift_mod.detect_drift(atlas_mod.get_storage(repo), repo)
            self.assertEqual(result["status"], "DRIFT_DETECTED")
            self.assertGreaterEqual(result["stale_symbol_paths_count"], 1)
        finally:
            shutil.rmtree(repo, ignore_errors=True)


class TestHealthcheckKnowledgeChecks(unittest.TestCase):
    def test_check_includes_consolidation_and_drift(self):
        repo = _make_repo()
        try:
            atlas_mod.index_repository(repo, rebuild=True)
            ctx = config_mod.AtlasContext.discover(repo)
            report = health_mod.run_healthcheck(ctx, atlas_mod.get_storage(repo))
            ids = {c["id"] for c in report["checks"]}
            self.assertIn("knowledge.consolidation", ids)
            self.assertIn("knowledge.drift", ids)
        finally:
            shutil.rmtree(repo, ignore_errors=True)


class TestRepoReportPlugin(unittest.TestCase):
    def test_plugin_registers_and_generates_report(self):
        plugin_mod = import_module("tools.007_LLM_DOCS_ATLAS.plugins.repo_report.plugin")
        registry = import_module("tools.007_LLM_DOCS_ATLAS.core.registry")

        repo = _make_repo()
        try:
            ctx = config_mod.AtlasContext.discover(repo)
            plugin = plugin_mod.RepoReportPlugin()
            providers = plugin.providers()
            self.assertEqual(len(providers), 1)
            result = providers[0].collect(ctx)
            self.assertEqual(result.provider, "repo_report")
            self.assertTrue((repo / ".lda" / "repo-report" / "report.json").exists())

            manager = registry.PluginManager.get_instance()
            manager.register_plugin(plugin)
            listed = {entry.get("name") for entry in manager.list_plugins()}
            self.assertIn("repo_report", listed)
        finally:
            shutil.rmtree(repo, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
