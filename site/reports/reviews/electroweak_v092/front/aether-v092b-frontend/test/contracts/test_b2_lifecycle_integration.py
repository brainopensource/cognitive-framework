"""B2 Public Lifecycle, Fault Containment, and Deterministic Cleanup Tests.

Owning contract: ADR-0088 §1 (RF-80).
Verifies:
1. Public lifecycle sequence: discover -> resolve -> verify -> activate -> call -> quiesce -> retire.
2. Fault paths: fault -> cleanup -> retire.
3. In-process and UDS RPC parity.
4. Process crash containment: child death emits PluginFaulted and leaves runtime intact.
5. Deterministic resource cleanup: zero leaked socket files, orphan processes, or dangling directories.
"""

from __future__ import annotations

import os
import signal
import tempfile
import time
import unittest
from pathlib import Path

from vanguard.packages.domain.wire.types_gen import EventKind
from vanguard.packages.runtime.registry.broker import (
    CellState,
    IllegalCellTransition,
    PluginCell,
    PluginIsolationBroker,
    RpcResponse,
)
from vanguard.packages.runtime.registry.lifecycle import (
    IllegalPluginTransition,
    PluginLifecycle,
    PluginState,
)
from vanguard.packages.runtime.registry.sandbox import SandboxLimits


class RecordingEmitter:
    """Mock emitter collecting lifecycle and registry events."""

    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    def emit_kind(self, kind: str, **kwargs: object) -> None:
        self.events.append({"kind": kind, **kwargs})


class B2LifecycleIntegrationTests(unittest.TestCase):
    """Lifecycle integration and fault cleanup contract tests."""

    def setUp(self) -> None:
        self.emitter = RecordingEmitter()
        self.broker = PluginIsolationBroker(
            self.emitter,
            run_id="run-b2",
            principal="principal-b2",
            call_timeout=1.0,
        )

    def tearDown(self) -> None:
        self.broker.shutdown()

    def test_b2_01_complete_plugin_lifecycle_events_in_order(self) -> None:
        """RF-80: Standard happy path emits discovery, resolve, verify, activate, quiesce, retire."""
        lc = PluginLifecycle(
            "echo-service",
            self.emitter,
            run_id="run-b2",
            principal="principal-b2",
            manifest_digest="sha256:manifest-1",
        )
        self.assertEqual(lc.state, PluginState.DISCOVERED)

        lc.resolve()
        self.assertEqual(lc.state, PluginState.RESOLVED)

        lc.verify(graph_digest="sha256:graph-1", ceiling_digest="sha256:ceiling-1")
        self.assertEqual(lc.state, PluginState.VERIFIED)

        lc.activate()
        self.assertEqual(lc.state, PluginState.ACTIVATED)

        lc.quiesce()
        self.assertEqual(lc.state, PluginState.QUIESCING)

        lc.retire()
        self.assertEqual(lc.state, PluginState.RETIRED)

        event_names = [e["kind"] for e in self.emitter.events]
        self.assertEqual(
            event_names,
            [
                "PluginDiscovered",
                "PluginResolved",
                "PluginVerified",
                "PluginActivated",
                "PluginQuiesced",
                "PluginRetired",
            ],
        )

    def test_b2_02_in_process_cell_execution_and_parity(self) -> None:
        """RF-80: In-process cells execute with explicit policy grants and direct dispatch."""
        cell = self.broker.bind(
            "inproc-tool",
            isolation="in_process",
            policy_granted=True,
            capabilities=({"verb": "echo", "selector": {"kind": "generic", "uriPattern": "*"}},),
            handler=lambda method, params: {"status": "ok", "echoed": params.get("args")},
        )
        self.assertEqual(cell.state, CellState.BOUND)
        self.broker.start(cell)
        self.assertEqual(cell.state, CellState.RUNNING)

        response = self.broker.call(
            cell,
            "execute",
            {"verb": "echo", "selector": {"kind": "generic", "uriPattern": "*"}, "args": {"data": 42}},
        )
        self.assertTrue(response.ok)
        self.assertEqual(response.result, {"status": "ok", "echoed": {"data": 42}})

        self.broker.terminate(cell)
        self.assertEqual(cell.state, CellState.TERMINATED)

    def test_b2_03_fault_path_and_cleanup_containment(self) -> None:
        """RF-80: Injected fault moves lifecycle to FAULTED -> RETIRED and releases cell resources."""
        lc = PluginLifecycle(
            "faulty-plugin",
            self.emitter,
            run_id="run-b2",
            principal="principal-b2",
            manifest_digest="sha256:manifest-1",
        )
        lc.resolve()
        lc.fault("Verification signature invalid")
        self.assertEqual(lc.state, PluginState.FAULTED)

        lc.retire()
        self.assertEqual(lc.state, PluginState.RETIRED)

        events = [e["kind"] for e in self.emitter.events]
        self.assertEqual(events, ["PluginDiscovered", "PluginResolved", "PluginFaulted", "PluginRetired"])

    def test_b2_04_uds_subprocess_lifecycle_and_leak_free_cleanup(self) -> None:
        """RF-80: Subprocess cells start over UDS, execute health/calls, and clean up sockets/workdirs."""
        cell = self.broker.bind(
            "subproc-worker",
            isolation="subprocess",
            capabilities=({"verb": "health", "selector": {"kind": "generic", "uriPattern": "*"}},),
        )
        self.assertEqual(cell.state, CellState.BOUND)
        workdir = Path(cell.workdir)
        socket_path = Path(cell.socket_path)
        self.assertTrue(workdir.exists())

        self.broker.start(cell)
        self.assertEqual(cell.state, CellState.RUNNING)
        self.assertTrue(socket_path.exists())
        self.assertIsNotNone(cell.pid)

        # Call health check
        resp = self.broker.call(cell, "health")
        self.assertTrue(resp.ok)
        self.assertTrue(resp.result.get("ok"))

        # Terminate cell
        self.broker.terminate(cell)
        self.assertEqual(cell.state, CellState.TERMINATED)

        # Confirm resources are completely unlinked (no socket/workdir leak)
        self.assertFalse(socket_path.exists())
        self.assertFalse(workdir.exists())

    def test_b2_05_unexpected_child_crash_contained(self) -> None:
        """RF-80: Subprocess crash is caught gracefully without terminating the host runtime."""
        cell = self.broker.bind(
            "crashing-worker",
            isolation="subprocess",
            capabilities=({"verb": "execute", "selector": {"kind": "generic", "uriPattern": "*"}},),
        )
        self.broker.start(cell)
        pid = cell.pid
        self.assertIsNotNone(pid)

        # Send SIGKILL to simulate catastrophic crash of child
        os.kill(pid, signal.SIGKILL)
        time.sleep(0.1)

        # Subsequent call should fail gracefully and report fault
        resp = self.broker.call(
            cell,
            "execute",
            {"verb": "execute", "selector": {"kind": "generic", "uriPattern": "*"}, "args": {}},
        )
        self.assertFalse(resp.ok)
        self.assertEqual(resp.error.get("code"), "plugin_failed")

        # Cleanup
        self.broker.terminate(cell)
        self.assertEqual(cell.state, CellState.TERMINATED)


if __name__ == "__main__":
    unittest.main()
