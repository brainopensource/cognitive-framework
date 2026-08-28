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
        self.assertTrue(CONFIG_V2_3_COMPOUND_FULL.use_mutation_testing)
        self.assertTrue(CONFIG_V2_3_COMPOUND_FULL.use_mcts_search)

        # Test Pillar v3.0, v3.1, v3.2 presets
        self.assertTrue(CONFIG_V3_0_CAUSAL_MCTS.use_causal_slicing)
        self.assertTrue(CONFIG_V3_1_ADVERSARIAL_APEX.use_adversarial_fuzzing)
        self.assertTrue(CONFIG_V3_2_RLVR_SOTA_90.use_rlvr_logging)
        self.assertEqual(CONFIG_V3_2_RLVR_SOTA_90.mcts_branching_factor, 8)

    def test_preset_retrieval(self):
        cfg = get_preset("v2.0_sbfl_graph")
        self.assertEqual(cfg.config_name, "v2.0_sbfl_graph")
        self.assertTrue(cfg.use_sbfl_localization)

        cfg_apex = get_preset("apex")
        self.assertEqual(cfg_apex.config_name, "v3.1_adversarial_apex")

        with self.assertRaises(KeyError):
            get_preset("non_existent_preset")

    def test_config_hash_determinism(self):
        cfg1 = CONFIG_V1_2_SOTA_FULL
        cfg2 = CONFIG_V1_2_SOTA_FULL
        self.assertEqual(cfg1.config_hash(), cfg2.config_hash())
        
        cfg_modified = cfg1.derive(temperature=0.7)
        self.assertNotEqual(cfg1.config_hash(), cfg_modified.config_hash())


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


class TestCausalRepairAndFuzzing(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        sample = self.test_dir / "math_ops.py"
        sample.write_text("def divide(a, b):\n    if b == 0:\n        return None\n    return a / b\n", encoding="utf-8")
        self.causal = CausalFaultLocalizer(self.test_dir)
        self.fuzzer = AdversarialInvariantFuzzer(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_causal_slicing_computation(self):
        deps = self.causal.parse_data_dependencies("math_ops.py")
        self.assertIn(1, deps)
        self.assertIn("a", deps[1])
        self.assertIn("b", deps[1])

        failing = [{("math_ops.py", 4)}]
        passing = [{("math_ops.py", 1), ("math_ops.py", 2)}]
        ranks = self.causal.compute_causal_rankings(failing, passing)
        self.assertGreaterEqual(len(ranks), 1)
        self.assertGreater(ranks[0].causal_effect, 0.5)

        injection = self.causal.format_causal_prompt_injection(ranks)
        self.assertIn("CausalRepair", injection)

    def test_adversarial_fuzzer(self):
        probes = self.fuzzer.generate_boundary_probes()
        self.assertGreaterEqual(len(probes), 5)
        
        # Test safe function
        rep = self.fuzzer.verify_patch_robustness(test_callable=lambda x: True)
        self.assertTrue(rep.is_adversarially_sound)
        self.assertEqual(rep.robustness_score, 1.0)


class TestRLVREngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.rlvr = RLVREngine(output_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_rlvr_trajectory_recording(self):
        traj = self.rlvr.start_episode("traj_001", "tier1_lru_cache", "mock-model", "v3.2_rlvr_sota_90")
        self.assertEqual(traj.trajectory_id, "traj_001")

        reward_step = self.rlvr.record_step(
            trajectory_id="traj_001",
            turn_index=1,
            prompt_messages=[{"role": "user", "content": "fix bug"}],
            model_response_content="applying patch",
            tool_calls=[{"name": "patch_apply"}],
            tool_results=[{"ok": True}],
            ast_valid=True,
        )
        self.assertEqual(reward_step, 0.2)

        final_reward = self.rlvr.finalize_episode(
            trajectory_id="traj_001",
            final_oracle_passed=True,
            mutation_score=1.0,
        )
        self.assertGreater(final_reward, 0.5)
        self.assertTrue((self.test_dir / "traj_001.jsonl").is_file())


class TestChallengesAndOracles(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_tier1_lru_cache_setup_and_oracle(self):
        setup_challenge_workspace("tier1_lru_cache", self.test_dir)
        self.assertFalse(evaluate_challenge_oracle("tier1_lru_cache", self.test_dir))

        # Fix LRU cache bug
        entry_p = self.test_dir / "lru" / "entry.py"
        entry_content = entry_p.read_text(encoding="utf-8")
        fixed_content = entry_content.replace("return False\n        return False", "return False\n        return (current_time - self.created_at) > self.ttl_seconds")
        entry_p.write_text(fixed_content, encoding="utf-8")
        self.assertTrue(evaluate_challenge_oracle("tier1_lru_cache", self.test_dir))

    def test_tier6_raft_consensus_setup_and_oracle(self):
        setup_challenge_workspace("tier6_raft_consensus", self.test_dir)
        self.assertFalse(evaluate_challenge_oracle("tier6_raft_consensus", self.test_dir))

    def test_tier8_ast_compiler_setup_and_oracle(self):
        setup_challenge_workspace("tier8_ast_compiler", self.test_dir)
        self.assertFalse(evaluate_challenge_oracle("tier8_ast_compiler", self.test_dir))


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
            config=CONFIG_V3_2_RLVR_SOTA_90,
            llm_client=mock_client,
            oracle_fn=oracle,
        )
        report = engine.run(task_brief="Fix LRU Cache TTL", challenge_id="tier1_lru_cache")
        self.assertTrue(report.success)
        self.assertGreaterEqual(report.turns_taken, 2)


if __name__ == "__main__":
    unittest.main()
