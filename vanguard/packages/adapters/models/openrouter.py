"""OpenAI-compatible OpenRouter adapter for ModelPort.

Owning contract: REQ-PORT-006, REQ-SLICE-001, T2.7, CT-33, ADR-0047.
Never import `slice/` or `spike/`. Secrets are references, never stored values.
Trust spine tests must never import this adapter.
"""

from __future__ import annotations

import json
import os
import random
import time
import urllib.error
import urllib.request
from typing import Any, Callable, Mapping, Sequence

from ...ports.event_store import Result
from ...ports.model import ContextBundle, Proposal, Sampling, ToolSchemas
from .cassette import Cassette, CassettePlayer, CassetteRecorder

__all__ = [
    "OpenRouterModel",
    "OpenRouterModelAdapter",
    "DEFAULT_ENDPOINT",
    "DEFAULT_KEY_REF",
    "DEFAULT_MODEL",
    "MODEL_PRICING",
    "DEFAULT_MODEL_PRICING",
    "calculate_cost",
    "estimate_tokens",
    "estimate_context_tokens",
    "estimate_proposal_tokens",
]

DEFAULT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_KEY_REF = "OPENROUTER_API_KEY"
DEFAULT_MODEL = "openai/gpt-4o-mini"

# Pricing per 1,000,000 tokens (USD): (prompt_per_1m, completion_per_1m, cached_prompt_per_1m)
MODEL_PRICING: dict[str, tuple[float, float, float]] = {
    "openai/gpt-4o-mini": (0.15, 0.60, 0.075),
    "openai/gpt-4o": (2.50, 10.00, 1.25),
    "anthropic/claude-3.5-sonnet": (3.00, 15.00, 0.30),
    "anthropic/claude-3-5-sonnet": (3.00, 15.00, 0.30),
    "anthropic/claude-3.5-haiku": (0.80, 4.00, 0.08),
    "anthropic/claude-3-5-haiku": (0.80, 4.00, 0.08),
    "google/gemini-2.0-flash-001": (0.10, 0.40, 0.025),
    "google/gemini-flash-1.5": (0.075, 0.30, 0.01875),
    "deepseek/deepseek-chat": (0.14, 0.28, 0.014),
    "deepseek/deepseek-r1": (0.55, 2.19, 0.14),
    "meta-llama/llama-3.3-70b-instruct": (0.12, 0.30, 0.03),
}
DEFAULT_MODEL_PRICING: tuple[float, float, float] = (0.15, 0.60, 0.075)

Transport = Callable[
    [str, dict[str, str], bytes],
    tuple[int, bytes] | tuple[int, Mapping[str, str], bytes],
]


def estimate_tokens(text: str) -> int:
    """Estimate token count for a text string using character heuristics (~4 chars/token)."""
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)


def estimate_context_tokens(context: ContextBundle, tools: ToolSchemas) -> int:
    """Estimate prompt tokens from context and tool schemas."""
    total = 0
    messages = _messages(context)
    for msg in messages:
        total += 3  # formatting overhead per message
        content = msg.get("content", "")
        if isinstance(content, str):
            total += estimate_tokens(content)
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, str):
                    total += estimate_tokens(part)
                elif isinstance(part, Mapping):
                    total += estimate_tokens(str(part.get("text", "")))
        role = msg.get("role", "")
        if role:
            total += estimate_tokens(role)
    if tools:
        tool_payload = _tools_payload(tools)
        tool_json = json.dumps(tool_payload, separators=(",", ":"))
        total += estimate_tokens(tool_json)
    return max(1, total)


def estimate_proposal_tokens(proposal: Mapping[str, Any]) -> int:
    """Estimate completion tokens from proposal text and tool calls."""
    text = proposal.get("text", "")
    total = estimate_tokens(text) if isinstance(text, str) and text else 0
    tool_calls = proposal.get("toolCalls") or ()
    for call in tool_calls:
        if isinstance(call, Mapping):
            name = call.get("name", "")
            total += estimate_tokens(name)
            args = call.get("arguments", {})
            if args:
                total += estimate_tokens(json.dumps(args, separators=(",", ":")))
            total += 3
    return max(1, total) if (text or tool_calls) else 0


def calculate_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    cached_tokens: int = 0,
    pricing_table: Mapping[str, tuple[float, float, float]] | None = None,
) -> float:
    """Calculate USD cost for a token count given the model and pricing table."""
    table = pricing_table if pricing_table is not None else MODEL_PRICING
    pricing = table.get(model, DEFAULT_MODEL_PRICING)
    prompt_price, completion_price, cached_price = pricing
    uncached_prompt = max(0, prompt_tokens - cached_tokens)
    cost = (
        (uncached_prompt * prompt_price)
        + (cached_tokens * cached_price)
        + (completion_tokens * completion_price)
    ) / 1_000_000.0
    return round(cost, 8)


def _http_post(
    url: str, headers: dict[str, str], body: bytes, timeout: float = 30.0
) -> tuple[int, dict[str, str], bytes]:
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            resp_headers = {k.lower(): v for k, v in response.headers.items()}
            return int(response.status), resp_headers, response.read()
    except urllib.error.HTTPError as exc:
        resp_headers = (
            {k.lower(): v for k, v in exc.headers.items()}
            if hasattr(exc, "headers") and exc.headers
            else {}
        )
        return int(exc.code), resp_headers, exc.read() or b""


def _redact(text: str, secret: str | None, ref: str) -> str:
    if secret:
        return text.replace(secret, ref)
    return text


def _messages(context: ContextBundle) -> list[dict[str, Any]]:
    if "messages" in context:
        return [dict(item) for item in context["messages"]]
    messages: list[dict[str, Any]] = []
    system = context.get("system")
    if isinstance(system, str) and system:
        messages.append({"role": "system", "content": system})
    for block in context.get("blocks") or ():
        label = block.get("label", "")
        content = block.get("content", "")
        messages.append({"role": "user", "content": f"[{label}] {content}"})
    for item in context.get("history") or ():
        if isinstance(item, str):
            messages.append({"role": "user", "content": item})
        elif isinstance(item, Mapping):
            messages.append(dict(item))
    if not messages:
        messages.append({"role": "user", "content": ""})
    return messages


def _tools_payload(tools: ToolSchemas) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for tool in tools:
        payload.append(
            {
                "type": "function",
                "function": {
                    "name": tool.get("name", ""),
                    "parameters": tool.get("schema") or {"type": "object"},
                },
            }
        )
    return payload


def _parse_proposal(body: Mapping[str, Any]) -> dict[str, Any] | None:
    choices = body.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    first = choices[0]
    if not isinstance(first, Mapping):
        return None
    message = first.get("message")
    if not isinstance(message, Mapping):
        return None
    text = message.get("content")
    if text is None:
        text = ""
    if not isinstance(text, str):
        return None
    tool_calls: list[dict[str, Any]] = []
    raw_calls = message.get("tool_calls") or ()
    for raw in raw_calls:
        if not isinstance(raw, Mapping):
            continue
        function = raw.get("function") if isinstance(raw.get("function"), Mapping) else {}
        arguments: Any = function.get("arguments", {})
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                arguments = {"raw": arguments}
        tool_calls.append(
            {
                "id": str(raw.get("id", "")),
                "name": str(function.get("name", "")),
                "arguments": arguments if isinstance(arguments, Mapping) else {},
            }
        )
    return {"text": text, "toolCalls": tool_calls}


class OpenRouterModel:
    """Live or cassette-backed ModelPort. Trust-spine tests must not construct this."""

    def __init__(
        self,
        *,
        api_key_ref: str = DEFAULT_KEY_REF,
        endpoint: str = DEFAULT_ENDPOINT,
        model: str = DEFAULT_MODEL,
        cassette: Cassette | None = None,
        mode: str = "live",
        transport: Transport | None = None,
        environ: Mapping[str, str] | None = None,
        max_retries: int = 3,
        initial_delay: float = 0.1,
        max_delay: float = 30.0,
        jitter: bool = True,
        sleeper: Callable[[float], None] = time.sleep,
        pricing_table: Mapping[str, tuple[float, float, float]] | None = None,
    ) -> None:
        self.api_key_ref = api_key_ref
        self._endpoint = endpoint
        self._model = model
        self._mode = mode
        self._transport = transport
        self._environ = dict(environ) if environ is not None else None
        self._max_retries = max_retries
        self._initial_delay = initial_delay
        self._max_delay = max_delay
        self._jitter = jitter
        self._sleeper = sleeper
        self._pricing_table = pricing_table
        self._player = (
            CassettePlayer(cassette, match_mode="tape")
            if cassette is not None and mode == "replay"
            else None
        )
        self._recorder = (
            CassetteRecorder(cassette)
            if cassette is not None and mode == "record"
            else None
        )

    def propose(
        self,
        context: ContextBundle,
        tools: ToolSchemas,
        sampling: Sampling,
    ) -> Result[Proposal]:
        if self._player is not None:
            return self._player.propose(context, tools, sampling)
        return self._complete(context, tools, sampling)

    def _lookup_secret(self) -> str | None:
        if self._environ is not None:
            value = self._environ.get(self.api_key_ref)
        else:
            value = os.environ.get(self.api_key_ref)
        return value if value else None

    def _execute_transport(
        self,
        headers: dict[str, str],
        payload: bytes,
        secret: str,
    ) -> tuple[int, Mapping[str, str], bytes] | Result[Proposal]:
        transport = self._transport or _http_post
        attempts = 0
        max_retries = self._max_retries
        retry_statuses = {429, 500, 502, 503, 504}

        while attempts <= max_retries:
            try:
                res = transport(self._endpoint, headers, payload)
                if len(res) == 3:
                    status, resp_headers, raw = res
                else:
                    status, raw = res
                    resp_headers = {}
            except Exception as exc:
                if attempts < max_retries:
                    delay = min(self._initial_delay * (2 ** attempts), self._max_delay)
                    if self._jitter:
                        delay = delay * random.uniform(0.8, 1.2)
                    self._sleeper(delay)
                    attempts += 1
                    continue
                return Result.fail(
                    kind="instrument_error",
                    message=_redact(
                        f"provider request failed after {attempts + 1} attempts: {exc}",
                        secret,
                        self.api_key_ref,
                    ),
                    retryable=True,
                )

            if status in retry_statuses:
                if attempts < max_retries:
                    # Check Retry-After header
                    retry_after_val = None
                    for k, v in resp_headers.items():
                        if k.lower() == "retry-after":
                            retry_after_val = v
                            break
                    delay = None
                    if retry_after_val:
                        try:
                            delay = float(retry_after_val)
                        except (ValueError, TypeError):
                            delay = None
                    if delay is None:
                        delay = min(self._initial_delay * (2 ** attempts), self._max_delay)
                    else:
                        delay = min(delay, self._max_delay)
                    if self._jitter:
                        delay = delay * random.uniform(0.8, 1.2)
                    self._sleeper(delay)
                    attempts += 1
                    continue
                return Result.fail(
                    kind="instrument_error",
                    message=_redact(
                        f"provider returned HTTP {status} after {attempts + 1} attempts",
                        secret,
                        self.api_key_ref,
                    ),
                    retryable=True,
                )

            if status != 200:
                return Result.fail(
                    kind="instrument_error",
                    message=_redact(
                        f"provider returned HTTP {status}",
                        secret,
                        self.api_key_ref,
                    ),
                    retryable=False,
                )

            return int(status), resp_headers, raw

        return Result.fail(
            kind="instrument_error",
            message=f"provider request exhausted {max_retries} retries",
            retryable=True,
        )

    def _complete(
        self,
        context: ContextBundle,
        tools: ToolSchemas,
        sampling: Sampling,
    ) -> Result[Proposal]:
        secret = self._lookup_secret()
        if secret is None:
            return Result.fail(
                kind="instrument_error",
                message=f"secret reference {self.api_key_ref} is unset",
            )
        body_obj: dict[str, Any] = {
            "model": self._model,
            "messages": _messages(context),
            "temperature": sampling.get("temperature", 0.0),
            "max_tokens": sampling.get("maxTokens", 256),
        }
        tool_payload = _tools_payload(tools)
        if tool_payload:
            body_obj["tools"] = tool_payload
        payload = json.dumps(body_obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {secret}",
        }

        transport_result = self._execute_transport(headers, payload, secret)
        if isinstance(transport_result, Result):
            return transport_result
        status, resp_headers, raw = transport_result

        decoded = raw.decode("utf-8", "replace")
        try:
            parsed = json.loads(decoded)
        except json.JSONDecodeError:
            return Result.fail(
                kind="instrument_error",
                message="provider response was not JSON",
            )
        if not isinstance(parsed, Mapping):
            return Result.fail(kind="instrument_error", message="provider response was not an object")
        proposal = _parse_proposal(parsed)
        if proposal is None:
            return Result.fail(
                kind="instrument_error",
                message="provider response did not contain a chat completion",
            )

        # Token usage and priced accounting
        raw_usage = parsed.get("usage") if isinstance(parsed.get("usage"), Mapping) else None
        if raw_usage is not None:
            prompt_tokens = int(raw_usage.get("prompt_tokens") or 0)
            completion_tokens = int(raw_usage.get("completion_tokens") or 0)
            prompt_details = raw_usage.get("prompt_tokens_details")
            if isinstance(prompt_details, Mapping):
                cached_tokens = int(prompt_details.get("cached_tokens") or 0)
            else:
                cached_tokens = int(raw_usage.get("cached_tokens") or 0)
            total_tokens = int(raw_usage.get("total_tokens") or (prompt_tokens + completion_tokens))

            # Fallback if provider passed zero/missing values
            if prompt_tokens <= 0:
                prompt_tokens = estimate_context_tokens(context, tools)
            if completion_tokens <= 0:
                completion_tokens = estimate_proposal_tokens(proposal)
            if total_tokens <= 0:
                total_tokens = prompt_tokens + completion_tokens
        else:
            # Fallback token estimation
            prompt_tokens = estimate_context_tokens(context, tools)
            completion_tokens = estimate_proposal_tokens(proposal)
            cached_tokens = 0
            total_tokens = prompt_tokens + completion_tokens

        cost_usd = calculate_cost(
            self._model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cached_tokens=cached_tokens,
            pricing_table=self._pricing_table,
        )

        proposal["usage"] = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cached_tokens": cached_tokens,
            "total_tokens": total_tokens,
            "cost_usd": cost_usd,
        }
        proposal["cost_usd"] = cost_usd

        if self._recorder is not None:
            self._recorder.record_interaction(context, tools, sampling, proposal)
        return Result.success(proposal)


# Canonical alias for ModelPort adapter naming
OpenRouterModelAdapter = OpenRouterModel
