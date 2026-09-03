"""Tests for test_output_parser and verification_gate in code-default pack."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "code-default"
if str(PACK) not in sys.path:
    sys.path.insert(0, str(PACK))

from middleware.testing.test_output_parser import (
    ParsedTestOutput,
    parse_test_output,
)
from middleware.testing.verification_gate import (
    GateDecision,
    evaluate_verification_gate,
)


class TestOutputParserTests(unittest.TestCase):
    def test_parse_successful_unittest_output(self) -> None:
        output = """
.....................
----------------------------------------------------------------------
Ran 21 tests in 0.052s

OK
"""
        parsed = parse_test_output(output, exit_code=0)
        self.assertTrue(parsed.passed)
        self.assertEqual(parsed.exit_code, 0)
        self.assertEqual(parsed.total_tests, 21)
        self.assertEqual(len(parsed.failed_tests), 0)
        self.assertTrue(parsed.raw_output_digest.startswith("sha256:"))

    def test_parse_failed_unittest_output(self) -> None:
        output = """
..F..E..
======================================================================
FAIL: test_addition (test_calc.TestCalc.test_addition)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test_calc.py", line 12, in test_addition
    self.assertEqual(add(1, 2), 4)
AssertionError: 3 != 4

======================================================================
ERROR: test_division (test_calc.TestCalc.test_division)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test_calc.py", line 18, in test_division
    div(1, 0)
ZeroDivisionError: division by zero

----------------------------------------------------------------------
Ran 8 tests in 0.010s

FAILED (failures=1, errors=1)
"""
        parsed = parse_test_output(output, exit_code=1)
        self.assertFalse(parsed.passed)
        self.assertEqual(parsed.exit_code, 1)
        self.assertEqual(parsed.total_tests, 8)
        self.assertEqual(len(parsed.failed_tests), 2)
        self.assertIn("test_addition (test_calc.TestCalc.test_addition)", parsed.failed_tests)
        self.assertIn("test_division (test_calc.TestCalc.test_division)", parsed.failed_tests)
        self.assertIn("AssertionError", parsed.exception_types)
        self.assertIn("ZeroDivisionError", parsed.exception_types)
        self.assertGreaterEqual(len(parsed.error_locations), 2)

    def test_parse_pytest_failed_output(self) -> None:
        output = """
============================= test session starts ==============================
FAILED tests/test_api.py::test_create_user
FAILED tests/test_db.py::test_connection
======================== 2 failed, 10 passed in 0.45s =========================
"""
        parsed = parse_test_output(output, exit_code=1)
        self.assertFalse(parsed.passed)
        self.assertEqual(len(parsed.failed_tests), 2)
        self.assertEqual(parsed.failed_tests[0], "tests/test_api.py::test_create_user")
        self.assertEqual(parsed.failed_tests[1], "tests/test_db.py::test_connection")

    def test_parse_empty_output(self) -> None:
        parsed = parse_test_output("", exit_code=0)
        self.assertFalse(parsed.passed)
        self.assertEqual(parsed.total_tests, 0)
        self.assertEqual(len(parsed.failed_tests), 0)
        self.assertEqual(parsed.runner, "unknown")
        self.assertIsNone(parsed.tests_collected)
        self.assertIsNone(parsed.tests_executed)
        self.assertIsNone(parsed.tests_passed)
        self.assertIsNone(parsed.tests_failed)
        self.assertIsNone(parsed.tests_skipped)

    def test_parse_ran_zero_and_pytest_zero_passed(self) -> None:
        ran_zero = parse_test_output("Ran 0 tests in 0.001s\n\nOK", exit_code=0)
        self.assertEqual(ran_zero.runner, "unittest")
        self.assertEqual(ran_zero.tests_collected, 0)
        self.assertEqual(ran_zero.tests_executed, 0)
        self.assertEqual(ran_zero.tests_passed, 0)
        self.assertFalse(ran_zero.passed)

        pytest_zero = parse_test_output("0 passed in 0.01s", exit_code=0)
        self.assertEqual(pytest_zero.runner, "pytest")
        self.assertEqual(pytest_zero.tests_passed, 0)
        self.assertEqual(pytest_zero.tests_executed, 0)
        self.assertFalse(pytest_zero.passed)


class VerificationGateTests(unittest.TestCase):
    def test_successful_run_admitted(self) -> None:
        parsed = ParsedTestOutput(
            exit_code=0,
            passed=True,
            total_tests=5,
            failed_tests=(),
            error_locations=(),
            exception_types=(),
            short_diagnostics=(),
            raw_output_digest="sha256:abc",
        )
        decision = evaluate_verification_gate(parsed)
        self.assertTrue(decision.admitted)
        self.assertIn("All tests passed", decision.reason)

    def test_nonzero_exit_code_rejected(self) -> None:
        parsed = ParsedTestOutput(
            exit_code=2,
            passed=False,
            total_tests=5,
            failed_tests=(),
            error_locations=(),
            exception_types=(),
            short_diagnostics=("syntax error",),
            raw_output_digest="sha256:abc",
        )
        decision = evaluate_verification_gate(parsed)
        self.assertFalse(decision.admitted)
        self.assertIn("non-zero code 2", decision.reason)

    def test_failed_tests_rejected(self) -> None:
        parsed = ParsedTestOutput(
            exit_code=0,
            passed=False,
            total_tests=10,
            failed_tests=("test_foo", "test_bar"),
            error_locations=(),
            exception_types=("AssertionError",),
            short_diagnostics=("2 tests failed",),
            raw_output_digest="sha256:abc",
        )
        decision = evaluate_verification_gate(parsed)
        self.assertFalse(decision.admitted)
        self.assertIn("2 tests failed", decision.reason)

    def test_zero_tests_executed_rejected_when_required(self) -> None:
        parsed = ParsedTestOutput(
            exit_code=0,
            passed=True,
            total_tests=0,
            failed_tests=(),
            error_locations=(),
            exception_types=(),
            short_diagnostics=(),
            raw_output_digest="sha256:abc",
        )
        decision = evaluate_verification_gate(parsed, require_executed_tests=True)
        self.assertFalse(decision.admitted)
        self.assertIn("No tests were executed", decision.reason)

    def test_zero_tests_admitted_when_not_required(self) -> None:
        parsed = ParsedTestOutput(
            exit_code=0,
            passed=True,
            total_tests=0,
            failed_tests=(),
            error_locations=(),
            exception_types=(),
            short_diagnostics=(),
            raw_output_digest="sha256:abc",
        )
        decision = evaluate_verification_gate(parsed, require_executed_tests=False)
        self.assertTrue(decision.admitted)


if __name__ == "__main__":
    unittest.main()
