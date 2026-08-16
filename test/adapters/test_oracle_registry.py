"""Preregistered evaluator oracle integrity tests."""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

_TOOLS = str(Path(__file__).resolve().parents[2] / "tools")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

import repo_paths  # noqa: E402


class OracleRegistryContract(unittest.TestCase):
    def test_three_oracles_are_digest_bound(self) -> None:
        registry = json.loads(repo_paths.preregistered_oracles().read_text())
        tasks = registry["tasks"]
        self.assertEqual(len(tasks), 3)
        self.assertEqual(len({task["id"] for task in tasks}), 3)
        for task in tasks:
            path = repo_paths.repo_path(task["oracle"])
            actual = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(actual, task["oracleDigest"])
            self.assertNotIn("REPLACE", task["oracleDigest"])

    def test_registry_does_not_claim_runs_were_completed(self) -> None:
        registry = json.loads(repo_paths.preregistered_oracles().read_text())
        self.assertEqual(registry["status"], "preregistered-not-run")


if __name__ == "__main__":
    unittest.main()
