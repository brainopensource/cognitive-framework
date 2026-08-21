from __future__ import annotations

import unittest

from tools.linters.check_falsifier_ids import allocations, check, expand_ids


class FalsifierIdentifierLinter(unittest.TestCase):
    def test_ranges_expand_inclusively(self) -> None:
        self.assertEqual(expand_ids("RF-23, RF-28–RF-30"), (23, 28, 29, 30))

    def test_conflicting_allocations_are_rejected(self) -> None:
        text = (
            "| RF allocation | Owner | Locked subject / milestone |\n"
            "|---|---|---|\n"
            "| `RF-23` | ADR-A | first |\n"
            "| `RF-23` | ADR-B | second |\n"
        )
        _rows, errors = allocations(text)
        self.assertTrue(errors)

    def test_multiple_backticked_ids_and_ranges_share_one_allocation(self) -> None:
        text = (
            "| RF allocation | Owner | Locked subject / milestone |\n"
            "|---|---|---|\n"
            "| `RF-23`, `RF-24`, `RF-27` | ADR-0078 | trajectory / M-2 |\n"
            "| `RF-28`–`RF-30` | ADR-0077 | graph / M-3 |\n"
        )
        rows, errors = allocations(text)
        self.assertEqual(errors, [])
        self.assertEqual(set(rows), {23, 24, 27, 28, 29, 30})

    def test_repository_allocations_are_consistent(self) -> None:
        self.assertEqual(check(), [])


if __name__ == "__main__":
    unittest.main()
