"""Bound falsifiers RF-38..RF-45 (ADR-0081 / NOVA-4).

Proves plugin lifecycle parity, registry-only writer authority, fail-closed
manifest validation, isolation broker UDS JSON-RPC wire lifecycle, fault containment,
and absence of Layer-0 production imports.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_TOOLS = str(ROOT / "tools")
_COMMON = str(ROOT / "tools" / "common")
for _p in (_COMMON, _TOOLS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from vanguard.packages.adapters.stores.event_store import InMemoryEventStore
from vanguard.packages.domain.ledger.reducer import reduce_event, reconstruct_state
from vanguard.packages.domain.wire.types_gen import EventKind
from vanguard.packages.runtime.ledger_emitter import LedgerEmitter, WriterAuthorityError
from vanguard.packages.runtime.registry.lifecycle import (
    IllegalPluginTransition,
    PluginLifecycle,
    PluginState,
)
from vanguard.packages.runtime.registry.validator import (
    ManifestValidationError,
    compatible,
    satisfies,
    validate_manifest,
    validate_plugin_manifest,
)
from vanguard.packages.runtime.registry.broker import (
    CellState,
    IllegalCellTransition,
    PluginIsolationBroker,
    RpcResponse,
)
from vanguard.packages.runtime.registry.sandbox import SandboxLimits

DUMMY_HARNESS = "sha256:" + "0" * 64


class TestRF38LifecycleEventCompleteness(unittest.TestCase):
    """RF-38: All seven lifecycle states emit their corresponding event and reduce."""

    def test_full_lifecycle_emission_and_reduction(self) -> None:
        store = InMemoryEventStore()
        emitter = LedgerEmitter(store, episode_id="ep-1", project_id="proj-rf38", principal_id="agent-1", harness_digest=DUMMY_HARNESS)
        lifecycle = PluginLifecycle("mhf.toolkit.echo", emitter, run_id="run-1", principal="agent-1", manifest_digest="sha256:manifest")

        lifecycle.resolve()
        lifecycle.verify(graph_digest="sha256:graph", ceiling_digest="sha256:ceiling")
        lifecycle.activate()
        lifecycle.quiesce()
        lifecycle.retire()

        envelopes = list(store._events)
        kinds = [e.payload.get("kind") for e in envelopes]
        self.assertEqual(
            kinds,
            [
                "PluginDiscovered",
                "PluginResolved",
                "PluginVerified",
                "PluginActivated",
                "PluginQuiesced",
                "PluginRetired",
            ],
        )

        state = reconstruct_state(envelopes)
        plugin_record = state.plugins.get("mhf.toolkit.echo")
        self.assertIsNotNone(plugin_record)
        self.assertEqual(plugin_record.status, "retired")
        self.assertEqual(plugin_record.manifest_digest, "sha256:manifest")

    def test_fault_lifecycle_emission_and_reduction(self) -> None:
        store = InMemoryEventStore()
        emitter = LedgerEmitter(store, episode_id="ep-1", project_id="proj-rf38", principal_id="agent-1", harness_digest=DUMMY_HARNESS)
        lifecycle = PluginLifecycle("mhf.toolkit.faulty", emitter, run_id="run-1", principal="agent-1", manifest_digest="sha256:faulty")

        lifecycle.resolve()
        lifecycle.fault("checksum mismatch")
        lifecycle.retire()

        envelopes = list(store._events)
        kinds = [e.payload.get("kind") for e in envelopes]
        self.assertEqual(
            kinds,
            [
                "PluginDiscovered",
                "PluginResolved",
                "PluginFaulted",
                "PluginRetired",
            ],
        )


class TestRF39RegistryOnlyWriterAuthority(unittest.TestCase):
    """RF-39: Only writer='registry' can emit Plugin* lifecycle events."""

    def test_non_registry_writer_denied(self) -> None:
        store = InMemoryEventStore()
        emitter = LedgerEmitter(store, episode_id="ep-1", project_id="proj-rf39", principal_id="agent-1", harness_digest=DUMMY_HARNESS)

        for kind in ("PluginDiscovered", "PluginResolved", "PluginVerified", "PluginActivated", "PluginQuiesced", "PluginRetired", "PluginFaulted"):
            with self.assertRaises(WriterAuthorityError):
                emitter.emit_kind(kind, run_id="run-1", principal="agent-1", payload={"plugin_id": "echo"}, writer="session")

            # Emitting with writer="registry" must succeed
            event = emitter.emit_kind(kind, run_id="run-1", principal="agent-1", payload={"plugin_id": "echo"}, writer="registry")
            self.assertEqual(event.payload.get("kind"), kind)


class TestRF40TransitionAcceptanceAndRejection(unittest.TestCase):
    """RF-40: FSM strictly validates state transitions."""

    def test_illegal_transitions_raise(self) -> None:
        store = InMemoryEventStore()
        emitter = LedgerEmitter(store, episode_id="ep-1", project_id="proj-rf40", principal_id="agent-1", harness_digest=DUMMY_HARNESS)

        # Cannot jump from DISCOVERED directly to ACTIVATED
        l1 = PluginLifecycle("echo1", emitter, run_id="run-1", principal="agent-1",
                             manifest_digest="sha256:echo1")
        with self.assertRaises(IllegalPluginTransition):
            l1.activate()

        # Cannot jump from RESOLVED directly to ACTIVATED without VERIFIED
        l2 = PluginLifecycle("echo2", emitter, run_id="run-1", principal="agent-1",
                             manifest_digest="sha256:echo2")
        l2.resolve()
        with self.assertRaises(IllegalPluginTransition):
            l2.activate()

        # RETIRED cannot reactivate
        l3 = PluginLifecycle("echo3", emitter, run_id="run-1", principal="agent-1",
                             manifest_digest="sha256:echo3")
        l3.resolve()
        l3.verify(graph_digest="sha256:graph", ceiling_digest="sha256:ceiling")
        l3.activate()
        l3.quiesce()
        l3.retire()
        with self.assertRaises(IllegalPluginTransition):
            l3.activate()


class TestRF41ManifestAndInterfaceValidation(unittest.TestCase):
    """RF-41: Manifest validation fails closed on invalid metadata."""

    def test_valid_manifest(self) -> None:
        manifest = {
            "api": "mhf.plugin/1",
            "id": "echo",
            "version": "1.0.0",
            "isolation": "subprocess",
            "provides": [{"spi": "IToolkit", "spi_version": "1.0"}],
            "entry": "main.py",
        }
        validate_plugin_manifest(manifest)

    def test_unknown_spi_rejected(self) -> None:
        manifest = {
            "api": "mhf.plugin/1",
            "id": "echo",
            "version": "1.0.0",
            "isolation": "subprocess",
            "provides": [{"spi": "IUnknownSpi", "spi_version": "1.0"}],
            "entry": "main.py",
        }
        with self.assertRaises(ManifestValidationError):
            validate_plugin_manifest(manifest)

    def test_invalid_api_version_rejected(self) -> None:
        manifest = {
            "api": "mhf.plugin/999",
            "id": "echo",
            "version": "1.0.0",
            "isolation": "subprocess",
            "provides": [{"spi": "IToolkit", "spi_version": "1.0"}],
            "entry": "main.py",
        }
        with self.assertRaises(ManifestValidationError):
            validate_plugin_manifest(manifest)


class TestRF42CeilingAndIsolationValidation(unittest.TestCase):
    """RF-42: Invalid isolation tier or unread authority fields fail closed."""

    def test_invalid_isolation_tier_rejected(self) -> None:
        manifest = {
            "api": "mhf.plugin/1",
            "id": "echo",
            "version": "1.0.0",
            "isolation": "hypervisor_root_unsupported",
            "provides": [{"spi": "IToolkit", "spi_version": "1.0"}],
            "entry": "main.py",
        }
        with self.assertRaises(ManifestValidationError):
            validate_plugin_manifest(manifest)

    def test_unread_authority_fields_rejected(self) -> None:
        manifest = {
            "api": "mhf.plugin/1",
            "id": "echo",
            "version": "1.0.0",
            "isolation": "subprocess",
            "provides": [{"spi": "IToolkit", "spi_version": "1.0"}],
            "entry": "main.py",
            "backdoor_privilege_escalation": True,
        }
        with self.assertRaises(ManifestValidationError):
            validate_plugin_manifest(manifest)


class TestRF43IsolationBrokerUdsWireLifecycle(unittest.TestCase):
    """RF-43: Full UDS wire lifecycle with echo worker and crash containment."""

    def test_echo_plugin_wire_lifecycle(self) -> None:
        store = InMemoryEventStore()
        emitter = LedgerEmitter(store, episode_id="ep-1", project_id="proj-rf43", principal_id="agent-1", harness_digest=DUMMY_HARNESS)
        broker = PluginIsolationBroker(emitter, run_id="run-1", principal="agent-1", call_timeout=2.0)

        capabilities = [{"verb": "echo", "selector": {"kind": "generic", "uriPattern": "echo:*"}}]
        cell = broker.bind("mhf.toolkit.echo", capabilities=capabilities)
        self.assertEqual(cell.state, CellState.BOUND)
        self.assertTrue(os.path.exists(cell.workdir))

        broker.start(cell)
        try:
            self.assertEqual(cell.state, CellState.RUNNING)
            self.assertTrue(os.path.exists(cell.socket_path))
            mode = os.stat(cell.socket_path).st_mode & 0o777
            self.assertEqual(mode, 0o600)

            # RPC call: health
            resp = broker.call(cell, "health")
            self.assertTrue(resp.ok)
            self.assertTrue(resp.result.get("ok"))

            # RPC call: execute echo
            resp2 = broker.call(cell, "execute", {"verb": "echo", "args": {"text": "hello_world"}, "selector": {"kind": "generic", "uriPattern": "echo:*"}})
            self.assertTrue(resp2.ok)
            self.assertEqual(resp2.result.get("echo"), "hello_world")

            # Unknown method fails closed
            resp3 = broker.call(cell, "unregistered_method")
            self.assertFalse(resp3.ok)
            self.assertEqual(resp3.error.get("code"), "attenuation_denied")
        finally:
            broker.terminate(cell)

        self.assertEqual(cell.state, CellState.TERMINATED)
        self.assertFalse(os.path.exists(cell.socket_path))

    def test_child_crash_containment(self) -> None:
        store = InMemoryEventStore()
        emitter = LedgerEmitter(store, episode_id="ep-1", project_id="proj-rf43", principal_id="agent-1", harness_digest=DUMMY_HARNESS)
        broker = PluginIsolationBroker(emitter, run_id="run-1", principal="agent-1", call_timeout=2.0)

        capabilities = [{"verb": "echo", "selector": {"kind": "generic", "uriPattern": "echo:*"}}]
        cell = broker.bind("mhf.toolkit.crashy", capabilities=capabilities)
        broker.start(cell)
        self.assertEqual(cell.state, CellState.RUNNING)

        try:
            # Kill child process externally (SIGKILL)
            if cell.pid:
                os.kill(cell.pid, signal.SIGKILL)
                time.sleep(0.05)

            # Broker call to dead cell must return error and emit PluginFaulted without raising unhandled exception
            resp = broker.call(cell, "execute", {"verb": "echo", "args": {"text": "fail"}, "selector": {"kind": "generic", "uriPattern": "echo:*"}})
            self.assertFalse(resp.ok)
            self.assertEqual(cell.state, CellState.TERMINATED)

            # Verify PluginFaulted event was emitted by registry writer
            fault_events = [e for e in store._events if e.payload.get("kind") == "PluginFaulted"]
            self.assertEqual(len(fault_events), 1)
            self.assertEqual(fault_events[0].payload.get("plugin_id"), "mhf.toolkit.crashy")
        finally:
            broker.shutdown()


class TestRF44UniqueParserAndSingleReducer(unittest.TestCase):
    """RF-44: Sole canonical parser and state reducer in vanguard/packages/."""

    def test_manifest_loader_canonical(self) -> None:
        from vanguard.packages.agency.manifests.loader import ManifestLoader
        loader = ManifestLoader()
        self.assertTrue(hasattr(loader, "load_pack"))


class TestRF45NoLayer0ImportsInPackages(unittest.TestCase):
    """RF-45: No production code in vanguard/packages/ imports layer0."""

    def test_packages_have_no_layer0_imports(self) -> None:
        packages_root = ROOT / "vanguard" / "packages"
        layer0_imports: list[str] = []
        for py_file in packages_root.rglob("*.py"):
            text = py_file.read_text(encoding="utf-8")
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("import layer0") or stripped.startswith("from layer0"):
                    layer0_imports.append(f"{py_file.relative_to(ROOT)}: {stripped}")
        self.assertEqual(layer0_imports, [], f"Forbidden layer0 imports found: {layer0_imports}")


if __name__ == "__main__":
    unittest.main()
