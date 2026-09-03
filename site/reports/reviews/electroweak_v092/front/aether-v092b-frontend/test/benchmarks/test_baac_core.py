"""Unit tests for BaaC (Benchmarking as Code) core components.

Tests:
1. Zero-state verification, drift detection, and workspace isolation (lib/state.py).
2. Fail-closed budget and request caps (lib/budget.py).
3. External oracle evaluation (lib/oracle.py).
4. Attribution classification and reporting (lib/report.py).
"""

from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import unittest

from benchmarks.baac.lib.budget import (
    BudgetCapConfig,
    BudgetExceededError,
    BudgetTracker,
    DisallowedModelError,
)
from benchmarks.baac.lib.oracle import OracleResult, run_external_oracle
from benchmarks.baac.lib.report import (
    BaaCReport,
    ChallengeExecutionResult,
    classify_attribution,
)
from benchmarks.baac.lib.state import (
    clean_scratch_workspace,
    compute_directory_manifest,
    generate_challenge_manifest,
    materialize_scratch_workspace,
    verify_challenge_zero_state,
)


class TestBaaCState(unittest.TestCase):
    """Test zero-state verification and scratch workspace isolation."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="baac-state-test-")
        self.root = Path(self.temp_dir)
        (self.root / "src").mkdir()
        (self.root / "oracle").mkdir()
        (self.root / "TASK.md").write_text("# Task\nSolve problem\n", encoding="utf-8")
        (self.root / "challenge.yaml").write_text("id: test_c\n", encoding="utf-8")
        (self.root / "src" / "main.py").write_text("def solve(): pass\n", encoding="utf-8")
        (self.root / "oracle" / "verify.py").write_text("print('oracle')\n", encoding="utf-8")
        generate_challenge_manifest(self.root)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_zero_state_clean_and_drift_detection(self) -> None:
        # 1. Clean state
        ok, drifts = verify_challenge_zero_state(self.root)
        self.assertTrue(ok)
        self.assertEqual(len(drifts), 0)

        # 2. Modify a file
        (self.root / "src" / "main.py").write_text("def solve(): return 42\n", encoding="utf-8")
        ok, drifts = verify_challenge_zero_state(self.root)
        self.assertFalse(ok)
        self.assertTrue(any("Content drift in src/main.py" in d for d in drifts))

        # 3. Add untracked file
        (self.root / "src" / "untracked.py").write_text("x = 1\n", encoding="utf-8")
        ok, drifts = verify_challenge_zero_state(self.root)
        self.assertFalse(ok)
        self.assertTrue(any("Untracked file" in d for d in drifts))

    def test_scratch_workspace_isolation(self) -> None:
        scratch = Path(tempfile.mkdtemp(prefix="scratch-dest-"))
        try:
            materialize_scratch_workspace(self.root, scratch)

            # Files that MUST exist in agent scratch workspace
            self.assertTrue((scratch / "TASK.md").is_file())
            self.assertTrue((scratch / "src" / "main.py").is_file())

            # Files that MUST NEVER be copied to agent scratch workspace
            self.assertFalse((scratch / "oracle").exists(), "oracle/ directory must never leak to agent workspace")
            self.assertFalse((scratch / "challenge.yaml").exists())
            self.assertFalse((scratch / "manifest.sha256").exists())
        finally:
            clean_scratch_workspace(scratch)
            self.assertFalse(scratch.exists())


class TestBaaCBudget(unittest.TestCase):
    """Test fail-closed budget, request caps, and allowlists."""

    def test_request_cap_abort(self) -> None:
        cfg = BudgetCapConfig(max_requests=2, max_cost_usd=1.0)
        tracker = BudgetTracker(cfg)

        tracker.check_pre_call("lam-mock")
        tracker.record_request("lam-mock", 100, 20)

        tracker.check_pre_call("lam-mock")
        tracker.record_request("lam-mock", 100, 20)

        # 3rd request must fail pre-call
        with self.assertRaises(BudgetExceededError):
            tracker.check_pre_call("lam-mock")

    def test_cost_cap_abort(self) -> None:
        cfg = BudgetCapConfig(max_requests=10, max_cost_usd=0.05)
        tracker = BudgetTracker(cfg)

        tracker.check_pre_call("lam-mock")
        tracker.record_request("lam-mock", 1000, 500, reported_cost=0.06)

        # Next call must abort fail-closed
        with self.assertRaises(BudgetExceededError):
            tracker.check_pre_call("lam-mock")

    def test_disallowed_model_rejection(self) -> None:
        cfg = BudgetCapConfig(allowed_models=("deepseek/deepseek-v4-flash-0731",))
        tracker = BudgetTracker(cfg)

        with self.assertRaises(Exception):
            tracker.check_pre_call("unapproved/random-model")


class TestBaaCAttribution(unittest.TestCase):
    """Test attribution taxonomy."""

    def test_classification_outcomes(self) -> None:
        # 1. Passing oracle
        pass_oracle = OracleResult(True, 0, "OK", "", 0.1)
        self.assertEqual(classify_attribution(pass_oracle, "COMPLETED", 2, 8), "PASS")

        # 2. Failing oracle with valid harness run -> LLM cognitive error
        fail_oracle = OracleResult(False, 1, "FAIL", "AssertionError", 0.1)
        self.assertEqual(classify_attribution(fail_oracle, "COMPLETED", 2, 8, changed_files=("src/a.py",)), "LLM_COGNITIVE_ERROR")

        # 3. Budget exhausted -> Harness error
        self.assertEqual(classify_attribution(fail_oracle, "BUDGET_EXHAUSTED", 5, 8, budget_exceeded=True), "HARNESS_ERROR")

        # 4. Missing oracle script -> Dataset invalid
        missing_oracle = OracleResult(False, 1, "", "Oracle script missing", 0.0, error="Oracle script missing")
        self.assertEqual(classify_attribution(missing_oracle, "COMPLETED", 2, 8), "DATASET_INVALID")

    def test_report_kpi_and_promotion(self) -> None:
        report = BaaCReport(run_id="test_run", preset="vg-1-forge", model="deepseek", mode="lam")
        report.results.append(
            ChallengeExecutionResult(
                challenge_id="c1",
                tier="easy",
                preset="vg-1-forge",
                model="deepseek",
                mode="lam",
                status="PASS",
                attribution="PASS",
                turns=2,
                prompt_tokens=300,
                completion_tokens=50,
                total_tokens=350,
                cost_usd=0.001,
                duration_seconds=1.2,
            )
        )
        report.results.append(
            ChallengeExecutionResult(
                challenge_id="c2",
                tier="easy",
                preset="vg-1-forge",
                model="deepseek",
                mode="lam",
                status="PASS",
                attribution="PASS",
                turns=3,
                prompt_tokens=400,
                completion_tokens=60,
                total_tokens=460,
                cost_usd=0.001,
                duration_seconds=1.5,
            )
        )
        self.assertEqual(report.pass_count, 2)
        self.assertEqual(report.overall_pass_rate_pct, 100.0)
        self.assertTrue(report.is_tier_promoted("easy", threshold_pct=80.0))

        md = report.to_markdown_table()
        self.assertIn("BaaC Evaluation Matrix", md)
        self.assertIn("100.0%", md)


if __name__ == "__main__":
    unittest.main()
