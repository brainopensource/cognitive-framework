#!/usr/bin/env python3
"""Observe the M-7 topology and independence falsifiers in a fresh process.

M-7's predicate is `three_topologies_verified AND adr_0099_disposition_verified`
(`docs/03_execution/sprint_active.md`). The markers below are the two halves of
that predicate, plus the fail-closed rejections that make "verified" mean
something: a topology language that accepted cycles, dangling artifacts or
embedded authority would lower three names for one structure.

`m701_live_path` is the honest discriminator between M7-01 measured on the real
canonical path and M7-01 measured over library fixtures. The milestone requires
the former.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from falsifier_proof import ROOT, emit, run_suite  # noqa: E402

MODULES = (
    "test.falsifiers.test_m7_topology_and_independence",
    "test.falsifiers.test_m701_recorded_workload",
    "test.falsifiers.test_m7_topology_execution",
)

#: Report field -> the test name whose presence proves the behaviour ran.
MARKERS = {
    "three_topologies": "ThreeTopologiesShareOneRuntime",
    "one_runtime_shape": "test_all_three_lower_through_the_same_shape",
    "distinct_structures": "test_they_remain_three_structures_not_three_names_for_one",
    "lowering_is_not_concurrency": "test_lowering_activates_nothing_concurrent",
    "cycles_rejected": "test_a_delegation_cycle_is_rejected_at_parse",
    "authority_rejected": "test_a_topology_carrying_authority_is_refused_by_the_parser",
    "unreachable_role_visible": "test_an_unreachable_role_is_visible",
    "missing_resource_named": "test_the_missing_resource_is_named_not_merely_counted",
    "independence_measured": "test_useful_independence_on_the_real_path_is_measured",
    "m701_live_path": "M701RunsOnTheCanonicalPath",
    "recorded_timestamps": "test_effect_windows_use_recorded_event_timestamps",
    "unobserved_not_invented": "test_unobserved_cache_and_wal_metrics_are_not_invented",
    "analysis_only": "test_the_report_stays_analysis_only_and_digest_stable",
    "digest_stable": "test_the_report_over_a_fixed_seed_run_is_digest_stable",

    # -- execution, not merely lowering (Lane A landed the topology bridge) --
    "forms_execute": "test_all_three_forms_complete_through_the_one_public_path",
    "role_operations_executed": "test_role_operations_execute_as_m6_children",
    "children_bound_to_root": "test_every_child_is_bound_to_the_root_episode",
    "roles_run_once": "test_each_role_runs_exactly_once",
    "causal_order_honoured": "test_children_are_spawned_in_causal_predecessor_order",
    "intent_keys_topology_bound": "test_each_intent_key_is_bound_to_the_topology_digest",
    "sequential_not_overlapped": "test_execution_is_sequential_not_overlapped",
    "cold_reconstructs_tree": "test_the_ledger_reconstructs_the_whole_tree_cold",
    "children_never_get_spawn": "test_children_never_receive_the_spawn_verb",
    "direct_form_does_real_work": "test_the_direct_form_does_real_work_through_the_canonical_path",

    # This marker is tied to the ledger-backed artifact-flow assertion, not to
    # topology lowering or a counter supplied by the caller.
    "artifact_flows_exercised": "test_artifact_flows_are_exercised_between_roles",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = run_suite(
        args.root.resolve(), MODULES,
        schema="aether.m7-falsifier-report/1", markers=MARKERS,
    )
    return emit(report, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
