#!/usr/bin/env python3
"""Must-fail counterparts for the kernel controls (`MF-KRN-001..003`).

The harness contract (`verification-threat-evaluation-plan.md` §3): each test
runs once against the reference implementation and once against the named
broken counterpart. The harness succeeds only when the reference passes and
the broken run exits non-zero **for its expected reason** — a broken run that
fails for an unrelated reason proves nothing about the control.

Each defect is injected at exactly one seam. Everything else is the real
kernel, so a scenario that still passes with the defect present means the
control is inert, which is the failure these tests exist to detect.

    python3 test/broken/fixtures/kernel/scenario.py --variant reference
    python3 test/broken/fixtures/kernel/scenario.py --variant constant-classifier
    python3 test/broken/fixtures/kernel/scenario.py --variant span-reset
    python3 test/broken/fixtures/kernel/scenario.py --variant unbound-grant
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from test.kernel import fakes  # noqa: E402
from vanguard.packages.kernel import (  # noqa: E402
    Accumulation,
    FailurePath,
    Grant,
    GrantIssuer,
    HeldAuthority,
    Span,
    StandardClassifier,
    Trust,
    descriptor_of,
)


class Failed(AssertionError):
    """Raised with the exact string the manifest expects to see."""


def check(condition: bool, message: str) -> None:
    if not condition:
        raise Failed(message)


# ---------------------------------------------------------------------------
# The planted defects
# ---------------------------------------------------------------------------


class ConstantClassifier:
    """`MF-KRN-001`. The prototype hardcoded this to *true* for every
    subprocess call, so the authority predicate appeared to fail closed on all
    tool use and three documents recorded the deadlock as a property of the
    taint model."""

    def __init__(self, value: bool = True) -> None:
        self._value = value

    def widens_capability(self, request) -> bool:
        return self._value


class ResettingAccumulation:
    """`MF-KRN-002`. Spans reset at each turn instead of accumulating.

    With the reset, the predicate evaluates over a set that cannot contain an
    untrusted span by construction, so the untrusted branch is unreachable
    dead code — the invariant exists, has a test, and does nothing.
    """

    def __init__(self, spans=()) -> None:
        self._spans = list(spans)

    def advance_turn(self, *, reply_spans=(), result_spans=()):
        self._spans = list(reply_spans)  # the defect: previous turns dropped
        return self

    @property
    def spans(self):
        return tuple(self._spans)


class UnboundGrantIssuer(GrantIssuer):
    """`MF-KRN-003`. Issues a grant that binds no descriptor, and verifies it
    without comparing one — the shape of the defect `ADR-0039` describes,
    where the missing field stayed invisible because nothing refused it."""

    def issue(self, **kwargs) -> Grant:
        kwargs["descriptor_digest"] = ""
        grant = Grant(
            grant_id=kwargs["grant_id"], principal=kwargs["principal"],
            descriptor_digest="", scope=kwargs["scope"],
            expires_at=kwargs["expires_at"], purpose_digest=kwargs["purpose_digest"],
            single_use=kwargs.get("single_use", True))
        self._issued[grant.grant_id] = grant
        return grant

    def verify(self, grant, *, descriptor_digest, now, cross_process=False):
        from vanguard.packages.kernel.grants import GrantVerification

        return GrantVerification(True)  # the defect: no point-of-effect check


# ---------------------------------------------------------------------------
# The scenarios
# ---------------------------------------------------------------------------


def scenario_classifier(variant: str) -> None:
    """`K-32`: widening is a computed predicate, so one scenario must classify
    false and the other true. No constant satisfies both."""
    if variant == "constant-classifier":
        classifier = ConstantClassifier(True)
    else:
        classifier = StandardClassifier([HeldAuthority(
            "agent-1", frozenset({"fs.read", "fs.write"}), (fakes.WORKSPACE,), max_depth=4)])

    within = classifier.widens_capability(fakes.request())
    escalating = classifier.widens_capability(fakes.request(action="exec.run"))
    check(within is False,
          "widening classifier is constant: work inside held authority classified as widening")
    check(escalating is True,
          "widening classifier is constant: escalation outside held authority classified as safe")


def scenario_spans(variant: str) -> None:
    """`K-33`: tool output is untrusted at birth and steers later turns, so
    the untrusted branch must still be reachable at turn 2."""
    accumulation = (ResettingAccumulation([fakes.operator_span()])
                    if variant == "span-reset"
                    else Accumulation([fakes.operator_span()]))
    accumulation.advance_turn(result_spans=[fakes.untrusted_result_span()])
    accumulation.advance_turn(
        reply_spans=[Span("reply-2", Trust.AGENT_DERIVED, "model_reply")])

    harness = fakes.build(held_actions=frozenset({"fs.read"}))
    result = harness.kernel.dispatch(
        fakes.request(), requested_scope=fakes.child_scope(),
        reservation=fakes.reservation(), spans=accumulation.spans)
    check(result.failure is FailurePath.DENIED_UNTRUSTED_JUSTIFYING,
          "justifying spans reset between turns: the untrusted-result branch is unreachable, "
          f"widening request was resolved as {result.failure.value}")
    check(harness.adapter.calls == [],
          "justifying spans reset between turns: the effect executed")


def scenario_grant_binding(variant: str) -> None:
    """`K-18` / `CT-51`: the grant binds one call, verified at the point of
    effect. Approve descriptor A, then execute B."""
    issuer = UnboundGrantIssuer() if variant == "unbound-grant" else GrantIssuer()
    harness = fakes.build(issuer=issuer)

    approved = fakes.request(args={"path": "/workspace/src/a.ts", "bytes": "12"})
    substituted = fakes.request(args={"path": "/workspace/src/evil.ts", "bytes": "12"})

    # Issue against the approved call, then present the substituted one at S8.
    grant = issuer.issue(
        grant_id="grant-approved", principal="agent-1",
        descriptor_digest=descriptor_of(approved.action, approved.args),
        scope=fakes.child_scope(), expires_at=fakes.FAR_FUTURE,
        purpose_digest="sha256:" + "a" * 64)
    verification = issuer.verify(
        grant, descriptor_digest=descriptor_of(substituted.action, substituted.args),
        now=harness.clock.now())
    check(not verification.ok,
          "grant omits or bypasses descriptor binding: a substituted call verified against "
          "a grant issued for a different call")
    check(verification.failure is FailurePath.GRANT_MISMATCH,
          "grant omits or bypasses descriptor binding: rejection was not a descriptor mismatch")

    # And a grant with no binding at all must not be issuable.
    if variant != "unbound-grant":
        try:
            issuer.issue(grant_id="grant-unbound", principal="agent-1",
                         descriptor_digest="", scope=fakes.child_scope(),
                         expires_at=fakes.FAR_FUTURE, purpose_digest="sha256:" + "a" * 64)
        except Exception:
            pass
        else:
            raise Failed("grant omits or bypasses descriptor binding: issuance accepted "
                         "a grant with no descriptorDigest")
    else:
        unbound = issuer.issue(grant_id="grant-unbound", principal="agent-1",
                               descriptor_digest="", scope=fakes.child_scope(),
                               expires_at=fakes.FAR_FUTURE,
                               purpose_digest="sha256:" + "a" * 64)
        check(bool(unbound.descriptor_digest),
              "grant omits or bypasses descriptor binding: issuance accepted a grant with "
              "no descriptorDigest")


SCENARIOS = {
    "reference": (scenario_classifier, scenario_spans, scenario_grant_binding),
    "constant-classifier": (scenario_classifier,),
    "span-reset": (scenario_spans,),
    "unbound-grant": (scenario_grant_binding,),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", required=True, choices=sorted(SCENARIOS))
    variant = parser.parse_args().variant
    try:
        for scenario in SCENARIOS[variant]:
            scenario(variant)
    except Failed as failure:
        print(f"KERNEL MUST-FAIL: {failure}")
        return 1
    print(f"KERNEL SCENARIO PASS: {variant}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
