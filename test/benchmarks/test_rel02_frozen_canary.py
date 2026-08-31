"""REL-02: frozen content-addressed canary with max_attempts=1.

Falsifies the entry-gate defect recorded in docs/execution/active.md: no
canary manifest existed under benchmarks/m8_heldout/artifacts/. This suite
proves the manifest that repairs it is genuinely frozen (its digest changes
if any row's content changes), single-attempt, and honest about missing
workspaces rather than silently dropping them from the denominator.
"""

from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "benchmarks/m8_heldout/artifacts/canary_manifest.json"


def _digest_of(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


class TestRel02FrozenCanary(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_manifest_exists_and_is_non_empty(self) -> None:
        self.assertTrue(MANIFEST_PATH.is_file())
        self.assertTrue(self.manifest["rows"])

    def test_max_attempts_is_exactly_one(self) -> None:
        self.assertEqual(self.manifest["attempt_policy"]["max_attempts"], 1)
        self.assertFalse(self.manifest["attempt_policy"]["retry_on_instrument_error"])

    def test_manifest_digest_is_content_addressed_and_stable(self) -> None:
        body = {k: v for k, v in self.manifest.items() if k != "manifest_digest"}
        self.assertEqual(self.manifest["manifest_digest"], _digest_of(body))

    def test_mutating_any_row_changes_the_manifest_digest(self) -> None:
        mutated = copy.deepcopy(self.manifest)
        mutated["rows"][0]["task_class"] = "tampered"
        body = {k: v for k, v in mutated.items() if k != "manifest_digest"}
        self.assertNotEqual(self.manifest["manifest_digest"], _digest_of(body))

    def test_every_present_workspace_content_digest_matches_disk(self) -> None:
        for row in self.manifest["rows"]:
            workspace = ROOT / row["workspace"]
            if not workspace.is_dir():
                self.assertFalse(row["workspace_exists"])
                self.assertIsNone(row["content_digest"])
                continue
            self.assertTrue(row["workspace_exists"])
            files = sorted(p for p in workspace.rglob("*") if p.is_file())
            parts = [
                p.relative_to(workspace).as_posix() + ":" + hashlib.sha256(p.read_bytes()).hexdigest()
                for p in files
            ]
            expected = "sha256:" + hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()
            self.assertEqual(row["content_digest"], expected, msg=f"content drift for {row['task_id']}")

    def test_missing_workspace_is_a_typed_row_not_a_dropped_task(self) -> None:
        """A row whose directory disappeared stays in the denominator as inconclusive, never silently filtered."""
        for row in self.manifest["rows"]:
            if not row["workspace_exists"]:
                self.assertEqual(row["disposition_if_missing"], "inconclusive:workspace_missing")
                self.assertIsNone(row["content_digest"])

    def test_every_row_has_evaluator_and_evidence_schema(self) -> None:
        for row in self.manifest["rows"]:
            self.assertTrue(row["evaluator"])
            self.assertEqual(row["expected_evidence_schema"], "aether.canary-evidence/1")

    def test_no_row_ids_are_duplicated(self) -> None:
        ids = [row["task_id"] for row in self.manifest["rows"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_resource_budget_ceilings_are_positive(self) -> None:
        budget = self.manifest["resource_budget"]
        for key, value in budget.items():
            self.assertGreater(value, 0, msg=f"{key} must be a positive ceiling")


if __name__ == "__main__":
    unittest.main()
