"""Tests for llama MCP server fail-closed completions and retry bounds (T-88 / BRG-01)."""

from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

from tools.llama_cpp import mcp_server


class TestLlamaMcpFailClosed(unittest.TestCase):
    def setUp(self) -> None:
        self.server = mcp_server.LlamaMCPServer()

    def test_empty_content_yields_typed_failure_empty_completion(self) -> None:
        """Proves empty content cannot return success and yields EMPTY_COMPLETION."""
        empty_resp_data = {
            "choices": [
                {
                    "message": {"role": "assistant", "content": ""},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 0},
        }

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(empty_resp_data).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen:
            res = self.server.handle_tool_call("llama_chat", {"prompt": "hello"})
            self.assertTrue(res.get("isError"), "Empty completion must return isError=True")
            self.assertEqual(res.get("error_code"), "EMPTY_COMPLETION")
            self.assertIn("EMPTY_COMPLETION", res["content"][0]["text"])
            # Retry bound is 1: total attempts = 1 initial + 1 retry = 2 calls
            self.assertEqual(mock_urlopen.call_count, 2)

    def test_length_finish_without_content_yields_max_tokens_without_content(self) -> None:
        """Proves finish_reason=length with empty content yields MAX_TOKENS_WITHOUT_CONTENT."""
        length_resp_data = {
            "choices": [
                {
                    "message": {"role": "assistant", "content": "   "},
                    "finish_reason": "length",
                }
            ],
            "usage": {"prompt_tokens": 2048, "completion_tokens": 0},
        }

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(length_resp_data).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen:
            res = self.server.handle_tool_call("llama_chat", {"prompt": "generate code"})
            self.assertTrue(res.get("isError"))
            self.assertEqual(res.get("error_code"), "MAX_TOKENS_WITHOUT_CONTENT")
            self.assertIn("MAX_TOKENS_WITHOUT_CONTENT", res["content"][0]["text"])
            # Verified retry bound is at most 1 (total attempts = 2)
            self.assertEqual(mock_urlopen.call_count, 2)

    def test_bounded_retry_succeeds_on_second_attempt(self) -> None:
        """Proves that a single bounded retry succeeds if second attempt returns content."""
        empty_resp = MagicMock()
        empty_resp.read.return_value = json.dumps({
            "choices": [{"message": {"role": "assistant", "content": ""}, "finish_reason": "stop"}],
        }).encode("utf-8")
        empty_resp.__enter__.return_value = empty_resp

        success_resp = MagicMock()
        success_resp.read.return_value = json.dumps({
            "choices": [{"message": {"role": "assistant", "content": "Valid response on retry"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 5},
        }).encode("utf-8")
        success_resp.__enter__.return_value = success_resp

        with patch("urllib.request.urlopen", side_effect=[empty_resp, success_resp]) as mock_urlopen:
            res = self.server.handle_tool_call("llama_chat", {"prompt": "retry test"})
            self.assertFalse(res.get("isError", False), "Should succeed on second attempt")
            self.assertEqual(res["content"][0]["text"], "Valid response on retry")
            self.assertEqual(res["telemetry"]["attempts"], 2)
            self.assertEqual(mock_urlopen.call_count, 2)

    def test_status_hides_chat_template_by_default(self) -> None:
        """Raw chat template must be hidden unless explicit opt-in is provided."""
        mock_health = {
            "online": True,
            "props": {
                "default_generation_settings": {
                    "model": "test-model.gguf",
                    "chat_template": "{% for message in messages %}{{ message.content }}{% endfor %}",
                },
                "chat_template": "raw-jinja-template",
            },
            "health": {"status": "ok"},
        }
        with patch("tools.llama_cpp.mcp_server.check_server_health", return_value=mock_health):
            # Default call: template hidden
            res = self.server.handle_tool_call("llama_status", {})
            status_text = res["content"][0]["text"]
            self.assertNotIn("raw-jinja-template", status_text)
            self.assertNotIn("{% for message", status_text)

            # Explicit opt-in call: template included
            res_opt = self.server.handle_tool_call("llama_status", {"include_template": True})
            status_opt_text = res_opt["content"][0]["text"]
            self.assertIn("raw-jinja-template", status_opt_text)


if __name__ == "__main__":
    unittest.main()
