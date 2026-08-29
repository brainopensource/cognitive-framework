"""Contract test for EVO-09: Unified Model Provider Factory.

Owning contract: EVO-09, GTS-13C §7.1, ADR-0047.
Invariants:
- Canonical aliases (free, fast, smart, local) resolve strictly through models_registry.json.
- Cassette replay / recorder wrapping works transparently via create_model.
- Unknown provider schemes and unregistered identifiers fail closed with ModelResolutionError.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.models.cassette import Cassette, CassettePlayer, CassetteRecorder
from vanguard.packages.adapters.models.factory import ModelResolutionError, create_model
from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.models.ollama import OllamaModel
from vanguard.packages.adapters.models.openrouter import OpenRouterModel


class TestEvo09ModelFactory(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_alias_resolutions(self) -> None:
        """Verify standard aliases resolve to valid ModelPort instances."""
        # free alias
        m_free = create_model("free")
        self.assertIsInstance(m_free, OpenRouterModel)
        self.assertEqual(m_free._model, "openrouter/free")

        # fast alias
        m_fast = create_model("fast")
        self.assertIsInstance(m_fast, OpenRouterModel)
        self.assertEqual(m_fast._model, "deepseek/deepseek-v4-flash-0731")

        # smart alias
        m_smart = create_model("smart")
        self.assertIsInstance(m_smart, OpenRouterModel)
        self.assertEqual(m_smart._model, "deepseek/deepseek-v4-flash-0731")

        # local alias
        m_local = create_model("local")
        self.assertIsInstance(m_local, OllamaModel)
        self.assertEqual(m_local.model, "deepseek-r1")

    def test_explicit_provider_schemes(self) -> None:
        """Verify scheme-prefixed model specifiers resolve properly."""
        # ollama:<model>
        m_ollama = create_model("ollama:llama3.1")
        self.assertIsInstance(m_ollama, OllamaModel)
        self.assertEqual(m_ollama.model, "llama3.1")

        # openrouter:<model> must be registered in an enabled tier
        m_openrouter = create_model("openrouter:deepseek/deepseek-v4-flash-0731")
        self.assertIsInstance(m_openrouter, OpenRouterModel)
        self.assertEqual(m_openrouter._model, "deepseek/deepseek-v4-flash-0731")

        # fake / mock
        proposals = [{"kind": "finish", "note": "test"}]
        m_fake = create_model("fake", fake_proposals=proposals)
        self.assertIsInstance(m_fake, FakeModel)

    def test_mapping_model_spec(self) -> None:
        """Verify dictionary/mapping model specifiers resolve correctly."""
        m_dict_fake = create_model({"provider": "fake", "proposals": [{"kind": "finish"}]})
        self.assertIsInstance(m_dict_fake, FakeModel)

        m_dict_ollama = create_model({"provider": "ollama", "model": "qwen2.5-coder"})
        self.assertIsInstance(m_dict_ollama, OllamaModel)
        self.assertEqual(m_dict_ollama.model, "qwen2.5-coder")

        m_dict_openrouter = create_model({"provider": "openrouter", "model": "openrouter/free"})
        self.assertIsInstance(m_dict_openrouter, OpenRouterModel)

    def test_cassette_playback_and_record(self) -> None:
        """Verify cassette path resolution, playback, and recorder wrapping."""
        cassette_file = self.tmp_path / "test.cassette.json"
        
        # Create a valid cassette JSON
        cas = Cassette()
        cas.add_record(
            context={"messages": [{"role": "user", "content": "hello"}]},
            tools=[],
            sampling={},
            proposal={"text": "world"},
        )
        cassette_file.write_text(cas.to_json(), encoding="utf-8")

        # Replay via cassette_path argument
        player1 = create_model("openrouter/free", cassette_path=cassette_file, record=False)
        self.assertIsInstance(player1, CassettePlayer)

        # Replay via cassette:<path> spec
        player2 = create_model(f"cassette:{cassette_file}")
        self.assertIsInstance(player2, CassettePlayer)

        # Recording wrapping
        out_cassette = self.tmp_path / "out.cassette.json"
        recorder = create_model("fake", cassette_path=out_cassette, record=True)
        self.assertIsInstance(recorder, CassetteRecorder)
        self.assertIsInstance(recorder.delegate, FakeModel)

    def test_fail_closed_on_invalid_scheme_or_unknown_model(self) -> None:
        """Verify unknown schemes and nonexistent models fail closed with ModelResolutionError."""
        with self.assertRaises(ModelResolutionError):
            create_model("unknown_provider:model_xyz")
        with self.assertRaises(ValueError):
            create_model("openrouter:unapproved/vendor-model")

        with self.assertRaises(ModelResolutionError):
            create_model("totally_unregistered_and_unknown_model_12345")

        with self.assertRaises(ModelResolutionError):
            create_model("")

        with self.assertRaises(ModelResolutionError):
            create_model(f"cassette:{self.tmp_path}/nonexistent.json")


if __name__ == "__main__":
    unittest.main()
