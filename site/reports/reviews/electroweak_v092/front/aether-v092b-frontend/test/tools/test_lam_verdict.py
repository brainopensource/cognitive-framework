"""Honest LAM/LAR verdicts: pytest exit, evidence labels, no live-from-replay."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAM = ROOT / "tools" / "002_LLM_API_MOCK"
if str(LAM) not in sys.path:
    sys.path.insert(0, str(LAM))


class PytestVerdict(unittest.TestCase):
    def test_multi_call_without_green_tests_is_not_a_pass(self) -> None:
        from verdict import pytest_passed, workspace_verdict

        tmp = Path(tempfile.mkdtemp())
        (tmp / "broken.py").write_text("def f():\n    return 0\n", encoding="utf-8")
        (tmp / "test_broken.py").write_text(
            "from broken import f\n\ndef test_f():\n    assert f() == 1\n",
            encoding="utf-8",
        )
        self.assertFalse(pytest_passed(tmp))
        row = workspace_verdict(tmp, backend="lam", llm_calls=4)
        self.assertFalse(row["passed"])
        self.assertEqual(row["evidence_label"], "lam-replay")

    def test_green_pytest_is_a_pass(self) -> None:
        from verdict import pytest_passed

        tmp = Path(tempfile.mkdtemp())
        (tmp / "ok.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        (tmp / "test_ok.py").write_text(
            "from ok import f\n\ndef test_f():\n    assert f() == 1\n",
            encoding="utf-8",
        )
        self.assertTrue(pytest_passed(tmp))

    def test_lam_backend_is_never_labelled_live(self) -> None:
        from verdict import evidence_label

        self.assertEqual(evidence_label("lam"), "lam-replay")
        self.assertEqual(evidence_label("ollama"), "live-ollama")
        self.assertEqual(evidence_label("openrouter"), "live-openrouter")


class LeakScan(unittest.TestCase):
    def test_detects_oracle_dir_and_bug_comments(self) -> None:
        from verdict import leak_paths

        tmp = Path(tempfile.mkdtemp())
        (tmp / "src.py").write_text("# Bug 1: forget TTL\n", encoding="utf-8")
        oracle = tmp / "oracle"
        oracle.mkdir()
        (oracle / "test_oracle.py").write_text("assert False\n", encoding="utf-8")
        leaks = leak_paths(tmp)
        self.assertTrue(any("oracle" in p for p in leaks))
        self.assertTrue(any("Bug 1" in p or "src.py" in p for p in leaks))


class AnalyzerDoesNotCallLamLive(unittest.TestCase):
    def test_kpi_summary_separates_lam_from_live(self) -> None:
        from analyzer import HarnessAnalyzer

        db = Path(tempfile.mkdtemp()) / "a.sqlite"
        analyzer = HarnessAnalyzer(db)
        analyzer.store.upsert_scenario(
            scenario_id="t1-calculator",
            tier=1,
            title="calc",
            atoms=["view_file"],
            n_files=1,
            n_turns=2,
        )
        analyzer.store.insert_trace(
            scenario_id="t1-calculator",
            backend="lam",
            model="lam/t1-calculator",
            passed=True,
            llm_calls=4,
            prompt_tokens=10,
            completion_tokens=10,
            usd=0.0,
            wall_s=0.01,
        )
        summary = analyzer.generate_kpi_summary()
        self.assertEqual(summary["summary"]["live_pass_count"], 0)
        self.assertGreaterEqual(summary["summary"]["lam_replay_pass_count"], 1)
        md = analyzer.render_markdown_report()
        self.assertNotIn("Live Pass Rate", md)
        self.assertIn("lam-replay", md)


class LarCalibrationFirst(unittest.TestCase):
    def test_balanced_does_not_route_paid_before_calibration(self) -> None:
        router = ROOT / "tools" / "001_LLM_API_ROUTER"
        if str(router) not in sys.path:
            sys.path.insert(0, str(router))
        from optimizer import ProviderOptimizer

        rec = ProviderOptimizer().recommend_provider(
            scenario_tier=5,
            policy="balanced",
            budget_remaining_usd=0.50,
            calibration_passed=False,
        )
        self.assertEqual(rec["provider"], "ollama")
        self.assertNotIn("gemini", rec["model"])


if __name__ == "__main__":
    unittest.main()
