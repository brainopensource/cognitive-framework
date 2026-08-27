"""Unit tests for InstrumentTuple and M-18 comparability rule.

Owning contract: REQ-BENCH-001, VG-07 §5.6, §5.8.
"""

import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.telemetry.tuple import (
    CompatibilityKey,
    InstrumentTuple,
    ObservationMetadata,
    StratificationFields,
    TreatmentDimensions,
)


class InstrumentTupleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.compat_a = CompatibilityKey(
            benchmark_id="swe_bench_lite",
            split_hash="sha256:split_1",
            model_fingerprint="openai/gpt-4o-mini",
            sampling_params={"temperature": 0.0, "max_tokens": 256},
            harness_commit="cddaaa33",
            agent_hash="agent_v4",
            evaluator_image_digest="sha256:eval_img",
            containment_digest="sha256:containment",
            substrate_profile="linux_x86_64",
        )
        self.strat_a = StratificationFields(difficulty="standard", language="python")
        self.meta_a = ObservationMetadata(
            timestamp="2026-08-15T20:00:00Z",
            run_id="run_arm_a",
            node_id="worker_01",
        )
        self.meta_b = ObservationMetadata(
            timestamp="2026-08-15T20:05:00Z",
            run_id="run_arm_b",
            node_id="worker_02",
        )

    def test_comparable_arms_differ_only_in_declared_treatment(self) -> None:
        treatment_a = TreatmentDimensions(manifest="vg-code-default", cache_enabled=True)
        treatment_b = TreatmentDimensions(manifest="vg-shell-only", cache_enabled=True)

        tuple_a = InstrumentTuple(self.compat_a, treatment_a, self.strat_a, self.meta_a)
        tuple_b = InstrumentTuple(self.compat_a, treatment_b, self.strat_a, self.meta_b)

        is_valid, reason = tuple_a.is_comparable_with(tuple_b)
        self.assertTrue(is_valid)
        self.assertEqual(reason, "")

    def test_mismatched_compatibility_key_refuses_comparison(self) -> None:
        compat_diff_model = CompatibilityKey(
            benchmark_id="swe_bench_lite",
            split_hash="sha256:split_1",
            model_fingerprint="deepseek/deepseek-v4-flash-0731",  # Different model
            sampling_params={"temperature": 0.0, "max_tokens": 256},
            harness_commit="cddaaa33",
            agent_hash="agent_v4",
            evaluator_image_digest="sha256:eval_img",
            containment_digest="sha256:containment",
            substrate_profile="linux_x86_64",
        )
        treatment_a = TreatmentDimensions(manifest="vg-code-default")
        treatment_b = TreatmentDimensions(manifest="vg-shell-only")

        tuple_a = InstrumentTuple(self.compat_a, treatment_a, self.strat_a, self.meta_a)
        tuple_b = InstrumentTuple(compat_diff_model, treatment_b, self.strat_a, self.meta_b)

        is_valid, reason = tuple_a.is_comparable_with(tuple_b)
        self.assertFalse(is_valid)
        self.assertIn("Compatibility key mismatch (M-18 violation)", reason)
        self.assertIn("modelFingerprint", reason)

    def test_mismatched_schema_version_refuses_comparison(self) -> None:
        compat_diff_schema = CompatibilityKey(
            benchmark_id="swe_bench_lite",
            split_hash="sha256:split_1",
            model_fingerprint="openai/gpt-4o-mini",
            schema_version="vg.3",  # Mismatched schema
        )
        treatment_a = TreatmentDimensions(manifest="vg-code-default")
        treatment_b = TreatmentDimensions(manifest="vg-shell-only")

        tuple_a = InstrumentTuple(self.compat_a, treatment_a, self.strat_a, self.meta_a)
        tuple_b = InstrumentTuple(compat_diff_schema, treatment_b, self.strat_a, self.meta_b)

        is_valid, reason = tuple_a.is_comparable_with(tuple_b)
        self.assertFalse(is_valid)
        self.assertIn("schemaVersion", reason)

    def test_identical_treatment_dimensions_flagged_as_aa_comparison(self) -> None:
        treatment_a = TreatmentDimensions(manifest="vg-code-default", cache_enabled=True)
        treatment_same = TreatmentDimensions(manifest="vg-code-default", cache_enabled=True)

        tuple_a = InstrumentTuple(self.compat_a, treatment_a, self.strat_a, self.meta_a)
        tuple_b = InstrumentTuple(self.compat_a, treatment_same, self.strat_a, self.meta_b)

        is_valid, reason = tuple_a.is_comparable_with(tuple_b)
        self.assertFalse(is_valid)
        self.assertIn("Treatment dimensions are identical", reason)


if __name__ == "__main__":
    unittest.main()
