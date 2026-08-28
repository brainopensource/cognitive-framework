"""Unit and integration test suite for 006_LLM_INT_MACHINE."""

import ast
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add package directory to sys.path so modules can be imported directly
_PKG_DIR = Path(__file__).resolve().parents[1]
if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))

from config import (
    HarnessConfig,
    CONFIG_V1_0_BASELINE,
    CONFIG_V1_1_VANGUARD_CORE,
    CONFIG_V1_2_SOTA_FULL,
    CONFIG_V2_0_SBFL_GRAPH,
    CONFIG_V2_1_MCTS_SPECULATIVE,
    CONFIG_V2_2_MUTATION_ROBUST,
    CONFIG_V2_3_COMPOUND_FULL,
    get_preset,
)
from env_loader import load_openrouter_api_key, has_openrouter_api_key
from tools import ToolWorkspace, ToolExecutionResult
from context_engine import ContextEngine, ContextBlock, ContextLayer
from reproducer_protocol import ReproducerManager, ReproducerPhase
from llm_client import MockLLMClient, LLMResponse, estimate_cost
from challenges import CHALLENGES, setup_challenge_workspace, evaluate_challenge_oracle
from engine import IntelligentMachineEngine, ExecutionReport
from code_graph import ASTCodeGraph
from fault_localizer import SBFLEngine
from mcts_search import SpeculativeMCTSSearch
from mutation_verifier import PatchMutationVerifier
from subagent_orchestrator import SubagentCoordinator, SubagentSandbox
from hierarchical_router import HierarchicalModelRouter
from telemetry_kpi import AdvancedKPITelemetry
from catalog import RunCatalog, RunReceipt, generate_run_id
from experiment_matrix import run_multi_trial_experiment, parse_override_string


class TestConfigAndRegistry(unittest.TestCase):
    def test_presets(self):
        self.assertFalse(CONFIG_V1_0_BASELINE.use_ast_preflight)
        self.assertFalse(CONFIG_V1_0_BASELINE.use_l1_l5_prefix_stability)
        
        self.assertTrue(CONFIG_V1_1_VANGUARD_CORE.use_l1_l5_prefix_stability)
        self.assertTrue(CONFIG_V1_1_VANGUARD_CORE.use_dialogue_compaction)
        self.assertFalse(CONFIG_V1_1_VANGUARD_CORE.use_ast_preflight)
        
        self.assertTrue(CONFIG_V1_2_SOTA_FULL.use_ast_preflight)
        self.assertTrue(CONFIG_V1_2_SOTA_FULL.use_reproduce_first)
        self.assertTrue(CONFIG_V1_2_SOTA_FULL.use_speculative_rollback)
        self.assertTrue(CONFIG_V1_2_SOTA_FULL.use_paged_output)

        self.assertTrue(CONFIG_V2_0_SBFL_GRAPH.use_code_graph)
        self.assertTrue(CONFIG_V2_0_SBFL_GRAPH.use_sbfl_localization)
        self.assertTrue(CONFIG_V2_1_MCTS_SPECULATIVE.use_mcts_search)
        self.assertTrue(CONFIG_V2_2_MUTATION_ROBUST.use_mutation_testing)
        self.assertTrue(CONFIG_V2_3_COMPOUND_FULL.use_code_graph)
        self.assertTrue(CONFIG_V2_3_COMPOUND_FULL.use_mcts_search)
        self.assertTrue(CONFIG_V2_3_COMPOUND_FULL.use_mutation_testing)

    def test_config_hashing_and_derivation(self):
        cfg1 = CONFIG_V1_2_SOTA_FULL
        cfg2 = CONFIG_V1_2_SOTA_FULL
        self.assertEqual(cfg1.config_hash(), cfg2.config_hash())

        derived = cfg1.derive(seed=999, max_turns=20)
        self.assertNotEqual(cfg1.config_hash(), derived.config_hash())
        self.assertEqual(derived.seed, 999)
        self.assertEqual(derived.max_turns, 20)
        self.assertEqual(derived.use_ast_preflight, cfg1.use_ast_preflight)

    def test_preset_lookup(self):
        preset = get_preset("v2.3_compound_full")
        self.assertEqual(preset.config_name, "v2.3_compound_full")
        self.assertEqual(get_preset("compound").config_name, "v2.3_compound_full")
        with self.assertRaises(KeyError):
            get_preset("non_existent_preset")


class TestToolsAndASTPreflight(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.config = CONFIG_V1_2_SOTA_FULL
        self.ws = ToolWorkspace(self.test_dir, self.config)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_fs_read_and_search(self):
        f = self.test_dir / "sample.py"
        f.write_text("def hello():\n    return 42\n", encoding="utf-8")
        
        read_res = self.ws.fs_read("sample.py")
        self.assertTrue(read_res.ok)
        self.assertIn("return 42", read_res.output)
        
        search_res = self.ws.fs_search("hello")
        self.assertTrue(search_res.ok)
        self.assertIn("sample.py", search_res.output)

    def test_ast_preflight_catches_syntax_error(self):
        f = self.test_dir / "broken.py"
        f.write_text("def valid_func():\n    return True\n", encoding="utf-8")

        patch_res = self.ws.patch_apply(
            path="broken.py",
            target_chunk="def valid_func():\n    return True",
            replacement_chunk="def valid_func(\n    return True",
        )
        self.assertFalse(patch_res.ok)
        self.assertTrue(patch_res.is_ast_error)
        self.assertIn("AST PRE-FLIGHT SYNTAX ERROR", patch_res.output)
        self.assertEqual(f.read_text(encoding="utf-8"), "def valid_func():\n    return True\n")


class TestSubagentOrchestrator(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.config = CONFIG_V2_0_SBFL_GRAPH
        self.ws = ToolWorkspace(self.test_dir, self.config)
        (self.test_dir / "app.py").write_text("def run():\n    return 1\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_scout_subagent_clean_slate(self):
        mock_client = MockLLMClient(canned_responses=[
            {"content": "Found symbol definition in app.py", "tool_calls": []}
        ])
        coordinator = SubagentCoordinator(self.config, mock_client)
        report = coordinator.delegate_exploration(self.ws, "Find run function")
        self.assertEqual(report.role, "Codebase Scout")
        self.assertIn("Found symbol", report.summary)
        self.assertEqual(len(coordinator.execution_history), 1)


class TestHierarchicalRouter(unittest.TestCase):
    def test_routing_phases_and_escalation(self):
        router = HierarchicalModelRouter(
            planner_model="deepseek/deepseek-v4-pro-0813",
            worker_model="deepseek/deepseek-v4-flash-0731",
            enable_dynamic_escalation=True,
        )
        # Turn 1 should route to Planner
        d1 = router.select_model_for_turn(1, "PLANNING")
        self.assertEqual(d1.selected_model, "deepseek/deepseek-v4-pro-0813")
        self.assertEqual(d1.phase, "PLANNING")

        # Turn 2 should route to Worker
        d2 = router.select_model_for_turn(2, "EXECUTION")
        self.assertEqual(d2.selected_model, "deepseek/deepseek-v4-flash-0731")

        # Two consecutive failures trigger escalation
        router.record_turn_outcome(False)
        router.record_turn_outcome(False)
        d3 = router.select_model_for_turn(3, "EXECUTION")
        self.assertEqual(d3.phase, "ESCALATED_RECOVERY")
        self.assertEqual(d3.selected_model, "deepseek/deepseek-v4-pro-0813")


class TestChallengesAndOracles(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_all_tiers_initial_failure(self):
        tiers = [
            "tier1_lru_cache",
            "tier2_semver_parser",
            "tier3_token_bucket",
            "tier5_datalog_engine",
            "tier6_raft_consensus",
            "tier7_mvcc_storage",
            "tier8_ast_compiler",
        ]
        for t in tiers:
            setup_challenge_workspace(t, self.test_dir)
            self.assertFalse(
                evaluate_challenge_oracle(t, self.test_dir),
                f"Challenge {t} oracle should initially fail on unpatched buggy code"
            )


class TestCatalogAndReceipts(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.catalog = RunCatalog(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_save_and_load_receipt(self):
        receipt = RunReceipt(
            run_id="run_test_001",
            timestamp_utc="2026-08-28T02:00:00Z",
            challenge_id="tier1_lru_cache",
            config_name="v1.2_sota_full",
            version_tag="1.2.0",
            config_hash="abc12345",
            model="openrouter/free",
            seed=42,
            success=True,
            turns_taken=2,
            total_tokens=2874,
            cached_tokens=2048,
            total_cost_usd=0.00033,
            duration_seconds=6.38,
            git_diff_lines=12,
            ast_errors_prevented=1,
            mutation_score=1.0,
            pareto_score=237428.1,
            config_snapshot={},
            kpi_metrics={},
            turn_events=[],
        )
        saved_path = self.catalog.save_run(receipt)
        self.assertTrue(saved_path.is_file())

        loaded = self.catalog.load_run("run_test_001")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.run_id, "run_test_001")
        self.assertTrue(loaded.success)


class TestEngineWithMockLLM(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        setup_challenge_workspace("tier1_lru_cache", self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_engine_executes_tool_calls_from_mock(self):
        canned = [
            {
                "content": "I will read the cache entry file.",
                "tool_calls": [
                    {
                        "function": {
                            "name": "fs_read",
                            "arguments": '{"path": "lru/entry.py"}'
                        }
                    }
                ]
            },
            {
                "content": "Now I will fix the expiration check.",
                "tool_calls": [
                    {
                        "function": {
                            "name": "patch_apply",
                            "arguments": '{"path": "lru/entry.py", "target_chunk": "return False\\n        return False", "replacement_chunk": "return False\\n        return (current_time - self.created_at) > self.ttl_seconds"}'
                        }
                    }
                ]
            },
            {
                "content": "Task complete. The bug is fixed.",
                "tool_calls": []
            }
        ]
        mock_client = MockLLMClient(canned_responses=canned)
        oracle = lambda d: evaluate_challenge_oracle("tier1_lru_cache", d)
        engine = IntelligentMachineEngine(
            workspace_dir=self.test_dir,
            config=CONFIG_V2_3_COMPOUND_FULL,
            llm_client=mock_client,
            oracle_fn=oracle,
        )
        report = engine.run(task_brief="Fix LRU Cache TTL", challenge_id="tier1_lru_cache")
        self.assertTrue(report.success)
        self.assertGreaterEqual(report.turns_taken, 2)


if __name__ == "__main__":
    unittest.main()
