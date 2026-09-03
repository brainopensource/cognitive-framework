"""Unit and Contract Tests for LDA SOTA Features (PPR, Submodular Knapsack, RepoMap, Cache, TestAssociation)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock
import importlib

ppr_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.ppr_engine")
submod_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.submodular_allocator")
repo_map_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.repo_map")
cache_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.cache")
test_assoc_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.test_association")
switches_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.plugin_switches")
models_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.models")

PPREngine = ppr_mod.PPREngine
SubmodularContextAllocator = submod_mod.SubmodularContextAllocator
RepositoryMapGenerator = repo_map_mod.RepositoryMapGenerator
PacketCache = cache_mod.PacketCache
FileCache = cache_mod.FileCache
TestAssociationEngine = test_assoc_mod.TestAssociationEngine
StrategySwitcher = switches_mod.StrategySwitcher
AtlasStrategyConfig = switches_mod.AtlasStrategyConfig
Candidate = models_mod.Candidate


class TestPPREngine(unittest.TestCase):
    def setUp(self):
        self.engine = PPREngine(gamma=0.15, max_iter=30)

    def test_ppr_diffusion_convergence(self):
        entity_ids = ["sym:A", "sym:B", "sym:C", "sym:D"]
        relations = [
            {"source": "sym:A", "target": "sym:B", "kind": "calls"},
            {"source": "sym:B", "target": "sym:C", "kind": "calls"},
            {"source": "sym:C", "target": "sym:A", "kind": "calls"},
            {"source": "sym:B", "target": "sym:D", "kind": "tests"},
        ]
        adj, id_to_idx, out_degrees = self.engine.build_adjacency(entity_ids, relations)
        self.assertEqual(len(id_to_idx), 4)

        # Seed activation at node A
        r = self.engine.diffuse(
            num_nodes=4,
            adj=adj,
            out_degrees=out_degrees,
            seed_indices=[id_to_idx["sym:A"]],
        )
        self.assertEqual(len(r), 4)
        self.assertAlmostEqual(sum(r), 1.0, places=3)
        # Node B should have high probability because A calls B directly
        self.assertGreater(r[id_to_idx["sym:B"]], 0.0)


class TestSubmodularAllocator(unittest.TestCase):
    def setUp(self):
        self.allocator = SubmodularContextAllocator(redundancy_penalty=0.5)

    def test_submodular_knapsack_budget_and_redundancy(self):
        candidates = [
            Candidate(locator="pkg/engine.py#start", kind="symbol", title="Engine start", score=10.0, tokens=100, reason=""),
            Candidate(locator="pkg/engine.py#stop", kind="symbol", title="Engine stop", score=9.0, tokens=100, reason=""),
            Candidate(locator="pkg/storage.py#read", kind="symbol", title="Storage read", score=8.5, tokens=100, reason=""),
            Candidate(locator="pkg/engine.py#restart", kind="symbol", title="Engine restart", score=8.0, tokens=100, reason=""),
        ]

        # Budget allows 2 items (200 tokens)
        selected, used_tokens = self.allocator.allocate(candidates, budget=200)
        self.assertEqual(len(selected), 2)
        self.assertLessEqual(used_tokens, 200)

        # Due to redundancy penalty on "engine", Storage read should be favored over 2nd engine sibling
        locators = [c.locator for c in selected]
        self.assertIn("pkg/engine.py#start", locators)
        self.assertIn("pkg/storage.py#read", locators)


class TestRepositoryMapGenerator(unittest.TestCase):
    def test_repomap_generation(self):
        storage = MagicMock()
        storage.get_all_symbols.return_value = [
            {"symbol_id": "s1", "name": "Kernel", "file_path": "kernel.py", "signature": "class Kernel", "kind": "class", "docstring": "Core runtime kernel."},
            {"symbol_id": "s2", "name": "dispatch", "file_path": "kernel.py", "signature": "def dispatch()", "kind": "function", "docstring": "Dispatch pipeline."},
            {"symbol_id": "s3", "name": "Storage", "file_path": "storage.py", "signature": "class Storage", "kind": "class", "docstring": "Fact graph storage."},
        ]
        storage.get_all_relations.return_value = [
            {"source_id": "s2", "target_id": "s1", "kind": "defines"},
            {"source_id": "s3", "target_id": "s1", "kind": "calls"},
        ]

        gen = RepositoryMapGenerator(storage, max_symbols_budget=10)
        repomap = gen.generate_map(token_budget=500)

        self.assertIn("# REPOSITORY STRUCTURAL MAP", repomap)
        self.assertIn("File: `kernel.py`", repomap)
        self.assertIn("class Kernel", repomap)


class TestPacketCache(unittest.TestCase):
    def test_packet_cache_invalidation_on_git_head(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = PacketCache(Path(tmpdir))
            sample_packet = {"task": "test task", "budget": 4000, "provenance": {"source_head_sha": "sha_v1"}}

            cache.put("test task", 4000, "ppr_submodular", True, "sha_v1", sample_packet)

            # Hit on same HEAD
            hit = cache.get("test task", 4000, "ppr_submodular", True, "sha_v1")
            self.assertIsNotNone(hit)
            self.assertEqual(hit["task"], "test task")

            # Miss on different HEAD
            miss = cache.get("test task", 4000, "ppr_submodular", True, "sha_v2")
            self.assertIsNone(miss)


class TestTestAssociationEngine(unittest.TestCase):
    def test_find_associated_tests(self):
        storage = MagicMock()
        storage.get_all_symbols.return_value = [
            {"symbol_id": "sym:budget", "name": "Governor", "file_path": "vanguard/packages/kernel/budget.py"},
            {"symbol_id": "sym:test_gov", "name": "test_budget_commit", "file_path": "test/kernel/test_budget.py"},
        ]
        storage.get_all_relations.return_value = [
            {"source": "sym:test_gov", "target": "sym:budget", "kind": "tests"}
        ]

        engine = TestAssociationEngine(storage)
        res = engine.find_associated_tests(["vanguard/packages/kernel/budget.py"])

        self.assertIn("test/kernel/test_budget.py", res["associated_test_files"])
        self.assertTrue(any("test_budget" in cmd for cmd in res["suggested_commands"]))


class TestStrategySwitcher(unittest.TestCase):
    def test_strategy_watchdog_and_fallback(self):
        cfg = AtlasStrategyConfig(max_latency_ms=10.0, fallback_ranker="fts5_bm25")
        switcher = StrategySwitcher(cfg)

        def failing_strategy():
            raise RuntimeError("Strategy crash")

        def fallback_strategy():
            return ["fallback_result"]

        res, active_strat = switcher.execute_with_guard(
            "flaky_plugin",
            failing_strategy,
            fallback_strategy,
        )
        self.assertEqual(res, ["fallback_result"])
        self.assertEqual(active_strat, "fts5_bm25")


if __name__ == "__main__":
    unittest.main()
