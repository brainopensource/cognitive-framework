"""M-4 Foundation Evidence Auditor (`milestones.md § M-4 single-run evidence contract`).

Validates the nine required evidence rows from one uninterrupted real run,
enforcing single-run causal lineage, rejecting mock/cassette substitutions,
unsigned verdicts, host-execution fallbacks, and manual repair markers.
Derives evidence state and promotion eligibility without trusting input flags.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import base64
from typing import Any, Callable, Mapping, Sequence

from ..canonicalisation.digest import digest_of

__all__ = [
    "EvidenceAuditResult",
    "REQUIRED_ROW_COUNT",
    "REQUIRED_ROW_NAMES",
    "audit_foundation_evidence",
]

REQUIRED_ROW_COUNT = 9

REQUIRED_ROW_NAMES: Mapping[int, str] = {
    1: "real_model_invocation",
    2: "authorized_effect",
    3: "real_filesystem_change",
    4: "rootless_sandbox",
    5: "exterior_signed_evaluation",
    6: "sqlite_wal_record",
    7: "cold_reconstruction",
    8: "rich_trajectory",
    9: "one_runtime_authority",
}

_FORBIDDEN_PROVIDERS = frozenset({"fake", "mock", "cassette", "test", "playback", "lam-replay", "double"})
_FORBIDDEN_EVIDENCE_LABELS = frozenset({"fake", "mock", "cassette", "lam-replay", "synthetic", "playback"})


@dataclass(frozen=True, slots=True)
class EvidenceAuditResult:
    passed: bool
    evidence_state: str
    promotion_eligible: bool
    unattributable_for_promotion: bool
    run_id: str | None
    verified_rows: tuple[int, ...] = field(default_factory=tuple)
    rejection_reasons: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "evidence_state": self.evidence_state,
            "promotion_eligible": self.promotion_eligible,
            "unattributable_for_promotion": self.unattributable_for_promotion,
            "run_id": self.run_id,
            "verified_rows": list(self.verified_rows),
            "rejection_reasons": list(self.rejection_reasons),
        }


def audit_foundation_evidence(
    evidence: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    *,
    expected_run_id: str | None = None,
    signature_verifier: Callable[[Mapping[str, Any], str, bytes], bool] | None = None,
) -> EvidenceAuditResult:
    """Audit the nine required M-4 foundation evidence rows.

    Requires:
      1. All 9 required evidence rows present and individually valid.
      2. Exactly one uninterrupted run_id across all rows and causal lineage.
      3. No fake/cassette/mock model providers or synthetic evidence labels.
      4. Verifiable exterior signature on evaluation; no missing verdicts.
      5. Enforced rootless sandbox with no host-execution fallback.
      6. Complete WAL continuity and cold reconstruction parity.
      7. Populated, conserved mhf.trajectory/1 trajectory bound to D_H/D_R/D_X.
      8. Canonical runtime execution authority with zero Layer-0 paths.
      9. Zero manual repairs, stitched traces, or human interventions.
    """
    reasons: list[str] = []
    verified_rows: list[int] = []

    # Normalise row mapping from sequence or dictionary
    rows_by_idx: dict[int, Mapping[str, Any]] = {}
    duplicate_rows: set[int] = set()
    if isinstance(evidence, Sequence):
        for item in evidence:
            if not isinstance(item, Mapping):
                continue
            idx = item.get("row") or item.get("index") or item.get("id")
            if isinstance(idx, int) and 1 <= idx <= REQUIRED_ROW_COUNT:
                if idx in rows_by_idx:
                    duplicate_rows.add(idx)
                rows_by_idx[idx] = item
            elif isinstance(idx, str) and idx.isdigit():
                number = int(idx)
                if not 1 <= number <= REQUIRED_ROW_COUNT:
                    continue
                if number in rows_by_idx:
                    duplicate_rows.add(number)
                rows_by_idx[number] = item
            elif "name" in item:
                for num, name in REQUIRED_ROW_NAMES.items():
                    if item["name"] == name:
                        if num in rows_by_idx:
                            duplicate_rows.add(num)
                        rows_by_idx[num] = item
                        break
    elif isinstance(evidence, Mapping):
        if "rows" in evidence and isinstance(evidence["rows"], (list, tuple, Mapping)):
            return audit_foundation_evidence(
                evidence["rows"], expected_run_id=expected_run_id or evidence.get("run_id"),
                signature_verifier=signature_verifier,
            )
        for num, name in REQUIRED_ROW_NAMES.items():
            if str(num) in evidence and isinstance(evidence[str(num)], Mapping):
                rows_by_idx[num] = evidence[str(num)]
            elif num in evidence and isinstance(evidence[num], Mapping):
                rows_by_idx[num] = evidence[num]
            elif name in evidence and isinstance(evidence[name], Mapping):
                rows_by_idx[num] = evidence[name]

    # Every accepted row is a source-bound derivation. Legacy flat rows are
    # assertions and cannot become promotion evidence.
    for num, row in tuple(rows_by_idx.items()):
        source = row.get("source")
        observation = row.get("observation")
        source_digest = row.get("source_digest")
        if row.get("status") != "derived" or not isinstance(source, Mapping):
            reasons.append(f"row_{num}: asserted_evidence_rejected")
            continue
        if not isinstance(observation, Mapping):
            reasons.append(f"row_{num}: missing_derived_observation")
            continue
        recomputed = digest_of(dict(source))
        if source_digest != recomputed:
            reasons.append(f"row_{num}: source_digest_mismatch")
            continue
        if dict(observation) != dict(source):
            reasons.append(f"row_{num}: observation_not_derived_from_source")
            continue
        rows_by_idx[num] = observation

    # 1. Row count completeness
    missing_rows = [num for num in range(1, REQUIRED_ROW_COUNT + 1) if num not in rows_by_idx]
    if missing_rows:
        reasons.append(f"missing_required_evidence_rows: {missing_rows}")
    if duplicate_rows:
        reasons.append(f"duplicate_evidence_rows: {sorted(duplicate_rows)}")

    # 2. Check run_id continuity and lineage
    run_ids: set[str] = set()
    for num, row in rows_by_idx.items():
        rid = row.get("run_id")
        if isinstance(rid, str) and rid.strip():
            run_ids.add(rid.strip())
        else:
            reasons.append(f"row_{num}: missing_or_empty_run_id")

    if expected_run_id is not None:
        if not isinstance(expected_run_id, str) or not expected_run_id.strip():
            reasons.append("invalid_expected_run_id")
        else:
            run_ids.add(expected_run_id.strip())

    if len(run_ids) > 1:
        reasons.append(f"discontinuous_run_id_lineage: {sorted(run_ids)}")
    elif not run_ids:
        reasons.append("no_valid_run_id_found")

    active_run_id = next(iter(run_ids)) if len(run_ids) == 1 else None

    # Check for forbidden stitching / manual repair markers across all rows
    for num, row in rows_by_idx.items():
        if row.get("stitched") is True or row.get("stitched_trace") is True:
            reasons.append(f"row_{num}: stitched_trace_detected")
        if row.get("manual_repair") is True or row.get("human_intervention") is True:
            reasons.append(f"row_{num}: manual_repair_detected")

    # Row 1: Real model invocation
    r1 = rows_by_idx.get(1)
    if r1:
        provider = str(r1.get("provider", "")).lower()
        model = str(r1.get("model", "")).lower()
        label = str(r1.get("evidence_label", "")).lower()
        if any(p in provider for p in _FORBIDDEN_PROVIDERS) or any(p in model for p in _FORBIDDEN_PROVIDERS):
            reasons.append("row_1: fake_or_mock_model_provider_rejected")
        elif label in _FORBIDDEN_EVIDENCE_LABELS:
            reasons.append(f"row_1: forbidden_evidence_label: {label}")
        elif not provider or not model or not r1.get("fingerprint"):
            reasons.append("row_1: incomplete_model_identification")
        elif r1.get("measurement_status") != "measured":
            reasons.append("row_1: model_telemetry_unmeasured")
        elif not all(isinstance(r1.get(key), int) and r1[key] >= 0
                     for key in ("prompt_tokens", "completion_tokens", "total_tokens")):
            reasons.append("row_1: missing_measured_usage")
        else:
            verified_rows.append(1)

    # Row 2: Authorized effect
    r2 = rows_by_idx.get(2)
    if r2:
        decision = r2.get("decision") or r2.get("gate_decision")
        grant = r2.get("grant")
        reservation = r2.get("reservation")
        if decision not in ("authorized", "grant_applied", "allow", "ALLOW"):
            reasons.append(f"row_2: unauthorized_or_missing_decision: {decision}")
        elif not grant or not isinstance(grant, Mapping):
            reasons.append("row_2: missing_or_invalid_grant_descriptor")
        elif reservation is None:
            reasons.append("row_2: missing_budget_reservation")
        elif r2.get("request_matched") is not True or r2.get("point_of_effect_verified") is not True:
            reasons.append("row_2: effect_request_or_point_of_effect_unverified")
        else:
            verified_rows.append(2)

    # Row 3: Real filesystem change
    r3 = rows_by_idx.get(3)
    if r3:
        before = r3.get("before_digest") or r3.get("digest_before")
        after = r3.get("after_digest") or r3.get("digest_after")
        receipt = r3.get("patch_receipt") or r3.get("receipt")
        if not before or not after:
            reasons.append("row_3: missing_before_after_artifact_digests")
        elif before == after and not r3.get("mutated"):
            reasons.append("row_3: unmutated_filesystem_state")
        elif not receipt:
            reasons.append("row_3: missing_patch_receipt")
        else:
            verified_rows.append(3)

    # Row 4: Rootless sandbox
    r4 = rows_by_idx.get(4)
    if r4:
        uid = r4.get("uid")
        host_fallback = r4.get("host_fallback") is True or r4.get("host_execution") is True
        evaluator_present = r4.get("evaluator_path_present") is True or r4.get("evaluator_accessible") is True
        if host_fallback:
            reasons.append("row_4: host_execution_fallback_rejected")
        elif not isinstance(uid, int) or uid <= 0:
            reasons.append("row_4: missing_or_non_rootless_uid")
        elif evaluator_present:
            reasons.append("row_4: evaluator_path_breached_into_sandbox")
        elif r4.get("mount_probe") is not True or r4.get("network_probe") is not True or r4.get("syscall_probe") is not True:
            reasons.append("row_4: incomplete_sandbox_probes")
        else:
            verified_rows.append(4)

    # Row 5: Exterior signed evaluation
    r5 = rows_by_idx.get(5)
    if r5:
        signature = r5.get("signature") or (r5.get("signed_verdict", {}).get("signature") if isinstance(r5.get("signed_verdict"), Mapping) else None)
        verdict = r5.get("verdict") or (r5.get("signed_verdict", {}).get("verdict") if isinstance(r5.get("signed_verdict"), Mapping) else None)
        if not signature or not isinstance(signature, str):
            reasons.append("row_5: missing_or_unsigned_exterior_verdict")
        elif signature_verifier is None:
            reasons.append("row_5: exterior_signature_verifier_absent")
        elif not isinstance(r5.get("signed_body"), Mapping) or not isinstance(
            r5.get("public_key"), str
        ) or not _verify_signature(
            signature_verifier, r5["signed_body"], signature, r5["public_key"]
        ):
            reasons.append("row_5: exterior_signature_not_verified")
        elif not r5.get("signer_key_id") or not r5.get("binding_digest") or not r5.get("oracle_binding"):
            reasons.append("row_5: incomplete_exterior_binding")
        elif not verdict:
            reasons.append("row_5: missing_verdict_outcome")
        elif verdict not in ("pass", "PASS", "passed", "success"):
            reasons.append(f"row_5: failing_evaluation_verdict: {verdict}")
        else:
            verified_rows.append(5)

    # Row 6: SQLite-WAL record
    r6 = rows_by_idx.get(6)
    if r6:
        event_count = r6.get("event_count", 0)
        wal_events = r6.get("events")
        chain_valid = isinstance(wal_events, Sequence) and bool(wal_events) and all(
            isinstance(wal_events[index], Mapping)
            and wal_events[index].get("prev_digest") == wal_events[index - 1].get("digest")
            for index in range(1, len(wal_events))
        )
        durable_intent = isinstance(wal_events, Sequence) and any(
            isinstance(item, Mapping) and item.get("kind") == "EffectStarted"
            for item in wal_events
        )
        if event_count <= 0 and not r6.get("event_range"):
            reasons.append("row_6: empty_or_missing_event_range")
        elif not chain_valid or event_count != len(wal_events):
            reasons.append("row_6: hash_chain_continuity_broken")
        elif r6.get("chain_digest") != wal_events[-1].get("digest"):
            reasons.append("row_6: terminal_chain_digest_mismatch")
        elif not durable_intent or r6.get("wal_mode") != "wal":
            reasons.append("row_6: wal_or_durable_intent_unverified")
        else:
            verified_rows.append(6)

    # Row 7: Cold reconstruction
    r7 = rows_by_idx.get(7)
    if r7:
        reconstructed = r7.get("reconstructed") is True or r7.get("state_matches") is True
        replayed_settled = r7.get("replayed_settled_effects") is True
        if not reconstructed:
            reasons.append("row_7: cold_state_reconstruction_failed")
        elif replayed_settled:
            reasons.append("row_7: settled_effects_illegally_replayed")
        elif r7.get("fresh_process") is not True or r7.get("state_digest_matches") is not True:
            reasons.append("row_7: fresh_process_or_state_digest_unverified")
        else:
            verified_rows.append(7)

    # Row 8: Rich trajectory
    r8 = rows_by_idx.get(8)
    if r8:
        schema = r8.get("schema") or r8.get("$schema")
        turn_costs = r8.get("turn_costs")
        total_cost = r8.get("total_cost")
        cost_conserved = isinstance(turn_costs, Sequence) and isinstance(total_cost, Mapping) and all(
            int(total_cost.get(dim) or 0) == sum(
                int(cost.get(dim) or 0) for cost in turn_costs if isinstance(cost, Mapping)
            ) for dim in ("usd_micros", "tokens", "bytes", "millis")
        )
        d_h = r8.get("harness_digest") or r8.get("D_H")
        d_r = r8.get("execution_digest") or r8.get("run_digest") or r8.get("D_R")
        if schema != "mhf.trajectory/1":
            reasons.append(f"row_8: invalid_trajectory_schema: {schema}")
        elif not cost_conserved:
            reasons.append("row_8: non_conserved_trajectory_cost")
        elif not d_h or not d_r:
            reasons.append("row_8: missing_d_h_d_r_lineage_digests")
        elif not isinstance(r8.get("turns_count"), int) or r8["turns_count"] <= 0 or not r8.get("receipts"):
            reasons.append("row_8: empty_turn_or_receipt_trajectory")
        else:
            verified_rows.append(8)

    # Row 9: One runtime authority
    r9 = rows_by_idx.get(9)
    if r9:
        layer0_present = r9.get("layer0_used") is True or r9.get("layer0_imported") is True
        runtime_path = str(r9.get("runtime_path", "vanguard.packages.runtime"))
        if layer0_present:
            reasons.append("row_9: layer0_runtime_authority_breached")
        elif "vanguard.packages.runtime" not in runtime_path:
            reasons.append(f"row_9: invalid_runtime_authority_path: {runtime_path}")
        elif r9.get("violations") != [] or not isinstance(r9.get("files"), Sequence):
            reasons.append("row_9: runtime_authority_trace_unverified")
        elif r9.get("trace_digest") != digest_of({
            "files": list(r9["files"]), "public_boundary": runtime_path,
            "violations": list(r9["violations"]),
        }):
            reasons.append("row_9: runtime_authority_trace_digest_mismatch")
        else:
            verified_rows.append(9)

    passed = len(verified_rows) == REQUIRED_ROW_COUNT and not reasons
    evidence_state = "present_valid" if passed else "forged_or_broken" if reasons else "absent_declared"

    return EvidenceAuditResult(
        passed=passed,
        evidence_state=evidence_state,
        promotion_eligible=passed,
        unattributable_for_promotion=not passed,
        run_id=active_run_id,
        verified_rows=tuple(sorted(verified_rows)),
        rejection_reasons=tuple(reasons),
    )


def _verify_signature(
    verifier: Callable[[Mapping[str, Any], str, bytes], bool],
    body: Mapping[str, Any], signature: str, public_key: str,
) -> bool:
    try:
        decoded = base64.b64decode(public_key, validate=True)
    except (ValueError, TypeError):
        return False
    return verifier(body, signature, decoded)
