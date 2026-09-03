"""Tests for Harness Analyzer & Pareto metrics engine."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

tools_dir = Path(__file__).resolve().parents[2] / "tools" / "002_LLM_API_MOCK"
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from analyzer import HarnessAnalyzer


class TestHarnessAnalyzer(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.tmp_dir) / "test_analyzer.sqlite"
        self.analyzer = HarnessAnalyzer(self.db_path)

    def test_analyzer_report_generation(self) -> None:
        self.analyzer.store.upsert_scenario(
            scenario_id="t3-event-bus",
            tier=3,
            title="Event Bus Test",
            atoms=["view_file", "edit_file", "run_command"],
            n_files=2,
            n_turns=4,
        )

        # Simulate a Tier 3 task passed by a Tier 1 model (Downgrade success!)
        self.analyzer.store.insert_trace(
            scenario_id="t3-event-bus",
            backend="ollama",
            model="llama3.2:3b",
            passed=True,
            llm_calls=4,
            prompt_tokens=800,
            completion_tokens=200,
            usd=0.0,
            wall_s=0.05,
            model_tier=1,
            scenario_tier=3,
            is_downgrade=True,
        )

        summary = self.analyzer.generate_kpi_summary()
        self.assertEqual(summary["summary"]["downgrade_pass_rate"], 1.0)
        self.assertEqual(len(summary["tier_downgrade_matrix"]), 1)

        md = self.analyzer.render_markdown_report()
        self.assertIn("Harness Pipeline Optimization & Pareto Cost Report", md)
        self.assertIn("Tier-Downgrade Pass Rate", md)


if __name__ == "__main__":
    unittest.main()
