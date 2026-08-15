"""The authority predicate and its two operands (`05 §5`).

> Untrusted content may inform work; it may never authorise it.

Both operands have failed silently in this project's history, and both
failures looked like working controls: a documented, tested, inert check. The
tests here are written so that they fail against those specific defects rather
than against an obviously broken kernel.
"""

from __future__ import annotations

import unittest

from vanguard.packages.kernel import (
    Accumulation,
    FailurePath,
    HeldAuthority,
    Span,
    StandardClassifier,
    Trust,
    authority_violation,
    combine,
)

from . import fakes


class LabelAlgebra(unittest.TestCase):
    def test_labels_never_improve(self) -> None:
        """`K-28`: no operation produces a label lower than its inputs."""
        for weaker in Trust:
            for stronger in Trust:
                with self.subTest(a=weaker, b=stronger):
                    result = combine(weaker, stronger)
                    self.assertGreaterEqual(result.rank, weaker.rank)
                    self.assertGreaterEqual(result.rank, stronger.rank)

    def test_combination_is_commutative_and_idempotent(self) -> None:
        for a in Trust:
            for b in Trust:
                self.assertIs(combine(a, b), combine(b, a))
            self.assertIs(combine(a, a), a)

    def test_untrusted_boundary(self) -> None:
        self.assertFalse(Trust.OPERATOR.is_untrusted)
        self.assertFalse(Trust.SYSTEM.is_untrusted)
        self.assertFalse(Trust.AGENT_DERIVED.is_untrusted)
        self.assertTrue(Trust.UNTRUSTED_DERIVED.is_untrusted)
        self.assertTrue(Trust.UNTRUSTED_EXTERNAL.is_untrusted)


class SpanAccumulation(unittest.TestCase):
    """`K-33`: monotone, never reset within a run."""

    def test_spans_accumulate_across_turns(self) -> None:
        accumulation = Accumulation([fakes.operator_span("brief")])
        self.assertFalse(accumulation.has_untrusted)
        accumulation.advance_turn(
            reply_spans=[Span("reply-1", Trust.AGENT_DERIVED, "model_reply")],
            result_spans=[fakes.untrusted_result_span("tool-1")])
        # From the second round onward, tool output can steer a tool call.
        self.assertTrue(accumulation.has_untrusted)
        accumulation.advance_turn(reply_spans=[Span("reply-2", Trust.AGENT_DERIVED, "model_reply")])
        self.assertTrue(accumulation.has_untrusted,
                        "a later turn must not lose the earlier untrusted span")
        self.assertEqual(len(accumulation), 4)

    def test_accumulation_is_monotone_in_span_count(self) -> None:
        accumulation = Accumulation()
        sizes = []
        for turn in range(6):
            accumulation.advance_turn(
                reply_spans=[Span(f"reply-{turn}", Trust.AGENT_DERIVED, "model_reply")],
                result_spans=[Span(f"result-{turn}", Trust.UNTRUSTED_EXTERNAL, "tool_result")])
            sizes.append(len(accumulation))
        self.assertEqual(sizes, sorted(sizes))
        self.assertEqual(sizes[-1], 12)

    def test_re_observed_span_can_only_weaken(self) -> None:
        """`K-28` again, at the accumulator: a span cannot be laundered by
        being re-added with a better label."""
        accumulation = Accumulation([Span("s", Trust.UNTRUSTED_EXTERNAL, "tool_result")])
        accumulation.extend([Span("s", Trust.OPERATOR, "operator_brief")])
        self.assertIs(accumulation.spans[0].trust, Trust.UNTRUSTED_EXTERNAL)

    def test_child_return_enters_as_untrusted_derived_at_minimum(self) -> None:
        """`K-33`: a child operator starts a fresh accumulation, and its return
        value enters the parent's as untrusted-derived at minimum."""
        parent = Accumulation([fakes.operator_span()])
        parent.child_return([Span("child-result", Trust.OPERATOR, "child_operator")])
        self.assertTrue(parent.has_untrusted)

    def test_there_is_no_public_way_to_reset(self) -> None:
        """The defect this rule exists for is a *reset*. Making union the only
        mutation means a reset has to be written deliberately, which is what
        the broken counterpart in `test/broken/fixtures/kernel/` does."""
        accumulation = Accumulation([fakes.untrusted_result_span()])
        for forbidden in ("clear", "reset", "remove", "discard", "pop"):
            self.assertFalse(hasattr(accumulation, forbidden), forbidden)


class Predicate(unittest.TestCase):
    """A violation needs *both* operands. Neither alone is a violation."""

    UNTRUSTED = (fakes.untrusted_result_span(),)
    TRUSTED = (fakes.operator_span(),)

    def test_widening_plus_untrusted_is_a_violation(self) -> None:
        result = authority_violation(self.UNTRUSTED, widens_capability=True)
        self.assertTrue(result.violated)
        self.assertEqual(result.untrusted_span_ids, ("tool-result-1",))

    def test_untrusted_without_widening_is_allowed(self) -> None:
        """This is the point: untrusted content is supposed to inform work."""
        self.assertFalse(authority_violation(self.UNTRUSTED, widens_capability=False).violated)

    def test_widening_without_untrusted_is_allowed(self) -> None:
        """An ordinary privileged request from an operator brief."""
        self.assertFalse(authority_violation(self.TRUSTED, widens_capability=True).violated)

    def test_neither_is_allowed(self) -> None:
        self.assertFalse(authority_violation(self.TRUSTED, widens_capability=False).violated)

    def test_one_untrusted_span_among_many_is_enough(self) -> None:
        spans = (fakes.operator_span("a"), fakes.operator_span("b"),
                 fakes.untrusted_result_span("c"))
        self.assertTrue(authority_violation(spans, widens_capability=True).violated)


class WideningClassifier(unittest.TestCase):
    """`K-32`, and why a constant cannot satisfy it (`MF-KRN-001`)."""

    def setUp(self) -> None:
        self.classifier = StandardClassifier([HeldAuthority(
            "agent-1", frozenset({"fs.read", "fs.write"}), (fakes.WORKSPACE,), max_depth=4)])

    def test_within_held_authority_does_not_widen(self) -> None:
        """Running the test suite under an already-held execution capability
        escalates nothing and classifies false."""
        self.assertFalse(self.classifier.widens_capability(fakes.request()))

    def test_unheld_action_widens(self) -> None:
        self.assertTrue(self.classifier.widens_capability(fakes.request(action="exec.run")))

    def test_resource_outside_the_perimeter_widens(self) -> None:
        self.assertTrue(self.classifier.widens_capability(
            fakes.request(resource={"kind": "fs", "root": "/etc", "paths": ["/etc/shadow"]})))

    def test_egress_outside_the_allowlist_widens(self) -> None:
        self.assertTrue(self.classifier.widens_capability(
            fakes.request(action="net.fetch", resource=fakes.EGRESS)))

    def test_cross_kind_comparison_fails_closed(self) -> None:
        """`K-48`: an undefined pair is denied, so it lands on the widening
        side rather than being treated as contained."""
        self.assertTrue(self.classifier.widens_capability(
            fakes.request(resource={"kind": "generic", "uriPattern": "file:///workspace/src"})))

    def test_unknown_principal_holds_nothing(self) -> None:
        self.assertTrue(self.classifier.widens_capability(fakes.request(principal="stranger")))

    def test_depth_beyond_the_ceiling_widens(self) -> None:
        """`K-24`: depth is a budget dimension."""
        self.assertTrue(self.classifier.widens_capability(fakes.request(depth=9)))

    def test_no_constant_satisfies_both_scenarios(self) -> None:
        """The must-fail property, stated as a test.

        `MF-KRN-001` plants a constant classifier. Whichever constant is
        chosen, one of these two assertions fails — which is exactly what
        makes the planted defect detectable rather than merely unlikely.
        """
        within = self.classifier.widens_capability(fakes.request())
        escalating = self.classifier.widens_capability(fakes.request(action="exec.run"))
        self.assertNotEqual(within, escalating)


class PredicateThroughDispatch(unittest.TestCase):
    """The predicate as the kernel actually evaluates it, at S5."""

    def test_untrusted_span_cannot_authorise_a_widening_request(self) -> None:
        """The prompt-injection case: repository or tool content asking for
        broader authority. Denied, and alertable."""
        harness = fakes.build(held_actions=frozenset({"fs.read"}))
        result = harness.kernel.dispatch(
            fakes.request(justifying_spans=(fakes.untrusted_result_span(),)),
            requested_scope=fakes.child_scope(),
            reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.DENIED_UNTRUSTED_JUSTIFYING)
        denial = result.events[-1]
        self.assertEqual(denial.kind, "AuthorizationDenied")
        self.assertTrue(denial.alertable)
        self.assertEqual(harness.adapter.calls, [])

    def test_untrusted_span_may_still_justify_already_held_work(self) -> None:
        """"Already granted safe work may continue" — the adversarial suite's
        pass condition for prompt injection."""
        harness = fakes.build()
        result = harness.kernel.dispatch(
            fakes.request(justifying_spans=(fakes.untrusted_result_span(),)),
            requested_scope=fakes.child_scope(),
            reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.OK)

    def test_accumulated_spans_are_what_the_kernel_evaluates(self) -> None:
        """`K-33` through dispatch: a span from turn 1 still denies at turn 3."""
        accumulation = Accumulation([fakes.operator_span()])
        accumulation.advance_turn(result_spans=[fakes.untrusted_result_span()])
        accumulation.advance_turn(
            reply_spans=[Span("reply-2", Trust.AGENT_DERIVED, "model_reply")])
        harness = fakes.build(held_actions=frozenset({"fs.read"}))
        result = harness.kernel.dispatch(
            fakes.request(), requested_scope=fakes.child_scope(),
            reservation=fakes.reservation(), spans=accumulation.spans)
        self.assertIs(result.failure, FailurePath.DENIED_UNTRUSTED_JUSTIFYING)
