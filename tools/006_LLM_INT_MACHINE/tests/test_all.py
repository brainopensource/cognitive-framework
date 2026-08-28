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

    def test_preset_retrieval(self):
        cfg_100 = get_preset("sota_100")
        self.assertEqual(cfg_100.config_name, "v4.5_sota_100_apex")
        self.assertTrue(cfg_100.use_cluster_mcts)

        cfg_cegis = get_preset("cegis")
        self.assertEqual(cfg_cegis.config_name, "v4.0_cegis_smt")


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
        res = self.workspace.patch_apply(
            path="sample.py",
            target_chunk="    return a + b",
            replacement_chunk="    # return sum\n    return a + b",
        )
        self.assertTrue(res.ok)
        self.assertIn("Successfully patched", res.output)

        # Invalid syntax patch
        res_bad = self.workspace.patch_apply(
            path="sample.py",
            target_chunk="    return a + b",
            replacement_chunk="    return a + (bad syntax",
        )
        self.assertFalse(res_bad.ok)
        self.assertIn("AST PRE-FLIGHT SYNTAX ERROR", res_bad.output)


class TestCEGISAndConcolicFuzzing(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        sample = self.test_dir / "calc.py"
        sample.write_text(
            "def safe_divide(x: int) -> int:\n"
            "    assert x != 0, 'Cannot divide by zero'\n"
            "    if x > 10:\n"
            "        return x * 2\n"
            "    return x // 2\n",
            encoding="utf-8"
        )
        self.cegis = CEGISSolver(self.test_dir)
        self.concolic = ConcolicPathFuzzer(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_cegis_contract_extraction_and_counterexample(self):
        contracts = self.cegis.extract_function_contracts("calc.py", "safe_divide")
        self.assertGreaterEqual(len(contracts), 1)

        # Sound function
        sound_rep = self.cegis.synthesize_counterexamples(lambda x: x + 1, {"x": int})
        self.assertTrue(sound_rep.verified_sound)

        # Violating function that raises ZeroDivisionError on 0
        def buggy(x):
            return 10 // x
        viol_rep = self.cegis.synthesize_counterexamples(buggy, {"x": int})
        self.assertFalse(viol_rep.verified_sound)
        self.assertGreaterEqual(len(viol_rep.counterexamples), 1)
        feedback = self.cegis.format_cegis_feedback_prompt(viol_rep)
        self.assertIn("SMT / CEGIS Invariant Counterexample Alert", feedback)

    def test_concolic_branch_coverage(self):
        branches = self.concolic.discover_ast_branches("calc.py")
        self.assertGreaterEqual(len(branches), 1)
        
        rep = self.concolic.execute_concolic_analysis("calc.py")
        self.assertGreaterEqual(rep.total_branches_discovered, 2)
        self.assertGreaterEqual(rep.coverage_ratio, 0.5)


class TestArenaAndDebuggerAndSkills(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        sample = self.test_dir / "app.py"
        sample.write_text("def run():\n    return 42\n", encoding="utf-8")
        self.ws = ToolWorkspace(self.test_dir, CONFIG_V1_2_SOTA_FULL)
        self.arena = ArenaTournament(self.ws)
        self.debugger = TimeTravelDebugger(max_history_steps=100)
        self.skills = DynamicSkillCompiler(self.test_dir)
        self.cluster = ClusterMCTSSearch(self.ws, sample_size=4)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_arena_tournament(self):
        proposals = [
            {
                "role": "minimal_diff",
                "patch": {"path": "app.py", "target_chunk": "return 42", "replacement_chunk": "return 100"}
            },
            {
                "role": "bad_syntax",
                "patch": {"path": "app.py", "target_chunk": "return 42", "replacement_chunk": "return 100 + ("}
            }
        ]
        rep = self.arena.run_tournament(
            candidate_proposals=proposals,
            oracle_evaluator=lambda: True,
            adversarial_tests=[lambda: True],
        )
        self.assertIsNotNone(rep.winner_patch)
        self.assertEqual(rep.winner_candidate_id, "arena_cand_1")

    def test_time_travel_debugger(self):
        snap1 = self.debugger.record_frame("app.py", "run", 1, {"count": 1})
        snap2 = self.debugger.record_frame("app.py", "run", 2, {"count": 2})
        self.assertEqual(len(self.debugger.history), 2)
        
        back = self.debugger.step_backward(1)
        self.assertEqual(back.step_index, 1)

        step_idx, frame = self.debugger.find_state_corruption_point(lambda v: v.get("count") != "2")
        self.assertEqual(step_idx, 2)

    def test_dynamic_skill_compiler(self):
        code = "def custom_ast_helper(x):\n    return x * 10\n"
        ok, msg = self.skills.compile_and_register_skill(
            skill_name="custom_ast_helper",
            description="Multiplies by 10",
            python_code=code,
            test_assertion=lambda: True,
        )
        self.assertTrue(ok)
        out = self.skills.execute_skill("custom_ast_helper", x=5)
        self.assertEqual(out, 50)

    def test_cluster_mcts_search(self):
        def sampler(temp):
            return {"path": "app.py", "target_chunk": "return 42", "replacement_chunk": f"return {int(temp*100)}"}
        rep = self.cluster.run_cluster_search(sampler, lambda: True)
        self.assertIsNotNone(rep.winning_patch)


class TestChallengesAndOracles(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_tier1_lru_cache_setup_and_oracle(self):
        setup_challenge_workspace("tier1_lru_cache", self.test_dir)
        self.assertFalse(evaluate_challenge_oracle("tier1_lru_cache", self.test_dir))

        entry_p = self.test_dir / "lru" / "entry.py"
        entry_content = entry_p.read_text(encoding="utf-8")
        fixed_content = entry_content.replace("return False\n        return False", "return False\n        return (current_time - self.created_at) > self.ttl_seconds")
        entry_p.write_text(fixed_content, encoding="utf-8")
        self.assertTrue(evaluate_challenge_oracle("tier1_lru_cache", self.test_dir))


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
            config=CONFIG_V4_5_SOTA_100_APEX,
            llm_client=mock_client,
            oracle_fn=oracle,
        )
        report = engine.run(task_brief="Fix LRU Cache TTL", challenge_id="tier1_lru_cache")
        self.assertTrue(report.success)
        self.assertGreaterEqual(report.turns_taken, 2)


if __name__ == "__main__":
    unittest.main()
