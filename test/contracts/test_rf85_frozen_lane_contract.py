"""RED lock for the two independent RF-85 implementation lanes.

These tests specify M-4 preparation interfaces.  Synthetic values here are
contract fixtures only and are permanently ineligible as RF-85 evidence.
"""

from __future__ import annotations

from dataclasses import replace
import unittest

from vanguard.packages.domain.evidence import (
    absent,
    audit_foundation_evidence,
    build_foundation_evidence,
)


LINEAGE = {
    "project_id": "project-contract",
    "run_id": "run-contract",
    "episode_id": "episode-contract",
    "composition_digest": "sha256:dh",
    "activation_digest": "sha256:da",
    "run_digest": "sha256:dr",
}


class TestRF85FrozenWireContract(unittest.TestCase):
    def test_bundle_binds_immutable_task_oracle_preregistration(self) -> None:
        bundle = build_foundation_evidence(
            lineage=LINEAGE,
            task_digest="sha256:task",
            oracle="oracle-v1",
            preregistration_digest="sha256:prereg",
            event_range={"first_seq": 1, "last_seq": 1, "count": 1},
            terminal_chain_digest="sha256:chain",
            rows=[],
        )
        self.assertEqual(bundle.header()["preregistration_digest"], "sha256:prereg")

    def test_absent_is_distinct_from_invalid_and_unverifiable(self) -> None:
        rows = [absent(number, "canonical source did not exist before run")
                for number in range(1, 10)]
        result = audit_foundation_evidence([row.identity() for row in rows])
        self.assertEqual(result.evidence_state, "absent")
        self.assertFalse(result.passed)

        invalid = [dict(row.identity()) for row in rows]
        invalid[0] = {**invalid[0], "status": "derived", "source": {}}
        self.assertEqual(
            audit_foundation_evidence(invalid).evidence_state, "invalid")

        # A derived exterior verdict without the verifier is well-shaped but
        # cannot be established in this audit environment.
        unverifiable = [dict(row.identity()) for row in rows]
        unverifiable[4] = {
            "number": 5, "name": "exterior_signed_evaluation",
            "status": "derived", "source_digest": "sha256:unavailable",
            "source": {"run_id": "run-contract", "signature": "opaque"},
            "observation": {"run_id": "run-contract", "signature": "opaque"},
            "absence_reason": "",
        }
        self.assertEqual(
            audit_foundation_evidence(unverifiable).evidence_state, "unverifiable")

    def test_run_lineage_contract_includes_every_join_key(self) -> None:
        required = {
            "project_id", "run_id", "episode_id", "composition_digest",
            "activation_digest", "run_digest",
        }
        self.assertEqual(set(LINEAGE), required)


if __name__ == "__main__":
    unittest.main()
