"""Sealed test oracle for Dogfood Task 03 (Palindrome validation ignoring non-alphanumeric)."""

import unittest
from pathlib import Path

class TestPalindromeOracle(unittest.TestCase):
    def test_palindrome(self) -> None:
        try:
            import str_utils
        except ImportError:
            import sys
            sys.path.insert(0, str(Path(".").resolve()))
            import str_utils

        self.assertTrue(str_utils.is_palindrome("A man, a plan, a canal: Panama"))
        self.assertFalse(str_utils.is_palindrome("race a car"))
        self.assertTrue(str_utils.is_palindrome(""))

if __name__ == "__main__":
    unittest.main()
