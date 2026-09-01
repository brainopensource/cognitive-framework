"""OpenAI-compatible OpenRouter adapter for ModelPort.

Owning contract: REQ-PORT-006, REQ-SLICE-001, T2.7, CT-33, ADR-0047.
Never import `slice/` or `spike/`. Secrets are references, never stored values.
Trust spine tests must never import this adapter.
"""

from __future__ import annotations

import json
import os
import random
import threading
import time
import urllib.error
import urllib.request
from codecs import getincrementaldecoder
from contextlib import contextmanager
from typing import Any, Callable, Iterable, Iterator, Mapping, Sequence

from ...ports.event_store import Result
from ...ports.model import ContextBundle, Proposal, Sampling, ToolSchemas
from .cassette import Cassette, CassettePlayer, CassetteRecorder
from .invocation import ProposalTranslator
from .dialect import ModelIntent, compile_intent
from ...domain.models.profile import profile_for
from .routing import resolve_route, preflight_check

__all__ = [
    "OpenRouterModel",
    "OpenRouterModelAdapter",
    "DEFAULT_ENDPOINT",
    "DEFAULT_KEY_REF",
    "DEFAULT_MODEL",
    "MODEL_PRICING",
    "DEFAULT_MODEL_PRICING",
    "MODEL_PRICING_MICROS",
    "DEFAULT_MODEL_PRICING_MICROS",
    "calculate_cost",
    "calculate_cost_micros",
    "estimate_tokens",
    "estimate_context_tokens",
    "estimate_proposal_tokens",
]

DEFAULT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_KEY_REF = "OPENROUTER_API_KEY"
from .config import get_pricing_usd_table, get_pricing_micros_table, get_default_model

DEFAULT_MODEL = get_default_model()
MODEL_PRICING = get_pricing_usd_table()
MODEL_PRICING_MICROS = get_pricing_micros_table()
DEFAULT_MODEL_PRICING: tuple[float, float, float] = (0.14, 0.28, 0.014)
DEFAULT_MODEL_PRICING_MICROS: tuple[int, int, int] = (140_000, 280_000, 14_000)


Transport = Callable[
    [str, dict[str, str], bytes],
    tuple[int, bytes] | tuple[int, Mapping[str, str], bytes],
]
StreamTransport = Callable[
    [str, dict[str, str], bytes],
    tuple[int, Mapping[str, str], Iterable[bytes]],
]


def _set_response_socket_timeout(response: Any, timeout: float) -> None:
    """Bound body reads as well as connection setup to the request timeout.

    ``urllib`` applies ``timeout`` while opening a connection, but some
    response implementations leave the underlying socket without that bound
    once headers have arrived.  A stalled provider body must become a typed
    adapter failure so the runtime can retry or fail closed; it must not hold
    an episode forever.  Test doubles and non-socket responses are deliberately
    ignored because their own read implementation owns its timing.
    """
    pending = [response]
    visited: set[int] = set()
    while pending:
        current = pending.pop()
        if current is None or id(current) in visited:
            continue
        visited.add(id(current))
        try:
            setter = getattr(current, "settimeout", None)
            if callable(setter):
                setter(timeout)
        except (OSError, TypeError, ValueError):
            pass
        # urllib/http.client versions differ in whether the socket is exposed
        # through fp.raw._sock, fp._sock, or an SSL/connection wrapper.
        for name in ("fp", "raw", "_sock", "_sslobj", "_connection"):
            try:
                nested = getattr(current, name, None)
            except (AttributeError, OSError):
                nested = None
            if nested is not None and id(nested) not in visited:
                pending.append(nested)


@contextmanager
def _response_read_deadline(response: Any, timeout: float):
    """Close a provider response if a body read outlives its deadline.

    Some urllib/TLS combinations do not propagate a socket timeout to a
    chunked body after headers arrive. A daemon timer is an independent
    enforcement path: closing the response unblocks the read and lets the
    adapter classify the interruption as a retryable instrument failure.
    """
    closer = getattr(response, "close", None)
    if not callable(closer):
        yield
        return
    timer = threading.Timer(timeout, closer)
    timer.daemon = True
    timer.start()
    try:
        yield
    finally:
        timer.cancel()


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


def calculate_cost_micros(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    cached_tokens: int = 0,
    pricing_table_micros: Mapping[str, tuple[int, int, int]] | None = None,
) -> tuple[int, bool]:
    """Calculate USD micros and whether pricing was explicitly known."""
    table = pricing_table_micros if pricing_table_micros is not None else MODEL_PRICING_MICROS
    pricing_known = model in table
    if not pricing_known:
        # Unknown pricing is not permission to invent a default price. The
        # caller receives an explicit unknown flag and zero measured cost.
        return 0, False
    pricing = table[model]
    prompt_price, completion_price, cached_price = pricing
    uncached_prompt = max(0, prompt_tokens - cached_tokens)
    micros = (
        (uncached_prompt * prompt_price)
        + (cached_tokens * cached_price)
        + (completion_tokens * completion_price)
    ) // 1_000_000
    return max(0, micros), pricing_known



def _http_post(
    url: str, headers: dict[str, str], body: bytes, timeout: float = 30.0
) -> tuple[int, dict[str, str], bytes]:
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            _set_response_socket_timeout(response, timeout)
            resp_headers = {k.lower(): v for k, v in response.headers.items()}
            with _response_read_deadline(response, timeout):
                raw = response.read()
            return int(response.status), resp_headers, raw
    except urllib.error.HTTPError as exc:
        resp_headers = (
            {k.lower(): v for k, v in exc.headers.items()}
            if hasattr(exc, "headers") and exc.headers
            else {}
        )
        body = b""
        if getattr(exc, "fp", None) is not None:
            try:
                body = exc.read() or b""
            except Exception:
                body = b""
        return int(exc.code), resp_headers, body


def _http_stream(
    url: str,
    headers: dict[str, str],
    body: bytes,
    timeout: float = 30.0,
) -> tuple[int, Mapping[str, str], Iterable[bytes]]:
    """Open an HTTP response and yield its body without first materialising it."""
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        response = urllib.request.urlopen(request, timeout=timeout)
    except urllib.error.HTTPError as exc:
        resp_headers = (
            {k.lower(): v for k, v in exc.headers.items()}
            if hasattr(exc, "headers") and exc.headers
            else {}
        )
        body = b""
        if getattr(exc, "fp", None) is not None:
            try:
                body = exc.read() or b""
            except Exception:
                body = b""
        return int(exc.code), resp_headers, (body,)

    resp_headers = {k.lower(): v for k, v in response.headers.items()}
    _set_response_socket_timeout(response, timeout)

    def chunks() -> Iterator[bytes]:
        with response:
            while True:
                with _response_read_deadline(response, timeout):
                    chunk = response.read(8_192)
                if not chunk:
                    return
                yield chunk

    return int(response.status), resp_headers, chunks()


def _redact(text: str, secret: str | None, ref: str) -> str:
    if secret:
        return text.replace(secret, ref)
    return text


def _messages(context: ContextBundle) -> list[dict[str, Any]]:
    # `list` alone is wrong here: `PromptAssembler` publishes this key as a
    # *tuple* (immutable bundle), so an exact `list` check silently missed the
    # assembled conversation and fell through to the lossy block rendering
    # below -- dropping tool-call structure and the protocol-recovery nudge on
    # every single live turn. Accept any non-str sequence.
    if isinstance(context, Mapping) and isinstance(
            context.get("messages"), (list, tuple)):
        return [dict(item) for item in context["messages"]]

    messages: list[dict[str, Any]] = []

    system = getattr(context, "system", None) or (context.get("system") if isinstance(context, Mapping) else None)
    if isinstance(system, str) and system:
        messages.append({"role": "system", "content": system})

    blocks = getattr(context, "blocks", None)
    if blocks is None and isinstance(context, Mapping):
        blocks = context.get("blocks")

    for block in (blocks or ()):
        layer = getattr(block, "layer", None) or (block.get("layer") if isinstance(block, Mapping) else None)
        if hasattr(layer, "value"):
            layer = layer.value
        label = getattr(block, "label", None) or (block.get("label", "") if isinstance(block, Mapping) else "")
        content = getattr(block, "text", None) or getattr(block, "content", None) or (block.get("text") or block.get("content", "") if isinstance(block, Mapping) else "")
        content_str = str(content or "")
        role = getattr(block, "role", None) or (block.get("role") if isinstance(block, Mapping) else None)

        # `VG-03 §10.1` (`agency/context/layers.py:ROLE_FOR_LAYER`) declares
        # L1 (system), L2 (tool schemas), and L3 (environment/conventions) all
        # route to role="system" -- this used to only implement L1, silently
        # demoting the tool-schema and harness/AGENTS.md blocks (L2, L3) into
        # role="user" instead. A live qualification traced a model repeatedly
        # emitting a malformed tool call (`fs.read({"path": "."})`) back to
        # this exact prompt shape: the tool contract and workspace
        # instructions arrived as anonymous user turns ahead of the real
        # task, rather than as the system framing the model was designed to
        # weight differently. Honoring the block's own declared role (already
        # correct in the compiled bundle) rather than re-deriving it from the
        # layer tag is the fix, and it stays correct if a layer is ever added.
        if role == "system" or layer == "L1" or label == "system-core":
            if not any(m.get("role") == "system" for m in messages):
                messages.append({"role": "system", "content": content_str})
            else:
                for m in messages:
                    if m.get("role") == "system":
                        if content_str not in m["content"]:
                            m["content"] += "\n\n" + content_str
                        break
        elif layer == "L5" and role in {"assistant", "tool"}:
            msg_entry: dict[str, Any] = {"role": role, "content": content_str}
            tool_calls = getattr(block, "tool_calls", None) or (block.get("tool_calls") if isinstance(block, Mapping) else None)
            if tool_calls:
                msg_entry["tool_calls"] = tool_calls
            tool_call_id = getattr(block, "tool_call_id", None) or (block.get("tool_call_id") if isinstance(block, Mapping) else None)
            if tool_call_id:
                msg_entry["tool_call_id"] = tool_call_id
            messages.append(msg_entry)
        else:
            if content_str:
                messages.append({"role": "user", "content": f"[{label}] {content_str}" if label else content_str})

    history = getattr(context, "history", None) or (context.get("history") if isinstance(context, Mapping) else None)
    for item in (history or ()):
        if isinstance(item, str):
            messages.append({"role": "user", "content": item})
        elif isinstance(item, Mapping):
            messages.append(dict(item))

    history_steps = getattr(context, "history_steps", None) or (context.get("history_steps") if isinstance(context, Mapping) else None)
    for step in (history_steps or ()):
        if not isinstance(step, Mapping):
            continue
        if step.get("type") == "assistant_tool_call":
            messages.append({"role": "assistant", "content": step.get("thought") or "",
                             "tool_calls": [{"id": step.get("call_id", "call_0"),
                                             "type": "function", "function": {
                                                 "name": step.get("action", ""),
                                                 "arguments": json.dumps(step.get("args", {}), sort_keys=True)}}]})
        elif step.get("type") == "tool_response":
            messages.append({"role": "tool", "tool_call_id": step.get("call_id", "call_0"),
                             "content": str(step.get("result_text", ""))})

    if not messages:
        messages.append({"role": "user", "content": "Please inspect the task and proceed."})
    return messages


def _tools_payload(tools: ToolSchemas) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for tool in tools:
        payload.append(
            {
                "type": "function",
                "function": {
                    "name": tool.get("name", ""),
                    # The manifest's description is the tool contract the
                    # model's function-calling head actually reads. Dropping it
                    # made every carefully-worded manifest description
                    # decorative on the wire.
                    "description": tool.get("description", ""),
                    "parameters": tool.get("schema") or {"type": "object"},
                },
            }
        )
    return payload


def _extract_dsml_tool_calls(text: str) -> tuple[str, list[dict[str, Any]]]:
    """Extract tool calls emitted via DeepSeek DSML markup tags."""
    import re
    invoke_rx = re.compile(
        r'<[｜|]DSML[｜|]invoke\s+name=["\']([^"\']+)["\']>(.*?)</[｜|]DSML[｜|]invoke>',
        re.DOTALL,
    )
    param_rx = re.compile(
        r'<[｜|]DSML[｜|]parameter\s+name=["\']([^"\']+)["\'][^>]*>(.*?)</[｜|]DSML[｜|]parameter>',
        re.DOTALL,
    )
    calls: list[dict[str, Any]] = []
    for idx, match in enumerate(invoke_rx.finditer(text)):
        name = match.group(1).strip()
        body = match.group(2)
        args: dict[str, Any] = {}
        for pmatch in param_rx.finditer(body):
            pname = pmatch.group(1).strip()
            pval = pmatch.group(2).strip()
            args[pname] = pval
        calls.append({
            "id": f"call_dsml_{idx + 1}",
            "name": name,
            "arguments": args,
        })
    clean_text = invoke_rx.sub("", text)
    clean_text = re.sub(r'</?[｜|]DSML[｜|][^>]*>', '', clean_text).strip()
    return clean_text, calls


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
    raw_calls = message.get("tool_calls")
    if raw_calls is None:
        raw_calls = []
    if not isinstance(raw_calls, list):
        return None
    for raw in raw_calls:
        if not isinstance(raw, Mapping):
            return None
        function = raw.get("function") if isinstance(raw.get("function"), Mapping) else {}
        if not function:
            return None
        arguments: Any = function.get("arguments", {})
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except Exception:
                return None
        if not isinstance(arguments, Mapping):
            return None
        name = function.get("name")
        call_id = raw.get("id")
        if not isinstance(name, str) or not name or not isinstance(call_id, str) or not call_id:
            return None
        tool_calls.append(
            {
                "id": call_id,
                "name": name,
                "arguments": dict(arguments),
            }
        )
    if not tool_calls and text and ("DSML" in text or "invoke" in text):
        clean_text, dsml_calls = _extract_dsml_tool_calls(text)
        if dsml_calls:
            tool_calls.extend(dsml_calls)
            text = clean_text
    return {"text": text, "toolCalls": tool_calls}


def _parse_sse_stream(
    raw: bytes | str | Iterable[str] | Iterable[bytes],
    *,
    start_monotonic: float | None = None,
    monotonic: Callable[[], float] = time.monotonic,
    max_event_bytes: int = 1_048_576,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, int]:
    """Incrementally parse a strict OpenAI-compatible SSE stream.

    A partial provider response is never a proposal. Malformed UTF-8/JSON,
    unsupported multiple choices, malformed tool calls, oversized frames, and
    EOF before ``[DONE]`` all fail closed as provider instrument errors.
    """
    if isinstance(raw, bytes | str):
        chunks: Iterable[bytes | str] = (raw,)
    else:
        chunks = raw

    text_parts: list[str] = []
    tool_calls_acc: dict[int, dict[str, str]] = {}
    raw_usage: dict[str, Any] | None = None
    first_token_time: float | None = None
    done = False
    terminal_choice = False
    buffer = ""
    decoder = getincrementaldecoder("utf-8")("strict")

    def note_first_delta() -> None:
        nonlocal first_token_time
        if first_token_time is None and start_monotonic is not None:
            first_token_time = monotonic()

    def accept_event(event: str) -> bool:
        nonlocal done, raw_usage, terminal_choice
        data_lines = [line[5:].lstrip(" ") for line in event.splitlines()
                      if line.startswith("data:")]
        if not data_lines:
            return True
        data = "\n".join(data_lines)
        if data == "[DONE]":
            done = True
            return True
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            return False
        if not isinstance(parsed, Mapping):
            return False
        usage = parsed.get("usage")
        if usage is not None:
            if not isinstance(usage, Mapping):
                return False
            raw_usage = dict(usage)
        choices = parsed.get("choices")
        if choices is None:
            return True
        if choices == [] and usage is not None:
            return True
        if not isinstance(choices, list) or len(choices) != 1:
            return False
        choice = choices[0]
        if not isinstance(choice, Mapping) or choice.get("index", 0) != 0:
            return False
        delta = choice.get("delta", {})
        if not isinstance(delta, Mapping):
            return False
        finish_reason = choice.get("finish_reason")
        if finish_reason is not None:
            if not isinstance(finish_reason, str) or not finish_reason:
                return False
            terminal_choice = True
        content = delta.get("content")
        if content is not None:
            if not isinstance(content, str):
                return False
            if content:
                note_first_delta()
                text_parts.append(content)
        calls = delta.get("tool_calls")
        if calls is None:
            return True
        if not isinstance(calls, list):
            return False
        for raw_call in calls:
            if not isinstance(raw_call, Mapping):
                return False
            index = raw_call.get("index", 0)
            if not isinstance(index, int) or isinstance(index, bool) or index < 0:
                return False
            call = tool_calls_acc.setdefault(index, {
                "id": "", "name": "", "arguments_str": "",
            })
            call_id = raw_call.get("id")
            if call_id is not None:
                if not isinstance(call_id, str) or not call_id:
                    return False
                call["id"] = call_id
                note_first_delta()
            function = raw_call.get("function")
            if function is None:
                continue
            if not isinstance(function, Mapping):
                return False
            name = function.get("name")
            if name is not None:
                if not isinstance(name, str) or not name:
                    return False
                call["name"] += name
                note_first_delta()
            arguments = function.get("arguments")
            if arguments is not None:
                if not isinstance(arguments, str):
                    return False
                call["arguments_str"] += arguments
                if len(call["arguments_str"].encode("utf-8")) > max_event_bytes:
                    return False
            if sum(len(value.encode("utf-8")) for value in text_parts) > max_event_bytes:
                return False
                note_first_delta()
        return True

    try:
        for chunk in chunks:
            if isinstance(chunk, bytes):
                buffer += decoder.decode(chunk, final=False)
            elif isinstance(chunk, str):
                buffer += chunk
            else:
                return None, None, 0
            if len(buffer.encode("utf-8")) > max_event_bytes:
                return None, None, 0
            while True:
                lf = buffer.find("\n\n")
                crlf = buffer.find("\r\n\r\n")
                if lf < 0 and crlf < 0:
                    break
                if crlf >= 0 and (lf < 0 or crlf < lf):
                    boundary, width = crlf, 4
                else:
                    boundary, width = lf, 2
                event, buffer = buffer[:boundary], buffer[boundary + width:]
                if not accept_event(event):
                    return None, None, 0
                if done:
                    break
            if done:
                break
        if not done:
            decoder.decode(b"", final=True)
            # OpenRouter-compatible providers sometimes close the SSE body
            # immediately after a terminal choice instead of sending the
            # optional `[DONE]` sentinel. A finish_reason is an explicit
            # protocol terminator; EOF without one remains truncated.
            if buffer.strip():
                if not accept_event(buffer):
                    return None, None, 0
            if not terminal_choice:
                return None, None, 0
    except (UnicodeDecodeError, OSError, ValueError):
        return None, None, 0

    ttft_millis = 0
    if first_token_time is not None and start_monotonic is not None:
        ttft_millis = max(1, int((first_token_time - start_monotonic) * 1000))

    tool_calls_list: list[dict[str, Any]] = []
    for idx in sorted(tool_calls_acc):
        call = tool_calls_acc[idx]
        if not call["id"] or not call["name"] or not call["arguments_str"]:
            return None, None, 0
        try:
            arguments = json.loads(call["arguments_str"], strict=False)
        except Exception:
            try:
                import ast
                arguments = ast.literal_eval(call["arguments_str"])
            except Exception:
                return None, None, 0
        if not isinstance(arguments, Mapping):
            return None, None, 0
        tool_calls_list.append({
            "id": call["id"],
            "name": call["name"],
            "arguments": dict(arguments),
        })

    proposal_text = "".join(text_parts)
    if not tool_calls_list and proposal_text and ("DSML" in proposal_text or "invoke" in proposal_text):
        clean_text, dsml_calls = _extract_dsml_tool_calls(proposal_text)
        if dsml_calls:
            tool_calls_list.extend(dsml_calls)
            proposal_text = clean_text
    if not proposal_text and not tool_calls_list:
        return None, None, 0
    return {"text": proposal_text, "toolCalls": tool_calls_list}, raw_usage, ttft_millis


class OpenRouterModel:
    """Live or cassette-backed ModelPort. Trust-spine tests must not construct this."""

    def __init__(
        self,
        *,
        api_key_ref: str = DEFAULT_KEY_REF,
        endpoint: str = DEFAULT_ENDPOINT,
        model: str = DEFAULT_MODEL,
        models: Sequence[str] | None = None,
        cassette: Cassette | None = None,
        mode: str = "live",
        transport: Transport | None = None,
        stream_transport: StreamTransport | None = None,
        environ: Mapping[str, str] | None = None,
        max_retries: int = 3,
        initial_delay: float = 0.1,
        max_delay: float = 30.0,
        jitter: bool = True,
        sleeper: Callable[[float], None] = time.sleep,
        pricing_table: Mapping[str, tuple[float, float, float]] | None = None,
        pricing_micros_table: Mapping[str, tuple[int, int, int]] | None = None,
        stream: bool = True,
        reasoning_effort: str | None = None,
        request_timeout: float = 30.0,
        monotonic: Callable[[], float] = time.monotonic,
        provider: str = "openrouter",
    ) -> None:
        self.api_key_ref = api_key_ref
        self._endpoint = endpoint
        # Policy-facing factories resolve and authorize identifiers. The
        # adapter still represents unknown routes so accounting can report
        # `pricing_known=false` instead of inventing a price.
        self._model = model
        self._models = list(models) if models is not None else None
        self._mode = mode
        self._provider = provider
        self._transport = transport
        self._stream_transport = stream_transport
        self._environ = dict(environ) if environ is not None else None
        self._max_retries = max_retries
        self._initial_delay = initial_delay
        self._max_delay = max_delay
        self._jitter = jitter
        self._sleeper = sleeper
        self._pricing_table = pricing_table
        self._pricing_micros_table = pricing_micros_table
        self._stream = stream
        self._reasoning_effort = reasoning_effort
        if request_timeout <= 0:
            raise ValueError("request_timeout must be positive")
        self._request_timeout = float(request_timeout)
        self._monotonic = monotonic
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

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def model(self) -> str:
        return self._model

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def capability_profile(self):
        """Versioned protocol profile used for attribution, not pricing."""
        return profile_for(self._model)

    def _lookup_secret(self) -> str | None:
        if self._environ is not None:
            value = self._environ.get(self.api_key_ref)
        else:
            value = os.environ.get(self.api_key_ref)
        if not value:
            from pathlib import Path
            root = Path(__file__).resolve().parents[4]
            env_p = root / ".env"
            if env_p.is_file():
                try:
                    for line in env_p.read_text(encoding="utf-8").splitlines():
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            if k.strip() == self.api_key_ref:
                                value = v.strip().strip("'\"")
                                break
                except Exception:
                    pass
        return value if value else None

    def _execute_transport(
        self,
        headers: dict[str, str],
        payload: bytes,
        secret: str,
    ) -> tuple[int, Mapping[str, str], bytes] | Result[Proposal]:
        transport = self._transport
        if transport is None:
            def transport(url: str, request_headers: dict[str, str], body: bytes):
                return _http_post(
                    url, request_headers, body, timeout=self._request_timeout
                )
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

    def _execute_stream_transport(
        self,
        headers: dict[str, str],
        payload: bytes,
        secret: str,
    ) -> tuple[int, Mapping[str, str], Iterable[bytes]] | Result[Proposal]:
        """Open an SSE response; retry only before any provider delta exists."""
        transport = self._stream_transport
        if transport is None:
            def transport(url: str, request_headers: dict[str, str], body: bytes):
                return _http_stream(
                    url, request_headers, body, timeout=self._request_timeout
                )
        attempts = 0
        retry_statuses = {429, 500, 502, 503, 504}
        while attempts <= self._max_retries:
            try:
                status, response_headers, chunks = transport(self._endpoint, headers, payload)
            except Exception as exc:
                if attempts < self._max_retries:
                    delay = min(self._initial_delay * (2 ** attempts), self._max_delay)
                    if self._jitter:
                        delay *= random.uniform(0.8, 1.2)
                    self._sleeper(delay)
                    attempts += 1
                    continue
                return Result.fail(
                    kind="instrument_error",
                    message=_redact(
                        f"provider stream could not open after {attempts + 1} attempts: {exc}",
                        secret,
                        self.api_key_ref,
                    ),
                    retryable=True,
                )
            if status == 200:
                return status, response_headers, chunks
            if status in retry_statuses and attempts < self._max_retries:
                self._sleeper(min(self._initial_delay * (2 ** attempts), self._max_delay))
                attempts += 1
                continue
            return Result.fail(
                kind="instrument_error",
                message=f"provider stream returned HTTP {status}",
                retryable=status in retry_statuses,
            )
        return Result.fail(
            kind="instrument_error",
            message="provider stream retries exhausted",
            retryable=True,
        )

    #: A well-formed HTTP 200 with no text and no tool call is a real,
    #: occasionally-observed provider behavior -- seen live against
    #: `deepseek/deepseek-v4-flash-0731` after several turns of otherwise
    #: normal tool use -- not evidence the model will repeat it. Bounded and
    #: named so it cannot silently become an unlimited loop against a model
    #: that genuinely never produces content.
    _EMPTY_PROPOSAL_MESSAGE = "proposal must contain text or a tool call"
    _MALFORMED_STREAM_MESSAGE = (
        "provider streaming response was malformed, truncated, or empty"
    )
    _EMPTY_PROPOSAL_RETRIES = 1

    def _complete(
        self,
        context: ContextBundle,
        tools: ToolSchemas,
        sampling: Sampling,
    ) -> Result[Proposal]:
        """Re-ask once on a genuinely empty completion before failing the episode.

        `_complete_once` already retries transport-level failures (429/5xx,
        connection errors). This is a different, adapter-observed failure
        class: the request succeeds and the provider returns a schema-valid
        response that simply carries no content. Previously that reached
        `EpisodeEngine` as an immediate `INSTRUMENT_ERROR`, terminating the
        whole episode on one empty completion (SWE-harness smoke runs hit
        this reliably). The retried attempt's own usage is billed and
        accounted normally on success; the discarded first attempt's tokens
        are not merged in, matching the existing behaviour when transport
        retries are exhausted without a usable response.
        """
        result = self._complete_once(context, tools, sampling)
        if result.ok:
            return result
        error = result.error
        if (
            self._EMPTY_PROPOSAL_RETRIES <= 0
            or error is None
            or error.kind != "instrument_error"
            or error.message not in {
                self._EMPTY_PROPOSAL_MESSAGE,
                self._MALFORMED_STREAM_MESSAGE,
            }
        ):
            return result
        for _ in range(self._EMPTY_PROPOSAL_RETRIES):
            result = self._complete_once(context, tools, sampling)
            if result.ok or (
                result.error is None
                or result.error.message not in {
                    self._EMPTY_PROPOSAL_MESSAGE,
                    self._MALFORMED_STREAM_MESSAGE,
                }
            ):
                return result
        return result

    def _complete_once(
        self,
        context: ContextBundle,
        tools: ToolSchemas,
        sampling: Sampling,
    ) -> Result[Proposal]:
        route = resolve_route(self._model)
        preflight = preflight_check(route)
        if isinstance(preflight, Result) and not preflight.ok:
            return preflight

        secret = self._lookup_secret()
        if secret is None:
            return Result.fail(
                kind="instrument_error",
                message=f"secret reference {self.api_key_ref} is unset",
            )
        target_model = self._models[0] if self._models else route.resolved_model
        dialect = compile_intent(
            ModelIntent(system="", messages=tuple(_messages(context)),
                        tools=tuple(tools), sampling=dict(sampling)),
            self.capability_profile,
        )
        body_obj: dict[str, Any] = {
            "model": target_model,
            "messages": list(dialect.messages),
            # 0.0 (fully greedy) reliably drove small/fast models into an
            # exact-repetition trap once two or three near-identical
            # (tool_call, tool_result) pairs sat in context: every subsequent
            # turn deterministically reproduced the same failing call, even
            # with the corrective tool result already in view. A low but
            # non-zero default breaks that attractor while staying close to
            # deterministic; callers that need exact reproducibility (a
            # cassette recording pass, a frozen canary) still get it by
            # passing sampling={"temperature": 0.0} explicitly.
            "temperature": sampling.get("temperature", 0.2),
            # Temperature alone did not reliably break the exact-repetition
            # trap above -- some turns still reissued the identical failing
            # tool call even with a corrective result already in context. A
            # frequency penalty is the more targeted lever: it discounts
            # tokens by how often they already occurred in this context, so
            # it specifically discourages regenerating the same JSON tool
            # call rather than perturbing everything uniformly. Overridable
            # the same way for reproducibility-sensitive callers.
            "frequency_penalty": sampling.get("frequencyPenalty", 0.4),
            # Reasoning-capable routes can spend the first tokens on hidden
            # deliberation.  The old 256-token default routinely exhausted
            # before a tool call, producing an empty proposal and burning a
            # turn.  Keep the bound explicit while leaving callers free to
            # narrow it through the sampling contract.
            "max_tokens": sampling.get("maxTokens", 4096),
        }
        if self._models:
            body_obj["models"] = list(self._models)
        if self._reasoning_effort is not None:
            body_obj["reasoning"] = {"effort": self._reasoning_effort}
        if self._stream and dialect.sampling.get("stream", True):
            body_obj["stream"] = True
            body_obj["stream_options"] = {"include_usage": True}
        tool_payload = list(dialect.tools)
        if tool_payload:
            body_obj["tools"] = tool_payload
            body_obj["parallel_tool_calls"] = bool(
                dialect.sampling.get("parallel_tool_calls", False))
            tool_choice = sampling.get("toolChoice") or sampling.get("tool_choice")
            if tool_choice is not None:
                if isinstance(tool_choice, str):
                    body_obj["tool_choice"] = tool_choice
                elif isinstance(tool_choice, Mapping):
                    body_obj["tool_choice"] = dict(tool_choice)
        payload = json.dumps(body_obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {secret}",
        }

        raw_usage = None
        ttft_millis = 0
        proposal = None

        start_time = self._monotonic()
        use_incremental_stream = self._stream and (
            self._stream_transport is not None or self._transport is None
        )
        if use_incremental_stream:
            stream_result = self._execute_stream_transport(headers, payload, secret)
            if isinstance(stream_result, Result):
                return stream_result
            _status, _response_headers, chunks = stream_result
            proposal, raw_usage, ttft_millis = _parse_sse_stream(
                chunks,
                start_monotonic=start_time,
                monotonic=self._monotonic,
            )
            if proposal is None:
                return Result.fail(
                    kind="instrument_error",
                    message="provider streaming response was malformed, truncated, or empty",
                )
        else:
            transport_result = self._execute_transport(headers, payload, secret)
            if isinstance(transport_result, Result):
                return transport_result
            _status, _response_headers, raw = transport_result
            is_sse = b"data:" in raw or (isinstance(raw, str) and "data:" in raw)
            if is_sse:
                proposal, raw_usage, ttft_millis = _parse_sse_stream(
                    raw,
                    start_monotonic=start_time,
                    monotonic=self._monotonic,
                )
                if proposal is None:
                    return Result.fail(
                        kind="instrument_error",
                        message="provider streaming response was malformed, truncated, or empty",
                    )
            else:
                decoded = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else str(raw)
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
                if isinstance(parsed.get("usage"), Mapping):
                    raw_usage = dict(parsed["usage"])
                fingerprint = parsed.get("system_fingerprint")
                if isinstance(fingerprint, str) and fingerprint:
                    proposal["model_fingerprint"] = fingerprint

        # Token usage and priced accounting
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

        uncached_prompt = max(0, prompt_tokens - cached_tokens)
        usd_micros = (
            (uncached_prompt * route.prompt_micros_per_1m)
            + (cached_tokens * route.cached_micros_per_1m)
            + (completion_tokens * route.completion_micros_per_1m)
        ) // 1_000_000
        cost_usd = round(usd_micros / 1_000_000.0, 8)

        proposal["usage"] = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cached_tokens": cached_tokens,
            "total_tokens": total_tokens,
            "cost_usd": cost_usd,
            "usd_micros": usd_micros,
            "pricing_known": route.pricing_known,
            "pricing_source": route.pricing_source,
            "resolved_model": route.resolved_model,
            "ttft_millis": ttft_millis,
        }
        proposal["cost_usd"] = cost_usd
        proposal["usd_micros"] = usd_micros
        proposal["pricing_known"] = route.pricing_known
        proposal["pricing_source"] = route.pricing_source
        proposal["resolved_model"] = route.resolved_model

        # In streaming/live mode, if a provider emits multiple parallel tool calls,
        # normalize to the primary atomic action to satisfy the single-action protocol.
        if proposal and isinstance(proposal.get("toolCalls"), list) and len(proposal["toolCalls"]) > 1:
            proposal = dict(proposal)
            proposal["toolCalls"] = [proposal["toolCalls"][0]]

        translated = ProposalTranslator.translate(proposal, tool_schemas=tools)
        if not translated.ok:
            return Result.fail(translated.error.kind, translated.error.message)
        canonical = dict(translated.value)
        # Usage is measurement metadata, not authority. Keep it beside the
        # canonical proposal for accounting without allowing it into args.
        canonical["usage"] = proposal["usage"]
        canonical["cost_usd"] = proposal["cost_usd"]
        canonical["usd_micros"] = proposal["usd_micros"]
        canonical["pricing_known"] = proposal["pricing_known"]
        canonical["pricing_source"] = proposal["pricing_source"]
        canonical["resolved_model"] = proposal["resolved_model"]
        if isinstance(proposal.get("model_fingerprint"), str):
            canonical["model_fingerprint"] = proposal["model_fingerprint"]
        canonical["text"] = proposal.get("text", "")

        if self._recorder is not None:
            self._recorder.record_interaction(context, tools, sampling, canonical)

        return Result.success(canonical)


# Canonical alias for ModelPort adapter naming
OpenRouterModelAdapter = OpenRouterModel
