from __future__ import annotations

import unittest

from slugify import slugify


class SlugifyTests(unittest.TestCase):
    def test_normalizes_punctuation_and_whitespace(self) -> None:
        self.assertEqual(slugify("  Hello, Vanguard!  "), "hello-vanguard")

    def test_empty_or_punctuation_only_input_is_empty(self) -> None:
        self.assertEqual(slugify("  !!!  "), "")

    def test_truncation_does_not_leave_a_trailing_separator(self) -> None:
        self.assertEqual(slugify("alpha beta", max_length=6), "alpha")


if __name__ == "__main__":
    unittest.main()
