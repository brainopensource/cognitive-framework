from __future__ import annotations

import subprocess
import sys
import unittest

import vanguard
from vanguard.packages.runtime.service.service import RuntimeService
from vanguard.packages.runtime.service.inbox import ServiceInboxStore
from vanguard.packages.adapters.stores.event_store import SqliteEventStore


class TestReleaseIdentity(unittest.TestCase):
    def test_package_version_literal(self) -> None:
        self.assertEqual(vanguard.__version__, "0.9.3")

    def test_service_capabilities_server_version(self) -> None:
        store = ServiceInboxStore(db_path=":memory:")
        event_store = SqliteEventStore(":memory:")
        service = RuntimeService(inbox_store=store, event_store=event_store)
        frame = service.execute_command({
            "version": "vg.4",
            "frameType": "command",
            "frameId": "frame-1",
            "command": {
                "commandId": "cmd-1",
                "idempotencyKey": "ik-1",
                "name": "GetCapabilities",
                "actor": "test",
                "payload": {},
            },
        })
        receipt = frame.get("receipt", {})
        self.assertEqual(receipt.get("status"), "completed")
        result = receipt.get("result", {})
        self.assertEqual(result.get("serverVersion"), "0.9.3")

    def test_cli_version_flag(self) -> None:
        res = subprocess.run(
            [sys.executable, "-m", "vanguard.packages.runtime.cli", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("0.9.3", res.stdout + res.stderr)
