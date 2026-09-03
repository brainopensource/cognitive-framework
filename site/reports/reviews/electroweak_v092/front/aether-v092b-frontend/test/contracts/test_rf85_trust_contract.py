"""RF-85 trust-lane negatives; all values are ineligible synthetic fixtures."""

from __future__ import annotations

import unittest

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.evidence import (
    Preregistration,
    absent,
    audit_foundation_evidence,
    build_foundation_evidence,
)


LINEAGE = {
    "project_id": "project-fixture",
    "run_id": "run-fixture",
    "episode_id": "episode-fixture",
    "composition_digest": "sha256:dh",
    "activation_digest": "sha256:da",
    "run_digest": "sha256:dr",
}


class TestRF85TrustContract(unittest.TestCase):
    def test_preregistration_digest_binds_every_trust_input(self) -> None:
        prereg = Preregistration(
            task_digest="sha256:task", oracle_id="oracle-v1",
            oracle_digest="sha256:oracle", evaluator_key_id="key-v1",
            evaluator_public_key="base64-public-key", protocol="pytest-v1",
            subject_digest="sha256:subject", created_at="2026-08-24T00:00:00Z",
        )
        changed = Preregistration(
            task_digest="sha256:task", oracle_id="oracle-v1",
            oracle_digest="sha256:changed", evaluator_key_id="key-v1",
            evaluator_public_key="base64-public-key", protocol="pytest-v1",
            subject_digest="sha256:subject", created_at="2026-08-24T00:00:00Z",
        )
        self.assertNotEqual(prereg.digest, changed.digest)
        self.assertEqual(prereg.to_wire()["preregistration_digest"], prereg.digest)

    def test_bundle_digest_tampering_is_invalid(self) -> None:
        bundle = build_foundation_evidence(
            lineage=LINEAGE, task_digest="sha256:task", oracle="oracle-v1",
            preregistration_digest="sha256:prereg",
            event_range={"first_seq": 1, "last_seq": 1, "count": 1},
            terminal_chain_digest="sha256:chain", rows=[],
        ).to_wire()
        tampered = {**bundle, "bundle_digest": "sha256:tampered"}
        result = audit_foundation_evidence(tampered)
        self.assertEqual(result.evidence_state, "invalid")
        self.assertIn("bundle_digest_mismatch", result.rejection_reasons)

    def test_canonical_bundle_without_preregistration_source_is_unverifiable(self) -> None:
        bundle = build_foundation_evidence(
            lineage=LINEAGE, task_digest="sha256:task", oracle="oracle-v1",
            preregistration_digest="sha256:prereg",
            event_range={"first_seq": 1, "last_seq": 1, "count": 1},
            terminal_chain_digest="sha256:chain", rows=[],
        ).to_wire()
        result = audit_foundation_evidence(bundle)
        self.assertEqual(result.evidence_state, "unverifiable")
        self.assertFalse(result.promotion_eligible)

    def test_mixed_lineage_is_invalid(self) -> None:
        source = {
            **LINEAGE, "preregistration_digest": "sha256:prereg",
            "run_id": "other-run", "invocation_id": "invocation-1",
            "provider": "openrouter", "model": "model", "fingerprint": "fp",
            "measurement_status": "measured", "prompt_tokens": 1,
            "completion_tokens": 1, "total_tokens": 2,
        }
        row = {
            "number": 1, "name": "real_model_invocation", "status": "derived",
            "source": source, "observation": source,
            "source_digest": digest_of(source), "absence_reason": "",
        }
        rows = [row] + [dict(absent(n, "fixture source absent").identity())
                        for n in range(2, 10)]
        result = audit_foundation_evidence(
            rows, expected_run_id=LINEAGE["run_id"],
            expected_lineage={**LINEAGE, "preregistration_digest": "sha256:prereg"},
        )
        self.assertEqual(result.evidence_state, "invalid")
        self.assertIn("row_1: run_id_lineage_mismatch", result.rejection_reasons)

    def test_self_attested_boolean_is_not_a_derived_row(self) -> None:
        rows = [{"number": 4, "name": "rootless_sandbox", "passed": True}]
        result = audit_foundation_evidence(rows)
        self.assertEqual(result.evidence_state, "invalid")
        self.assertIn("row_4: asserted_evidence_rejected", result.rejection_reasons)


if __name__ == "__main__":
    unittest.main()
