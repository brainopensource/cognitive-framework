"""Exterior step and final behavioral verification (REQ-TRUST-001, S32).

Enforces that neither step completion nor final oracle_green can be declared
by the model or an agent-requested proc.exec effect. Verification commands originate
from the validated plan or task manifest and execute strictly exterior to episodes.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Sequence

from ..ports.environment import EffectRequest as EnvironmentRequest
from ..ports.event_store import Result

__all__ = [
    "FinalVerificationReceipt",
    "FinalVerifier",
    "StepVerificationReceipt",
    "StepVerifier",
    "digest_bytes",
]


def digest_bytes(data: bytes | str) -> str:
    raw = data.encode("utf-8") if isinstance(data, str) else data
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


@dataclass(frozen=True, slots=True)
class StepVerificationReceipt:
    """Attributable receipt from an exterior step verification run."""

    step_id: str
    argv: tuple[str, ...]
    exit_code: int
    passed: bool
    stdout_digest: str
    stderr_digest: str
    failed_test_ids: tuple[str, ...]
    timestamp: str
    receipt_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "stepId": self.step_id,
            "argv": list(self.argv),
            "exitCode": self.exit_code,
            "passed": self.passed,
            "stdoutDigest": self.stdout_digest,
            "stderrDigest": self.stderr_digest,
            "failedTestIds": list(self.failed_test_ids),
            "timestamp": self.timestamp,
            "receiptDigest": self.receipt_digest,
        }


@dataclass(frozen=True, slots=True)
class FinalVerificationReceipt:
    """Attributable receipt from the final exterior behavioral oracle."""

    task_id: str
    argv: tuple[str, ...]
    exit_code: int
    passed: bool
    oracle_green: bool
    behavioral_checks_passed: int
    behavioral_checks_total: int
    timestamp: str
    receipt_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "taskId": self.task_id,
            "argv": list(self.argv),
            "exitCode": self.exit_code,
            "passed": self.passed,
            "oracleGreen": self.oracle_green,
            "behavioralChecksPassed": self.behavioral_checks_passed,
            "behavioralChecksTotal": self.behavioral_checks_total,
            "timestamp": self.timestamp,
            "receiptDigest": self.receipt_digest,
        }


class StepVerifier:
    """Exterior verifier for plan steps."""

    def __init__(self, environment: Any) -> None:
        self.environment = environment

    def verify_step(
        self,
        step_id: str,
        argv: Sequence[str],
    ) -> StepVerificationReceipt:
        """Run step verification command in the sandbox environment."""
        if not self.environment:
            return self._fail_receipt(step_id, argv, "environment_unavailable")

        command_list = list(argv)
        req = EnvironmentRequest(
            verb="proc.exec",
            action="exec",
            args={"argv": command_list},
            command=command_list,
        )
        result = self.environment.apply(req)
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        if not result.ok or result.value is None:
            return self._fail_receipt(step_id, argv, "environment_execution_failed")

        outcome = getattr(result.value, "outcome", "")
        # Bubblewrap worker sets outcome="ok" on exit 0, outcome="failed" on non-zero
        passed = (outcome == "ok")
        exit_code = 0 if passed else 1

        # Extract digests if available
        stdout_raw = getattr(result.value, "stdout", b"")
        stderr_raw = getattr(result.value, "stderr", b"")
        stdout_digest = digest_bytes(stdout_raw)
        stderr_digest = digest_bytes(stderr_raw)

        # Parse test failure IDs if non-zero
        failed_ids: list[str] = []
        if not passed and (stdout_raw or stderr_raw):
            import re
            text = f"{stdout_raw}\n{stderr_raw}"
            for m in re.finditer(r"(?:FAIL|FAILED)[:\s]+([\w\.\:\-\_]+)", text):
                failed_ids.append(m.group(1))

        payload = {
            "stepId": step_id,
            "argv": command_list,
            "exitCode": exit_code,
            "passed": passed,
            "stdoutDigest": stdout_digest,
            "stderrDigest": stderr_digest,
            "timestamp": timestamp,
        }
        receipt_digest = digest_bytes(json.dumps(payload, sort_keys=True))

        return StepVerificationReceipt(
            step_id=step_id,
            argv=tuple(command_list),
            exit_code=exit_code,
            passed=passed,
            stdout_digest=stdout_digest,
            stderr_digest=stderr_digest,
            failed_test_ids=tuple(sorted(failed_ids)),
            timestamp=timestamp,
            receipt_digest=receipt_digest,
        )

    def _fail_receipt(self, step_id: str, argv: Sequence[str], reason: str) -> StepVerificationReceipt:
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return StepVerificationReceipt(
            step_id=step_id,
            argv=tuple(argv),
            exit_code=1,
            passed=False,
            stdout_digest=digest_bytes(""),
            stderr_digest=digest_bytes(reason),
            failed_test_ids=(),
            timestamp=ts,
            receipt_digest=digest_bytes(f"fail:{step_id}:{reason}"),
        )


class FinalVerifier:
    """Exterior behavioral oracle for final task acceptance."""

    def __init__(self, environment: Any) -> None:
        self.environment = environment

    def verify_final(
        self,
        task_id: str,
        argv: Sequence[str],
        expected_checks: int = 1,
    ) -> FinalVerificationReceipt:
        """Run the final declared verification command in the sandbox environment."""
        if not self.environment:
            return self._fail_final(task_id, argv, "environment_unavailable")

        command_list = list(argv)
        req = EnvironmentRequest(
            verb="proc.exec",
            action="exec",
            args={"argv": command_list},
            command=command_list,
        )
        result = self.environment.apply(req)
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        if not result.ok or result.value is None:
            return self._fail_final(task_id, argv, "oracle_execution_failed")

        outcome = getattr(result.value, "outcome", "")
        passed = (outcome == "ok")
        exit_code = 0 if passed else 1
        oracle_green = passed

        checks_passed = expected_checks if passed else 0

        payload = {
            "taskId": task_id,
            "argv": command_list,
            "exitCode": exit_code,
            "oracleGreen": oracle_green,
            "timestamp": timestamp,
        }
        receipt_digest = digest_bytes(json.dumps(payload, sort_keys=True))

        return FinalVerificationReceipt(
            task_id=task_id,
            argv=tuple(command_list),
            exit_code=exit_code,
            passed=passed,
            oracle_green=oracle_green,
            behavioral_checks_passed=checks_passed,
            behavioral_checks_total=expected_checks,
            timestamp=timestamp,
            receipt_digest=receipt_digest,
        )

    def _fail_final(self, task_id: str, argv: Sequence[str], reason: str) -> FinalVerificationReceipt:
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return FinalVerificationReceipt(
            task_id=task_id,
            argv=tuple(argv),
            exit_code=1,
            passed=False,
            oracle_green=False,
            behavioral_checks_passed=0,
            behavioral_checks_total=1,
            timestamp=ts,
            receipt_digest=digest_bytes(f"fail:{task_id}:{reason}"),
        )
