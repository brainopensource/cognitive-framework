"""Phase A retrieval-quality falsifiers for LDA.

Covers: deterministic dense embeddings (cross-process), section-level FTS
retrieval, stack-trace frame routing, hybrid RRF fusion, intent-conditioned
budget mix (with profile override), and content dedup in the knapsack
allocator.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from importlib import import_module
from pathlib import Path

atlas_mod = import_module("tools.007_LLM_DOCS_ATLAS.atlas")
ranking_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.ranking")
hybrid_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.hybrid")
query_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.query")
compiler_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.compiler")
profile_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.profile")
submod_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.submodular_allocator")
models_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.models")

analyze_query = query_mod.analyze_query
DEFAULT_BUDGET_MIX = query_mod.DEFAULT_BUDGET_MIX
stable_embedding = hybrid_mod.stable_embedding
DenseRetriever = hybrid_mod.DenseRetriever
reciprocal_rank_fusion = hybrid_mod.reciprocal_rank_fusion
rank_entities = ranking_mod.rank_entities
_budget_mix_for = compiler_mod._budget_mix_for
RepositoryProfile = profile_mod.RepositoryProfile
SubmodularContextAllocator = submod_mod.SubmodularContextAllocator
Candidate = models_mod.Candidate


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_repo(**extra: str) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="lda-retrieval-"))
    _write(tmp / "docs" / "guide.md", "# Guide\n\nDelegation topology and spawn behavior.\n")
    _write(tmp / "src" / "app.py", "def spawn_child():\n    ...\n")
    for rel, content in extra.items():
        _write(tmp / rel, content)
    return tmp


class TestDeterministicEmbeddings(unittest.TestCase):
    def test_embeddings_stable_across_interpreter_processes(self):
        """hash() is salted per process; embeddings must NOT be."""
        vec = stable_embedding("delegation budget attenuation", 64)
        digest = hash(tuple(round(v, 9) for v in vec))
        code = (
            "import sys, importlib\n"
            "sys.path.insert(0, %r)\n"
            "m = importlib.import_module('tools.007_LLM_DOCS_ATLAS.core.hybrid')\n"
            "v = m.stable_embedding('delegation budget attenuation', 64)\n"
            "print(hash(tuple(round(x, 9) for x in v)))\n"
        ) % str(Path(__file__).resolve().parents[2])
        digests = {digest}
        for _ in range(2):
            out = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True, text=True, timeout=60,
                cwd=str(Path(__file__).resolve().parents[2]),
            )
            self.assertEqual(out.returncode, 0, out.stderr)
            digests.add(int(out.stdout.strip()))
        self.assertEqual(len(digests), 1, "embeddings differ across processes")

    def test_rrf_fusion_is_deterministic_and_tie_broken(self):
        fused = reciprocal_rank_fusion({"lexical": ["a", "b"], "dense": ["b", "c"]})
        locators = [loc for loc, _ in fused]
        self.assertEqual(set(locators), {"a", "b", "c"})
        self.assertEqual(locators[0], "b")  # high in both channels
        again = reciprocal_rank_fusion({"lexical": ["a", "b"], "dense": ["b", "c"]})
        self.assertEqual(again, fused)

    def test_dense_retriever_surfaces_semantic_match(self):
        r = DenseRetriever(dim=128)
        r.add("docs/atlas.md#L1-L5", "monotonic capability attenuation ledger")
        r.add("docs/cook.md#L1-L5", "how to bake bread at home")
        hits = r.search("capability attenuation ledger semantics", limit=3)
        self.assertTrue(hits)
        self.assertEqual(hits[0], "docs/atlas.md#L1-L5")


class TestSectionRetrieval(unittest.TestCase):
    def test_matching_section_becomes_zoomed_candidate(self):
        repo = _make_repo(**{
            "docs/quotas.md": (
                "# Quotas\n\nIntro paragraph about budgets.\n\n"
                "## Xylophone Allocation\n\n"
                "The xylophone quota governs per-agent instrument budgets.\n"
                "Every spawn consumes one xylophone token.\n"
            )
        })
        try:
            atlas_mod.index_repository(repo, rebuild=True)
            storage = atlas_mod.get_storage(repo)
            rows = storage.search_sections("xylophone quota", limit=10)
            self.assertTrue(rows, "section FTS must index section content")
            self.assertTrue(any("xylophone" in (r.get("content") or "").lower() for r in rows))

            candidates = rank_entities("xylophone quota semantics", storage, repo_root=repo)
            sections = [c for c in candidates if c.kind == "doc_section"]
            self.assertTrue(sections, "rank_entities must emit doc_section candidates")
            self.assertTrue(any("xylophone" in (c.content or "").lower() for c in sections))
            self.assertTrue(all("#L" in c.locator for c in sections))
        finally:
            shutil.rmtree(repo, ignore_errors=True)


class TestStackTraceRouting(unittest.TestCase):
    def test_file_line_frame_becomes_top_code_candidate(self):
        repo = _make_repo(**{"src/kernel/budget.py": "class Governor:\n    ...\n"})
        try:
            atlas_mod.index_repository(repo, rebuild=True)
            storage = atlas_mod.get_storage(repo)
            task = 'fix crash: File "src/kernel/budget.py", line 42'
            candidates = rank_entities(task, storage, repo_root=repo)
            frames = [c for c in candidates if c.kind == "code" and "budget.py#L42" in c.locator]
            self.assertTrue(frames, "stack-trace frames must become code candidates")
            self.assertGreaterEqual(frames[0].score, 90.0)
        finally:
            shutil.rmtree(repo, ignore_errors=True)


class TestQueryConditioning(unittest.TestCase):
    def test_intent_detection(self):
        self.assertEqual(analyze_query("fix the failing budget").intent, "bugfix")
        self.assertEqual(analyze_query("add support for retries").intent, "feature")
        self.assertEqual(analyze_query("write unit tests for spawn").intent, "test")
        self.assertEqual(analyze_query("explain how compaction works").intent, "explain")

    def test_budget_mix_override_and_defaults(self):
        plan = analyze_query("fix the crash in dispatch")
        self.assertEqual(plan.intent, "bugfix")
        mix = _budget_mix_for("fix the crash in dispatch", RepositoryProfile())
        self.assertEqual(mix, DEFAULT_BUDGET_MIX["bugfix"])
        self.assertAlmostEqual(sum(mix), 1.0, places=6)
        profile = RepositoryProfile(budget_mix={"bugfix": (0.1, 0.8, 0.1)})
        self.assertEqual(_budget_mix_for("fix the crash in dispatch", profile), (0.1, 0.8, 0.1))
        bad = RepositoryProfile(budget_mix={"bugfix": (0.5, 0.5)})
        self.assertEqual(_budget_mix_for("fix the crash in dispatch", bad), DEFAULT_BUDGET_MIX["bugfix"])


class TestContentDedup(unittest.TestCase):
    def test_identical_content_occupies_one_slot(self):
        allocator = SubmodularContextAllocator()
        body = "The xylophone quota governs per-agent instrument budgets and spawn tokens."
        candidates = [
            Candidate(locator="docs/a.md", kind="document", title="A", score=10.0, tokens=40, reason="", content=body),
            Candidate(locator="docs/b.md", kind="document", title="B", score=9.0, tokens=40, reason="", content=body),
        ]
        selected, used = allocator.allocate(candidates, budget=400)
        self.assertEqual(len(selected), 1)
        self.assertLessEqual(used, 400)


class TestHybridStrategyIntegration(unittest.TestCase):
    def test_compile_with_hybrid_rrf(self):
        repo = _make_repo(**{
            "docs/quotas.md": "# Quotas\n\n## Instrument Budgets\n\nThe xylophone quota governs spawn tokens.\n",
            "src/instrument.py": 'class Xylophone:\n    """Per-agent instrument budget ledger."""\n    ...\n',
        })
        try:
            atlas_mod.index_repository(repo, rebuild=True)
            packet = atlas_mod.compile_task_context(
                repo, "xylophone instrument budgets", budget=2000, strategy="hybrid_rrf"
            )
            self.assertEqual(packet.provenance.get("strategy"), "hybrid_rrf")
            self.assertTrue(packet.provenance.get("ranking_channels", {}).get("dense_rrf"))
            self.assertGreater(packet.estimated_tokens, 0)
        finally:
            shutil.rmtree(repo, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
