"""Adversarial evaluator verdict signature tests."""

from __future__ import annotations

import unittest

from vanguard.packages.adapters.evaluators.signing import VerdictSigner


class VerdictSigningContract(unittest.TestCase):
    def test_signature_verifies_only_for_exact_payload(self) -> None:
        signer = VerdictSigner(b"s" * 32, "eval-1")
        payload = {"outcome": "claims", "claims": [{"status": "passed"}], "reason": ""}
        signature = signer.sign(payload)
        self.assertTrue(VerdictSigner.verify(payload, signature, signer.public_bytes))
        self.assertFalse(VerdictSigner.verify({**payload, "reason": "tampered"}, signature, signer.public_bytes))

    def test_wrong_key_and_malformed_signature_fail(self) -> None:
        signer = VerdictSigner(b"s" * 32, "eval-1")
        payload = {"outcome": "inconclusive", "claims": [], "reason": "timeout"}
        signature = signer.sign(payload)
        other = VerdictSigner(b"t" * 32, "eval-2")
        self.assertFalse(VerdictSigner.verify(payload, signature, other.public_bytes))
        self.assertFalse(VerdictSigner.verify(payload, "not-base64", signer.public_bytes))


if __name__ == "__main__":
    unittest.main()
