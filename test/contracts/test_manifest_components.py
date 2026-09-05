"""Contract coverage for product-preset component declarations."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from vanguard.packages.domain.artifacts.graph import BUILTIN_KINDS


ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = ROOT / "vanguard" / "packages" / "agency" / "manifests"
PRODUCT_PRESETS = (
    "vg-code-default",
    "vg-code-fast",
    "vg-code-balanced",
    "vg-code-max",
)
FINISH_COMPONENT = "vg-code-default/finish-tool.json"


class ProductManifestComponentsContract(unittest.TestCase):
    def test_finish_is_flat_declared_and_resolvable_for_all_product_presets(self) -> None:
        self.assertFalse((MANIFESTS / "vg-code-default" / "components").exists())

        for preset in PRODUCT_PRESETS:
            with self.subTest(preset=preset):
                manifest_path = MANIFESTS / preset / "manifest.json"
                raw = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertIn(FINISH_COMPONENT, raw["components"]["tools"])
                self.assertEqual(raw["components"]["tools"].count(FINISH_COMPONENT), 1)

                for paths in raw["components"].values():
                    for component_path in paths:
                        resolved = MANIFESTS / component_path
                        self.assertTrue(
                            resolved.is_file(),
                            f"{preset} component does not resolve: {component_path}",
                        )

                finish_tool = json.loads(
                    (MANIFESTS / FINISH_COMPONENT).read_text(encoding="utf-8")
                )
                self.assertEqual(finish_tool["name"], "finish")
                self.assertEqual(finish_tool["verb"], "agency.finish")
                self.assertEqual(finish_tool["schema"]["type"], "object")
                self.assertIn("summary", finish_tool["schema"]["required"])
                declared_verbs = {capability["verb"] for capability in raw["capabilities"]}
                self.assertIn(finish_tool["verb"], declared_verbs)

    def test_finish_component_uses_a_registered_artifact_kind(self) -> None:
        kind_rows = json.loads((MANIFESTS / "kinds.json").read_text(encoding="utf-8"))
        registered_kinds = {row["kind"] for row in kind_rows}
        self.assertEqual(registered_kinds, set(BUILTIN_KINDS))
        self.assertIn("tool_schema", registered_kinds)


if __name__ == "__main__":
    unittest.main()
