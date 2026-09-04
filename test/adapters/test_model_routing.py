import unittest
from vanguard.packages.adapters.models.routing import ModelRoute, resolve_route, preflight_check
from vanguard.packages.ports.event_store import Result

class TestModelRouting(unittest.TestCase):
    def test_openrouter_free_model(self):
        route = resolve_route("openrouter/free")
        self.assertEqual(route.requested_model, "openrouter/free")
        self.assertEqual(route.resolved_model, "openrouter/free")
        self.assertTrue(route.pricing_known)
        self.assertEqual(route.prompt_micros_per_1m, 0)
        self.assertEqual(route.completion_micros_per_1m, 0)
        self.assertEqual(route.cached_micros_per_1m, 0)
        self.assertEqual(route.pricing_source, "free_tier")

    def test_deepseek_v4_flash(self):
        route = resolve_route("deepseek/deepseek-v4-flash")
        self.assertEqual(route.requested_model, "deepseek/deepseek-v4-flash")
        self.assertTrue(route.pricing_known)
        self.assertEqual(route.pricing_source, "hardcoded")

    def test_known_model(self):
        # Prices come from models_registry.json, the single source (Order 4).
        # This test used to assert 150_000 against a registry entry of 140_000:
        # a restated price drifts the moment the registry moves, so the
        # expectation is derived rather than copied.
        from vanguard.packages.adapters.models.config import get_pricing_micros_table

        model = "deepseek/deepseek-v4-flash-0731"
        prompt, completion, cached = get_pricing_micros_table()[model]
        route = resolve_route(model)
        self.assertTrue(route.pricing_known)
        self.assertEqual(route.prompt_micros_per_1m, prompt)
        self.assertEqual(route.completion_micros_per_1m, completion)
        self.assertEqual(route.cached_micros_per_1m, cached)
        self.assertEqual(route.pricing_source, "hardcoded")

    def test_missing_flash_suffix_aliases_or_errors_never_silent_unknown(self) -> None:
        from vanguard.packages.adapters.models.config import ModelPolicyError

        try:
            route = resolve_route("deepseek/deepseek-v4-flash")
        except ModelPolicyError:
            return
        self.assertNotEqual(route.pricing_source, "unknown")
        self.assertEqual(route.resolved_model, "deepseek/deepseek-v4-flash-0731")

    def test_unknown_model(self):
        from vanguard.packages.adapters.models.config import ModelPolicyError

        with self.assertRaises(ModelPolicyError):
            resolve_route("some/unknown-model")
        
    def test_preflight_check(self):
        valid_route = resolve_route("deepseek/deepseek-v4-flash-0731")
        res = preflight_check(valid_route)
        self.assertTrue(res.ok)

        invalid_route = ModelRoute(
            requested_model="",
            resolved_model="",
            pricing_known=False,
            prompt_micros_per_1m=0,
            completion_micros_per_1m=0,
            cached_micros_per_1m=0,
            pricing_source="unknown",
            pricing_as_of="static",
            capabilities=(),
        )
        res_invalid = preflight_check(invalid_route)
        self.assertFalse(res_invalid.ok)
        self.assertEqual(res_invalid.error.kind, "instrument_error")
