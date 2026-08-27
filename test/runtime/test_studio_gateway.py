"""Unit and integration tests for StudioGateway HTTP and SSE endpoints."""

from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
import urllib.request
from http import HTTPStatus
from pathlib import Path

from vanguard.packages.domain.primitives.primitives import uuidv7
from vanguard.packages.runtime.governance.approvals import ApprovalAuthority, OperatorSigner
from vanguard.packages.runtime.service.inbox import ServiceInboxStore
from vanguard.packages.runtime.service.service import RuntimeService
from vanguard.packages.runtime.service.studio_gateway import create_gateway


class TestStudioGateway(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self._tempdir.name)
        self.workspace = self.temp_path / "workspace"
        self.workspace.mkdir(parents=True, exist_ok=True)
        (self.workspace / "sample.txt").write_text("hello world", encoding="utf-8")

        self.db_path = self.temp_path / "service.db"
        self.inbox = ServiceInboxStore(self.db_path)
        self.signer = OperatorSigner(key_id="op-test")
        self.authority = ApprovalAuthority({"op-test": self.signer.public_bytes})
        self.service = RuntimeService(self.inbox, authority=self.authority)

        # Bind to ephemeral port on 127.0.0.1
        self.server = create_gateway(
            host="127.0.0.1",
            port=0,
            workspace_root=self.workspace,
            service=self.service,
        )
        self.port = self.server.server_port
        self.base_url = f"http://127.0.0.1:{self.port}"

        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        time.sleep(0.05)

    def tearDown(self) -> None:
        self.server.is_running = False
        self.server.shutdown()
        self.server.server_close()
        self.inbox.close()
        self._tempdir.cleanup()

    def _get(self, path: str, headers: dict[str, str] | None = None) -> tuple[int, dict]:
        req = urllib.request.Request(f"{self.base_url}{path}", headers=headers or {})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return resp.status, data

    def _post(self, path: str, body: dict) -> tuple[int, dict]:
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return resp.status, data

    def test_health_endpoint(self) -> None:
        status, data = self._get("/api/health")
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("service"), "vanguard-studio-gateway")

        status_v1, data_v1 = self._get("/api/v1/health")
        self.assertEqual(status_v1, HTTPStatus.OK)
        self.assertEqual(data_v1.get("status"), "ok")

    def test_capabilities_endpoint(self) -> None:
        status, data = self._get("/api/capabilities")
        self.assertEqual(status, HTTPStatus.OK)
        caps = data.get("receipt", {}).get("result", {}).get("capabilities", {})
        self.assertEqual(caps.get("run.start", {}).get("implementation"), "available")
        self.assertEqual(caps.get("topology.execute", {}).get("authorization"), "disabled")

    def test_workspace_file_access_and_security(self) -> None:
        # Valid file
        status, data = self._get("/api/workspace/file?path=sample.txt")
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(data.get("content"), "hello world")

        # Missing path
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._get("/api/workspace/file?path=")
        self.assertEqual(ctx.exception.code, HTTPStatus.BAD_REQUEST)

        # Path traversal rejection
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._get("/api/workspace/file?path=../../etc/passwd")
        self.assertEqual(ctx.exception.code, HTTPStatus.NOT_FOUND)

    def test_run_lifecycle_and_streaming(self) -> None:
        # Launch run
        run_id = f"run-gw-{uuidv7()[:8]}"
        status, data = self._post(
            "/api/runs/launch",
            {
                "runId": run_id,
                "brief": "Studio Gateway Integration Test",
                "manifestPath": "harness.yaml",
            },
        )
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(data.get("receipt", {}).get("result", {}).get("status"), "started")

        # Get run
        status, get_data = self._get(f"/api/runs/{run_id}")
        self.assertEqual(status, HTTPStatus.OK)
        snap = get_data.get("receipt", {}).get("result", {})
        self.assertEqual(snap.get("runId"), run_id)
        self.assertEqual(snap.get("status"), "running")

        # List runs
        status, list_data = self._get("/api/runs")
        self.assertEqual(status, HTTPStatus.OK)
        runs = list_data.get("receipt", {}).get("result", {}).get("runs", [])
        self.assertTrue(any(r.get("run_id") == run_id for r in runs))

        # Resolve approval
        status, app_data = self._post(
            "/api/approvals/resolve",
            {
                "runId": run_id,
                "approvalId": "app-001",
                "decision": "approved",
            },
        )
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(app_data.get("receipt", {}).get("result", {}).get("status"), "resolved")

        # Cancel run
        status, cancel_data = self._post(f"/api/runs/{run_id}:cancel", {})
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(cancel_data.get("receipt", {}).get("result", {}).get("status"), "cancelled")

    def test_sse_events_stream_and_resume_cursor(self) -> None:
        run_id = f"run-sse-{uuidv7()[:8]}"
        self._post("/api/runs/launch", {"runId": run_id, "brief": "SSE test"})

        # Connect to stream
        req = urllib.request.Request(f"{self.base_url}/api/v1/runs/{run_id}/events:stream")
        with urllib.request.urlopen(req) as resp:
            # Read first line chunk
            chunk = resp.readline().decode("utf-8")
            self.assertTrue(chunk.startswith("id:") or chunk.startswith(":"))


if __name__ == "__main__":
    unittest.main()
