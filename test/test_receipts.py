"""S6B-EVID-001 / QA-003 receipt validator must-fail cases."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "linters"))
from check_receipt import validate_receipt  # noqa: E402


def _base() -> dict:
    return {
        "schema_version": "gts.gate-receipt.v1",
        "gate": "R2",
        "result": "PASS",
        "subject_sha": "a" * 40,
        "evidence_commit": "a" * 40,
        "evidence_commit_relation": "same-commit",
        "commands": [
            {
                "argv": ["python3", "tools/check_boundaries.py"],
                "exit_code": 0,
                "stdout_sha256": "sha256:" + ("b" * 64),
                "stderr_sha256": "sha256:" + ("c" * 64),
            }
        ],
        "implementer": "lane-a",
        "signer": "lane-d",
        "countersigner": "project-lead",
        "timestamp_utc": "2026-08-16T00:00:00Z",
        "environment": {"python": "3.12", "node": "20", "os": "linux"},
    }


class ReceiptValidatorTests(unittest.TestCase):
    def test_valid_receipt(self) -> None:
        self.assertEqual(validate_receipt(_base(), path=Path("ok.json")), [])

    def test_self_approval_fails(self) -> None:
        data = _base()
        data["signer"] = data["implementer"]
        errors = validate_receipt(data, path=Path("self.json"))
        self.assertTrue(any("self-approval" in e for e in errors))

    def test_pending_result_fails(self) -> None:
        data = _base()
        data["result"] = "pending"
        errors = validate_receipt(data, path=Path("pending.json"))
        self.assertTrue(errors)

    def test_wrong_sha_relation_fails(self) -> None:
        data = _base()
        data["evidence_commit"] = "d" * 40
        errors = validate_receipt(data, path=Path("sha.json"))
        self.assertTrue(any("same-commit" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
