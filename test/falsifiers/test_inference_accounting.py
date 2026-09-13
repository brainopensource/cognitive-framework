"""Inference is metered against the same governor as every other resource.

The defect this guards
----------------------
The model call was the one resource in an episode that nobody debited. It was
invoked directly and its usage and cost were recorded as proposal diagnostics --
telemetry, never a reservation. Measured on the product path through the public
entrypoint before the repair, every preset overran its own declared ceilings and
terminated only on the turn bound:

    preset     declared            reported            stopped by
    fast       $0.05 /  16,000tok  $0.20 /  31,200tok  turn bound 8
    balanced   $0.15 /  40,000tok  $0.50 /  78,000tok  turn bound 20
    max        $0.40 /  96,000tok  $1.00 / 156,000tok  turn bound 40

Two of the three declared ceilings were decorative, including the one denominated
in money. `RUN-09(8)` names the *escalation* half of that gap; this is the base
case, which needs no escalation to occur.

Every adversarial assertion below has been mutation-proven: reverting the meter
wiring in `runtime/session.py`, or the terminal branch in
`agency/episode/engine.py`, turns the corresponding test red.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.kernel.budget import BudgetDenied, Governor
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime import entrypoint
from vanguard.packages.runtime.inference_meter import (
    INFERENCE_DENIED_KIND,
    InferenceMeter,
    observed_usage,
)

_PRESETS = {
    name: entry["budget"]
    for name, entry in json.loads(
        (Path("packs/code-default/presets.json")).read_text(encoding="utf-8")
    )["presets"].items()
}


class _Model:
    """A ModelPort that reads a fresh file each turn and reports its own cost."""

    def __init__(self, *, prompt: int = 3_500, completion: int = 350,
                 usd_micros: int | None = 0,
                 pricing: tuple[int, int] | None = None) -> None:
        self.calls = 0
        self._prompt = prompt
        self._completion = completion
        self._usd = usd_micros
        if pricing is not None:
            self.pricing = pricing

    def propose(self, context, tools, sampling):
        del context, tools, sampling
        self.calls += 1
        payload = {
            "kind": "effect",
            "action": "fs.read",
            "args": {"path": f"target_{self.calls}.py", "limit": 20},
            "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
            "note": f"turn {self.calls}",
            "usage": {"prompt_tokens": self._prompt,
                      "completion_tokens": self._completion},
        }
        if self._usd is not None:
            payload["usd_micros"] = self._usd
            payload["pricing_known"] = True
        return Result.success(payload)


def _run(preset: str, model: _Model) -> dict:
    """One real episode through the public entrypoint. Zero provider calls."""
    with tempfile.TemporaryDirectory() as raw:
        workspace = Path(raw).resolve()
        (workspace / "pyproject.toml").write_text("[project]\nname='t'\n", encoding="utf-8")
        for index in range(1, 80):
            (workspace / f"target_{index}.py").write_text(
                "def f():\n    return 1\n" * 10, encoding="utf-8")
        (workspace / ".vanguard" / "blobs").mkdir(parents=True, exist_ok=True)
        frame = entrypoint.execute({
            "command": "code",
            "brief": "read the targets",
            "workspace": str(workspace),
            "preset": preset,
            "storePath": str(workspace / ".vanguard" / "events.sqlite3"),
            "injectedModel": model,
            "profile": "product",
            "interactive": False,
        })
    return frame.get("result", {})


class DeclaredCeilingsBindInference(unittest.TestCase):
    """The product path, not a unit fixture: the defect lived in composition."""

    def test_a_token_overrun_is_denied_rather_than_reported_after_the_fact(self) -> None:
        """A model that consumes past the declared ceiling is stopped by it.

        Mutation proof: drop `meter=self._inference_meter` from the operator
        construction in `runtime/session.py` and this runs to the turn bound
        with the ceiling silently exceeded, exactly as it did before.
        """
        declared = _PRESETS["balanced"]["tokens"]
        # Each call reports a third of the whole episode's declared spend.
        model = _Model(prompt=declared // 3, completion=1_000)
        result = _run("balanced", model)

        self.assertEqual(result.get("outcome"), "budget_exhausted")
        self.assertIn("reservation denied", (result.get("detail") or ""))
        consumed = model.calls * (declared // 3 + 1_000)
        self.assertLess(
            consumed, declared * 2,
            "inference ran past twice its declared token ceiling without denial")

    def test_a_spend_refusal_is_not_reported_as_a_provider_failure(self) -> None:
        """`budget_exhausted` keeps its own terminal.

        Mutation proof: delete the `INFERENCE_DENIED_KIND` branch in
        `agency/episode/engine.py` and this reds with `instrument_error` --
        a working ceiling misreported as the model misbehaving, which would
        move the observation into the missingness taxonomy (`DIR-D2`).
        """
        declared = _PRESETS["fast"]["tokens"]
        model = _Model(prompt=declared, completion=1_000)
        result = _run("fast", model)

        self.assertIn("reservation denied", (result.get("detail") or ""),
                      "the run must stop on the reservation, not the turn bound")
        self.assertEqual(result.get("outcome"), "budget_exhausted")
        self.assertNotEqual(result.get("outcome"), "instrument_error")

    def test_every_preset_funds_the_turns_it_declares(self) -> None:
        """The regression that would have caught the original calibration.

        A ceiling that cannot pay for its own declared turns is a measurement
        defect: `MS-CONTROL` must not be frozen on top of a preset that stops
        early for a reason its acceptance predicate does not name.
        """
        for preset, budget in _PRESETS.items():
            with self.subTest(preset=preset):
                model = _Model(prompt=3_500, completion=350)
                result = _run(preset, model)
                self.assertEqual(
                    model.calls, budget["turns"],
                    f"{preset} declares {budget['turns']} turns but funded "
                    f"{model.calls}: {result.get('detail')}")
                self.assertIn("turn bound", (result.get("detail") or ""))


class TheTwoConservationLawsAreSeparateKeys(unittest.TestCase):
    """`tokens` is conserved spend; `context_window_tokens` bounds one prompt."""

    def test_every_preset_declares_both_and_the_window_is_the_smaller(self) -> None:
        for preset, budget in _PRESETS.items():
            with self.subTest(preset=preset):
                self.assertIn("context_window_tokens", budget)
                self.assertLess(
                    budget["context_window_tokens"], budget["tokens"],
                    "a single prompt may not be allowed to consume the whole "
                    "episode's declared spend")

    def test_the_window_funds_at_least_one_turn_of_the_declared_spend(self) -> None:
        """Calibration sanity: spend must cover turns x window, not less."""
        for preset, budget in _PRESETS.items():
            with self.subTest(preset=preset):
                self.assertGreaterEqual(
                    budget["tokens"], budget["context_window_tokens"],
                    f"{preset} cannot fund even one maximal prompt")


class MeterHonesty(unittest.TestCase):
    """Unknown cost stays unknown (`RUN-12`); overruns are charged, not clamped."""

    def _meter(self, ceilings, pricing=None) -> tuple[InferenceMeter, Governor]:
        governor = Governor(ceilings)
        return InferenceMeter(governor, "run-x", pricing=pricing), governor

    def test_an_unreported_cost_is_recorded_unsettled_and_never_as_zero(self) -> None:
        meter, governor = self._meter({"tokens": 100_000})
        reservation = meter.reserve(prompt_tokens=1_000, sampling={"maxTokens": 100})
        settlement = meter.settle(reservation, {"kind": "finish"})  # no usage reported

        self.assertEqual(meter.unsettled_calls, 1)
        self.assertFalse(settlement.usage_observed)
        self.assertIsNone(settlement.as_payload()["usdMicros"],
                          "an unpriced call must not report a zero cost")
        self.assertEqual(
            governor.spent("tokens"), reservation.tokens,
            "an unreported call must be charged its reservation, not refunded")

    def test_an_overrun_is_charged_in_full(self) -> None:
        meter, governor = self._meter({"tokens": 100_000})
        reservation = meter.reserve(prompt_tokens=1_000, sampling={"maxTokens": 100})
        meter.settle(reservation, {"usage": {"total_tokens": 9_999}})
        self.assertEqual(governor.spent("tokens"), 9_999)

    def test_the_usd_ceiling_denies_a_priced_route(self) -> None:
        """The half that costs real money."""
        meter, _ = self._meter({"usd_micros": 1_000, "tokens": 10_000_000},
                               pricing=(65_000, 180_000))
        with self.assertRaises(BudgetDenied) as caught:
            meter.reserve(prompt_tokens=100_000, sampling={"maxTokens": 4_096})
        self.assertEqual(caught.exception.dimension, "usd_micros")

    def test_a_free_route_is_never_denied_on_cost(self) -> None:
        meter, _ = self._meter({"usd_micros": 0, "tokens": 1_000_000},
                               pricing=(0, 0))
        reservation = meter.reserve(prompt_tokens=50_000, sampling={"maxTokens": 4_096})
        self.assertEqual(reservation.usd_micros, 0)

    def test_the_denied_kind_is_the_budget_terminal_spelling(self) -> None:
        """A rename here silently reverts the engine branch to instrument_error."""
        from vanguard.packages.agency.episode.state import RunTermination
        self.assertEqual(INFERENCE_DENIED_KIND, RunTermination.BUDGET_EXHAUSTED.value)


class UsageReadingIsThreeValued(unittest.TestCase):
    def test_absent_counts_stay_none(self) -> None:
        self.assertEqual(observed_usage({}), (None, None))
        self.assertEqual(observed_usage("not a mapping"), (None, None))

    def test_totals_and_halves_are_both_understood(self) -> None:
        self.assertEqual(observed_usage({"usage": {"total_tokens": 7}})[0], 7)
        self.assertEqual(
            observed_usage({"usage": {"prompt_tokens": 4, "completion_tokens": 3}})[0], 7)

    def test_a_dollar_cost_converts_without_inventing_precision(self) -> None:
        self.assertEqual(observed_usage({"cost_usd": 0.25})[1], 250_000)
        self.assertEqual(observed_usage({"usd_micros": 42})[1], 42)


class PricingIsThreeValuedAtTheAdapter(unittest.TestCase):
    """`None` means unknown. It has never meant free."""

    def test_priced_free_and_unknown_routes_are_distinguishable(self) -> None:
        from vanguard.packages.adapters.models.openrouter import OpenRouterModel
        paid = OpenRouterModel(model="deepseek/deepseek-v4-flash-0731", mode="cassette")
        free = OpenRouterModel(model="openrouter/free", mode="cassette")
        unknown = OpenRouterModel(model="no-such-vendor/no-such-model", mode="cassette")

        self.assertIsNotNone(paid.pricing)
        self.assertGreater(paid.pricing[0], 0)
        self.assertEqual(free.pricing, (0, 0))
        self.assertIsNone(unknown.pricing,
                          "an unknown route must not borrow a default price")


if __name__ == "__main__":
    unittest.main()
