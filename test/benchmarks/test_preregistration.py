"""T-95 / T-26: preregistration, single-dimension comparisons, L2 arm pin."""

from __future__ import annotations

import unittest

from benchmarks.ladder.control import (
    CONTROL_ARM,
    ControlManifestError,
    ControlNotFrozen,
    load_preregistration,
    require_frozen,
)
from benchmarks.ladder.evidence import suite_digest
from benchmarks.ladder.hypotheses import HypothesisError, assert_single_dimension, require_hypothesis
from vanguard.packages.runtime.paired_evaluation import assert_single_varied_dimension


FROZEN_SUBJECT = "abc" * 8 + "0" * 16
TASK_IDS = tuple(f"L2-T{index:02d}" for index in range(1, 31))


def _digests(prefix: str) -> dict:
    return {task: f"sha256:{prefix}{index:062d}" for index, task in enumerate(TASK_IDS)}


def frozen_manifest(**overrides: object) -> dict:
    """A completely bound FROZEN control manifest. Never written to disk."""
    record = {
        "schema": "aether.control-preregistration/1",
        "task": "T-26",
        "status": "FROZEN",
        "arm": {
            "harness": "vg-code-balanced",
            "preset": "balanced",
            "workers": 1,
            "product_path": "vanguard.packages.runtime.entrypoint.execute",
            "excluded": ["forge", "chimera", "vg-code-fast", "vg-code-max"],
            "provider": "llama-cpp",
            "manifest_digest": "sha256:" + "11" * 32,
            "sampling_digest": "sha256:" + "22" * 32,
            "prompt_digest": "sha256:" + "33" * 32,
            "tool_schema_digest": "sha256:" + "44" * 32,
        },
        "sample": {
            "n_min": 30,
            "confidence": "wilson_95",
            "wilson_lb_min": 0.40,
            "retries_increase_coverage": False,
            "attempts_per_task": 1,
            "missing_outcomes_retain_slots": True,
            "stopping_rule": "stop after the 30 scheduled attempts, a resource ceiling or an integrity veto",
        },
        "suite": {
            "tasks": list(TASK_IDS),
            "task_digests": _digests("aa"),
            "oracle_digests": _digests("bb"),
        },
        "resources": {
            "max_attempts": 30,
            "max_provider_calls": 600,
            "max_inference_cost_usd_micros": 0,
            "max_evaluation_cost_usd_micros": 0,
            "max_wall_time_s": 7200,
        },
        "subject_sha": FROZEN_SUBJECT,
        "suite_digest": suite_digest(TASK_IDS),
        "model_id": "qwen2.5-coder-7b-instruct",
        "frozen_at": "2026-09-12T00:00:00Z",
        "notes": "test fixture; not a passing score",
    }
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(record.get(key), dict):
            record[key] = {**record[key], **value}
        else:
            record[key] = value
    return record


class TestPreregistration(unittest.TestCase):
    def test_control_arm_is_single_worker_balanced_product_path(self) -> None:
        self.assertEqual(CONTROL_ARM["harness"], "vg-code-balanced")
        self.assertEqual(CONTROL_ARM["preset"], "balanced")
        self.assertEqual(CONTROL_ARM["workers"], 1)
        self.assertIn("entrypoint.execute", CONTROL_ARM["product_path"])

    def test_unfrozen_control_cannot_be_scored(self) -> None:
        with self.assertRaises(ControlNotFrozen):
            require_frozen()

    def test_unregistered_treatment_is_refused(self) -> None:
        with self.assertRaises(HypothesisError):
            require_hypothesis("H-not-a-real-treatment")

    def test_registered_route_l_row_has_one_varied_dimension(self) -> None:
        row = require_hypothesis("H-T78-str-replace")
        self.assertEqual(row["varied_dimension"], "edit_primitive")
        self.assertEqual(row["task"], "T-78")

    def test_multi_dimension_comparison_is_refused(self) -> None:
        control = {"preset": "balanced", "model_id": "m1", "edit_primitive": "apply_patch"}
        treatment = {"preset": "max", "model_id": "m1", "edit_primitive": "str_replace"}
        with self.assertRaises(HypothesisError):
            assert_single_dimension(control, treatment, varied_dimension="edit_primitive")
        with self.assertRaises(ValueError):
            assert_single_varied_dimension(control, treatment, "edit_primitive")

    def test_single_dimension_comparison_is_admitted(self) -> None:
        control = {"preset": "balanced", "model_id": "m1", "edit_primitive": "apply_patch"}
        treatment = {"preset": "balanced", "model_id": "m1", "edit_primitive": "str_replace"}
        assert_single_dimension(control, treatment, varied_dimension="edit_primitive")
        assert_single_varied_dimension(control, treatment, "edit_primitive")


class TestManifestAdmission(unittest.TestCase):
    """T-26a: every field the refusal message names is actually validated."""

    def test_checked_in_record_stays_unfrozen_and_unbound(self) -> None:
        record = load_preregistration()
        self.assertEqual(record["status"], "UNFROZEN")
        self.assertIsNone(record["subject_sha"])
        self.assertIsNone(record["suite_digest"])
        self.assertIsNone(record["model_id"])

    def test_empty_record_does_not_fall_back_to_the_ambient_file(self) -> None:
        with self.assertRaises(ControlNotFrozen):
            require_frozen({})

    def test_frozen_status_without_a_subject_is_refused(self) -> None:
        with self.assertRaises(ControlNotFrozen):
            require_frozen(frozen_manifest(subject_sha=None))

    def test_a_fully_bound_manifest_is_admitted(self) -> None:
        admitted = require_frozen(frozen_manifest())
        self.assertEqual(admitted["subject_sha"], FROZEN_SUBJECT)
        self.assertEqual(len(admitted["suite"]["tasks"]), 30)

    def test_malformed_manifests_each_fail_closed(self) -> None:
        cases = {
            "wrong schema version": {"schema": "aether.control-preregistration/2"},
            "malformed subject": {"subject_sha": "not-a-sha"},
            "missing model identity": {"model_id": None},
            "missing freeze timestamp": {"frozen_at": None},
            "missing provider identity": {"arm": {"provider": None}},
            "missing configuration identity": {"arm": {"sampling_digest": None}},
            "unpinned harness": {"arm": {"harness": "vg-code-max"}},
            "unpinned preset": {"arm": {"preset": "max"}},
            "multi worker": {"arm": {"workers": 2}},
            "off product path": {"arm": {"product_path": "benchmarks.ladder_runner.main"}},
            "retries widen coverage": {"sample": {"retries_increase_coverage": True}},
            "more than one attempt per task": {"sample": {"attempts_per_task": 2}},
            "slots not retained": {"sample": {"missing_outcomes_retain_slots": False}},
            "no stopping rule": {"sample": {"stopping_rule": ""}},
            "lowered acceptance bound": {"sample": {"wilson_lb_min": 0.10}},
            "lowered sample floor": {"sample": {"n_min": 12}},
        }
        for label, override in cases.items():
            with self.subTest(label):
                with self.assertRaises(ControlManifestError):
                    require_frozen(frozen_manifest(**override))

    def test_unbound_suite_identity_is_refused(self) -> None:
        short = frozen_manifest()
        short["suite"]["tasks"] = list(TASK_IDS[:29])
        with self.assertRaises(ControlManifestError):
            require_frozen(short)

        duplicated = frozen_manifest()
        duplicated["suite"]["tasks"] = list(TASK_IDS[:29]) + [TASK_IDS[0]]
        with self.assertRaises(ControlManifestError):
            require_frozen(duplicated)

        with self.assertRaises(ControlManifestError):
            require_frozen(frozen_manifest(suite_digest="sha256:" + "00" * 32))

        missing_oracle = frozen_manifest()
        missing_oracle["suite"]["oracle_digests"].pop(TASK_IDS[3])
        with self.assertRaises(ControlManifestError):
            require_frozen(missing_oracle)

        missing_task_digest = frozen_manifest()
        missing_task_digest["suite"]["task_digests"][TASK_IDS[5]] = None
        with self.assertRaises(ControlManifestError):
            require_frozen(missing_task_digest)

    def test_no_resource_ceiling_is_left_unspecified(self) -> None:
        absent = frozen_manifest()
        del absent["resources"]
        with self.assertRaises(ControlManifestError):
            require_frozen(absent)
        for ceiling in (
            "max_attempts", "max_provider_calls", "max_inference_cost_usd_micros",
            "max_evaluation_cost_usd_micros", "max_wall_time_s",
        ):
            with self.subTest(ceiling):
                with self.assertRaises(ControlManifestError):
                    require_frozen(frozen_manifest(resources={ceiling: None}))

    def test_attempt_ceiling_must_cover_the_frozen_membership(self) -> None:
        with self.assertRaises(ControlManifestError):
            require_frozen(frozen_manifest(resources={"max_attempts": 29}))


if __name__ == "__main__":
    unittest.main()
