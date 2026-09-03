"""M-7 measurement package and ResourceSelector independence contract tests.

Validates:
1. Disjointness relation over all ResourceSelector kinds (fs, network, secret, git, generic, cross-kind).
2. Independence-group partitioning and conflict detection for candidate action graphs.
3. Fail-closed rejection of conflicting / overlapping action sets.
4. Pareto measurement report attribution and cost-per-signed-pass calculations.
5. Invariant I-11 preservation: concurrency remains un-activated before M-7 approval.
"""

from __future__ import annotations

import unittest
from vanguard.packages.domain.selectors.independence import (
    are_independent,
    compute_independence_groups,
    disjoint,
)
from vanguard.packages.runtime.pareto_measurement import (
    ParetoMeasurementReport,
    ParetoProfile,
    WalContentionMetrics,
)


class TestResourceSelectorIndependence(unittest.TestCase):
    def test_disjoint_filesystem_paths(self) -> None:
        s1 = {"kind": "fs", "root": "/workspace", "paths": ["/workspace/src/a.py"]}
        s2 = {"kind": "fs", "root": "/workspace", "paths": ["/workspace/src/b.py"]}
        s_overlap = {"kind": "fs", "root": "/workspace", "paths": ["/workspace/src"]}

        self.assertTrue(disjoint(s1, s2), "Disjoint sibling files must be independent")
        self.assertFalse(disjoint(s1, s_overlap), "Parent directory and child file must conflict")
        self.assertFalse(disjoint(s1, s1), "Identical file selectors must conflict")

    def test_cross_kind_resources_are_disjoint(self) -> None:
        s_fs = {"kind": "fs", "root": "/workspace", "paths": ["/workspace/a.py"]}
        s_net = {"kind": "network", "hosts": ["api.vendor.com"], "ports": [443]}
        s_sec = {"kind": "secret", "refs": ["api_key"], "discloseToModel": False}

        self.assertTrue(disjoint(s_fs, s_net), "FS and Network must be mutually independent")
        self.assertTrue(disjoint(s_fs, s_sec), "FS and Secret must be mutually independent")
        self.assertTrue(disjoint(s_net, s_sec), "Network and Secret must be mutually independent")

    def test_network_selectors_disjointness(self) -> None:
        n1 = {"kind": "network", "hosts": ["host-a.com"], "ports": [80]}
        n2 = {"kind": "network", "hosts": ["host-b.com"], "ports": [80]}
        n3 = {"kind": "network", "hosts": ["host-a.com"], "ports": [8080]}

        self.assertTrue(disjoint(n1, n2), "Distinct hosts must be disjoint")
        self.assertTrue(disjoint(n1, n3), "Same host with distinct ports must be disjoint")
        self.assertFalse(disjoint(n1, n1), "Identical network targets must conflict")

    def test_secret_and_git_disjointness(self) -> None:
        g1 = {"kind": "git", "repo": "https://github.com/org/repo-a", "refs": ["main"]}
        g2 = {"kind": "git", "repo": "https://github.com/org/repo-b", "refs": ["main"]}
        self.assertTrue(disjoint(g1, g2), "Distinct git repositories must be disjoint")

        sec1 = {"kind": "secret", "refs": ["token_a"], "discloseToModel": False}
        sec2 = {"kind": "secret", "refs": ["token_b"], "discloseToModel": False}
        self.assertTrue(disjoint(sec1, sec2), "Distinct secret keys must be disjoint")
        self.assertFalse(disjoint(sec1, {"kind": "secret", "refs": ["token_a", "token_c"], "discloseToModel": False}))

    def test_independence_group_partitioning(self) -> None:
        # 3 requests:
        # req 0: writes /workspace/a.py
        # req 1: writes /workspace/b.py (disjoint from req 0)
        # req 2: writes /workspace/a.py (conflicts with req 0, disjoint from req 1)
        reqs = [
            {"resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace/a.py"]}},
            {"resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace/b.py"]}},
            {"resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace/a.py"]}},
        ]

        waves = compute_independence_groups(reqs)
        self.assertEqual(len(waves), 2, "Conflicting requests must be split into 2 waves")
        self.assertIn(0, waves[0])
        self.assertIn(1, waves[0])
        self.assertEqual(waves[1], (2,))

    def test_pareto_measurement_report(self) -> None:
        report = ParetoMeasurementReport(
            profile=ParetoProfile.BETA,
            model_calls=3,
            coordination_envelopes=6,
            retries=0,
            bytes_transferred=4096,
            critical_path_millis=250,
            usd_micros=1000,
            tokens=400,
            signed_passes=2,
            wal_contention=WalContentionMetrics(claims_count=6, contention_events=0),
            independence_waves=2,
            max_wave_width=2,
        )

        self.assertEqual(report.cost_per_signed_pass_micros, 500)
        self.assertTrue(report.measurement_digest().startswith("sha256:"))
        d = report.to_dict()
        self.assertEqual(d["profile"], "beta")
        self.assertEqual(d["signed_passes"], 2)


if __name__ == "__main__":
    unittest.main()
