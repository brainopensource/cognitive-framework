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

    def test_native_chat_options_include_num_ctx(self) -> None:
        captured: dict[str, object] = {}

        def transport(endpoint: str, body: bytes) -> tuple[int, bytes]:
            captured["endpoint"] = endpoint
            captured["body"] = json.loads(body.decode("utf-8"))
            payload = {
                "model": "qwen2.5-coder:7b",
                "message": {"content": "", "tool_calls": []},
            }
            return 200, json.dumps(payload).encode()

        model = OllamaModel(
            model="qwen2.5-coder:7b",
            endpoint="http://127.0.0.1:11434/api/chat",
            transport=transport,
        )
        model.propose(CONTEXT, TOOLS, {"maxTokens": 2048})
        self.assertEqual(captured["endpoint"], "http://127.0.0.1:11434/api/chat")
        options = captured["body"]["options"]
        self.assertEqual(options["num_ctx"], 4096)
        self.assertEqual(options["num_predict"], 2048)


if __name__ == "__main__":
    unittest.main()
