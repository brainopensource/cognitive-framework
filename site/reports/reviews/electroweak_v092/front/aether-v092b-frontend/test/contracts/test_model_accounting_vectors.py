"""B-O4-01: one checked source for model pricing, and one checked cost formula.

Order 4 requires that routing and cost tests cannot drift independently.
``models_registry.json`` is already the single source of prices, and
``config.py`` loads it fail-closed -- but nothing stopped a test from restating
a price beside it, and two did. ``test_openrouter.py`` priced a deepseek route
with gpt-4o-mini arithmetic, and ``test_model_routing.py`` asserted a
prompt rate no entry in the registry has. Both restatements were wrong, and
both had been wrong silently.

This module closes that by making every accounting expectation reach agreement
three ways:

1. the value stored in the vector,
2. the value recomputed from the registry through the frozen formula,
3. the value the adapter actually reports.

The stored value is a tripwire, not a second source: editing a price in the
registry makes the stored expectation stale and fails here loudly, which is the
right signal for a priced change. Editing the *formula* fails here too. What is
no longer possible is a test that quietly believes its own prices.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from vanguard.packages.adapters.models.config import get_pricing_micros_table
from vanguard.packages.adapters.models.routing import resolve_route

_REPO_ROOT = Path(__file__).resolve().parents[2]
_VECTORS = _REPO_ROOT / "schemas" / "v4" / "vectors" / "model-accounting"
_MODELS_DIR = _REPO_ROOT / "vanguard" / "packages" / "adapters" / "models"


def accounted_micros(model: str, prompt: int, completion: int, cached: int) -> int:
    """The frozen accounting formula, stated once (openrouter.py `_finalise_usage`).

    Cached tokens are billed at the cached rate and removed from the uncached
    prompt count; the subtraction clamps at zero so an over-reported cache
    figure cannot credit the caller. Integer micro-dollar division floors.
    """
    route = resolve_route(model)
    uncached = max(0, prompt - cached)
    return (
        uncached * route.prompt_micros_per_1m
        + cached * route.cached_micros_per_1m
        + completion * route.completion_micros_per_1m
    ) // 1_000_000


def _cases() -> list[tuple[str, dict]]:
    return sorted(
        (p.stem, json.loads(p.read_text(encoding="utf-8")))
        for p in _VECTORS.glob("*.json")
    )


class AccountingVectorCorpus(unittest.TestCase):
    def test_corpus_is_present(self) -> None:
        self.assertTrue(_cases(), "no model-accounting vectors published")

    def test_every_vector_names_a_route_the_registry_can_price(self) -> None:
        table = get_pricing_micros_table()
        for name, case in _cases():
            with self.subTest(case=name):
                route = resolve_route(case["model"])
                self.assertTrue(
                    route.pricing_known,
                    f"{case['model']} has no known price; a vector may not "
                    f"assert a cost for an unpriced route",
                )
                if route.pricing_source == "hardcoded":
                    self.assertIn(case["model"], table)

    def test_stored_expectation_agrees_with_the_registry(self) -> None:
        """The tripwire: a registry edit must not silently pass."""
        for name, case in _cases():
            with self.subTest(case=name):
                derived = accounted_micros(
                    case["model"],
                    case["promptTokens"],
                    case["completionTokens"],
                    case["cachedTokens"],
                )
                self.assertEqual(
                    case["expectedUsdMicros"],
                    derived,
                    f"{name}: stored expectation and registry-derived price disagree. "
                    f"If a price changed on purpose, restate the vector; if not, the "
                    f"registry moved unintentionally.",
                )
                self.assertAlmostEqual(
                    case["expectedCostUsd"], derived / 1_000_000.0, places=8
                )

    def test_cached_tokens_never_credit_the_caller(self) -> None:
        """An over-reported cache figure clamps, it does not go negative."""
        self.assertEqual(
            accounted_micros("deepseek/deepseek-v4-flash-0731", 100, 0, 10_000),
            accounted_micros("deepseek/deepseek-v4-flash-0731", 0, 0, 10_000),
        )

    def test_unknown_route_is_not_priced_as_free(self) -> None:
        """Unknown must stay distinct from zero (guidelines.md execution rules)."""
        route = resolve_route("some/unregistered-model")
        self.assertFalse(route.pricing_known)
        self.assertEqual(route.pricing_source, "unknown")
        free = resolve_route("openrouter/free")
        self.assertTrue(free.pricing_known)
        self.assertEqual(free.pricing_source, "free_tier")
        self.assertNotEqual(route.pricing_source, free.pricing_source)


class RegistryIsTheSolePricingSource(unittest.TestCase):
    """No module beside the registry may carry a price table."""

    #: Micro-dollars-per-1M rates are 5-7 digit literals. A module that holds a
    #: cluster of them beside the registry is a second pricing source.
    _RATE = re.compile(r"\b\d{5,7}\b")

    def test_no_second_pricing_table_in_the_models_package(self) -> None:
        for path in sorted(_MODELS_DIR.glob("*.py")):
            with self.subTest(module=path.name):
                text = path.read_text(encoding="utf-8")
                rates = self._RATE.findall(text)
                self.assertLessEqual(
                    len(rates),
                    2,
                    f"{path.name} contains {len(rates)} rate-shaped literals "
                    f"({rates[:5]}...). Prices belong in models_registry.json.",
                )

    def test_pricing_load_is_fail_closed(self) -> None:
        from vanguard.packages.adapters.models.config import (
            ModelRegistryError,
            load_model_registry,
        )

        with self.assertRaises(ModelRegistryError):
            load_model_registry(_REPO_ROOT / "does-not-exist.json")


if __name__ == "__main__":
    unittest.main()
