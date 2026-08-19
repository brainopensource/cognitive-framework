"""Tests for progress analysis, fingerprinting, and escalation decisions (REQ-TRUST-001, S31)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.apps.coding.coding_progress import (
    EscalationAction,
    ProgressAnalyzer,
    ProgressSignals,
    compute_action_digest,
    compute_patch_digest,
    compute_test_fingerprint,
    compute_workspace_digest,
)


class TestCodingProgress(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / "app.py").write_text("print('hello')\n")

    def test_workspace_digest_excludes_caches_and_is_deterministic(self) -> None:
        (self.root / "__pycache__").mkdir()
        (self.root / "__pycache__" / "app.cpython-312.pyc").write_bytes(b"cached")
        (self.root / ".git").mkdir()
        (self.root / ".git" / "HEAD").write_text("ref: main\n")

        digest1, hashes1 = compute_workspace_digest(self.root)
        digest2, hashes2 = compute_workspace_digest(self.root)

        self.assertEqual(digest1, digest2)
        self.assertIn("app.py", hashes1)
        self.assertNotIn("__pycache__/app.cpython-312.pyc", hashes1)
        self.assertNotIn(".git/HEAD", hashes1)

    def test_action_and_patch_digests_canonical(self) -> None:
        d1 = compute_action_digest("fs.read", {"path": "app.py"})
        d2 = compute_action_digest("fs.read", {"path": "app.py"})
        d3 = compute_action_digest("patch.apply", {"path": "app.py"})
        self.assertEqual(d1, d2)
        self.assertNotEqual(d1, d3)

        p1 = compute_patch_digest("--- a\n+++ b\n")
        p2 = compute_patch_digest("--- a\r\n+++ b\r\n")
        self.assertEqual(p1, p2)

    def test_test_fingerprint_normalization(self) -> None:
        fp1 = compute_test_fingerprint(
            ["python3", "-m", "unittest"],
            1,
            stdout="FAIL: test_divide (test_calc.TestCalc)\nAssertionError: 1 != 2",
        )
        fp2 = compute_test_fingerprint(
            ["python3", "-m", "unittest"],
            1,
            stdout="FAIL: test_divide (test_calc.TestCalc)\nAssertionError: 1 != 2\nExtra noise 12:34",
        )
        self.assertEqual(fp1, fp2)

    def test_progress_analyzer_detects_deltas(self) -> None:
        analyzer = ProgressAnalyzer(self.root)
        signals = analyzer.analyze_turn(
            verb="fs.read",
            args={"path": "app.py"},
        )
        self.assertTrue(signals.real_tool_action)
        self.assertFalse(signals.workspace_changed)
        self.assertFalse(signals.repeated_action_digest)

        # Second identical turn
        signals2 = analyzer.analyze_turn(
            verb="fs.read",
            args={"path": "app.py"},
        )
        self.assertTrue(signals2.repeated_action_digest)

        # Modify workspace
        (self.root / "new.py").write_text("def f(): pass\n")
        signals3 = analyzer.analyze_turn(
            verb="patch.apply",
            args={"path": "new.py"},
            patch="diff",
        )
        self.assertTrue(signals3.workspace_changed)
        self.assertIn("new.py", signals3.changed_paths)

    def test_escalation_decision_rules(self) -> None:
        analyzer = ProgressAnalyzer(self.root)

        # 1. Stop fail closed on missing key
        dec = analyzer.decide_escalation(missing_key=True)
        self.assertEqual(dec.action, EscalationAction.STOP_FAIL_CLOSED)

        # 2. Stop fail closed on unknown price
        dec = analyzer.decide_escalation(unknown_price=True)
        self.assertEqual(dec.action, EscalationAction.STOP_FAIL_CLOSED)

        # 3. 1st malformed -> retry same
        analyzer.analyze_turn(malformed=True)
        dec = analyzer.decide_escalation()
        self.assertEqual(dec.action, EscalationAction.RETRY_SAME)

        # 4. 2nd malformed -> rotate free provider
        analyzer.analyze_turn(malformed=True)
        dec = analyzer.decide_escalation()
        self.assertEqual(dec.action, EscalationAction.ROTATE_FREE_PROVIDER)

        # 5. Repeated test failure -> request diagnostic/replan
        analyzer.consecutive_malformed = 0
        analyzer.analyze_turn(
            test_result=(["python3", "test.py"], 1, "FAIL: test_a", ""),
        )
        analyzer.analyze_turn(
            test_result=(["python3", "test.py"], 1, "FAIL: test_a", ""),
        )
        dec = analyzer.decide_escalation()
        self.assertEqual(dec.action, EscalationAction.REQUEST_DIAGNOSTIC_REPLAN)
        self.assertEqual(dec.target_tier, "medium")

        # 6. Diagnosis succeeded -> descend to free executor
        dec = analyzer.decide_escalation(diagnosis_succeeded=True)
        self.assertEqual(dec.action, EscalationAction.DESCEND_TO_FREE_EXECUTOR)
        self.assertEqual(dec.target_tier, "free")

        # 7. Frontier requires explicit authorization
        dec = analyzer.decide_escalation(frontier_requested=True, frontier_authorized=False)
        self.assertEqual(dec.action, EscalationAction.REQUIRE_FRONTIER_AUTHORIZATION)


if __name__ == "__main__":
    unittest.main()
