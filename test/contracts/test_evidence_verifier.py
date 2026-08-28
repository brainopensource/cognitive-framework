"""B-O10-01: the independent evidence verifier fails closed.

``tools/linters/verify_evidence.py`` decides whether a milestone's evidence
supports its claim, with no human in the loop. A verifier that says `passed`
too easily is worse than none, so this module builds bundles that are wrong in
one specific way each and requires the verifier to notice.

The defect that motivated it: ``accepts()`` checked reviewer independence,
acceptance outcome and digest binding, but never the *subject's* own outcome.
A bundle reporting ``undeterminable`` with an acceptance record reporting
``passed`` therefore passed the gate. Three milestone claims -- M-4, M-5b and
M-6 -- rested on exactly that shape.
"""

from __future__ import annotations

import base64
import json
import unittest
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from vanguard.packages.domain.canonicalisation.jcs import canonical_bytes
from vanguard.packages.domain.evidence.envelope import (
    acceptance_defects,
    parse_envelope,
)

import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT / "tools" / "linters") not in sys.path:
    sys.path.insert(0, str(_ROOT / "tools" / "linters"))

from verify_evidence import FAILED, PASSED, UNDETERMINABLE, verify_bundle  # noqa: E402


def _bundle(outcome: str = "passed", **overrides) -> dict:
    body = {
        "schema": "aether.evidence/1",
        "claim": "TEST-01",
        "protocol": "aether.test/1",
        "outcome": outcome,
        "producer": {"identity": "dev-b", "role": "producer", "keyId": "producer-key"},
        "pins": {
            "branch": "main",
            "commit": "0" * 40,
            "tree": "1" * 40,
            "eventSchema": "mhf.event/2",
            "trajectorySchema": "mhf.trajectory/2",
        },
        "materials": [],
        "artifactRefs": [],
        "subject": ["milestone:TEST"],
        "signature": "producer-signature",
    }
    body.update(overrides)
    return body


def _acceptance(subject_digest: str, key: ed25519.Ed25519PrivateKey, **overrides) -> dict:
    public = key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    body = {
        "schema": "aether.evidence/1",
        "claim": "acceptance:TEST-01",
        "protocol": "aether.evidence.acceptance/1",
        "outcome": "passed",
        "producer": {
            "identity": "independent-reviewer",
            "role": "reviewer",
            "keyId": "reviewer-key",
        },
        "pins": {
            "branch": "main",
            "commit": "0" * 40,
            "tree": "1" * 40,
            "eventSchema": "mhf.event/2",
            "trajectorySchema": "mhf.trajectory/2",
        },
        "materials": [],
        "artifactRefs": [],
        "subject": [subject_digest],
        "environment": {"reviewerPublicKey": base64.b64encode(public).decode("ascii")},
    }
    body.update(overrides)
    envelope = parse_envelope({**body, "signature": ""})
    signature = key.sign(canonical_bytes(envelope.body()))
    body["signature"] = "ed25519:" + base64.b64encode(signature).decode("ascii")
    return body


class VerifierFailsClosed(unittest.TestCase):
    def setUp(self) -> None:
        self.key = ed25519.Ed25519PrivateKey.generate()
        self.tmp = Path(self.enterContext(__import__("tempfile").TemporaryDirectory()))

    def _write(self, bundle: dict, acceptance: dict | None) -> Path:
        path = self.tmp / "TEST-01.json"
        path.write_text(json.dumps(bundle), encoding="utf-8")
        if acceptance is not None:
            path.with_name(path.name + ".acceptance.json").write_text(
                json.dumps(acceptance), encoding="utf-8"
            )
        return path

    def _verify(self, bundle: dict, acceptance: dict | None = "auto"):
        if acceptance == "auto":
            digest = parse_envelope(bundle).digest()
            acceptance = _acceptance(digest, self.key)
        return verify_bundle(self._write(bundle, acceptance))

    # -- the defect this verifier exists for ------------------------------

    def test_acceptance_cannot_upgrade_an_undeterminable_subject(self) -> None:
        verdict = self._verify(_bundle(outcome="undeterminable"))
        self.assertEqual(verdict.outcome, FAILED)
        self.assertTrue(
            any("own outcome is 'undeterminable'" in f for f in verdict.failures),
            verdict.failures,
        )

    def test_acceptance_cannot_upgrade_a_failed_subject(self) -> None:
        verdict = self._verify(_bundle(outcome="failed"))
        self.assertEqual(verdict.outcome, FAILED)

    # -- authority separation ---------------------------------------------

    def test_a_producer_cannot_accept_their_own_evidence(self) -> None:
        bundle = _bundle()
        digest = parse_envelope(bundle).digest()
        acceptance = _acceptance(
            digest, self.key,
            producer={"identity": "dev-b", "role": "reviewer", "keyId": "reviewer-key"},
        )
        verdict = self._verify(bundle, acceptance)
        self.assertEqual(verdict.outcome, FAILED)
        self.assertTrue(any("cannot accept their own" in f for f in verdict.failures))

    def test_separate_identities_sharing_one_key_are_not_separate(self) -> None:
        bundle = _bundle()
        digest = parse_envelope(bundle).digest()
        acceptance = _acceptance(
            digest, self.key,
            producer={
                "identity": "independent-reviewer",
                "role": "reviewer",
                "keyId": "producer-key",
            },
        )
        verdict = self._verify(bundle, acceptance)
        self.assertEqual(verdict.outcome, FAILED)
        self.assertTrue(any("not separate authorities" in f for f in verdict.failures))

    # -- binding and signatures -------------------------------------------

    def test_an_acceptance_bound_to_another_artifact_is_refused(self) -> None:
        bundle = _bundle()
        acceptance = _acceptance("sha256:" + "9" * 64, self.key)
        verdict = self._verify(bundle, acceptance)
        self.assertEqual(verdict.outcome, FAILED)
        self.assertTrue(any("different artifact" in f for f in verdict.failures))

    def test_a_forged_acceptance_signature_is_refused(self) -> None:
        bundle = _bundle()
        digest = parse_envelope(bundle).digest()
        acceptance = _acceptance(digest, self.key)
        acceptance["signature"] = "ed25519:" + base64.b64encode(b"\x00" * 64).decode()
        verdict = self._verify(bundle, acceptance)
        self.assertEqual(verdict.outcome, FAILED)
        self.assertTrue(any("does not verify" in f for f in verdict.failures))

    def test_a_signature_from_the_wrong_key_is_refused(self) -> None:
        bundle = _bundle()
        digest = parse_envelope(bundle).digest()
        acceptance = _acceptance(digest, ed25519.Ed25519PrivateKey.generate())
        other = ed25519.Ed25519PrivateKey.generate().public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        acceptance["environment"]["reviewerPublicKey"] = base64.b64encode(other).decode()
        verdict = self._verify(bundle, acceptance)
        self.assertEqual(verdict.outcome, FAILED)

    def test_an_unsigned_producer_envelope_is_refused(self) -> None:
        verdict = self._verify(_bundle(signature=""))
        self.assertEqual(verdict.outcome, FAILED)

    def test_a_missing_acceptance_is_refused(self) -> None:
        verdict = self._verify(_bundle(), acceptance=None)
        self.assertEqual(verdict.outcome, FAILED)
        self.assertTrue(any("no independent acceptance" in f for f in verdict.failures))

    # -- undeterminable is distinct from both -----------------------------

    def test_a_dirty_tree_is_undeterminable_not_passed(self) -> None:
        bundle = _bundle()
        bundle["pins"] = {**bundle["pins"], "dirty": True}
        verdict = self._verify(bundle)
        self.assertEqual(verdict.outcome, UNDETERMINABLE)
        self.assertNotEqual(verdict.outcome, PASSED)
        self.assertTrue(any("dirty at capture" in u for u in verdict.unresolved))

    def test_an_unresolvable_material_is_undeterminable_not_failed(self) -> None:
        """A material nobody can locate is unobserved, not disproved."""
        bundle = _bundle()
        bundle["materials"] = [{"name": "ledger", "digest": "sha256:" + "a" * 64}]
        verdict = self._verify(bundle)
        self.assertEqual(verdict.outcome, UNDETERMINABLE)
        self.assertNotEqual(verdict.outcome, FAILED)

    def test_a_clean_fully_bound_bundle_passes(self) -> None:
        """Fail-closed, not closed to everything."""
        verdict = self._verify(_bundle())
        self.assertEqual(verdict.outcome, PASSED, verdict.failures + verdict.unresolved)


class CanonicalEvidenceStateIsReportedTruthfully(unittest.TestCase):
    """What the repository's own evidence currently verifies as."""

    def test_m4_m5b_m6_are_not_accepted(self) -> None:
        evidence = _ROOT / "docs" / "03_execution" / "evidence"
        for name in (
            "M-4-rf95-candidate-03.json",
            "M-5b-graph-coloring.json",
            "M-6-canonical-recursion.json",
        ):
            with self.subTest(bundle=name):
                verdict = verify_bundle(evidence / name)
                self.assertNotEqual(
                    verdict.outcome,
                    PASSED,
                    f"{name} reports outcome {verdict.claimed_outcome!r} but its "
                    f"acceptance record claims 'passed'; that must not verify",
                )

    def test_m65_disposition_is_preserved(self) -> None:
        """Order 10: the accepted M-6.5 disposition is not overturned here.

        Its bundle and acceptance are internally consistent and independently
        reviewed. The verifier reports `undeterminable` only because the
        bundle's materials are not uniformly content-addressed, which is a
        packaging gap, not a negative result about the study.
        """
        verdict = verify_bundle(
            _ROOT / "docs" / "03_execution" / "evidence"
            / "M-6.5-attributable-paired-study.json"
        )
        self.assertEqual(verdict.claimed_outcome, "passed")
        self.assertEqual(verdict.failures, [])
        self.assertEqual(verdict.outcome, UNDETERMINABLE)


if __name__ == "__main__":
    unittest.main()
