"""HTTP and Server-Sent Events (SSE) Studio Gateway for the AETHER Observatory.

Connects the browser studio frontend directly to RuntimeService and the SQLite WAL
event stream with zero external dependencies (stdlib http.server & threading only).
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import sys
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.metadata import PackageNotFoundError, version as distribution_version
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import parse_qs, urlparse

from ...domain.primitives.primitives import uuidv7
from ..governance.approvals import OperatorSigner
from .server import MAX_FRAME_BYTES
from .service import RuntimeService, _utc_now

#: HTTP and UDS carry the same protocol and therefore enforce the same limit.
#: Two limits for one protocol means the looser transport is the real one.
MAX_BODY_BYTES = MAX_FRAME_BYTES

#: Where the composable harness manifests live, relative to a repository root.
_AGENCY_MANIFESTS = Path("vanguard") / "packages" / "agency" / "manifests"

#: Execution profiles the runtime actually presets. Anything else is an
#: agent name that reached the wrong field.
_EXECUTION_PROFILES = frozenset({"product", "local", "sandboxed", "hermetic",
                                 "standard", "ci", "fast", "code-default"})

#: Manifests ship with the runtime, so a workspace that is not this repository
#: still resolves `vg-code-default` instead of failing to find a harness.
_REPO_ROOT = Path(__file__).resolve().parents[4]

#: Workspace reads are mediated: only these suffixes may be dereferenced, and
#: only inside the resolved workspace root. Everything else goes through
#: `ExplainArtifact`, which is the audited path.
WORKSPACE_READ_SUFFIXES = frozenset({
    ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".txt", ".toml",
    ".yaml", ".yml", ".cfg", ".ini", ".sh", ".sql", ".rs", ".go",
})

#: Never served, regardless of suffix or location.
WORKSPACE_READ_DENYLIST = frozenset({
    ".env", ".env.local", "id_rsa", "id_ed25519", "credentials", ".netrc",
})


def _package_version() -> str:
    """Read the installed version whose source is ``pyproject.toml``."""
    try:
        return distribution_version("vanguard-runtime")
    except PackageNotFoundError:
        try:
            from vanguard import __version__
            return __version__
        except ImportError:
            return "0.9.0b1"


def _http_status_for_code(code: str) -> int:
    if code in ("invalid_request", "incompatible_version", "frame_too_large"):
        return HTTPStatus.BAD_REQUEST
    if code == "unauthenticated":
        return HTTPStatus.UNAUTHORIZED
    if code == "permission_denied":
        return HTTPStatus.FORBIDDEN
    if code == "not_found":
        return HTTPStatus.NOT_FOUND
    if code == "conflict":
        return HTTPStatus.CONFLICT
    if code == "rate_limited":
        return HTTPStatus.TOO_MANY_REQUESTS
    if code == "not_available":
        return HTTPStatus.SERVICE_UNAVAILABLE
    return HTTPStatus.INTERNAL_SERVER_ERROR


class StudioGatewayHandler(BaseHTTPRequestHandler):
    """HTTP and SSE request handler for the Studio Frontend."""

    server: StudioGatewayServer

    def _set_cors_headers(self) -> None:
        """Echo only a configured origin. Never a wildcard.

        This surface resolves approvals and launches runs; a wildcard here lets
        any page the operator happens to visit drive their runtime.
        """
        origin = self.headers.get("Origin", "")
        if origin and origin in getattr(self.server, "allowed_origins", ()):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, Last-Event-ID")

    def _authenticate(self) -> bool:
        """Resolve the caller, or send a canonical refusal and return False.

        Loopback with no configured tokens stays open for local development;
        `create_gateway` refuses to bind a non-loopback address in that state,
        so this cannot become an unauthenticated remote surface.
        """
        tokens = getattr(self.server, "auth_tokens", frozenset())
        if not tokens and getattr(self.server, "is_loopback", lambda: False)():
            return True

        header = self.headers.get("Authorization", "")
        presented = header[7:].strip() if header.lower().startswith("bearer ") else ""
        if presented and presented in tokens:
            return True

        self._send_error_code(
            "unauthenticated",
            "missing or invalid bearer token",
        )
        return False

    def _read_body(self) -> bytes | None:
        """Read a size-capped request body, or refuse and return None.

        The UDS transport has always enforced `MAX_FRAME_BYTES`; the same
        protocol over HTTP enforced nothing, so one transport could be used to
        submit frames the other would reject.
        """
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            self._send_error_code("invalid_request", "malformed Content-Length")
            return None
        if length < 0:
            self._send_error_code("invalid_request", "negative Content-Length")
            return None
        if length > MAX_BODY_BYTES:
            self._send_error_code(
                "frame_too_large", f"body exceeds {MAX_BODY_BYTES} bytes limit")
            return None
        return self.rfile.read(length) if length > 0 else b"{}"

    def _send_error_code(self, code: str, message: str) -> None:
        body = json.dumps({
            "error": {"code": code, "message": message, "retryable": False}
        }).encode("utf-8")
        self.send_response(_http_status_for_code(code))
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        query = parse_qs(parsed.query)

        # Health is the only unauthenticated route: a liveness probe that
        # requires a credential cannot report that credentials are misconfigured.
        if path not in ("/api/health", "/api/v1/health") and not self._authenticate():
            return

        if path in ("/api/health", "/api/v1/health"):
            self._handle_health()
        elif path in ("/api/capabilities", "/api/v1/capabilities"):
            self._handle_capabilities()
        elif path in ("/api/credentials", "/api/v1/credentials"):
            self._handle_credential_status()
        elif path in ("/api/runs", "/api/v1/runs"):
            self._handle_list_runs(query)
        elif path.startswith("/api/artifacts/") or path.startswith("/api/v1/artifacts/"):
            parts = path.split("/")
            artifact_id = parts[3] if path.startswith("/api/artifacts/") else parts[4]
            artifact_id = artifact_id.split(":")[0].split("/")[0]
            self._handle_explain_artifact(artifact_id, query)
        elif path.startswith("/api/runs/") or path.startswith("/api/v1/runs/"):
            parts = path.split("/")
            run_id = parts[3] if path.startswith("/api/runs/") else parts[4]
            if path.endswith("/events:stream") or path.endswith("/events"):
                self._handle_events_stream(run_id, query)
            else:
                self._handle_get_run(run_id)
        elif path == "/api/events/stream":
            run_id = query.get("runId", query.get("run_id", [""]))[0]
            self._handle_events_stream(run_id, query)
        elif path == "/api/workspace/file":
            self._handle_workspace_file(query)
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        # Order matters: cap, then authenticate, then parse. An unauthenticated
        # caller must not be able to make the server allocate or parse anything.
        body = self._read_body()
        if body is None:
            return
        if not self._authenticate():
            return
        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_error_code("invalid_request", "malformed JSON body")
            return
        if not isinstance(payload, Mapping):
            self._send_error_code("invalid_request", "request body must be a JSON object")
            return

        if path in ("/api/runs", "/api/v1/runs", "/api/runs/launch"):
            self._handle_launch_run(payload)
        elif path in ("/api/credentials:test", "/api/v1/credentials:test"):
            self._handle_credential_probe(payload)
        elif path in ("/api/approvals/resolve", "/api/v1/approvals/resolve") or (
            path.startswith("/api/v1/approvals/") and path.endswith(":resolve")
        ):
            approval_id = ""
            if path.startswith("/api/v1/approvals/") and path.endswith(":resolve"):
                approval_id = path[len("/api/v1/approvals/") : -len(":resolve")]
            self._handle_resolve_approval(payload, approval_id=approval_id)
        elif path in ("/api/artifacts/explain", "/api/v1/artifacts:explain", "/api/v1/artifacts/explain"):
            self._handle_explain_artifact_post(payload)
        elif path in ("/api/corrections", "/api/v1/corrections"):
            self._handle_record_correction("", payload)
        elif ":recordCorrection" in path or "/corrections" in path:
            run_id = path.split("/")[3].split(":")[0].split("/")[0] if path.startswith("/api/runs/") else path.split("/")[4].split(":")[0].split("/")[0]
            self._handle_record_correction(run_id, payload)
        elif ":cancel" in path:
            run_id = path.split("/")[3].split(":")[0] if path.startswith("/api/runs/") else path.split("/")[4].split(":")[0]
            self._handle_cancel(run_id, payload)
        elif ":checkpoint" in path:
            run_id = path.split("/")[3].split(":")[0] if path.startswith("/api/runs/") else path.split("/")[4].split(":")[0]
            self._handle_checkpoint(run_id, payload)
        elif ":resume" in path:
            run_id = path.split("/")[3].split(":")[0] if path.startswith("/api/runs/") else path.split("/")[4].split(":")[0]
            self._handle_resume(run_id, payload)
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

    # -- Handler Implementations ---------------------------------------

    def _handle_health(self) -> None:
        self.send_response(HTTPStatus.OK)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {
            "status": "ok",
            "service": "vanguard-studio-gateway",
            "version": _package_version(),
            "activeRuns": len(self.server.service._active_runs),
            "timestamp": _utc_now(),
        }
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def _handle_credential_status(self) -> None:
        """Report whether the runtime can load the provider key, and why not.

        The desktop pane used to render a hardcoded "CONFIGURED", which is how
        an operator ends up believing a key is saved when no key exists. This
        answers from the only authority there is -- the loader that the run
        path itself uses -- and carries a reason and a remedy, never a secret.
        """
        from ...adapters.models.credential_probe import credential_status

        self._send_plain_json(credential_status(self.server.workspace_root))

    def _handle_credential_probe(self, payload: Mapping[str, Any]) -> None:
        """Spend one token against the provider and report what came back."""
        from ...adapters.models.credential_probe import PROBE_MODEL, probe_provider

        model = str(payload.get("model") or PROBE_MODEL)
        self._send_plain_json(probe_provider(self.server.workspace_root, model=model))

    def _send_plain_json(self, data: Mapping[str, Any], status: int = HTTPStatus.OK) -> None:
        """Send a non-frame JSON body. Status endpoints are not run receipts."""
        self.send_response(status)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _handle_capabilities(self) -> None:
        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "GetCapabilities",
                "commandId": uuidv7(),
                "idempotencyKey": uuidv7(),
                "payload": {},
            },
        }
        res = self.server.service.execute_command(cmd_frame)
        self._send_json_response(res)

    def _handle_list_runs(self, query: Mapping[str, list[str]]) -> None:
        limit = int(query.get("limit", ["50"])[0])
        offset = int(query.get("offset", ["0"])[0])
        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "ListRuns",
                "commandId": uuidv7(),
                "idempotencyKey": uuidv7(),
                "payload": {"limit": limit, "offset": offset},
            },
        }
        res = self.server.service.execute_command(cmd_frame)
        self._send_json_response(res)

    def _handle_get_run(self, run_id: str) -> None:
        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "GetRun",
                "commandId": uuidv7(),
                "idempotencyKey": uuidv7(),
                "runId": run_id,
                "payload": {},
            },
        }
        res = self.server.service.execute_command(cmd_frame)
        self._send_json_response(res)

    def _handle_launch_run(self, payload: Mapping[str, Any]) -> None:
        brief = str(payload.get("brief") or "Interactive Studio Task")
        repo_path = str(payload.get("repoPath") or str(self.server.workspace_root))
        run_id = str(payload.get("runId") or f"run-studio-{uuidv7()[:8]}")

        # `_cmd_StartRun` only spawns a worker when the manifest resolves to a
        # real file, and `_run_worker_thread` reads `profileId`/`model` out of
        # this same payload. Defaulting to a bare "harness.yaml" that exists in
        # no workspace meant every launch was accepted, published one heartbeat
        # and then executed nothing -- a run that streams forever because there
        # is nothing on the other end producing events.
        manifest_path = self._resolve_manifest(payload)

        run_payload: dict[str, Any] = {
            "manifestPath": manifest_path,
            "repoPath": repo_path,
            "brief": brief,
        }
        # Carried through rather than dropped: the client sends the operator's
        # model and profile selection, and the worker thread is the consumer.
        for key in ("model", "episodeId", "actor"):
            value = payload.get(key)
            if value:
                run_payload[key] = str(value)

        # `_run_worker_thread` defaults this to "code-default", which is an
        # agent name and not a member of PRESETS, so every run died on
        # "unknown execution profile". `local` is the preset that runs on the
        # operator's own host, which is what a desktop session is.
        profile_id = str(payload.get("profileId") or "").strip()
        run_payload["profileId"] = profile_id if profile_id in _EXECUTION_PROFILES else "local"

        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "StartRun",
                "commandId": str(payload.get("commandId") or uuidv7()),
                "idempotencyKey": str(payload.get("idempotencyKey") or uuidv7()),
                "runId": run_id,
                "payload": run_payload,
            },
        }
        res = self.server.service.execute_command(cmd_frame)
        self._send_json_response(res)

    def _resolve_manifest(self, payload: Mapping[str, Any]) -> str:
        """Resolve the harness manifest to a file that actually composes.

        Order: an explicit `manifestPath` (absolute, or relative to the
        workspace), then the agency manifest named by `agentId`, then
        `vg-code-default`.

        The agency manifests are the live composition surface. `packs/*.yaml`
        is a third dialect that no current ingress accepts -- `compose` routes
        `mhf.harness/1` to `canonical_from_legacy`, which reads
        `{harness, components, ...}`, while the packs carry
        `{id, plugins, system_prompt, ...}`. Pointing a run at one produced
        `manifest has unread fields` before any model was called.
        """
        root = self.server.workspace_root
        explicit = str(payload.get("manifestPath") or "").strip()
        candidates: list[Path] = []
        if explicit and explicit not in (".", "harness.yaml"):
            candidates.append(Path(explicit) if Path(explicit).is_absolute() else root / explicit)

        # `profileId` is the *execution* profile (local/sandboxed/hermetic), a
        # different axis from which agent runs. The agent comes from `agentId`.
        agent_id = str(payload.get("agentId") or "").strip()
        for name in (agent_id, f"vg-{agent_id}" if agent_id else "", "vg-code-default"):
            if not name:
                continue
            for base in (root, _REPO_ROOT):
                candidates.append(base / _AGENCY_MANIFESTS / name / "manifest.json")

        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
        # Nothing resolved. Returning the explicit value keeps the failure
        # attributable: `StartRun` reports the path that did not exist rather
        # than silently substituting one that does.
        return explicit or str(_REPO_ROOT / _AGENCY_MANIFESTS / "vg-code-default" / "manifest.json")

    def _handle_cancel(self, run_id: str, payload: Mapping[str, Any]) -> None:
        p_clean = {k: v for k, v in payload.items() if k in ("reason", "expectedSeq")}
        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "Cancel",
                "commandId": str(payload.get("commandId") or uuidv7()),
                "idempotencyKey": str(payload.get("idempotencyKey") or uuidv7()),
                "runId": run_id,
                "payload": p_clean,
            },
        }
        res = self.server.service.execute_command(cmd_frame)
        self._send_json_response(res)

    def _handle_checkpoint(self, run_id: str, payload: Mapping[str, Any]) -> None:
        p_clean = {k: v for k, v in payload.items() if k in ("reason", "expectedSeq")}
        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "Checkpoint",
                "commandId": str(payload.get("commandId") or uuidv7()),
                "idempotencyKey": str(payload.get("idempotencyKey") or uuidv7()),
                "runId": run_id,
                "payload": p_clean,
            },
        }
        res = self.server.service.execute_command(cmd_frame)
        self._send_json_response(res)

    def _handle_resume(self, run_id: str, payload: Mapping[str, Any]) -> None:
        p_clean = {k: v for k, v in payload.items() if k in ("checkpointId", "expectedSeq")}
        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "Resume",
                "commandId": str(payload.get("commandId") or uuidv7()),
                "idempotencyKey": str(payload.get("idempotencyKey") or uuidv7()),
                "runId": run_id,
                "payload": p_clean,
            },
        }
        res = self.server.service.execute_command(cmd_frame)
        self._send_json_response(res)

    def _handle_resolve_approval(self, payload: Mapping[str, Any], approval_id: str = "") -> None:
        """Forward a caller-supplied decision verbatim. The gateway signs nothing.

        Every field here was previously defaulted -- a request that omitted
        ``signature`` was given ``"dummy-sig-approved"`` and recorded as
        resolved. The gateway is a transport: it may fill in the approval ID
        already present in the route, and nothing else. Missing fields are the
        service's to reject.
        """
        run_id = str(payload.get("runId", ""))
        p = dict(payload)

        decision_raw = p.get("decision")
        if isinstance(decision_raw, Mapping):
            dec_dict = dict(decision_raw)
        else:
            # Accept the flat form for convenience, but carry only what was
            # actually sent. No synthesised digests, expiry, key, or signature.
            dec_dict = {
                key: p[key]
                for key in (
                    "approvalId", "resolution", "reviewer", "argsDigest",
                    "descriptorDigest", "expiresAt", "keyId", "signature",
                )
                if key in p
            }
        if approval_id and "approvalId" not in dec_dict:
            dec_dict["approvalId"] = approval_id

        p_clean = {"decision": dec_dict}
        if "expectedSeq" in p:
            p_clean["expectedSeq"] = p["expectedSeq"]

        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "ResolveApproval",
                "commandId": str(payload.get("commandId") or uuidv7()),
                "idempotencyKey": str(payload.get("idempotencyKey") or uuidv7()),
                "runId": run_id,
                "payload": p_clean,
            },
        }
        res = self.server.service.execute_command(cmd_frame)
        self._send_json_response(res)

    def _handle_explain_artifact(self, artifact_id: str, query: Mapping[str, list[str]]) -> None:
        run_id = query.get("runId", query.get("run_id", [""]))[0]
        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "ExplainArtifact",
                "commandId": uuidv7(),
                "idempotencyKey": uuidv7(),
                "runId": run_id,
                "payload": {"artifactId": artifact_id},
            },
        }
        res = self.server.service.execute_command(cmd_frame)
        self._send_json_response(res)

    def _handle_explain_artifact_post(self, payload: Mapping[str, Any]) -> None:
        run_id = str(payload.get("runId", ""))
        artifact_id = str(payload.get("artifactId", ""))
        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "ExplainArtifact",
                "commandId": str(payload.get("commandId") or uuidv7()),
                "idempotencyKey": str(payload.get("idempotencyKey") or uuidv7()),
                "runId": run_id,
                "payload": {"artifactId": artifact_id},
            },
        }
        res = self.server.service.execute_command(cmd_frame)
        self._send_json_response(res)

    def _handle_record_correction(self, run_id: str, payload: Mapping[str, Any]) -> None:
        r_id = run_id or str(payload.get("runId", ""))
        correction = payload.get("correction") if "correction" in payload else payload
        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "RecordCorrection",
                "commandId": str(payload.get("commandId") or uuidv7()),
                "idempotencyKey": str(payload.get("idempotencyKey") or uuidv7()),
                "runId": r_id,
                "payload": {"correction": dict(correction)},
            },
        }
        res = self.server.service.execute_command(cmd_frame)
        self._send_json_response(res)

    def _handle_workspace_file(self, query: Mapping[str, list[str]]) -> None:
        file_param = query.get("path", [""])[0]
        if not file_param:
            self.send_response(HTTPStatus.BAD_REQUEST)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Missing 'path' query parameter"}).encode("utf-8"))
            return

        workspace_root = self.server.workspace_root.resolve()
        target_path = (workspace_root / file_param).resolve()

        # Containment first: a path outside the workspace is indistinguishable
        # from one that does not exist, so it must not be answerable.
        if not target_path.is_relative_to(workspace_root) or not target_path.exists() or not target_path.is_file():
            self.send_response(HTTPStatus.NOT_FOUND)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"File not found or outside workspace: {file_param}"}).encode("utf-8"))
            return

        # Selector mediation. Containment alone still exposes every secret the
        # workspace happens to contain, so reads are restricted to an allowlist
        # of readable kinds, outside dot-directories, minus credential names.
        relative = target_path.relative_to(workspace_root)
        if (
            target_path.name in WORKSPACE_READ_DENYLIST
            or target_path.suffix.lower() not in WORKSPACE_READ_SUFFIXES
            or any(part.startswith(".") for part in relative.parts[:-1])
        ):
            self._send_error_code(
                "permission_denied",
                f"path {file_param!r} is not within the readable workspace selector",
            )
            return

        try:
            content = target_path.read_text(encoding="utf-8")
        except Exception as exc:
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))
            return

        self.send_response(HTTPStatus.OK)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"path": file_param, "content": content}).encode("utf-8"))

    def _handle_events_stream(self, run_id: str, query: Mapping[str, list[str]]) -> None:
        # Determine starting sequence from query or Last-Event-ID header
        after_seq = 0
        after_seq_param = query.get("afterSeq", query.get("after_seq", [""]))[0]
        last_event_id = self.headers.get("Last-Event-ID", "")
        if after_seq_param:
            try:
                after_seq = int(after_seq_param)
            except ValueError:
                after_seq = 0
        elif last_event_id:
            try:
                after_seq = int(last_event_id)
            except ValueError:
                after_seq = 0

        self.send_response(HTTPStatus.OK)
        self._set_cors_headers()
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        try:
            for frame in self.server.service.stream_events(run_id, after_seq=after_seq):
                if not self.server.is_running:
                    break
                evt = frame.get("event", {})
                seq = str(evt.get("seq", "0"))
                data = json.dumps(frame)
                msg = f"id: {seq}\nevent: vg.4\ndata: {data}\n\n"
                self.wfile.write(msg.encode("utf-8"))
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    def _send_json_response(self, data: Mapping[str, Any]) -> None:
        status = HTTPStatus.OK
        if data.get("frameType") == "error":
            code = str(data.get("error", {}).get("code", "internal"))
            status = _http_status_for_code(code)
        elif data.get("frameType") == "receipt":
            receipt = data.get("receipt", {})
            if receipt.get("status") == "error":
                err = receipt.get("error", {})
                code = str(
                    err.get("code")
                    or (
                        "not_found"
                        if "not found" in str(receipt.get("detail", "")).lower()
                        else "invalid_request"
                    )
                )
                status = _http_status_for_code(code)

        self.send_response(status)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))


class StudioGatewayServer(ThreadingHTTPServer):
    """Threading HTTP Server hosting the Studio Gateway."""

    allow_reuse_address = True

    def __init__(
        self,
        server_address: tuple[str, int],
        service: RuntimeService,
        workspace_root: Path,
        *,
        auth_tokens: frozenset[str] = frozenset(),
        allowed_origins: tuple[str, ...] = (),
    ) -> None:
        super().__init__(server_address, StudioGatewayHandler)
        self.service = service
        self.workspace_root = workspace_root
        #: Bearer tokens accepted for command routes. Empty means loopback-only
        #: development; `create_gateway` refuses a non-loopback bind in that case.
        self.auth_tokens = auth_tokens
        #: Exact origins echoed back on CORS responses. Never a wildcard: a
        #: wildcard on a surface that resolves approvals lets any page a
        #: developer visits drive their runtime.
        self.allowed_origins = tuple(allowed_origins)
        self.is_running = True

    def is_loopback(self) -> bool:
        host = self.server_address[0]
        return host in ("127.0.0.1", "::1", "localhost")


def create_gateway(
    host: str = "127.0.0.1",
    port: int = 8000,
    workspace_root: Path | None = None,
    service: RuntimeService | None = None,
    db_path: Path | str | None = None,
    auth_tokens: Sequence[str] = (),
    allowed_origins: Sequence[str] = (),
) -> StudioGatewayServer:
    from ...adapters.stores.event_store import SqliteEventStore
    from .inbox import ServiceInboxStore

    root = (workspace_root or Path.cwd()).resolve()

    tokens = frozenset(t for t in auth_tokens if t)
    if not tokens:
        env_tokens = os.environ.get("VANGUARD_GATEWAY_TOKENS", "")
        tokens = frozenset(t.strip() for t in env_tokens.split(",") if t.strip())
    if not allowed_origins:
        env_origins = os.environ.get("VANGUARD_GATEWAY_ORIGINS", "")
        allowed_origins = tuple(o.strip() for o in env_origins.split(",") if o.strip())

    if host not in ("127.0.0.1", "::1", "localhost") and not tokens:
        # An unauthenticated gateway reachable off-host is a remote command
        # execution surface. Refuse to start rather than serve it.
        raise ValueError(
            f"refusing to bind {host}: a non-loopback gateway requires bearer tokens "
            "(pass auth_tokens= or set VANGUARD_GATEWAY_TOKENS)"
        )

    if service is None:
        from ..state_contract import ensure_state_directory

        if db_path is None:
            db_path = root / ".vanguard" / "runtime.db"
        else:
            db_path = Path(db_path)
        # EVO-01: same fail-closed writability/durability contract every
        # other transport goes through (`RuntimeBootstrap`, the CLI) --
        # not a bare `mkdir` that silently succeeds even when the target
        # isn't genuinely writable.
        ensure_state_directory(db_path.parent, durability_mode="sqlite-wal")
        inbox = ServiceInboxStore(db_path)
        event_store = SqliteEventStore(db_path)
        service = RuntimeService(inbox_store=inbox, event_store=event_store)
    return StudioGatewayServer(
        (host, port), service, root,
        auth_tokens=tokens, allowed_origins=tuple(allowed_origins),
    )


def run_gateway(
    host: str = "127.0.0.1",
    port: int = 8000,
    workspace: str = ".",
    db_path: str | None = None,
    auth_tokens: Sequence[str] = (),
    allowed_origins: Sequence[str] = (),
) -> None:
    root = Path(workspace).resolve()
    print(f"[*] Starting AETHER Studio Gateway on http://{host}:{port}")
    print(f"[*] Serving workspace at {root}")
    server = create_gateway(
        host=host, port=port, workspace_root=root, db_path=db_path,
        auth_tokens=auth_tokens, allowed_origins=allowed_origins,
    )
    if not server.auth_tokens:
        print("[!] No bearer tokens configured: loopback-only development mode.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down Studio Gateway...")
        server.is_running = False
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="AETHER Studio Gateway")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument("--workspace", default=".", help="Workspace root directory")
    parser.add_argument("--db", default=None, help="Database path for persistent SQLite WAL store")
    args = parser.parse_args()
    run_gateway(host=args.host, port=args.port, workspace=args.workspace, db_path=args.db)


if __name__ == "__main__":
    main()

