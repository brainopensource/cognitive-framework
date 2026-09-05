"""T-94: false-completion veto; Wilson only on LIVE-* rows."""

from __future__ import annotations

import unittest

from benchmarks.ladder.metrics import MetricVeto, canary_disposition, score_metrics
from test.benchmarks.test_evidence_row_schema import _row


class TestMetricVeto(unittest.TestCase):
    def test_nonzero_false_completion_vetoes_the_gate(self) -> None:
        rows = [
            _row(settlement={"terminal_status": "completed", "disposition": "failed"},
                 change={"patch_digest": None}, verification={"tests_executed": 0}),
        ]
        with self.assertRaises(MetricVeto):
            score_metrics(rows)

    def test_wilson_excludes_replay_rows(self) -> None:
        live = _row(execution={"evidence_label": "LIVE-LOCAL"},
                    settlement={"disposition": "passed"})
        replay = _row(execution={"evidence_label": "REPLAY"},
                      settlement={"disposition": "passed"})
        metrics = score_metrics([live, replay])
        self.assertEqual(metrics["n_live_evaluated"], 1)
        self.assertEqual(metrics["n_live_passed"], 1)
        self.assertIsNotNone(metrics["wilson"])

    def test_zero_live_observations_do_not_claim_zero_risk(self) -> None:
        replay = _row(execution={"evidence_label": "REPLAY"},
                      settlement={"disposition": "passed"})
        metrics = score_metrics([replay])
        self.assertEqual(metrics["n_live_evaluated"], 0)
        self.assertIsNone(metrics["wilson"])
        self.assertEqual(
            canary_disposition(metrics=metrics, n_evaluable=0, frozen=True),
            "UNDETERMINABLE",
        )

    def test_unfrozen_control_is_invalid(self) -> None:
        self.assertEqual(
            canary_disposition(metrics=None, n_evaluable=30, frozen=False),
            "INVALID",
        )


if __name__ == "__main__":
    unittest.main()
