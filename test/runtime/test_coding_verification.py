"""T-42 adversarial coding verification and T-38 bugfix fail-to-pass."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "packs" / "code-default"
if str(PACK) not in sys.path:
    sys.path.insert(0, str(PACK))

from middleware.repository.multi_file_completeness import CodeDefaultCompletionPolicy
from vanguard.packages.agency.chimera.verification import VerificationCortex
from vanguard.packages.agency.episode.admission_gate import AdmissionGate, VerificationReceipt
from vanguard.packages.agency.forge.engine import parse_test_output


def _policy() -> CodeDefaultCompletionPolicy:
    return CodeDefaultCompletionPolicy()


def _passing_receipt(**overrides: object) -> VerificationReceipt:
    values = {
        "exit_code": 0,
        "executed_test_count": 3,
        "workspace_digest": "sha256:ws",
        "task_digest": "sha256:task",
        "composition_digest": "sha256:comp",
        "verification_command": "python3 -m unittest discover -s test -t .",
    }
    values.update(overrides)
    return VerificationReceipt(**values)  # type: ignore[arg-type]


def _admit_kwargs(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "preset_name": "vg-code-max",
        "changed_files": ["src/cache.py"],
        "proposal": {"kind": "finish"},
        "inspected_files": ["src/cache.py"],
        "implicated_files": ["src/cache.py"],
        "verification": _passing_receipt(),
        "current_workspace_digest": "sha256:ws",
        "task_text": "fix the broken cache eviction bug",
        "pre_verify": {"exit_code": 1, "executed_test_count": 3, "passed": False},
        "task_test_ids": ("test_cache.py::test_evict",),
        "executed_test_ids": ("test_cache.py::test_evict",),
    }
    values.update(overrides)
    return values


class TestAdversarialCodingVerificationT42(unittest.TestCase):
    def test_true_cannot_admit(self) -> None:
        chimera = VerificationCortex.parse_test_output("", exit_code=0)
        forge_count, _, _, _ = parse_test_output("", exit_code=0)
        self.assertEqual(chimera.executed_tests, 0)
        self.assertEqual(forge_count, 0)
        receipt = VerificationReceipt(
            exit_code=0,
            executed_test_count=chimera.executed_tests,
            workspace_digest="sha256:ws",
            verification_command="true",
        )
        self.assertFalse(receipt.passed)
        gate = AdmissionGate()
        verdict = gate.evaluate(
            "vg-code-max",
            ["src/cache.py"],
            {"kind": "finish"},
            inspected_files=["src/cache.py"],
            verification=receipt,
            current_workspace_digest="sha256:ws",
        )
        self.assertFalse(verdict.admissible)
        policy = _policy().evaluate(
            **_admit_kwargs(  # type: ignore[arg-type]
                verification=receipt,
                task_text="document the cache",
                pre_verify=None,
            )
        )
        self.assertFalse(policy["admissible"])

    def test_echo_ten_tests_passed_cannot_admit(self) -> None:
        spoof = "10 tests passed\n"
        chimera = VerificationCortex.parse_test_output(spoof, exit_code=0)
        forge_count, _, _, _ = parse_test_output(spoof, exit_code=0)
        self.assertEqual(chimera.executed_tests, 0)
        self.assertEqual(forge_count, 0)
        receipt = VerificationReceipt(
            exit_code=0,
            executed_test_count=10,
            workspace_digest="sha256:ws",
            verification_command="echo 10 tests passed",
        )
        policy = _policy().evaluate(**_admit_kwargs(verification=receipt))  # type: ignore[arg-type]
        self.assertFalse(policy["admissible"])
        self.assertEqual(policy["reason"], "VACUOUS_VERIFICATION_COMMAND")

    def test_unrelated_suite_cannot_satisfy_task_relevance(self) -> None:
        policy = _policy().evaluate(
            **_admit_kwargs(executed_test_ids=("test_unrelated.py::test_ok",))  # type: ignore[arg-type]
        )
        self.assertFalse(policy["admissible"])
        self.assertEqual(policy["reason"], "UNRELATED_SUITE")

    def test_stale_verification_after_write_is_rejected(self) -> None:
        gate = AdmissionGate()
        verdict = gate.evaluate(
            "vg-code-max",
            ["src/cache.py"],
            {"kind": "finish"},
            inspected_files=["src/cache.py"],
            verification=_passing_receipt(),
            current_workspace_digest="sha256:after-write",
        )
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, "VERIFICATION_STALE")

    def test_foreign_task_and_composition_digests_are_rejected(self) -> None:
        gate = AdmissionGate()
        foreign_task = gate.evaluate(
            "vg-code-max",
            ["src/cache.py"],
            {"kind": "finish"},
            inspected_files=["src/cache.py"],
            verification=_passing_receipt(),
            current_workspace_digest="sha256:ws",
            current_task_digest="sha256:other-task",
        )
        self.assertFalse(foreign_task.admissible)
        self.assertEqual(foreign_task.reason, "VERIFICATION_FOREIGN_TASK")
        foreign_comp = gate.evaluate(
            "vg-code-max",
            ["src/cache.py"],
            {"kind": "finish"},
            inspected_files=["src/cache.py"],
            verification=_passing_receipt(),
            current_workspace_digest="sha256:ws",
            current_composition_digest="sha256:other-comp",
        )
        self.assertFalse(foreign_comp.admissible)
        self.assertEqual(foreign_comp.reason, "VERIFICATION_FOREIGN_COMPOSITION")


class TestFailToPassT38(unittest.TestCase):
    def test_bugfix_requires_failing_pre_verify_and_passing_post_verify(self) -> None:
        admitted = _policy().evaluate(**_admit_kwargs())  # type: ignore[arg-type]
        self.assertTrue(admitted["admissible"])

        missing = _policy().evaluate(**_admit_kwargs(pre_verify=None))  # type: ignore[arg-type]
        self.assertFalse(missing["admissible"])
        self.assertEqual(missing["reason"], "FAIL_TO_PASS_REQUIRED")

        vacuous = _policy().evaluate(
            **_admit_kwargs(pre_verify={"exit_code": 0, "executed_test_count": 3, "passed": True})  # type: ignore[arg-type]
        )
        self.assertFalse(vacuous["admissible"])
        self.assertEqual(vacuous["reason"], "VACUOUS_REPRODUCER")

        post_failed = _policy().evaluate(
            **_admit_kwargs(verification=_passing_receipt(exit_code=1))  # type: ignore[arg-type]
        )
        self.assertFalse(post_failed["admissible"])
        self.assertEqual(post_failed["reason"], "VERIFICATION_FAILED")

    def test_explanation_class_is_not_bound_to_fail_to_pass(self) -> None:
        verdict = _policy().evaluate(
            **_admit_kwargs(  # type: ignore[arg-type]
                task_text="explain the cache eviction algorithm",
                pre_verify=None,
            )
        )
        self.assertTrue(verdict["admissible"])


class TestChimeraNonZeroCountHonesty(unittest.TestCase):
    def test_nonzero_exit_without_runner_summary_does_not_invent_executed(self) -> None:
        record = VerificationCortex.parse_test_output("", exit_code=1)
        self.assertEqual(record.executed_tests, 0)
        self.assertEqual(record.passed_tests, 0)
        self.assertFalse(
            VerificationReceipt(1, record.executed_tests, "sha256:ws").passed
        )


if __name__ == "__main__":
    unittest.main()
