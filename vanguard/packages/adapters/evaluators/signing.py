"""Evaluator-owned Ed25519 verdict signing and verification."""

from __future__ import annotations

import base64
import json
from typing import Any, Mapping

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

__all__ = ["VerdictSigner", "canonical_verdict_bytes"]


def canonical_verdict_bytes(verdict: Mapping[str, Any]) -> bytes:
    return json.dumps(dict(verdict), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


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
