"""M7-01 on a real recorded workload, and what it finds there (`B-M7`).

`test_m7_topology_and_independence.py` checks the analyzer against fixtures
whose right answer is known by construction.  This file runs it against the
*canonical* path -- `Runtime.execute_harness` over the coding pack with the
deterministic offline LAM provider -- because an analysis validated only on
its own fixtures measures its author's expectations.

The result is a finding, and the finding is the deliverable:

**The canonical ledger does not currently carry what M7-01 needs.**
`EffectStarted` writes `descriptorDigest`, `sinkClass`, `grantId` and
`leaseId`, but `idempotencyKey` is `null` and there is **no resolved resource
selector and no timing**.  Without a selector the analyzer cannot show two
effects touch disjoint resources, so every pair is conservatively dependent
and useful independence on the real path is `0.0`.

That zero is not evidence that concurrency would not help.  It is evidence
that the question cannot yet be asked, which is a different statement and must
not be reported as the first one.  `ADR-0099` needs the measured fraction over
recorded workloads; until effect capture carries resolved selectors, M7-01 can
report only the conservative floor.  The tests below pin both halves so the
gap cannot close silently in either direction: if capture starts carrying
selectors, `test_the_capture_gap_is_still_open` fails and this file is updated
with a real fraction.
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
        return result, [{"payload": {"kind": event.kind, **dict(event.payload)}}
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

    def test_useful_independence_on_the_real_path_is_the_conservative_floor(self) -> None:
        report = analyze_events(self.events)
        self.assertEqual(report["independent_pairs"], 0)
        self.assertEqual(report["useful_independence_fraction"], 0.0)

    def test_the_capture_gap_is_still_open(self) -> None:
        # THE FINDING. Every pair is dependent for one reason only: no
        # resolved selector was recorded. If this ever fails because capture
        # improved, that is good news and this file must be updated with a
        # real measured fraction rather than left asserting the floor.
        reasons = analyze_events(self.events)["serialization"]["reasons"]
        self.assertEqual(reasons["unknown_selector"], 3,
                         "effect capture now carries selectors: rerun M7-01 and "
                         "record the measured independence fraction for ADR-0099")
        self.assertEqual(reasons["resource"], 0)
        self.assertEqual(reasons["causal"], 0)

    def test_no_timing_is_recorded_so_contention_is_unmeasured(self) -> None:
        contention = analyze_events(self.events)["wal_contention"]
        self.assertEqual(contention["measured_windows"], 0)
        self.assertEqual(contention["observed_span_millis"], 0.0)

    def test_the_conservative_floor_is_not_reported_as_a_cancel_decision(self) -> None:
        # `ADR-0092` cancels advanced scheduling below ~30% useful
        # independence. This 0.0 is unmeasurable, not measured, and must not
        # be handed to that decision as if it were the latter.
        report = analyze_events(self.events)
        self.assertTrue(report["analysis_only"])
        self.assertEqual(report["cache"]["observed"], 0)
        self.assertEqual(report["cache"]["unobserved"], 3)

    def test_the_report_over_a_fixed_seed_run_is_digest_stable(self) -> None:
        self.assertEqual(analyze_events(self.events)["report_digest"],
                         analyze_events(list(self.events))["report_digest"])


if __name__ == "__main__":
    unittest.main()
