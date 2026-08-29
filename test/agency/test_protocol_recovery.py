"""Tests for bounded protocol recovery and tool policy."""

from __future__ import annotations

import unittest

from vanguard.packages.agency.episode.protocol_recovery import (
    ProtocolRecoveryState,
    RecoveryDecision,
    recover_proposal,
)
from vanguard.packages.agency.episode.state import ProposalKind
from vanguard.packages.agency.episode.tool_policy import resolve_tool_policy


class TestProtocolRecovery(unittest.TestCase):
    def setUp(self) -> None:
        self.state = ProtocolRecoveryState()

    def test_valid_proposal_accepted(self) -> None:
        raw = {"kind": "effect", "action": "fs.read", "args": {"path": "a.txt"}}
        decision, next_state = recover_proposal(raw, self.state, allowed_tools=("fs.read",))
        self.assertEqual(decision.status, "accept")
        self.assertIsNotNone(decision.proposal)
        self.assertEqual(decision.proposal.action, "fs.read")

    def test_dsml_recovery(self) -> None:
        raw_dsml = '<invoke name="fs.read"><parameter name="path">"b.txt"</parameter></invoke>'
        decision, next_state = recover_proposal(raw_dsml, self.state, allowed_tools=("fs.read",))
        self.assertEqual(decision.status, "accept")
        self.assertIsNotNone(decision.proposal)
        self.assertEqual(decision.proposal.action, "fs.read")

    def test_markdown_patch_retry_directive(self) -> None:
        raw_diff = "```diff\n--- a/f.py\n+++ b/f.py\n@@ -1 +1 @@\n-1\n+2\n```"
        decision, next_state = recover_proposal(raw_diff, self.state, allowed_tools=("patch.apply",))
        self.assertEqual(decision.status, "retry_model")
        self.assertEqual(decision.retry_reason, "PATCH_EMITTED_AS_TEXT")
        self.assertEqual(decision.retry_feedback.get("required_tool"), "patch.apply")
        self.assertEqual(next_state.protocol_retries, 1)

    def test_truncation_continuation(self) -> None:
        raw_trunc = {"finish_reason": "length", "content": '{"action": "fs.read", "args": {"p'}
        decision, next_state = recover_proposal(raw_trunc, self.state)
        self.assertEqual(decision.status, "retry_model")
        self.assertEqual(decision.retry_reason, "OUTPUT_TRUNCATED")
        self.assertTrue(decision.continuation)
        self.assertEqual(next_state.truncation_retries, 1)

    def test_disallowed_tool_retry(self) -> None:
        raw = {"kind": "effect", "action": "disallowed.tool", "args": {}}
        decision, next_state = recover_proposal(raw, self.state, allowed_tools=("fs.read",))
        self.assertEqual(decision.status, "retry_model")
        self.assertEqual(decision.retry_reason, "DISALLOWED_TOOL")

    def test_tool_policy_resolution(self) -> None:
        p_inspect = resolve_tool_policy("inspect")
        self.assertEqual(p_inspect.mode, "required")
        self.assertIn("fs.read", p_inspect.allowed)

        p_edit = resolve_tool_policy("edit")
        self.assertIn("patch.apply", p_edit.allowed)

        p_verified = resolve_tool_policy("verify", verification_passed=True)
        self.assertEqual(p_verified.mode, "auto")


if __name__ == "__main__":
    unittest.main()
