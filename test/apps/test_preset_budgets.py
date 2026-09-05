"""T-79 (Wave 2, CMX-01): one product budget catalog, three distinct ceilings.

SCAFFOLD -- these are the acceptance criteria from the T-79 row in
``docs/execution/tasks.md``, written before the implementation so the target
is falsifiable rather than described. Several assertions are RED today and
are expected to stay red until T-79 lands; that is the point of filing them.

Current (pre-T-79) state this test pins down:
  * `fast`/`balanced`/`max` all point at `vg-code-default/budget-policy.json`,
    a policy carrying neither a cost nor a turn dimension, so the three
    presets are byte-identical in the only place a budget could bite.
  * `CodingMaxFacade.run` carries `max_turns: int = 40` as a Python default,
    which silently overrides whatever the catalog declares.

Do NOT weaken these to green. They close when the facade reads
`packs/code-default/presets.json` and each preset declares its own policy.
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from vanguard.packages.apps.coding_max.facade import CodingMaxFacade

ROOT = Path(__file__).resolve().parents[2]
PRESETS_JSON = ROOT / "packs" / "code-default" / "presets.json"
MANIFESTS = ROOT / "vanguard" / "packages" / "agency" / "manifests"

#: The frozen catalog from the T-79 specification (µUSD, turns).
EXPECTED = {
    "fast": {"usd_micros": 50_000, "turns": 8},
    "balanced": {"usd_micros": 150_000, "turns": 20},
    "max": {"usd_micros": 400_000, "turns": 40},
}


def _catalog() -> dict:
    return json.loads(PRESETS_JSON.read_text(encoding="utf-8"))["presets"]


class TheCatalogIsTheSingleSourceOfBudget(unittest.TestCase):
    """GREEN today: the catalog itself already declares distinct ceilings."""

    def test_the_catalog_declares_the_frozen_ceilings(self) -> None:
        catalog = _catalog()
        for preset, expected in EXPECTED.items():
            budget = catalog[preset]["budget"]
            self.assertEqual(budget["usd_micros"], expected["usd_micros"], preset)
            self.assertEqual(budget["turns"], expected["turns"], preset)

    def test_the_three_ceilings_are_mutually_distinct(self) -> None:
        catalog = _catalog()
        costs = {catalog[p]["budget"]["usd_micros"] for p in EXPECTED}
        turns = {catalog[p]["budget"]["turns"] for p in EXPECTED}
        self.assertEqual(len(costs), 3, "presets must not share a cost ceiling")
        self.assertEqual(len(turns), 3, "presets must not share a turn ceiling")


class TheProductPathReadsThatCatalog(unittest.TestCase):
    """RED until T-79 lands. These are the implementation's real target."""

    def test_max_turns_is_not_a_python_default_in_the_facade(self) -> None:
        default = inspect.signature(CodingMaxFacade.run).parameters["max_turns"].default
        self.assertIs(
            default, inspect.Parameter.empty,
            "T-79: the turn ceiling must come from presets.json, not from a "
            "Python default that silently overrides the catalog",
        )

    def test_each_preset_declares_a_distinct_budget_policy(self) -> None:
        policies = {}
        for preset in EXPECTED:
            manifest = json.loads(
                (MANIFESTS / f"vg-code-{preset}" / "manifest.json").read_text(encoding="utf-8"))
            policies[preset] = manifest.get("budgetPolicy")
        self.assertEqual(
            len(set(policies.values())), 3,
            f"T-79: presets route to byte-identical budget policies: {policies}",
        )

    def test_the_product_budget_policy_carries_cost_and_turn_dimensions(self) -> None:
        for preset in EXPECTED:
            manifest = json.loads(
                (MANIFESTS / f"vg-code-{preset}" / "manifest.json").read_text(encoding="utf-8"))
            policy = json.loads(
                (MANIFESTS / str(manifest["budgetPolicy"])).read_text(encoding="utf-8"))
            self.assertIn("usdMicros", policy, f"{preset}: no cost dimension")
            self.assertIn("turns", policy, f"{preset}: no turn dimension")


@unittest.skip("T-79 not implemented: requires the facade to read presets.json")
class TheCeilingReachesTheLedger(unittest.TestCase):
    """The T-79 falsifier proper. Unskip as part of the implementation."""

    def test_episode_started_carries_the_declared_ceiling(self) -> None:
        """`EpisodeStarted.budgetCeiling` must match presets.json exactly."""
        raise NotImplementedError("T-79")

    def test_fast_halts_at_turn_eight_with_budget_exhausted(self) -> None:
        raise NotImplementedError("T-79")


if __name__ == "__main__":
    unittest.main()
