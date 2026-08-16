"""Ollama ModelPort contract tests."""

from __future__ import annotations

import json
import unittest

from vanguard.packages.adapters.models.ollama import OllamaModel


TOOLS = ({"name": "read", "verb": "fs.read"},)
CONTEXT = {"messages": [{"role": "user", "content": "inspect"}]}


class OllamaModelContract(unittest.TestCase):
    def test_tool_call_uses_canonical_translator(self) -> None:
        payload = {
            "model": "llama3.2:3b",
            "message": {"content": "", "tool_calls": [{"function": {"name": "read", "arguments": {"path": "x.py"}}}]},
            "prompt_eval_count": 4,
            "eval_count": 2,
        }
        model = OllamaModel(model="llama3.2:3b", transport=lambda *_: (200, json.dumps(payload).encode()))
        result = model.propose(CONTEXT, TOOLS, {})
        self.assertTrue(result.ok)
        self.assertEqual(result.value["action"], "fs.read")

    def test_malformed_response_is_instrument_error(self) -> None:
        model = OllamaModel(model="llama3.2:3b", transport=lambda *_: (200, b"{bad"))
        result = model.propose(CONTEXT, TOOLS, {})
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "instrument_error")

    def test_http_failure_does_not_fallback(self) -> None:
        model = OllamaModel(model="llama3.2:3b", transport=lambda *_: (503, b""))
        result = model.propose(CONTEXT, TOOLS, {})
        self.assertFalse(result.ok)
        self.assertTrue(result.error.retryable)


if __name__ == "__main__":
    unittest.main()
