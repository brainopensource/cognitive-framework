"""REQ-PORT-006 / TEST-PORT-006 — OpenRouter ModelPort adapter.

Cassette tests must pass without network. The optional live call is skipped
when `OPENROUTER_API_KEY` is unset. Trust-spine sources must not import this
adapter (`REQ-TRUST-001`).
"""

from __future__ import annotations

import ast
import json
import os
import socket
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from vanguard.packages.adapters.models.cassette import Cassette
from vanguard.packages.adapters.models.openrouter import (
    OpenRouterModel,
    OpenRouterModelAdapter,
    calculate_cost,
    calculate_cost_micros,
    estimate_context_tokens,
    estimate_proposal_tokens,
    estimate_tokens,
)
from vanguard.packages.ports.event_store import Result


CONTEXT = {"blocks": [{"label": "L5", "content": "say hello"}]}
TOOLS = [{"name": "read", "schema": {"type": "object"}}]
SAMPLING = {"temperature": 0.0, "maxTokens": 8}
PROPOSAL = {"text": "hello from cassette", "toolCalls": []}
SECRET = "sk-test-secret-do-not-leak"


def _boom_transport(url: str, headers: dict[str, str], body: bytes) -> tuple[int, bytes]:
    raise AssertionError(f"network forbidden: {url}")


def _status_transport(status: int, payload: bytes):
    def transport(url: str, headers: dict[str, str], body: bytes) -> tuple[int, bytes]:
        del url, headers
        encoded = body.decode("utf-8", "replace")
        assert SECRET not in encoded
        return status, payload

    return transport


def _trust_openrouter_imports() -> list[str]:
    root = Path("test/trust")
    if not root.exists():
        return []
    offenders: list[str] = []
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            specs: list[str] = []
            if isinstance(node, ast.Import):
                specs.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    specs.append(node.module)
                specs.extend(alias.name for alias in node.names)
            for spec in specs:
                lowered = spec.lower()
                if "openrouter" in lowered:
                    offenders.append(f"{path.as_posix()}:{node.lineno}: {spec}")
    return offenders


class OpenRouterModelContract(unittest.TestCase):
    def test_cassette_replay_does_not_touch_the_network(self) -> None:
        cassette = Cassette()
        cassette.add_record(CONTEXT, TOOLS, SAMPLING, PROPOSAL)
        port = OpenRouterModel(cassette=cassette, mode="replay", transport=_boom_transport)
        with patch.object(socket, "socket", side_effect=AssertionError("no network")):
            result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertTrue(result.ok)
        self.assertEqual(result.value, PROPOSAL)

    def test_http_rate_limit_is_instrument_error_without_secret(self) -> None:
        port = OpenRouterModel(
            api_key_ref="OPENROUTER_API_KEY",
            transport=_status_transport(429, b'{"error":{"message":"rate limit"}}'),
            environ={"OPENROUTER_API_KEY": SECRET},
            max_retries=1,
            initial_delay=0.0,
            jitter=False,
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertFalse(result.ok)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error.kind, "instrument_error")
        self.assertTrue(result.error.retryable)
        self.assertNotIn(SECRET, result.error.message)
        dumped = Result.fail(
            result.error.kind, result.error.message, result.error.retryable
        )
        self.assertNotIn(SECRET, str(dumped))

    def test_adapter_holds_a_secret_reference_not_the_value(self) -> None:
        port = OpenRouterModel(
            api_key_ref="OPENROUTER_API_KEY",
            transport=_boom_transport,
            environ={"OPENROUTER_API_KEY": SECRET},
        )
        self.assertEqual(port.api_key_ref, "OPENROUTER_API_KEY")
        self.assertFalse(hasattr(port, "api_key"))
        self.assertNotIn(SECRET, vars(port).values())

    def test_trust_spine_sources_do_not_import_openrouter(self) -> None:
        self.assertEqual(_trust_openrouter_imports(), [])

    def test_openrouter_model_adapter_alias(self) -> None:
        self.assertIs(OpenRouterModelAdapter, OpenRouterModel)

    def test_429_rate_limit_triggers_exponential_backoff_and_recovers(self) -> None:
        calls = []
        sleep_durations = []

        def flaky_transport(url: str, headers: dict[str, str], body: bytes) -> tuple[int, bytes]:
            calls.append(len(calls) + 1)
            if len(calls) < 3:
                return 429, b'{"error":{"message":"rate limited"}}'
            return 200, json.dumps({
                "choices": [{"message": {"role": "assistant", "content": "recovered!"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            }).encode("utf-8")

        port = OpenRouterModel(
            api_key_ref="OPENROUTER_API_KEY",
            transport=flaky_transport,
            environ={"OPENROUTER_API_KEY": SECRET},
            max_retries=3,
            initial_delay=0.1,
            jitter=False,
            sleeper=sleep_durations.append,
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertTrue(result.ok)
        self.assertEqual(result.value["text"], "recovered!")
        self.assertEqual(len(calls), 3)
        self.assertEqual(len(sleep_durations), 2)
        self.assertAlmostEqual(sleep_durations[0], 0.1)
        self.assertAlmostEqual(sleep_durations[1], 0.2)

    def test_503_service_unavailable_triggers_backoff_and_recovers(self) -> None:
        calls = []
        sleep_durations = []

        def overloaded_transport(url: str, headers: dict[str, str], body: bytes) -> tuple[int, bytes]:
            calls.append(1)
            if len(calls) == 1:
                return 503, b'{"error":{"message":"Service Unavailable"}}'
            return 200, json.dumps({
                "choices": [{"message": {"role": "assistant", "content": "service restored"}}],
            }).encode("utf-8")

        port = OpenRouterModel(
            api_key_ref="OPENROUTER_API_KEY",
            transport=overloaded_transport,
            environ={"OPENROUTER_API_KEY": SECRET},
            max_retries=2,
            initial_delay=0.05,
            jitter=False,
            sleeper=sleep_durations.append,
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertTrue(result.ok)
        self.assertEqual(result.value["text"], "service restored")
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(sleep_durations), 1)
        self.assertAlmostEqual(sleep_durations[0], 0.05)

    def test_429_retry_after_header_is_respected(self) -> None:
        sleep_durations = []
        calls = 0

        def retry_after_transport(url: str, headers: dict[str, str], body: bytes):
            nonlocal calls
            calls += 1
            if calls == 1:
                return 429, {"Retry-After": "1.5"}, b'{"error":{"message":"slow down"}}'
            return 200, {}, json.dumps({
                "choices": [{"message": {"role": "assistant", "content": "ok"}}],
            }).encode("utf-8")

        port = OpenRouterModel(
            api_key_ref="OPENROUTER_API_KEY",
            transport=retry_after_transport,
            environ={"OPENROUTER_API_KEY": SECRET},
            max_retries=2,
            initial_delay=0.01,
            jitter=False,
            sleeper=sleep_durations.append,
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertTrue(result.ok)
        self.assertEqual(len(sleep_durations), 1)
        self.assertAlmostEqual(sleep_durations[0], 1.5)

    def test_max_retries_exhaustion_returns_instrument_error(self) -> None:
        calls = 0
        sleep_durations = []

        def failing_transport(url: str, headers: dict[str, str], body: bytes) -> tuple[int, bytes]:
            nonlocal calls
            calls += 1
            return 429, b'{"error":{"message":"still rate limited"}}'

        port = OpenRouterModel(
            api_key_ref="OPENROUTER_API_KEY",
            transport=failing_transport,
            environ={"OPENROUTER_API_KEY": SECRET},
            max_retries=2,
            initial_delay=0.01,
            jitter=False,
            sleeper=sleep_durations.append,
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "instrument_error")
        self.assertTrue(result.error.retryable)
        self.assertEqual(calls, 3)  # 1 initial + 2 retries
        self.assertEqual(len(sleep_durations), 2)
        self.assertNotIn(SECRET, result.error.message)

    def test_auth_failure_401_fails_fast_without_retries(self) -> None:
        calls = 0
        sleep_durations = []

        def unauth_transport(url: str, headers: dict[str, str], body: bytes) -> tuple[int, bytes]:
            nonlocal calls
            calls += 1
            return 401, b'{"error":{"message":"invalid api key"}}'

        port = OpenRouterModel(
            api_key_ref="OPENROUTER_API_KEY",
            transport=unauth_transport,
            environ={"OPENROUTER_API_KEY": SECRET},
            max_retries=3,
            sleeper=sleep_durations.append,
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "instrument_error")
        self.assertFalse(result.error.retryable)
        self.assertEqual(calls, 1)
        self.assertEqual(len(sleep_durations), 0)

    def test_transient_network_exception_retries_and_recovers(self) -> None:
        calls = 0
        sleep_durations = []

        def flaky_net_transport(url: str, headers: dict[str, str], body: bytes) -> tuple[int, bytes]:
            nonlocal calls
            calls += 1
            if calls == 1:
                raise urllib.error.URLError("Connection reset by peer")
            return 200, json.dumps({
                "choices": [{"message": {"role": "assistant", "content": "connection succeeded"}}],
            }).encode("utf-8")

        port = OpenRouterModel(
            api_key_ref="OPENROUTER_API_KEY",
            transport=flaky_net_transport,
            environ={"OPENROUTER_API_KEY": SECRET},
            max_retries=2,
            initial_delay=0.01,
            jitter=False,
            sleeper=sleep_durations.append,
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertTrue(result.ok)
        self.assertEqual(result.value["text"], "connection succeeded")
        self.assertEqual(calls, 2)
        self.assertEqual(len(sleep_durations), 1)

    def test_cassette_recording_preserves_usage_and_cost(self) -> None:
        cassette = Cassette()
        payload = json.dumps({
            "choices": [{"message": {"role": "assistant", "content": "Recorded response"}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        }).encode("utf-8")

        port = OpenRouterModel(
            cassette=cassette,
            mode="record",
            transport=_status_transport(200, payload),
            environ={"OPENROUTER_API_KEY": SECRET},
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertTrue(result.ok)
        self.assertEqual(len(cassette.records), 1)
        record = cassette.records[0]
        self.assertEqual(record.proposal["text"], "Recorded response")
        self.assertIn("usage", record.proposal)
        self.assertEqual(record.proposal["usage"]["prompt_tokens"], 100)
        self.assertEqual(record.proposal["usage"]["completion_tokens"], 50)
        self.assertIn("cost_usd", record.proposal)

    def test_priced_accounting_with_provider_usage_and_caching(self) -> None:
        payload = json.dumps({
            "choices": [{"message": {"role": "assistant", "content": "I calculated the gradient."}}],
            "usage": {
                "prompt_tokens": 1000,
                "completion_tokens": 200,
                "total_tokens": 1200,
                "prompt_tokens_details": {"cached_tokens": 400},
            },
        }).encode("utf-8")

        port = OpenRouterModel(
            model="openai/gpt-4o-mini",
            api_key_ref="OPENROUTER_API_KEY",
            transport=_status_transport(200, payload),
            environ={"OPENROUTER_API_KEY": SECRET},
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertTrue(result.ok)
        self.assertIn("usage", result.value)
        usage = result.value["usage"]
        self.assertEqual(usage["prompt_tokens"], 1000)
        self.assertEqual(usage["completion_tokens"], 200)
        self.assertEqual(usage["cached_tokens"], 400)
        self.assertEqual(usage["total_tokens"], 1200)

        # Cost check:
        # gpt-4o-mini pricing: prompt $0.15/1M, completion $0.60/1M, cached $0.075/1M
        # uncached prompt = 600 * 0.15 / 1M = $0.000090
        # cached prompt = 400 * 0.075 / 1M = $0.000030
        # completion = 200 * 0.60 / 1M = $0.000120
        # total = $0.000240
        expected_cost = 0.00024
        self.assertAlmostEqual(usage["cost_usd"], expected_cost, places=6)
        self.assertAlmostEqual(result.value["cost_usd"], expected_cost, places=6)

    def test_fallback_token_estimation_when_provider_omits_usage(self) -> None:
        payload = json.dumps({
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "Hello, here is a detailed response without usage.",
                    "tool_calls": [{
                        "id": "call_1",
                        "type": "function",
                        "function": {"name": "read", "arguments": "{\"path\":\"foo.py\"}"},
                    }],
                }
            }],
        }).encode("utf-8")

        port = OpenRouterModel(
            model="openai/gpt-4o-mini",
            api_key_ref="OPENROUTER_API_KEY",
            transport=_status_transport(200, payload),
            environ={"OPENROUTER_API_KEY": SECRET},
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertTrue(result.ok)
        self.assertIn("usage", result.value)
        usage = result.value["usage"]
        self.assertGreater(usage["prompt_tokens"], 0)
        self.assertGreater(usage["completion_tokens"], 0)
        self.assertEqual(usage["cached_tokens"], 0)
        self.assertEqual(usage["total_tokens"], usage["prompt_tokens"] + usage["completion_tokens"])
        self.assertGreater(usage["cost_usd"], 0.0)

    def test_custom_pricing_table(self) -> None:
        custom_pricing = {
            "custom/fast-model": (1.0, 2.0, 0.5),  # $1/1M prompt, $2/1M completion, $0.5/1M cached
        }
        cost = calculate_cost(
            "custom/fast-model",
            prompt_tokens=1000,
            completion_tokens=500,
            cached_tokens=200,
            pricing_table=custom_pricing,
        )
        # uncached prompt = 800 * 1.0 / 1M = 0.0008
        # cached prompt = 200 * 0.5 / 1M = 0.0001
        # completion = 500 * 2.0 / 1M = 0.0010
        # total = 0.0019
        self.assertAlmostEqual(cost, 0.0019, places=6)

    def test_token_estimation_helpers(self) -> None:
        self.assertEqual(estimate_tokens(""), 0)
        self.assertGreater(estimate_tokens("hello world"), 0)
        ctx_tokens = estimate_context_tokens(CONTEXT, TOOLS)
        self.assertGreater(ctx_tokens, 0)
        prop_tokens = estimate_proposal_tokens({"text": "done", "toolCalls": []})
        self.assertGreater(prop_tokens, 0)

    def test_streaming_sse_deltas_assembled_correctly(self) -> None:
        sse_payload = (
            b"data: {\"choices\":[{\"index\":0,\"delta\":{\"role\":\"assistant\",\"content\":\"Hello \"}}]}\n\n"
            b"data: {\"choices\":[{\"index\":0,\"delta\":{\"content\":\"world!\"}}]}\n\n"
            b"data: {\"choices\":[],\"usage\":{\"prompt_tokens\":12,\"completion_tokens\":4,\"total_tokens\":16}}\n\n"
            b"data: [DONE]\n\n"
        )
        port = OpenRouterModel(
            api_key_ref="OPENROUTER_API_KEY",
            transport=_status_transport(200, sse_payload),
            environ={"OPENROUTER_API_KEY": SECRET},
            stream=True,
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertTrue(result.ok)
        self.assertEqual(result.value["text"], "Hello world!")
        self.assertIn("usage", result.value)
        self.assertEqual(result.value["usage"]["prompt_tokens"], 12)
        self.assertEqual(result.value["usage"]["completion_tokens"], 4)
        self.assertIn("usd_micros", result.value["usage"])
        self.assertTrue(result.value["usage"]["pricing_known"])

    def test_streaming_tool_calls_assembled_across_chunks(self) -> None:
        sse_payload = (
            b"data: {\"choices\":[{\"index\":0,\"delta\":{\"tool_calls\":[{\"index\":0,\"id\":\"call_1\",\"function\":{\"name\":\"fs.read\",\"arguments\":\"{\\\"path\\\":\"}}]}}]}\n\n"
            b"data: {\"choices\":[{\"index\":0,\"delta\":{\"tool_calls\":[{\"index\":0,\"function\":{\"arguments\":\"\\\"main.py\\\"}\"}}]}}]}\n\n"
            b"data: {\"choices\":[],\"usage\":{\"prompt_tokens\":20,\"completion_tokens\":10,\"total_tokens\":30}}\n\n"
            b"data: [DONE]\n\n"
        )
        port = OpenRouterModel(
            api_key_ref="OPENROUTER_API_KEY",
            transport=_status_transport(200, sse_payload),
            environ={"OPENROUTER_API_KEY": SECRET},
            stream=True,
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertTrue(result.ok)
        self.assertEqual(len(result.value["toolCalls"]), 1)
        tool_call = result.value["toolCalls"][0]
        self.assertEqual(tool_call["name"], "fs.read")
        self.assertEqual(tool_call["arguments"], {"path": "main.py"})

    def test_live_stream_transport_is_incremental_and_measures_first_delta(self) -> None:
        event = (
            "data: "
            + json.dumps(
                {"choices": [{"index": 0, "delta": {"content": "hé"}}]},
                ensure_ascii=False,
                separators=(",", ":"),
            )
            + "\n\n"
        ).encode("utf-8")
        split = event.index(b"\xc3") + 1  # split the UTF-8 encoding of "é"
        chunks = (event[:split], event[split:], b"data: [DONE]\n\n")
        calls: list[bytes] = []
        ticks = iter((100.0, 100.125))

        def stream_transport(url: str, headers: dict[str, str], body: bytes):
            del url, headers
            calls.append(body)
            return 200, {"content-type": "text/event-stream"}, iter(chunks)

        port = OpenRouterModel(
            api_key_ref="OPENROUTER_API_KEY",
            stream_transport=stream_transport,
            environ={"OPENROUTER_API_KEY": SECRET},
            monotonic=lambda: next(ticks),
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)

        self.assertTrue(result.ok)
        self.assertEqual(result.value["text"], "hé")
        self.assertEqual(result.value["usage"]["ttft_millis"], 125)
        self.assertEqual(len(calls), 1)
        self.assertTrue(json.loads(calls[0])["stream"])

    def test_truncated_sse_stream_fails_closed(self) -> None:
        truncated = b"data: {\"choices\":[{\"index\":0,\"delta\":{\"content\":\"partial\"}}]}\n\n"
        port = OpenRouterModel(
            api_key_ref="OPENROUTER_API_KEY",
            transport=_status_transport(200, truncated),
            environ={"OPENROUTER_API_KEY": SECRET},
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "instrument_error")
        self.assertIn("truncated", result.error.message.lower())

    def test_malformed_fragmented_tool_arguments_fail_closed(self) -> None:
        sse_payload = (
            b"data: {\"choices\":[{\"index\":0,\"delta\":{\"tool_calls\":[{\"index\":0,\"id\":\"call_1\",\"function\":{\"name\":\"fs.read\",\"arguments\":\"{bad\"}}]}}]}\n\n"
            b"data: [DONE]\n\n"
        )
        port = OpenRouterModel(
            api_key_ref="OPENROUTER_API_KEY",
            transport=_status_transport(200, sse_payload),
            environ={"OPENROUTER_API_KEY": SECRET},
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "instrument_error")

    def test_non_streaming_malformed_tool_json_fails_closed(self) -> None:
        payload = json.dumps({
            "choices": [{"message": {
                "content": None,
                "tool_calls": [{
                    "id": "call_bad",
                    "function": {"name": "fs.read", "arguments": "{bad"},
                }],
            }}],
        }).encode()
        port = OpenRouterModel(
            transport=lambda *_: (200, payload),
            environ={"OPENROUTER_API_KEY": SECRET},
            stream=False,
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "instrument_error")

    def test_unknown_model_pricing_marked_explicitly(self) -> None:
        payload = json.dumps({
            "choices": [{"message": {"role": "assistant", "content": "custom model reply"}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        }).encode("utf-8")
        port = OpenRouterModel(
            model="custom/unknown-model-xyz",
            api_key_ref="OPENROUTER_API_KEY",
            transport=_status_transport(200, payload),
            environ={"OPENROUTER_API_KEY": SECRET},
            stream=False,
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertTrue(result.ok)
        self.assertFalse(result.value["usage"]["pricing_known"])
        self.assertFalse(result.value["pricing_known"])

    def test_unknown_pricing_never_invents_a_cost(self) -> None:
        cost, known = calculate_cost_micros(
            "provider/model-without-pricing",
            prompt_tokens=100,
            completion_tokens=50,
        )
        self.assertEqual(cost, 0)
        self.assertFalse(known)
        self.assertGreaterEqual(result.value["usage"]["usd_micros"], 0)

    def test_malformed_sse_stream_fails_closed(self) -> None:
        malformed_sse = b"data: {corrupted json line\n\ndata: [DONE]\n\n"
        port = OpenRouterModel(
            api_key_ref="OPENROUTER_API_KEY",
            transport=_status_transport(200, malformed_sse),
            environ={"OPENROUTER_API_KEY": SECRET},
            stream=True,
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "instrument_error")
        self.assertIn("malformed", result.error.message.lower())

    @unittest.skipUnless(
        os.environ.get("OPENROUTER_API_KEY"),
        "live OpenRouter skipped: key unset",
    )
    def test_optional_live_chat_completion(self) -> None:
        port = OpenRouterModel()
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertTrue(
            result.ok or (result.error is not None and result.error.kind == "instrument_error")
        )
        if result.ok:
            self.assertIn("usage", result.value)
            self.assertIn("cost_usd", result.value)
            self.assertIn("usd_micros", result.value)
        if result.error is not None:
            self.assertNotIn(os.environ["OPENROUTER_API_KEY"], result.error.message)


if __name__ == "__main__":
    unittest.main()
