"""REL-02 falsifiers: frozen single-attempt canary integrity.

The canary is content-addressed and single-attempt.  These tests pin that any
drift in task payload, base commit, evaluator, attempt policy, ceilings, or
missingness vocabulary refuses live execution with a typed failure -- never a
warning and never a silent substitution.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from benchmarks.m8_heldout.canary import (
    CANARY_DISPOSITIONS,
    CANARY_SCHEMA,
    CanaryIntegrityError,
    compute_manifest_digest,
    load_canary,
    verify_canary,
)

ROOT = Path(__file__).resolve().parents[2]
CANARY_PATH = ROOT / "benchmarks" / "m8_heldout" / "artifacts" / "canary_manifest.json"


def _tampered(mutate) -> dict:
    manifest = json.loads(CANARY_PATH.read_text(encoding="utf-8"))
    mutate(manifest)
    return manifest


def _load_tampered(manifest: dict):
    """Run the live-admission reader against a tampered in-memory manifest."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(manifest, handle)
        path = handle.name
    try:
        return load_canary(path)
    finally:
        Path(path).unlink(missing_ok=True)


class TestRel02FrozenCanary(unittest.TestCase):
    def test_frozen_manifest_verifies_and_loads(self) -> None:
        self.assertTrue(CANARY_PATH.is_file(), "canary artifact must exist")
        manifest = json.loads(CANARY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema"], CANARY_SCHEMA)
        verification = verify_canary(manifest)
        self.assertTrue(verification.ok, verification.failures)
        self.assertEqual(load_canary()["schema"], CANARY_SCHEMA)

    def test_manifest_digest_is_deterministic_and_self_binding(self) -> None:
        manifest = json.loads(CANARY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            compute_manifest_digest(manifest),
            compute_manifest_digest(manifest),
            "digest computation must be pure",
        )
        self.assertEqual(manifest["manifest_digest"], compute_manifest_digest(manifest))

    def test_tampered_task_payload_refuses_live_execution(self) -> None:
        def mutate(manifest: dict) -> None:
            manifest["tasks"][0]["title"] = "silently replaced task"

        with self.assertRaises(CanaryIntegrityError) as caught:
            _load_tampered(_tampered(mutate))
        self.assertIn("DIGEST_MISMATCH", str(caught.exception))

    def test_tampered_base_commit_refuses_live_execution(self) -> None:
        def mutate(manifest: dict) -> None:
            manifest["base_commit"] = "0" * 40

        with self.assertRaises(CanaryIntegrityError) as caught:
            _load_tampered(_tampered(mutate))
        self.assertIn("DIGEST_MISMATCH", str(caught.exception))

    def test_tampered_evaluator_refuses_live_execution(self) -> None:
        def mutate(manifest: dict) -> None:
            manifest["tasks"][0]["evaluator"] = "self:graded"

        with self.assertRaises(CanaryIntegrityError) as caught:
            _load_tampered(_tampered(mutate))
        self.assertIn("DIGEST_MISMATCH", str(caught.exception))

    def test_structural_drift_fails_closed_even_with_forged_digest(self) -> None:
        """A recomputed digest must not launder a policy violation."""
        def mutate(manifest: dict) -> None:
            manifest["attempt_policy"]["max_attempts"] = 3
            manifest["manifest_digest"] = compute_manifest_digest(manifest)

        verification = verify_canary(_tampered(mutate))
        self.assertFalse(verification.ok)
        self.assertIn("MAX_ATTEMPTS_NOT_ONE", verification.failures)

    def test_ten_unique_executable_single_attempt_tasks(self) -> None:
        manifest = json.loads(CANARY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(manifest["task_count"], 10)
        self.assertEqual(len(manifest["tasks"]), 10)
        ids = [task["id"] for task in manifest["tasks"]]
        self.assertEqual(len(set(ids)), 10)
        for task in manifest["tasks"]:
            self.assertTrue(task["payload_digest"].startswith("sha256:"))
            self.assertEqual(task["max_attempts"], 1)
            self.assertTrue(task["setup_commands"])
            self.assertTrue(task["evaluator"].startswith("exterior:"))
        self.assertEqual(manifest["attempt_policy"]["max_attempts"], 1)
        self.assertFalse(manifest["attempt_policy"]["retry_on_instrument_error"])

    def test_denominator_and_missingness_policy_are_declared(self) -> None:
        manifest = json.loads(CANARY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(manifest["denominator"], manifest["task_count"])
        policy = manifest["missingness_policy"]
        self.assertEqual(set(policy["dispositions"]), set(CANARY_DISPOSITIONS))
        self.assertEqual(policy["success_disposition"], "PASSED")
        self.assertEqual(policy["denominator_rule"], "fixed_at_task_count")
        self.assertEqual(policy["invalid_task_substitution"], "forbidden")

    def test_cost_token_and_time_ceilings_are_declared(self) -> None:
        budget = json.loads(CANARY_PATH.read_text(encoding="utf-8"))["resource_budget"]
        for key in ("global_cost_usd_ceiling", "per_task_cost_usd_ceiling",
                    "global_token_ceiling", "per_task_token_ceiling",
                    "per_task_timeout_seconds"):
            self.assertGreater(budget[key], 0, key)

    def test_adverse_case_present_and_dataset_limits_disclosed(self) -> None:
        manifest = json.loads(CANARY_PATH.read_text(encoding="utf-8"))
        classes = {task["task_class"] for task in manifest["tasks"]}
        self.assertIn("adversarial", classes)
        # The dataset does not support bugfix/multi-file classes yet; the
        # freeze must disclose that limitation rather than mislabel tasks.
        self.assertIn("bugfix", manifest["freeze_note"])
        self.assertIn("multi-file", manifest["freeze_note"])

    def test_expected_artifact_schema_is_declared_with_digest_binding(self) -> None:
        schema = json.loads(CANARY_PATH.read_text(encoding="utf-8"))["expected_artifact_schema"]
        for name in ("task_digest", "patch_digest", "trajectory_digest",
                     "evaluator_identity_digest", "verdict"):
            self.assertIn(name, schema["required_fields"])
        self.assertIn("digest mismatch", schema["binding"])


if __name__ == "__main__":
    unittest.main()
