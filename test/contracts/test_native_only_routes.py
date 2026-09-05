"""T-91 native llama.cpp route and environment contract."""

from __future__ import annotations

import unittest
from pathlib import Path

from vanguard.packages.adapters.models.env_loader import (
    LOCAL_INFERENCE_KEYS,
    load_local_inference_env,
)
from vanguard.packages.adapters.models.factory import ModelResolutionError, create_model
from vanguard.packages.adapters.models.llama_cpp import LlamaCppModel
from vanguard.packages.adapters.models.routing import ModelRoutingError, resolve_route


ROOT = Path(__file__).resolve().parents[2]


class TestNativeOnlyRoutes(unittest.TestCase):
    def test_supported_pack_has_no_retired_provider_or_placeholder(self) -> None:
        harness = (ROOT / "packs/code-default/harness.yaml").read_text(encoding="utf-8")
        self.assertNotIn("ollama", harness.lower())
        self.assertNotIn("$FRONTIER", harness)

    def test_local_environment_surface_is_exact(self) -> None:
        self.assertEqual(
            LOCAL_INFERENCE_KEYS,
            frozenset({"VANGUARD_LLAMA_ENDPOINT", "VANGUARD_LLAMA_MODEL"}),
        )
        loaded = load_local_inference_env({
            "VANGUARD_LLAMA_ENDPOINT": " http://127.0.0.1:8080/v1/chat/completions ",
            "VANGUARD_LLAMA_MODEL": " local.gguf ",
            "VANGUARD_OLLAMA_ENDPOINT": "http://legacy.invalid",
        })
        self.assertEqual(set(loaded), LOCAL_INFERENCE_KEYS)
        self.assertEqual(loaded["VANGUARD_LLAMA_MODEL"], "local.gguf")

    def test_canonical_llama_cpp_and_optional_local_alias_still_resolve(self) -> None:
        canonical = create_model("llama_cpp:qwen.gguf")
        local = create_model("local")
        self.assertIsInstance(canonical, LlamaCppModel)
        self.assertIsInstance(local, LlamaCppModel)

    def test_retired_provider_alias_fails_with_typed_factory_error(self) -> None:
        with self.assertRaises(ModelResolutionError) as caught:
            create_model("ollama:qwen2.5")
        self.assertEqual(caught.exception.kind, "RETIRED_PROVIDER_ALIAS")

        with self.assertRaises(ModelResolutionError) as caught_mapping:
            create_model({"provider": "ollama", "model": "qwen2.5"})
        self.assertEqual(caught_mapping.exception.kind, "RETIRED_PROVIDER_ALIAS")

    def test_retired_provider_alias_fails_with_typed_routing_error(self) -> None:
        with self.assertRaises(ModelRoutingError) as caught:
            resolve_route("ollama:qwen2.5")
        self.assertEqual(caught.exception.kind, "RETIRED_PROVIDER_ALIAS")


if __name__ == "__main__":
    unittest.main()
