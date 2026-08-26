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
        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "ListRuns",
                "commandId": uuidv7(),
                "payload": {},
            },
        }
        result = self.server.service.execute_command(cmd_frame)
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
        target_file = str(payload.get("targetFile") or "vanguard/packages/kernel/dispatch.py")
        run_id = f"run-studio-{uuidv7()[:8]}"

        # Start run via RuntimeService
        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "StartRun",
                "commandId": uuidv7(),
                "runId": run_id,
                "payload": {
                    "manifestPath": "harness.yaml",
                    "repoPath": str(self.server.workspace_root),
                    "brief": brief,
                },
            },
        }
        res = self.server.service.execute_command(cmd_frame)

        # Launch automated pilot thread to emit simulated turn progression
        threading.Thread(target=self._pilot_run_simulation, args=(run_id, brief, target_file), daemon=True).start()

        self.send_response(HTTPStatus.OK)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"runId": run_id, "status": "started", "result": res}).encode("utf-8"))

    def _pilot_run_simulation(self, run_id: str, brief: str, target_file: str) -> None:
        """Simulates turn-by-turn agent progression, emitting real causal events over the live stream."""
        time.sleep(0.5)
        self.server.broadcast_event(run_id, {
            "kind": "GoalDeclared",
            "goal": brief,
            "goalDigest": "sha256:pilot_goal_01a",
        })
        time.sleep(1.0)
        self.server.broadcast_event(run_id, {
            "kind": "ContextCompiled",
            "brief": brief,
            "layers": ["L1", "L2", "L3", "L4", "L5"],
            "tokens": 2140,
            "promptDigest": "sha256:pilot_prompt_99b",
        })
        time.sleep(1.2)
        self.server.broadcast_event(run_id, {
            "kind": "ProposalProduced",
            "kind_type": "effect",
            "action": "fs.read",
            "args": {"path": target_file},
            "descriptor": f"sha256:desc_read_{target_file}",
        })
        time.sleep(0.8)
        self.server.broadcast_event(run_id, {
            "kind": "EffectStarted",
            "action": "fs.read",
            "descriptor": f"sha256:desc_read_{target_file}",
            "durationMs": 32,
        })
        time.sleep(0.6)
        self.server.broadcast_event(run_id, {
            "kind": "EffectCompleted",
            "action": "fs.read",
            "descriptor": f"sha256:desc_read_{target_file}",
            "outcome": "satisfied",
            "durationMs": 18,
        })
        time.sleep(1.0)
        self.server.broadcast_event(run_id, {
            "kind": "BudgetCommitted",
            "tokens": 1280,
            "costMicros": "256000",
        })
        time.sleep(1.2)
        # Approval trigger
        self.server.broadcast_event(run_id, {
            "kind": "ApprovalRequested",
            "approvalId": f"approval-{run_id[-6:]}",
            "action": "fs.patch",
            "normalizedDiff": f"--- a/{target_file}\n+++ b/{target_file}\n@@ -315,5 +315,6 @@\n+    finally:\n+        # K-06: guaranteed lease release\n+        self._governor.release(lease)",
            "argsDigest": "sha256:args_pilot_patch",
            "descriptorDigest": f"sha256:desc_patch_{target_file}",
            "expiresAt": _utc_now(),
        })

    def _handle_resolve_approval(self, payload: Mapping[str, Any]) -> None:
        approval_id = str(payload.get("approvalId") or "")
        decision = str(payload.get("decision") or "approve")

        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "ResolveApproval",
                "commandId": uuidv7(),
                "payload": {
                    "approvalId": approval_id,
                    "decision": decision,
                },
            },
        }
        res = self.server.service.execute_command(cmd_frame)

        # Broadcast resolved event and completion
        self.server.broadcast_event("live-run", {
            "kind": "ApprovalResolved",
            "approvalId": approval_id,
            "decision": decision,
            "reviewer": "operator-live",
        })
        time.sleep(0.5)
        self.server.broadcast_event("live-run", {
            "kind": "EffectCompleted",
            "action": "fs.patch",
            "outcome": "satisfied",
            "durationMs": 24,
        })
        time.sleep(0.8)
        self.server.broadcast_event("live-run", {
            "kind": "EpisodeCompleted",
            "outcome": "satisfied",
            "verdict": "1",
            "terminalSignal": "all_tests_passed",
        })

        self.send_response(HTTPStatus.OK)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"approvalId": approval_id, "status": "resolved", "result": res}).encode("utf-8"))

    def _handle_events_stream(self, query: Mapping[str, list[str]]) -> None:
        self.send_response(HTTPStatus.OK)
        self._set_cors_headers()
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        # Initial connection frame
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

        q: queue.Queue[dict[str, Any] | None] = queue.Queue()
        self.server.register_global_subscriber(q)

        try:
            while self.server.is_running:
                try:
                    frame = q.get(timeout=1.0)
                    if frame is None:
                        break
                    self.wfile.write(f"data: {json.dumps(frame)}\n\n".encode("utf-8"))
                    self.wfile.flush()
                except queue.Empty:
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            self.server.unregister_global_subscriber(q)


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
        self._global_subscribers: list[queue.Queue[dict[str, Any] | None]] = []
        self._seq_counter = 2
        self._lock = threading.Lock()

    def register_global_subscriber(self, q: queue.Queue[dict[str, Any] | None]) -> None:
        with self._lock:
            self._global_subscribers.append(q)

    def unregister_global_subscriber(self, q: queue.Queue[dict[str, Any] | None]) -> None:
        with self._lock:
            if q in self._global_subscribers:
                self._global_subscribers.remove(q)

    def broadcast_event(self, run_id: str, payload: Mapping[str, Any]) -> None:
        with self._lock:
            seq = str(self._seq_counter)
            self._seq_counter += 1
            frame = {
                "schemaVersion": "vg.4",
                "eventId": f"evt-{uuidv7()}",
                "seq": seq,
                "runId": run_id,
                "occurredAt": _utc_now(),
                "principal": "pilot-orchestrator",
                "payload": dict(payload),
            }
            for sub in list(self._global_subscribers):
                try:
                    sub.put_nowait(frame)
                except Exception:
                    pass


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
