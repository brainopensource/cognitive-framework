"""T-95 / T-26: preregistration, single-dimension comparisons, L2 arm pin."""

from __future__ import annotations

import unittest

from benchmarks.ladder.control import CONTROL_ARM, ControlNotFrozen, require_frozen
from benchmarks.ladder.hypotheses import HypothesisError, assert_single_dimension, require_hypothesis
from vanguard.packages.runtime.paired_evaluation import assert_single_varied_dimension


class TestPreregistration(unittest.TestCase):
    def test_control_arm_is_single_worker_balanced_product_path(self) -> None:
        self.assertEqual(CONTROL_ARM["harness"], "vg-code-balanced")
        self.assertEqual(CONTROL_ARM["preset"], "balanced")
        self.assertEqual(CONTROL_ARM["workers"], 1)
        self.assertIn("entrypoint.execute", CONTROL_ARM["product_path"])

    def test_unfrozen_control_cannot_be_scored(self) -> None:
        with self.assertRaises(ControlNotFrozen):
            require_frozen()

    def test_unregistered_treatment_is_refused(self) -> None:
        with self.assertRaises(HypothesisError):
            require_hypothesis("H-not-a-real-treatment")

    def test_registered_route_l_row_has_one_varied_dimension(self) -> None:
        row = require_hypothesis("H-T78-str-replace")
        self.assertEqual(row["varied_dimension"], "edit_primitive")
        self.assertEqual(row["task"], "T-78")

    def test_multi_dimension_comparison_is_refused(self) -> None:
        control = {"preset": "balanced", "model_id": "m1", "edit_primitive": "apply_patch"}
        treatment = {"preset": "max", "model_id": "m1", "edit_primitive": "str_replace"}
        with self.assertRaises(HypothesisError):
            assert_single_dimension(control, treatment, varied_dimension="edit_primitive")
        with self.assertRaises(ValueError):
            assert_single_varied_dimension(control, treatment, "edit_primitive")

    def test_single_dimension_comparison_is_admitted(self) -> None:
        control = {"preset": "balanced", "model_id": "m1", "edit_primitive": "apply_patch"}
        treatment = {"preset": "balanced", "model_id": "m1", "edit_primitive": "str_replace"}
        assert_single_dimension(control, treatment, varied_dimension="edit_primitive")
        assert_single_varied_dimension(control, treatment, "edit_primitive")


if __name__ == "__main__":
    unittest.main()
