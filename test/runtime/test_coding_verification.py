"""Tests for exterior step and final verification (REQ-TRUST-001, S32)."""

from __future__ import annotations

import unittest
from typing import Any

from vanguard.packages.ports.environment import EnvironmentProfile
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.coding_verification import (
    FinalVerifier,
    StepVerifier,
)


class _MockReceipt:
    def __init__(self, outcome: str = "ok", stdout: bytes = b"", stderr: bytes = b"") -> None:
        self.outcome = outcome
        self.stdout = stdout
        self.stderr = stderr
        self.descriptor_digest = "sha256:desc"
        self.result_digest = "sha256:res"
        self.observed_at = "2026-08-17T00:00:00.000Z"


class _MockEnvironment:
    def __init__(self, outcome: str = "ok", stdout: bytes = b"", stderr: bytes = b"") -> None:
        self.outcome = outcome
        self.stdout = stdout
        self.stderr = stderr
        self.applied_requests: list[Any] = []

    def profile(self) -> Result[Any]:
        return Result.success(EnvironmentProfile(
            environment_id="fake:/workspace", kind="memory", root="/workspace"))

    def apply(self, req: Any, grant: Any = None) -> Result[Any]:
        self.applied_requests.append(req)
        return Result.success(_MockReceipt(self.outcome, self.stdout, self.stderr))


class TestCodingVerification(unittest.TestCase):
    def test_step_verifier_passes_on_ok_outcome(self) -> None:
        env = _MockEnvironment(outcome="ok", stdout=b"OK (ran 3 tests)")
        verifier = StepVerifier(env)
        receipt = verifier.verify_step("step-1", ["python3", "-m", "unittest"])

        self.assertTrue(receipt.passed)
        self.assertEqual(receipt.exit_code, 0)
        self.assertEqual(len(env.applied_requests), 1)

    def test_step_verifier_fails_on_nonzero_outcome(self) -> None:
        env = _MockEnvironment(outcome="failed", stderr=b"FAIL: test_feature (test_app.TestApp)")
        verifier = StepVerifier(env)
        receipt = verifier.verify_step("step-1", ["python3", "-m", "unittest"])

        self.assertFalse(receipt.passed)
        self.assertEqual(receipt.exit_code, 1)
        self.assertIn("test_feature", receipt.failed_test_ids)

    def test_final_verifier_oracle_green(self) -> None:
        env = _MockEnvironment(outcome="ok")
        verifier = FinalVerifier(env)
        receipt = verifier.verify_final("task-01", ["python3", "-m", "unittest", "discover"])

        self.assertTrue(receipt.passed)
        self.assertTrue(receipt.oracle_green)
        self.assertEqual(receipt.behavioral_checks_passed, 1)

    def test_final_verifier_non_green_on_failure(self) -> None:
        env = _MockEnvironment(outcome="failed")
        verifier = FinalVerifier(env)
        receipt = verifier.verify_final("task-01", ["python3", "-m", "unittest", "discover"])

        self.assertFalse(receipt.passed)
        self.assertFalse(receipt.oracle_green)
        self.assertEqual(receipt.behavioral_checks_passed, 0)

    def test_verifier_fails_closed_when_env_unavailable(self) -> None:
        verifier = StepVerifier(None)
        receipt = verifier.verify_step("step-1", ["python3", "test.py"])
        self.assertFalse(receipt.passed)

        final_ver = FinalVerifier(None)
        final_receipt = final_ver.verify_final("task-01", ["python3", "test.py"])
        self.assertFalse(final_receipt.oracle_green)


if __name__ == "__main__":
    unittest.main()
