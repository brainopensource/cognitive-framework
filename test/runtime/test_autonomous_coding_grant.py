"""Tests for bounded autonomous coding grants (REQ-TRUST-001, K-17, S32)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.runtime.autonomous_grant import (
    create_autonomous_grant,
    validate_grant_request,
)


class TestAutonomousCodingGrant(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name)

    def test_create_signed_autonomous_grant(self) -> None:
        grant = create_autonomous_grant(
            self.workspace,
            allowed_verbs=("fs.read", "patch.apply", "proc.exec"),
            command_allowlist=("git", "pytest", "python3"),
            max_turns=20,
            max_budget_micros=100_000,
        )
        self.assertTrue(grant.grant_id.startswith("grant-"))
        self.assertTrue(len(grant.signature) > 0)
        self.assertEqual(grant.workspace_root, self.workspace.resolve().as_posix())

    def test_validate_allowed_and_disallowed_requests(self) -> None:
        grant = create_autonomous_grant(
            self.workspace,
            allowed_verbs=("fs.read", "patch.apply", "proc.exec"),
            command_allowlist=("git", "pytest", "python3"),
            max_turns=10,
            max_budget_micros=50_000,
        )

        # 1. Valid read request within workspace
        ok, reason = validate_grant_request(
            grant,
            verb="fs.read",
            target_path=self.workspace / "app.py",
            turn=1,
            spent_micros=0,
        )
        self.assertTrue(ok)

        # 2. Denied verb (not in allowed list)
        ok, reason = validate_grant_request(
            grant,
            verb="fs.delete",
            target_path=self.workspace / "app.py",
        )
        self.assertFalse(ok)
        self.assertTrue(reason.startswith("verb_denied"))

        # 3. Path escape denied
        outside_path = Path("/etc/passwd")
        ok, reason = validate_grant_request(
            grant,
            verb="fs.read",
            target_path=outside_path,
        )
        self.assertFalse(ok)
        self.assertTrue(reason.startswith("workspace_path_escape_denied"))

        # 4. Disallowed command binary
        ok, reason = validate_grant_request(
            grant,
            verb="proc.exec",
            command_argv=["curl", "https://example.com"],
        )
        self.assertFalse(ok)
        self.assertTrue(reason.startswith("command_disallowed"))

        # 5. Exceeded turn limit
        ok, reason = validate_grant_request(
            grant,
            verb="fs.read",
            turn=15,
        )
        self.assertFalse(ok)
        self.assertTrue(reason.startswith("turn_limit_exceeded"))

        # 6. Exceeded budget ceiling
        ok, reason = validate_grant_request(
            grant,
            verb="fs.read",
            spent_micros=60_000,
        )
        self.assertFalse(ok)
        self.assertTrue(reason.startswith("budget_ceiling_exceeded"))


if __name__ == "__main__":
    unittest.main()
