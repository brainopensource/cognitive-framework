"""Unit and integration tests for RuntimeService and RuntimeServer."""

from __future__ import annotations

import json
import socket
import tempfile
import time
import unittest
from pathlib import Path

from vanguard.packages.domain.primitives.primitives import uuidv7
from vanguard.packages.runtime.governance.approvals import ApprovalAuthority, OperatorSigner
from vanguard.packages.runtime.service import (
    ActiveRunContext,
    RuntimeServer,
    RuntimeService,
    ServiceInboxStore,
)


class TestRuntimeService(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self._tempdir.name)
        self.db_path = self.temp_path / "service.db"
        self.sock_path = self.temp_path / "runtime.sock"

        self.signer = OperatorSigner(key_id="op-test")
        self.authority = ApprovalAuthority({"op-test": self.signer.public_bytes})
        self.inbox = ServiceInboxStore(self.db_path)
        self.service = RuntimeService(self.inbox, authority=self.authority)
        self.server = RuntimeServer(self.service, self.sock_path)
        self.server.start()
        time.sleep(0.05)

    def tearDown(self) -> None:
        self.server.stop()
        self.inbox.close()
        self._tempdir.cleanup()

    def _client_send(self, frame: dict) -> dict:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(str(self.sock_path))
        with client:
            line = json.dumps(frame).encode("utf-8") + b"\n"
            client.sendall(line)
            data = b""
            while b"\n" not in data:
                chunk = client.recv(4096)
                if not chunk:
                    break
                data += chunk
            return json.loads(data.split(b"\n")[0].decode("utf-8"))

    def test_socket_permissions_mode_0600(self) -> None:
        mode = self.sock_path.stat().st_mode & 0o777
        self.assertEqual(mode, 0o600)

    def test_start_run_and_idempotency(self) -> None:
        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "StartRun",
                "commandId": "cmd-1",
                "idempotencyKey": "idem-1",
                "runId": "run-100",
                "actor": "operator",
                "payload": {
                    "manifestPath": "manifest.json",
                    "repoPath": ".",
                    "brief": "test run",
                },
            },
        }
        res1 = self._client_send(cmd_frame)
        self.assertEqual(res1.get("frameType"), "receipt")
        receipt1 = res1.get("receipt", {})
        self.assertEqual(receipt1.get("status"), "completed")
        self.assertEqual(receipt1.get("result", {}).get("status"), "started")

        # Duplicate command with same idempotency key
        res2 = self._client_send(cmd_frame)
        self.assertEqual(res2.get("frameType"), "receipt")
        receipt2 = res2.get("receipt", {})
        self.assertEqual(receipt2.get("commandId"), "cmd-1")
        self.assertEqual(receipt2.get("status"), "completed")

    def test_record_correction_appends_event(self) -> None:
        cmd_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "RecordCorrection",
                "commandId": "cmd-corr-1",
                "idempotencyKey": "idem-corr-1",
                "runId": "run-200",
                "actor": "operator",
                # `S8-A-04`: a CorrectionRecord, not a free-form note. The
                # old payload here was never a valid record -- it passed only
                # because nothing parsed it.
                "payload": {
                    "correction": {
                        "episodeId": "01890000-0000-7000-8000-000000000001",
                        "proposedPatchDigest": "sha256:" + "a" * 64,
                        "acceptedPatchDigest": "sha256:" + "b" * 64,
                        "reasonCodes": ["style"],
                        "magnitude": "minor",
                        # `D-07`: taste stays local to the people it came from.
                        "scope": "team",
                        "correctingPrincipalRole": "user",
                    }
                },
            },
        }
        res = self._client_send(cmd_frame)
        self.assertEqual(res.get("frameType"), "receipt")
        receipt = res.get("receipt", {})
        self.assertEqual(receipt.get("status"), "completed")
        self.assertEqual(receipt.get("result", {}).get("status"), "recorded")

        events = self.inbox.get_events("run-200")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["payload"]["kind"], "CorrectionRecorded")

    def test_cancel_run(self) -> None:
        start_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "StartRun",
                "commandId": "cmd-start-3",
                "idempotencyKey": "idem-start-3",
                "runId": "run-300",
                "actor": "operator",
                "payload": {
                    "manifestPath": "manifest.json",
                    "repoPath": ".",
                    "brief": "cancel test",
                },
            },
        }
        self._client_send(start_frame)

        cancel_frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "Cancel",
                "commandId": "cmd-cancel-3",
                "idempotencyKey": "idem-cancel-3",
                "runId": "run-300",
                "actor": "operator",
                "payload": {},
            },
        }
        res = self._client_send(cancel_frame)
        self.assertEqual(res.get("frameType"), "receipt")
        self.assertEqual(res.get("receipt", {}).get("result", {}).get("status"), "cancelled")


if __name__ == "__main__":
    unittest.main()
