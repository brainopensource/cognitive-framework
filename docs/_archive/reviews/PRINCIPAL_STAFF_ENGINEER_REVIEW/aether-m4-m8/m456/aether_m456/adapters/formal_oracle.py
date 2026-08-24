"""M-5 exterior formal oracle. Separately isolated identity.

CRITICAL: the oracle REPLAYS the proof term. It does not re-solve.
If it re-ran the solver it would be the prover again, and the verdict
would be self-issued -- which fails the exterior-truth law (001_alfa L4).
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Any, Mapping
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey)
from cryptography.exceptions import InvalidSignature
from ..runtime.memo import jcs, digest_of

@dataclass(frozen=True, slots=True)
class SignedVerdict:
    body: Mapping[str, Any]
    signature: bytes
    key_id: str
    def verify(self, pub: Ed25519PublicKey) -> bool:
        try:
            pub.verify(self.signature, jcs(self.body)); return True
        except InvalidSignature:
            return False

class FormalOracle:
    def __init__(self, key: Ed25519PrivateKey, key_id: str, checker) -> None:
        self._k, self.key_id, self._checker = key, key_id, checker

    @property
    def public_key(self) -> Ed25519PublicKey:
        return self._k.public_key()

    def evaluate(self, run_ref, protocol) -> SignedVerdict:
        # 1. preregistration must predate the first run event
        if protocol.preregistration_digest != run_ref.preregistration_digest:
            return self._sign(run_ref, protocol, "invalid",
                              "preregistration_mismatch")
        # 2. replay the proof against the preregistered theorem
        ok = self._checker.check(protocol.theorem, run_ref.proof_bytes)
        return self._sign(run_ref, protocol,
                          "pass" if ok else "fail",
                          None if ok else "proof_did_not_replay")

    def _sign(self, run_ref, protocol, outcome, reason) -> SignedVerdict:
        body = {                       # every binding the auditor recomputes
            "api": "mhf.verdict/1",
            "outcome": outcome, "reason": reason,
            "subject": run_ref.D_X, "harness": run_ref.D_H, "run": run_ref.D_R,
            "runId": run_ref.run_id, "episodeId": run_ref.episode_id,
            "taskDigest": protocol.task_digest,
            "oracleDigest": protocol.oracle_digest,
            "preregistrationDigest": protocol.preregistration_digest,
            "protocol": protocol.name, "keyId": self.key_id,
        }
        return SignedVerdict(body, self._k.sign(jcs(body)), self.key_id)
