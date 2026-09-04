"""T-20: brownfield implicated-set fail-closed (empty coverage, no greenfield bypass, 2PC callers)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "code-default"
if str(PACK) not in sys.path:
    sys.path.insert(0, str(PACK))

from middleware.repository.multi_file_completeness import (
    CodeDefaultCompletionPolicy,
    check_multi_file_completeness,
)
from vanguard.packages.adapters.environment.transaction import (
    AtomicMultiFileTransactionManager,
    FileMutation,
)
from vanguard.packages.agency.episode.admission_gate import VerificationReceipt
from vanguard.packages.domain.transforms.repository.change_surface import (
    ChangeSurfaceEstimator,
)

_API = "def greet(name):\n    return f'hi {name}'\n"
_API_NEW = "def greet(name, title):\n    return f'hi {title} {name}'\n"
_CONSUMER = "from api import greet\n\ndef run():\n    return greet('ada')\n"
_CONSUMER_NEW = "from api import greet\n\ndef run():\n    return greet('ada', 'ms')\n"


class TestBrownfieldImplicatedSet(unittest.TestCase):
    def test_empty_primary_with_coverage_ratio_one_cannot_admit(self) -> None:
        estimate = ChangeSurfaceEstimator().estimate("no files mentioned")
        self.assertEqual(estimate.primary_files, ())
        self.assertNotEqual(estimate.coverage_ratio, 1.0)

        report = check_multi_file_completeness(
            [], [], ["api.py"],
            coverage_ratio=1.0,
            primary_files=(),
        )
        self.assertFalse(report.is_complete)
        self.assertTrue(
            any("EMPTY_PRIMARY" in item or "VACUOUS" in item for item in report.rejections)
        )

        verdict = CodeDefaultCompletionPolicy().evaluate(
            "vg-code-balanced",
            ["api.py"],
            {"kind": "finish"},
            inspected_files=["api.py"],
            implicated_files=[],
            verification=VerificationReceipt(0, 1, "sha256:workspace"),
            current_workspace_digest="sha256:workspace",
            task_text="fix the crash in production",
            primary_files=(),
            coverage_ratio=1.0,
        )
        self.assertFalse(verdict["admissible"])
        self.assertIn("EMPTY_PRIMARY", verdict["reason"])

    def test_greenfield_bypass_cannot_apply_to_bugfix_brief(self) -> None:
        verdict = CodeDefaultCompletionPolicy().evaluate(
            "vg-code-balanced",
            ["api.py"],
            {"kind": "finish"},
            inspected_files=["api.py"],
            implicated_files=["api.py", "consumer.py"],
            verification=VerificationReceipt(0, 1, "sha256:workspace"),
            current_workspace_digest="sha256:workspace",
            task_text="bugfix: fix the null deref in the greenfield scaffold",
            greenfield_evidence={
                "baseline_recorded": True,
                "structural_passed": True,
                "smoke_test_created": True,
                "behavioral_passed": True,
                "oracle_failed_on_stub": True,
            },
        )
        self.assertFalse(verdict["admissible"])
        self.assertNotEqual(verdict["reason"], "completion_admissible")

    def test_public_signature_change_requires_callers_in_same_2pc_transaction(self) -> None:
        report = check_multi_file_completeness(
            ["api.py", "consumer.py"], ["api.py", "consumer.py"], ["api.py"],
            changed_public_symbols=["greet"],
            callers_by_symbol={"greet": ["consumer.py"]},
            same_transaction_files=["api.py"],
        )
        self.assertFalse(report.is_complete)
        self.assertTrue(
            any("TRANSACTION" in item or "CALLERS" in item for item in report.rejections)
        )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "api.py").write_text(_API, encoding="utf-8")
            (root / "consumer.py").write_text(_CONSUMER, encoding="utf-8")
            manager = AtomicMultiFileTransactionManager(root)
            result = manager.execute_transaction((
                FileMutation("api.py", _API_NEW, "modify"),
                FileMutation("consumer.py", _CONSUMER_NEW, "modify"),
            ))
            self.assertTrue(result.ok)
            self.assertEqual(
                set(result.value.mutated_files),
                {"api.py", "consumer.py"},
            )
            closed = check_multi_file_completeness(
                ["api.py", "consumer.py"],
                ["api.py", "consumer.py"],
                ["api.py", "consumer.py"],
                changed_public_symbols=["greet"],
                callers_by_symbol={"greet": ["consumer.py"]},
                same_transaction_files=result.value.mutated_files,
            )
            self.assertTrue(closed.is_complete)


if __name__ == "__main__":
    unittest.main()
