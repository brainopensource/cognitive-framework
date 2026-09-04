"""T-19: greenfield tests that pass on stubs are vacuous and cannot admit."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "code-default"
if str(PACK) not in sys.path:
    sys.path.insert(0, str(PACK))

from middleware.repository.greenfield import GreenfieldPolicy
from middleware.repository.multi_file_completeness import CodeDefaultCompletionPolicy
from vanguard.packages.agency.episode.admission_gate import VerificationReceipt

_STUB = "def add(a, b):\n    raise NotImplementedError\n"
_IMPL = "def add(a, b):\n    return a + b\n"
_TEST = "from app import add\n\ndef test_add():\n    assert add(1, 1) == 2\n"


class TestGreenfieldOracleVacuity(unittest.TestCase):
    def test_empty_impl_with_green_tests_is_not_admitted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            policy = GreenfieldPolicy(root)
            baseline = policy.record_scaffold_baseline()
            (root / "app.py").write_text(_STUB, encoding="utf-8")
            (root / "test_app.py").write_text(_TEST, encoding="utf-8")
            verdict = policy.evaluate(
                structural_passed=True,
                behavioral_passed=True,
                smoke_test_created=True,
                created_files=["app.py", "test_app.py"],
                baseline=baseline,
            )
            self.assertFalse(verdict.admissible)
            self.assertEqual(verdict.reason, "VACUOUS_ORACLE")

    def test_scaffold_alone_is_not_done(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            policy = GreenfieldPolicy(directory)
            baseline = policy.record_scaffold_baseline()
            verdict = policy.evaluate(
                structural_passed=True,
                behavioral_passed=False,
                smoke_test_created=True,
                created_files=["app.py"],
                baseline=baseline,
                oracle_failed_on_stub=True,
            )
            self.assertFalse(verdict.admissible)
            self.assertNotEqual(verdict.reason, "greenfield_completion_admissible")

    def test_fail_on_stub_then_pass_on_impl_admits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            policy = GreenfieldPolicy(root)
            baseline = policy.record_scaffold_baseline()
            (root / "app.py").write_text(_IMPL, encoding="utf-8")
            (root / "test_app.py").write_text(_TEST, encoding="utf-8")
            verdict = policy.evaluate(
                structural_passed=True,
                behavioral_passed=True,
                smoke_test_created=True,
                created_files=["app.py", "test_app.py"],
                baseline=baseline,
                oracle_failed_on_stub=True,
            )
            self.assertTrue(verdict.admissible)

    def test_completion_policy_rejects_greenfield_without_stub_fail(self) -> None:
        verdict = CodeDefaultCompletionPolicy().evaluate(
            "vg-code-balanced",
            ["app.py", "test_app.py"],
            {"kind": "finish"},
            inspected_files=["app.py", "test_app.py"],
            implicated_files=["app.py", "test_app.py"],
            verification=VerificationReceipt(0, 1, "sha256:workspace"),
            current_workspace_digest="sha256:workspace",
            task_text="greenfield: build add() from scratch",
            greenfield_evidence={
                "baseline_recorded": True,
                "structural_passed": True,
                "smoke_test_created": True,
                "behavioral_passed": True,
                "oracle_failed_on_stub": False,
            },
        )
        self.assertFalse(verdict["admissible"])
        self.assertEqual(verdict["reason"], "VACUOUS_ORACLE")

    def test_completion_policy_admits_fail_on_stub_then_pass_on_impl(self) -> None:
        verdict = CodeDefaultCompletionPolicy().evaluate(
            "vg-code-balanced",
            ["app.py", "test_app.py"],
            {"kind": "finish"},
            inspected_files=["app.py", "test_app.py"],
            implicated_files=["app.py", "test_app.py"],
            verification=VerificationReceipt(0, 1, "sha256:workspace"),
            current_workspace_digest="sha256:workspace",
            task_text="greenfield: build add() from scratch",
            greenfield_evidence={
                "baseline_recorded": True,
                "structural_passed": True,
                "smoke_test_created": True,
                "behavioral_passed": True,
                "oracle_failed_on_stub": True,
            },
        )
        self.assertTrue(verdict["admissible"])


if __name__ == "__main__":
    unittest.main()
