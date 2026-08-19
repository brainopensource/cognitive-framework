"""S-M3-A-01: pack frame, harness compile, plugin catalog."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "packs" / "code-default"


class PackFrameTests(unittest.TestCase):
    def test_harness_and_plugin_yaml_exist(self) -> None:
        self.assertTrue((PACK / "harness.yaml").is_file())
        self.assertTrue((PACK / "plugin.yaml").is_file())
        self.assertTrue((PACK / "oracles").is_dir())
        self.assertTrue((PACK / "oracles" / "registry.json").is_file())

    def test_compose_resolves_catalog_plugins(self) -> None:
        import sys
        sys.path.insert(0, str(PACK))
        from load import compile_pack, discover_plugins

        plugins = discover_plugins()
        for ident in (
            "mhf.planner.drive-until-green",
            "mhf.toolkit.ast-patch",
            "mhf.toolkit.terminal",
            "mhf.toolkit.index",
            "mhf.context.repo-map",
        ):
            self.assertIn(ident, plugins)
        frozen = compile_pack()
        self.assertEqual(frozen.id, "code-default")
        self.assertTrue(frozen.digest.startswith("sha256:"))
        self.assertIn("planner", frozen.resolved_refs)
        self.assertEqual(frozen.budget.turns, 40)
        self.assertEqual(frozen.budget.usd_micros, 250000)


if __name__ == "__main__":
    unittest.main()
