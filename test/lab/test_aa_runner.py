"""Tests for A/A Runner and Floor Calibration (S9-C-03)."""

from __future__ import annotations

import random
import unittest

from tools.telemetry.aa_runner import AARunner


class TestAARunner(unittest.TestCase):
    def test_aa_runner_refuses_replay(self) -> None:
        """S9-C-03: A/A runner refuses deterministic replay input."""
        runner = AARunner(manifest="vg-shell-only", is_replay=True)
        res = runner.run_calibration(
            task_classes=["unit", "integration", "syntax"],
            arm1_evaluator=lambda t, i: {"passed": True},
            arm2_evaluator=lambda t, i: {"passed": True},
            n_repeats=5,
        )
        self.assertTrue(res.refused)
        self.assertIn("replay", res.reason.lower())

    def test_aa_runner_refuses_degenerate_all_pass(self) -> None:
        """S9-C-03: A/A runner refuses degenerate all-pass floor with zero variance."""
        runner = AARunner(manifest="vg-shell-only", is_replay=False)
        res = runner.run_calibration(
            task_classes=["unit", "integration", "syntax"],
            arm1_evaluator=lambda t, i: {"passed": True},
            arm2_evaluator=lambda t, i: {"passed": True},
            n_repeats=10,
        )
        self.assertTrue(res.refused)
        self.assertIn("degenerate", res.reason.lower())

    def test_aa_runner_refuses_under_three_task_classes(self) -> None:
        """S9-C-03: A/A runner requires at least 3 task classes."""
        runner = AARunner(manifest="vg-shell-only", is_replay=False)
        res = runner.run_calibration(
            task_classes=["unit", "integration"],
            arm1_evaluator=lambda t, i: {"passed": (i % 2 == 0)},
            arm2_evaluator=lambda t, i: {"passed": (i % 3 == 0)},
            n_repeats=10,
        )
        self.assertTrue(res.refused)
        self.assertIn("3 task classes", res.reason)

    def test_aa_runner_measures_valid_noise_floor(self) -> None:
        """S9-C-03: A/A runner measures realistic non-degenerate noise floor across 3 task classes."""
        runner = AARunner(manifest="vg-shell-only", temperature=0.2, is_replay=False)
        random.seed(42)

        def eval_arm1(task: str, i: int) -> dict[str, Any]:
            p = 0.7 if task == "unit" else (0.5 if task == "integration" else 0.3)
            return {"passed": random.random() < p, "instrument_error": i == 0}

        def eval_arm2(task: str, i: int) -> dict[str, Any]:
            p = 0.7 if task == "unit" else (0.5 if task == "integration" else 0.3)
            return {"passed": random.random() < p, "instrument_error": False}

        res = runner.run_calibration(
            task_classes=["unit", "integration", "multi-file"],
            arm1_evaluator=eval_arm1,
            arm2_evaluator=eval_arm2,
            n_repeats=30,
        )
        self.assertFalse(res.refused)
        self.assertIsNone(res.reason)
        self.assertTrue(res.floor_variance > 0.0)
        self.assertTrue(res.discordant_b > 0)
        self.assertTrue(res.discordant_c > 0)
        self.assertEqual(res.temperature, 0.2)
        self.assertTrue(res.instrument_error_rate_arm1 > 0)


if __name__ == "__main__":
    unittest.main()
