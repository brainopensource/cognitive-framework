"""Unit and integration tests for 1-Forge (Reflexive Agentic Micro-Forge).

Tests:
1. ForgeAtomicPatcher (unified diffs, block replace, AST replace, atomic rollback).
2. ForgeContextCompiler & ForgeDistillStrategy (RFC-8785 canonicalization, token pruning).
3. ForgeAdmissionGate & GoalContract (closed-loop verification gate, freshness binding).
4. Reflex Policy & Rules (repeated failure detection, no-progress detection).
5. ForgeEngine fast-cycle TDD execution loop.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from vanguard.packages.agency.context.layers import Block, Layer
from vanguard.packages.agency.forge import (
    ASTPatcher,
    AdmissionVerdict,
    BlockPatcher,
    FailureFingerprint,
    FilePatch,
    ForgeAdmissionGate,
    ForgeAtomicPatcher,
    ForgeConfig,
    ForgeContextCompiler,
    ForgeDistillStrategy,
    ForgeEngine,
    ForgeFacade,
    ForgeOutcome,
    ForgeWorkingState,
    GoalContract,
    NoProgressRule,
    PatchHunk,
    PatchResult,
    RepeatedFailureRule,
    UnifiedDiffParser,
    VerificationReceipt,
    compute_workspace_digest,
    parse_test_output,
)


class ScriptedForgeModel:
    """Scripted model double for predictable 1-Forge testing."""

    def __init__(self, turns_proposals: Sequence[Mapping[str, Any]]) -> None:
        self.proposals = list(turns_proposals)
        self.cursor = 0
        self.recorded_contexts: list[Mapping[str, Any]] = []

    def propose(self, context: Mapping[str, Any], tools: Any, sampling: Any) -> Any:
        self.recorded_contexts.append(dict(context))
        if self.cursor >= len(self.proposals):
            return {
                "message": {"content": "I have completed all steps.", "tool_calls": []},
                "usage": {"prompt_tokens": 100, "completion_tokens": 20, "cost": 0.0001},
            }
        p = self.proposals[self.cursor]
        self.cursor += 1
        return {
            "message": {
                "content": p.get("content", ""),
                "tool_calls": p.get("tool_calls", []),
            },
            "usage": {"prompt_tokens": 150, "completion_tokens": 30, "cost": 0.0002},
        }


class TestForgePatcher(unittest.TestCase):
    """Tests for ForgeAtomicPatcher."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="forge-patch-test-")
        self.ws = Path(self.temp_dir)
        self.patcher = ForgeAtomicPatcher(self.ws)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_file_write_atomic_and_syntax_validation(self) -> None:
        # 1. Valid file write
        res = self.patcher.apply_file_write("src/calc.py", "def add(a, b):\n    return a + b\n")
        self.assertTrue(res.success)
        self.assertEqual(res.changed_files, ("src/calc.py",))
        self.assertTrue((self.ws / "src" / "calc.py").is_file())

        # 2. Invalid syntax triggers rollback
        orig_content = (self.ws / "src" / "calc.py").read_text(encoding="utf-8")
        bad_res = self.patcher.apply_file_write("src/calc.py", "def broken_func(\n    return a + \n")
        self.assertFalse(bad_res.success)
        self.assertIn("SyntaxError", bad_res.error or "")
        # Content remains original
        self.assertEqual((self.ws / "src" / "calc.py").read_text(encoding="utf-8"), orig_content)

    def test_block_replace_exact_and_normalized(self) -> None:
        file_p = self.ws / "src" / "service.py"
        file_p.parent.mkdir(parents=True, exist_ok=True)
        file_p.write_text("class Service:\n    def run(self):\n        return False\n", encoding="utf-8")

        # Exact replacement
        res = self.patcher.apply_block_replace(
            "src/service.py",
            "return False",
            "return True",
            mode="exact",
        )
        self.assertTrue(res.success)
        self.assertIn("return True", file_p.read_text(encoding="utf-8"))

        # Normalized whitespace replacement
        res2 = self.patcher.apply_block_replace(
            "src/service.py",
            "def run(self):\n      return True",
            "def run(self):\n        return 42",
            mode="normalized_ws",
        )
        self.assertTrue(res2.success)
        self.assertIn("return 42", file_p.read_text(encoding="utf-8"))

    def test_ast_replace(self) -> None:
        file_p = self.ws / "src" / "math_ops.py"
        file_p.parent.mkdir(parents=True, exist_ok=True)
        file_p.write_text("def multiply(x, y):\n    return x - y\n\ndef divide(x, y):\n    return x / y\n", encoding="utf-8")

        res = self.patcher.apply_ast_replace(
            "src/math_ops.py",
            "multiply",
            "def multiply(x, y):\n    return x * y",
        )
        self.assertTrue(res.success)
        content = file_p.read_text(encoding="utf-8")
        self.assertIn("return x * y", content)
        self.assertIn("def divide", content)

    def test_unified_diff_application(self) -> None:
        file_p = self.ws / "src" / "greet.py"
        file_p.parent.mkdir(parents=True, exist_ok=True)
        file_p.write_text('def greet(name):\n    return "Hello"\n', encoding="utf-8")

        diff = """--- a/src/greet.py
+++ b/src/greet.py
@@ -1,2 +1,2 @@
 def greet(name):
-    return "Hello"
+    return f"Hello, {name}!"
"""
        res = self.patcher.apply_unified_diff(diff)
        self.assertTrue(res.success)
        self.assertIn('return f"Hello, {name}!"', file_p.read_text(encoding="utf-8"))

    def test_path_traversal_refused(self) -> None:
        with self.assertRaises(Exception):
            self.patcher.apply_file_write("../../../evil.py", "malicious = True")


class TestForgeCompiler(unittest.TestCase):
    """Tests for ForgeContextCompiler and ForgeDistillStrategy."""

    def test_canonical_working_state_digest(self) -> None:
        state1 = ForgeWorkingState(
            task_brief="Fix math bug",
            active_hypothesis="Off by one",
            confirmed_facts=("File exists",),
        )
        state2 = ForgeWorkingState(
            task_brief="Fix math bug",
            active_hypothesis="Off by one",
            confirmed_facts=("File exists",),
        )
        self.assertEqual(state1.digest(), state2.digest())
        self.assertTrue(state1.digest().startswith("sha256:"))

    def test_compaction_distills_long_dialogue(self) -> None:
        compiler = ForgeContextCompiler(token_ceiling=1200)
        dialogue = [
            Block(Layer.DIALOGUE, "model", f"turn_{i}_model", "Inspecting file " * 20, evictable=False)
            for i in range(5)
        ] + [
            Block(Layer.DIALOGUE, "tool", f"pytest_run_{i}", "FAIL: test error traceback " * 30, evictable=True)
            for i in range(10)
        ]
        state = ForgeWorkingState(task_brief="Run tests and fix failures")
        messages, meta = compiler.compile(
            brief="Run tests and fix failures",
            working_state=state,
            dialogue=dialogue,
        )
        self.assertLessEqual(meta["total_tokens"], 1200)
        self.assertGreater(meta["elided_count"] + meta["dropped_count"], 0)
        self.assertGreaterEqual(len(messages), 2)


class TestForgeAdmissionGate(unittest.TestCase):
    """Tests for ForgeAdmissionGate and GoalContract."""

    def setUp(self) -> None:
        self.gate = ForgeAdmissionGate(require_patch_for_write=True)
        self.contract = GoalContract(task_digest="sha256:task123", mode="bugfix")

    def test_rejects_without_changed_files(self) -> None:
        verdict = self.gate.evaluate(
            goal_contract=self.contract,
            changed_files=(),
            current_workspace_digest="sha256:ws1",
        )
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, "MISSING_SOURCE_PATCH")

    def test_rejects_without_verification_receipt(self) -> None:
        verdict = self.gate.evaluate(
            goal_contract=self.contract,
            changed_files=("src/main.py",),
            current_workspace_digest="sha256:ws1",
            verification=None,
        )
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, "VERIFICATION_REQUIRED")

    def test_rejects_failing_verification(self) -> None:
        receipt = VerificationReceipt(
            exit_code=1,
            executed_test_count=5,
            workspace_digest="sha256:ws1",
        )
        verdict = self.gate.evaluate(
            goal_contract=self.contract,
            changed_files=("src/main.py",),
            current_workspace_digest="sha256:ws1",
            verification=receipt,
        )
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, "VERIFICATION_FAILED")

    def test_rejects_stale_verification(self) -> None:
        receipt = VerificationReceipt(
            exit_code=0,
            executed_test_count=5,
            workspace_digest="sha256:ws_old",
        )
        verdict = self.gate.evaluate(
            goal_contract=self.contract,
            changed_files=("src/main.py",),
            current_workspace_digest="sha256:ws_new",
            verification=receipt,
        )
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, "VERIFICATION_STALE")

    def test_accepts_fresh_passing_verification(self) -> None:
        receipt = VerificationReceipt(
            exit_code=0,
            executed_test_count=5,
            workspace_digest="sha256:ws1",
            task_digest=self.contract.task_digest,
            receipt_digest="sha256:receipt",
            command="python -m unittest",
            verification_subject_digest="sha256:subject",
        )
        verdict = self.gate.evaluate(
            goal_contract=self.contract,
            changed_files=("src/main.py",),
            current_workspace_digest="sha256:ws1",
            verification=receipt,
        )
        self.assertTrue(verdict.admissible)
        self.assertEqual(verdict.reason, "completion_admissible")


class TestForgeReflexRules(unittest.TestCase):
    """Tests for deterministic reflex rules."""

    def test_repeated_failure_detection(self) -> None:
        fp1 = FailureFingerprint(
            tool_kind="run_command",
            exit_code=1,
            failing_tests=("test_foo",),
            exception_type="AssertionError",
            top_stack_frame="test.py:10",
        )
        fp2 = FailureFingerprint(
            tool_kind="run_command",
            exit_code=1,
            failing_tests=("test_foo",),
            exception_type="AssertionError",
            top_stack_frame="test.py:10",
        )
        directive = RepeatedFailureRule.evaluate([fp1, fp2])
        self.assertIsNotNone(directive)
        self.assertEqual(directive.kind, "redirect")
        self.assertIn("Repeated identical failure", directive.reason)

    def test_no_progress_detection(self) -> None:
        directive = NoProgressRule.evaluate(3)
        self.assertIsNotNone(directive)
        self.assertEqual(directive.kind, "abandon_hypothesis")


class TestForgeEngineExecution(unittest.TestCase):
    """Full reflexive TDD episode execution tests."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="forge-engine-test-")
        self.ws = Path(self.temp_dir)
        (self.ws / "src").mkdir(parents=True)
        (self.ws / "test").mkdir(parents=True)
        (self.ws / "src" / "calc.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
        (self.ws / "test" / "test_calc.py").write_text(
            "import unittest\nimport sys\nfrom pathlib import Path\n"
            "sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))\n"
            "from calc import add\n\n"
            "class TestCalc(unittest.TestCase):\n"
            "    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n\n"
            "if __name__ == '__main__':\n    unittest.main()\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_fast_cycle_tdd_convergence(self) -> None:
        # Script a 3-turn model resolution:
        # Turn 1: run failing test
        # Turn 2: edit file to fix bug + re-run test (green)
        # Turn 3: finish task
        proposals = [
            {
                "content": "Let me run the test suite to observe the failure.",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "function": {
                            "name": "run_command",
                            "arguments": {"command": "python3 -B test/test_calc.py"},
                        },
                    }
                ],
            },
            {
                "content": "Fixing the bug in src/calc.py and verifying.",
                "tool_calls": [
                    {
                        "id": "call_2a",
                        "function": {
                            "name": "edit_file",
                            "arguments": {
                                "path": "src/calc.py",
                                "content": "def add(a, b):\n    return a + b\n",
                            },
                        },
                    },
                    {
                        "id": "call_2b",
                        "function": {
                            "name": "run_command",
                            "arguments": {"command": "python3 -B test/test_calc.py"},
                        },
                    },
                ],
            },
            {
                "content": "All tests pass. Finishing task.",
                "tool_calls": [
                    {
                        "id": "call_3",
                        "function": {
                            "name": "finish_task",
                            "arguments": {"summary": "Fixed subtraction to addition in add()."},
                        },
                    }
                ],
            },
        ]

        model = ScriptedForgeModel(proposals)
        
        # Test command runner helper executing locally in test workspace
        def local_runner(cmd: str, cwd: Path) -> Tuple[int, str]:
            import os
            import subprocess
            env = {
                **os.environ,
                "PYTHONPATH": f"{str(cwd)}:{str(cwd / 'src')}",
                "PYTHONDONTWRITEBYTECODE": "1",
            }
            p = subprocess.run(cmd, shell=True, cwd=cwd, env=env, capture_output=True, text=True)
            return p.returncode, p.stdout + "\n" + p.stderr

        engine = ForgeFacade.create_engine(
            workspace_root=self.ws,
            model_port=model,
            command_runner=local_runner,
        )

        outcome = engine.run_episode(task_brief="Fix bug in add function")
        self.assertEqual(outcome.status, "COMPLETED")
        self.assertEqual(outcome.turns, 3)
        self.assertIn("src/calc.py", outcome.changed_files)
        self.assertIsNotNone(outcome.verification_receipt)
        self.assertTrue(outcome.verification_receipt.passed)


if __name__ == "__main__":
    unittest.main()
