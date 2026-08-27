"""RF-113: `aether.evidence/1` cannot be used to launder an assertion.

An evidence protocol is only worth the refusals it makes. These falsify the
four ways an envelope could be turned back into the prose it replaced:
unpinned code, a silently edited field, a producer accepting their own work,
and an outcome vocabulary with no way to say "I do not know".
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from vanguard.packages.domain.evidence.envelope import (
    EVIDENCE_SCHEMA,
    OUTCOMES,
    EvidenceEnvelope,
    EvidenceEnvelopeError,
    Material,
    Producer,
    accepts,
    parse_envelope,
)

ROOT = Path(__file__).resolve().parents[2]


def _envelope(**overrides) -> EvidenceEnvelope:
    base = dict(
        claim="M-6", protocol="aether.m6.canonical-recursion/1",
        subjects=("package:WP-A1",),
        materials=(Material(name="surface", digest="sha256:" + "a" * 64),),
        run={"runId": "run-1"},
        pins={"commit": "abc123", "tree": "def456"},
        environment={"python": "3.12"},
        outcome="passed", producer=Producer(identity="dev-a"),
    )
    base.update(overrides)
    return EvidenceEnvelope(**base)


class RF113AnEnvelopeMustBindItsCode(unittest.TestCase):

    def test_an_envelope_without_a_commit_pin_is_refused(self) -> None:
        with self.assertRaises(EvidenceEnvelopeError):
            _envelope(pins={"tree": "def456"})

    def test_an_envelope_without_a_tree_pin_is_refused(self) -> None:
        with self.assertRaises(EvidenceEnvelopeError):
            _envelope(pins={"commit": "abc123"})

    def test_an_envelope_without_a_protocol_is_refused(self) -> None:
        """A claim whose method is unstated cannot be re-run, so it is not evidence."""
        with self.assertRaises(EvidenceEnvelopeError):
            _envelope(protocol="")

    def test_an_envelope_without_a_subject_is_refused(self) -> None:
        with self.assertRaises(EvidenceEnvelopeError):
            _envelope(subjects=())

    def test_a_material_without_a_digest_is_refused(self) -> None:
        """A filename is not evidence."""
        with self.assertRaises(EvidenceEnvelopeError):
            Material(name="ledger", digest="")

    def test_a_material_digest_must_name_its_algorithm(self) -> None:
        with self.assertRaises(EvidenceEnvelopeError):
            Material(name="ledger", digest="deadbeef")


class RF113TamperingIsDetected(unittest.TestCase):

    def test_an_edited_field_breaks_the_digest(self) -> None:
        wire = _envelope().to_wire()
        wire["outcome"] = "passed" if wire["outcome"] != "passed" else "failed"
        with self.assertRaises(EvidenceEnvelopeError):
            parse_envelope(wire)

    def test_an_edited_pin_breaks_the_digest(self) -> None:
        wire = _envelope().to_wire()
        wire["pins"]["commit"] = "0000000"
        with self.assertRaises(EvidenceEnvelopeError):
            parse_envelope(wire)

    def test_a_round_trip_preserves_the_digest(self) -> None:
        envelope = _envelope()
        self.assertEqual(parse_envelope(envelope.to_wire()).digest(),
                         envelope.digest())

    def test_a_foreign_schema_is_refused(self) -> None:
        wire = _envelope().to_wire()
        wire["schema"] = "aether.evidence/2"
        with self.assertRaises(EvidenceEnvelopeError):
            parse_envelope(wire)

    def test_the_signature_is_not_covered_by_its_own_digest(self) -> None:
        """Otherwise signing would change what was signed."""
        unsigned = _envelope()
        signed = _envelope(signature="ed25519:deadbeef")
        self.assertEqual(unsigned.digest(), signed.digest())


class RF113IndependenceIsCheckedNotAssumed(unittest.TestCase):

    def test_a_producer_cannot_accept_their_own_envelope(self) -> None:
        produced = _envelope(producer=Producer(identity="dev-a"))
        self_acceptance = _envelope(
            claim="acceptance", producer=Producer(identity="dev-a"),
            subjects=(produced.digest(),))
        self.assertFalse(accepts(self_acceptance, produced))

    def test_an_independent_reviewer_can_accept(self) -> None:
        produced = _envelope(producer=Producer(identity="dev-a"))
        acceptance = _envelope(
            claim="acceptance", producer=Producer(identity="reviewer-x"),
            subjects=(produced.digest(),))
        self.assertTrue(accepts(acceptance, produced))

    def test_an_acceptance_of_a_different_digest_does_not_count(self) -> None:
        """Accepting a drifted artifact is accepting a different artifact."""
        produced = _envelope(producer=Producer(identity="dev-a"))
        acceptance = _envelope(
            claim="acceptance", producer=Producer(identity="reviewer-x"),
            subjects=("sha256:" + "f" * 64,))
        self.assertFalse(accepts(acceptance, produced))

    def test_a_failing_acceptance_does_not_accept(self) -> None:
        produced = _envelope(producer=Producer(identity="dev-a"))
        acceptance = _envelope(
            claim="acceptance", producer=Producer(identity="reviewer-x"),
            outcome="failed", subjects=(produced.digest(),))
        self.assertFalse(accepts(acceptance, produced))


class RF113UnknownIsNeverAPass(unittest.TestCase):

    def test_undeterminable_is_a_first_class_outcome(self) -> None:
        """Invalid instrumentation must be recordable, or it becomes silence."""
        self.assertIn("undeterminable", OUTCOMES)
        envelope = _envelope(outcome="undeterminable")
        self.assertEqual(envelope.outcome, "undeterminable")

    def test_an_invented_outcome_is_refused(self) -> None:
        for bogus in ("ok", "green", "waived", "n/a", ""):
            with self.subTest(outcome=bogus):
                with self.assertRaises(EvidenceEnvelopeError):
                    _envelope(outcome=bogus)


class RF113TheShippedBundlesAreWellFormed(unittest.TestCase):
    """The two envelopes WP-A1 actually produced must survive their own rules."""

    def _load(self, name: str) -> EvidenceEnvelope:
        path = ROOT / "docs/03_execution/evidence" / name
        if not path.exists():
            self.skipTest(f"{name} not present")
        return parse_envelope(json.loads(path.read_text(encoding="utf-8")))

    def test_the_m4_bundle_parses_and_verifies_its_digest(self) -> None:
        envelope = self._load("M-4-rf95-candidate-03.json")
        self.assertEqual(envelope.claim, "RF-95")
        self.assertTrue(envelope.pins.get("commit"))
        self.assertIn(envelope.outcome, OUTCOMES)

    def test_the_m6_bundle_parses_and_verifies_its_digest(self) -> None:
        envelope = self._load("M-6-canonical-recursion.json")
        self.assertEqual(envelope.claim, "M-6")
        self.assertTrue(envelope.materials)

    def test_the_m65_bundle_parses_and_verifies_its_digest(self) -> None:
        envelope = self._load("M-6.5-attributable-paired-study.json")
        self.assertEqual(envelope.claim, "M-6.5")
        self.assertEqual(envelope.protocol, "aether.m65.attributable-paired-study/1")
        self.assertTrue(envelope.materials)
        self.assertTrue(envelope.signature)
        self.assertIn(envelope.outcome, OUTCOMES)


    def test_neither_bundle_claims_independent_acceptance(self) -> None:
        """Producing evidence is not accepting it. Both stay unaccepted."""
        for name in ("M-4-rf95-candidate-03.json", "M-6-canonical-recursion.json", "M-6.5-attributable-paired-study.json"):
            envelope = self._load(name)
            self.assertEqual(envelope.producer.role, "producer", name)
            self.assertFalse(accepts(envelope, envelope), name)


if __name__ == "__main__":
    unittest.main()

