from __future__ import annotations

import unittest

from layer0.events.store import MemoryLedger
from layer0.registry.lifecycle import PluginLifecycle, PluginState
from vanguard.packages.domain.wire.types_gen import EventKind


class RegistryLifecycleTests(unittest.TestCase):
    def test_full_lifecycle_emits_plugin_kinds(self) -> None:
        ledger = MemoryLedger()
        plugin = PluginLifecycle("mhf.toolkit.echo", ledger.emitter, run_id="r", principal="p")
        plugin.resolve()
        plugin.verify()
        plugin.activate()
        plugin.quiesce()
        plugin.retire()
        self.assertEqual(plugin.state, PluginState.RETIRED)
        kinds = [envelope.kind for envelope in ledger.envelopes]
        self.assertEqual(
            kinds,
            [
                EventKind.PLUGIN_RESOLVED,
                EventKind.PLUGIN_ACTIVATED,
                EventKind.PLUGIN_QUIESCED,
                EventKind.PLUGIN_RETIRED,
            ],
        )

    def test_fault_from_activated(self) -> None:
        ledger = MemoryLedger()
        plugin = PluginLifecycle("echo", ledger.emitter, run_id="r", principal="p")
        plugin.resolve()
        plugin.verify()
        plugin.activate()
        plugin.fault("crash")
        self.assertEqual(plugin.state, PluginState.FAULTED)
        self.assertEqual(ledger.envelopes[-1].kind, EventKind.PLUGIN_FAULTED)
