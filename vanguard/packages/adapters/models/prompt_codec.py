"""Provider-request serialization, counting, reservation and cache negotiation.

T-105 / NT-C03 / NT-C06. The number that matters is the size of the bytes a
provider actually receives, not the size of any intermediate envelope. The
:class:`ContextCompiler` packet (T-104, owned by the agency layer) is the
*input* to this codec and is consumed unchanged -- this module neither
re-selects nor re-compacts context. What it adds is the last mile:

* serialize the final provider request exactly once, and count *that*;
* include native tool-schema overhead in the count, because the schemas are
  part of the request the provider bills and truncates;
* enforce ``usable = window - output - safety - recovery`` against that count,
  fail-closed;
* keep the cacheable prefix byte-stable when only dynamic state changes;
* attach cache controls only on routes documented to accept them;
* report the cache usage a provider actually returned, or explicit
  missingness.

Deliberately absent: any cache-hit-rate or provider-performance claim. A
stable prefix is a statement about bytes. Whether a provider served those
bytes from its cache is only ever *observed* here, never asserted, and every
reservation below assumes the worst case that nothing was cached.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

__all__ = [
    "CacheObservation",
    "PromptBudget",
    "PromptBudgetExceeded",
    "PromptCodec",
    "SerializedRequest",
    "count_serialized_tokens",
    "supports_cache_control",
]

# NT-C03 permits an exact route tokenizer or a documented conservative bound.
# Average natural-language density (for example, three or four bytes/token) is
# not an upper bound for punctuation-heavy code, generated data, or arbitrary
# UTF-8. OpenAI-compatible production tokenizers are byte-level: every emitted
# token consumes at least one serialized byte. Counting one token per byte is
# therefore the fail-closed ceiling when the adapter has no exact tokenizer.
# An adapter with the provider's tokenizer injects ``counter`` and avoids this
# deliberately pessimistic fallback.
CONSERVATIVE_BYTES_PER_TOKEN = 1

# Anthropic-family routes are the ones documented to accept explicit
# ``cache_control`` breakpoints on the OpenAI-compatible surface. Everything
# else is treated as not supporting them, so the serialized request stays
# byte-identical to what the route accepts today. Adding a family here is a
# statement that its wire API documents the control, nothing more.
_CACHE_CONTROL_PREFIXES = ("anthropic/",)

# Providers that accept the control still bound how many breakpoints one
# request may carry.
MAX_CACHE_BREAKPOINTS = 4


class PromptBudgetExceeded(ValueError):
    """The final serialized request does not fit the usable input window."""


def supports_cache_control(model: str) -> bool:
    """Whether this route documents explicit prompt-cache breakpoints."""
    normalised = (model or "").strip().lower()
    return normalised.startswith(_CACHE_CONTROL_PREFIXES)


def count_serialized_tokens(payload: bytes) -> int:
    """Conservative token bound over the *final* serialized request bytes."""
    if not payload:
        return 0
    return -(-len(payload) // CONSERVATIVE_BYTES_PER_TOKEN)


@dataclass(frozen=True, slots=True)
class PromptBudget:
    """NT-C03 window reservation, stated in provider tokens.

    ``usable`` never widens because a prefix was cached: a cache miss must
    leave semantics and limits untouched, so every bound here is the
    worst-case uncached one.
    """

    window: int
    output: int = 0
    safety: int = 0
    recovery: int = 0

    def __post_init__(self) -> None:
        for name in ("window", "output", "safety", "recovery"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.window <= 0:
            raise ValueError("window must be positive")
        if self.usable <= 0:
            raise ValueError(
                "no usable input budget: output, safety and recovery "
                "reservations consume the whole window")

    @property
    def usable(self) -> int:
        return self.window - self.output - self.safety - self.recovery


@dataclass(frozen=True, slots=True)
class CacheObservation:
    """What the provider reported about cache reuse -- or that it reported nothing.

    ``cached_tokens is None`` means the provider did not tell us. That is a
    distinct fact from ``0`` (it told us nothing was reused) and the two are
    never collapsed. There is deliberately no hit-rate on this type.
    """

    supported: bool
    cached_tokens: int | None = None
    prompt_tokens: int | None = None
    source: str = "absent"

    @property
    def observed(self) -> bool:
        return self.cached_tokens is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "cacheControlSupported": self.supported,
            "cachedTokens": self.cached_tokens,
            "promptTokens": self.prompt_tokens,
            "cacheReportSource": self.source,
        }


@dataclass(frozen=True, slots=True)
class SerializedRequest:
    """The exact bytes posted, and the accounting taken over those bytes."""

    body: Mapping[str, Any]
    payload: bytes
    prefix_payload: bytes
    input_tokens: int
    tool_schema_tokens: int
    cache_breakpoints: int
    budget: PromptBudget | None = None
    counter_name: str = "conservative_json_bound"
    omissions: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    @property
    def usable(self) -> int | None:
        return None if self.budget is None else self.budget.usable

    @property
    def headroom(self) -> int | None:
        return None if self.budget is None else self.budget.usable - self.input_tokens

    def to_dict(self) -> dict[str, Any]:
        return {
            "inputTokens": self.input_tokens,
            "toolSchemaTokens": self.tool_schema_tokens,
            "payloadBytes": len(self.payload),
            "prefixBytes": len(self.prefix_payload),
            "cacheBreakpoints": self.cache_breakpoints,
            "usableTokens": self.usable,
            "headroomTokens": self.headroom,
            "counter": self.counter_name,
        }


def _dumps(value: Any) -> bytes:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class PromptCodec:
    """Serialize, count, and bound one provider request.

    The codec is the single place a request becomes bytes. Counting anywhere
    upstream of it is an estimate about a different object.
    """

    def __init__(
        self,
        *,
        counter: Callable[[bytes], int] | None = None,
        counter_name: str | None = None,
    ) -> None:
        self._counter = counter or count_serialized_tokens
        self._counter_name = counter_name or (
            "provider_counter" if counter is not None else "conservative_json_bound")

    # -- prefix ---------------------------------------------------------

    @staticmethod
    def prefix_length(context: Any) -> int:
        """How many leading messages form the cacheable prefix.

        The compiled packet marks its own breakpoints (``cacheBreakpoint`` on
        each rendered layer). The prefix is everything up to and including the
        last marked layer. With no packet metadata the prefix is the leading
        system message, which is the only span this codec can honestly claim
        is stable.
        """
        layers = context.get("layers") if isinstance(context, Mapping) else None
        if isinstance(layers, Sequence) and layers:
            last = 0
            for index, layer in enumerate(layers):
                if isinstance(layer, Mapping) and layer.get("cacheBreakpoint"):
                    last = index + 1
            if last:
                return last
        return 1

    # -- serialization --------------------------------------------------

    def serialize(
        self,
        body: Mapping[str, Any],
        *,
        context: Any = None,
        budget: PromptBudget | None = None,
        model: str | None = None,
        cache_controls: bool | None = None,
    ) -> SerializedRequest:
        """Finalize ``body`` into wire bytes and account for them.

        ``budget`` is optional: with no declared window there is nothing to
        enforce, and the codec reports the count rather than inventing a
        limit. With a window, the final count must fit ``usable`` or this
        raises -- the request is never trimmed silently.
        """
        target = str(model or body.get("model") or "")
        negotiate = supports_cache_control(target) if cache_controls is None else bool(cache_controls)

        final = dict(body)
        messages = [dict(item) for item in (final.get("messages") or ())]
        breakpoints = 0
        if negotiate and messages:
            prefix = min(self.prefix_length(context), len(messages), MAX_CACHE_BREAKPOINTS)
            if prefix:
                messages[prefix - 1] = _with_cache_control(messages[prefix - 1])
                breakpoints = 1
        final["messages"] = messages

        payload = _dumps(final)
        input_tokens = int(self._counter(payload))

        tools = final.get("tools") or ()
        tool_schema_tokens = int(self._counter(_dumps(list(tools)))) if tools else 0

        prefix_count = min(self.prefix_length(context), len(messages)) if messages else 0
        # The prefix is what a provider could cache: route identity, the tool
        # schemas that frame every call, and the leading stable messages. It
        # deliberately excludes sampling knobs and dynamic layers.
        prefix_payload = _dumps({
            "model": target,
            "tools": list(tools),
            "messages": messages[:prefix_count],
        })

        request = SerializedRequest(
            body=final,
            payload=payload,
            prefix_payload=prefix_payload,
            input_tokens=input_tokens,
            tool_schema_tokens=tool_schema_tokens,
            cache_breakpoints=breakpoints,
            budget=budget,
            counter_name=self._counter_name,
        )
        if budget is not None and input_tokens > budget.usable:
            raise PromptBudgetExceeded(
                f"CONTEXT_BUDGET_EXCEEDED: final serialized request is "
                f"{input_tokens} tokens (of which {tool_schema_tokens} are tool "
                f"schemas) against usable {budget.usable} "
                f"(window {budget.window} - output {budget.output} - safety "
                f"{budget.safety} - recovery {budget.recovery})"
            )
        return request

    # -- observation ----------------------------------------------------

    @staticmethod
    def observe_cache(raw_usage: Any, *, model: str | None = None) -> CacheObservation:
        """Report the provider's own cache accounting, or its absence.

        Never derives, infers, or averages a hit rate. A provider that says
        nothing yields ``cached_tokens=None``.
        """
        supported = supports_cache_control(model or "")
        if not isinstance(raw_usage, Mapping):
            return CacheObservation(supported=supported)
        prompt_tokens = raw_usage.get("prompt_tokens")
        prompt = int(prompt_tokens) if isinstance(prompt_tokens, int) else None
        details = raw_usage.get("prompt_tokens_details")
        if isinstance(details, Mapping) and isinstance(details.get("cached_tokens"), int):
            return CacheObservation(
                supported=supported,
                cached_tokens=int(details["cached_tokens"]),
                prompt_tokens=prompt,
                source="prompt_tokens_details",
            )
        if isinstance(raw_usage.get("cached_tokens"), int):
            return CacheObservation(
                supported=supported,
                cached_tokens=int(raw_usage["cached_tokens"]),
                prompt_tokens=prompt,
                source="usage",
            )
        return CacheObservation(supported=supported, prompt_tokens=prompt, source="absent")


def _with_cache_control(message: Mapping[str, Any]) -> dict[str, Any]:
    """Mark one message as a cache breakpoint without changing what it says."""
    updated = dict(message)
    content = updated.get("content")
    if isinstance(content, str):
        updated["content"] = [{
            "type": "text",
            "text": content,
            "cache_control": {"type": "ephemeral"},
        }]
    elif isinstance(content, list) and content:
        parts = [dict(part) if isinstance(part, Mapping) else part for part in content]
        if isinstance(parts[-1], dict):
            parts[-1]["cache_control"] = {"type": "ephemeral"}
        updated["content"] = parts
    return updated
