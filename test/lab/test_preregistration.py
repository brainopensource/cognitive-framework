"""Tests for Pre-registration schema, hashing, and status lifecycle (S9-C-02)."""

from __future__ import annotations

import unittest

from tools.telemetry.preregistration import (
    Preregistration,
    PreregistrationError,
    PreregistrationStatus,
)


class TestPreregistration(unittest.TestCase):
    def setUp(self) -> None:
        self.prereg = Preregistration(
            preregistration_id="prereg-2026-001",
            hypotheses=["claude-shaped improves pass rate on multi-file tasks vs default"],
            primary_metric="pass_rate",
            alpha=0.05,
            correction="bonferroni",
            manifest_digests={
                "vg-code-default": "sha256:digest_default_123",
                "vg-code-claude-shaped": "sha256:digest_claude_456",
            },
            model_id="mock-provider",
            stopping_rule="fixed_n_50",
            corpus_split_ids=["split-dev-01"],
            instrument_error_policy="censor_and_refuse",
            created_at="2026-08-17T00:00:00Z",
            backend="mock",
        )

    def test_preregistration_hash_is_stable(self) -> None:
        """S9-C-02: Pre-registration produces a deterministic cryptographic hash."""
        h1 = self.prereg.compute_hash()
        h2 = self.prereg.compute_hash()
        self.assertEqual(h1, h2)
        self.assertTrue(h1.startswith("sha256:"))
        self.assertEqual(len(h1), 71)  # 'sha256:' + 64 hex characters (CT-09)

    def test_status_transitions_and_records_run_ids(self) -> None:
        """S9-C-02: Status transitions from preregistered to executed-lab with run ids."""
        self.assertEqual(self.prereg.status, PreregistrationStatus.PREREGISTERED)
        self.assertEqual(self.prereg.run_ids, [])

        self.prereg.mark_executed("run-001", is_live=False)
        self.assertEqual(self.prereg.status, PreregistrationStatus.EXECUTED_LAB)
        self.assertIn("run-001", self.prereg.run_ids)

        self.prereg.mark_executed("run-002", is_live=True)
        self.assertEqual(self.prereg.status, PreregistrationStatus.EXECUTED_LIVE)
        self.assertEqual(self.prereg.run_ids, ["run-001", "run-002"])

    def test_prior_hash_verification(self) -> None:
        """S9-C-02: Verification against prior registered hash succeeds or fails properly."""
        expected_hash = self.prereg.compute_hash()
        self.assertTrue(self.prereg.verify_prior_hash(expected_hash))
        self.assertFalse(self.prereg.verify_prior_hash("0" * 64))


if __name__ == "__main__":
    unittest.main()
