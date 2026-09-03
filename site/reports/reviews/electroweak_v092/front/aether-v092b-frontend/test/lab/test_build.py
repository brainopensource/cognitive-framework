"""Unit tests for lab/build.py (Task B.3)."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = ROOT / "vanguard" / "packages" / "agency" / "manifests"


def load_lab(name: str):
    path = ROOT / "lab" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lab_{name}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestLabBuild(unittest.TestCase):
    def setUp(self) -> None:
        self.build_mod = load_lab("build")

    def test_build_all_packs(self) -> None:
        results = self.build_mod.build_packs(MANIFESTS)
        self.assertGreaterEqual(len(results), 5)
        names = {r["harness"] for r in results}
        self.assertIn("vg-code-default", names)
        self.assertIn("vg-shell-only", names)
        self.assertIn("vg-code-claude-shaped", names)
        self.assertIn("vg-code-opencode-shaped", names)
        self.assertIn("vg-code-swe-mini", names)

        for res in results:
            self.assertTrue(res["composition_digest"].startswith("sha256:"))
            self.assertEqual(res["status"], "built")

    def test_build_single_pack(self) -> None:
        results = self.build_mod.build_packs(MANIFESTS, pack_name="vg-code-default")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["harness"], "vg-code-default")
        self.assertEqual(results[0]["capabilities_count"], 4)

    def test_build_vg_shell_only(self) -> None:
        results = self.build_mod.build_packs(MANIFESTS, pack_name="vg-shell-only")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["harness"], "vg-shell-only")
        self.assertTrue(results[0]["undeletable"])
        self.assertEqual(results[0]["capabilities_count"], 1)


if __name__ == "__main__":
    unittest.main()
