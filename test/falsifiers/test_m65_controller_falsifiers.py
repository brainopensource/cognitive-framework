"""M-6.5: the five ways an adaptive-strategy result gets manufactured (`B-M65`).

`test_m65_paired_evaluation.py` attacks the *arithmetic* of the comparison.
This file attacks the *inputs and outputs of the controller itself*, because a
harness that compares two arms honestly still reports nonsense if the treatment
arm was deciding on stale signals, answering nondeterministically, or quietly
writing itself a larger budget.

Each class below is a way a controller could look like it helped without ever
having helped.  All five must fail closed -- raise -- rather than degrade into
a proposal nobody can attribute.
"""

from __future__ import annotations

import unittest

from vanguard.packages.domain.ledger.agent_view import AgentView
from vanguard.packages.domain.ledger.progress import ConfidenceRecord, ProgressView
from vanguard.packages.ports.meta_controller import StrategyDirective
from vanguard.packages.runtime.meta_controller import (
    ControllerInputError,
    ControllerOutputError,
    consult,
    guarded_consult,
    validate_confidence,
    validate_directive,
    view_reference_set,
)

VIEW = AgentView(
    lineage_id="lin-1",
    goal="fix the failing test",
    settled_effects={"eff-1": "completed"},
    attempts=({"id": "att-1"},),
    strategy="depth-first",
    context_epoch=3,
)
PROGRESS = ProgressView(assessment="stalled", stall_count=2)


def _record(subject: str = "eff-1", *, epoch: int | None = 3) -> ConfidenceRecord:
    calibration = {"method": "held-out"}
    if epoch is not None:
        calibration["contextEpoch"] = epoch
    return ConfidenceRecord("behavioral", 0.4, subject, ("event-1",), calibration)


class _Fixed:
    controller_id = "det-1"

    def __init__(self, directive: StrategyDirective | None) -> None:
        self._directive = directive

    def assess(self, view, progress, confidence):
        return self._directive


class StaleConfidenceIsRefused(unittest.TestCase):
    """A decision on a pre-compaction signal answers a situation that is gone."""

    def test_a_record_from_an_earlier_context_epoch_is_stale(self) -> None:
        with self.assertRaises(ControllerInputError) as ctx:
            validate_confidence(VIEW, (_record(epoch=2),))
        self.assertIn("stale", str(ctx.exception))

    def test_a_record_from_a_later_epoch_is_equally_refused(self) -> None:
        # Not "newer is fine": a signal from an epoch the view has not reached
        # cannot have been derived from the history the view describes.
        with self.assertRaises(ControllerInputError):
            validate_confidence(VIEW, (_record(epoch=4),))

    def test_an_undated_record_cannot_be_shown_to_be_current(self) -> None:
        with self.assertRaises(ControllerInputError) as ctx:
            validate_confidence(VIEW, (_record(epoch=None),))
        self.assertIn("context epoch", str(ctx.exception))

    def test_a_current_record_passes(self) -> None:
        validate_confidence(VIEW, (_record(),))


class MissingReferencesAreRefused(unittest.TestCase):
    """Confidence about something the projection never saw is not evidence."""

    def test_a_subject_outside_the_view_is_refused(self) -> None:
        with self.assertRaises(ControllerInputError) as ctx:
            validate_confidence(VIEW, (_record("eff-does-not-exist"),))
        self.assertIn("not in the view", str(ctx.exception))

    def test_the_reference_set_is_derived_from_the_projection(self) -> None:
        refs = view_reference_set(VIEW)
        for expected in ("lin-1", "goal", "eff-1", "att-1", "depth-first"):
            self.assertIn(expected, refs)

    def test_the_reference_set_is_a_fold_not_a_free_pass(self) -> None:
        self.assertNotIn("anything", view_reference_set(VIEW))
        self.assertEqual(view_reference_set(AgentView("bare")),
                         frozenset({"bare", "goal"}))

    def test_the_goal_is_referenceable_even_though_c06_keeps_it_out_of_the_ledger(self) -> None:
        # The lineage has a goal whether or not its text was ledgered, so
        # goal-level confidence must remain expressible on the real path.
        validate_confidence(AgentView("lin-2", context_epoch=0), (
            ConfidenceRecord("behavioral", 0.4, "goal", ("e",),
                             {"contextEpoch": 0}),))


class NondeterministicDirectivesAreRefused(unittest.TestCase):
    """Two answers to one question makes the paired arms incomparable."""

    def test_a_controller_that_varies_on_identical_inputs_is_refused(self) -> None:
        class Flapping:
            controller_id = "flap"

            def __init__(self) -> None:
                self.calls = 0

            def assess(self, view, progress, confidence):
                self.calls += 1
                return StrategyDirective(
                    "revise_plan" if self.calls % 2 else "request_context",
                    "flap", "reason")

        with self.assertRaises(ControllerOutputError) as ctx:
            guarded_consult(Flapping(), VIEW, PROGRESS, (_record(),))
        self.assertIn("nondeterministic", str(ctx.exception))

    def test_a_deterministic_controller_is_consulted_normally(self) -> None:
        directive = StrategyDirective("request_context", "det-1", "missing knowledge")
        proposal = guarded_consult(_Fixed(directive), VIEW, PROGRESS, (_record(),))
        self.assertEqual(proposal.kind, "request_context")
        self.assertEqual(proposal.attribution["confidenceRefs"], (_record().digest(),))

    def test_declining_to_act_is_a_valid_deterministic_answer(self) -> None:
        self.assertIsNone(guarded_consult(_Fixed(None), VIEW, PROGRESS, (_record(),)))


class BudgetBypassIsRefused(unittest.TestCase):
    """A strategy hint may spend less; it may never raise its own ceiling."""

    def _delegate(self, **scope) -> StrategyDirective:
        return StrategyDirective("delegate", "c", "stalled", brief="run tests",
                                 scope_slice=scope)

    def test_a_slice_within_the_remaining_budget_is_allowed(self) -> None:
        validate_directive(self._delegate(maxTurns=2), remaining_budget={"turns": 5})

    def test_a_slice_larger_than_what_remains_is_refused(self) -> None:
        with self.assertRaises(ControllerOutputError) as ctx:
            validate_directive(self._delegate(maxTurns=9), remaining_budget={"turns": 5})
        self.assertIn("cannot enlarge a budget", str(ctx.exception))

    def test_a_budget_slice_with_no_ceiling_to_check_is_refused(self) -> None:
        # Unchecked is not the same as allowed. Without a remaining-budget
        # ceiling there is nothing to compare against, so it fails closed.
        with self.assertRaises(ControllerOutputError):
            validate_directive(self._delegate(maxTurns=1))

    def test_an_unknown_budget_dimension_is_refused(self) -> None:
        with self.assertRaises(ControllerOutputError):
            validate_directive(self._delegate(maxWidgets=1),
                               remaining_budget={"turns": 5})

    def test_a_non_integer_budget_slice_is_refused(self) -> None:
        for bad in (1.5, True, -1, "2"):
            with self.assertRaises(ControllerOutputError):
                validate_directive(self._delegate(maxTurns=bad),
                                   remaining_budget={"turns": 5})

    def test_guarded_consult_enforces_the_ceiling(self) -> None:
        controller = _Fixed(self._delegate(maxTurns=99))
        with self.assertRaises(ControllerOutputError):
            guarded_consult(controller, VIEW, PROGRESS, (_record(),),
                            remaining_budget={"turns": 3})


class AuthorityEscalationIsRefused(unittest.TestCase):
    """Metacognition is policy. A policy that grants is not policy any more."""

    def test_a_scope_carrying_capabilities_is_refused(self) -> None:
        for key in ("capabilities", "grants", "authority", "principal", "verb",
                    "selector", "approval", "signature", "uid"):
            directive = StrategyDirective("delegate", "c", "r", brief="b",
                                          scope_slice={key: "anything"})
            with self.assertRaises(ControllerOutputError) as ctx:
                validate_directive(directive)
            self.assertIn("authority", str(ctx.exception), key)

    def test_the_directive_kind_set_stays_closed(self) -> None:
        # An escalating controller's first move is a new verb.
        with self.assertRaises(ValueError):
            StrategyDirective("grant_capability", "c", "r")

    def test_the_proposal_is_an_ordinary_value_with_no_effect_path(self) -> None:
        proposal = guarded_consult(
            _Fixed(StrategyDirective("revise_plan", "c", "stalled")),
            VIEW, PROGRESS, (_record(),))
        self.assertEqual(set(proposal.payload), {"reason"})
        for forbidden in ("emit", "store", "model", "grant", "apply", "run"):
            self.assertFalse(hasattr(proposal, forbidden), forbidden)


class TheSeamStaysOptIn(unittest.TestCase):
    def test_no_controller_means_no_proposal_on_either_path(self) -> None:
        self.assertIsNone(consult(None, VIEW, PROGRESS))
        self.assertIsNone(guarded_consult(None, VIEW, PROGRESS))

    def test_the_guarded_path_and_the_seam_agree_on_a_clean_case(self) -> None:
        directive = StrategyDirective("conclude", "c", "goal met")
        self.assertEqual(
            consult(_Fixed(directive), VIEW, PROGRESS, (_record(),)),
            guarded_consult(_Fixed(directive), VIEW, PROGRESS, (_record(),)))


if __name__ == "__main__":
    unittest.main()
