"""Kernel-side scope membership: what holds today, and the gap that does not.

`ADR-0067` is **proposed, not accepted** — see the register. The intended rule
(deny when `request.action ∉ requested_scope.actions`) was implemented here and
**reverted**, because it cannot be expressed in `policy.py` alone without
deleting a designed property.

The obstacle, recorded so nobody re-derives it: `Scope` carries no signal
distinguishing *attenuated and sealed* from *attenuated and still permitted to
widen on trusted justification*. Neither depth nor strict-narrowing is a usable
proxy — `test/trust/spine.py`'s `requested_scope()` is depth 1 and strictly
narrower than its parent, and the system deliberately allows it to widen to
`fs.delete` on a trusted operator span. `test_widening_alone_is_not_a_violation`
exists exactly so that an implementation denying every widening cannot pass.

The exploit path is closed at the agency boundary (`S8-B-01`, `8f5f16d`): an
attenuated child engine declines to emit the request. What is still open is
defence in depth for a caller constructing a `Kernel` directly. The one
`expectedFailure` below is that gap, kept live so it cannot be forgotten.
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


def _scope(actions, depth: int = 0) -> Scope:
    return Scope(actions=frozenset(actions), resources=(RESOURCE,),
                 constraints=_constraints(), depth=depth)


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

    @unittest.expectedFailure
    def test_an_action_outside_the_requested_scope_is_denied(self) -> None:
        """THE LIVE GAP (`ADR-0067`, proposed). Fails today, by design of this file.

        A caller constructing a `Kernel` directly can dispatch a verb the
        episode scope does not contain, provided the principal holds it. The
        episode engine no longer allows this for attenuated children, so the
        system is not exploitable through the normal path -- but the kernel
        itself does not refuse, and this marker says so out loud.
        """
        decision = _policy(self.PARENT).authorize(
            _request("patch.apply"),
            widens_capability=False,
            requested_scope=_scope({"fs.read"}, depth=1),
        )
        self.assertIs(decision.outcome, Outcome.REJECT)
        self.assertIs(decision.failure, FailurePath.DENIED_SCOPE_ESCALATION)

    @unittest.expectedFailure
    def test_the_denial_names_what_was_requested_and_what_was_grantable(self) -> None:
        """Part of the same proposed rule. See `ADR-0067`."""

        decision = _policy(self.PARENT).authorize(
            _request("patch.apply"),
            widens_capability=False,
            requested_scope=_scope({"fs.read"}, depth=1),
        )
        self.assertIn("patch.apply", str(decision.requested))
        self.assertIn("fs.read", str(decision.grantable))

    @unittest.expectedFailure
    def test_the_denial_is_alertable(self) -> None:
        """Part of the same proposed rule. See `ADR-0067`."""

        decision = _policy(self.PARENT).authorize(
            _request("patch.apply"),
            widens_capability=False,
            requested_scope=_scope({"fs.read"}, depth=1),
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

    @unittest.expectedFailure
    def test_membership_is_checked_before_the_approval_gate(self) -> None:
        """Part of the same proposed rule, and its sharpest edge.

        An ungranted verb should be refused, not escalated to a human: asking a
        reviewer to approve something the episode was never granted turns an
        authorisation bug into a social-engineering surface. See `ADR-0067`.
        """

        decision = _policy(self.PARENT, mode=Mode.INTERACTIVE,
                           approval_required_above="low",
                           risk_of={"patch.apply": "high"}).authorize(
            _request("patch.apply"),
            widens_capability=False,
            requested_scope=_scope({"fs.read"}, depth=1),
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
