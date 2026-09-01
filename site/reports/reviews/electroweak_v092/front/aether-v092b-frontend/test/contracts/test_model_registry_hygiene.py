"""Contract tests for model registry centralization and fail-closed policy."""

import unittest
from pathlib import Path
import json

from vanguard.packages.adapters.models.config import (
    load_model_registry,
    get_default_model,
    get_default_paid_model,
    get_allowed_models,
    resolve_model,
    ModelPolicyError,
    ModelRegistryError,
)


class TestModelRegistryHygiene(unittest.TestCase):
    def test_registry_loads_successfully(self):
        reg = load_model_registry()
        self.assertIn("default_model", reg)
        self.assertIn("default_paid_model", reg)
        self.assertIn("active_tiers", reg)
        self.assertIn("tiers", reg)

    def test_default_models_are_in_allowed_tiers(self):
        allowed = get_allowed_models()
        self.assertIn(get_default_model(), allowed)
        self.assertIn(get_default_paid_model(), allowed)

    def test_resolve_model_accepts_valid_aliases_and_models(self):
        default_paid = get_default_paid_model()
        self.assertEqual(resolve_model("paid"), default_paid)
        self.assertEqual(resolve_model(default_paid), default_paid)

    def test_resolve_model_fails_closed_on_unauthorized_models(self):
        with self.assertRaises(ModelPolicyError):
            resolve_model("unauthorized-model-xyz")

        with self.assertRaises(ModelPolicyError):
            resolve_model("gpt-4o-mini")

        with self.assertRaises(ModelPolicyError):
            resolve_model("claude-3-5-sonnet")


if __name__ == "__main__":
    unittest.main()
