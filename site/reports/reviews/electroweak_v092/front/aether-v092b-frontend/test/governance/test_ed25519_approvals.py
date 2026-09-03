"""Test Ed25519 asymmetric descriptor-bound approval authority and flow."""

from __future__ import annotations

import unittest
from pathlib import Path

from vanguard.packages.domain.primitives.primitives import uuidv7
from vanguard.packages.kernel import (
    Constraints,
    Decision,
    EffectRequest,
    FailurePath,
    Outcome,
    SinkClass,
    StandardPolicy,
    SuspensionToken,
    descriptor_of,
)
from vanguard.packages.runtime.governance.approvals import (
    ApprovalAuthority,
    ApprovalChallenge,
    ApprovalDecision,
    ApprovalFlow,
    ApprovalFormatError,
    DescriptorBoundApprovalPolicy,
    OperatorSigner,
    normalise_unified_diff,
)


class TestEd25519Approvals(unittest.TestCase):
    def setUp(self) -> None:
        self.signer = OperatorSigner(key_id="op-1")
        self.authority = ApprovalAuthority({"op-1": self.signer.public_bytes})
        self.flow = ApprovalFlow(self.authority, patch_verb="patch.apply")
        self.diff = "--- a/foo.py\n+++ b/foo.py\n@@ -1 +1 @@\n-old\n+new\n"
        self.args = {"diff": self.diff, "path": "foo.py"}
        self.request = EffectRequest(
            action="patch.apply",
            resource={"kind": "fs", "path": "foo.py"},
            args=self.args,
            principal="agent-1",
            run_id="run-1",
            declared_sink_class=SinkClass.PRIVILEGED,
        )
        self.desc_digest = descriptor_of("patch.apply", self.args)
        self.suspension = SuspensionToken(
            token_id=uuidv7(),
            descriptor_digest=self.desc_digest,
            principal="agent-1",
            expires_at="2026-08-16T01:00:00.000Z",
        )

    def test_signer_approve_and_authority_verify_success(self) -> None:
        challenge = self.flow.request(
            self.request,
            self.suspension,
            process_id="proc-1",
            expires_at="2026-08-16T01:00:00.000Z",
        )
        decision = self.signer.approve(challenge, reviewer="alice")
        self.assertEqual(decision.resolution, "approved")
        self.assertEqual(decision.reviewer, "alice")
        self.assertEqual(decision.key_id, "op-1")
        self.assertTrue(self.authority.verify(decision))

        auth = self.flow.verify(
            challenge,
            decision,
            self.request,
            now="2026-08-16T00:30:00.000Z",
        )
        self.assertTrue(auth.approved)
        self.assertEqual(auth.reason, "approved")

    def test_forged_signature_fails_closed(self) -> None:
        challenge = self.flow.request(
            self.request,
            self.suspension,
            process_id="proc-1",
            expires_at="2026-08-16T01:00:00.000Z",
        )
        decision = self.signer.approve(challenge, reviewer="alice")
        # Tamper signature
        tampered_sig = "0" * 128
        tampered_decision = ApprovalDecision(
            approval_id=decision.approval_id,
            resolution=decision.resolution,
            reviewer=decision.reviewer,
            args_digest=decision.args_digest,
            descriptor_digest=decision.descriptor_digest,
            expires_at=decision.expires_at,
            key_id=decision.key_id,
            signature=tampered_sig,
        )
        self.assertFalse(self.authority.verify(tampered_decision))
        auth = self.flow.verify(
            challenge,
            tampered_decision,
            self.request,
            now="2026-08-16T00:30:00.000Z",
        )
        self.assertFalse(auth.approved)
        self.assertEqual(auth.reason, "signature_invalid")

    def test_expired_approval_fails_closed(self) -> None:
        challenge = self.flow.request(
            self.request,
            self.suspension,
            process_id="proc-1",
            expires_at="2026-08-16T01:00:00.000Z",
        )
        decision = self.signer.approve(challenge, reviewer="alice")
        # now is after expiry
        auth = self.flow.verify(
            challenge,
            decision,
            self.request,
            now="2026-08-16T01:30:00.000Z",
        )
        self.assertFalse(auth.approved)
        self.assertEqual(auth.reason, "approval_expired")

    def test_unknown_key_id_fails_closed(self) -> None:
        challenge = self.flow.request(
            self.request,
            self.suspension,
            process_id="proc-1",
            expires_at="2026-08-16T01:00:00.000Z",
        )
        other_signer = OperatorSigner(key_id="op-untrusted")
        decision = other_signer.approve(challenge, reviewer="alice")
        self.assertFalse(self.authority.verify(decision))

    def test_diff_normalization_and_tampered_diff(self) -> None:
        norm = normalise_unified_diff("--- a/f\n+++ b/f\n@@ -1 +1 @@\n-1\n+2\r\n")
        self.assertTrue(norm.endswith("\n"))
        self.assertNotIn("\r", norm)

        with self.assertRaises(ApprovalFormatError):
            normalise_unified_diff("plain text without patch headers")


if __name__ == "__main__":
    unittest.main()
