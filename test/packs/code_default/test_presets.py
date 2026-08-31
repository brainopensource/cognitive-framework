import sys
import unittest
from pathlib import Path

PACK = Path(__file__).resolve().parents[3] / "packs" / "code-default"
if str(PACK) not in sys.path:
    sys.path.insert(0, str(PACK))
from load import compile_preset, load_preset


class CodePresetTests(unittest.TestCase):
    def test_all_presets_compile_through_one_composition_path(self) -> None:
        compiled = {name: compile_preset(name) for name in ("fast", "balanced", "max")}
        self.assertEqual(compiled["fast"].capability_ceiling, compiled["max"].capability_ceiling)
        self.assertLess(compiled["fast"].budget.turns, compiled["balanced"].budget.turns)
        self.assertLess(compiled["balanced"].budget.turns, compiled["max"].budget.turns)

    def test_unknown_and_negative_preset_data_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            load_preset("unknown")
