from __future__ import annotations

import unittest
from vanguard.packages.runtime.model_selection import (
    MODEL_PORTS,
    ModelUnavailable,
    inspect_model_providers,
    select_model,
)


class TestModelSelection(unittest.TestCase):
    def test_mock_and_fake_selection(self) -> None:
        mock_sel = select_model("mock", tape=[{"kind": "finish"}])
        self.assertEqual(mock_sel.port, "mock")
        self.assertIsNotNone(mock_sel.model)

        fake_sel = select_model("fake", tape=[{"kind": "finish"}])
        self.assertEqual(fake_sel.port, "fake")
        self.assertIsNotNone(fake_sel.model)

    def test_unknown_port_fails_closed(self) -> None:
        with self.assertRaises(ModelUnavailable):
            select_model("nonexistent_provider_xyz")

    def test_openrouter_without_key_fails_closed(self) -> None:
        with self.assertRaises(ModelUnavailable) as ctx:
            select_model("openrouter", env={})
        self.assertIn("OPENROUTER_API_KEY", str(ctx.exception))

    def test_inspect_model_providers_safe_redacted(self) -> None:
        providers = inspect_model_providers(env={"OPENROUTER_API_KEY": "sk-secret-key-12345"})
        self.assertTrue(any(p["port"] == "openrouter" and p["hasCredentials"] is True for p in providers))
        # Ensure secret key is nowhere in the inspect output
        as_str = str(providers)
        self.assertNotIn("sk-secret-key-12345", as_str)
