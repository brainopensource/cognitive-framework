"""T-105 / NT-C03 / NT-C06: the provider-request serialization boundary.

The object under test is the *final* request -- the bytes an adapter posts,
native tool schemas included. Every claim here is about those bytes and about
what a provider reported back. Nothing here claims, or is permitted to claim,
a cache-hit rate or any provider-performance property: a stable prefix proves
byte identity and nothing more.

The compiled context packet (T-104) is consumed exactly as the agency layer
produces it. These tests never construct a second compiler, and never edit
one.
"""

from __future__ import annotations

import json
import unittest

from vanguard.packages.adapters.models.dialect import ModelIntent, compile_intent
from vanguard.packages.adapters.models.openrouter import OpenRouterModel
from vanguard.packages.adapters.models.prompt_codec import (
    CONSERVATIVE_BYTES_PER_TOKEN,
    MAX_CACHE_BREAKPOINTS,
    CacheObservation,
    PromptBudget,
    PromptBudgetExceeded,
    PromptCodec,
    count_serialized_tokens,
    supports_cache_control,
)
from vanguard.packages.agency.context.compiler import ContextCompiler
from vanguard.packages.agency.context.layers import Fragment

TOOLS = (
    {"name": "fs.read", "description": "read one file",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}},
                    "required": ["path"]}},
    {"name": "patch.apply", "description": "apply one unified diff",
     "parameters": {"type": "object", "properties": {"diff": {"type": "string"}},
                    "required": ["diff"]}},
    {"name": "proc.exec", "description": "run one command",
     "parameters": {"type": "object", "properties": {"argv": {"type": "array"}},
                    "required": ["argv"]}},
)


def _compiler() -> ContextCompiler:
    return ContextCompiler(
        system_core="You are a coding agent. Obey the harness contract.",
        tool_schemas=TOOLS,
        environment="repo=cognitive-framework\nbranch=main",
        token_ceiling=64_000,
    )


def _packet(dialogue_text: str):
    """One compiled packet from B's compiler. Only L5 varies between calls."""
    return _compiler().compile(
        brief="Repair the failing import in src/value.py",
        notes=(Fragment(source="evidence", label="e1", text="pytest fails on import"),),
        dialogue=(Fragment(source="interaction", label="t1", text=dialogue_text,
                           evictable=True),),
    )


def _body(bundle, *, model: str) -> dict:
    """The request an adapter builds from that packet, native tools included."""
    dialect = compile_intent(
        ModelIntent(system="", messages=tuple(bundle["messages"]), tools=TOOLS,
                    sampling={}),
        model,
    )
    body: dict = {
        "model": model,
        "messages": [dict(message) for message in dialect.messages],
        "temperature": 0.2,
        "max_tokens": 4096,
    }
    if dialect.tools:
        body["tools"] = [dict(tool) for tool in dialect.tools]
    return body


class TheCountIsTakenOnTheFinalRequest(unittest.TestCase):
    def test_the_bound_is_conservative_over_the_serialized_bytes(self) -> None:
        payload = b'{"model":"x","messages":[]}'
        self.assertEqual(CONSERVATIVE_BYTES_PER_TOKEN, 1)
        self.assertEqual(count_serialized_tokens(payload), len(payload))
        self.assertEqual(count_serialized_tokens(b""), 0)

    def test_the_fallback_does_not_assume_average_natural_language_density(self) -> None:
        # JSON may contain punctuation-heavy generated data, code, or UTF-8.
        # Without the route's exact tokenizer the only fail-closed byte-level
        # BPE ceiling is one token per serialized byte; bytes/3 is an average,
        # not an upper bound.
        for payload in (b'! ! ! ! !', bytes(range(128)), "🧪漢字".encode("utf-8")):
            with self.subTest(payload=payload):
                self.assertEqual(count_serialized_tokens(payload), len(payload))

    def test_native_tool_schema_overhead_is_counted_not_ignored(self) -> None:
        bundle = _packet("ran pytest -> ImportError").bundle()
        model = "deepseek/deepseek-v4-flash-0731"  # native tool-call style
        with_tools = _body(bundle, model=model)
        self.assertTrue(with_tools.get("tools"), "the fixture must exercise native tools")
        without_tools = {k: v for k, v in with_tools.items() if k != "tools"}

        codec = PromptCodec()
        full = codec.serialize(with_tools, model=model)
        bare = codec.serialize(without_tools, model=model)

        self.assertGreater(full.tool_schema_tokens, 0)
        self.assertEqual(bare.tool_schema_tokens, 0)
        self.assertGreater(full.input_tokens, bare.input_tokens,
                           "tool schemas must be inside the counted request")
        self.assertIn(b'"tools"', full.payload)

    def test_an_intermediate_envelope_is_not_what_gets_counted(self) -> None:
        bundle = _packet("ran pytest -> ImportError").bundle()
        model = "deepseek/deepseek-v4-flash-0731"
        serialized = PromptCodec().serialize(_body(bundle, model=model), model=model)
        # The packet's own pre-flight estimate answers a different question;
        # the request carries framing and schemas the packet never saw.
        self.assertGreater(serialized.input_tokens, int(bundle["tokens"]) // 4)
        self.assertEqual(
            json.loads(serialized.payload.decode("utf-8")), dict(serialized.body))


class ReservationsBindTheFinalWindow(unittest.TestCase):
    def test_usable_is_window_minus_output_safety_and_recovery(self) -> None:
        budget = PromptBudget(window=8000, output=1024, safety=256, recovery=512)
        self.assertEqual(budget.usable, 8000 - 1024 - 256 - 512)

    def test_a_window_consumed_by_reservations_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            PromptBudget(window=1000, output=600, safety=300, recovery=200)
        with self.assertRaises(ValueError):
            PromptBudget(window=0)
        with self.assertRaises(ValueError):
            PromptBudget(window=1000, output=-1)

    def test_a_request_over_usable_fails_closed_and_is_never_trimmed(self) -> None:
        bundle = _packet("x" * 4000).bundle()
        model = "deepseek/deepseek-v4-flash-0731"
        body = _body(bundle, model=model)
        codec = PromptCodec()
        counted = codec.serialize(body, model=model).input_tokens

        fits = PromptBudget(window=counted + 200, output=50, safety=25, recovery=25)
        self.assertEqual(codec.serialize(body, model=model, budget=fits).input_tokens, counted)

        # One token of reservation past the edge must refuse, not silently cut.
        edge = PromptBudget(window=counted + 100, output=50, safety=25, recovery=26)
        with self.assertRaises(PromptBudgetExceeded) as caught:
            codec.serialize(body, model=model, budget=edge)
        self.assertIn("CONTEXT_BUDGET_EXCEEDED", str(caught.exception))

    def test_reservations_use_uncached_bounds_regardless_of_any_cache_report(self) -> None:
        """A cache hit never widens the window it was measured against."""
        budget = PromptBudget(window=8000, output=1024, safety=256, recovery=512)
        uncached = budget.usable
        for report in (None, {}, {"prompt_tokens_details": {"cached_tokens": 7000}}):
            PromptCodec.observe_cache(report, model="anthropic/claude-sonnet-4")
            self.assertEqual(budget.usable, uncached)


class TheCacheablePrefixIsByteStable(unittest.TestCase):
    def test_changed_dynamic_state_preserves_the_prefix_bytes(self) -> None:
        model = "deepseek/deepseek-v4-flash-0731"
        codec = PromptCodec()
        first = _packet("turn one: ran pytest").bundle()
        second = _packet("turn two: read src/value.py and edited it").bundle()

        self.assertNotEqual(first["promptDigest"], second["promptDigest"],
                            "the fixture must actually change dynamic state")

        a = codec.serialize(_body(first, model=model), context=first, model=model)
        b = codec.serialize(_body(second, model=model), context=second, model=model)

        self.assertEqual(a.prefix_payload, b.prefix_payload)
        self.assertNotEqual(a.payload, b.payload)

    def test_a_changed_prefix_changes_the_prefix_bytes(self) -> None:
        """The stability claim is falsifiable, not vacuous."""
        model = "deepseek/deepseek-v4-flash-0731"
        codec = PromptCodec()
        bundle = _packet("turn one").bundle()
        baseline = codec.serialize(_body(bundle, model=model), context=bundle, model=model)

        moved = ContextCompiler(
            system_core="A DIFFERENT system core moves the cached region.",
            tool_schemas=TOOLS,
            environment="repo=cognitive-framework\nbranch=main",
        ).compile(brief="Repair the failing import in src/value.py",
                  dialogue=(Fragment(source="interaction", label="t1",
                                     text="turn one", evictable=True),)).bundle()
        shifted = codec.serialize(_body(moved, model=model), context=moved, model=model)
        self.assertNotEqual(baseline.prefix_payload, shifted.prefix_payload)

    def test_the_prefix_is_read_from_the_packets_own_breakpoints(self) -> None:
        bundle = _packet("turn one").bundle()
        marked = [index for index, layer in enumerate(bundle["layers"])
                  if layer["cacheBreakpoint"]]
        self.assertTrue(marked, "the compiled packet must declare breakpoints")
        self.assertEqual(PromptCodec.prefix_length(bundle), marked[-1] + 1)
        # With no packet metadata the codec claims only the leading message.
        self.assertEqual(PromptCodec.prefix_length({}), 1)


class CacheControlsAreNegotiatedOnlyWhereSupported(unittest.TestCase):
    def test_only_documented_routes_receive_cache_controls(self) -> None:
        self.assertTrue(supports_cache_control("anthropic/claude-sonnet-4"))
        self.assertFalse(supports_cache_control("deepseek/deepseek-v4-flash-0731"))
        self.assertFalse(supports_cache_control(""))

    def test_an_unsupported_route_is_serialized_untouched(self) -> None:
        model = "deepseek/deepseek-v4-flash-0731"
        bundle = _packet("turn one").bundle()
        body = _body(bundle, model=model)
        serialized = PromptCodec().serialize(body, context=bundle, model=model)
        self.assertEqual(serialized.cache_breakpoints, 0)
        self.assertNotIn(b"cache_control", serialized.payload)
        for sent, built in zip(serialized.body["messages"], body["messages"]):
            self.assertEqual(sent["content"], built["content"])

    def test_a_supported_route_is_marked_within_the_provider_bound(self) -> None:
        model = "anthropic/claude-sonnet-4"
        bundle = _packet("turn one").bundle()
        serialized = PromptCodec().serialize(
            _body(bundle, model=model), context=bundle, model=model)
        self.assertGreaterEqual(serialized.cache_breakpoints, 1)
        self.assertLessEqual(serialized.cache_breakpoints, MAX_CACHE_BREAKPOINTS)
        self.assertIn(b"cache_control", serialized.payload)

    def test_marking_a_breakpoint_does_not_change_what_the_message_says(self) -> None:
        model = "anthropic/claude-sonnet-4"
        bundle = _packet("turn one").bundle()
        body = _body(bundle, model=model)
        serialized = PromptCodec().serialize(body, context=bundle, model=model)
        for sent, built in zip(serialized.body["messages"], body["messages"]):
            content = sent["content"]
            if isinstance(content, list):
                self.assertEqual(
                    "".join(part["text"] for part in content), built["content"])
            else:
                self.assertEqual(content, built["content"])


class CacheUsageIsObservedOrExplicitlyMissing(unittest.TestCase):
    def test_a_silent_provider_yields_null_not_zero(self) -> None:
        for report in (None, {}, {"prompt_tokens": 900}):
            observation = PromptCodec.observe_cache(report, model="anthropic/claude-sonnet-4")
            self.assertIsNone(observation.cached_tokens)
            self.assertFalse(observation.observed)
            self.assertEqual(observation.to_dict()["cachedTokens"], None)

    def test_a_reported_zero_is_distinct_from_missingness(self) -> None:
        reported = PromptCodec.observe_cache(
            {"prompt_tokens": 900, "prompt_tokens_details": {"cached_tokens": 0}},
            model="anthropic/claude-sonnet-4")
        self.assertEqual(reported.cached_tokens, 0)
        self.assertTrue(reported.observed)
        self.assertEqual(reported.source, "prompt_tokens_details")

        silent = PromptCodec.observe_cache({"prompt_tokens": 900},
                                           model="anthropic/claude-sonnet-4")
        self.assertIsNone(silent.cached_tokens)
        self.assertNotEqual(reported.to_dict(), silent.to_dict())

    def test_the_flat_usage_spelling_is_read_too(self) -> None:
        observation = PromptCodec.observe_cache(
            {"prompt_tokens": 900, "cached_tokens": 512}, model="anthropic/claude-sonnet-4")
        self.assertEqual(observation.cached_tokens, 512)
        self.assertEqual(observation.prompt_tokens, 900)
        self.assertEqual(observation.source, "usage")

    def test_no_hit_rate_or_performance_claim_is_exposed(self) -> None:
        surface = set(dir(CacheObservation)) | set(dir(PromptCodec))
        for forbidden in ("hit_rate", "hit_ratio", "cache_hit_rate", "speedup", "savings"):
            self.assertNotIn(forbidden, surface)
        text = (CacheObservation.__doc__ or "") + (PromptCodec.__doc__ or "")
        self.assertNotIn("%", text)


class TheAdapterUsesTheCodecAtItsRealBoundary(unittest.TestCase):
    """The codec is not a side calculator: the adapter posts its bytes."""

    def _model(self, transport, **kwargs) -> OpenRouterModel:
        return OpenRouterModel(
            model="deepseek/deepseek-v4-flash-0731",
            transport=transport, stream=False, environ={"OPENROUTER_API_KEY": "k"},
            **kwargs,
        )

    def test_the_posted_payload_is_the_codec_payload(self) -> None:
        seen: list[bytes] = []

        def transport(url, headers, body, timeout=None):  # noqa: ANN001
            seen.append(body)
            return 200, {}, json.dumps({
                "choices": [{"message": {"content": '{"kind":"finish","note":"done"}'}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 2,
                          "prompt_tokens_details": {"cached_tokens": 4}},
            }).encode("utf-8")

        model = self._model(transport)
        bundle = _packet("turn one").bundle()
        result = model.propose(bundle, TOOLS, {})
        self.assertTrue(result.ok, getattr(result, "error", ""))
        self.assertTrue(seen)
        self.assertEqual(seen[-1], model._last_request.payload)
        self.assertGreater(model._last_request.input_tokens, 0)

    def test_the_adapter_reports_observed_cache_usage(self) -> None:
        def transport(url, headers, body, timeout=None):  # noqa: ANN001
            return 200, {}, json.dumps({
                "choices": [{"message": {"content": '{"kind":"finish","note":"done"}'}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 2,
                          "prompt_tokens_details": {"cached_tokens": 4}},
            }).encode("utf-8")

        model = self._model(transport)
        result = model.propose(_packet("turn one").bundle(), TOOLS, {})
        self.assertTrue(result.ok, getattr(result, "error", ""))
        self.assertEqual(result.value["usage"]["cachedTokens"], 4)
        self.assertEqual(result.value["usage"]["cacheReportSource"], "prompt_tokens_details")

    def test_a_silent_provider_reaches_the_proposal_as_null(self) -> None:
        def transport(url, headers, body, timeout=None):  # noqa: ANN001
            return 200, {}, json.dumps({
                "choices": [{"message": {"content": '{"kind":"finish","note":"done"}'}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 2},
            }).encode("utf-8")

        model = self._model(transport)
        result = model.propose(_packet("turn one").bundle(), TOOLS, {})
        self.assertTrue(result.ok, getattr(result, "error", ""))
        self.assertIsNone(result.value["usage"]["cachedTokens"])

    def test_a_cache_miss_preserves_semantics(self) -> None:
        """Miss and hit differ only in reported accounting, not in the answer."""
        proposals = []
        for usage in ({"prompt_tokens": 10, "completion_tokens": 2},
                      {"prompt_tokens": 10, "completion_tokens": 2,
                       "prompt_tokens_details": {"cached_tokens": 9}}):
            def transport(url, headers, body, timeout=None, _u=usage):  # noqa: ANN001
                return 200, {}, json.dumps({
                    "choices": [{"message": {"content": '{"kind":"finish","note":"done"}'}}],
                    "usage": _u,
                }).encode("utf-8")

            result = self._model(transport).propose(_packet("turn one").bundle(), TOOLS, {})
            self.assertTrue(result.ok, getattr(result, "error", ""))
            proposals.append(result.value)

        self.assertEqual(proposals[0]["kind"], proposals[1]["kind"])
        self.assertEqual(proposals[0]["note"], proposals[1]["note"])
        self.assertEqual(proposals[0]["usage"]["serializedInputTokens"],
                         proposals[1]["usage"]["serializedInputTokens"])

    def test_an_oversized_request_fails_closed_at_the_adapter(self) -> None:
        def transport(url, headers, body, timeout=None):  # noqa: ANN001
            raise AssertionError("an over-budget request must never be sent")

        model = self._model(transport, prompt_budget=PromptBudget(
            window=200, output=64, safety=16, recovery=16))
        result = model.propose(_packet("x" * 4000).bundle(), TOOLS, {})
        self.assertFalse(result.ok)
        self.assertIn("CONTEXT_BUDGET_EXCEEDED", str(result.error))


if __name__ == "__main__":
    unittest.main()
