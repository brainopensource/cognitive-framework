"""Tests for OpenRouter mid-stream SSE abort reproduction and resolution (T-70a / HAR-01)."""

from __future__ import annotations

import unittest
from vanguard.packages.adapters.models.openrouter import OpenRouterModel


class TestOpenRouterStreamAbort(unittest.TestCase):
    def test_midstream_sse_abort_is_retryable_instrument_error(self) -> None:
        """A truncated SSE stream after at least one delta must yield retryable=True."""
        # Chunk 1: a valid delta arrives
        chunk1 = b'data: {"choices":[{"index":0,"delta":{"content":"Thinking..."}}]}\n\n'
        # Chunk 2: truncated SSE chunk arrives without finish_reason or [DONE]
        chunk2 = b'data: {"choices":[{"index":0,"delta":'  # Truncated mid-stream!

        def abort_stream_transport(url, headers, body):
            return 200, {"content-type": "text/event-stream"}, iter([chunk1, chunk2])

        model = OpenRouterModel(
            stream_transport=abort_stream_transport,
            stream=True,
            api_key_ref="DUMMY_KEY",
            environ={"DUMMY_KEY": "dummy-token"},
            max_retries=0,
        )
        # Force 0 retries in _complete so we observe the returned error directly
        model._EMPTY_PROPOSAL_RETRIES = 0

        context = {"messages": [{"role": "user", "content": "hello"}]}
        tools = ()
        sampling = {}

        result = model.propose(context, tools, sampling)

        self.assertFalse(result.ok, "Aborted stream must fail")
        self.assertEqual(result.error.kind, "instrument_error")
        self.assertEqual(
            result.error.message,
            "provider streaming response was malformed, truncated, or empty",
        )
        # This assertion verifies that the error is marked retryable=True
        self.assertTrue(
            result.error.retryable,
            "Mid-stream abort must be retryable for bounded protocol recovery",
        )


if __name__ == "__main__":
    unittest.main()
