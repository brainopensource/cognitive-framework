"""Tests for ModelRouter protocol and routing_policy resolution (S8-B-03)."""

from __future__ import annotations

import unittest

from vanguard.packages.adapters.models.routing import (
    FallbackModelRouter,
    SingleModelRouter,
    TierEscalationRouter,
    resolve_model_router,
    resolve_route,
)


class TestModelRouter(unittest.TestCase):
    def test_single_model_router_resolves_direct(self) -> None:
        policy = {"kind": "single-model", "model": "deepseek/deepseek-v4-flash-0731"}
        router = resolve_model_router(policy)
        self.assertIsInstance(router, SingleModelRouter)
        route = router.route()
        self.assertEqual(route.resolved_model, "deepseek/deepseek-v4-flash-0731")
        self.assertTrue(route.pricing_known)

    def test_tier_escalation_router_escalates_by_attempt(self) -> None:
        policy = {
            "kind": "tier-escalation",
            "tiers": ["openrouter/free", "deepseek/deepseek-v4-flash", "deepseek/deepseek-v4-flash-0731"],
        }
        router = resolve_model_router(policy)
        self.assertIsInstance(router, TierEscalationRouter)

        route_0 = router.route(attempt=0)
        self.assertEqual(route_0.resolved_model, "openrouter/free")

        route_1 = router.route(attempt=1)
        self.assertEqual(route_1.resolved_model, "deepseek/deepseek-v4-flash")

        route_2 = router.route(attempt=2)
        self.assertEqual(route_2.resolved_model, "deepseek/deepseek-v4-flash-0731")

    def test_fallback_model_router(self) -> None:
        policy = {
            "kind": "fallback",
            "primary": "deepseek/deepseek-v4-flash-0731",
            "fallback": "openrouter/free",
        }
        router = resolve_model_router(policy)
        self.assertIsInstance(router, FallbackModelRouter)

        route_primary = router.route(attempt=0)
        self.assertEqual(route_primary.resolved_model, "deepseek/deepseek-v4-flash-0731")

        route_fallback = router.route(attempt=1)
        self.assertEqual(route_fallback.resolved_model, "openrouter/free")

    def test_changing_routing_policy_changes_selected_model(self) -> None:
        """Changing routing_policy in pack changes the model selected (S8-B-03 DoD)."""
        policy_cheap = {"kind": "single-model", "model": "cohere/north-mini-code:free"}
        policy_frontier = {"kind": "single-model", "model": "openai/gpt-5.6-luna"}

        router_cheap = resolve_model_router(policy_cheap)
        router_frontier = resolve_model_router(policy_frontier)

        self.assertNotEqual(router_cheap.route().resolved_model, router_frontier.route().resolved_model)
        self.assertEqual(router_cheap.route().resolved_model, "cohere/north-mini-code:free")
        self.assertEqual(router_frontier.route().resolved_model, "openai/gpt-5.6-luna")


if __name__ == "__main__":
    unittest.main()
