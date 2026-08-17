"""Tests for LAM OpenRouter model band registry.

Band vocabulary is `free | medium | high | top` (S7-C). The historical
`tier1_local / tier2_local / tier3_cloud` names were retired with the band
rework and are asserted absent so they cannot silently return.

`top` is a *spend* band. It stays empty until the Project Lead names frontier
ids in `models.json`, and `models_for_band("top")` must refuse while empty —
that refusal is the budget control, so it is tested as a required behaviour
rather than worked around.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

tools_dir = Path(__file__).resolve().parents[2] / "tools" / "002_LLM_API_MOCK"
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from models import load_models, models_for_band

RETIRED_BANDS = ("tier1_local", "tier2_local", "tier3_cloud")


class TestLamModels(unittest.TestCase):
    def test_load_models_structure(self) -> None:
        models = load_models()
        for band in ("free", "medium", "high", "top"):
            self.assertIn(band, models)
            self.assertIsInstance(models[band], list)

    def test_retired_tier_names_are_absent(self) -> None:
        models = load_models()
        for band in RETIRED_BANDS:
            self.assertNotIn(band, models)

    def test_top_band_refuses_while_unnamed(self) -> None:
        """band=top must fail closed until frontier ids are named by the Project Lead."""
        models = load_models()
        if models["top"]:
            self.assertGreaterEqual(len(models_for_band("top")), 1)
            return
        with self.assertRaises(RuntimeError):
            models_for_band("top")

    def test_unknown_band_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            models_for_band("frontier")

    def test_free_band_returns_list(self) -> None:
        free_models = models_for_band("free")
        self.assertIsInstance(free_models, list)
        self.assertGreater(len(free_models), 0)


if __name__ == "__main__":
    unittest.main()
