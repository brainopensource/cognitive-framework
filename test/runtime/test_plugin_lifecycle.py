from __future__ import annotations

import unittest

from vanguard.packages.runtime.registry import (
    IllegalPluginTransition,
    PluginLifecycle,
    PluginState,
)


class RecordingEmitter:
    def __init__(self) -> None:
        self.events: list[str] = []

    def emit_kind(self, kind: str, **_: object) -> None:
        self.events.append(kind)


class PluginLifecycleTests(unittest.TestCase):
    def test_every_state_entry_emits_once(self) -> None:
        emitter = RecordingEmitter()
        lifecycle = PluginLifecycle("echo", emitter, run_id="run", principal="registry")
        lifecycle.resolve()
        lifecycle.verify(graph_digest="sha256:graph")
        lifecycle.activate()
        lifecycle.quiesce()
        lifecycle.retire()
        self.assertEqual(
            emitter.events,
            ["PluginDiscovered", "PluginResolved", "PluginVerified", "PluginActivated",
             "PluginQuiesced", "PluginRetired"],
        )
        self.assertIs(lifecycle.state, PluginState.RETIRED)

    def test_fault_path_and_illegal_transition_fail_closed(self) -> None:
        emitter = RecordingEmitter()
        lifecycle = PluginLifecycle("echo", emitter, run_id="run", principal="registry")
        lifecycle.resolve()
        lifecycle.fault("verification failed")
        lifecycle.retire()
        with self.assertRaises(IllegalPluginTransition):
            lifecycle.activate()
        self.assertEqual(
            emitter.events,
            ["PluginDiscovered", "PluginResolved", "PluginFaulted", "PluginRetired"],
        )


if __name__ == "__main__":
    unittest.main()
