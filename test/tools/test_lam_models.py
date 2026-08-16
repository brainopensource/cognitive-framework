"""Tests for LAM OpenRouter model band registry."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

tools_dir = Path(__file__).resolve().parents[2] / "tools" / "002_LLM_API_MOCK"
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from models import load_models, models_for_band


class TestLamModels(unittest.TestCase):
    def test_load_models_structure(self) -> None:
        models = load_models()
        self.assertIn("free", models)
        self.assertIn("medium", models)
        self.assertIn("high", models)
        self.assertIn("top", models)

    def test_top_band_is_empty_and_refuses_to_run(self) -> None:
        models = load_models()
        self.assertEqual(models["top"], [])
        with self.assertRaises(RuntimeError):
            models_for_band("top")

    def test_free_band_returns_list(self) -> None:
        free_models = models_for_band("free")
        self.assertIsInstance(free_models, list)
        self.assertGreater(len(free_models), 0)


if __name__ == "__main__":
    unittest.main()
