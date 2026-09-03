"""M-6.5 falsifiers for pure projections and exterior strategy policy."""

from __future__ import annotations

import unittest

from vanguard.packages.domain.ledger.progress import (
    ConfidenceRecord,
    ProgressProjection,
    SemanticCheckpointRef,
    fold_progress,
    fold_progress_projection,
)
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
        directive = StrategyDirective("delegate", "controller", "stalled",
                                      brief="run tests", scope_slice={"maxTurns": 2})
        self.assertEqual(directive.controller_id, "controller")


class ProgressProjectionContractTests(unittest.TestCase):
    """`ADR-0103` §1: `ProgressProjection/2` is a derived, rebuildable projection."""

    def _projection(self) -> "ProgressProjection":
        events = [
            {"payload": {"kind": "ProgressAssessed",
                         "signals": {"budgetConsumed": 10}}},
            {"payload": {"kind": "EffectCompleted", "descriptorDigest": "edit-a"}},
            {"payload": {"kind": "StrategyChanged", "to": "breadth"}},
            {"payload": {"kind": "EffectCompleted", "descriptorDigest": "edit-b"}},
            {"payload": {"kind": "EffectFailed", "descriptorDigest": "edit-a"}},
            {"payload": {"kind": "AuthorizationDenied"}},
            {"payload": {"kind": "ProgressAssessed",
                         "signals": {"budgetConsumed": 14}}},
        ]
        return fold_progress_projection(events)

    def test_projection_exposes_exactly_the_frozen_fields(self) -> None:
        projection = self._projection()
        self.assertEqual(projection.schema, "ProgressProjection/2")
        self.assertEqual(
            set(projection.to_dict()),
            {"schema", "verifiedDelta", "failedUnknownRate", "repeatEntropy",
             "novelty", "normalizedBurn", "revisionEffectiveness",
             "calibratedUncertainty"},
        )

    def test_fold_is_deterministic_and_rebuildable(self) -> None:
        events = [{"payload": {"kind": "EffectFailed", "descriptorDigest": "x"}}]
        first = fold_progress_projection(events)
        second = fold_progress_projection(list(reversed([])) + events)
        self.assertEqual(first, second)
        self.assertEqual(first.digest(), second.digest())

    def test_rates_derive_from_event_kinds(self) -> None:
        projection = self._projection()
        # 2 failures (EffectFailed + AuthorizationDenied) of 4 effect events.
        self.assertAlmostEqual(projection.failed_unknown_rate, 2 / 4)
        # edit-a repeats once across three descriptors.
        self.assertAlmostEqual(projection.repeat_entropy, 1 / 3)
        self.assertAlmostEqual(projection.novelty, 2 / 3)
        # One StrategyChanged followed by a successful effect.
        self.assertAlmostEqual(projection.revision_effectiveness, 1.0)
        # (14 - 10) / (2 - 1) assessments.
        self.assertAlmostEqual(projection.normalized_burn, 4.0)

    def test_empty_ledger_yields_neutral_projection(self) -> None:
        projection = fold_progress_projection([])
        self.assertEqual(projection.verified_delta, 0.0)
        self.assertEqual(projection.failed_unknown_rate, 0.0)
        self.assertEqual(projection.repeat_entropy, 0.0)
        self.assertEqual(projection.novelty, 1.0)
        self.assertEqual(projection.normalized_burn, 0.0)
        self.assertEqual(projection.revision_effectiveness, 1.0)
        self.assertEqual(projection.calibrated_uncertainty, 0.0)

    def test_calibrated_uncertainty_averages_confidence_inversion(self) -> None:
        confidence = [
            ConfidenceRecord("self_report", 0.8, "subject", basis=("b",),
                             calibration={"method": "fixed"}),
            ConfidenceRecord("behavioral", 0.6, "subject", basis=("b",),
                             calibration={"method": "fixed"}),
        ]
        projection = fold_progress_projection([], confidence)
        self.assertAlmostEqual(projection.calibrated_uncertainty, 0.3)


class SemanticCheckpointRefContractTests(unittest.TestCase):
    """`ADR-0103` §2 / RF-117: semantic reference binds the four-tuple."""

    def test_rejects_empty_identity_and_negative_epoch_attempt(self) -> None:
        with self.assertRaises(ValueError):
            SemanticCheckpointRef("", "episode")
        with self.assertRaises(ValueError):
            SemanticCheckpointRef("run", "")
        with self.assertRaises(ValueError):
            SemanticCheckpointRef("run", "episode", epoch=-1)
        with self.assertRaises(ValueError):
            SemanticCheckpointRef("run", "episode", attempt=-1)

    def test_wire_shape_is_canonical(self) -> None:
        ref = SemanticCheckpointRef("run-1", "ep-1", 2, 3)
        self.assertEqual(ref.to_dict(), {
            "runId": "run-1", "episodeId": "ep-1", "epoch": 2, "attempt": 3,
        })
        self.assertEqual(ref.digest(), SemanticCheckpointRef(
            "run-1", "ep-1", epoch=2, attempt=3).digest())

    def test_stable_across_retry_but_distinct_per_tuple_member(self) -> None:
        base = SemanticCheckpointRef("run-1", "ep-1", 1, 0)
        retry = SemanticCheckpointRef("run-1", "ep-1", 1, 1)
        escalation = SemanticCheckpointRef("run-1", "ep-1", 2, 0)
        sibling_episode = SemanticCheckpointRef("run-1", "ep-2", 1, 0)
        # A retry advances the attempt, not the digest mechanism: same binding
        # produces a byte-identical reference; each tuple member moves it.
        digests = {base.digest(), retry.digest(),
                   escalation.digest(), sibling_episode.digest()}
        self.assertNotEqual(base.digest(), retry.digest())
        self.assertNotEqual(base.digest(), escalation.digest())
        self.assertNotEqual(base.digest(), sibling_episode.digest())
        self.assertEqual(len(digests), 4)


if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()
