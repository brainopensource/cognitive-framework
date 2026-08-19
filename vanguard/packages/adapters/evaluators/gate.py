"""Agent-side IEvaluationGate: UDS client to the exterior signed evaluator."""

from __future__ import annotations

import socket
from typing import Any, ClassVar, Sequence

from layer0.spi import jsonrpc
from layer0.spi.result import Err, Ok, Result
from layer0.spi.types_gen import (
    EvaluationRequestId,
    EvaluationSubject,
    GateDecision,
    OracleSpec,
    PreregistrationId,
    SignedVerdict,
)
from vanguard.packages.adapters.evaluators.signing import VerdictSigner

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
        verdict = result.get("verdict")
        signature = result.get("signature")
        key_id = result.get("keyId")
        if key_id != self._key_id or not isinstance(verdict, dict) or not isinstance(signature, str):
            return Err("instrument_error", "evaluator_verdict_unverified", instrument_error=True)
        if not VerdictSigner.verify(verdict, signature, self._public_key):
            return Err("instrument_error", "evaluator_verdict_unverified", instrument_error=True)
        return Ok(f"eval-{self._n}")

    def gate(self, verdicts: Sequence[SignedVerdict]) -> GateDecision:
        if not verdicts:
            return GateDecision.ABANDON
        outcomes = {item.verdict.lower() for item in verdicts}
        if "pass" in outcomes:
            return GateDecision.PASS
        if "fail" in outcomes:
            return GateDecision.RETRY
        if "escalate" in outcomes:
            return GateDecision.ESCALATE
        return GateDecision.ABANDON

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
