"""F1: one causal event ledger, reachable identically over HTTP/SSE and UDS.

`RuntimeService` self-derives its `event_store` from the inbox's `db_path` when
none is passed explicitly (`service.py`'s `__init__`), and both the UDS daemon
(`server.py`'s `StreamEvents` branch) and the HTTP gateway (`studio_gateway.py`'s
`_handle_events_stream`) read events exclusively through the same
`RuntimeService.stream_events(run_id, after_seq=...)` method. This test proves
that structural guarantee empirically: the same run's event sequence, as seen by
each transport, must be byte-for-byte identical -- no synthetic or transport-local
event history is possible.
"""

from __future__ import annotations

import json
import socket
import tempfile
import threading
import time
import unittest
import urllib.request
from pathlib import Path

from vanguard.packages.domain.primitives.primitives import uuidv7
from vanguard.packages.runtime.governance.approvals import ApprovalAuthority, OperatorSigner
from vanguard.packages.runtime.service import RuntimeServer, RuntimeService, ServiceInboxStore
from vanguard.packages.runtime.service.studio_gateway import create_gateway


class TestTransportParity(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        temp_path = Path(self._tempdir.name)
        self.db_path = temp_path / "service.db"
        self.sock_path = temp_path / "runtime.sock"
        workspace = temp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)

        signer = OperatorSigner(key_id="op-test")
        authority = ApprovalAuthority({"op-test": signer.public_bytes})
        # One inbox, one db_path -> one self-derived SqliteEventStore, shared by
        # both transports below. This is the invariant under test.
        self.inbox = ServiceInboxStore(self.db_path)
        self.service = RuntimeService(self.inbox, authority=authority)

        self.uds_server = RuntimeServer(self.service, self.sock_path)
        self.uds_server.start()

        self.http_server = create_gateway(
            host="127.0.0.1", port=0, workspace_root=workspace, service=self.service,
        )
        self.http_port = self.http_server.server_port
        self.http_thread = threading.Thread(target=self.http_server.serve_forever, daemon=True)
        self.http_thread.start()
        time.sleep(0.05)

    def tearDown(self) -> None:
        self.uds_server.stop()
        self.http_server.is_running = False
        self.http_server.shutdown()
        self.http_server.server_close()
        self.inbox.close()
        self._tempdir.cleanup()

    def _uds_send(self, frame: dict) -> dict:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(str(self.sock_path))
        with client:
            client.sendall(json.dumps(frame).encode("utf-8") + b"\n")
            data = b""
            while b"\n" not in data:
                chunk = client.recv(4096)
                if not chunk:
                    break
                data += chunk
            return json.loads(data.split(b"\n")[0].decode("utf-8"))

    def _uds_stream_events(self, run_id: str) -> list[dict]:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(str(self.sock_path))
        frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "StreamEvents",
                "commandId": "cmd-stream",
                "idempotencyKey": "idem-stream",
                "runId": run_id,
                "actor": "operator",
                "payload": {},
            },
        }
        events: list[dict] = []
        with client:
            client.sendall(json.dumps(frame).encode("utf-8") + b"\n")
            client.settimeout(2.0)
            buf = b""
            try:
                while True:
                    chunk = client.recv(65536)
                    if not chunk:
                        break
                    buf += chunk
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        if line:
                            events.append(json.loads(line))
            except socket.timeout:
                pass
        return events

    def _http_stream_events(self, run_id: str) -> list[dict]:
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.http_port}/api/v1/runs/{run_id}/events:stream"
        )
        events: list[dict] = []
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            buf = ""
            try:
                while True:
                    # read1(), not read(): a keep-alive SSE stream without
                    # Content-Length never signals EOF, so read() blocks trying
                    # to fill the buffer. read1() returns after one recv().
                    chunk = resp.read1(65536)
                    if not chunk:
                        break
                    buf += chunk.decode("utf-8")
                    while "\n\n" in buf:
                        raw_event, buf = buf.split("\n\n", 1)
                        for line in raw_event.splitlines():
                            if line.startswith("data: "):
                                events.append(json.loads(line[len("data: "):]))
            except (TimeoutError, OSError):
                pass
        return events

    def test_uds_and_http_see_identical_event_sequence_for_the_same_run(self) -> None:
        run_id = f"run-parity-{uuidv7()[:8]}"
        start = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "StartRun",
                "commandId": "cmd-start",
                "idempotencyKey": "idem-start",
                "runId": run_id,
                "actor": "operator",
                "payload": {"manifestPath": "harness.yaml", "repoPath": ".", "brief": "parity test"},
            },
        }
        started = self._uds_send(start)
        self.assertEqual(started.get("receipt", {}).get("status"), "completed")

        cancel = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "Cancel",
                "commandId": "cmd-cancel",
                "idempotencyKey": "idem-cancel",
                "runId": run_id,
                "actor": "operator",
                "payload": {},
            },
        }
        cancelled = self._uds_send(cancel)
        self.assertEqual(cancelled.get("receipt", {}).get("result", {}).get("status"), "cancelled")

        # Run is now inactive: stream_events() replays purely historical events
        # on both transports and returns without blocking on a live queue.
        uds_events = self._uds_stream_events(run_id)
        http_events = self._http_stream_events(run_id)

        self.assertTrue(uds_events, "UDS transport returned no events")
        self.assertTrue(http_events, "HTTP transport returned no events")

        uds_seqs = [e["event"]["seq"] for e in uds_events]
        http_seqs = [e["event"]["seq"] for e in http_events]
        self.assertEqual(uds_seqs, http_seqs, "UDS and HTTP disagree on event sequence order")

        uds_digests = [e["event"].get("digest") for e in uds_events]
        http_digests = [e["event"].get("digest") for e in http_events]
        self.assertEqual(
            uds_digests, http_digests,
            "UDS and HTTP disagree on event hash chain -- two event histories detected",
        )


if __name__ == "__main__":
    unittest.main()
