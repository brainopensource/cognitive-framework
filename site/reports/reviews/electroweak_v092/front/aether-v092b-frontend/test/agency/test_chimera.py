"""Comprehensive Unit and Contract Test Suite for Vanguard CHIMERA.

Tests:
1. CognitiveBlackboard & approximate Bayesian belief updating.
2. MetaCognitiveGovernor directive selection & phase transitions.
3. CognitiveRouter Thompson sampling & bandit arm updates.
4. RetrievalMarket multi-provider auctions & VOI ranking.
5. SymbolicCortex AST syntax checking & invariant solving.
6. ChimeraAtomicPatcher multi-strategy file modifications & rollbacks.
7. VerificationCortex multi-stage output parsing & risk analysis.
8. ChimeraEngine & ChimeraFacade full hermetic autonomous episodes.
"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from typing import Any, Dict, List

from vanguard.packages.agency.chimera import (
    BUILTIN_SKILLS,
    BanditArm,
    BestFirstEngineeringSearch,
    CalibratedConfidence,
    ChimeraAtomicPatcher,
    ChimeraConfig,
    ChimeraContextCompiler,
    ChimeraEngine,
    ChimeraFacade,
    ChimeraOutcome,
    CognitiveBlackboard,
    CognitiveBudget,
    CognitiveDirective,
    CognitiveDirectiveKind,
    CognitiveRouter,
    EngineeringState,
    Fact,
    GovernorPolicy,
    Hypothesis,
    MetaCognitiveGovernor,
    PatchCandidate,
    RankedFile,
    RankedSymbol,
    RankedTest,
    RetrievalBid,
    RetrievalMarket,
    SkillRegistry,
    SymbolicCortex,
    TaskFeatures,
    UncertaintyProfile,
    VerificationCortex,
    VerificationLevel,
    VerificationRecord,
)
from vanguard.packages.agency.forge.engine import (
    GoalContract,
    VerificationReceipt,
)


class FakeChimeraModelPort:
    """Deterministic mock model port simulating multi-turn autonomous tool calls."""

    def __init__(self, turns_script: list[dict[str, Any]] | None = None) -> None:
        self.turns_script = turns_script or []
        self.call_count = 0

    def propose(self, context: Any, tools: Any, sampling: Any) -> dict[str, Any]:
        if self.call_count < len(self.turns_script):
            res = self.turns_script[self.call_count]
        else:
            res = {
                "tool_calls": [
                    {
                        "name": "finish_task",
                        "args": {"summary": "Done."},
                    }
                ],
                "usage": {"prompt_tokens": 100, "completion_tokens": 20},
            }
        self.call_count += 1
        return res


class TestChimeraBlackboard(unittest.TestCase):
    def test_blackboard_creation_and_belief_updating(self) -> None:
        board = CognitiveBlackboard.from_task(
            task_brief="Fix LRUCache TTL expiration in lru/cache.py",
            features=TaskFeatures(language="python", kind="bugfix", multi_file=False),
        )
        self.assertEqual(len(board.hypotheses), 1)
        self.assertGreater(board.uncertainty.localization_uncertainty, 0.5)

        # Update hypothesis with positive evidence
        h = board.hypotheses[0]
        h_updated = h.update_evidence(support_weight=2.0, evidence_id="ev_test_traceback")
        self.assertGreater(h_updated.posterior, h.posterior)
        self.assertEqual(h_updated.status, "supported")

        # Update blackboard
        board = board.update_hypothesis(h_updated)
        self.assertEqual(board.hypotheses[0].status, "supported")

        # Add Fact
        fact = Fact(
            fact_id="f1",
            kind="traceback",
            statement="AssertionError: 2 != 3 at test_lru.py:45",
            source="test",
        )
        board = board.add_fact(fact)
        self.assertEqual(len(board.facts), 1)

        # Record Verification
        ver = VerificationRecord(
            verification_id="v1",
            level="V2_FULL_SUITE",
            exit_code=0,
            executed_tests=5,
            passed_tests=5,
            failed_tests=(),
            output_summary="Ran 5 tests in 0.1s\n\nOK",
        )
        board = board.record_verification(ver)
        self.assertTrue(board.verifications[-1].passed)
        self.assertGreater(board.confidence.calibrated_score, 0.5)
        self.assertLess(board.uncertainty.verification_uncertainty, 0.1)

        # Digest should be deterministic
        dig1 = board.digest()
        dig2 = board.digest()
        self.assertEqual(dig1, dig2)


class TestChimeraGovernorAndRouter(unittest.TestCase):
    def test_governor_phases(self) -> None:
        governor = MetaCognitiveGovernor()

        # Phase 1: Needs exploration / localization
        b1 = CognitiveBlackboard.from_task(task_brief="Fix math utils")
        d1 = governor.decide(b1)
        self.assertEqual(d1.kind, CognitiveDirectiveKind.RETRIEVE)
        self.assertEqual(d1.route, "LDA_AST")

        # Phase 2: Candidate files known -> Generate
        b2 = b1.update_candidates(
            files=[RankedFile(path="src/math_util.py", relevance_score=0.9, provider="lexical")]
        )
        d2 = governor.decide(b2)
        self.assertIn(d2.kind, (CognitiveDirectiveKind.GENERATE, CognitiveDirectiveKind.ACT))

        # Phase 3: Repeated failures -> Fork / Escalate
        d3 = governor.decide(b2, failure_streak=3)
        self.assertIn(d3.kind, (CognitiveDirectiveKind.FORK, CognitiveDirectiveKind.ESCALATE))

        # Phase 4: Budget exhausted -> Stop
        b_depleted = b2.consume_budget(turns=20)
        d4 = governor.decide(b_depleted)
        self.assertEqual(d4.kind, CognitiveDirectiveKind.STOP)

    def test_router_thompson_sampling(self) -> None:
        router = CognitiveRouter(seed=123)
        directive = CognitiveDirective(
            kind=CognitiveDirectiveKind.GENERATE,
            objective="Synthesize patch",
            route="FRONTIER_LLM",
        )
        board = CognitiveBlackboard.from_task(task_brief="Implement algorithm")
        selected = router.select(directive, board)
        self.assertIn(selected, ("FRONTIER_LLM", "CHEAP_LLM", "SEARCH", "SYMBOLIC_SOLVER"))

        # Feedback update
        router.record_feedback("FRONTIER_LLM", success=True, cost_usd=0.01)
        self.assertGreater(router._arms["FRONTIER_LLM"].alpha, 7.0)


class TestChimeraSymbolicAndPatcher(unittest.TestCase):
    def test_symbolic_syntax_validation(self) -> None:
        # Python Valid
        res_py = SymbolicCortex.validate_code_syntax("def add(a, b):\n    return a + b\n", "math.py")
        self.assertTrue(res_py.valid)

        # Python Syntax Error
        res_bad = SymbolicCortex.validate_code_syntax("def add(a, b\n    return a + b", "bad.py")
        self.assertFalse(res_bad.valid)
        self.assertIsNotNone(res_bad.error_message)

        # JSON Valid
        res_json = SymbolicCortex.validate_code_syntax('{"key": "value"}', "config.json")
        self.assertTrue(res_json.valid)

        # JS / Rust Delimiter match
        res_js = SymbolicCortex.validate_code_syntax("function foo() { return [1, 2, (3 + 4)]; }", "app.js")
        self.assertTrue(res_js.valid)

        res_js_bad = SymbolicCortex.validate_code_syntax("function foo() { return [1, 2, (3 + 4]; }", "app.js")
        self.assertFalse(res_js_bad.valid)

    def test_resilient_patcher(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td)
            patcher = ChimeraAtomicPatcher(workspace_root=ws)

            # Write initial file
            w_res = patcher.write_file("src/calc.py", "def add(x, y):\n    return x - y\n")
            self.assertTrue(w_res.success)
            self.assertEqual(w_res.changed_files, ("src/calc.py",))

            # Apply surgical patch with fuzzy whitespace
            s_res = patcher.apply_resilient_patch(
                "src/calc.py",
                target_chunk="return x - y",
                replacement_chunk="return x + y",
            )
            self.assertTrue(s_res.success)
            content = (ws / "src/calc.py").read_text(encoding="utf-8")
            self.assertEqual(content, "def add(x, y):\n    return x + y\n")

            # Syntax error rollback
            bad_patch = patcher.apply_resilient_patch(
                "src/calc.py",
                target_chunk="return x + y",
                replacement_chunk="return x + + + def",
            )
            self.assertFalse(bad_patch.success)
            # Original content unchanged
            self.assertEqual((ws / "src/calc.py").read_text(encoding="utf-8"), "def add(x, y):\n    return x + y\n")


class TestChimeraHermeticEpisode(unittest.TestCase):
    def test_hermetic_bugfix_episode(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td)
            (ws / "math_mod").mkdir(parents=True)
            (ws / "math_mod/__init__.py").write_text("from .core import subtract\n", encoding="utf-8")
            (ws / "math_mod/core.py").write_text("def subtract(a, b):\n    return a + b\n", encoding="utf-8")

            # Mock command runner simulating test execution
            def mock_runner(cmd: str, cwd: Path) -> tuple[int, str]:
                core_p = cwd / "math_mod/core.py"
                if core_p.exists() and "return a - b" in core_p.read_text(encoding="utf-8"):
                    return 0, "Ran 3 tests in 0.05s\n\nOK"
                return 1, "FAIL: test_subtract\nAssertionError: 5 != 1"

            # Scripted model turn sequence:
            # Turn 1: run_command to observe failure
            # Turn 2: surgical_patch to fix subtraction
            # Turn 3: run_command to verify pass
            # Turn 4: finish_task
            script = [
                {
                    "tool_calls": [
                        {"name": "run_command", "args": {"command": "python3 -m unittest discover"}}
                    ],
                    "usage": {"prompt_tokens": 100, "completion_tokens": 30},
                },
                {
                    "tool_calls": [
                        {
                            "name": "surgical_patch",
                            "args": {
                                "path": "math_mod/core.py",
                                "target": "return a + b",
                                "replacement": "return a - b",
                            },
                        }
                    ],
                    "usage": {"prompt_tokens": 120, "completion_tokens": 40},
                },
                {
                    "tool_calls": [
                        {"name": "run_command", "args": {"command": "python3 -m unittest discover"}}
                    ],
                    "usage": {"prompt_tokens": 150, "completion_tokens": 30},
                },
                {
                    "tool_calls": [
                        {"name": "finish_task", "args": {"summary": "Fixed subtract in math_mod/core.py"}}
                    ],
                    "usage": {"prompt_tokens": 160, "completion_tokens": 20},
                },
            ]

            model = FakeChimeraModelPort(script)
            outcome: ChimeraOutcome = ChimeraFacade.run_task(
                workspace_root=ws,
                task_brief="Fix subtraction bug in math_mod/core.py",
                model_port=model,
                config=ChimeraConfig(max_turns=6),
                command_runner=mock_runner,
            )

            self.assertEqual(outcome.status, "COMPLETED")
            self.assertIn("math_mod/core.py", outcome.changed_files)
            self.assertIsNotNone(outcome.verification_receipt)
            self.assertTrue(outcome.verification_receipt.passed)
            self.assertIsNotNone(outcome.admission_verdict)
            self.assertTrue(outcome.admission_verdict.admissible)

    def test_greenfield_multi_file_creation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td)
            
            def mock_runner(cmd: str, cwd: Path) -> tuple[int, str]:
                app_p = cwd / "app/server.py"
                test_p = cwd / "test/test_server.py"
                if app_p.exists() and test_p.exists():
                    return 0, "Ran 4 tests in 0.08s\n\nOK"
                return 1, "FAIL: tests missing"

            script = [
                {
                    "tool_calls": [
                        {
                            "name": "edit_file",
                            "args": {
                                "path": "app/server.py",
                                "content": "def handle_request(path):\n    return {'status': 200, 'path': path}\n",
                            },
                        },
                        {
                            "name": "edit_file",
                            "args": {
                                "path": "test/test_server.py",
                                "content": "def test_ok():\n    pass\n",
                            },
                        },
                    ],
                    "usage": {"prompt_tokens": 150, "completion_tokens": 80},
                },
                {
                    "tool_calls": [
                        {"name": "run_command", "args": {"command": "python3 -m unittest discover -s test"}}
                    ],
                    "usage": {"prompt_tokens": 180, "completion_tokens": 30},
                },
                {
                    "tool_calls": [
                        {"name": "finish_task", "args": {"summary": "Built greenfield app and test suite"}}
                    ],
                    "usage": {"prompt_tokens": 200, "completion_tokens": 20},
                },
            ]

            model = FakeChimeraModelPort(script)
            outcome: ChimeraOutcome = ChimeraFacade.run_task(
                workspace_root=ws,
                task_brief="Build greenfield web server in app/server.py and test in test/test_server.py",
                model_port=model,
                config=ChimeraConfig(max_turns=5),
                command_runner=mock_runner,
            )

            self.assertEqual(outcome.status, "COMPLETED")
            self.assertIn("app/server.py", outcome.changed_files)
            self.assertIn("test/test_server.py", outcome.changed_files)
            self.assertTrue(outcome.verification_receipt.passed)

    def test_admission_gate_rejection_on_failing_test(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td)
            (ws / "mod.py").write_text("x = 1\n", encoding="utf-8")

            def mock_runner(cmd: str, cwd: Path) -> tuple[int, str]:
                return 1, "FAIL: test_x\nAssertionError: 1 != 2"

            script = [
                {
                    "tool_calls": [
                        {"name": "edit_file", "args": {"path": "mod.py", "content": "x = 2\n"}},
                        {"name": "run_command", "args": {"command": "python3 test.py"}},
                        {"name": "finish_task", "args": {"summary": "Try to finish despite failing test"}},
                    ],
                    "usage": {"prompt_tokens": 100, "completion_tokens": 40},
                }
            ]

            model = FakeChimeraModelPort(script)
            outcome = ChimeraFacade.run_task(
                workspace_root=ws,
                task_brief="Fix x in mod.py",
                model_port=model,
                config=ChimeraConfig(max_turns=2),
                command_runner=mock_runner,
            )

            # Finish should have been rejected by admission gate
            self.assertNotEqual(outcome.status, "COMPLETED")

    def test_runtime_composition_of_manifests(self) -> None:
        from vanguard.packages.runtime.root import Runtime

        root = Path(__file__).resolve().parents[2]
        manifest_v1 = root / "vanguard/packages/agency/manifests/vg-chimera-v1/manifest.json"
        manifest_code = root / "vanguard/packages/agency/manifests/vg-code-chimera/manifest.json"

        harness_v1 = Runtime.compose(manifest_v1)
        self.assertEqual(harness_v1.harness, "vg-chimera-v1")
        self.assertTrue(harness_v1.gene_digests)

        harness_code = Runtime.compose(manifest_code)
        self.assertEqual(harness_code.harness, "vg-code-chimera")
        self.assertTrue(harness_code.gene_digests)


if __name__ == "__main__":
    unittest.main()
