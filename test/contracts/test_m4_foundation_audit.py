"""Tests for M-4 Foundation Single-Run Evidence Audit Contract (`milestones.md § M-4`)."""

from __future__ import annotations

import unittest
from typing import Any

from vanguard.packages.domain.evidence import (
    REQUIRED_ROW_COUNT,
    audit_foundation_evidence,
)


def _valid_nine_rows(run_id: str = "run-foundation-001") -> list[dict[str, Any]]:
    return [
        {
            "row": 1,
            "run_id": run_id,
            "provider": "openrouter",
            "model": "anthropic/claude-3.5-sonnet",
            "fingerprint": "fp_claude35_prod",
            "measurement_status": "measured",
            "evidence_label": "live-openrouter",
            "prompt_tokens": 1200,
            "completion_tokens": 300,
            "total_tokens": 1500,
        },
        {
            "row": 2,
            "run_id": run_id,
            "decision": "authorized",
            "grant": {"descriptor": "grant:fs:read+patch:apply", "ceiling": "fs:/workspace"},
            "reservation": {"usd_micros": 5000, "millis": 1000},
            "request_matched": True,
            "point_of_effect_verified": True,
        },
        {
            "row": 3,
            "run_id": run_id,
            "before_digest": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
            "after_digest": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
            "patch_receipt": {"status": "applied", "path": "src/calc.py"},
        },
        {
            "row": 4,
            "run_id": run_id,
            "uid": 10001,
            "host_fallback": False,
            "evaluator_path_present": False,
            "isolation": "container",
            "mount_probe": True,
            "network_probe": True,
            "syscall_probe": True,
        },
        {
            "row": 5,
            "run_id": run_id,
            "verdict": "pass",
            "signature": "ed25519:abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
            "oracle_binding": "sha256:oracle_calc_v1",
            "signature_verified": True,
            "signer_key_id": "evaluator-key-1",
            "binding_digest": "sha256:verdict_binding_001",
        },
        {
            "row": 6,
            "run_id": run_id,
            "event_count": 42,
            "hash_chain_valid": True,
            "event_range": {"first": 0, "last": 41},
            "chain_digest": "sha256:wal_chain_001",
            "durable_intent_present": True,
            "wal_mode": "wal",
        },
        {
            "row": 7,
            "run_id": run_id,
            "reconstructed": True,
            "replayed_settled_effects": False,
            "fresh_process": True,
            "state_digest_matches": True,
        },
        {
            "row": 8,
            "run_id": run_id,
            "schema": "mhf.trajectory/1",
            "cost_conserved": True,
            "harness_digest": "sha256:harness_001",
            "state_digest": "sha256:state_001",
            "execution_digest": "sha256:exec_001",
            "turns_count": 3,
            "receipts": ["sha256:receipt_001"],
        },
        {
            "row": 9,
            "run_id": run_id,
            "runtime_path": "vanguard.packages.runtime.session",
            "layer0_used": False,
            "canonical_trace_verified": True,
            "alternate_runtime_detected": False,
        },
    ]


class TestM4FoundationEvidenceAudit(unittest.TestCase):
    def test_complete_valid_nine_rows_pass(self) -> None:
        rows = _valid_nine_rows()
        res = audit_foundation_evidence(rows)
        self.assertTrue(res.passed)
        self.assertEqual(res.evidence_state, "present_valid")
        self.assertTrue(res.promotion_eligible)
        self.assertFalse(res.unattributable_for_promotion)
        self.assertEqual(len(res.verified_rows), REQUIRED_ROW_COUNT)
        self.assertEqual(res.run_id, "run-foundation-001")

    def test_missing_any_row_fails(self) -> None:
        rows = _valid_nine_rows()
        rows.pop(4)  # Remove row 5 (exterior signed evaluation)
        res = audit_foundation_evidence(rows)
        self.assertFalse(res.passed)
        self.assertFalse(res.promotion_eligible)
        self.assertIn("missing_required_evidence_rows: [5]", res.rejection_reasons)

    def test_discontinuous_run_id_rejected(self) -> None:
        rows = _valid_nine_rows()
        rows[3]["run_id"] = "different-run-id"
        res = audit_foundation_evidence(rows)
        self.assertFalse(res.passed)
        self.assertFalse(res.promotion_eligible)
        self.assertTrue(any("discontinuous_run_id_lineage" in r for r in res.rejection_reasons))

    def test_fake_or_cassette_provider_rejected(self) -> None:
        rows = _valid_nine_rows()
        rows[0]["provider"] = "fake"
        res = audit_foundation_evidence(rows)
        self.assertFalse(res.passed)
        self.assertIn("row_1: fake_or_mock_model_provider_rejected", res.rejection_reasons)

    def test_lam_replay_evidence_label_rejected(self) -> None:
        rows = _valid_nine_rows()
        rows[0]["evidence_label"] = "lam-replay"
        res = audit_foundation_evidence(rows)
        self.assertFalse(res.passed)
        self.assertIn("row_1: forbidden_evidence_label: lam-replay", res.rejection_reasons)

    def test_unsigned_exterior_verdict_rejected(self) -> None:
        rows = _valid_nine_rows()
        rows[4]["signature"] = ""
        res = audit_foundation_evidence(rows)
        self.assertFalse(res.passed)
        self.assertIn("row_5: missing_or_unsigned_exterior_verdict", res.rejection_reasons)

    def test_host_execution_fallback_rejected(self) -> None:
        rows = _valid_nine_rows()
        rows[3]["host_fallback"] = True
        res = audit_foundation_evidence(rows)
        self.assertFalse(res.passed)
        self.assertIn("row_4: host_execution_fallback_rejected", res.rejection_reasons)

    def test_manual_repair_marker_rejected(self) -> None:
        rows = _valid_nine_rows()
        rows[2]["manual_repair"] = True
        res = audit_foundation_evidence(rows)
        self.assertFalse(res.passed)
        self.assertIn("row_3: manual_repair_detected", res.rejection_reasons)

    def test_stitched_trace_rejected(self) -> None:
        rows = _valid_nine_rows()
        rows[7]["stitched"] = True
        res = audit_foundation_evidence(rows)
        self.assertFalse(res.passed)
        self.assertIn("row_8: stitched_trace_detected", res.rejection_reasons)

    def test_layer0_runtime_breach_rejected(self) -> None:
        rows = _valid_nine_rows()
        rows[8]["layer0_used"] = True
        res = audit_foundation_evidence(rows)
        self.assertFalse(res.passed)
        self.assertIn("row_9: layer0_runtime_authority_breached", res.rejection_reasons)

    def test_promotable_input_flag_is_ignored(self) -> None:
        # Attacker injects promotable=True with missing rows
        bad_evidence = {
            "promotable": True,
            "promotion_eligible": True,
            "rows": [_valid_nine_rows()[0]],
        }
        res = audit_foundation_evidence(bad_evidence)
        self.assertFalse(res.passed)
        self.assertFalse(res.promotion_eligible)
        self.assertTrue(res.unattributable_for_promotion)

    def test_unverified_signature_string_is_rejected(self) -> None:
        rows = _valid_nine_rows()
        rows[4]["signature_verified"] = False
        res = audit_foundation_evidence(rows)
        self.assertFalse(res.passed)
        self.assertIn("row_5: exterior_signature_not_verified", res.rejection_reasons)

    def test_duplicate_row_is_rejected(self) -> None:
        rows = _valid_nine_rows()
        rows.append(dict(rows[0]))
        res = audit_foundation_evidence(rows)
        self.assertFalse(res.passed)
        self.assertIn("duplicate_evidence_rows: [1]", res.rejection_reasons)


if __name__ == "__main__":
    unittest.main()
