#!/usr/bin/env python3
"""Observe the M-8 memory, promotion and rollback falsifiers in a fresh process.

M-8's predicate is `durable_memory_and_signed_rollback_verified`. That is two
claims, and this report keeps them separable: durable authorized memory on one
side, signed promotion with an *executed* rollback on the other.

The suites span `falsifiers/`, `security/`, `adapters/` and `runtime/` because
M-8's invariants do: authorization before ranking is a security property, CAS
durability is an adapter property, and authority separation is a governance
property. Reporting only the falsifier directory would understate what the
milestone actually rests on.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from falsifier_proof import ROOT, emit, run_suite  # noqa: E402

MODULES = (
    "test.falsifiers.test_m8_skill_lifecycle",
    "test.security.test_m8_memory_falsifiers",
    "test.security.test_m8_memory_fake_parity",
    "test.adapters.test_durable_memory_port",
    "test.runtime.test_governed_learning",
)

#: One marker per property M-8's predicate actually rests on. Naming the suite
#: class alone would let a whole behaviour be deleted from inside a class that
#: still runs, so the load-bearing ones name individual tests.
MARKERS = {
    # -- authority separation: no self-promotion --------------------------
    "authorities_distinct": "TheThreeAuthoritiesStayDistinct",
    "promoter_is_not_generator": "test_a_promoter_that_is_also_the_generator_is_refused",
    "promoter_is_not_evaluator": "test_a_promoter_that_is_also_the_evaluator_is_refused",
    "generator_is_not_evaluator": "test_a_generator_that_is_also_the_evaluator_is_refused",
    "evaluator_holds_no_key": "test_the_evaluator_holds_no_signing_key",

    # -- durable authorized memory ----------------------------------------
    "authorization_before_ranking": "test_unauthorized_recall_never_reaches_the_ranker",
    "ranker_sees_only_authorized": "test_ranker_receives_only_authorized_candidates",
    "isolation_enforced": "test_cross_tenant_project_and_category_are_denied",
    "expiry_and_revocation": "test_expired_and_revoked_grants_fail_at_use_time",
    "provenance_required": "test_context_rejects_missing_or_mismatched_provenance",
    "no_fail_open_grant": "test_fake_nonempty_grant_fails_closed",
    "fake_parity_no_fail_open": "test_a_grant_in_name_only_is_refused",
    "denial_precedes_shape": "test_denial_precedes_query_shape_reporting",

    # -- durability, backup/restore, corruption recovery -------------------
    "backup_restore_verified": "test_backup_restore_verifies_checksum_and_survives_new_process",
    "restart_recovery": "test_restart_recovery_and_deterministic_index",
    "corruption_quarantined": "test_causal_notification_failure_quarantines_record",
    "legal_hold_protects_gc": "test_legal_hold_and_quarantine_interval_protect_gc",

    # -- held-out evaluation ----------------------------------------------
    "held_out_is_real": "HeldOutEvidenceMustBeReal",
    "presence_is_not_use": "PresenceIsNotUseAndUseIsNotGrounding",
    "contaminated_split_refused": "test_a_held_out_task_contaminated_by_the_dev_split_is_refused",
    "thresholds_not_disableable": "test_measurement_thresholds_cannot_be_disabled",

    # -- signed promotion, CAS, replay protection --------------------------
    "promotion_binds_decision": "PromotionEvidenceBindsWhatWasDecided",
    "promotion_signature_verified": "test_another_key_does_not_verify_the_promotion",
    "promotion_needs_verifier": "test_promotion_without_a_verifier_fails_closed",
    "cas_conflict_handled": "test_cas_conflict_handling_on_concurrent_promotion",
    "stale_base_refused": "test_promotion_on_a_stale_base_version_is_refused",

    # -- signed rollback, executed ----------------------------------------
    "rollback_executed": "RollbackIsExecutableNotDocumented",
    "rollback_restores_behaviour": "test_an_injected_regression_is_caught_and_the_rollback_restores_behaviour",
    "unsigned_rollback_refused": "test_an_unsigned_rollback_is_refused_outright",
    "forged_rollback_refused": "test_a_forged_rollback_signature_cannot_move_the_served_version",
    "rollback_replay_refused": "test_rollback_evidence_cannot_be_replayed_against_a_moved_head",
    "restore_in_fresh_process": "test_restore_restores_previous_behavior_in_a_fresh_process",

    # -- invariants --------------------------------------------------------
    "reproducibility_recomputed": "ReproducibilityIsRecomputedAfterPromotion",
    "no_premature_event_kinds": "NoLifecycleEventKindIsIntroducedBeforeADR0100",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = run_suite(
        args.root.resolve(), MODULES,
        schema="aether.m8-falsifier-report/1", markers=MARKERS,
    )
    return emit(report, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
