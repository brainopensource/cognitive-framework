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


class TestEnvLoader(unittest.TestCase):
    def test_key_loading(self):
        key = load_openrouter_api_key()
        self.assertIsInstance(key, str)


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

        # Attempt to patch with a syntax error (missing colon, mismatched parens)
        patch_res = self.ws.patch_apply(
            path="broken.py",
            target_chunk="def valid_func():\n    return True",
            replacement_chunk="def valid_func(\n    return True",
        )
        self.assertFalse(patch_res.ok)
        self.assertTrue(patch_res.is_ast_error)
        self.assertIn("AST PRE-FLIGHT SYNTAX ERROR", patch_res.output)
        
        # File should remain uncorrupted
        self.assertEqual(f.read_text(encoding="utf-8"), "def valid_func():\n    return True\n")

    def test_paged_output_truncation(self):
        long_output = "\n".join(f"Line {i}" for i in range(200))
        truncated = self.ws._truncate_output(long_output)
        lines = truncated.splitlines()
        self.assertLessEqual(len(lines), 85)
        self.assertIn("Line 0", truncated)
        self.assertIn("Line 199", truncated)
        self.assertIn("truncated for token efficiency", truncated)


class TestCodeGraph(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.code_file = self.test_dir / "calc.py"
        self.code_file.write_text(
            "class Calculator:\n"
            "    def add(self, a, b):\n"
            "        return a + b\n\n"
            "def run_calc():\n"
            "    c = Calculator()\n"
            "    return c.add(1, 2)\n",
            encoding="utf-8"
        )
        self.graph = ASTCodeGraph(self.test_dir)
        self.graph.index_workspace()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_symbol_extraction_and_skeleton(self):
        defs = self.graph.find_definitions("Calculator")
        self.assertEqual(len(defs), 1)
        self.assertEqual(defs[0].kind, "class")

        func_defs = self.graph.find_definitions("run_calc")
        self.assertEqual(len(func_defs), 1)

        skeleton = self.graph.generate_compact_skeleton()
        self.assertIn("CALC.PY", skeleton.upper())
        self.assertIn("CALCULATOR", skeleton.upper())
        self.assertIn("RUN_CALC", skeleton.upper())


class TestFaultLocalization(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.sbfl = SBFLEngine(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_sbfl_ochiai_scoring(self):
        failing_trace = {("datalog/engine.py", 42), ("datalog/engine.py", 43)}
        passing_trace = {("datalog/engine.py", 10)}
        rankings = self.sbfl.compute_rankings([failing_trace], [passing_trace])
        
        self.assertGreater(len(rankings), 0)
        # Statements in failing trace should have highest Ochiai score (1.0)
        self.assertEqual(rankings[0].ochiai_score, 1.0)
        prompt_txt = self.sbfl.format_for_prompt(rankings, top_k=2)
        self.assertIn("SBFL Fault Localization", prompt_txt)


class TestMutationVerifier(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.target = self.test_dir / "logic.py"
        self.target.write_text(
            "def check_limit(val):\n"
            "    if val > 10:\n"
            "        return True\n"
            "    return False\n",
            encoding="utf-8"
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_mutant_generation_and_falsification(self):
        oracle_fn = lambda: True # Lax oracle that accepts anything
        verifier = PatchMutationVerifier(self.test_dir, oracle_fn)
        card = verifier.falsify_patch("logic.py", [1, 2])
        self.assertGreater(card.total_mutants, 0)
        # Since oracle always passes, mutants survive -> low kill score
        self.assertEqual(card.killed_mutants, 0)
        self.assertFalse(card.is_general)


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
        self.assertEqual(loaded.turns_taken, 2)
        self.assertTrue(loaded.success)

        runs = self.catalog.list_runs(challenge_id="tier1_lru_cache")
        self.assertEqual(len(runs), 1)


class TestContextEngine(unittest.TestCase):
    def test_compaction_and_dead_ends(self):
        engine = ContextEngine(CONFIG_V1_2_SOTA_FULL, "System Prompt", "Task Brief")
        engine.record_dead_end("Modifying tokenizer failed test 3")
        
        engine.add_tool_receipt("fs_read", "A" * 5000, is_large=True)
        engine.add_turn_assistant("Let me try another approach.")
        
        elided = engine.compact(ceiling_tokens=100)
        self.assertGreater(elided, 0)
        
        messages = engine.compile_messages()
        self.assertTrue(any("AVOIDED DEAD ENDS" in m["content"] for m in messages))


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
        self.assertIn("mps_model_pareto_score", report.kpi_metrics)


class TestParametricOverrides(unittest.TestCase):
    def test_parse_override_string(self):
        s = "use_code_graph=True,max_turns=25,temperature=0.7,config_name=custom_test"
        res = parse_override_string(s)
        self.assertTrue(res["use_code_graph"])
        self.assertEqual(res["max_turns"], 25)
        self.assertEqual(res["temperature"], 0.7)
        self.assertEqual(res["config_name"], "custom_test")


if __name__ == "__main__":
    unittest.main()
