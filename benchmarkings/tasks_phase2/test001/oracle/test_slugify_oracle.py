from __future__ import annotations

import unittest

from slugify import slugify


class SlugifyOracle(unittest.TestCase):
    def test_boundary_after_multiple_separators(self) -> None:
        self.assertEqual(slugify("alpha --- beta", max_length=6), "alpha")

    def test_exact_non_separator_boundary_is_preserved(self) -> None:
        self.assertEqual(slugify("alphabet soup", max_length=8), "alphabet")


if __name__ == "__main__":
    unittest.main()
