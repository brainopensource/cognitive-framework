"""Unit tests for ProtocolRecoveryPolicy and AdmissionGate."""

import unittest

from vanguard.packages.agency.episode.admission_gate import AdmissionGate, VerificationReceipt
from vanguard.packages.agency.episode.protocol_recovery import ProtocolRecoveryPolicy, RecoveryState


class TestProtocolRecoveryAndAdmissionGate(unittest.TestCase):

    def test_protocol_recovery_patch_required(self) -> None:
        policy = ProtocolRecoveryPolicy()
        state = RecoveryState()

        # Proposal with only conversational text when patch is required
        proposal = {"text": "I analyzed the issue.", "toolCalls": ()}
        decision = policy.evaluate(proposal, state, patch_required=True)

        self.assertEqual(decision.action, "retry_model")
        self.assertEqual(decision.reason, "PATCH_REQUIRED_BUT_TEXT_EMITTED")
        self.assertIn("patch.apply", decision.feedback_message or "")

    def test_admission_gate_write_preset(self) -> None:
        gate = AdmissionGate()

        # Proposal attempting exit without changed files on write preset
        verdict = gate.evaluate("vg-code-v090-react-control", changed_files=(), proposal={"text": "done"})
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, "MISSING_SOURCE_PATCH")

        # Proposal with changed files
        verdict_ok = gate.evaluate(
            "vg-code-v090-react-control", changed_files=("lru/entry.py",), proposal={"text": "done"},
            verification=VerificationReceipt(0, 1, "sha256:workspace"),
            current_workspace_digest="sha256:workspace",
        )
        self.assertTrue(verdict_ok.admissible)

    def test_admission_gate_read_only_preset(self) -> None:
        gate = AdmissionGate()
        verdict = gate.evaluate("vg-tutor-v090-v1-read-search", changed_files=(), proposal={"text": "summary"})
        self.assertTrue(verdict.admissible)


if __name__ == "__main__":
    unittest.main()
