"""Exterior oracle for P0-BUG. Pre-fix this file fails; post-fix it passes."""

from __future__ import annotations

import unittest

from string_utils import truncate_with_ellipsis


class TruncateOracle(unittest.TestCase):
    def test_short_unchanged(self) -> None:
        self.assertEqual(truncate_with_ellipsis("ab", 5), "ab")

    def test_ellipsis_length(self) -> None:
        self.assertEqual(truncate_with_ellipsis("abcdefghij", 6), "abc...")

    def test_tiny_budget(self) -> None:
        self.assertEqual(truncate_with_ellipsis("abcd", 2), "ab")


if __name__ == "__main__":
    unittest.main()
