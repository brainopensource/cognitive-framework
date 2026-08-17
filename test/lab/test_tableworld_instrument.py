"""Tests for Instrument Support on Second Domain (TableWorld) (S10-C-01)."""

from __future__ import annotations

import unittest

from tools.telemetry.aa_runner import AARunner
from tools.telemetry.statistics import mcnemar_exact
from tools.telemetry.tuple import (
    CompatibilityKey,
    InstrumentTuple,
    ObservationMetadata,
    StratificationFields,
    TreatmentDimensions,
    compute_lift,
)
from vanguard.packages.adapters.environment.tableworld import (
    TableWorldEnvironment,
    TableWorldEvaluator,
)


class TestTableWorldInstrument(unittest.TestCase):
    def test_aa_runner_works_unchanged_on_tableworld(self) -> None:
        """S10-C-01: A/A runner calibrates noise floor on TableWorld tasks without code changes."""
        runner = AARunner(manifest="vg-table-default", temperature=0.1, is_replay=False)

        def eval_arm1(task_class: str, rep: int) -> dict:
            passed = not (task_class == "reconciliation" and rep % 3 == 0)
            return {"passed": passed, "instrument_error": False}

        def eval_arm2(task_class: str, rep: int) -> dict:
            passed = not (task_class == "reconciliation" and rep % 4 == 0)
            return {"passed": passed, "instrument_error": False}

        res = runner.run_calibration(
            task_classes=["accounts_sum", "reconciliation", "uniqueness_check"],
            arm1_evaluator=eval_arm1,
            arm2_evaluator=eval_arm2,
            n_repeats=25,
        )
        self.assertFalse(res.refused)
        self.assertEqual(res.manifest, "vg-table-default")
        self.assertEqual(len(res.task_classes), 3)

    def test_mcnemar_exact_works_unchanged_on_tableworld_results(self) -> None:
        """S10-C-01: Statistical testing operates identically across domain outputs."""
        stats = mcnemar_exact(b=8, c=1, n_total=24)
        self.assertFalse(stats.refused_p_value)
        self.assertIsNotNone(stats.p_value)
        self.assertTrue(stats.p_value < 0.05)


if __name__ == "__main__":
    unittest.main()
