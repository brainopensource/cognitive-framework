"""M-6.5 falsifiers for pure projections and exterior strategy policy."""

from __future__ import annotations

import unittest

from vanguard.packages.domain.ledger.progress import ConfidenceRecord, fold_progress
from vanguard.packages.ports.meta_controller import StrategyDirective


class M65ProjectionTests(unittest.TestCase):
    def test_progress_fold_is_ordered_and_deterministic(self) -> None:
        events = [
            {"payload": {"kind": "ProgressAssessed", "assessment": "stalled",
                         "signals": {"budgetConsumed": 10}}},
            {"payload": {"kind": "EffectFailed", "repeatSignature": "same-edit"}},
            {"payload": {"kind": "ProgressAssessed", "assessment": "advancing",
                         "signals": {"budgetConsumed": 14}}},
            {"payload": {"kind": "StrategyChanged", "to": "breadth"}},
        ]
        view = fold_progress(events)
        self.assertEqual(view.assessment, "advancing")
        # A later advancing assessment clears the consecutive-stall counter.
        self.assertEqual(view.stall_count, 0)
        self.assertEqual(view.repeat_signatures, ("same-edit",))
        self.assertEqual(view.budget_burn_rate, 4.0)
        self.assertEqual(view, fold_progress(events))

    def test_confidence_rejects_out_of_range_and_unknown_signals(self) -> None:
        with self.assertRaises(ValueError):
            ConfidenceRecord("self_report", 1.1, "subject")
        with self.assertRaises(ValueError):
            ConfidenceRecord("magic", 0.5, "subject")

    def test_directive_is_closed_set_and_delegate_is_explicit(self) -> None:
        with self.assertRaises(ValueError):
            StrategyDirective("grant_authority", "controller", "bad")
        with self.assertRaises(ValueError):
            StrategyDirective("delegate", "controller", "need help")
        directive = StrategyDirective("delegate", "controller", "stalled",
                                      brief="run tests", scope_slice={"maxTurns": 2})
        self.assertEqual(directive.controller_id, "controller")


if __name__ == "__main__":
    unittest.main()
