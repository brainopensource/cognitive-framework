from __future__ import annotations

import unittest
from vanguard.packages.runtime.registry.validator import (
    ManifestValidationError,
    validate_plugin_manifest,
)
from vanguard.packages.runtime.registry.lifecycle import (
    IllegalPluginTransition,
    PluginLifecycle,
    PluginState,
)
from vanguard.packages.runtime.registry.broker import (
    PluginIsolationBroker,
    CellState,
)


class DummyEmitter:
    def __init__(self) -> None:
        self.events: list[dict[str, str]] = []

    def emit_kind(self, kind: str, **kwargs: object) -> None:
        self.events.append({"kind": kind, **{str(k): str(v) for k, v in kwargs.items()}})


class TestPluginFullLifecycle(unittest.TestCase):
    def test_valid_manifest_passes_validation(self) -> None:
        manifest = {
            "api": "mhf.plugin/1",
            "id": "org.example.calculator",
            "version": "1.2.0",
            "isolation": "in_process",
            "provides": [{"spi": "IToolkit", "spi_version": "1.0"}],
            "entry": "calculator:plugin_entry",
            "tools": {
                "add": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number"},
                        "b": {"type": "number"},
                    },
                    "required": ["a", "b"],
                }
            },
        }
        validate_plugin_manifest(manifest, hosted_spi_version="1.0")

    def test_invalid_manifest_missing_id_fails_closed(self) -> None:
        manifest = {
            "api": "mhf.plugin/1",
            "version": "1.0.0",
            "isolation": "in_process",
            "provides": [{"spi": "IToolkit", "spi_version": "1.0"}],
            "entry": "calculator:plugin_entry",
        }
        with self.assertRaises(ManifestValidationError):
            validate_plugin_manifest(manifest)

    def test_incompatible_spi_version_fails_closed(self) -> None:
        manifest = {
            "api": "mhf.plugin/1",
            "id": "org.example.future_plugin",
            "version": "2.0.0",
            "isolation": "in_process",
            "provides": [{"spi": "IToolkit", "spi_version": ">=2.0"}],
            "entry": "future:plugin_entry",
        }
        with self.assertRaises(ManifestValidationError):
            validate_plugin_manifest(manifest, hosted_spi_version="1.0")

    def test_unknown_isolation_tier_fails_closed(self) -> None:
        manifest = {
            "api": "mhf.plugin/1",
            "id": "org.example.root_plugin",
            "version": "1.0.0",
            "isolation": "kernel_root_escalated",
            "provides": [{"spi": "IToolkit", "spi_version": "1.0"}],
            "entry": "root:plugin_entry",
        }
        with self.assertRaises(ManifestValidationError):
            validate_plugin_manifest(manifest)

    def test_plugin_lifecycle_state_machine_and_fault(self) -> None:
        emitter = DummyEmitter()
        lc = PluginLifecycle(
            "org.example.test",
            emitter,
            run_id="run-1",
            principal="admin",
            manifest_digest="sha256:abcd",
        )
        self.assertEqual(lc.state, PluginState.DISCOVERED)

        lc.resolve()
        self.assertEqual(lc.state, PluginState.RESOLVED)

        lc.verify(graph_digest="sha256:1111", ceiling_digest="sha256:2222")
        self.assertEqual(lc.state, PluginState.VERIFIED)

        lc.activate()
        self.assertEqual(lc.state, PluginState.ACTIVATED)

        lc.quiesce()
        self.assertEqual(lc.state, PluginState.QUIESCING)

        lc.retire()
        self.assertEqual(lc.state, PluginState.RETIRED)

        # Illegal transition after retirement
        with self.assertRaises(IllegalPluginTransition):
            lc.activate()
