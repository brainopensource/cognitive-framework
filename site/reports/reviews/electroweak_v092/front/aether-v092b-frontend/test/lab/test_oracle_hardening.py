"""Tests for Oracle Hardening, Mutation Checks, and Perturbations (S9-C-06)."""

from __future__ import annotations

import unittest


class TestOracleHardening(unittest.TestCase):
    def test_comment_only_patch_fails_execution(self) -> None:
        """S9-C-06: A comment containing the formula string does not pass functional evaluation."""
        comment_code = """
# calculate_value computes (A + B) * B
def calculate_value(a, b):
    pass
"""
        ns: dict = {}
        exec(comment_code, ns)
        fn = ns["calculate_value"]
        # Executing functional check fails on None return
        self.assertNotEqual(fn(2, 3), 15)

    def test_mutation_check_rejects_incorrect_implementations(self) -> None:
        """S9-C-06: Mutants of the formula must fail the oracle."""
        mutant_subtraction = lambda a, b: (a - b) * b
        mutant_precedence = lambda a, b: a + b * b
        mutant_constant = lambda a, b: 15

        # Oracle checks:
        def evaluate_oracle(fn) -> bool:
            try:
                if fn(2, 3) != 15:
                    return False
                if fn(0, 4) != 16:
                    return False
                if fn(-2, 3) != 3:
                    return False
                if fn(10, 5) != 75:
                    return False
                return True
            except Exception:
                return False

        self.assertFalse(evaluate_oracle(mutant_subtraction))
        self.assertFalse(evaluate_oracle(mutant_precedence))
        self.assertFalse(evaluate_oracle(mutant_constant))

        correct_fn = lambda a, b: (a + b) * b
        self.assertTrue(evaluate_oracle(correct_fn))

    def test_isomorphic_perturbation_check(self) -> None:
        """S9-C-06: Isomorphic perturbation verifies semantic identity (A + B)*B == A*B + B^2."""
        correct_fn = lambda a, b: (a + b) * b
        isomorph_fn = lambda a, b: (a * b) + (b ** 2)

        for a in (-5, 0, 3, 10):
            for b in (-2, 0, 4, 8):
                self.assertEqual(correct_fn(a, b), isomorph_fn(a, b))


if __name__ == "__main__":
    unittest.main()
