"""Adversarial evaluator verdict signature tests."""

from __future__ import annotations

import json
import unittest

from vanguard.packages.adapters.evaluators.signing import (
    VerdictSigner,
    canonical_verdict_bytes,
)


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

    def test_non_bmp_key_order_is_jcs_not_json_dumps(self) -> None:
        """ADR-0076 §3: `json.dumps(sort_keys=True)` sorts object keys by
        Python codepoint order; JCS sorts by UTF-16 code unit. A key in the
        BMP above U+DFFF and a non-BMP (surrogate-pair) key land in opposite
        order under the two schemes, so the two byte sources disagree here —
        exactly the drift this signer must not reproduce.
        """
        payload = {"￿": 1, "\U00010000": 2}
        json_bytes = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        self.assertNotEqual(canonical_verdict_bytes(payload), json_bytes)

        signer = VerdictSigner(b"s" * 32, "eval-1")
        signature = signer.sign(payload)
        self.assertTrue(VerdictSigner.verify(payload, signature, signer.public_bytes))
        # Reordering the same keys must not change the JCS-canonical body.
        reordered = {"\U00010000": 2, "￿": 1}
        self.assertTrue(VerdictSigner.verify(reordered, signature, signer.public_bytes))


if __name__ == "__main__":
    unittest.main()
