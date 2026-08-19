"""Pack-local evaluation gate. Planner never grades; only signed verdicts count."""

from __future__ import annotations

import hashlib
import json
from typing import ClassVar, Sequence

from cryptography.hazmat.primitives.asymmetric import ed25519

from layer0.spi.result import Err, Ok, Result
from layer0.spi.types_gen import (
    EvaluationRequestId,
    EvaluationSubject,
    GateDecision,
    OracleSpec,
    PreregistrationId,
    SignedVerdict,
)

__all__ = ["PackOracleGate", "sign_verdict", "verify_verdict"]


def sign_verdict(verdict: dict, private_key: bytes) -> str:
    key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key)
    payload = json.dumps(verdict, sort_keys=True, separators=(",", ":")).encode("utf-8")
    import base64
    return base64.b64encode(key.sign(payload)).decode("ascii")


def verify_verdict(verdict: dict, signature: str, public_key: bytes) -> bool:
    import base64
    try:
        key = ed25519.Ed25519PublicKey.from_public_bytes(public_key)
        payload = json.dumps(verdict, sort_keys=True, separators=(",", ":")).encode("utf-8")
        key.verify(base64.b64decode(signature, validate=True), payload)
        return True
    except Exception:
        return False


class PackOracleGate:
    spi_version: ClassVar[str] = "1.0"

    def __init__(self, *, public_key: bytes | None = None) -> None:
        self._public_key = public_key
        self._n = 0
        self.requested: list[EvaluationSubject] = []

    def request(self, subject: EvaluationSubject) -> Result[EvaluationRequestId]:
        self.requested.append(subject)
        self._n += 1
        return Ok(f"eval-{self._n}")

    def gate(self, verdicts: Sequence[SignedVerdict]) -> GateDecision:
        if not verdicts:
            return GateDecision.ABANDON
        signed = [item for item in verdicts if item.signature and item.signature != "unsigned"]
        if not signed:
            return GateDecision.ABANDON
        if self._public_key is not None:
            accepted: list[SignedVerdict] = []
            for item in signed:
                body = {"outcome": item.verdict}
                if verify_verdict(body, item.signature, self._public_key):
                    accepted.append(item)
            if not accepted:
                return GateDecision.ABANDON
            signed = accepted
        outcomes = {item.verdict.lower() for item in signed}
        if "pass" in outcomes:
            return GateDecision.PASS
        if "fail" in outcomes:
            return GateDecision.RETRY
        return GateDecision.ESCALATE

    def preregister(self, oracle: OracleSpec) -> Result[PreregistrationId]:
        if not oracle.id:
            return Err("invalid_request", "oracle id required")
        return Ok(oracle.id)


def oracle_digest(body: bytes) -> str:
    return "sha256:" + hashlib.sha256(body).hexdigest()
