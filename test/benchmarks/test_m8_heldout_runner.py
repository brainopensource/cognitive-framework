"""Unit and scientific integrity tests for M-8 held-out benchmark runner."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from benchmarks.m8_heldout.runner import (
    WorkloadDefinition,
    execute_empirical_run,
    load_workload,
)


class M8HeldOutBenchmarkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workload, self.tasks_meta = load_workload()

    def test_workload_splits_and_counts(self) -> None:
        self.assertEqual(len(self.workload.dev), 2)
        self.assertEqual(len(self.workload.held_out), 40)
        self.assertEqual(len(self.workload.adversarial), 1)
        self.assertEqual(len(self.workload.transfer), 1)
        self.assertEqual(len(self.tasks_meta), 44)

    def test_preregistration_artifact_integrity(self) -> None:
        prereg_path = Path("benchmarks/m8_heldout/artifacts/preregistration.json")
        self.assertTrue(prereg_path.is_file())
        data = json.loads(prereg_path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "aether.m8-preregistration/1")
        self.assertEqual(data["split_counts"]["total_unique_tasks"], 44)
        self.assertEqual(data["attempt_policy"]["max_attempts"], 1)
        self.assertEqual(data["min_held_out_lift"], 0.05)
        self.assertEqual(data["regression_budget"], 0.02)
        self.assertEqual(data["workload_digest"], self.workload.digest())

    def test_workload_rejects_contamination(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            WorkloadDefinition(
                dev=("dev_01", "held_out_01"),
                held_out=self.workload.held_out,
            )
        self.assertIn("contaminated", str(ctx.exception).lower())

    def test_dry_run_produces_verifiable_evidence_bundle(self) -> None:
        bundle = execute_empirical_run(
            self.workload,
            self.tasks_meta,
            candidate_id="cand-test-1",
            source_trajectory_digest="sha256:source-traj-1",
            generator_id="gen-test-1",
            evaluator_id="eval-test-1",
            promoter_id="promoter-test-1",
            gains=("held_out_01", "held_out_02", "held_out_03", "held_out_04"),
        )

        self.assertEqual(bundle["schema"], "aether.m8-evidence-bundle/1")
        self.assertEqual(bundle["workload_digest"], self.workload.digest())
        self.assertEqual(bundle["evaluation_detail"]["heldOutLift"], 0.1)
        self.assertEqual(bundle["evaluation_detail"]["regressionRate"], 0.0)
        self.assertTrue(bundle["evaluation_report"]["promotable"])

        # Check telemetry records
        records = bundle["records"]
        self.assertEqual(len(records), 82)
        for r in records:
            self.assertIn("turns", r["usage"])
            self.assertIn("promptTokens", r["usage"])
            self.assertIn("completionTokens", r["usage"])
            self.assertIn("usdMicros", r["usage"])
            self.assertIsNotNone(r["trajectoryDigest"])
            self.assertIn(r["arm"], ("control", "treatment"))


if __name__ == "__main__":
    unittest.main()
