from __future__ import annotations

import unittest

from layer0.compose.compiler import ComposeError, compose
from vanguard.packages.domain.wire.types_gen import HarnessManifest, PluginBindings, PluginRef, Reservation


class ComposeTests(unittest.TestCase):
    def test_identical_inputs_yield_identical_digest(self) -> None:
        manifest = {
            "api": "mhf.harness/1",
            "id": "code-default",
            "plugins": {
                "planner": {"ref": "mhf.planner.drive-until-green@^1"},
                "toolkits": [{"ref": "mhf.toolkit.echo@^1"}],
            },
            "budget": {"usd_micros": 1, "millis": 0, "tokens": 0, "bytes": 0, "turns": 4, "depth": 1},
        }
        known = {
            "mhf.planner.drive-until-green": "sha256:" + "1" * 64,
            "mhf.toolkit.echo": "sha256:" + "2" * 64,
        }
        first = compose(manifest, known_plugins=known)
        second = compose(manifest, known_plugins=known)
        self.assertEqual(first.digest, second.digest)
        self.assertTrue(first.digest.startswith("sha256:"))

    def test_unknown_alias_fails_with_named_path(self) -> None:
        manifest = HarnessManifest(
            api="mhf.harness/1",
            id="x",
            plugins=PluginBindings(planner=PluginRef(ref="missing@1")),
            budget=Reservation(0, 0, 0, 0, 1, 1),
        )
        with self.assertRaises(ComposeError) as caught:
            compose(manifest, known_plugins={})
        self.assertEqual(caught.exception.path, "plugins.planner")
