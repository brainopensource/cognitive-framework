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
from typing import Any, Mapping
from urllib.parse import parse_qs, urlparse

from ...domain.primitives.primitives import uuidv7
from ..governance.approvals import OperatorSigner
from .service import RuntimeService, _utc_now


def _package_version() -> str:
    """Read the installed version whose source is ``pyproject.toml``."""
    try:
        return distribution_version("vanguard-runtime")
    except PackageNotFoundError:
        return "unknown"


class StudioGatewayHandler(BaseHTTPRequestHandler):
    """HTTP and SSE request handler for the Studio Frontend."""

    server: StudioGatewayServer

    def _set_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, Last-Event-ID")

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        query = parse_qs(parsed.query)

        if path in ("/api/health", "/api/v1/health"):
            self._handle_health()
        elif path in ("/api/capabilities", "/api/v1/capabilities"):
            self._handle_capabilities()
        elif path in ("/api/runs", "/api/v1/runs"):
            self._handle_list_runs(query)
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

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except json.JSONDecodeError:
            self.send_response(HTTPStatus.BAD_REQUEST)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON body"}).encode("utf-8"))
            return

        if path in ("/api/runs", "/api/v1/runs", "/api/runs/launch"):
            self._handle_launch_run(payload)
        elif path in ("/api/approvals/resolve", "/api/v1/approvals/resolve") or (
            path.startswith("/api/v1/approvals/") and path.endswith(":resolve")
        ):
            approval_id = ""
            if path.startswith("/api/v1/approvals/") and path.endswith(":resolve"):
                approval_id = path[len("/api/v1/approvals/") : -len(":resolve")]
            self._handle_resolve_approval(payload, approval_id=approval_id)
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

    def _handle_capabilities(self) -> None:
        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "GetCapabilities",
                "commandId": uuidv7(),
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
                "runId": run_id,
                "payload": {},
            },
        }
        res = self.server.service.execute_command(cmd_frame)
        self._send_json_response(res)

    def _handle_launch_run(self, payload: Mapping[str, Any]) -> None:
        brief = str(payload.get("brief") or "Interactive Studio Task")
        manifest_path = str(payload.get("manifestPath") or "harness.yaml")
        repo_path = str(payload.get("repoPath") or str(self.server.workspace_root))
        run_id = str(payload.get("runId") or f"run-studio-{uuidv7()[:8]}")

        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "StartRun",
                "commandId": uuidv7(),
                "runId": run_id,
                "payload": {
                    "manifestPath": manifest_path,
                    "repoPath": repo_path,
                    "brief": brief,
                },
            },
        }
        res = self.server.service.execute_command(cmd_frame)
        self._send_json_response(res)

    def _handle_cancel(self, run_id: str, payload: Mapping[str, Any]) -> None:
        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "Cancel",
                "commandId": uuidv7(),
                "runId": run_id,
                "payload": dict(payload),
            },
        }
        res = self.server.service.execute_command(cmd_frame)
        self._send_json_response(res)

    def _handle_checkpoint(self, run_id: str, payload: Mapping[str, Any]) -> None:
        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "Checkpoint",
                "commandId": uuidv7(),
                "runId": run_id,
                "payload": dict(payload),
            },
        }
        res = self.server.service.execute_command(cmd_frame)
        self._send_json_response(res)

    def _handle_resume(self, run_id: str, payload: Mapping[str, Any]) -> None:
        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "Resume",
                "commandId": uuidv7(),
                "runId": run_id,
                "payload": dict(payload),
            },
        }
        res = self.server.service.execute_command(cmd_frame)
        self._send_json_response(res)

    def _handle_resolve_approval(self, payload: Mapping[str, Any], approval_id: str = "") -> None:
        run_id = str(payload.get("runId", ""))
        p = dict(payload)
        if approval_id and "approvalId" not in p:
            p["approvalId"] = approval_id

        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "ResolveApproval",
                "commandId": uuidv7(),
                "runId": run_id,
                "payload": p,
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

        if not target_path.is_relative_to(workspace_root) or not target_path.exists() or not target_path.is_file():
            self.send_response(HTTPStatus.NOT_FOUND)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"File not found or outside workspace: {file_param}"}).encode("utf-8"))
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
        self.send_response(HTTPStatus.OK)
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
    ) -> None:
        super().__init__(server_address, StudioGatewayHandler)
        self.service = service
        self.workspace_root = workspace_root
        self.is_running = True


def create_gateway(
    host: str = "127.0.0.1",
    port: int = 8000,
    workspace_root: Path | None = None,
    service: RuntimeService | None = None,
) -> StudioGatewayServer:
    root = (workspace_root or Path.cwd()).resolve()
    srv = service or RuntimeService()
    return StudioGatewayServer((host, port), srv, root)


def run_gateway(host: str = "127.0.0.1", port: int = 8000, workspace: str = ".") -> None:
    root = Path(workspace).resolve()
    print(f"[*] Starting AETHER Studio Gateway on http://{host}:{port}")
    print(f"[*] Serving workspace at {root}")
    server = create_gateway(host=host, port=port, workspace_root=root)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down Studio Gateway...")
        server.is_running = False
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AETHER Studio Gateway")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument("--workspace", default=".", help="Workspace root directory")
    args = parser.parse_args()
    run_gateway(host=args.host, port=args.port, workspace=args.workspace)

