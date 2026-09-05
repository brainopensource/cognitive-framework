"""T-08 counts and the T-07 typed verification subject.

Counts stay honest (`Ran 0 tests` is zero, an unrecognised runner stays
unknown) and the subject those counts are attached to is typed: a verification
receipt binds argv, the postimage it ran over, and the task it ran for, so it
cannot be carried across a write or borrowed from another task.
"""

from __future__ import annotations

import unittest

from vanguard.packages.runtime.session import (
    VerificationSubject,
    parse_observed_test_counts,
    verification_argv,
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

class TestTypedVerificationSubject(unittest.TestCase):
    """T-07. What the receipt is a receipt *of*, not just what was typed."""

    def test_an_inline_interpreter_one_liner_is_not_verification(self) -> None:
        """`python3 -c 'print("OK")'` is prose the agent wrote, not an oracle."""
        self.assertIsNone(verification_argv({"argv": ["python3", "-c", 'print("OK")']}))

    def test_an_inline_one_liner_cannot_buy_a_subject_by_saying_test(self) -> None:
        """A model that writes the program can write its output too."""
        self.assertIsNone(
            verification_argv({"argv": ["python3", "-c", 'print("3 tests passed")']}))

    def test_a_named_runner_is_a_subject(self) -> None:
        self.assertEqual(
            verification_argv({"argv": ["pytest", "-q"]}), ("pytest", "-q"))
        self.assertEqual(
            verification_argv({"argv": ["python3", "-m", "unittest", "test.app"]}),
            ("python3", "-m", "unittest", "test.app"),
        )

    def test_an_unrelated_command_is_not_a_subject(self) -> None:
        self.assertIsNone(verification_argv({"argv": ["git", "status"]}))
        self.assertIsNone(verification_argv({"argv": []}))
        self.assertIsNone(verification_argv({"argv": "pytest -q"}))

    def test_the_same_argv_over_a_different_postimage_is_a_different_subject(self) -> None:
        argv = ("pytest", "-q")
        before = VerificationSubject(argv, "sha256:before", "sha256:task")
        after = VerificationSubject(argv, "sha256:after", "sha256:task")
        self.assertNotEqual(before.digest(), after.digest())

    def test_the_same_argv_for_a_different_task_is_a_different_subject(self) -> None:
        argv = ("pytest", "-q")
        mine = VerificationSubject(argv, "sha256:ws", "sha256:mine")
        theirs = VerificationSubject(argv, "sha256:ws", "sha256:theirs")
        self.assertNotEqual(mine.digest(), theirs.digest())

    def test_the_subject_digest_is_stable_for_the_same_three_facts(self) -> None:
        subject = VerificationSubject(("pytest", "-q"), "sha256:ws", "sha256:task")
        self.assertEqual(
            subject.digest(),
            VerificationSubject(("pytest", "-q"), "sha256:ws", "sha256:task").digest(),
        )


if __name__ == "__main__":
    unittest.main()
