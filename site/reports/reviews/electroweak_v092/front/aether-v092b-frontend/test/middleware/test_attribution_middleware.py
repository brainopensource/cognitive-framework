"""Tests for deterministic attribution projection and Invariant I10."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "packs" / "code-default"
if str(PACK) not in sys.path:
    sys.path.insert(0, str(PACK))

from middleware.attribution.trajectory_classifier import classify_trajectory_failure


class TestAttributionMiddleware(unittest.TestCase):
    def test_harness_denial_classification(self) -> None:
        rec = classify_trajectory_failure([], "denied", "command_disallowed:curl")
        self.assertEqual(rec.classification, "harness")
        self.assertIn("HARNESS_DENIAL", rec.evidence_codes)

    def test_provider_transport_error(self) -> None:
        rec = classify_trajectory_failure([], "instrument_error", "provider returned HTTP 429")
        self.assertEqual(rec.classification, "provider")

    def test_protocol_truncation_error(self) -> None:
        rec = classify_trajectory_failure([], "instrument_error", "OUTPUT_TRUNCATED")
        self.assertEqual(rec.classification, "protocol")

    def test_dataset_invalid_classification(self) -> None:
        rec = classify_trajectory_failure([], "inconclusive:dataset_invalid", "DATASET_INVALID: baseline passes")
        self.assertEqual(rec.classification, "dataset")

    def test_invariant_i10_unknown_never_defaults_to_model(self) -> None:
        rec = classify_trajectory_failure([], "unexpected_abort", "some non-descript crash")
        self.assertEqual(rec.classification, "unknown")
        self.assertNotEqual(rec.classification, "llm")


if __name__ == "__main__":
    unittest.main()
