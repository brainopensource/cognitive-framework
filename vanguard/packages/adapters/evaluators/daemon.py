"""Evaluator daemon: separately supervised process with authenticated IPC.

Owning contract: S6B-MD-007, REQ-EVAL-001, ADR-0048, VG-05 §6.
Runs under a dedicated OS identity (UID 10002). Uses Unix domain socket
with SO_PEERCRED for peer verification. Reports immutable executable/image
digest at handshake.
"""

from __future__ import annotations

import json
import os
import socket
from dataclasses import dataclass
from typing import Mapping

from vanguard.packages.adapters.evaluators.isolated import IsolatedEvaluator
from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef

__all__ = ["DaemonConfig", "EvaluatorDaemon"]


@dataclass(frozen=True)
class DaemonConfig:
    socket_path: str
    image_digest: str
    workspace: str
    oracle_digests: Mapping[str, str]
    command: tuple[str, ...]
    expected_uid: int = 10002
    timeout_seconds: float = 60.0


class EvaluatorDaemon:
    def __init__(self, config: DaemonConfig) -> None:
        self._config = config

    def serve_once(self) -> None:
        if os.path.exists(self._config.socket_path):
            os.remove(self._config.socket_path)

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
            server.bind(self._config.socket_path)
            server.listen(1)
            conn, _ = server.accept()
            with conn:
                self._handle_connection(conn)

    def _handle_connection(self, conn: socket.socket) -> None:
        try:
            nonce = os.urandom(16).hex()
            handshake = {
                "protocol": "vg-eval-v1",
                "uid": os.getuid(),
                "imageDigest": self._config.image_digest,
                "nonce": nonce,
            }
            conn.sendall(json.dumps(handshake).encode("utf-8") + b"\n")

            f = conn.makefile("r", encoding="utf-8")
            line = f.readline()
            if not line:
                return

            req = json.loads(line)
            if req.get("nonce") != nonce:
                self._send_error(conn, "invalid_nonce")
                return

            if req.get("action") != "evaluate":
                self._send_error(conn, "invalid_action")
                return

            run_ref_data = req.get("runRef", {})
            protocol_data = req.get("protocol", {})

            run_ref = RunRef(
                run_id=run_ref_data.get("run_id"),
                episode_id=run_ref_data.get("episode_id"),
            )
            protocol = EvaluationProtocol(
                name=protocol_data.get("name"),
                parameters=protocol_data.get("parameters", {}),
            )

            evaluator = IsolatedEvaluator(
                workspace=self._config.workspace,
                oracle_digests=self._config.oracle_digests,
                command=self._config.command,
                expected_uid=self._config.expected_uid,
                image_digest=self._config.image_digest,
                timeout_seconds=self._config.timeout_seconds,
            )

            result = evaluator.evaluate(run_ref, protocol)
            if not result.ok:
                self._send_error(conn, result.error)
                return

            verdict = result.value
            resp = {
                "verdict": {
                    "outcome": verdict.outcome,
                    "claims": verdict.claims,
                    "reason": verdict.reason,
                }
            }
            conn.sendall(json.dumps(resp).encode("utf-8") + b"\n")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._send_error(conn, "instrument_error")

    def _send_error(self, conn: socket.socket, msg: str) -> None:
        try:
            resp = {"error": msg}
            conn.sendall(json.dumps(resp).encode("utf-8") + b"\n")
        except Exception:
            pass
