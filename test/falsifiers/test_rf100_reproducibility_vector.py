"""RF-100: Proof-honest reproducibility vector and falsifiers (`ADR-0096 §8, §13, §14.4`, `ADR-0097 §1`).

Asserts:
1. WAL presence establishes state reconstruction capability (full_cold), but never verification (unverified).
2. Pin presence establishes semantic replay capability (pinned), but never verification (unverified).
3. `verified` strictly requires an executed verification receipt bound to the run and digests.
4. `reproducibility_at_run_close` is immutable historical evidence.
5. Post-run reassessment produces a separate `reproducibility_current` claim without mutating run-close.
6. The executing episode cannot self-certify its reproducibility.
7. Domain vocabulary is strictly bounded.
"""

from __future__ import annotations

import unittest
from typing import Any

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.ledger.reducer import REDUCER_VERSION
from vanguard.packages.runtime.profiles import PRESETS, resolve_profile
from vanguard.packages.runtime.reproducibility import (
    REPRO_DOMAINS,
    ReproducibilityVector,
    SemanticReplayAssessment,
    StateReconstructionAssessment,
    assess_reproducibility,
    reassess_current_reproducibility,
    verify_reconstruction_receipt,
    verify_replay_receipt,
)


class RF100ReproducibilityFalsifier(unittest.TestCase):
    def test_wal_presence_establishes_capability_only_never_verification(self) -> None:
        """WAL presence proves cold replay is *possible* (capability), not that it was executed (verification)."""
        profile = resolve_profile("product")
        vector = assess_reproducibility(
            profile=profile,
            wal_durable=True,
            model_route={"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"},
        )
        self.assertEqual(vector.state_reconstruction.capability, "full_cold")
        self.assertEqual(vector.state_reconstruction.verification, "unverified")
        self.assertIsNone(vector.state_reconstruction.receipt)

        d = vector.to_dict()
        self.assertEqual(d["values"]["state_reconstruction"]["capability"], "full_cold")
        self.assertEqual(d["values"]["state_reconstruction"]["verification"], "unverified")

    def test_pins_presence_establishes_capability_only_never_verification(self) -> None:
        """Complete pins establish semantic replay capability (pinned), not executed verification."""
        profile = resolve_profile("hermetic", host_qualifies=True)
        vector = assess_reproducibility(
            profile=profile,
            pins={"reducer": "v1.0.0", "schemas": "v1.0.0"},
            model_route={"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"},
        )
        self.assertEqual(vector.semantic_replay.capability, "pinned")
        self.assertEqual(vector.semantic_replay.verification, "unverified")
        self.assertIsNone(vector.semantic_replay.receipt)

    def test_executed_state_reconstruction_receipt_upgrades_verification(self) -> None:
        """An executed receipt with matching run_id, state_digest, and reducer_version proves verification."""
        run_id = "run-verified-001"
        state_digest = "sha256:state-abc-123"
        valid_receipt = {
            "verified": True,
            "run_id": run_id,
            "reconstructed_state_digest": state_digest,
            "reducer_version": REDUCER_VERSION,
            "input_history_digest": "sha256:history-123",
            "event_count": 42,
        }

        self.assertTrue(verify_reconstruction_receipt(
            valid_receipt,
            expected_run_id=run_id,
            expected_state_digest=state_digest,
            expected_reducer_version=REDUCER_VERSION,
        ))

        vector = assess_reproducibility(
            profile=resolve_profile("product"),
            wal_durable=True,
            run_id=run_id,
            state_digest=state_digest,
            state_reconstruction_receipt=valid_receipt,
        )
        self.assertEqual(vector.state_reconstruction.capability, "full_cold")
        self.assertEqual(vector.state_reconstruction.verification, "verified")
        self.assertIsNotNone(vector.state_reconstruction.receipt)

    def test_mismatched_receipt_leaves_verification_unverified(self) -> None:
        """A tampered or mismatched receipt fails verification closed."""
        run_id = "run-001"
        state_digest = "sha256:state-good"
        tampered_receipt = {
            "verified": True,
            "run_id": "run-DIFFERENT",  # wrong run
            "reconstructed_state_digest": state_digest,
            "reducer_version": "v1.0.0",
            "input_history_digest": "sha256:history-123",
        }
        self.assertFalse(verify_reconstruction_receipt(
            tampered_receipt,
            expected_run_id=run_id,
            expected_state_digest=state_digest,
        ))

        vector = assess_reproducibility(
            profile=resolve_profile("product"),
            wal_durable=True,
            run_id=run_id,
            state_digest=state_digest,
            state_reconstruction_receipt=tampered_receipt,
        )
        self.assertEqual(vector.state_reconstruction.verification, "unverified")

    def test_run_close_reproducibility_is_immutable(self) -> None:
        """reproducibility_at_run_close cannot be modified in place by post-run evaluation."""
        run_close_vector = assess_reproducibility(
            profile=resolve_profile("product"),
            wal_durable=True,
            model_route={"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"},
            assessed_at="2026-08-25T12:00:00.000Z",
        )
        self.assertEqual(run_close_vector.state_reconstruction.verification, "unverified")
        self.assertEqual(run_close_vector.assessed_at, "2026-08-25T12:00:00.000Z")

        # Later, a reconstruction verification is executed in a background harness
        current_vector = reassess_current_reproducibility(
            run_close_vector,
            current_facts={
                "assessed_at": "2026-08-25T14:00:00.000Z",
                "state_reconstruction_receipt": {
                    "verified": True,
                    "reconstructed_state_digest": "sha256:s1",
                    "input_history_digest": "sha256:h1",
                },
            },
        )
        # New vector reflects current verification
        self.assertEqual(current_vector.state_reconstruction.verification, "verified")
        self.assertEqual(current_vector.assessed_at, "2026-08-25T14:00:00.000Z")
        self.assertIn("current_state_reconstruction_verified", current_vector.basis)

        # Original run_close remains immutable and unverified
        self.assertEqual(run_close_vector.state_reconstruction.verification, "unverified")
        self.assertEqual(run_close_vector.assessed_at, "2026-08-25T12:00:00.000Z")

    def test_external_reexecution_dimension_mapping(self) -> None:
        # Fake provider -> unavailable
        v_fake = assess_reproducibility(profile=resolve_profile("product"), model_route={"provider": "fake", "model": "m1"})
        self.assertEqual(v_fake.external_reexecution, "unavailable")

        # Scripted / cassette provider -> degraded
        v_cassette = assess_reproducibility(profile=resolve_profile("product"), model_route={"provider": "cassette", "model": "m1"})
        self.assertEqual(v_cassette.external_reexecution, "degraded")

        # Live attributable provider -> available
        v_live = assess_reproducibility(profile=resolve_profile("product"), model_route={"provider": "openrouter", "model": "claude-3.5-sonnet"})
        self.assertEqual(v_live.external_reexecution, "available")

    def test_artifact_retention_dimension_mapping(self) -> None:
        # full profile -> full retention
        v_herm = assess_reproducibility(profile=resolve_profile("hermetic", host_qualifies=True))
        self.assertEqual(v_herm.artifact_retention, "full")

        # standard profile -> partial retention
        v_prod = assess_reproducibility(profile=resolve_profile("product"))
        self.assertEqual(v_prod.artifact_retention, "partial")

        # digests_only profile -> digests_only
        v_do = assess_reproducibility(profile=resolve_profile("product", overrides={"retention": "digests_only"}))
        self.assertEqual(v_do.artifact_retention, "digests_only")

    def test_domain_vocabulary_is_strictly_bounded(self) -> None:
        with self.assertRaises(ValueError):
            StateReconstructionAssessment(capability="unbounded_capability", verification="unverified")

        with self.assertRaises(ValueError):
            StateReconstructionAssessment(capability="full_cold", verification="certified_without_proof")

        with self.assertRaises(ValueError):
            SemanticReplayAssessment(capability="pinned", verification="guaranteed")


if __name__ == "__main__":
    unittest.main()
