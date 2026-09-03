"""Evaluator client: connects to the evaluator daemon over authenticated IPC.

Owning contract: S6B-MD-007, VG-05 §6.
This client implements the EvaluatorPort protocol and delegates to the
separately supervised daemon process.
"""

from __future__ import annotations

import json
import socket
import struct
import base64
from typing import Any, Mapping

from vanguard.packages.ports.evaluator import EvaluationProtocol, EvaluatorPort, RunRef, Verdict
from vanguard.packages.ports.event_store import Result
from vanguard.packages.adapters.evaluators.signing import VerdictSigner

__all__ = ["EvaluatorClient"]


class EvaluatorClient(EvaluatorPort):
    def __init__(
        self,
        socket_path: str,
        expected_uid: int,
        expected_image_digest: str,
        timeout_seconds: float,
        expected_verdict_key_id: str | None = None,
        expected_verdict_public_key: bytes | None = None,
    ) -> None:
        self._socket_path = socket_path
        self._expected_uid = expected_uid
        self._expected_image_digest = expected_image_digest
        self._timeout_seconds = timeout_seconds
        self._expected_verdict_key_id = expected_verdict_key_id
        self._expected_verdict_public_key = expected_verdict_public_key

    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol) -> Result[Verdict]:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.settimeout(self._timeout_seconds)
                sock.connect(self._socket_path)

                creds = sock.getsockopt(
                    socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i")
                )
                pid, uid, gid = struct.unpack("3i", creds)

                if uid != self._expected_uid:
                    return self._inconclusive("evaluator_identity_unverified")

                f = sock.makefile("r", encoding="utf-8", errors="strict")
                line = f.readline(65_537)
                if not line:
                    return self._inconclusive("evaluator_truncation")
                if len(line.encode("utf-8")) > 65_536:
                    return self._inconclusive("evaluator_truncation")

                try:
                    handshake = json.loads(line)
                except (UnicodeError, json.JSONDecodeError):
                    return self._inconclusive("evaluator_protocol_mismatch")
                if handshake.get("protocol") != "vg-eval-v1":
                    return self._inconclusive("evaluator_protocol_mismatch")
                if handshake.get("imageDigest") != self._expected_image_digest:
                    return self._inconclusive("evaluator_image_unverified")

                nonce = handshake.get("nonce")
                if self._expected_verdict_key_id is not None:
                    if handshake.get("verdictKeyId") != self._expected_verdict_key_id:
                        return self._inconclusive("evaluator_verdict_key_unverified")
                    try:
                        advertised_key = base64.b64decode(handshake.get("verdictPublicKey", ""), validate=True)
                    except Exception:
                        return self._inconclusive("evaluator_verdict_key_unverified")
                    if self._expected_verdict_public_key != advertised_key:
                        return self._inconclusive("evaluator_verdict_key_unverified")

                req = {
                    "action": "evaluate",
                    "runRef": {
                        "run_id": run_ref.run_id,
                        "episode_id": run_ref.episode_id,
                    },
                    "protocol": {
                        "name": protocol.name,
                        "parameters": protocol.parameters,
                    },
                    "nonce": nonce,
                }

                sock.sendall(json.dumps(req).encode("utf-8") + b"\n")

                resp_line = f.readline(65_537)
                if not resp_line:
                    return self._inconclusive("evaluator_truncation")
                if len(resp_line.encode("utf-8")) > 65_536:
                    return self._inconclusive("evaluator_truncation")

                try:
                    resp = json.loads(resp_line)
                except (UnicodeError, json.JSONDecodeError):
                    return self._inconclusive("evaluator_protocol_mismatch")
                if "error" in resp:
                    return self._inconclusive("instrument_error")

                # `v_data` is the exact JCS-signed body (ADR-0076 §5): the
                # bound `verdict` string plus binding fields, never the raw
                # `outcome`/`claims` evidence directly. Verifying it here is
                # verifying the same bytes the daemon signed.
                v_data = resp.get("verdict", {})
                signature = resp.get("signature")
                key_id = resp.get("keyId")
                binding: Mapping[str, Any] | None = None
                if self._expected_verdict_public_key is not None:
                    if key_id != self._expected_verdict_key_id or not isinstance(signature, str):
                        return self._inconclusive("evaluator_verdict_unverified")
                    if not VerdictSigner.verify(v_data, signature, self._expected_verdict_public_key):
                        return self._inconclusive("evaluator_verdict_unverified")
                    binding = v_data
                claims = tuple(resp.get("claims", ()))
                verdict = Verdict(
                    outcome="claims" if claims else "inconclusive",
                    claims=claims,
                    reason=resp.get("reason", ""),
                    signature=signature,
                    signer_key_id=key_id,
                    binding=binding,
                )
                return Result.success(verdict)

        except socket.timeout:
            return self._inconclusive("evaluator_timeout")
        except Exception:
            return self._inconclusive("instrument_error")

    def _inconclusive(self, reason: str) -> Result[Verdict]:
        return Result.success(Verdict(outcome="inconclusive", reason=reason))
