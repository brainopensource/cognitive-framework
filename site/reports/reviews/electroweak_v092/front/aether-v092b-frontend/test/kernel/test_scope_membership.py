"""Kernel-side scope membership (`ADR-0067`, `RF-26`).

A sealed scope (set by `attenuate()` when a parent withholds verbs) denies
`request.action ∉ requested_scope.actions` before the approval gate. An
unsealed narrower scope may still widen on trusted justification — that is
`test_widening_alone_is_not_a_violation`. Depth is not the signal.
"""

from __future__ import annotations

import unittest

from vanguard.packages.kernel import (
    Constraints,
    EffectRequest,
    FailurePath,
    Mode,
    Outcome,
    Scope,
    StandardPolicy,
)

RESOURCE = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}


def _constraints(**overrides) -> Constraints:
    base = dict(expires_at="2099-01-01T00:00:00.000Z", max_uses=100,
                budget_usd_micros=1_000_000, max_depth=4)
    base.update(overrides)
    return Constraints(**base)


def _scope(actions, depth: int = 0, *, sealed: bool = False) -> Scope:
    return Scope(actions=frozenset(actions), resources=(RESOURCE,),
                 constraints=_constraints(), depth=depth, sealed=sealed)


def _request(action: str) -> EffectRequest:
    return EffectRequest(action=action, resource=RESOURCE, args={"path": "a.py"},
                         principal="agent-1", run_id="run-1")


def _policy(parent: Scope, **overrides) -> StandardPolicy:
    base = dict(parent_scope=parent, mode=Mode.BENCHMARK,
                approval_required_above="high",
                risk_of={"fs.read": "low", "patch.apply": "low"})
    base.update(overrides)
    return StandardPolicy(**base)


class ActionMembershipIsEnforced(unittest.TestCase):
    """What the kernel does today with an action absent from the episode scope."""

    PARENT = _scope({"fs.read", "patch.apply"})

    def test_an_action_outside_the_requested_scope_is_denied(self) -> None:
        """RF-26: policy denies even with no episode-engine pre-filter."""
        decision = _policy(self.PARENT).authorize(
            _request("patch.apply"),
            widens_capability=False,
            requested_scope=_scope({"fs.read"}, depth=1, sealed=True),
        )
        self.assertIs(decision.outcome, Outcome.REJECT)
        self.assertIs(decision.failure, FailurePath.DENIED_SCOPE_ESCALATION)

    def test_the_denial_names_what_was_requested_and_what_was_grantable(self) -> None:
        decision = _policy(self.PARENT).authorize(
            _request("patch.apply"),
            widens_capability=False,
            requested_scope=_scope({"fs.read"}, depth=1, sealed=True),
        )
        self.assertIn("patch.apply", str(decision.requested))
        self.assertIn("fs.read", str(decision.grantable))

    def test_the_denial_is_alertable(self) -> None:
        decision = _policy(self.PARENT).authorize(
            _request("patch.apply"),
            widens_capability=False,
            requested_scope=_scope({"fs.read"}, depth=1, sealed=True),
        )
        self.assertTrue(decision.alertable)

    def test_an_action_inside_the_requested_scope_is_allowed(self) -> None:
        """Fail-closed must not mean fail-useless."""

        decision = _policy(self.PARENT).authorize(
            _request("fs.read"),
            widens_capability=False,
            requested_scope=_scope({"fs.read"}, depth=1),
        )
        self.assertIs(decision.outcome, Outcome.ALLOW)

    def test_a_full_scope_episode_keeps_every_verb_it_holds(self) -> None:
        for action in ("fs.read", "patch.apply"):
            with self.subTest(action=action):
                decision = _policy(self.PARENT).authorize(
                    _request(action),
                    widens_capability=False,
                    requested_scope=self.PARENT,
                )
                self.assertIs(decision.outcome, Outcome.ALLOW)

    def test_membership_is_checked_before_the_approval_gate(self) -> None:
        """An ungranted verb is refused, not escalated to a human."""
        decision = _policy(self.PARENT, mode=Mode.INTERACTIVE,
                           approval_required_above="low",
                           risk_of={"patch.apply": "high"}).authorize(
            _request("patch.apply"),
            widens_capability=False,
            requested_scope=_scope({"fs.read"}, depth=1, sealed=True),
        )
        self.assertIs(decision.outcome, Outcome.REJECT)
        self.assertIsNot(decision.outcome, Outcome.REQUIRE_APPROVAL)


class ScopeEscalationStillOutranksMembership(unittest.TestCase):
    """Ordering: a scope wider than the parent is still `F-10`, not `F-09`."""

    def test_a_widening_scope_is_denied_on_the_scope_dimension(self) -> None:
        parent = _scope({"fs.read"})
        decision = _policy(parent).authorize(
            _request("patch.apply"),
            widens_capability=True,
            requested_scope=_scope({"fs.read", "patch.apply"}, depth=1),
        )
        self.assertIs(decision.outcome, Outcome.REJECT)
        self.assertIs(decision.failure, FailurePath.DENIED_SCOPE_ESCALATION)


class UnsealedNarrowingIsNotASeal(unittest.TestCase):
    """Spine: a depth-1 narrower scope may still widen on trusted justification."""

    def test_an_unsealed_narrower_scope_does_not_deny_membership(self) -> None:
        parent = _scope({"fs.read", "patch.apply"})
        decision = _policy(parent).authorize(
            _request("patch.apply"),
            widens_capability=False,
            requested_scope=_scope({"fs.read"}, depth=1, sealed=False),
        )
        self.assertIs(decision.outcome, Outcome.ALLOW)


class UntrustedJustificationIsUnaffected(unittest.TestCase):
    """`F-09` must keep firing for in-scope actions justified by untrusted spans."""

    def test_an_in_scope_widening_on_untrusted_spans_is_still_denied(self) -> None:
        from vanguard.packages.kernel import Span, Trust

        parent = _scope({"fs.read", "patch.apply"})
        untrusted = Span("tool-result-1", Trust.UNTRUSTED_EXTERNAL, "tool_result")
        decision = _policy(parent).authorize(
            _request("patch.apply"),
            widens_capability=True,
            requested_scope=parent,
            spans=(untrusted,),
        )
        self.assertIs(decision.outcome, Outcome.REJECT)
        self.assertIs(decision.failure, FailurePath.DENIED_UNTRUSTED_JUSTIFYING)


if __name__ == "__main__":
    unittest.main()
