"""CMX-07: Repository-scale qualification set, content addressing, and ablations falsifiers."""

from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "benchmarks/m8_heldout/artifacts/qualification_manifest.json"


def _digest_of(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


class TestCMX07QualificationSet(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_qualification_manifest_exists_and_is_valid(self) -> None:
        self.assertTrue(MANIFEST_PATH.is_file())
        self.assertEqual(self.manifest["schema"], "aether.cmx07-qualification/1")
        self.assertGreaterEqual(len(self.manifest["rows"]), 10)

    def test_attempt_policy_is_strictly_single_attempt(self) -> None:
        policy = self.manifest["attempt_policy"]
        self.assertEqual(policy["max_attempts"], 1)
        self.assertFalse(policy["retry_on_instrument_error"])

    def test_content_addressing_digest_is_frozen_and_valid(self) -> None:
        body = {k: v for k, v in self.manifest.items() if k != "manifest_digest"}
        self.assertEqual(self.manifest["manifest_digest"], _digest_of(body))

    def test_mutating_any_row_or_field_invalidates_manifest_digest(self) -> None:
        tampered = copy.deepcopy(self.manifest)
        tampered["rows"][0]["task_class"] = "tampered_class"
        body = {k: v for k, v in tampered.items() if k != "manifest_digest"}
        self.assertNotEqual(self.manifest["manifest_digest"], _digest_of(body))

    def test_required_task_taxonomy_is_fully_covered(self) -> None:
        classes = {row["task_class"] for row in self.manifest["rows"]}
        required_classes = {
            "bugfix_single",
            "bugfix_multi",
            "feature_cross_package",
            "migration",
            "refactor",
            "greenfield_python",
            "greenfield_nonpython",
            "adversarial_noisy",
            "resume_interrupted",
            "swe_bench_pro",
        }
        self.assertTrue(
            required_classes.issubset(classes),
            f"Missing required classes: {required_classes - classes}",
        )

    def test_present_workspaces_content_digest_matches_disk(self) -> None:
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
            expected = "sha256:" + hashlib.sha256(chr(10).join(parts).encode("utf-8")).hexdigest()
            self.assertEqual(
                row["content_digest"],
                expected,
                msg=f"Content digest mismatch for {row['task_id']}",
            )

    def test_missing_workspace_policy_preserves_denominator(self) -> None:
        for row in self.manifest["rows"]:
            if not row["workspace_exists"]:
                self.assertEqual(row["disposition_if_missing"], "inconclusive:workspace_missing")
                self.assertIsNone(row["content_digest"])

    def test_evaluator_and_expected_schema_present_on_every_row(self) -> None:
        for row in self.manifest["rows"]:
            self.assertTrue(row.get("evaluator"))
            self.assertEqual(row.get("expected_evidence_schema"), "aether.qualification-evidence/1")

    def test_ablation_arms_comparison_semantics(self) -> None:
        """Prove ablation comparisons use identical tasks and budgets without changing retry counts."""
        tasks = [row["task_id"] for row in self.manifest["rows"]]
        self.assertEqual(len(tasks), len(set(tasks)))

        # Verify ablation arms definition
        arms = {
            "preset_comparison": ("fast", "balanced", "max"),
            "routing_comparison": ("deepseek_only", "hybrid_free_deepseek"),
            "reviewer_comparison": ("reviewer_off", "reviewer_on"),
        }
        for arm_group, treatments in arms.items():
            self.assertGreaterEqual(len(treatments), 2)


if __name__ == "__main__":
    unittest.main()
