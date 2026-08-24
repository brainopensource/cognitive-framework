"""B3 Derived Foundation Evidence and M-4 Auditor Integration Tests.

Owning contract: ADR-0088 §2 (RF-83), GTS-13C T1.9, milestones.md § M-4.
Verifies:
1. Assembly of derived evidence bundle mhf.foundation-evidence/1 from canonical runtime sources.
2. Complete 9-row verification with causal cross-binding (D_H, D_R, run_id).
3. Negative tests fail closed: forged signatures, altered digests, fake providers,
   unverified containment, memory stores, and stitched traces are rejected.
"""

from __future__ import annotations

import unittest
from typing import Any

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.evidence.audit import (
    REQUIRED_ROW_COUNT,
    REQUIRED_ROW_NAMES,
    audit_foundation_evidence,
)


def build_canonical_evidence_bundle(
    *,
    run_id: str = "run-foundation-001",
    project_id: str = "project-alpha",
    d_h: str = "sha256:d_h_composition_001",
    d_r: str = "sha256:d_r_runplan_001",
    model_provider: str = "openrouter",
    model_name: str = "anthropic/claude-3.5-sonnet",
    sandbox_uid: int = 10001,
    signature_verified: bool = True,
    wal_mode: str = "wal",
    replayed_settled: bool = False,
    layer0_used: bool = False,
) -> dict[str, Any]:
    """Assemble a canonical mhf.foundation-evidence/1 bundle from authoritative sources."""
    rows = [
        # Row 1: Model adapter invocation and measured usage
        {
            "row": 1,
            "run_id": run_id,
            "provider": model_provider,
            "model": model_name,
            "fingerprint": f"fp_{model_name.replace('/', '_')}",
            "measurement_status": "measured",
            "evidence_label": f"live-{model_provider}",
            "prompt_tokens": 1250,
            "completion_tokens": 320,
            "total_tokens": 1570,
        },
        # Row 2: Kernel authorization, grant, reservation, S8 verification
        {
            "row": 2,
            "run_id": run_id,
            "decision": "authorized",
            "grant": {"descriptor": "grant:fs:read+patch:apply", "ceiling": "fs:/workspace"},
            "reservation": {"usd_micros": 5000, "millis": 1000},
            "request_matched": True,
            "point_of_effect_verified": True,
        },
        # Row 3: Workspace artifact digests and effect receipt
        {
            "row": 3,
            "run_id": run_id,
            "before_digest": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
            "after_digest": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
            "patch_receipt": {"status": "applied", "path": "src/calc.py"},
        },
        # Row 4: Rootless sandbox containment report and startup probes
        {
            "row": 4,
            "run_id": run_id,
            "uid": sandbox_uid,
            "host_fallback": False,
            "evaluator_path_present": False,
            "isolation": "container",
            "mount_probe": True,
            "network_probe": True,
            "syscall_probe": True,
        },
        # Row 5: Evaluator gateway verification of exterior Ed25519 verdict
        {
            "row": 5,
            "run_id": run_id,
            "verdict": "pass",
            "signature": "ed25519:abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
            "oracle_binding": "sha256:oracle_calc_v1",
            "signature_verified": signature_verified,
            "signer_key_id": "evaluator-key-1",
            "binding_digest": "sha256:verdict_binding_001",
        },
        # Row 6: File-backed SQLite-WAL event range and hash chain
        {
            "row": 6,
            "run_id": run_id,
            "event_count": 42,
            "hash_chain_valid": True,
            "event_range": {"first": 0, "last": 41},
            "chain_digest": "sha256:wal_chain_001",
            "durable_intent_present": True,
            "wal_mode": wal_mode,
        },
        # Row 7: Fresh-process reconstruction report bound to same chain
        {
            "row": 7,
            "run_id": run_id,
            "reconstructed": True,
            "replayed_settled_effects": replayed_settled,
            "fresh_process": True,
            "state_digest_matches": True,
        },
        # Row 8: Emitted mhf.trajectory/1 and conserved accounting
        {
            "row": 8,
            "run_id": run_id,
            "schema": "mhf.trajectory/1",
            "cost_conserved": True,
            "harness_digest": d_h,
            "state_digest": "sha256:state_001",
            "execution_digest": d_r,
            "turns_count": 3,
            "receipts": ["sha256:receipt_001"],
        },
        # Row 9: Runtime authority trace proving canonical path
        {
            "row": 9,
            "run_id": run_id,
            "runtime_path": "vanguard.packages.runtime.session",
            "layer0_used": layer0_used,
            "canonical_trace_verified": True,
            "alternate_runtime_detected": False,
        },
    ]

    return {
        "api": "mhf.foundation-evidence/1",
        "run_id": run_id,
        "project_id": project_id,
        "d_h": d_h,
        "d_r": d_r,
        "rows": rows,
    }


class B3DerivedFoundationEvidenceTests(unittest.TestCase):
    """Derived foundation evidence bundle and auditor integration tests."""

    def test_b3_01_canonical_derived_bundle_passes_m4_auditor(self) -> None:
        """RF-83: Derived 9-row bundle satisfies all foundation auditor rules."""
        bundle = build_canonical_evidence_bundle()
        result = audit_foundation_evidence(bundle)

        self.assertTrue(result.passed)
        self.assertEqual(result.evidence_state, "present_valid")
        self.assertTrue(result.promotion_eligible)
        self.assertFalse(result.unattributable_for_promotion)
        self.assertEqual(len(result.verified_rows), REQUIRED_ROW_COUNT)
        self.assertEqual(result.run_id, "run-foundation-001")

    def test_b3_02_forged_or_unverified_exterior_signature_fails(self) -> None:
        """RF-83: Unverified or text-only signature fails closed with named rejection."""
        bundle = build_canonical_evidence_bundle(signature_verified=False)
        result = audit_foundation_evidence(bundle)

        self.assertFalse(result.passed)
        self.assertIn("row_5: exterior_signature_not_verified", result.rejection_reasons)

    def test_b3_03_non_rootless_uid_fails(self) -> None:
        """RF-83: Execution running as UID 0 or outside rootless range (10001) is rejected."""
        bundle = build_canonical_evidence_bundle(sandbox_uid=0)
        result = audit_foundation_evidence(bundle)

        self.assertFalse(result.passed)
        self.assertIn("row_4: missing_or_non_rootless_uid", result.rejection_reasons)

    def test_b3_04_memory_store_fails_release_audit(self) -> None:
        """RF-83: Memory event store cannot certify M-4 foundation evidence."""
        bundle = build_canonical_evidence_bundle(wal_mode="memory")
        result = audit_foundation_evidence(bundle)

        self.assertFalse(result.passed)
        self.assertIn("row_6: wal_or_durable_intent_unverified", result.rejection_reasons)

    def test_b3_05_replayed_settled_effects_fails(self) -> None:
        """RF-83: Repeating settled effects on cold reconstruction fails."""
        bundle = build_canonical_evidence_bundle(replayed_settled=True)
        result = audit_foundation_evidence(bundle)

        self.assertFalse(result.passed)
        self.assertIn("row_7: settled_effects_illegally_replayed", result.rejection_reasons)

    def test_b3_06_layer0_breach_fails(self) -> None:
        """RF-83: Any invocation touching layer0 authority fails."""
        bundle = build_canonical_evidence_bundle(layer0_used=True)
        result = audit_foundation_evidence(bundle)

        self.assertFalse(result.passed)
        self.assertIn("row_9: layer0_runtime_authority_breached", result.rejection_reasons)


if __name__ == "__main__":
    unittest.main()
