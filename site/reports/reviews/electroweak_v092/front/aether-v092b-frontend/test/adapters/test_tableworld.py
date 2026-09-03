"""Tests for TableWorld Environment and Evaluator (S10-B-01)."""

from __future__ import annotations

import unittest
from pathlib import Path

from vanguard.packages.adapters.environment.tableworld import (
    TableWorldEnvironment,
    TableWorldEvaluator,
)
from vanguard.packages.agency.manifests.loader import ManifestLoader

MANIFESTS_DIR = Path(__file__).resolve().parents[2] / "vanguard" / "packages" / "agency" / "manifests"


class TestTableWorld(unittest.TestCase):
    def setUp(self) -> None:
        self.initial_data = {
            "accounts": [
                {"id": "1", "name": "Alice", "balance": 100.0, "status": "active"},
                {"id": "2", "name": "Bob", "balance": 150.0, "status": "active"},
                {"id": "3", "name": "Charlie", "balance": 50.0, "status": "pending"},
            ]
        }
        self.env = TableWorldEnvironment(self.initial_data)

    def test_table_read_and_patch_operations(self) -> None:
        """S10-B-01: TableWorld handles structured table.read and table.patch."""
        read_res = self.env.handle_read("accounts")
        self.assertTrue(read_res.success)
        self.assertEqual(read_res.value["rowCount"], 3)

        # Patch Bob's balance
        patch_res = self.env.handle_patch("accounts", "2", {"balance": 200.0})
        self.assertTrue(patch_res.success)
        self.assertEqual(patch_res.value["updated"]["balance"], 200.0)

        # Read back with filter
        filtered_res = self.env.handle_read("accounts", "name", "Bob")
        self.assertTrue(filtered_res.success)
        self.assertEqual(filtered_res.value["rows"][0]["balance"], 200.0)

    def test_evaluator_checks_invariants_and_uniqueness(self) -> None:
        """S10-B-01: TableWorldEvaluator checks column sum and uniqueness invariants."""
        # Expected sum: 100 + 150 + 50 = 300
        res = TableWorldEvaluator.evaluate_invariants(
            self.env,
            "accounts",
            expected_sum_col="balance",
            expected_sum_val=300.0,
            uniqueness_col="name",
        )
        self.assertTrue(res["passed"])

        # Violate sum
        self.env.handle_patch("accounts", "1", {"balance": 500.0})
        res_fail = TableWorldEvaluator.evaluate_invariants(
            self.env,
            "accounts",
            expected_sum_col="balance",
            expected_sum_val=300.0,
        )
        self.assertFalse(res_fail["passed"])
        self.assertIn("Sum mismatch", res_fail["reason"])

    def test_evaluator_scores_abstention_on_inconsistency_as_success(self) -> None:
        """S10-B-01: Inconsistency -> abstention is a scored success (T4.5)."""
        res = TableWorldEvaluator.evaluate_invariants(
            self.env,
            "accounts",
            abstained=True,
            allow_abstention=True,
        )
        self.assertTrue(res["passed"])
        self.assertTrue(res["abstained"])

    def test_vg_table_default_pack_composes(self) -> None:
        """S10-B-01: vg-table-default pack composes cleanly with ManifestLoader."""
        loader = ManifestLoader(MANIFESTS_DIR)
        pack = loader.load_pack("vg-table-default")
        self.assertEqual(pack.name, "vg-table-default")
        self.assertEqual(pack.to_canonical("TableRead"), "table.read")
        self.assertEqual(pack.to_canonical("TablePatch"), "table.patch")


if __name__ == "__main__":
    unittest.main()
