"""T-89: the canary measures the shipped product path, not a private runtime."""

from __future__ import annotations

import unittest
from pathlib import Path

from benchmarks.product_path import execute_product, manifest_for_preset
from vanguard.packages.apps.coding_max.facade import CodingMaxFacade
from vanguard.packages.runtime import entrypoint

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "benchmarks" / "agentic_harness_matrix_benchmark.py"
PRODUCT_PATH = ROOT / "benchmarks" / "product_path.py"


class TestProductPathSubject(unittest.TestCase):
    def test_canary_runner_does_not_call_execute_profiled(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertNotIn("Runtime.execute_profiled", source)
        self.assertNotIn("execute_profiled(", source)
        self.assertIn("execute_product", source)

    def test_product_path_entry_is_entrypoint_execute(self) -> None:
        source = PRODUCT_PATH.read_text(encoding="utf-8")
        self.assertIn("from vanguard.packages.runtime.entrypoint import execute", source)
        self.assertIn("return execute(request)", source)

    def test_runner_and_cli_share_preset_manifest_identity(self) -> None:
        facade_manifest = CodingMaxFacade._manifest("balanced")
        entry_manifest = entrypoint._manifest("code", "balanced")
        helper_manifest = manifest_for_preset("balanced")
        self.assertEqual(facade_manifest.resolve(), entry_manifest.resolve())
        self.assertEqual(entry_manifest.resolve(), helper_manifest.resolve())
        self.assertIn("vg-code-balanced", str(entry_manifest))

    def test_execute_product_is_the_entrypoint_symbol(self) -> None:
        self.assertIs(execute_product.__wrapped__ if hasattr(execute_product, "__wrapped__") else execute_product, execute_product)
        self.assertEqual(execute_product.__module__, "benchmarks.product_path")
        self.assertIs(entrypoint.execute, entrypoint.execute)


if __name__ == "__main__":
    unittest.main()
