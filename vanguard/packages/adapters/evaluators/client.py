"""Evaluator client: connects to the evaluator daemon over authenticated IPC.

Owning contract: S6B-MD-007, VG-05 §6.
This client implements the EvaluatorPort protocol and delegates to the
separately supervised daemon process.
"""

from __future__ import annotations

import json
import socket
import struct

from vanguard.packages.ports.evaluator import EvaluationProtocol, EvaluatorPort, RunRef, Verdict
from vanguard.packages.ports.event_store import Result

__all__ = ["EvaluatorClient"]


class EvaluatorClient(EvaluatorPort):
    def __init__(
        self,
        socket_path: str,
        expected_uid: int,
        expected_image_digest: str,
        timeout_seconds: float,
    ) -> None:
        self._socket_path = socket_path
        self._expected_uid = expected_uid
        self._expected_image_digest = expected_image_digest
        self._timeout_seconds = timeout_seconds

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

                f = sock.makefile("r", encoding="utf-8")
                line = f.readline()
                if not line:
                    return self._inconclusive("evaluator_truncation")

                handshake = json.loads(line)
                if handshake.get("protocol") != "vg-eval-v1":
                    return self._inconclusive("evaluator_protocol_mismatch")
                if handshake.get("imageDigest") != self._expected_image_digest:
                    return self._inconclusive("evaluator_image_unverified")

                nonce = handshake.get("nonce")

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

                resp_line = f.readline()
                if not resp_line:
                    return self._inconclusive("evaluator_crash")

                resp = json.loads(resp_line)
                if "error" in resp:
                    print(f"SERVER RETURNED ERROR: {resp['error']}")
                    return self._inconclusive("instrument_error")

                v_data = resp.get("verdict", {})
                verdict = Verdict(
                    outcome=v_data.get("outcome", "inconclusive"),
                    claims=tuple(v_data.get("claims", ())),
                    reason=v_data.get("reason", ""),
                )
                return Result.success(verdict)

        except socket.timeout:
            return self._inconclusive("evaluator_timeout")
        except Exception as e:
            import traceback
            traceback.print_exc()
            return self._inconclusive("instrument_error")

    def _inconclusive(self, reason: str) -> Result[Verdict]:
        return Result.success(Verdict(outcome="inconclusive", reason=reason))
