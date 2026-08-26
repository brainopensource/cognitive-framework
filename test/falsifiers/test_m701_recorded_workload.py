"""M7-01 on a real recorded workload, and what it finds there (`B-M7`).

`test_m7_topology_and_independence.py` checks the analyzer against fixtures
whose right answer is known by construction.  This file runs it against the
*canonical* path -- `Runtime.execute_harness` over the coding pack with the
deterministic offline LAM provider -- because an analysis validated only on
its own fixtures measures its author's expectations.

The canonical capture path records the resolved selector on `EffectStarted`
and the analyzer reads the authoritative event timestamps. The workload thus
produces a real independence decomposition rather than a conservative value
caused by missing fields. Cache and WAL-writer instrumentation remain separate
inputs and an unobserved value is never treated as a hit, miss, or zero-cost
measurement.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from lab.m701_independence import analyze_events
from vanguard.packages.adapters.models.lam import LamModelAdapter
from vanguard.packages.agency import RunTermination
from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef, Verdict
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.governance.approvals import OperatorSigner
from vanguard.packages.runtime.root import Runtime, TaskContext

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "vanguard/packages/agency/manifests/vg-code-default/manifest.json"


class _Verifier:
    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol) -> Result[Verdict]:
        return Result.success(Verdict(outcome="claims",
                                      claims=({"claim": "m701", "holds": True},),
                                      reason=protocol.name))


def _record_canonical_workload():
    """One fixed-seed run through the canonical composition; no fakes."""
    with tempfile.TemporaryDirectory() as directory:
        repo = Path(directory)
        (repo / "src").mkdir()
        (repo / "src/value.py").write_text("VALUE = 1\n", encoding="utf-8")
        (repo / "test_value.py").write_text(
            "import unittest\nfrom src.value import VALUE\n\n"
            "class TestValue(unittest.TestCase):\n"
            "    def test_value(self):\n"
            "        self.assertEqual(VALUE, 2)\n\n"
            "if __name__ == '__main__':\n    unittest.main()\n",
            encoding="utf-8")
        signer = OperatorSigner(b"m701-recorded-workload-key")
        result = Runtime.execute_harness(
            MANIFEST,
            TaskContext(brief="Repair the value bug and verify the test suite.",
                        repo_path=repo, run_id="m701-run", episode_id="m701-episode",
                        principal="agent-1", max_turns=6),
            model=LamModelAdapter(model_name="lam/t0-vanguard-vertical"),
            approver=lambda challenge: signer.approve(challenge, reviewer="operator"),
            approval_key=signer.public_bytes,
            verifier=_Verifier(),
        )
        return result, [{"at": event.at,
                         "payload": {"kind": event.kind, **dict(event.payload)}}
                        for event in result.events]


class M701RunsOnTheCanonicalPath(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result, cls.events = _record_canonical_workload()

    def test_the_recorded_run_is_a_real_completed_execution(self) -> None:
        self.assertIs(self.result.terminal, RunTermination.COMPLETED)
        self.assertEqual([receipt.verb for receipt in self.result.receipts],
                         ["fs.read", "patch.apply", "proc.exec"])

    def test_the_analyzer_pairs_the_real_settled_effects(self) -> None:
        # Three settled effects, three pairs. A reader that found zero would
        # be reporting a vacuous 0/0 rather than a measurement.
        report = analyze_events(self.events)
        self.assertEqual(report["settled_effects"], 3)
        self.assertEqual(report["pair_count"], 3)

    def test_useful_independence_on_the_real_path_is_measured(self) -> None:
        report = analyze_events(self.events)
        self.assertEqual(report["independent_pairs"], 1)
        self.assertAlmostEqual(report["useful_independence_fraction"], 1 / 3)

    def test_resolved_selectors_drive_the_decomposition(self) -> None:
        reasons = analyze_events(self.events)["serialization"]["reasons"]
        self.assertEqual(reasons["unknown_selector"], 0)
        self.assertEqual(reasons["resource"], 1)
        self.assertEqual(reasons["causal"], 0)
        self.assertEqual(reasons["sink"], 1)

    def test_effect_windows_use_recorded_event_timestamps(self) -> None:
        contention = analyze_events(self.events)["wal_contention"]
        self.assertEqual(contention["measured_windows"], 3)
        self.assertGreaterEqual(contention["observed_span_millis"], 0.0)
        self.assertEqual(contention["overlapping_windows"], 0)

    def test_unobserved_cache_and_wal_metrics_are_not_invented(self) -> None:
        report = analyze_events(self.events)
        self.assertTrue(report["analysis_only"])
        self.assertEqual(report["cache"]["observed"], 0)
        self.assertEqual(report["cache"]["unobserved"], 3)
        self.assertEqual(report["wal_contention"]["wal_write_millis"], 0.0)

    def test_the_report_over_a_fixed_seed_run_is_digest_stable(self) -> None:
        self.assertEqual(analyze_events(self.events)["report_digest"],
                         analyze_events(list(self.events))["report_digest"])


if __name__ == "__main__":
    unittest.main()
