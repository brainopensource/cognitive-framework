"""CMX-04 falsifiers for multi-file and greenfield completion closure."""

from __future__ import annotations

import inspect
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "packs" / "code-default"
if str(PACK) not in sys.path:
    sys.path.insert(0, str(PACK))

from middleware.repository.greenfield import GreenfieldPolicy, assess_greenfield_workspace
from vanguard.packages.agency.episode.admission_gate import AdmissionGate, VerificationReceipt
from vanguard.packages.runtime.session import HarnessSession

from middleware.repository.multi_file_completeness import check_multi_file_completeness


class TestCMX04ChangeSurfaceClosure(unittest.TestCase):
    def test_interface_change_cannot_complete_after_patching_one_file(self) -> None:
        report = check_multi_file_completeness(
            ["api.py", "consumer.py"], ["api.py"], ["api.py"],
            changed_public_symbols=["Api"], callers_by_symbol={"Api": ["consumer.py"]},
        )
        self.assertFalse(report.is_complete)
        self.assertIn("IMPLICATED_FILES_NOT_INSPECTED:1", report.rejections)

    def test_direct_pass_with_affected_regression_failure_is_closed(self) -> None:
        from middleware.repository.multi_file_completeness import CodeDefaultCompletionPolicy

        verdict = CodeDefaultCompletionPolicy().evaluate(
            "vg-code-balanced", ["api.py"], {"kind": "finish"},
            inspected_files=["api.py"],
            verification=VerificationReceipt(0, 1, "sha256:workspace"),
            current_workspace_digest="sha256:workspace",
            task_text="fix api.py", regression_evidence={
                "direct_passed": True, "regression_passed": False,
            },
        )
        self.assertFalse(verdict["admissible"])
        self.assertEqual(verdict["reason"], "AFFECTED_REGRESSION_FAILED")

    def test_post_verification_patch_is_stale(self) -> None:
        gate = AdmissionGate()
        verdict = gate.evaluate(
            "vg-code-balanced", ["api.py"], {"kind": "finish"},
            inspected_files=["api.py"],
            verification=VerificationReceipt(0, 1, "sha256:before"),
            current_workspace_digest="sha256:after",
        )
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, "VERIFICATION_STALE")

    def test_greenfield_requires_smoke_behavior_and_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            policy = GreenfieldPolicy(directory)
            baseline = policy.record_scaffold_baseline()
            syntax_only = policy.evaluate(
                structural_passed=True, behavioral_passed=False,
                smoke_test_created=False, created_files=["app.py"], baseline=baseline,
            )
            self.assertFalse(syntax_only.admissible)
            admitted = policy.evaluate(
                structural_passed=True, behavioral_passed=True,
                smoke_test_created=True,
                created_files=["app.py", "test_app.py"], baseline=baseline,
            )
            self.assertTrue(admitted.admissible)

    def test_path_and_symlink_escapes_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            link = Path(directory) / "src"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            assessment = assess_greenfield_workspace(directory)
            self.assertFalse(assessment.effectively_empty)
            self.assertEqual(assessment.escaped_entries, ("src",))

    def test_session_has_no_hardcoded_requirements_pass(self) -> None:
        source = inspect.getsource(HarnessSession)
        self.assertNotIn("task_requirements_satisfied=True", source)


if __name__ == "__main__":
    unittest.main()
