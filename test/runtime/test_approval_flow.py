"""REQ-APP-001 / MF-GOV-001 descriptor-bound approval tests."""

from __future__ import annotations

import unittest

from test.kernel import fakes
from test.runtime.test_process_engine import event
from vanguard.packages.kernel import (
    FailurePath,
    Scope,
    StandardPolicy,
)
from vanguard.packages.runtime.governance.approvals import (
    ApprovalAuthority,
    ApprovalFlow,
    DescriptorBoundApprovalPolicy,
    OperatorSigner,
)


DIFF = """diff --git a/src/a.py b/src/a.py
--- a/src/a.py
+++ b/src/a.py
@@ -1 +1 @@
-return False
+return True
"""

TAMPERED_DIFF = DIFF.replace("return True", "return privileged_value")


class DescriptorBoundApprovalFlowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.signer = OperatorSigner(b"operator-held-test-key")
        self.authority = ApprovalAuthority(self.signer.public_bytes)
        self.flow = ApprovalFlow(self.authority)
        self.parent_scope = Scope(
            actions=frozenset({"fs.patch"}),
            resources=(fakes.WORKSPACE,),
            constraints=fakes.constraints(),
        )
        self.requested_scope = Scope(
            actions=frozenset({"fs.patch"}),
            resources=(
                {
                    "kind": "fs",
                    "root": "/workspace",
                    "paths": ["/workspace/src/a.ts"],
                },
            ),
            constraints=fakes.constraints(),
            depth=1,
        )
        self.request = fakes.request(action="fs.patch", args={"diff": DIFF})

    def _base_policy(self) -> StandardPolicy:
        return StandardPolicy(
            parent_scope=self.parent_scope,
            approval_required_above="low",
            risk_of={"fs.patch": "critical"},
        )

    def _initial_suspension(self):
        harness = fakes.build(
            adapter=fakes.FakeAdapter("fs.patch"),
            policy=self._base_policy(),
            held_actions=frozenset({"fs.patch"}),
            scope=self.parent_scope,
        )
        result = harness.kernel.dispatch(
            self.request,
            requested_scope=self.requested_scope,
            reservation=fakes.reservation(),
        )
        self.assertIs(result.failure, FailurePath.APPROVAL_SUSPENDED)
        self.assertIsNotNone(result.suspension)
        return result.suspension

    def test_tampered_diff_fails_before_effect_execution(self) -> None:
        suspension = self._initial_suspension()
        challenge = self.flow.request(
            self.request,
            suspension,
            process_id="approval-process-1",
            expires_at="2026-08-15T10:00:00.000Z",
        )
        signed = self.signer.approve(challenge, reviewer="human-lead")
        tampered = fakes.request(action="fs.patch", args={"diff": TAMPERED_DIFF})
        authorization = self.flow.verify(
            challenge,
            signed,
            tampered,
            now="2026-08-15T09:30:00.000Z",
        )
        policy = DescriptorBoundApprovalPolicy(self._base_policy(), authorization)
        harness = fakes.build(
            adapter=fakes.FakeAdapter("fs.patch"),
            policy=policy,
            held_actions=frozenset({"fs.patch"}),
            scope=self.parent_scope,
        )

        result = harness.kernel.dispatch(
            tampered,
            requested_scope=self.requested_scope,
            reservation=fakes.reservation(),
        )

        self.assertIs(result.failure, FailurePath.DENIED_REJECT)
        self.assertEqual(harness.adapter.calls, [])
        self.assertNotIn("reserve", harness.trace)

    def test_signed_exact_diff_reenters_s1_and_reaches_s9(self) -> None:
        suspension = self._initial_suspension()
        challenge = self.flow.request(
            self.request,
            suspension,
            process_id="approval-process-1",
            expires_at="2026-08-15T10:00:00.000Z",
        )
        signed = self.signer.approve(challenge, reviewer="human-lead")
        requested_event = event(
            1, "ApprovalRequested", **challenge.payload()
        )
        resolved_event = event(
            2, "ApprovalResolved", processId=challenge.process_id, **signed.payload()
        )
        authorization = self.flow.verify_from_ledger(
            [requested_event, resolved_event],
            self.request,
            suspension,
            process_id=challenge.process_id,
            now="2026-08-15T09:30:00.000Z",
        )
        policy = DescriptorBoundApprovalPolicy(self._base_policy(), authorization)
        harness = fakes.build(
            adapter=fakes.FakeAdapter("fs.patch"),
            policy=policy,
            held_actions=frozenset({"fs.patch"}),
            scope=self.parent_scope,
        )

        result = harness.kernel.dispatch(
            self.request,
            requested_scope=self.requested_scope,
            reservation=fakes.reservation(),
        )

        self.assertTrue(result.ok)
        self.assertEqual(harness.adapter.calls, [self.request])
        self.assertEqual(result.events[0].kind, "EffectStarted")

    def test_expired_or_forged_decision_fails_closed(self) -> None:
        suspension = self._initial_suspension()
        challenge = self.flow.request(
            self.request,
            suspension,
            process_id="approval-process-1",
            expires_at="2026-08-15T10:00:00.000Z",
        )
        signed = self.signer.approve(challenge, reviewer="human-lead")

        expired = self.flow.verify(
            challenge,
            signed,
            self.request,
            now="2026-08-15T10:00:00.000Z",
        )
        forged = self.flow.verify(
            challenge,
            signed.__class__(
                approval_id=signed.approval_id,
                resolution=signed.resolution,
                reviewer="attacker",
                args_digest=signed.args_digest,
                descriptor_digest=signed.descriptor_digest,
                expires_at=signed.expires_at,
                signature=signed.signature,
            ),
            self.request,
            now="2026-08-15T09:30:00.000Z",
        )

        self.assertFalse(expired.approved)
        self.assertEqual(expired.reason, "approval_expired")
        self.assertFalse(forged.approved)
        self.assertEqual(forged.reason, "signature_invalid")


if __name__ == "__main__":
    unittest.main()
