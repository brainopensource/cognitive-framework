"""LDA portability contract tests (Phase P1).

Executable definition of "LDA works in ANY project":

1. Generic profile is the default — no side-channel profile detection, even
   when a repository contains Aether-shaped artifacts (`.generated/knowledge/`,
   `.vanguard/`).
2. Profiles apply ONLY when explicitly named (lda.yaml `profile:` / $LDA_PROFILE)
   and missing named profiles fail closed.
3. Single Emitter invariant: LDA never writes the canonical knowledge base.
4. Context packets bind to the live workspace git HEAD (fail-closed freshness).
5. Bounded growth: global symbol rankings are capped at Top-K.
6. The full pipeline (index -> context packet) succeeds on a non-Python repo.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from importlib import import_module
from pathlib import Path
from unittest import mock

atlas_mod = import_module("tools.007_LLM_DOCS_ATLAS.atlas")
config_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.config")
ranking_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.ranking")
profile_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.profile")
gitinfo_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.gitinfo")

AtlasContext = config_mod.AtlasContext
RepositoryProfile = profile_mod.RepositoryProfile


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_repo(**extra_files: str) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="lda-portability-"))
    _write(tmp / "docs" / "guide.md", "# Guide\n\nDelegation topology and spawn behavior.\n")
    _write(tmp / "src" / "app.py", "def spawn_child():\n    ...\n")
    for rel, content in extra_files.items():
        _write(tmp / rel, content)
    return tmp


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", "user.email=lda@test", "-c", "user.name=lda", *args],
        cwd=repo, text=True, capture_output=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {result.stderr}")
    return result.stdout.strip()


def _rm(repo: Path) -> None:
    subprocess.run(["rm", "-rf", str(repo)], check=True)


class ProfileSelectionTests(unittest.TestCase):
    """A profile is applied only when explicitly named — never side-channelled."""

    def test_generic_profile_is_default(self):
        repo = _make_repo()
        try:
            ctx = AtlasContext.discover(repo)
            self.assertEqual(ctx.profile.name, "generic")
            # Zero AETHER vocabulary leakage into the generic default:
            self.assertEqual(ctx.profile.authority_score("normative"), 0)
            self.assertEqual(ctx.profile.authority_score("non-canonical"), 0)
            self.assertEqual(ctx.profile.non_canonical_prefixes, ())
            self.assertEqual(ctx.profile.source_roots, ("src", "lib", "packages"))
        finally:
            _rm(repo)

    def test_aether_artifacts_do_not_trigger_side_channel(self):
        # The old implementation selected the AETHER profile whenever
        # .generated/knowledge/catalog.jsonl existed. That side-channel is dead.
        repo = _make_repo(
            **{".generated/knowledge/catalog.jsonl": '{"path": "docs/SPEC.md"}\n'},
            **{".vanguard/workspace/tmp/x": "junk\n"},
            **{"dev_context_logs/01_state.txt": "state\n"},
        )
        try:
            ctx = AtlasContext.discover(repo)
            self.assertEqual(ctx.profile.name, "generic")
            self.assertEqual(ctx.profile.authority_score("normative"), 0)
        finally:
            _rm(repo)

    def test_explicit_profile_via_lda_yaml(self):
        repo = _make_repo(**{"lda.yaml": "profile: aether\n"})
        try:
            ctx = AtlasContext.discover(repo)
            self.assertEqual(ctx.profile.name, "aether")
            self.assertIn("docs/research/", ctx.profile.non_canonical_prefixes)
            self.assertEqual(ctx.profile.authority_score("normative"), 79)
            self.assertIn(".vanguard/", ctx.profile.low_signal_patterns)
            self.assertIn("dev_context_logs", ctx.profile.excluded_dirs)
            self.assertEqual(ctx.profile.knowledge_adapter, "aether-knowledge")
        finally:
            _rm(repo)

    def test_repo_local_profile_overrides_bundled(self):
        repo = _make_repo(**{"lda.yaml": "profile: custom\n"})
        _write(
            repo / "profiles" / "lda" / "custom.toml",
            'name = "custom"\nmax_global_symbols = 42\n',
        )
        try:
            ctx = AtlasContext.discover(repo)
            self.assertEqual(ctx.profile.name, "custom")
            self.assertEqual(ctx.profile.max_global_symbols, 42)
        finally:
            _rm(repo)

    def test_env_profile_selection(self):
        repo = _make_repo()
        try:
            with mock.patch.dict(os.environ, {"LDA_PROFILE": "aether"}):
                ctx = AtlasContext.discover(repo)
            self.assertEqual(ctx.profile.name, "aether")
        finally:
            _rm(repo)

    def test_unknown_profile_fails_closed(self):
        repo = _make_repo(**{"lda.yaml": "profile: does-not-exist\n"})
        try:
            with self.assertRaises(ValueError):
                AtlasContext.discover(repo)
        finally:
            _rm(repo)


class SingleEmitterTests(unittest.TestCase):
    """LDA consumes the knowledge base as a downstream projection; never writes it."""

    def test_rescan_catalog_is_read_only(self):
        catalog_rel = ".generated/knowledge/catalog.jsonl"
        catalog_body = '{"canonical_id": "spec.core", "path": "docs/SPEC.md"}\n'
        repo = _make_repo(**{catalog_rel: catalog_body})
        try:
            ctx = AtlasContext.discover(repo)
            result = atlas_mod.rescan_catalog(ctx)
            self.assertFalse(result["written"])
            self.assertEqual((repo / catalog_rel).read_text(encoding="utf-8"), catalog_body)
        finally:
            _rm(repo)

    def test_index_repository_never_writes_knowledge_base(self):
        catalog_rel = ".generated/knowledge/catalog.jsonl"
        catalog_body = '{"canonical_id": "spec.core", "path": "docs/SPEC.md"}\n'
        repo = _make_repo(**{catalog_rel: catalog_body})
        try:
            atlas_mod.index_repository(repo, incremental=False)
            self.assertEqual((repo / catalog_rel).read_text(encoding="utf-8"), catalog_body)
        finally:
            _rm(repo)


class HeadBindingTests(unittest.TestCase):
    """Context packets bind to the live workspace git HEAD (fail-closed freshness)."""

    def test_head_sha_captured_outside_git_returns_none(self):
        repo = _make_repo()
        try:
            self.assertIsNone(gitinfo_mod.current_head_sha(repo))
            ctx = AtlasContext.discover(repo)
            self.assertIsNone(ctx.head_sha)
        finally:
            _rm(repo)

    def test_packet_provenance_records_source_head_sha(self):
        repo = _make_repo()
        try:
            _git(repo, "init")
            _git(repo, "add", "-A")
            _git(repo, "commit", "-m", "init")
            expected_head = _git(repo, "rev-parse", "HEAD")
            packet = atlas_mod.compile_task_context(repo, "delegation spawn", budget=4000)
            self.assertEqual(packet.provenance.get("source_head_sha"), expected_head)
            self.assertIn(
                "source_head_sha",
                " ".join(packet.invariants),
                "HEAD-binding invariant must be declared in the packet contract",
            )
        finally:
            _rm(repo)


class BoundedGrowthTests(unittest.TestCase):
    """Global symbol rankings are capped at Top-K (profile.max_global_symbols)."""

    def test_symbol_ceiling_caps_top_k(self):
        profile = RepositoryProfile(max_global_symbols=3)
        candidates = [
            ranking_mod.Candidate(
                locator=f"src/mod_{i}.py#sym{i}", kind="symbol", title=f"sym{i}",
                score=float(i), tokens=10, reason="test",
            )
            for i in range(50)
        ]
        kept = ranking_mod.apply_symbol_ceiling(candidates, profile)
        kept_symbols = [c for c in kept if c.kind == "symbol"]
        self.assertEqual(len(kept_symbols), 3)
        # The highest-scoring symbols survive.
        self.assertEqual({c.title for c in kept_symbols}, {"sym47", "sym48", "sym49"})

    def test_symbol_ceiling_noop_under_ceiling(self):
        profile = RepositoryProfile(max_global_symbols=500)
        candidates = [
            ranking_mod.Candidate(
                locator="src/a.py#sym", kind="symbol", title="sym",
                score=1.0, tokens=10, reason="test",
            )
        ]
        self.assertEqual(ranking_mod.apply_symbol_ceiling(candidates, profile), candidates)


class NonPythonPipelineTests(unittest.TestCase):
    """The full pipeline succeeds on a repository with no Python source at all."""

    def test_index_and_context_on_typescript_markdown_repo(self):
        tmp = Path(tempfile.mkdtemp(prefix="lda-portability-"))
        try:
            _write(tmp / "docs" / "architecture.md", "# Architecture\n\nBudget algebra and dispatch.\n")
            _write(tmp / "src" / "index.ts", "export function dispatch(): void {}\n")
            _git(tmp, "init")
            _git(tmp, "add", "-A")
            _git(tmp, "commit", "-m", "init")
            expected_head = _git(tmp, "rev-parse", "HEAD")

            result = atlas_mod.index_repository(tmp, incremental=False)
            self.assertEqual(result["status"], "SUCCESS")

            packet = atlas_mod.compile_task_context(tmp, "budget algebra dispatch", budget=2000)
            self.assertLessEqual(packet.estimated_tokens, packet.budget)
            self.assertEqual(packet.provenance.get("source_head_sha"), expected_head)
            self.assertEqual(packet.provenance.get("profile"), "generic")
        finally:
            _rm(tmp)


if __name__ == "__main__":
    unittest.main()