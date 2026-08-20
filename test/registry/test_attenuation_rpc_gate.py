"""Capability leakage gate: RPC must not deliver over-broad work to a plugin cell."""

from __future__ import annotations

import unittest

from layer0.events.store import MemoryLedger
from layer0.registry.broker import PluginIsolationBroker
from layer0.registry.sandbox import SandboxLimits
from vanguard.packages.domain.wire.types_gen import EventKind, SinkClass

_FS = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}
_FS_CHILD = {"kind": "fs", "root": "/workspace", "paths": ["/workspace/README.md"]}
_FS_ETC = {"kind": "fs", "root": "/etc", "paths": ["/etc"]}
_PROC_DENIED = {"kind": "generic", "uriPattern": "proc://exec/allow/id"}
_CEILING = (
    {"verb": "echo", "selector": _FS},
    {"verb": "fs.read", "selector": _FS},
)
_LIMITS = SandboxLimits(
    cpu_seconds=2,
    address_space_bytes=256 * 1024 * 1024,
    max_open_files=32,
    max_processes=64,
)


class AttenuationRpcGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ledger = MemoryLedger()
        self.broker = PluginIsolationBroker(
            emitter=self.ledger.emitter,
            run_id="run-att",
            principal="layer0",
        )
        self.cell = self.broker.bind(
            "mhf.toolkit.echo",
            limits=_LIMITS,
            capabilities=_CEILING,
        )
        self.broker.start(self.cell)

    def tearDown(self) -> None:
        self.broker.shutdown()

    def test_allowed_verb_is_delivered(self) -> None:
        response = self.broker.call(
            self.cell,
            "execute",
            {
                "verb": "echo",
                "args": {"text": "ok"},
                "selector": _FS,
                "sink": SinkClass.OBSERVATION.value,
            },
        )
        self.assertTrue(response.ok)
        self.assertEqual(response.result["echo"], "ok")
        health = self.broker.call(self.cell, "health", {})
        self.assertEqual(health.result["execute_count"], 1)

    def test_unknown_verb_is_denied_before_plugin(self) -> None:
        response = self.broker.call(
            self.cell,
            "execute",
            {
                "verb": "proc.exec",
                "args": {"command": ["id"]},
                "selector": _PROC_DENIED,
                "sink": SinkClass.PRIVILEGED.value,
            },
        )
        self.assertFalse(response.ok)
        self.assertEqual(response.error["code"], "attenuation_denied")
        health = self.broker.call(self.cell, "health", {})
        self.assertEqual(health.result["execute_count"], 0)

    def test_selector_outside_ceiling_is_denied(self) -> None:
        response = self.broker.call(
            self.cell,
            "execute",
            {
                "verb": "fs.read",
                "args": {"path": "/etc/passwd"},
                "selector": _FS_ETC,
                "sink": SinkClass.OBSERVATION.value,
            },
        )
        self.assertFalse(response.ok)
        self.assertEqual(response.error["code"], "attenuation_denied")
        health = self.broker.call(self.cell, "health", {})
        self.assertEqual(health.result["execute_count"], 0)

    def test_plugin_cannot_widen_via_host_callback(self) -> None:
        response = self.broker.call(
            self.cell,
            "host.grant",
            {"verb": "proc.exec", "selector": _PROC_DENIED},
        )
        self.assertFalse(response.ok)
        self.assertEqual(response.error["code"], "attenuation_denied")
        kinds = [envelope.kind for envelope in self.ledger.envelopes]
        self.assertNotIn(EventKind.CAPABILITY_GRANTED, kinds)

    def test_in_ceiling_fs_read_is_delivered(self) -> None:
        response = self.broker.call(
            self.cell,
            "execute",
            {
                "verb": "fs.read",
                "args": {"path": "/workspace/README.md"},
                "selector": _FS_CHILD,
                "sink": SinkClass.OBSERVATION.value,
            },
        )
        self.assertTrue(response.ok)
        health = self.broker.call(self.cell, "health", {})
        self.assertEqual(health.result["execute_count"], 1)


if __name__ == "__main__":
    unittest.main()
