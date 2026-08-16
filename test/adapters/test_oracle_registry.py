"""Preregistered evaluator oracle integrity tests."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


class OracleRegistryContract(unittest.TestCase):
    def test_three_oracles_are_digest_bound(self) -> None:
        root = Path(__file__).resolve().parents[2]
        registry = json.loads((root / "docs/agile/sprint6B/preregistered_oracles.json").read_text())
        tasks = registry["tasks"]
        self.assertEqual(len(tasks), 3)
        self.assertEqual(len({task["id"] for task in tasks}), 3)
        for task in tasks:
            path = root / task["oracle"]
            actual = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(actual, task["oracleDigest"])
            self.assertNotIn("REPLACE", task["oracleDigest"])

    def test_registry_does_not_claim_runs_were_completed(self) -> None:
        root = Path(__file__).resolve().parents[2]
        registry = json.loads((root / "docs/agile/sprint6B/preregistered_oracles.json").read_text())
        self.assertEqual(registry["status"], "preregistered-not-run")


if __name__ == "__main__":
    unittest.main()
