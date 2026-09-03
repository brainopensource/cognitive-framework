"""T-08: session-side counts without inventing; unknown runner stays unknown."""

from __future__ import annotations

import unittest

from vanguard.packages.runtime.session import (
    ADMISSION_GATE_EXEMPT,
    parse_observed_test_counts,
)


class TestObservedTestCounts(unittest.TestCase):
    def test_unittest_ran_zero_is_zero(self) -> None:
        counts = parse_observed_test_counts("Ran 0 tests in 0.001s\n\nOK")
        self.assertEqual(counts.runner, "unittest")
        self.assertEqual(counts.collected, 0)
        self.assertEqual(counts.executed, 0)
        self.assertEqual(counts.passed, 0)
        self.assertEqual(counts.failed, 0)
        self.assertEqual(counts.skipped, 0)

    def test_pytest_zero_passed_is_zero(self) -> None:
        counts = parse_observed_test_counts("======================== 0 passed in 0.01s =========================")
        self.assertEqual(counts.runner, "pytest")
        self.assertEqual(counts.passed, 0)
        self.assertEqual(counts.executed, 0)

    def test_pytest_full_summary(self) -> None:
        counts = parse_observed_test_counts(
            "collected 12 items\n======================== 2 failed, 10 passed, 0 skipped in 0.45s"
        )
        self.assertEqual(counts.runner, "pytest")
        self.assertEqual(counts.collected, 12)
        self.assertEqual(counts.passed, 10)
        self.assertEqual(counts.failed, 2)
        self.assertEqual(counts.skipped, 0)
        self.assertEqual(counts.executed, 12)

    def test_unrecognized_runner_stays_unknown(self) -> None:
        counts = parse_observed_test_counts("command succeeded\nOK\n")
        self.assertEqual(counts.runner, "unknown")
        self.assertIsNone(counts.collected)
        self.assertIsNone(counts.executed)
        self.assertIsNone(counts.passed)
        self.assertIsNone(counts.failed)
        self.assertIsNone(counts.skipped)

    def test_admission_gate_exempt_is_not_shrunk(self) -> None:
        self.assertEqual(ADMISSION_GATE_EXEMPT, frozenset({"vg-code-default", "vg-code-lex"}))


if __name__ == "__main__":
    unittest.main()
