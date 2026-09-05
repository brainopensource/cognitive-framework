"""T-70: the approval threshold comes from the manifest, not from this file.

`HarnessSession` used to hardcode `approval_required_above="low"`, so every
capability a coding preset exists to use -- medium `patch.apply`, high
`proc.exec` -- needed a human.  In benchmark mode `StandardPolicy` turns that
ask into `DENIED_ASK_FAIL_CLOSED` (`F-07`), so the product path could not patch
or execute at all.  The manifest already declares the answer in
`components.approval_policy`; these falsifiers pin that it is read, that a pack
declaring nothing usable still fails closed, and that the literal is gone.
"""

from __future__ import annotations

import inspect
import json
import unittest
from dataclasses import dataclass
from typing import Any, Mapping

import vanguard.packages.runtime.session as session_module
from vanguard.packages.kernel import (
    EffectRequest,
    FailurePath,
    Mode,
    Outcome,
    StandardPolicy,
)
from vanguard.packages.runtime.root import Runtime
from vanguard.packages.runtime.session import resolve_approval_threshold
from vanguard.packages.runtime.wiring import _scope_for

PRODUCT_RISKS: Mapping[str, str] = {
    "fs.read": "low",
    "fs.search": "low",
    "patch.apply": "medium",
    "proc.exec": "high",
    "agency.finish": "low",
}


@dataclass(frozen=True)
class _Frozen:
    identity: Mapping[str, Any]


@dataclass(frozen=True)
class _Harness:
    """The duck type the resolver reads: a frozen identity and declared risks."""

    frozen: _Frozen
    risk_of: Mapping[str, str]

    @classmethod
    def declaring(cls, policy: Any, risk_of: Mapping[str, str] = PRODUCT_RISKS) -> "_Harness":
        text = policy if isinstance(policy, str) or policy is None else json.dumps(policy)
        return cls(_Frozen({"approvalPolicy": text}), risk_of)


def product_harness() -> Any:
    """The composed product default; its declared policy is the subject here."""
    return Runtime.compose("vg-code-default", episode_id="ep-approval")


def _dispatch(threshold: str | None, action: str, *, mode: Mode) -> Any:
    """Authorize one request under `threshold`, through the real product scope."""
    harness = product_harness()
    scope = _scope_for(harness, workspace_access="workspace-write")
    policy = StandardPolicy(
        parent_scope=scope, mode=mode,
        approval_required_above=threshold, risk_of=harness.risk_of,
    )
    return policy.authorize(
        EffectRequest(action=action, resource="fs://workspace", args={},
                      principal="agent-approval", run_id="run-approval"),
        widens_capability=False, requested_scope=scope, spans=(),
    )


class TestDeclaredThresholdIsRead(unittest.TestCase):
    def test_the_product_default_manifest_declares_standard(self) -> None:
        """The composed pack carries the policy; no second artifact is authored."""
        harness = Runtime.compose("vg-code-default", episode_id="ep-approval")
        declared = json.loads(harness.frozen.identity["approvalPolicy"])
        self.assertEqual(declared["mode"], "assisted")
        self.assertEqual(declared["threshold"], "standard")
        self.assertEqual(list(declared["escalate_on"]), ["proc.exec"])
        self.assertEqual(
            resolve_approval_threshold(harness, interactive=False), "high")

    def test_standard_admits_the_two_verbs_a_coding_preset_exists_to_use(self) -> None:
        """The T-70 acceptance: no fail-closed ask denial on patch or exec."""
        harness = Runtime.compose("vg-code-default", episode_id="ep-approval")
        threshold = resolve_approval_threshold(harness, interactive=False)
        for action in ("patch.apply", "proc.exec"):
            with self.subTest(action=action):
                decision = _dispatch(threshold, action, mode=Mode.BENCHMARK)
                self.assertIs(decision.outcome, Outcome.ALLOW)
                self.assertIsNot(decision.failure, FailurePath.DENIED_ASK_FAIL_CLOSED)

    def test_the_hardcoded_threshold_denied_both_of_them(self) -> None:
        """The defect this closes, kept executable so it cannot come back."""
        for action in ("patch.apply", "proc.exec"):
            with self.subTest(action=action):
                decision = _dispatch("low", action, mode=Mode.BENCHMARK)
                self.assertIs(decision.outcome, Outcome.REJECT)
                self.assertIs(decision.failure, FailurePath.DENIED_ASK_FAIL_CLOSED)

    def test_a_declared_bare_risk_name_passes_through(self) -> None:
        harness = _Harness.declaring({"threshold": "medium"})
        self.assertEqual(resolve_approval_threshold(harness, interactive=False), "medium")

    def test_strict_asks_about_everything_above_a_read(self) -> None:
        harness = _Harness.declaring({"threshold": "strict"})
        threshold = resolve_approval_threshold(harness, interactive=False)
        self.assertEqual(threshold, "low")
        self.assertIs(
            _dispatch(threshold, "patch.apply", mode=Mode.BENCHMARK).failure,
            FailurePath.DENIED_ASK_FAIL_CLOSED,
        )
        self.assertIs(
            _dispatch(threshold, "fs.read", mode=Mode.BENCHMARK).outcome, Outcome.ALLOW)


class TestUndeclaredPolicyFailsClosed(unittest.TestCase):
    def test_a_missing_component_fails_closed(self) -> None:
        self.assertEqual(
            resolve_approval_threshold(_Harness.declaring(None), interactive=False), "low")

    def test_a_harness_without_a_frozen_identity_fails_closed(self) -> None:
        self.assertEqual(
            resolve_approval_threshold(_Harness(_Frozen({}), PRODUCT_RISKS),
                                       interactive=False),
            "low",
        )

    def test_malformed_json_fails_closed(self) -> None:
        self.assertEqual(
            resolve_approval_threshold(_Harness.declaring("{not json"),
                                       interactive=False),
            "low",
        )

    def test_a_policy_that_is_not_an_object_fails_closed(self) -> None:
        self.assertEqual(
            resolve_approval_threshold(_Harness.declaring("[\"standard\"]"),
                                       interactive=False),
            "low",
        )

    def test_an_unrecognised_threshold_fails_closed(self) -> None:
        """An invented tier is undeclared; it must not widen the grant."""
        self.assertEqual(
            resolve_approval_threshold(_Harness.declaring({"threshold": "yolo"}),
                                       interactive=False),
            "low",
        )

    def test_a_non_string_threshold_fails_closed(self) -> None:
        self.assertEqual(
            resolve_approval_threshold(_Harness.declaring({"threshold": 3}),
                                       interactive=False),
            "low",
        )


class TestTheDeclaredModeGovernsTheInteractiveRun(unittest.TestCase):
    """`F-08` is not weakened: a pack asking to be assisted keeps asking."""

    def test_assisted_keeps_asking_about_every_declared_capability(self) -> None:
        harness = Runtime.compose("vg-code-default", episode_id="ep-approval")
        threshold = resolve_approval_threshold(harness, interactive=True)
        for action in ("patch.apply", "proc.exec"):
            with self.subTest(action=action):
                self.assertIs(
                    _dispatch(threshold, action, mode=Mode.INTERACTIVE).outcome,
                    Outcome.REQUIRE_APPROVAL,
                )

    def test_a_read_still_does_not_interrupt_a_person(self) -> None:
        harness = Runtime.compose("vg-code-default", episode_id="ep-approval")
        threshold = resolve_approval_threshold(harness, interactive=True)
        self.assertIs(
            _dispatch(threshold, "fs.read", mode=Mode.INTERACTIVE).outcome, Outcome.ALLOW)

    def test_an_unstated_mode_is_read_as_asking_for_a_human(self) -> None:
        harness = _Harness.declaring({"threshold": "permissive"})
        self.assertEqual(resolve_approval_threshold(harness, interactive=True), "low")

    def test_a_benchmark_is_not_escalated_into_a_denial(self) -> None:
        """There is no human on a benchmark; escalating there only denies."""
        harness = Runtime.compose("vg-code-default", episode_id="ep-approval")
        threshold = resolve_approval_threshold(harness, interactive=False)
        self.assertIs(
            _dispatch(threshold, "proc.exec", mode=Mode.BENCHMARK).outcome,
            Outcome.ALLOW,
        )


class TestEscalateOnIsHonouredWhereAnAskCanBeAnswered(unittest.TestCase):
    """A pack that seats no human still names the verbs that must suspend."""

    def test_the_named_verb_is_lowered_back_under_the_threshold(self) -> None:
        harness = _Harness.declaring(
            {"mode": "autonomous", "threshold": "standard", "escalate_on": ["proc.exec"]})
        threshold = resolve_approval_threshold(harness, interactive=True)
        self.assertEqual(threshold, "medium")
        self.assertIs(
            _dispatch(threshold, "proc.exec", mode=Mode.INTERACTIVE).outcome,
            Outcome.REQUIRE_APPROVAL,
        )

    def test_escalation_does_not_reach_the_verbs_it_did_not_name(self) -> None:
        harness = _Harness.declaring(
            {"mode": "autonomous", "threshold": "standard", "escalate_on": ["proc.exec"]})
        threshold = resolve_approval_threshold(harness, interactive=True)
        self.assertIs(
            _dispatch(threshold, "patch.apply", mode=Mode.INTERACTIVE).outcome,
            Outcome.ALLOW,
        )

    def test_a_malformed_escalate_on_leaves_the_threshold_alone(self) -> None:
        harness = _Harness.declaring(
            {"mode": "autonomous", "threshold": "standard", "escalate_on": "proc.exec"})
        self.assertEqual(resolve_approval_threshold(harness, interactive=True), "high")

    def test_an_unknown_verb_in_escalate_on_is_ignored(self) -> None:
        harness = _Harness.declaring(
            {"mode": "autonomous", "threshold": "standard", "escalate_on": ["nope", 7]})
        self.assertEqual(resolve_approval_threshold(harness, interactive=True), "high")


class TestTheLiteralIsGone(unittest.TestCase):
    def test_no_hardcoded_low_threshold_remains_in_session(self) -> None:
        """T-70 acceptance: the literal approval threshold is absent."""
        source = inspect.getsource(session_module)
        self.assertNotIn('"low"', source)
        self.assertNotIn("'low'", source)


if __name__ == "__main__":
    unittest.main()
