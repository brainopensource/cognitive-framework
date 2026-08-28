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
    CONFIG_V3_0_CAUSAL_MCTS,
    CONFIG_V3_1_ADVERSARIAL_APEX,
    CONFIG_V3_2_RLVR_SOTA_90,
    CONFIG_V4_0_CEGIS_SMT,
    CONFIG_V4_1_CONCOLIC_DSE,
    CONFIG_V4_2_ARENA_DEBATE,
    CONFIG_V4_3_TIMETRAVEL_REPLAY,
    CONFIG_V4_4_HERMES_SKILLS,
    CONFIG_V4_5_SOTA_100_APEX,
    CONFIG_V5_0_HIERARCHICAL_APEX,
    CONFIG_V5_1_FREE_TIER,
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
from coverage_sbfl import CoverageBackedSBFL
from mcts_search import SpeculativeMCTSSearch
from mutation_verifier import PatchMutationVerifier
from subagent_orchestrator import SubagentCoordinator, SubagentSandbox
from hierarchical_router import HierarchicalModelRouter
from causal_slicing import CausalFaultLocalizer, CausalStatementRank
from adversarial_fuzzer import AdversarialInvariantFuzzer, AdversarialFuzzReport
from rlvr_trajectory_engine import RLVREngine, RLVREpisodeTrajectory
from cegis_solver import CEGISSolver, CEGISSynthesisReport
from concolic_fuzzer import ConcolicPathFuzzer, ConcolicCoverageReport
from arena_tournament import ArenaTournament, ArenaTournamentReport
from time_travel_debugger import TimeTravelDebugger, TimeTravelDebugTrace
from skill_compiler import DynamicSkillCompiler, CompiledSkill
from cluster_mcts import ClusterMCTSSearch, ClusterMCTSReport
from telemetry_kpi import AdvancedKPITelemetry
from catalog import RunCatalog, RunReceipt, generate_run_id
from experiment_matrix import run_multi_trial_experiment, parse_override_string


class TestConfigAndRegistry(unittest.TestCase):
    def test_presets(self):
        self.assertFalse(CONFIG_V1_0_BASELINE.use_ast_preflight)
        self.assertTrue(CONFIG_V1_2_SOTA_FULL.use_ast_preflight)
        self.assertTrue(CONFIG_V2_0_SBFL_GRAPH.use_sbfl_localization)
        self.assertTrue(CONFIG_V2_3_COMPOUND_FULL.use_mutation_testing)
        self.assertTrue(CONFIG_V3_2_RLVR_SOTA_90.use_rlvr_logging)

        # Test 100% Frontier Presets v4.0 - v4.5
        self.assertTrue(CONFIG_V4_0_CEGIS_SMT.use_cegis_verification)
        self.assertTrue(CONFIG_V4_1_CONCOLIC_DSE.use_concolic_fuzzing)
        self.assertTrue(CONFIG_V4_2_ARENA_DEBATE.use_arena_tournament)
        self.assertTrue(CONFIG_V4_3_TIMETRAVEL_REPLAY.use_time_travel_debugger)
        self.assertTrue(CONFIG_V4_4_HERMES_SKILLS.use_dynamic_skills)
        self.assertTrue(CONFIG_V4_5_SOTA_100_APEX.use_cluster_mcts)
        self.assertEqual(CONFIG_V4_5_SOTA_100_APEX.cluster_mcts_samples, 32)

        # Test v5.0 and v5.1 Multi-Model Routing Presets
        self.assertTrue(CONFIG_V5_0_HIERARCHICAL_APEX.enable_hierarchical_routing)
        self.assertEqual(CONFIG_V5_0_HIERARCHICAL_APEX.resolve_planner(), "deepseek/deepseek-v4-pro-0813")
        self.assertEqual(CONFIG_V5_0_HIERARCHICAL_APEX.resolve_worker(), "deepseek/deepseek-v4-flash-0731")
        self.assertTrue(CONFIG_V5_1_FREE_TIER.use_lightweight_prompt)
        self.assertEqual(CONFIG_V5_1_FREE_TIER.max_cost_usd, 0.0)

    def test_preset_retrieval(self):
        cfg_100 = get_preset("sota_100")
        self.assertEqual(cfg_100.config_name, "v4.5_sota_100_apex")
        self.assertTrue(cfg_100.use_cluster_mcts)

        cfg_cegis = get_preset("cegis")
        self.assertEqual(cfg_cegis.config_name, "v4.0_cegis_smt")

        cfg_v50 = get_preset("v5.0")
        self.assertEqual(cfg_v50.config_name, "v5.0_hierarchical_apex")


class TestToolsWorkspaceAndAST(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.workspace = ToolWorkspace(self.test_dir, CONFIG_V1_2_SOTA_FULL)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_patch_apply_with_ast_preflight(self):
        file_p = self.test_dir / "sample.py"
        file_p.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
        
        # Valid patch
        res = self.workspace.patch_apply("sample.py", "return a + b", "return a - b")
        self.assertTrue(res.ok)
        self.assertIn("return a - b", file_p.read_text(encoding="utf-8"))

        # Broken syntax patch
        res_broken = self.workspace.patch_apply("sample.py", "return a - b", "return a - ")
        self.assertFalse(res_broken.ok)
        self.assertTrue(res_broken.is_ast_error)
        self.assertEqual(self.workspace.ast_errors_caught, 1)


class TestContextAndCompaction(unittest.TestCase):
    def test_context_compaction_and_tool_role(self):
        cfg = HarnessConfig(token_ceiling=100, use_dialogue_compaction=True)
        ctx = ContextEngine(cfg, "System instructions", "Task description")
        
        ctx.add_tool_receipt("fs_read", "line " * 50)
        ctx.add_turn_assistant("Let me fix this.")
        ctx.add_tool_receipt("proc_exec", "Test error: assertion failure")
        
        msgs = ctx.compile_messages()
        self.assertTrue(any(m["role"] == "system" for m in msgs))
        self.assertTrue(any(m["role"] == "user" for m in msgs))
        # Tool receipts must use role="tool"
        self.assertTrue(any(m.get("role") == "tool" for m in msgs))

    def test_semantic_compaction_with_mock(self):
        cfg = HarnessConfig(token_ceiling=30, use_dialogue_compaction=True)
        ctx = ContextEngine(cfg, "System instructions", "Task description")
        ctx.add_turn_user("Turn 1 user input with lots of tokens " * 10)
        ctx.add_turn_assistant("Turn 1 assistant answer with details " * 10)
        ctx.add_tool_receipt("proc_exec", "Failure in tests " * 10)
        ctx.add_turn_assistant("Turn 2 assistant proposal " * 10)
        
        mock_llm = MockLLMClient(["1. Location: main.py\n2. Hypothesis: off-by-one\n3. Patch failed: None"])
        elided = ctx.compact_with_llm(mock_llm)
        self.assertEqual(elided, 1)
        self.assertTrue(any("Semantic Summary" in b.text for b in ctx.dialogue_blocks))


class TestCEGISAndConcolicFuzzing(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_cegis_contract_extraction_and_counterexample(self):
        solver = CEGISSolver(self.test_dir)
        p = self.test_dir / "tested_math.py"
        p.write_text(
            "def safe_divide(a: int, b: int) -> float:\n"
            "    assert b != 0, 'b must not be zero'\n"
            "    return a / b\n",
            encoding="utf-8"
        )
        contracts = solver.extract_function_contracts("tested_math.py", "safe_divide")
        self.assertTrue(len(contracts) >= 1)

        # Counterexample finding for function that crashes on 0
        def buggy_div(x: int) -> float:
            if x == 0:
                raise ZeroDivisionError("division by zero")
            return 10.0 / x

        rep = solver.synthesize_counterexamples(buggy_div, {"x": int})
        self.assertFalse(rep.verified_sound)
        self.assertTrue(len(rep.counterexamples) > 0)
        prompt = solver.format_cegis_feedback_prompt(rep)
        self.assertIn("SMT / CEGIS Invariant Counterexample Alert", prompt)

    def test_concolic_branch_analysis(self):
        p = self.test_dir / "branch_code.py"
        p.write_text(
            "def check_bounds(val: int) -> bool:\n"
            "    if val > 100:\n"
            "        return True\n"
            "    elif val < 0:\n"
            "        return False\n"
            "    return True\n",
            encoding="utf-8"
        )
        fuzzer = ConcolicPathFuzzer(self.test_dir)
        rep = fuzzer.execute_concolic_analysis("branch_code.py")
        self.assertTrue(rep.total_branches_discovered >= 2)


class TestArenaAndDebuggerAndSkills(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.workspace = ToolWorkspace(self.test_dir, CONFIG_V1_2_SOTA_FULL)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_arena_tournament_scoring(self):
        sample_p = self.test_dir / "sample.py"
        sample_p.write_text("def foo():\n    return 0\n", encoding="utf-8")
        
        arena = ArenaTournament(self.workspace)
        candidates = [
            {
                "role": "worker",
                "patch": {"path": "sample.py", "target_chunk": "    return 0", "replacement_chunk": "    return 1"}
            },
            {
                "role": "supervisor",
                "patch": {"path": "sample.py", "target_chunk": "    return 0", "replacement_chunk": "    return 2"}
            },
        ]
        rep = arena.run_tournament(candidates, oracle_evaluator=lambda: True)
        self.assertIsNotNone(rep.winner_candidate_id)

    def test_time_travel_debugger(self):
        tt = TimeTravelDebugger()
        tt.record_frame("main.py", "setup", 10, {"count": 1})
        tt.record_frame("main.py", "mutate", 15, {"count": 2})
        self.assertEqual(len(tt.history), 2)
        step = tt.step_backward()
        self.assertEqual(step.step_index, 1)

    def test_skill_compiler(self):
        sc = DynamicSkillCompiler(self.test_dir)
        code = "def custom_sum(a, b):\n    return a + b\n"
        ok, msg = sc.compile_and_register_skill("custom_sum_skill", "Sums two values", code)
        self.assertTrue(ok)
        self.assertIn("custom_sum_skill", sc.registry)


class TestChallengesAndOracles(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_tier1_lru_cache_oracle(self):
        setup_challenge_workspace("tier1_lru_cache", self.test_dir)
        # Buggy initial state -> oracle must fail
        self.assertFalse(evaluate_challenge_oracle("tier1_lru_cache", self.test_dir))

        # Apply fix to lru/entry.py
        entry_p = self.test_dir / "lru" / "entry.py"
        entry_p.write_text(
            "import time\n"
            "from dataclasses import dataclass\n"
            "from typing import Any, Optional\n\n"
            "@dataclass\n"
            "class CacheEntry:\n"
            "    key: str\n"
            "    value: Any\n"
            "    ttl_seconds: Optional[float]\n"
            "    created_at: float\n\n"
            "    def is_expired(self, current_time: float) -> bool:\n"
            "        if self.ttl_seconds is None:\n"
            "            return False\n"
            "        return (current_time - self.created_at) > self.ttl_seconds\n",
            encoding="utf-8"
        )
        self.assertTrue(evaluate_challenge_oracle("tier1_lru_cache", self.test_dir))

    def test_multi_file_challenges_exist(self):
        self.assertIn("tier4_plugin_registry", CHALLENGES)
        self.assertIn("tier4_async_event_bus", CHALLENGES)
        self.assertIn("tier5_layered_cache", CHALLENGES)
        self.assertIn("tier5_schema_migration", CHALLENGES)
        self.assertIn("tier6_sharded_counter", CHALLENGES)
        self.assertEqual(len(CHALLENGES), 12)


class TestCoverageBackedSBFL(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.sbfl = SBFLEngine(self.test_dir)
        self.cov_sbfl = CoverageBackedSBFL(self.test_dir, self.sbfl)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_coverage_ranking_execution(self):
        src = self.test_dir / "calc.py"
        src.write_text("def div(a, b):\n    return a / b\n", encoding="utf-8")
        oracle = "import unittest\nfrom calc import div\nclass T(unittest.TestCase):\n    def test_fail(self):\n        div(1, 0)\nif __name__ == '__main__':\n    unittest.main()\n"
        rankings = self.cov_sbfl.compute_real_rankings(oracle)
        # Rankings computed without crashing
        self.assertIsInstance(rankings, list)


class TestEngineWithMockLLM(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_engine_executes_v5_hierarchical_apex(self):
        setup_challenge_workspace("tier1_lru_cache", self.test_dir)
        
        target_snip = "        if self.ttl_seconds is None:\n            return False\n        return False"
        replacement_snip = "        if self.ttl_seconds is None:\n            return False\n        return (current_time - self.created_at) > self.ttl_seconds"

        canned = [
            # Scout Subagent exploration
            {"content": "Located bug in lru/entry.py", "tool_calls": []},
            # Main turn 1: read file
            {
                "content": "Let me read entry.py",
                "tool_calls": [
                    {
                        "function": {
                            "name": "fs_read",
                            "arguments": '{"path": "lru/entry.py", "start_line": 1, "line_count": 50}'
                        }
                    }
                ]
            },
            # Main turn 2: apply patch
            {
                "content": "Applying fix to TTL check",
                "tool_calls": [
                    {
                        "function": {
                            "name": "patch_apply",
                            "arguments": {
                                "path": "lru/entry.py",
                                "target_snippet": target_snip,
                                "replacement_snippet": replacement_snip
                            }
                        }
                    }
                ]
            },
            # Main turn 3: task complete
            {
                "content": "The bug in lru/entry.py is resolved. TASK COMPLETE.",
                "tool_calls": []
            }
        ]

        mock_llm = MockLLMClient(canned)
        engine = IntelligentMachineEngine(
            workspace_dir=self.test_dir,
            config=CONFIG_V5_0_HIERARCHICAL_APEX,
            llm_client=mock_llm,
            oracle_fn=lambda ws: evaluate_challenge_oracle("tier1_lru_cache", ws),
        )

        report = engine.run("Fix the LRU Cache TTL expiration logic.", challenge_id="tier1_lru_cache")
        self.assertTrue(report.success)
        self.assertTrue(report.turns_taken >= 2)
        self.assertIn("mps_model_pareto_score", report.kpi_metrics)


if __name__ == "__main__":
    unittest.main()
