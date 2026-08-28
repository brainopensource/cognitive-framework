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
    CONFIG_BASELINE_REACT,
    CONFIG_VANGUARD_CORE,
    CONFIG_SOTA_FULL,
)
from env_loader import load_openrouter_api_key, has_openrouter_api_key
from tools import ToolWorkspace, ToolExecutionResult
from context_engine import ContextEngine, ContextBlock, ContextLayer
from reproducer_protocol import ReproducerManager, ReproducerPhase
from llm_client import MockLLMClient, LLMResponse, estimate_cost
from challenges import CHALLENGES, setup_challenge_workspace, evaluate_challenge_oracle
from engine import IntelligentMachineEngine


class TestConfig(unittest.TestCase):
    def test_presets(self):
        self.assertFalse(CONFIG_BASELINE_REACT.use_ast_preflight)
        self.assertFalse(CONFIG_BASELINE_REACT.use_l1_l5_prefix_stability)
        
        self.assertTrue(CONFIG_VANGUARD_CORE.use_l1_l5_prefix_stability)
        self.assertTrue(CONFIG_VANGUARD_CORE.use_dialogue_compaction)
        self.assertFalse(CONFIG_VANGUARD_CORE.use_ast_preflight)
        
        self.assertTrue(CONFIG_SOTA_FULL.use_ast_preflight)
        self.assertTrue(CONFIG_SOTA_FULL.use_reproduce_first)
        self.assertTrue(CONFIG_SOTA_FULL.use_speculative_rollback)
        self.assertTrue(CONFIG_SOTA_FULL.use_paged_output)


class TestEnvLoader(unittest.TestCase):
    def test_key_loading(self):
        key = load_openrouter_api_key()
        # Should be a string without raising
        self.assertIsInstance(key, str)


class TestToolsAndASTPreflight(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.config = CONFIG_SOTA_FULL
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


class TestContextEngine(unittest.TestCase):
    def test_compaction_and_dead_ends(self):
        engine = ContextEngine(CONFIG_SOTA_FULL, "System Prompt", "Task Brief")
        engine.record_dead_end("Modifying tokenizer failed test 3")
        
        # Add bulky tool output
        engine.add_tool_receipt("fs_read", "A" * 5000, is_large=True)
        engine.add_turn_assistant("Let me try another approach.")
        
        # Trigger compaction with small ceiling
        elided = engine.compact(ceiling_tokens=100)
        self.assertGreater(elided, 0)
        
        messages = engine.compile_messages()
        self.assertTrue(any("AVOIDED DEAD ENDS" in m["content"] for m in messages))


class TestChallengesAndOracles(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_tier1_lru_oracle_fails_initially_and_passes_after_fix(self):
        challenge = setup_challenge_workspace("tier1_lru_cache", self.test_dir)
        # Initially failing
        self.assertFalse(evaluate_challenge_oracle("tier1_lru_cache", self.test_dir))
        
        # Apply fix to lru/entry.py
        entry_file = self.test_dir / "lru" / "entry.py"
        entry_file.write_text(
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
        
        # Now oracle should pass!
        self.assertTrue(evaluate_challenge_oracle("tier1_lru_cache", self.test_dir))

    def test_tier5_datalog_oracle(self):
        challenge = setup_challenge_workspace("tier5_datalog_engine", self.test_dir)
        # Initially failing
        self.assertFalse(evaluate_challenge_oracle("tier5_datalog_engine", self.test_dir))


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
            config=CONFIG_SOTA_FULL,
            llm_client=mock_client,
            oracle_fn=oracle,
        )
        report = engine.run(task_brief="Fix LRU Cache TTL", challenge_id="tier1_lru_cache")
        self.assertTrue(report.success)
        self.assertGreaterEqual(report.turns_taken, 2)


if __name__ == "__main__":
    unittest.main()
