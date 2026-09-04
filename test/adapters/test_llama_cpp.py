"""llama.cpp (llama-server) ModelPort contract tests."""

from __future__ import annotations

import json
import unittest

from vanguard.packages.adapters.models.llama_cpp import LlamaCppModel


TOOLS = ({"name": "read", "verb": "fs.read"},)
CONTEXT = {"messages": [{"role": "user", "content": "inspect"}]}


class LlamaCppModelContract(unittest.TestCase):
    def test_tool_call_uses_openai_format(self) -> None:
        payload = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call_1",
                                "type": "function",
                                "function": {
                                    "name": "read",
                                    "arguments": json.dumps({"path": "x.py"}),
                                },
                            }
                        ],
                    }
                }
            ],
            "usage": {"prompt_tokens": 4, "completion_tokens": 2, "total_tokens": 6},
        }
        model = LlamaCppModel(
            model="local-model",
            transport=lambda *_: (200, json.dumps(payload).encode()),
        )
        result = model.propose(CONTEXT, TOOLS, {})
        self.assertTrue(result.ok)
        self.assertEqual(result.value["action"], "fs.read")

    def test_malformed_response_is_instrument_error(self) -> None:
        model = LlamaCppModel(
            model="local-model",
            transport=lambda *_: (200, b"{bad"),
        )
        result = model.propose(CONTEXT, TOOLS, {})
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "instrument_error")

    def test_http_failure_is_retryable(self) -> None:
        model = LlamaCppModel(
            model="local-model",
            transport=lambda *_: (503, b""),
        )
        result = model.propose(CONTEXT, TOOLS, {})
        self.assertFalse(result.ok)
        self.assertTrue(result.error.retryable)

    def test_local_model_provider_is_llama_cpp(self) -> None:
        model = LlamaCppModel()
        self.assertEqual(model.provider, "llama_cpp")
        self.assertEqual(model.model, "local-model")


if __name__ == "__main__":
    unittest.main()
