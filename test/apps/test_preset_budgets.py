"""T-79 (Wave 2, CMX-01): one product budget catalog, three distinct ceilings.

``EpisodeStarted.budgetCeiling`` is the declared catalog identity and MUST
match ``presets.json`` exactly. An explicit ``max_turns`` may only attenuate
the loop bound; that override is recorded on ``budgetAttenuation``, never by
rewriting the catalog ceiling.
"""

from __future__ import annotations

import inspect
import json
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.apps.coding_max.facade import CodingMaxFacade
from vanguard.packages.ports.event_store import EventRange

ROOT = Path(__file__).resolve().parents[2]
PRESETS_JSON = ROOT / "packs" / "code-default" / "presets.json"
MANIFESTS = ROOT / "vanguard" / "packages" / "agency" / "manifests"

EXPECTED = {
    "fast": {"usd_micros": 50_000, "turns": 8},
    "balanced": {"usd_micros": 150_000, "turns": 20},
    "max": {"usd_micros": 400_000, "turns": 40},
}

_KEEP_WORKING = {
    "kind": "effect",
    "action": "fs.read",
    "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
    "args": {"path": "README.md"},
    "note": "work remains",
}


def _catalog() -> dict:
    return json.loads(PRESETS_JSON.read_text(encoding="utf-8"))["presets"]


def _kind(event: object) -> str:
    payload = getattr(event, "payload", {}) or {}
    return str(getattr(event, "mhf_kind", None) or payload.get("kind") or "")


def _events(state_dir: Path, run_id: str) -> list:
    store = SqliteEventStore(state_dir / "events.sqlite3")
    try:
        result = store.read(EventRange(run_id=run_id))
        return list(result.value or ())
    finally:
        store.close()


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
    def test_max_turns_is_not_a_python_default_in_the_facade(self) -> None:
        default = inspect.signature(CodingMaxFacade.run).parameters["max_turns"].default
        self.assertNotEqual(
            default, 40,
            "T-79: the turn ceiling must come from presets.json, not from a "
            "Python default that silently overrides the catalog",
        )
        self.assertTrue(
            default in (None, inspect.Parameter.empty),
            "omitted max_turns must resolve from the catalog, not a numeric default",
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
        catalog = _catalog()
        for preset in EXPECTED:
            manifest = json.loads(
                (MANIFESTS / f"vg-code-{preset}" / "manifest.json").read_text(encoding="utf-8"))
            policy = json.loads(
                (MANIFESTS / str(manifest["budgetPolicy"])).read_text(encoding="utf-8"))
            self.assertIn("usdMicros", policy, f"{preset}: no cost dimension")
            self.assertIn("turns", policy, f"{preset}: no turn dimension")
            budget = catalog[preset]["budget"]
            self.assertEqual(int(policy["usdMicros"]), budget["usd_micros"], preset)
            self.assertEqual(int(policy["turns"]), budget["turns"], preset)
            self.assertEqual(int(policy["tokens"]), budget["tokens"], preset)
            self.assertEqual(int(policy["wallClockMillis"]), budget["millis"], preset)


class TheCeilingReachesTheLedger(unittest.TestCase):
    """Declared catalog identity on EpisodeStarted; fast halts at turn eight."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp.name).resolve()
        (self.workspace / "README.md").write_text("subject\n", encoding="utf-8")
        (self.workspace / "pyproject.toml").write_text("[project]\nname='t79'\n", encoding="utf-8")
        self.state_dir = self.workspace / ".vanguard"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_episode_started_carries_the_declared_ceiling(self) -> None:
        catalog = _catalog()
        for preset, expected in EXPECTED.items():
            run_id = f"run-ceiling-{preset}"
            CodingMaxFacade(workspace=self.workspace).run(
                "prove the declared ceiling",
                preset=preset, run_id=run_id, state_dir=self.state_dir,
                interactive=False, model=FakeModel([{"kind": "finish", "note": "stop"}]),
            )
            started = next(
                event for event in _events(self.state_dir, run_id)
                if _kind(event) == "EpisodeStarted")
            ceiling = dict(started.payload.get("budgetCeiling") or {})
            budget = catalog[preset]["budget"]
            self.assertEqual(int(ceiling["usd_micros"]), expected["usd_micros"], preset)
            self.assertEqual(int(ceiling["turns"]), expected["turns"], preset)
            self.assertEqual(int(ceiling["tokens"]), budget["tokens"], preset)
            self.assertEqual(int(ceiling["millis"]), budget["millis"], preset)
            self.assertNotIn("budgetAttenuation", started.payload, preset)

    def test_fast_halts_at_turn_eight_with_budget_exhausted(self) -> None:
        files = [f"file_{i}.txt" for i in range(12)]
        for name in files:
            (self.workspace / name).write_text(f"{name}\n", encoding="utf-8")
        tape = []
        for name in files:
            item = dict(_KEEP_WORKING)
            item["args"] = {"path": name}
            item["note"] = f"inspect {name}"
            tape.append(item)
        result = CodingMaxFacade(workspace=self.workspace).run(
            "keep going past the catalog",
            preset="fast", run_id="run-fast-halt", state_dir=self.state_dir,
            interactive=False, model=FakeModel(tape),
        )
        self.assertEqual(result.outcome, "budget_exhausted")
        turns = [
            int((event.payload or {}).get("turn", -1))
            for event in _events(self.state_dir, "run-fast-halt")
            if _kind(event) == "TurnStarted"
        ]
        self.assertTrue(turns)
        self.assertLess(max(turns), 8, "turn 9 (0-based index 8) must not run under fast")
        self.assertEqual(len(turns), 8)

    def test_explicit_override_does_not_rewrite_the_declared_ceiling(self) -> None:
        CodingMaxFacade(workspace=self.workspace).run(
            "attenuate without lying",
            preset="fast", run_id="run-attenuate", state_dir=self.state_dir,
            interactive=False, max_turns=6,
            model=FakeModel([{"kind": "finish", "note": "stop"}]),
        )
        started = next(
            event for event in _events(self.state_dir, "run-attenuate")
            if _kind(event) == "EpisodeStarted")
        ceiling = dict(started.payload.get("budgetCeiling") or {})
        self.assertEqual(int(ceiling["usd_micros"]), 50_000)
        self.assertEqual(int(ceiling["turns"]), 8)
        self.assertEqual(int(started.payload["maxTurns"]), 6)
        self.assertEqual(started.payload["budgetAttenuation"], {"turns": 6})


if __name__ == "__main__":
    unittest.main()
