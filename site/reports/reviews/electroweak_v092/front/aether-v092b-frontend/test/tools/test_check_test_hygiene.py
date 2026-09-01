from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from tools.linters.check_test_hygiene import exported_provider_keys


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
