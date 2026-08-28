"""B-O10-04: evidence signing produces something the verifier can re-derive.

Before this, ``build_evidence_bundle.py`` emitted M-4 and M-6 envelopes with no
signature at all, and signed M-5b with a 32-byte private key literal in its own
source. The committed bundles nonetheless carried 128-hex ``signature`` fields
that no code path in this repository produces. Both shapes are unverifiable, and
an unverifiable signature is an unavailable verifier, not a pass.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import ed25519

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_ROOT / "tools" / "linters") not in sys.path:
    sys.path.insert(0, str(_ROOT / "tools" / "linters"))

from tools.runners.build_evidence_bundle import sign_envelope  # noqa: E402
from tools.runners.keygen_evidence_key import generate, load_key, public_b64  # noqa: E402
from vanguard.packages.domain.evidence.envelope import (  # noqa: E402
    EvidenceEnvelope,
    Producer,
    parse_envelope,
)
import verify_evidence  # noqa: E402
from verify_evidence import _verify_signature  # noqa: E402


def _envelope() -> EvidenceEnvelope:
    return EvidenceEnvelope(
        claim="TEST-01",
        protocol="aether.test/1",
        subjects=("milestone:TEST",),
        materials=(),
        run={},
        pins={"commit": "0" * 40, "tree": "1" * 40},
        environment={},
        outcome="passed",
        producer=Producer(identity="dev-b", key_id="placeholder"),
    )


class GeneratedKeysAreUsableAndPrivate(unittest.TestCase):
    def test_a_generated_key_is_owner_only_and_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path, public = generate("test-key", Path(directory) / "test.key")
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(public_b64(load_key(path)), public)

    def test_generating_over_an_existing_key_does_not_replace_it(self) -> None:
        """Silently rotating a key invalidates every signature it ever made."""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "test.key"
            _, first = generate("test-key", target)
            _, second = generate("test-key", target)
            self.assertEqual(first, second)


class SignaturesAreIndependentlyReDerivable(unittest.TestCase):
    def test_a_signed_envelope_verifies_against_the_public_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path, public = generate("producer", Path(directory) / "p.key")
            signed = sign_envelope(_envelope(), path, "producer-1")
            self.assertTrue(signed.signature.startswith("ed25519:"))
            self.assertEqual(signed.producer.key_id, "producer-1")
            self.assertIsNone(_verify_signature(signed, public))

    def test_an_unprefixed_signature_is_refused_rather_than_guessed(self) -> None:
        """The 128-hex shape the committed bundles carry names no algorithm."""
        with tempfile.TemporaryDirectory() as directory:
            path, public = generate("producer", Path(directory) / "p.key")
            signed = sign_envelope(_envelope(), path, "producer-1")
            bare = signed.signature.removeprefix("ed25519:")
            reason = _verify_signature(
                parse_envelope({**signed.to_wire(), "signature": bare}), public)
            self.assertIsNotNone(reason)
            self.assertIn("unsupported signature format", reason)

    def test_another_key_does_not_verify(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path, _ = generate("producer", Path(directory) / "p.key")
            signed = sign_envelope(_envelope(), path, "producer-1")
            stranger = public_b64(ed25519.Ed25519PrivateKey.generate())
            self.assertIsNotNone(_verify_signature(signed, stranger))


class EvidenceIsAdditive(unittest.TestCase):
    def test_the_builder_refuses_to_overwrite_an_existing_bundle(self) -> None:
        """Overwriting invalidates any acceptance bound to the old digest."""
        with tempfile.TemporaryDirectory() as directory:
            existing = Path(directory) / "M-6.json"
            existing.write_text("{}", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "tools/runners/build_evidence_bundle.py",
                 "--claim", "M-5b", "--out", str(existing)],
                cwd=_ROOT, capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing to overwrite", result.stdout + result.stderr)
            self.assertEqual(existing.read_text(encoding="utf-8"), "{}")


class TheTrustRootIsWellFormed(unittest.TestCase):
    def test_every_registered_key_is_a_usable_ed25519_public_key(self) -> None:
        root = json.loads(verify_evidence.TRUST_ROOT_PATH.read_text(encoding="utf-8"))
        seen: dict[str, str] = {}
        for kind in ("producers", "reviewers"):
            for key_id, entry in (root.get(kind) or {}).items():
                public = entry.get("publicKey")
                if public is None:
                    continue  # known identity, unpublished key: undeterminable
                with self.subTest(key=key_id):
                    import base64
                    ed25519.Ed25519PublicKey.from_public_bytes(
                        base64.b64decode(public, validate=True))
                    # One key serving two roles would make producer and reviewer
                    # the same authority under two names.
                    self.assertNotIn(public, seen, f"{key_id} reuses {seen.get(public)}'s key")
                    seen[public] = key_id


if __name__ == "__main__":
    unittest.main()
