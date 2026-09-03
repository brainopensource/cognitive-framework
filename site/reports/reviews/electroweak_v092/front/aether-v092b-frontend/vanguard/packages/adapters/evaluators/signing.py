"""Evaluator-owned Ed25519 verdict signing and verification."""

from __future__ import annotations

import base64
from typing import Any, Mapping

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from ...domain.canonicalisation.jcs import canonical_bytes

__all__ = ["VerdictSigner", "canonical_verdict_bytes"]


def canonical_verdict_bytes(verdict: Mapping[str, Any]) -> bytes:
    """RFC 8785 JCS bytes of the verdict body (ADR-0076 §3, F-04).

    The domain JCS reader is the only canonicalisation/signing byte source in
    the system. `json.dumps(sort_keys=True)` agrees with it on ASCII but
    drifts on object-key order between a BMP code point above U+DFFF and any
    non-BMP (surrogate-pair) code point — JCS sorts by UTF-16 code unit, not
    by Python's codepoint order.
    """
    return canonical_bytes(dict(verdict))


class VerdictSigner:
    """Signer provisioned by the evaluator supervisor, never by the runtime."""

    def __init__(self, private_key: bytes, key_id: str) -> None:
        if not isinstance(private_key, bytes):
            raise TypeError("evaluator private key must be bytes")
        try:
            self._key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key)
        except ValueError as exc:
            raise ValueError("evaluator private key must be 32 raw bytes") from exc
        if not key_id:
            raise ValueError("evaluator key id is required")
        self.key_id = key_id

    @property
    def public_bytes(self) -> bytes:
        return self._key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )

    def sign(self, verdict: Mapping[str, Any]) -> str:
        return base64.b64encode(self._key.sign(canonical_verdict_bytes(verdict))).decode("ascii")

    @staticmethod
    def verify(verdict: Mapping[str, Any], signature: str, public_key: bytes) -> bool:
        try:
            key = ed25519.Ed25519PublicKey.from_public_bytes(public_key)
            key.verify(base64.b64decode(signature, validate=True), canonical_verdict_bytes(verdict))
            return True
        except Exception:
            return False
