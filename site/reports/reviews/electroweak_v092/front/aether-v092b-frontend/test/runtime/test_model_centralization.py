"""Test suite enforcing centralized model policy and preventing hardcoded model drift."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from vanguard.packages.adapters.models.config import (
    ModelPolicyError,
    get_allowed_models,
    load_model_registry,
    resolve_model,
)
from vanguard.packages.runtime.model_selection import ModelUnavailable, select_model

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "vanguard/packages/adapters/models/models_registry.json"


class TestModelCentralization(unittest.TestCase):
    def test_registry_file_exists_and_is_valid(self) -> None:
        self.assertTrue(REGISTRY_PATH.is_file())
        data = load_model_registry()
        self.assertEqual(data.get("schema"), "aether.model-policy/1")
        self.assertEqual(data.get("default_model"), "deepseek/deepseek-v4-flash-0731")
        self.assertEqual(data.get("default_paid_model"), "deepseek/deepseek-v4-flash-0731")

    def test_unauthorized_models_fail_closed_with_typed_error(self) -> None:
        forbidden = [
            "deepseek/deepseek-chat",
            "deepseek-v3",
            "deepseek/deepseek-v3",
            "openai/gpt-3.5-turbo",
            "claude-2",
            "random/hallucinated-model",
        ]
        for model in forbidden:
            with self.subTest(model=model):
                with self.assertRaises((ModelPolicyError, ModelUnavailable, ValueError)):
                    resolve_model(model)

                with self.assertRaises(ModelUnavailable):
                    select_model(
                        "openrouter",
                        model_name=model,
                        allow_paid=True,
                        env={"OPENROUTER_API_KEY": "sk-dummy"},
                    )

    def test_authorized_tier2_models_resolve_correctly(self) -> None:
        allowed = get_allowed_models()
        self.assertIn("deepseek/deepseek-v4-flash-0731", allowed)
        self.assertIn("z-ai/glm-5.3-flash", allowed)
        self.assertEqual(resolve_model("default"), "deepseek/deepseek-v4-flash-0731")
        self.assertEqual(resolve_model("paid"), "deepseek/deepseek-v4-flash-0731")
        self.assertEqual(resolve_model("fast"), "deepseek/deepseek-v4-flash-0731")

    def test_no_production_code_has_hardcoded_forbidden_models(self) -> None:
        """Scan vanguard/packages/ to ensure zero hardcoded deprecated/unauthorized model strings."""
        packages_dir = ROOT / "vanguard/packages"
        forbidden_patterns = [
            re.compile(r"deepseek/deepseek-chat", re.IGNORECASE),
            re.compile(r"deepseek-v3", re.IGNORECASE),
        ]
        violations = []
        for py_file in packages_dir.rglob("*.py"):
            text = py_file.read_text(encoding="utf-8")
            for pat in forbidden_patterns:
                if pat.search(text):
                    violations.append(f"{py_file.relative_to(ROOT)} matched {pat.pattern}")

        self.assertEqual(violations, [], msg=f"Found hardcoded forbidden model references: {violations}")


if __name__ == "__main__":
    unittest.main()
