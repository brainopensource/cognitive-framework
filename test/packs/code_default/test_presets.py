from copy import deepcopy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "code-default"
if str(PACK) not in sys.path:
    sys.path.insert(0, str(PACK))
from load import (
    PRESET_NAMES,
    ResolvedPresetPolicy,
    budget_policy_document,
    compile_preset,
    effective_limit,
    load_preset,
    resolve_preset_policy,
)
from vanguard.packages.runtime.paired_evaluation import assert_single_varied_dimension


EXPECTED_BUDGETS = {
    "fast": {"usd_micros": 50_000, "millis": 300_000, "tokens": 16_000, "turns": 8},
    "balanced": {"usd_micros": 150_000, "millis": 900_000, "tokens": 40_000, "turns": 20},
    "max": {"usd_micros": 400_000, "millis": 2_400_000, "tokens": 96_000, "turns": 40},
}


class CodePresetTests(unittest.TestCase):
    def test_all_presets_compile_through_one_composition_path(self) -> None:
        compiled = {name: compile_preset(name) for name in PRESET_NAMES}
        self.assertEqual(compiled["fast"].capability_ceiling, compiled["max"].capability_ceiling)
        self.assertLess(compiled["fast"].budget.turns, compiled["balanced"].budget.turns)
        self.assertLess(compiled["balanced"].budget.turns, compiled["max"].budget.turns)

    def test_unknown_and_negative_preset_data_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            load_preset("unknown")

    def test_declared_ceilings_and_manifest_parity_preserved(self) -> None:
        """NT-B04 / T-79: declared catalog ceilings are preserved and match manifests."""
        manifest_root = ROOT / "vanguard" / "packages" / "agency" / "manifests"
        for name, expected in EXPECTED_BUDGETS.items():
            policy = resolve_preset_policy(name)
            self.assertEqual(policy.name, name)
            self.assertEqual(policy.usd_micros, expected["usd_micros"])
            self.assertEqual(policy.millis, expected["millis"])
            self.assertEqual(policy.tokens, expected["tokens"])
            self.assertEqual(policy.turns, expected["turns"])
            self.assertEqual(policy.as_budget_map(), expected)

            doc = budget_policy_document(name)
            manifest_file = manifest_root / f"vg-code-{name}" / "budget-policy.json"
            if manifest_file.exists():
                manifest_doc = json.loads(manifest_file.read_text(encoding="utf-8"))
                self.assertEqual(doc, manifest_doc, f"{name} manifest budget policy mismatch")

    def test_declared_bounds_are_not_caller_attenuation(self) -> None:
        """Declared catalog bounds cannot be elevated by callers; explicit limit only attenuates."""
        # Omitted explicit limit preserves declared ceiling
        self.assertEqual(effective_limit(20, None), 20)
        # Caller may tighten (attenuate)
        self.assertEqual(effective_limit(20, 10), 10)
        self.assertEqual(effective_limit(20, 0), 0)
        # Caller CANNOT elevate / expand beyond declared ceiling
        self.assertEqual(effective_limit(20, 40), 20)
        self.assertEqual(effective_limit(8, 100), 8)

        # Invalid limits fail closed
        with self.assertRaises(ValueError):
            effective_limit(20, -1)
        with self.assertRaises(ValueError):
            effective_limit(20, "20")  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            effective_limit(20, True)  # type: ignore[arg-type]

    def test_normalized_behavioral_identity_includes_selected_plugins(self) -> None:
        """Normalized behavioral identity includes plugins (planner and context configurations)."""
        fast = load_preset("fast")
        balanced = load_preset("balanced")
        max_p = load_preset("max")

        self.assertIsNone(fast["plugins"]["planner"])
        self.assertEqual(fast["plugins"]["context"]["config"]["token_budget"], 1000)

        self.assertEqual(balanced["plugins"]["planner"]["config"]["max_repair_rounds"], 4)
        self.assertEqual(balanced["plugins"]["context"]["config"]["token_budget"], 3000)

        self.assertEqual(max_p["plugins"]["planner"]["config"]["max_repair_rounds"], 8)
        self.assertEqual(max_p["plugins"]["context"]["config"]["token_budget"], 8000)

    def test_relabeling_identical_behavior_cannot_establish_distinct_treatment(self) -> None:
        """NT-B04: budget-only presets or relabeling cannot establish distinct comparative treatments."""
        base_arm = {
            "harness": "vg-code-balanced",
            "model_id": "m1",
            "plugins": {"planner": 4, "context": 3000},
            "edit_primitive": "apply_patch",
        }
        # Identical configuration relabeled with another name or unchanged configuration
        relabeled_same = deepcopy(base_arm)
        with self.assertRaises(ValueError):
            # No dimension actually varied (changed == [])
            assert_single_varied_dimension(base_arm, relabeled_same, "edit_primitive")

        # Varying multiple keys (e.g. relabeling arm name AND changing budget/primitive)
        multi_varied = deepcopy(base_arm)
        multi_varied["harness"] = "vg-code-max"
        multi_varied["edit_primitive"] = "str_replace"
        with self.assertRaises(ValueError):
            assert_single_varied_dimension(base_arm, multi_varied, "edit_primitive")

        # Legitimate single varied dimension is admitted
        valid_treatment = deepcopy(base_arm)
        valid_treatment["edit_primitive"] = "str_replace"
        assert_single_varied_dimension(base_arm, valid_treatment, "edit_primitive")

