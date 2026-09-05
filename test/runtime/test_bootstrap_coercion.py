from __future__ import annotations

import unittest
from unittest.mock import patch
from vanguard.packages.runtime.bootstrap import _resolve_model_adapter
from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.models.openrouter import OpenRouterModel


class TestBootstrapCoercion(unittest.TestCase):
    def test_non_string_model_returned_as_is(self) -> None:
        fake = FakeModel([{"kind": "finish"}])
        res = _resolve_model_adapter(fake, "product")
        self.assertIs(res, fake)

    def test_string_port_resolves(self) -> None:
        res = _resolve_model_adapter("fake", "product")
        self.assertIsInstance(res, FakeModel)

    def test_empty_string_resolves_to_fake_under_local(self) -> None:
        res = _resolve_model_adapter("", "local")
        self.assertIsInstance(res, FakeModel)

    def test_none_model_resolves_to_fake_under_ci(self) -> None:
        res = _resolve_model_adapter(None, "ci")
        self.assertIsInstance(res, FakeModel)

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "sk-test-key"})
    def test_openrouter_catalog_string_coerces_to_openrouter_model(self) -> None:
        res = _resolve_model_adapter("openrouter/free", "product")
        self.assertIsInstance(res, OpenRouterModel)
