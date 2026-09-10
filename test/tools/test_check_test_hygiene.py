from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.linters.check_test_hygiene import (
    check_test_hygiene,
    detect_unsafe_inherited_state,
    exported_provider_keys,
    main,
)


class TestTestHygiene(unittest.TestCase):
    def test_clean_environment_is_empty(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(exported_provider_keys(), ())

    def test_every_provider_key_is_detected(self) -> None:
        values = {
            "OPENROUTER_API_KEY": "secret-a",
            "DEEPSEEK_API_KEY": "secret-b",
            "OPENAI_API_KEY": "secret-c",
        }
        with patch.dict(os.environ, values, clear=True):
            self.assertEqual(exported_provider_keys(), tuple(values))

    def test_expanded_provider_keys_detected(self) -> None:
        values = {
            "ANTHROPIC_API_KEY": "sk-ant",
            "GEMINI_API_KEY": "sk-gem",
            "MISTRAL_API_KEY": "sk-mis",
        }
        with patch.dict(os.environ, values, clear=True):
            keys = exported_provider_keys()
            for k in values:
                self.assertIn(k, keys)

    def test_generic_pattern_key_detected(self) -> None:
        values = {
            "CUSTOM_VENDOR_API_KEY": "secret-custom",
            "SERVICE_AUTH_TOKEN": "token-123",
        }
        with patch.dict(os.environ, values, clear=True):
            keys = exported_provider_keys()
            for k in values:
                self.assertIn(k, keys)

    def test_unsafe_lam_db_path_detected(self) -> None:
        root = Path(__file__).resolve().parents[2]
        tracked = root / "tools" / "002_LLM_API_MOCK" / "lam.sqlite"
        env = {"LAM_DB_PATH": str(tracked)}
        violations = detect_unsafe_inherited_state(env, root=root)
        self.assertTrue(any("LAM_DB_PATH points directly to tracked repo corpus" in v for v in violations))

    def test_unsafe_workspace_root_detected(self) -> None:
        root = Path(__file__).resolve().parents[2]
        env = {"AETHER_WORKSPACE_ROOT": str(root)}
        violations = detect_unsafe_inherited_state(env, root=root)
        self.assertTrue(any("AETHER_WORKSPACE_ROOT points directly to repository root" in v for v in violations))

    def test_unsafe_tmpdir_in_source_detected(self) -> None:
        root = Path(__file__).resolve().parents[2]
        env = {"TMPDIR": str(root / "vanguard" / "temp")}
        violations = detect_unsafe_inherited_state(env, root=root)
        self.assertTrue(any("TMPDIR points inside repository source tree" in v for v in violations))

    def test_safe_disposable_env_passes(self) -> None:
        root = Path(__file__).resolve().parents[2]
        env = {
            "AETHER_WORKSPACE_ROOT": "/tmp/disposable_workspace",
            "LAM_DB_PATH": "/tmp/disposable_workspace/lam.sqlite",
            "TMPDIR": "/tmp/disposable_workspace/tmp",
        }
        violations = check_test_hygiene(env, root=root)
        self.assertEqual(violations, [])

    def test_main_fails_on_provider_keys(self) -> None:
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "secret"}, clear=True):
            self.assertEqual(main(), 1)

    def test_main_fails_on_unsafe_state(self) -> None:
        root = Path(__file__).resolve().parents[2]
        tracked = root / "tools" / "002_LLM_API_MOCK" / "lam.sqlite"
        with patch.dict(os.environ, {"LAM_DB_PATH": str(tracked)}, clear=True):
            self.assertEqual(main(), 1)

    def test_main_passes_on_clean_env(self) -> None:
        with patch.dict(os.environ, {"AETHER_WORKSPACE_ROOT": "/tmp/safe_ws"}, clear=True):
            self.assertEqual(main(), 0)

