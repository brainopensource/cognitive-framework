"""Tests for M-18 Instrument Tuple and Comparability Rules (S9-C-01)."""

from __future__ import annotations

import unittest

from tools.telemetry.tuple import (
    CompatibilityKey,
    IncomparableLiftError,
    InstrumentTuple,
    ObservationMetadata,
    StratificationFields,
    TreatmentDimensions,
    compute_lift,
)


class TestInstrumentTuple(unittest.TestCase):
    def setUp(self) -> None:
        self.valid_k_compat = CompatibilityKey(
            benchmark_id="swe-bench-lite",
            split_hash="sha256:split123",
            model_fingerprint="fp:claude-3-5-sonnet",
            harness_commit="a1b2c3d4e5f6",
            agent_hash="sha256:agent_vanguard",
            evaluator_image_digest="sha256:evaluator_image_abc",
            containment_digest="sha256:containment_bwrap_xyz",
        )
        self.strat = StratificationFields(difficulty="standard", language="python")
        self.meta = ObservationMetadata(timestamp="2026-08-17T00:00:00Z", run_id="run-1", data_source="live")

    def test_comparable_arms_compute_lift(self) -> None:
        tuple_a = InstrumentTuple(
            compat_key=self.valid_k_compat,
            treatment=TreatmentDimensions(manifest="vg-code-default"),
            stratification=self.strat,
            meta=self.meta,
        )
        tuple_b = InstrumentTuple(
            compat_key=self.valid_k_compat,
            treatment=TreatmentDimensions(manifest="vg-code-claude-shaped"),
            stratification=self.strat,
            meta=self.meta,
        )
        result_a = {"pass_rate": 0.40}
        result_b = {"pass_rate": 0.60}

        lift = compute_lift(tuple_a, result_a, tuple_b, result_b)
        self.assertFalse(lift["refused"])
        self.assertEqual(lift["absolute_lift"], 0.20)
        self.assertEqual(lift["relative_lift"], 0.50)

    def test_differing_k_compat_refuses_lift(self) -> None:
        """S9-C-01: A lift computation across differing K_compat must refuse."""
        tuple_a = InstrumentTuple(
            compat_key=self.valid_k_compat,
            treatment=TreatmentDimensions(manifest="vg-code-default"),
            stratification=self.strat,
            meta=self.meta,
        )
        differing_k_compat = CompatibilityKey(
            benchmark_id="swe-bench-lite",
            split_hash="sha256:split456",  # Different split!
            model_fingerprint="fp:claude-3-5-sonnet",
            harness_commit="a1b2c3d4e5f6",
            agent_hash="sha256:agent_vanguard",
            evaluator_image_digest="sha256:evaluator_image_abc",
            containment_digest="sha256:containment_bwrap_xyz",
        )
        tuple_b = InstrumentTuple(
            compat_key=differing_k_compat,
            treatment=TreatmentDimensions(manifest="vg-code-claude-shaped"),
            stratification=self.strat,
            meta=self.meta,
        )
        result_a = {"pass_rate": 0.40}
        result_b = {"pass_rate": 0.60}

        lift = compute_lift(tuple_a, result_a, tuple_b, result_b)
        self.assertTrue(lift["refused"])
        self.assertIn("Compatibility key mismatch (M-18 violation)", lift["reason"])
        self.assertIn("splitHash", lift["reason"])

        with self.assertRaises(IncomparableLiftError):
            compute_lift(tuple_a, result_a, tuple_b, result_b, strict=True)

    def test_placeholder_digests_fail_closed(self) -> None:
        """S9-C-01: Fail closed on placeholder digests."""
        placeholder_k = CompatibilityKey(
            benchmark_id="swe-bench-lite",
            split_hash="sha256:split123",
            model_fingerprint="fp:claude-3-5-sonnet",
            harness_commit="v0.5.0",  # Placeholder!
            agent_hash="default_agent",  # Placeholder!
            evaluator_image_digest="sha256:evaluator_default",  # Placeholder!
            containment_digest="sha256:containment_default",  # Placeholder!
        )
        with self.assertRaises(ValueError) as cm:
            placeholder_k.validate_non_placeholder()
        self.assertIn("placeholder or empty digest not permitted", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
