"""Tests for testing middleware parsers and verification gates."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "packs" / "code-default"
if str(PACK) not in sys.path:
    sys.path.insert(0, str(PACK))

from middleware.testing.test_output_parser import parse_test_output
from middleware.testing.verification_gate import evaluate_verification_gate


class TestTestingMiddleware(unittest.TestCase):
    def test_parse_unittest_failure(self) -> None:
        sample_output = """
======================================================================
FAIL: test_multiplication (test_calc.TestCalc.test_multiplication)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test_calc.py", line 12, in test_multiplication
    self.assertEqual(multiply(2, 3), 6)
AssertionError: 5 != 6

----------------------------------------------------------------------
Ran 3 tests in 0.002s

FAILED (failures=1)
"""
        parsed = parse_test_output(sample_output, exit_code=1)
        self.assertFalse(parsed.passed)
        self.assertEqual(parsed.total_tests, 3)
        self.assertEqual(len(parsed.failed_tests), 1)
        self.assertIn("test_multiplication", parsed.failed_tests[0])
        self.assertIn("AssertionError", parsed.exception_types)
        self.assertEqual(len(parsed.error_locations), 1)
        self.assertEqual(parsed.error_locations[0]["file"], "test_calc.py")
        self.assertEqual(parsed.error_locations[0]["line"], 12)

    def test_verification_gate_eval(self) -> None:
        fail_parsed = parse_test_output("FAILED", exit_code=1)
        decision = evaluate_verification_gate(fail_parsed)
        self.assertFalse(decision.admitted)

        pass_output = "Ran 5 tests in 0.01s\n\nOK"
        pass_parsed = parse_test_output(pass_output, exit_code=0)
        pass_decision = evaluate_verification_gate(pass_parsed)
        self.assertTrue(pass_decision.admitted)


if __name__ == "__main__":
    unittest.main()
