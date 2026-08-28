"""B-O11-01: the M-7 and M-8 evidence builders cannot close a claim they did not observe.

A suite report is an observation, and the builders must treat it as one. The
failure these guard against is the quiet kind: a suite that stops exercising a
required behaviour still exits zero, so exit status alone would let coverage
rot into a milestone closure.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.runners.build_evidence_bundle import (  # noqa: E402
    _report_passed,
    build_m7,
    build_m8,
)
from tools.runners.run_m7_topology_proof import MARKERS as M7_MARKERS  # noqa: E402
from tools.runners.run_m8_governed_learning_proof import (  # noqa: E402
    MARKERS as M8_MARKERS,
)


def _report(markers: dict[str, bool], **overrides) -> dict:
    body = {
        "schema": "aether.test-report/1",
        "returncode": 0,
        "tests": 42,
        "failures": 0,
        "fresh_process": True,
        "markers": dict(markers),
    }
    body.update(overrides)
    return body


class AReportOnlySupportsWhatItObserved(unittest.TestCase):
    def test_a_clean_fully_covered_report_supports_the_claim(self) -> None:
        required = ("a", "b")
        self.assertTrue(_report_passed(_report({"a": True, "b": True}), required))

    def test_a_dropped_marker_degrades_the_claim(self) -> None:
        """Coverage rot must not read as success."""
        self.assertFalse(
            _report_passed(_report({"a": True, "b": False}), ("a", "b")))

    def test_a_nonzero_exit_never_supports_the_claim(self) -> None:
        self.assertFalse(
            _report_passed(_report({"a": True}, returncode=1), ("a",)))

    def test_a_report_with_no_tests_never_supports_the_claim(self) -> None:
        """An empty run is not a clean run."""
        self.assertFalse(_report_passed(_report({"a": True}, tests=0), ("a",)))

    def test_failures_never_support_the_claim(self) -> None:
        self.assertFalse(_report_passed(_report({"a": True}, failures=2), ("a",)))

    def test_a_report_without_a_returncode_is_refused_not_assumed(self) -> None:
        body = _report({"a": True})
        del body["returncode"]
        with self.assertRaises(ValueError):
            _report_passed(body, ("a",))


#: The marker no suite can set today: multi-role lineages settle `abandoned`
#: with no receipts, so declared artifact flows are never exercised.
_UNSETTABLE = "artifact_flows_exercised"


class M7CannotCloseItsUnexercisedArtifactFlows(unittest.TestCase):
    """M-7 requires more than lowering, and more than spawning.

    Role execution is real now -- roles run as M-6 children. What is still
    unobserved is the declared role-to-role artifact flow, because no role
    lineage performs an effect. M-7 must not report `passed` on the strength of
    everything else.
    """

    def _build(self, markers):
        return build_m7("dev-b", _report(markers), evidence_root=Path(
            self.enterContext(__import__("tempfile").TemporaryDirectory())))

    def test_every_settable_marker_green_still_cannot_close_m7(self) -> None:
        markers = {name: True for name in M7_MARKERS}
        markers[_UNSETTABLE] = False
        envelope = self._build(markers)
        self.assertEqual(envelope.outcome, "undeterminable")
        self.assertIn("artifact flow", envelope.detail)
        self.assertFalse(envelope.run["artifactFlowsExercised"])

    def test_role_execution_is_recorded_as_achieved(self) -> None:
        """The bundle must not keep reporting a gap Lane A already closed."""
        markers = {name: True for name in M7_MARKERS}
        markers[_UNSETTABLE] = False
        self.assertTrue(self._build(markers).run["roleOperationsExecuted"])

    def test_losing_role_execution_reopens_m7(self) -> None:
        markers = {name: True for name in M7_MARKERS}
        markers["role_operations_executed"] = False
        self.assertEqual(self._build(markers).outcome, "undeterminable")

    def test_losing_sequential_execution_reopens_m7(self) -> None:
        """ADR-0099 is SEQUENTIAL_CONFIRMED; overlap would contradict it."""
        markers = {name: True for name in M7_MARKERS}
        markers["sequential_not_overlapped"] = False
        self.assertEqual(self._build(markers).outcome, "undeterminable")

    def test_the_unmet_clause_is_named_in_the_bundle(self) -> None:
        markers = {name: True for name in M7_MARKERS}
        markers[_UNSETTABLE] = False
        self.assertIn("artifact flows", str(self._build(markers)
                                            .run["unobservedClause"]))

    def test_every_material_declares_a_re_derivable_scheme(self) -> None:
        envelope = self._build({name: True for name in M7_MARKERS})
        self.assertTrue(envelope.materials)
        for material in envelope.materials:
            with self.subTest(material=material.name):
                self.assertEqual(material.scheme, "raw-sha256")
                self.assertTrue(material.ref, "a digest with no ref locates nothing")


class M8RestsOnBothHalvesOfItsPredicate(unittest.TestCase):
    def _build(self, report):
        return build_m8("dev-b", report, evidence_root=Path(self.enterContext(
            __import__("tempfile").TemporaryDirectory())))

    def test_a_clean_fully_covered_suite_closes_m8(self) -> None:
        envelope = self._build(_report({name: True for name in M8_MARKERS}))
        self.assertEqual(envelope.outcome, "passed")

    def test_losing_the_rollback_marker_reopens_m8(self) -> None:
        """`durable_memory_and_signed_rollback_verified` is a conjunction."""
        markers = {name: True for name in M8_MARKERS}
        markers["rollback_executed"] = False
        self.assertEqual(self._build(_report(markers)).outcome, "undeterminable")

    def test_losing_authority_separation_reopens_m8(self) -> None:
        markers = {name: True for name in M8_MARKERS}
        markers["authorities_distinct"] = False
        self.assertEqual(self._build(_report(markers)).outcome, "undeterminable")

    def test_every_material_declares_a_re_derivable_scheme(self) -> None:
        envelope = self._build(_report({name: True for name in M8_MARKERS}))
        self.assertTrue(envelope.materials)
        for material in envelope.materials:
            with self.subTest(material=material.name):
                self.assertEqual(material.scheme, "raw-sha256")
                self.assertTrue(material.ref)


if __name__ == "__main__":
    unittest.main()
