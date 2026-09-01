"""Agent-side IEvaluationGate: UDS client to the exterior signed evaluator."""

from __future__ import annotations

import socket
from typing import Any, ClassVar, Sequence

from vanguard.packages.adapters.evaluators.signing import VerdictSigner
from vanguard.packages.domain.wire import jsonrpc
from vanguard.packages.domain.wire.result import Err, Ok, Result
from vanguard.packages.domain.wire.types_gen import (
    EvaluationRequestId,
    EvaluationSubject,
    GateDecision,
    OracleSpec,
    PreregistrationId,
    SignedVerdict,
)

__all__ = ["ExteriorJudgeAdapter"]


class ExteriorJudgeAdapter:
    spi_version: ClassVar[str] = "1.0"

    def __init__(
        self,
        socket_path: str,
        *,
        public_key: bytes,
        key_id: str,
        timeout: float = 2.0,
    ) -> None:
        self._socket_path = socket_path
        self._public_key = public_key
        self._key_id = key_id
        self._timeout = timeout
        self._rpc_id = 0
        self._n = 0

    def request(self, subject: EvaluationSubject) -> Result[EvaluationRequestId]:
        """Submit the evaluation and hand back its id -- nothing more.

        `ADR-0076 §5`: verifying and then discarding the verdict here (the
        pre-Wave-1 shape) is exactly the "verified verdict discarded" defect.
        Whether the response was actually signed by `self._key_id` is decided
        once, on read, by `gate()` -- checking it twice on the same bytes
        would not add a second independent judge, only a second place this
        class could silently disagree with itself.
        """
        self._rpc_id += 1
        self._n += 1
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.settimeout(self._timeout)
                sock.connect(self._socket_path)
                sock.sendall(
                    jsonrpc.dumps_request(
                        self._rpc_id,
                        "evaluate",
                        {
                            "subject": {
                                "run_id": subject.run_id,
                                "episode_id": subject.episode_id,
                                "artifact_digest": subject.artifact_digest,
                            }
                        },
                    )
                )
                raw = _read_frame(sock)
            message = jsonrpc.loads(raw)
        except OSError as exc:
            return Err("instrument_error", str(exc), instrument_error=True)
        if "error" in message:
            error = message["error"]
            text = str(error.get("message") if isinstance(error, dict) else error)
            return Err("instrument_error", text, instrument_error=True)
        result = message.get("result")
        if not isinstance(result, dict):
            return Err("instrument_error", "malformed verdict", instrument_error=True)
        if not isinstance(result.get("verdict"), dict) or not isinstance(result.get("signature"), str):
            return Err("instrument_error", "malformed verdict", instrument_error=True)
        return Ok(f"eval-{self._n}")

    def gate(self, verdicts: Sequence[SignedVerdict]) -> GateDecision:
        """Decide from ledgered `SignedVerdict` rows -- the reader half of
        `ADR-0076 §5` (F-03/F-08): every verdict here is re-verified against
        this evaluator's own key before it may contribute to a decision. A
        verdict whose signature does not cover exactly these binding fields
        (tampered, unbound, or signed by a different key) is worth nothing --
        it neither passes nor blocks, it is simply not evidence.
        """
        trusted = [item for item in verdicts if self._verified(item)]
        if not trusted:
            return GateDecision.ABANDON
        outcomes = {item.verdict.lower() for item in trusted}
        if "pass" in outcomes:
            return GateDecision.PASS
        if "fail" in outcomes:
            return GateDecision.RETRY
        if "escalate" in outcomes:
            return GateDecision.ESCALATE
        return GateDecision.ABANDON

    def _verified(self, item: SignedVerdict) -> bool:
        if item.key_id is not None and item.key_id != self._key_id:
            return False
        body = {
            key: value for key, value in {
                "verdict": item.verdict,
                "subject_digest": item.subject_digest,
                "evaluation_request_id": item.evaluation_request_id,
                "oracle_id": item.oracle_id,
                "nonce": item.nonce,
                "key_id": item.key_id,
                "signed_at": item.signed_at,
            }.items() if value is not None
        }
        return VerdictSigner.verify(body, item.signature, self._public_key)

    def preregister(self, oracle: OracleSpec) -> Result[PreregistrationId]:
        return Ok(oracle.id)


def _read_frame(sock: socket.socket) -> bytes:
    buf = b""
    while b"\n" not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
    return buf
