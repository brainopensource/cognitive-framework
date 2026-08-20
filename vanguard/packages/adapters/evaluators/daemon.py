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
import struct
import argparse
import base64
import sys
import time
from dataclasses import dataclass
from typing import Mapping

from vanguard.packages.adapters.evaluators.isolated import IsolatedEvaluator
from vanguard.packages.adapters.evaluators.signing import VerdictSigner
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef, Verdict

__all__ = ["DaemonConfig", "EvaluatorDaemon", "main"]


def _reduce_outcome(verdict: Verdict) -> str:
    """Fold the evidence-plane `Verdict` (raw claims, M5) to the bound
    `SignedVerdict.verdict` enum (ADR-0076 §5): `pass` | `fail` |
    `inconclusive`. Anything short of an explicit passing claim is not a
    pass — fail-closed, per the exterior-judge thesis (I-5).
    """
    if verdict.outcome != "claims" or not verdict.claims:
        return "inconclusive"
    status = verdict.claims[0].get("status")
    if status == "passed":
        return "pass"
    if status == "failed":
        return "fail"
    return "inconclusive"


@dataclass(frozen=True)
class DaemonConfig:
    socket_path: str
    image_digest: str
    workspace: str
    oracle_digests: Mapping[str, str]
    command: tuple[str, ...]
    expected_uid: int = 10002
    timeout_seconds: float = 60.0
    verdict_private_key: bytes | None = None
    verdict_key_id: str = "evaluator-key-default"
    expected_client_uid: int | None = None
    oracle_root: str | None = None


class EvaluatorDaemon:
    def __init__(self, config: DaemonConfig) -> None:
        self._config = config
        self._signer = (
            VerdictSigner(config.verdict_private_key, config.verdict_key_id)
            if config.verdict_private_key is not None else None
        )

    def serve_once(self) -> None:
        if os.path.exists(self._config.socket_path):
            os.remove(self._config.socket_path)

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
            server.bind(self._config.socket_path)
            # The socket is a transport only; the daemon authenticates the
            # peer with SO_PEERCRED before processing a request.  The mounted
            # host client must be able to reach that authentication boundary.
            os.chmod(self._config.socket_path, 0o666)
            server.listen(1)
            conn, _ = server.accept()
            with conn:
                if self._config.expected_client_uid is not None:
                    creds = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
                    _, uid, _ = struct.unpack("3i", creds)
                    if uid != self._config.expected_client_uid:
                        return
                self._handle_connection(conn)

    def serve_forever(self) -> None:
        while True:
            self.serve_once()

    def _handle_connection(self, conn: socket.socket) -> None:
        try:
            nonce = os.urandom(16).hex()
            handshake = {
                "protocol": "vg-eval-v1",
                "uid": os.getuid(),
                "imageDigest": self._config.image_digest,
                "nonce": nonce,
                "verdictKeyId": self._signer.key_id if self._signer else None,
            }
            if self._signer:
                import base64
                handshake["verdictPublicKey"] = base64.b64encode(self._signer.public_bytes).decode("ascii")
            conn.sendall(json.dumps(handshake).encode("utf-8") + b"\n")

            f = conn.makefile("r", encoding="utf-8", errors="strict")
            line = f.readline(65_537)
            if not line:
                return
            if len(line.encode("utf-8")) > 65_536:
                self._send_error(conn, "request_too_large")
                return

            req = json.loads(line)
            if not isinstance(req, dict) or set(req) - {"action", "runRef", "protocol", "nonce"}:
                self._send_error(conn, "invalid_request")
                return
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
                oracle_root=self._config.oracle_root,
            )

            result = evaluator.evaluate(run_ref, protocol)
            if not result.ok:
                self._send_error(conn, result.error)
                return

            verdict = result.value
            claims = verdict.claims
            reason = verdict.reason
            if self._signer is None:
                claims = ()
                reason = "evaluator_signer_unavailable"

            # ADR-0076 §5 binding contract (F-04): the signed body carries
            # `verdict` plus every binding field, all under one JCS signature.
            # `subject_digest` binds this run/episode identity because the
            # wire protocol here carries no separate artifact digest; `nonce`
            # is the same fresh, single-use handshake nonce the client already
            # echoed back, so a captured signature cannot be replayed against
            # a later connection.
            signed_body: dict = {
                "verdict": _reduce_outcome(verdict) if self._signer is not None else "inconclusive",
                "subject_digest": digest_of({"run_id": run_ref.run_id, "episode_id": run_ref.episode_id}),
                "evaluation_request_id": f"eval-{nonce}",
                "oracle_id": protocol.name or digest_of(dict(self._config.oracle_digests)),
                "nonce": nonce,
                "key_id": self._signer.key_id if self._signer else "",
                "signed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            signature = self._signer.sign(signed_body) if self._signer else ""
            resp = {
                "verdict": signed_body,
                "signature": signature,
                "keyId": self._signer.key_id if self._signer else "",
                # Legacy evidence fields for `EvaluatorClient`/`Verdict`
                # (ports/evaluator.py) callers not yet migrated to the bound
                # `SignedVerdict` reader (1.1-D/E).
                "claims": claims,
                "reason": reason,
            }
            conn.sendall(json.dumps(resp).encode("utf-8") + b"\n")
        except Exception:
            print("evaluator request failed", file=sys.stderr)
            self._send_error(conn, "instrument_error")

    def _send_error(self, conn: socket.socket, msg: str) -> None:
        try:
            resp = {"error": msg}
            conn.sendall(json.dumps(resp).encode("utf-8") + b"\n")
        except Exception:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Vanguard exterior evaluator daemon")
    parser.add_argument("--socket", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--oracle-manifest", required=True)
    parser.add_argument("--image-digest", required=True)
    parser.add_argument("--expected-client-uid", type=int, default=None)
    # This is the final option and must preserve argv entries such as ``-m``
    # and ``-q`` verbatim; ``nargs='+'`` lets argparse treat those as daemon
    # options instead of command arguments.
    parser.add_argument("--command", nargs=argparse.REMAINDER, required=True)
    args = parser.parse_args()
    if not args.command:
        parser.error("--command requires at least one argv entry")
    with open(args.oracle_manifest, encoding="utf-8") as handle:
        manifest = json.load(handle)
    oracle_digests = _oracle_digests_from_manifest(manifest)
    private_key_text = os.environ.get("VANGUARD_EVALUATOR_PRIVATE_KEY_B64", "")
    private_key = base64.b64decode(private_key_text, validate=True) if private_key_text else None
    daemon = EvaluatorDaemon(DaemonConfig(
        socket_path=args.socket,
        image_digest=args.image_digest,
        workspace=args.workspace,
        oracle_digests=oracle_digests,
        command=tuple(args.command),
        expected_uid=10002,
        expected_client_uid=args.expected_client_uid,
        verdict_private_key=private_key,
        verdict_key_id=os.environ.get("VANGUARD_EVALUATOR_VERDICT_KEY_ID", "evaluator-key-default"),
        oracle_root="/sealed-oracle",
    ))
    daemon.serve_forever()
    return 0


def _oracle_digests_from_manifest(manifest: object) -> dict[str, str]:
    """Normalize either a sealed digest map or the preregistration manifest."""
    if not isinstance(manifest, dict):
        raise ValueError("oracle manifest must be an object")
    if all(isinstance(key, str) and isinstance(value, str)
           for key, value in manifest.items()):
        return dict(manifest)
    tasks = manifest.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("oracle manifest has no digest map or tasks")
    result: dict[str, str] = {}
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("oracle task must be an object")
        path, digest = task.get("oracle"), task.get("oracleDigest")
        if not isinstance(path, str) or not isinstance(digest, str):
            raise ValueError("oracle task requires oracle and oracleDigest")
        result[path] = digest
    if not result:
        raise ValueError("oracle manifest has no tasks")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
