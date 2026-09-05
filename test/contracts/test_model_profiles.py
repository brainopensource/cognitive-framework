"""Contract test for ModelCapabilityProfile resolution and degradation (T-69)."""

from __future__ import annotations

import unittest

from vanguard.packages.domain.models.profile import (
    ModelCapabilityProfile,
    ToolCallStyle,
    profile_for,
)


class TestModelProfiles(unittest.TestCase):
    def test_native_routes_resolve_native_tool_call_style(self) -> None:
        native_routes = [
            "deepseek/deepseek-v4-flash-0731",
            "z-ai/glm-5.3-flash",
            "deepseek/deepseek-v4-flash",
            "deepseek-v4-flash",
            "openrouter:deepseek/deepseek-v4-flash-0731",
        ]
        for route in native_routes:
            profile = profile_for(route)
            self.assertEqual(
                profile.tool_call_style,
                ToolCallStyle.NATIVE,
                f"expected NATIVE for {route}, got {profile.tool_call_style}",
            )

    def test_unknown_and_unverified_routes_not_promoted_to_native(self) -> None:
        unverified_routes = [
            "unknown",
            "z-ai/glm-5.2",
            "google/gemma-4-31b-it:free",
            "minimax/minimax-m3:free",
            "openai/gpt-5.6-luna",
            "deepseek/deepseek-v4-pro",
            "deepseek-v4-pro",
            "google/gemini-3.8-flash",
            "gemini-3.8-flash",
            "custom/unverified-model",
            "ollama:deepseek/deepseek-v4-flash",
            "",
            None,
        ]
        for route in unverified_routes:
            profile = profile_for(route)
            self.assertNotEqual(
                profile.tool_call_style,
                ToolCallStyle.NATIVE,
                f"unverified route {route} should not be promoted to NATIVE",
            )
            self.assertEqual(
                profile.tool_call_style,
                ToolCallStyle.FENCED_JSON,
                f"unverified route {route} should default to FENCED_JSON",
            )

    def test_degraded_chain_preserves_order(self) -> None:
        native_profile = ModelCapabilityProfile(
            "deepseek/deepseek-v4-flash-0731",
            tool_call_style=ToolCallStyle.NATIVE,
            supports_parallel_tool_calls=True,
        )
        step1 = native_profile.degraded()
        self.assertEqual(step1.tool_call_style, ToolCallStyle.JSON_SCHEMA)
        self.assertFalse(step1.supports_parallel_tool_calls)

        step2 = step1.degraded()
        self.assertEqual(step2.tool_call_style, ToolCallStyle.FENCED_JSON)

        step3 = step2.degraded()
        self.assertEqual(step3.tool_call_style, ToolCallStyle.TEXT_GRAMMAR)

        step4 = step3.degraded()
        self.assertEqual(step4.tool_call_style, ToolCallStyle.TEXT_GRAMMAR)


if __name__ == "__main__":
    unittest.main()
