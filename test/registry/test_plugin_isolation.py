"""Plugin subprocess isolation: FSM, UDS JSON-RPC, rlimits, crash containment."""

from __future__ import annotations

import contextlib
import io
import os
import signal
import time
import unittest
from pathlib import Path

from vanguard.packages.adapters.stores.event_store import InMemoryEventStore
from vanguard.packages.runtime.ledger_emitter import LedgerEmitter
from vanguard.packages.runtime.registry.broker import CellState, IllegalCellTransition, PluginIsolationBroker
from vanguard.packages.runtime.registry.sandbox import SandboxLimits
from vanguard.packages.domain.wire.types_gen import EventKind

_LIMITS = SandboxLimits(
    cpu_seconds=2,
    address_space_bytes=256 * 1024 * 1024,
    max_open_files=32,
    max_processes=64,
)
_FS = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}
_ECHO_CAPS = ({"verb": "echo", "selector": _FS},)
_DUMMY_HARNESS = "sha256:" + "0" * 64


def _echo_params(text: str) -> dict:
    return {"verb": "echo", "args": {"text": text}, "selector": _FS}


def _wait_until(predicate, timeout: float = 3.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.02)
    return False


class PluginIsolationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryEventStore()
        self.emitter = LedgerEmitter(
            self.store,
            episode_id="ep-iso",
            project_id="proj-iso",
            principal_id="agent-1",
            harness_digest=_DUMMY_HARNESS,
        )
        self.broker = PluginIsolationBroker(
            emitter=self.emitter,
            run_id="run-iso",
            principal="agent-1",
        )

    def tearDown(self) -> None:
        self.broker.shutdown()

    def test_fsm_bind_start_terminate(self) -> None:
        cell = self.broker.bind("mhf.toolkit.echo", limits=_LIMITS, capabilities=_ECHO_CAPS)
        self.assertEqual(cell.state, CellState.BOUND)
        self.broker.start(cell)
        self.assertEqual(cell.state, CellState.RUNNING)
        self.assertIsNotNone(cell.pid)
        self.assertTrue(Path(cell.socket_path).exists())
        mode = os.stat(cell.socket_path).st_mode & 0o777
        self.assertEqual(mode, 0o600, f"socket mode is {oct(mode)}, expected 0o600")
        self.broker.terminate(cell)
        self.assertEqual(cell.state, CellState.TERMINATED)
        self.assertFalse(Path(cell.socket_path).exists())

    def test_in_process_isolation_tier_direct_dispatch(self) -> None:
        with self.assertRaises(PermissionError):
            self.broker.bind("mhf.toolkit.denied", isolation="in_process")
        cell = self.broker.bind(
            "mhf.toolkit.inproc",
            isolation="in_process",
            capabilities=_ECHO_CAPS,
            handler=lambda method, payload: {"inproc": payload.get("args", {}).get("text", "")},
            policy_granted=True,
        )
        self.assertEqual(cell.state, CellState.BOUND)
        self.assertEqual(cell.isolation, "in_process")
        self.broker.start(cell)
        self.assertEqual(cell.state, CellState.RUNNING)
        self.assertIsNone(cell.pid)
        response = self.broker.call(cell, "execute", _echo_params("direct"))
        self.assertTrue(response.ok)
        self.assertEqual(response.result["inproc"], "direct")
        self.broker.terminate(cell)
        self.assertEqual(cell.state, CellState.TERMINATED)

    def test_illegal_start_from_uninstantiated(self) -> None:
        cell = self.broker.cell("ghost")
        with self.assertRaises(IllegalCellTransition):
            self.broker.start(cell)

    def test_jsonrpc_echo_roundtrip(self) -> None:
        cell = self.broker.bind("mhf.toolkit.echo", limits=_LIMITS, capabilities=_ECHO_CAPS)
        self.broker.start(cell)
        response = self.broker.call(cell, "execute", _echo_params("ping"))
        self.assertTrue(response.ok)
        self.assertEqual(response.result["echo"], "ping")

    def test_child_stdout_does_not_pollute_parent(self) -> None:
        cell = self.broker.bind("mhf.toolkit.echo", limits=_LIMITS, capabilities=_ECHO_CAPS)
        self.broker.start(cell)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            self.broker.call(cell, "execute", _echo_params("LEAK-MARKER"))
        self.assertNotIn("LEAK-MARKER", buf.getvalue())
        log_text = Path(cell.stdout_log).read_text(encoding="utf-8")
        self.assertIn("LEAK-MARKER", log_text)

    def test_sigkill_emits_plugin_failed_and_cleans_socket(self) -> None:
        cell = self.broker.bind("mhf.toolkit.echo", limits=_LIMITS, capabilities=_ECHO_CAPS)
        self.broker.start(cell)
        socket_path = cell.socket_path
        os.kill(cell.pid, signal.SIGKILL)
        self.broker.reap(cell, timeout=3.0)
        self.assertEqual(cell.state, CellState.TERMINATED)
        self.assertFalse(Path(socket_path).exists())
        kinds = [envelope.payload.get("kind") for envelope in self.store._events]
        self.assertIn(EventKind.PLUGIN_FAULTED.value, kinds)
        payload = self.store._events[-1].payload
        self.assertEqual(payload.get("status"), "PluginFailed")

    def test_sigsegv_does_not_crash_broker(self) -> None:
        cell = self.broker.bind("mhf.toolkit.echo", limits=_LIMITS, capabilities=_ECHO_CAPS)
        self.broker.start(cell)
        os.kill(cell.pid, signal.SIGSEGV)
        response = self.broker.call(cell, "execute", _echo_params("x"))
        self.assertFalse(response.ok)
        self.assertEqual(cell.state, CellState.TERMINATED)
        self.assertEqual(self.store._events[-1].payload.get("kind"), EventKind.PLUGIN_FAULTED.value)
        # Broker remains usable for a new cell.
        other = self.broker.bind("mhf.toolkit.echo-2", limits=_LIMITS, capabilities=_ECHO_CAPS)
        self.broker.start(other)
        ok = self.broker.call(other, "health", {})
        self.assertTrue(ok.ok)
        self.broker.terminate(other)

    def test_child_reports_enforced_rlimits(self) -> None:
        cell = self.broker.bind("mhf.toolkit.echo", limits=_LIMITS, capabilities=_ECHO_CAPS)
        self.broker.start(cell)
        health = self.broker.call(cell, "health", {})
        self.assertTrue(health.ok)
        rlimits = health.result["rlimits"]
        self.assertEqual(int(rlimits["cpu"][0]), _LIMITS.cpu_seconds)
        self.assertEqual(int(rlimits["as"][0]), _LIMITS.address_space_bytes)
        self.assertEqual(int(rlimits["nofile"][0]), _LIMITS.max_open_files)
        self.assertEqual(int(rlimits["nproc"][0]), _LIMITS.max_processes)

    def test_reap_is_idempotent_after_clean_terminate(self) -> None:
        cell = self.broker.bind("mhf.toolkit.echo", limits=_LIMITS, capabilities=_ECHO_CAPS)
        self.broker.start(cell)
        self.broker.terminate(cell)
        self.broker.reap(cell, timeout=1.0)
        self.assertEqual(cell.state, CellState.TERMINATED)
        faulted = [e for e in self.store._events if e.payload.get("kind") == EventKind.PLUGIN_FAULTED.value]
        self.assertEqual(faulted, [])

    def test_wait_helper_sees_running_pid(self) -> None:
        cell = self.broker.bind("mhf.toolkit.echo", limits=_LIMITS, capabilities=_ECHO_CAPS)
        self.broker.start(cell)
        self.assertTrue(_wait_until(lambda: cell.pid is not None and os.path.exists(cell.socket_path)))
        self.broker.terminate(cell)


if __name__ == "__main__":
    unittest.main()
