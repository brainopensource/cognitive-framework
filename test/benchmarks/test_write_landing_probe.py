"""T-130 falsifier — the write-landing seam probe must be a valid instrument.

The row's standard is explicit: a probe that reports "no seam identified"
without passing both controls is an inconclusive instrument, not a finding
about the product. These tests are therefore mostly about the *probe*, and only
then about what it observed.

RUN-12: every test here runs on an in-memory provider tape. Zero provider
calls, zero USD, no network, no Ollama.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from benchmarks.diagnostics.write_landing_probe import (
    EXPECTED_WRITES,
    FRESH_FIXTURES,
    NEGATIVE_INJECTIONS,
    SEAMS,
    SEAM_NOT_REPRODUCED,
    SEAM_STALE_TREE,
    ProbeTrace,
    attribute,
    canonical_write_tape,
    exterior_oracle_digest,
    fixture_dir,
    negative_control,
    negative_control_passed,
    positive_control,
    positive_control_passed,
    run_all,
    run_probe,
    tree_digest,
)

REQUIRED_TRACES = ("L0", "multi-file", "greenfield")


class TestProbeShape(unittest.TestCase):
    """The instrument declares the discrimination classes T-130 fixed."""

    def test_eight_discrimination_classes(self) -> None:
        self.assertEqual(len(SEAMS), 8)
        self.assertEqual(len(set(SEAMS)), 8)

    def test_fresh_fixtures_exist_and_are_not_holdout_members(self) -> None:
        for fixture in FRESH_FIXTURES:
            folder = fixture_dir(fixture)
            self.assertTrue((folder / "TASK.md").is_file(), fixture)
            self.assertTrue((folder / "test_oracle.py").is_file(), fixture)
            # Authored under benchmarks/diagnostics precisely so no T-51 L2
            # holdout member is read, run, tuned against or diagnosed.
            self.assertIn("diagnostics", folder.parts)
            self.assertNotIn("l2_thirty", folder.parts)
            self.assertNotIn("m8_heldout", folder.parts)

    def test_probe_drives_the_real_product_entrypoint(self) -> None:
        source = (Path(__file__).resolve().parents[2] / "benchmarks"
                  / "diagnostics" / "write_landing_probe.py").read_text("utf-8")
        # The route must be the shipped one, not a substituted harness.
        self.assertIn("from benchmarks.product_path import execute_product", source)
        self.assertNotIn("execute_profiled", source)
        self.assertNotIn("ForgeFacade", source)
        self.assertNotIn("baac", source)

    def test_probe_uses_the_shipped_dialect_normalizer(self) -> None:
        source = (Path(__file__).resolve().parents[2] / "benchmarks"
                  / "diagnostics" / "write_landing_probe.py").read_text("utf-8")
        self.assertIn("ProposalTranslator", source)


class TestControls(unittest.TestCase):
    """Both controls gate every conclusion the probe is allowed to draw."""

    def test_positive_control_lands_and_is_observed_identically(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            trace = positive_control(Path(tmp) / "pos")
        self.assertTrue(positive_control_passed(trace), trace.to_dict())
        # Atomic landing: the tree moved, and the oracle observed *that* tree.
        self.assertNotEqual(trace.candidate_digest, trace.preimage_digest)
        self.assertEqual(trace.oracle_digest, trace.candidate_digest)
        self.assertEqual(set(trace.changed_files), set(EXPECTED_WRITES["P0-FIB"]))
        self.assertEqual(trace.seam, SEAM_NOT_REPRODUCED)

    def test_negative_control_attributes_each_injection_to_its_own_seam(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            results = negative_control(Path(tmp) / "neg")
        self.assertEqual(len(results), len(NEGATIVE_INJECTIONS))
        for name, expected, trace in results:
            with self.subTest(injection=name):
                self.assertEqual(trace.seam, expected, trace.to_dict())
                self.assertEqual(trace.candidate_digest, trace.preimage_digest)
        self.assertTrue(negative_control_passed(results))
        # Three injections, three distinct seams: the probe discriminates, it
        # does not merely emit one word.
        self.assertEqual(len({str(t.seam) for _n, _e, t in results}), 3)

    def test_stale_tree_divergence_is_detectable(self) -> None:
        """The oracle seam must be observable, not merely declared."""
        trace = ProbeTrace(
            label="synthetic", fixture="P0-FIB", run_id="r", workspace="/tmp/x",
            preimage_digest="sha256:aaa", candidate_digest="sha256:bbb",
            oracle_digest="sha256:ccc", oracle_files={}, changed_files=("f.py",),
            terminal_outcome="abandoned", terminal_detail="", turns_consumed=1,
        )
        # A landed, admitted write whose oracle observation diverges.
        trace.model_turns = []
        attribute(trace)
        self.assertEqual(trace.seam, SEAM_STALE_TREE)

    def test_two_independent_walkers_agree_on_an_unchanged_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "t"
            (base / "pkg").mkdir(parents=True)
            (base / "a.py").write_text("a\n")
            (base / "pkg" / "b.py").write_text("b\n")
            first = tree_digest(base)
            second, files = exterior_oracle_digest(base)
        self.assertEqual(first, second)
        self.assertEqual(set(files), {"a.py", "pkg/b.py"})


class TestTraces(unittest.TestCase):
    """The three required traces, each attributed to its first failing seam."""

    def test_each_fixture_yields_an_attributed_trace(self) -> None:
        for label, fixture in (("L0", "P0-FIB"), ("multi-file", "DX-MULTI"),
                               ("greenfield", "DX-GREEN")):
            with self.subTest(fixture=fixture), tempfile.TemporaryDirectory() as tmp:
                trace = run_probe(label, fixture, Path(tmp) / label,
                                  canonical_write_tape(fixture))
                self.assertIsNotNone(trace.seam)
                self.assertIn(trace.seam, set(SEAMS) | {SEAM_NOT_REPRODUCED})
                self.assertTrue(trace.seam_evidence, "an attribution needs evidence")
                # Whatever the seam, the trace must carry the correlated
                # material the row requires.
                self.assertTrue(trace.model_turns)
                self.assertTrue(trace.model_turns[0].offered_tools)
                self.assertTrue(trace.preimage_digest.startswith("sha256:"))
                self.assertTrue(trace.candidate_digest.startswith("sha256:"))
                self.assertTrue(trace.oracle_digest.startswith("sha256:"))
                self.assertTrue(trace.terminal_outcome)
                self.assertTrue(trace.ledger, "the durable ledger must be readable")

    def test_multifile_write_is_all_or_nothing(self) -> None:
        """A multi-file submission either lands whole or is attributed."""
        with tempfile.TemporaryDirectory() as tmp:
            trace = run_probe("multi-file", "DX-MULTI", Path(tmp) / "m",
                              canonical_write_tape("DX-MULTI"))
        expected = set(EXPECTED_WRITES["DX-MULTI"])
        if trace.seam == SEAM_NOT_REPRODUCED:
            self.assertEqual(set(trace.changed_files), expected)
            self.assertEqual(trace.oracle_digest, trace.candidate_digest)
        else:
            self.assertNotEqual(set(trace.changed_files), expected)


class TestPacket(unittest.TestCase):
    """The exit artefact: three traces plus both controls, in one packet."""

    def test_packet_is_complete_and_the_instrument_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet = run_all(Path(tmp) / "packet")
        self.assertEqual(packet["providerCalls"], 0)
        self.assertEqual(packet["usdSpent"], 0.0)
        self.assertEqual(tuple(packet["attributions"]), REQUIRED_TRACES)
        controls = packet["controls"]
        self.assertTrue(controls["positivePassed"], controls["positive"])
        self.assertTrue(controls["negativePassed"], controls["negative"])
        self.assertTrue(controls["bothPassed"])
        # Controls passed, so the instrument may speak about the product.
        self.assertEqual(packet["instrumentStatus"], "valid")
        for trace in packet["traces"]:
            self.assertIn(trace["seam"], set(SEAMS) | {SEAM_NOT_REPRODUCED})
            self.assertTrue(trace["seamEvidence"])

    def test_no_seam_identified_is_gated_on_the_controls(self) -> None:
        """The gate itself must be real: unpassed controls invalidate the finding."""
        with tempfile.TemporaryDirectory() as tmp:
            trace = positive_control(Path(tmp) / "p")
        # Corrupt the control outcome and prove the predicate rejects it.
        trace.oracle_digest = "sha256:divergent"
        self.assertFalse(positive_control_passed(trace))


if __name__ == "__main__":
    unittest.main()
