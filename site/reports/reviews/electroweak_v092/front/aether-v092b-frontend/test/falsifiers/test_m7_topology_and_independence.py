"""M-7 evidence: independence decomposition and topology falsification (`B-M7`).

Two claims are on trial here, and both are the kind that look obviously true
until measured.

**"Concurrency would help."**  M7-01 must be able to return *no*.  Below
roughly 30% useful independence, `ADR-0092` cancels advanced scheduling and
keeps I-11 -- so the analyzer's job is to make that outcome reachable, which
means every pair it cannot prove independent must count against the case.  The
tests below feed it workloads whose right answer is known by construction.

**"Three topologies run through one runtime."**  A gate satisfied by three
topologies merely *parsing* proves nothing at all.  What is checkable without
a live run is that they lower through the same code to the same shape while
staying distinct artifacts -- and that a structure which cannot run is
rejected before lowering rather than after deadlocking.

Nothing in this file activates concurrency; I-11 remains sequential.
"""

from __future__ import annotations

import unittest

from lab.m701_independence import analyze_events
from lab.topology_analysis import (
    analyze_topology,
    missing_resources,
    three_topology_report,
    unreachable_roles,
)
from test.fixtures.m7_topologies import (
    CAUSAL_DEPENDENCY_WORKLOAD,
    CONFLICTING_WRITE_WORKLOAD,
    CRITIC_REVISER,
    CYCLIC,
    DIRECT,
    MISSING_RESOURCE,
    PLANNER_EXECUTOR,
    SAFE_READ_WORKLOAD,
    VALID_TOPOLOGIES,
)
from vanguard.packages.runtime.topology import TopologyError, parse_topology


class TheAnalyzerCanReportThatConcurrencyWouldNotHelp(unittest.TestCase):
    """The result M7-01 exists to make reachable."""

    def test_two_writes_to_one_file_are_a_resource_conflict(self) -> None:
        report = analyze_events(CONFLICTING_WRITE_WORKLOAD)
        self.assertEqual(report["independent_pairs"], 0)
        self.assertEqual(report["useful_independence_fraction"], 0.0)
        self.assertEqual(report["serialization"]["reasons"]["resource"], 1)

    def test_a_causal_edge_is_reported_as_causal_not_as_a_resource_conflict(self) -> None:
        # Both are true of this pair; only one of them is recoverable by
        # removing the conflict, and reporting the wrong one overstates the
        # win a scheduler could deliver.
        report = analyze_events(CAUSAL_DEPENDENCY_WORKLOAD)
        self.assertEqual(report["serialization"]["reasons"]["causal"], 1)
        self.assertEqual(report["serialization"]["reasons"]["resource"], 0)
        self.assertEqual(report["independent_pairs"], 0)

    def test_disjoint_reads_on_the_observation_sink_stay_independent(self) -> None:
        # The one case `milestones.md` already permits. If shared-sink use
        # were treated as a conflict, this would be erased and the analysis
        # would understate independence rather than overstate it.
        report = analyze_events(SAFE_READ_WORKLOAD)
        self.assertEqual(report["independent_pairs"], 1)
        self.assertEqual(report["serialization"]["recoverable_fraction"], 1.0)

    def test_an_unknown_selector_counts_against_concurrency(self) -> None:
        events = [
            {"payload": {"kind": "EffectStarted", "idempotencyKey": "x", "sink": "observation"}},
            {"payload": {"kind": "EffectCompleted", "idempotencyKey": "x"}},
            {"payload": {"kind": "EffectStarted", "idempotencyKey": "y", "sink": "observation",
                         "resource": {"kind": "fs", "root": "/w", "paths": ["/w/y"]}}},
            {"payload": {"kind": "EffectCompleted", "idempotencyKey": "y"}},
        ]
        report = analyze_events(events)
        self.assertEqual(report["serialization"]["reasons"]["unknown_selector"], 1)
        self.assertEqual(report["independent_pairs"], 0)

    def test_the_decomposition_accounts_for_every_pair(self) -> None:
        for workload in (SAFE_READ_WORKLOAD, CONFLICTING_WRITE_WORKLOAD,
                         CAUSAL_DEPENDENCY_WORKLOAD):
            report = analyze_events(workload)
            self.assertEqual(
                report["independent_pairs"] + sum(report["serialization"]["reasons"].values()),
                report["pair_count"])


class ContentionAndCacheBoundTheAvailableWin(unittest.TestCase):
    """Independence is necessary for a speedup and nowhere near sufficient."""

    def test_wal_write_share_is_reported_against_the_observed_span(self) -> None:
        report = analyze_events(CONFLICTING_WRITE_WORKLOAD)
        contention = report["wal_contention"]
        self.assertEqual(contention["measured_windows"], 2)
        self.assertEqual(contention["observed_span_millis"], 41.0)
        self.assertAlmostEqual(contention["wal_write_share"], 12.0 / 41.0)

    def test_a_sequential_recording_shows_no_overlapping_windows(self) -> None:
        # I-11 says so; a non-zero count here is a finding about the
        # recording, never a licence to parallelise.
        for workload in (SAFE_READ_WORKLOAD, CONFLICTING_WRITE_WORKLOAD,
                         CAUSAL_DEPENDENCY_WORKLOAD):
            self.assertEqual(analyze_events(workload)["wal_contention"]["overlapping_windows"], 0)

    def test_cache_hits_are_counted_and_unobserved_is_not_a_miss(self) -> None:
        cache = analyze_events(SAFE_READ_WORKLOAD)["cache"]
        self.assertEqual((cache["hits"], cache["misses"], cache["hit_rate"]), (1, 1, 0.5))
        bare = analyze_events(CONFLICTING_WRITE_WORKLOAD + [
            {"payload": {"kind": "EffectStarted", "idempotencyKey": "z", "sink": "observation",
                         "resource": {"kind": "fs", "root": "/w", "paths": ["/w/z"]}}},
            {"payload": {"kind": "EffectCompleted", "idempotencyKey": "z"}},
        ])["cache"]
        self.assertEqual(bare["unobserved"], 1)
        self.assertEqual(bare["misses"], 2)

    def test_the_report_stays_analysis_only_and_digest_stable(self) -> None:
        first = analyze_events(SAFE_READ_WORKLOAD)
        second = analyze_events(list(reversed(SAFE_READ_WORKLOAD)))
        self.assertTrue(first["analysis_only"])
        self.assertEqual(first["report_digest"], second["report_digest"])


class ThreeTopologiesShareOneRuntime(unittest.TestCase):
    def test_all_three_lower_through_the_same_shape(self) -> None:
        report = three_topology_report(list(VALID_TOPOLOGIES))
        self.assertEqual(report["count"], 4)
        self.assertEqual(report["runnable"], 4)
        self.assertTrue(report["sharedLoweringShape"])
        self.assertTrue(report["distinctDigests"])

    def test_they_remain_three_structures_not_three_names_for_one(self) -> None:
        digests = {parse_topology(raw).digest() for raw in VALID_TOPOLOGIES}
        self.assertEqual(len(digests), 4)

    def test_lowering_activates_nothing_concurrent(self) -> None:
        report = three_topology_report(list(VALID_TOPOLOGIES))
        self.assertTrue(report["sequentialOnly"])
        self.assertEqual(report["sharedActivation"], ["ordinary-agent-spawn-sequential"])

    def test_the_direct_topology_is_the_degenerate_case_of_the_same_language(self) -> None:
        direct = analyze_topology(DIRECT)
        chained = analyze_topology(CRITIC_REVISER)
        self.assertEqual(direct["lowering"]["keys"], chained["lowering"]["keys"])
        self.assertEqual(direct["edgeCount"], 0)
        self.assertEqual(chained["edgeCount"], 2)


class UnrunnableTopologiesAreRejectedBeforeLowering(unittest.TestCase):
    def test_a_delegation_cycle_is_rejected_at_parse(self) -> None:
        report = analyze_topology(CYCLIC)
        self.assertFalse(report["parsed"])
        self.assertEqual(report["findings"][0]["code"], "parse_rejected")

    def test_a_consumed_artifact_nobody_produces_is_a_finding(self) -> None:
        # A topology that lowers and then deadlocks is worse than one refused
        # at the value boundary. A-M7 closes the former parser gap here.
        report = analyze_topology(MISSING_RESOURCE)
        self.assertFalse(report["parsed"])
        self.assertFalse(report["runnable"])
        self.assertEqual([f["code"] for f in report["findings"]], ["parse_rejected"])
        self.assertIn("no declared producer", report["findings"][0]["detail"])

    def test_the_missing_resource_is_named_not_merely_counted(self) -> None:
        with self.assertRaisesRegex(TopologyError, "researchNotes.*researcher"):
            parse_topology(MISSING_RESOURCE)

    def test_a_wired_topology_has_no_missing_resources(self) -> None:
        for raw in VALID_TOPOLOGIES:
            self.assertEqual(missing_resources(parse_topology(raw)), (), raw["topologyId"])

    def test_an_unreachable_role_is_visible(self) -> None:
        orphaned = {**PLANNER_EXECUTOR, "topologyId": "orphaned",
                    "roles": PLANNER_EXECUTOR["roles"] + [
                        {"id": "ghost", "policyRef": "policy/ghost@1"}],
                    "artifactFlows": []}
        with self.assertRaisesRegex(TopologyError, "unreachable.*ghost"):
            parse_topology(orphaned)

    def test_a_topology_carrying_authority_is_refused_by_the_parser(self) -> None:
        # Topology decides what may run; the kernel decides what is
        # authorized. A topology that grants has merged the two.
        for key in ("capabilities", "grants", "authority"):
            raw = {**DIRECT, "roles": [{"id": "agent", "policyRef": "p", key: ["fs.write"]}]}
            report = analyze_topology(raw)
            self.assertFalse(report["parsed"], key)


if __name__ == "__main__":
    unittest.main()
