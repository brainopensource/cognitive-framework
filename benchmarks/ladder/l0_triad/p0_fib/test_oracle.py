"""Exterior oracle for P0-FIB. The agent must make these tests pass."""

from __future__ import annotations

import unittest

from fibonacci import fibonacci


class FibonacciOracle(unittest.TestCase):
    def test_zero_and_one(self) -> None:
        self.assertEqual(fibonacci(0), 0)
        self.assertEqual(fibonacci(1), 1)

    def test_known_values(self) -> None:
        self.assertEqual(fibonacci(10), 55)

    def test_negative_rejected(self) -> None:
        with self.assertRaises(ValueError):
            fibonacci(-1)


if __name__ == "__main__":
    unittest.main()
