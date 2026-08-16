"""Tests for LAR Pareto optimizer."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

router_dir = Path(__file__).resolve().parents[2] / "tools" / "001_LLM_API_ROUTER"
if str(router_dir) not in sys.path:
    sys.path.insert(0, str(router_dir))

from optimizer import ProviderOptimizer


class TestProviderOptimizer(unittest.TestCase):
    def setUp(self) -> None:
        self.optimizer = ProviderOptimizer()

    def test_min_cost_policy_selects_zero_cost(self) -> None:
        rec = self.optimizer.recommend_provider(scenario_tier=1, policy="min-cost")
        self.assertEqual(rec["provider"], "ollama")

        rec_t3 = self.optimizer.recommend_provider(
            scenario_tier=3, policy="min-cost", calibration_passed=True
        )
        self.assertEqual(rec_t3["provider"], "openrouter")
        self.assertEqual(rec_t3["model"], "openrouter/free")

    def test_balanced_policy_escalation(self) -> None:
        rec1 = self.optimizer.recommend_provider(scenario_tier=1, policy="balanced")
        self.assertEqual(rec1["provider"], "ollama")

        rec5 = self.optimizer.recommend_provider(
            scenario_tier=5, policy="balanced", calibration_passed=True
        )
        self.assertEqual(rec5["provider"], "openrouter")
        self.assertEqual(rec5["model"], "google/gemini-3.7-flash")


if __name__ == "__main__":
    unittest.main()
