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
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import parse_qs, urlparse

from ...domain.primitives.primitives import uuidv7
from ..governance.approvals import OperatorSigner
from .service import RuntimeService, _utc_now


class StudioGatewayHandler(BaseHTTPRequestHandler):
    """HTTP and SSE request handler for the Studio Frontend."""

    server: StudioGatewayServer

    def _set_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/api/health":
            self._handle_health()
        elif path == "/api/events/stream":
            self._handle_events_stream(query)
        elif path == "/api/runs":
            self._handle_list_runs()
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

        if path == "/api/runs/launch":
            self._handle_launch_run(payload)
        elif path == "/api/approvals/resolve":
            self._handle_resolve_approval(payload)
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
            "version": "0.7.0",
            "activeRuns": len(self.server.service._active_runs),
            "timestamp": _utc_now(),
        }
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def _handle_list_runs(self) -> None:
        result = self.server.service.execute_command({"command": "runs.list"})
        self.send_response(HTTPStatus.OK)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode("utf-8"))

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

        if not str(target_path).startswith(str(workspace_root)) or not target_path.exists() or not target_path.is_file():
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

    def _handle_launch_run(self, payload: Mapping[str, Any]) -> None:
        brief = str(payload.get("brief") or "Interactive Studio Task")
        target_file = str(payload.get("targetFile") or "")
        run_id = f"run-studio-{uuidv7()[:8]}"

        # Start simulated/live run via RuntimeService
        cmd = {
            "command": "run.start",
            "runId": run_id,
            "manifestPath": "harness.yaml",
            "repoPath": str(self.server.workspace_root),
            "brief": f"{brief} (target: {target_file})" if target_file else brief,
        }
        res = self.server.service.execute_command(cmd)

        self.send_response(HTTPStatus.OK)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"runId": run_id, "result": res}).encode("utf-8"))

    def _handle_resolve_approval(self, payload: Mapping[str, Any]) -> None:
        approval_id = str(payload.get("approvalId") or "")
        decision = str(payload.get("decision") or "reject")

        cmd = {
            "command": "approval.resolve",
            "approvalId": approval_id,
            "decision": decision,
        }
        res = self.server.service.execute_command(cmd)

        self.send_response(HTTPStatus.OK)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(res).encode("utf-8"))

    def _handle_events_stream(self, query: Mapping[str, list[str]]) -> None:
        run_id_param = query.get("runId", [""])[0]

        self.send_response(HTTPStatus.OK)
        self._set_cors_headers()
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        # Send initial connection notice
        init_frame = {
            "schemaVersion": "vg.4",
            "eventId": f"evt-{uuidv7()}",
            "seq": "1",
            "occurredAt": _utc_now(),
            "principal": "studio-gateway",
            "payload": {
                "kind": "StudioBridgeConnected",
                "status": "connected",
                "time": _utc_now(),
            },
        }
        self.wfile.write(f"data: {json.dumps(init_frame)}\n\n".encode("utf-8"))
        self.wfile.flush()

        # Subscribe to RuntimeService events
        q: queue.Queue[dict[str, Any] | None] = queue.Queue()
        with self.server.service._lock:
            # Register subscriber to all active runs
            for active in self.server.service._active_runs.values():
                if not run_id_param or active.run_id == run_id_param:
                    active.event_subscribers.append(q)

        seq_counter = 2
        try:
            while self.server.is_running:
                try:
                    event = q.get(timeout=1.0)
                    if event is None:
                        break
                    frame = {
                        "schemaVersion": "vg.4",
                        "eventId": f"evt-{uuidv7()}",
                        "seq": str(seq_counter),
                        "occurredAt": _utc_now(),
                        "principal": "runtime-service",
                        "payload": event,
                    }
                    seq_counter += 1
                    self.wfile.write(f"data: {json.dumps(frame)}\n\n".encode("utf-8"))
                    self.wfile.flush()
                except queue.Empty:
                    # Send periodic keepalive comment to keep connection open
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass


class StudioGatewayServer(ThreadingHTTPServer):
    """Threading HTTP Server hosting the Studio Gateway."""

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
