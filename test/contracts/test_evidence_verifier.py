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

import verify_evidence  # noqa: E402
from verify_evidence import FAILED, PASSED, UNDETERMINABLE, verify_bundle  # noqa: E402


def _sign(body: dict, key: ed25519.Ed25519PrivateKey) -> dict:
    """Sign an envelope body the way its producer or reviewer would."""
    envelope = parse_envelope({**body, "signature": ""})
    signature = key.sign(canonical_bytes(envelope.body()))
    return {**body, "signature": "ed25519:" + base64.b64encode(signature).decode("ascii")}


def _public(key: ed25519.Ed25519PrivateKey) -> str:
    return base64.b64encode(
        key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
    ).decode("ascii")


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
        self.producer_key = ed25519.Ed25519PrivateKey.generate()
        self.tmp = Path(self.enterContext(__import__("tempfile").TemporaryDirectory()))
        # The verifier trusts keys its own lane registered, so a test that wants
        # a clean bundle to pass must register the keys that bundle is signed
        # with. Nothing here is read from the envelopes under test.
        trust_root = self.tmp / "trust_root.json"
        trust_root.write_text(json.dumps({
            "schema": "aether.evidence.trust-root/1",
            "producers": {
                "producer-key": {"identity": "dev-b", "publicKey": _public(self.producer_key)},
            },
            "reviewers": {
                "reviewer-key": {
                    "identity": "independent-reviewer", "publicKey": _public(self.key),
                },
            },
        }), encoding="utf-8")
        self._patch_trust_root(trust_root)

    def _patch_trust_root(self, path: Path) -> None:
        original = verify_evidence.TRUST_ROOT_PATH
        verify_evidence.TRUST_ROOT_PATH = path
        self.addCleanup(setattr, verify_evidence, "TRUST_ROOT_PATH", original)

    def _write(self, bundle: dict, acceptance: dict | None) -> Path:
        path = self.tmp / "TEST-01.json"
        path.write_text(json.dumps(bundle), encoding="utf-8")
        if acceptance is not None:
            path.with_name(path.name + ".acceptance.json").write_text(
                json.dumps(acceptance), encoding="utf-8"
            )
        return path

    def _verify(self, bundle: dict, acceptance: dict | None = "auto"):
        if bundle.get("signature") == "producer-signature":
            bundle = _sign(bundle, self.producer_key)
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

    # -- B-O10-02: the trust root, not the document, names the authority ---

    def test_an_acceptance_signed_by_an_unregistered_reviewer_is_undeterminable(self) -> None:
        """Minting a fresh keypair per bundle must not manufacture a reviewer.

        The self-supplied ``reviewerPublicKey`` verifies perfectly against its
        own signature, which is exactly why it cannot be the authority: anyone
        who can write the acceptance can also generate the key that signs it.
        """
        bundle = _bundle()
        signed = _sign(bundle, self.producer_key)
        digest = parse_envelope(signed).digest()
        stranger = ed25519.Ed25519PrivateKey.generate()
        acceptance = _acceptance(
            digest, stranger,
            producer={
                "identity": "order9-independent-verifier",
                "role": "reviewer",
                "keyId": "freshly-minted-reviewer",
            },
        )
        verdict = verify_bundle(self._write(signed, acceptance))
        self.assertEqual(verdict.outcome, UNDETERMINABLE)
        self.assertTrue(
            any("not registered in the verifier trust root" in u
                for u in verdict.unresolved), verdict.unresolved,
        )

    def test_a_registered_reviewer_id_signed_by_another_key_is_refused(self) -> None:
        """Claiming a registered keyId while signing with a different key."""
        bundle = _bundle()
        signed = _sign(bundle, self.producer_key)
        digest = parse_envelope(signed).digest()
        impostor = ed25519.Ed25519PrivateKey.generate()
        acceptance = _acceptance(digest, impostor)  # keyId stays 'reviewer-key'
        verdict = verify_bundle(self._write(signed, acceptance))
        self.assertEqual(verdict.outcome, FAILED)
        self.assertTrue(
            any("not the one registered" in f or "does not verify" in f
                for f in verdict.failures), verdict.failures,
        )

    def test_an_unregistered_producer_key_is_undeterminable(self) -> None:
        bundle = _bundle()
        bundle["producer"] = {"identity": "dev-b", "role": "producer", "keyId": "unknown-key"}
        verdict = self._verify(_sign(bundle, self.producer_key))
        self.assertEqual(verdict.outcome, UNDETERMINABLE)
        self.assertTrue(
            any("is not registered" in u for u in verdict.unresolved), verdict.unresolved,
        )

    def test_a_forged_producer_signature_is_refused(self) -> None:
        """A present-but-wrong producer signature is decidably negative."""
        bundle = _bundle()
        bundle = _sign(bundle, ed25519.Ed25519PrivateKey.generate())
        verdict = verify_bundle(self._write(
            bundle, _acceptance(parse_envelope(bundle).digest(), self.key)))
        self.assertEqual(verdict.outcome, FAILED)
        self.assertTrue(
            any(f.startswith("producer signature does not verify") for f in verdict.failures),
            verdict.failures,
        )

    # -- B-O10-03: bundle-local bytes may satisfy outputs, never sources ---

    def test_a_source_material_cannot_be_satisfied_from_beside_the_bundle(self) -> None:
        """The substitution the artifactRoot fence exists to stop.

        Resolving source refs at the pinned commit is what ties evidence to the
        code that ran. If any relative ref could also resolve from the bundle
        directory, a producer could drop a hand-written ``root.py`` next to the
        envelope and satisfy a runtime material the pinned commit never had.
        """
        payload = b"# not the runtime that ran\n"
        planted = self.tmp / "vanguard" / "packages" / "runtime"
        planted.mkdir(parents=True)
        (planted / "root.py").write_bytes(payload)
        import hashlib
        bundle = _bundle()
        bundle["pins"] = {**bundle["pins"], "artifactRoot": "artifacts/TEST-01"}
        bundle["materials"] = [{
            "name": "runtime",
            "ref": "vanguard/packages/runtime/root.py",
            "digest": "sha256:" + hashlib.sha256(payload).hexdigest(),
        }]
        verdict = self._verify(bundle)
        self.assertEqual(verdict.outcome, UNDETERMINABLE)
        self.assertTrue(
            any("does not resolve at pinned commit" in u for u in verdict.unresolved),
            verdict.unresolved,
        )

    def test_a_run_output_under_the_artifact_root_does_resolve(self) -> None:
        """Fenced, not closed: portable outputs still verify from the bundle."""
        import hashlib
        payload = b'{"failures": 0}\n'
        artifacts = self.tmp / "artifacts" / "TEST-01"
        artifacts.mkdir(parents=True)
        (artifacts / "report.json").write_bytes(payload)
        bundle = _bundle()
        bundle["pins"] = {**bundle["pins"], "artifactRoot": "artifacts/TEST-01"}
        bundle["materials"] = [{
            "name": "report",
            "ref": "artifacts/TEST-01/report.json",
            "digest": "sha256:" + hashlib.sha256(payload).hexdigest(),
        }]
        verdict = self._verify(bundle)
        self.assertEqual(verdict.outcome, PASSED, verdict.failures + verdict.unresolved)

    def test_a_bundle_declaring_no_artifact_root_resolves_nothing_locally(self) -> None:
        import hashlib
        payload = b'{"failures": 0}\n'
        artifacts = self.tmp / "artifacts" / "TEST-01"
        artifacts.mkdir(parents=True)
        (artifacts / "report.json").write_bytes(payload)
        bundle = _bundle()
        bundle["materials"] = [{
            "name": "report",
            "ref": "artifacts/TEST-01/report.json",
            "digest": "sha256:" + hashlib.sha256(payload).hexdigest(),
        }]
        verdict = self._verify(bundle)
        self.assertEqual(verdict.outcome, UNDETERMINABLE)

    # -- the digest scheme is what makes tampering decidable ---------------

    def _material_bundle(self, payload: bytes, digest: str, **material) -> dict:
        """A bundle whose single material resolves under the artifact root."""
        artifacts = self.tmp / "artifacts" / "TEST-01"
        artifacts.mkdir(parents=True, exist_ok=True)
        (artifacts / "report.json").write_bytes(payload)
        bundle = _bundle()
        bundle["pins"] = {**bundle["pins"], "artifactRoot": "artifacts/TEST-01"}
        bundle["materials"] = [{
            "name": "report",
            "ref": "artifacts/TEST-01/report.json",
            "digest": digest,
            **material,
        }]
        return bundle

    def test_a_tampered_material_under_a_declared_scheme_is_a_decidable_failure(self) -> None:
        """Declaring `scheme` is what turns a mismatch into a negative.

        The bundle says exactly how it hashed, so a verifier that re-derives a
        different value knows the bytes changed -- it is not guessing at an
        unfamiliar convention. That is the whole reason the field exists.
        """
        import hashlib
        claimed = "sha256:" + hashlib.sha256(b'{"failures": 0}\n').hexdigest()
        verdict = self._verify(self._material_bundle(
            b'{"failures": 99}\n', claimed, scheme="raw-sha256"))
        self.assertEqual(verdict.outcome, FAILED)
        self.assertTrue(
            any("digest mismatch" in f and "raw-sha256" in f for f in verdict.failures),
            verdict.failures,
        )

    def test_a_material_with_no_scheme_is_undeterminable_never_passed(self) -> None:
        """Without `scheme`, a mismatch is unreadable -- and unreadable is not a pass.

        The verifier cannot tell a changed material from a hashing convention it
        does not implement, so it must decline to decide. The repair is to
        record the scheme, not to loosen the comparison.
        """
        verdict = self._verify(self._material_bundle(
            b'{"failures": 0}\n', "sha256:" + "0" * 64))
        self.assertEqual(verdict.outcome, UNDETERMINABLE)
        self.assertEqual(verdict.failures, [])
        self.assertTrue(
            any("records no digest scheme" in u for u in verdict.unresolved),
            verdict.unresolved,
        )

    def test_a_raw_hex_producer_signature_is_refused_not_accepted(self) -> None:
        """The historical hex format names no algorithm, so it cannot be checked.

        Every bundle signed before the producer tooling was fixed carries a bare
        hex signature. Guessing that it is Ed25519 over the canonical body would
        make the prefix decorative; refusing it is what forced the re-emission.
        """
        signed = _sign(_bundle(), self.producer_key)
        raw = base64.b64decode(signed["signature"].removeprefix("ed25519:"))
        verdict = self._verify({**signed, "signature": raw.hex()})
        self.assertEqual(verdict.outcome, FAILED)
        self.assertTrue(
            any("unsupported signature format" in f for f in verdict.failures),
            verdict.failures,
        )

    def test_a_clean_fully_bound_bundle_passes(self) -> None:
        """Fail-closed, not closed to everything."""
        verdict = self._verify(_bundle())
        self.assertEqual(verdict.outcome, PASSED, verdict.failures + verdict.unresolved)


class CanonicalEvidenceStateIsReportedTruthfully(unittest.TestCase):
    """What the repository's own evidence currently verifies as."""

    def test_m4_m5b_m6_are_not_accepted(self) -> None:
        evidence = _ROOT / "docs" / "execution" / "evidence"
        if not evidence.exists():
            self.skipTest("No evidence directory present")
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
        bundle_path = _ROOT / "docs" / "execution" / "evidence" / "M-6.5-attributable-paired-study.json"
        if not bundle_path.exists():
            self.skipTest("M-6.5 evidence bundle is not present")
        verdict = verify_bundle(bundle_path)
        self.assertEqual(verdict.claimed_outcome, "passed")
        self.assertEqual(verdict.failures, [])
        self.assertEqual(verdict.outcome, UNDETERMINABLE)


if __name__ == "__main__":
    unittest.main()
