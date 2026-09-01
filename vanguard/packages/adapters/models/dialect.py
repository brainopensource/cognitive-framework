"""Provider dialect projection and typed response normalization."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ...domain.models.profile import ModelCapabilityProfile, ToolCallStyle, profile_for

__all__ = ["ModelIntent", "DialectRequest", "NormalizedResponse", "compile_intent", "normalize_response"]


@dataclass(frozen=True, slots=True)
class ModelIntent:
    system: str
    messages: tuple[Mapping[str, Any], ...] = ()
    tools: tuple[Mapping[str, Any], ...] = ()
    sampling: Mapping[str, Any] = field(default_factory=dict)
    response_schema: Mapping[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class DialectRequest:
    messages: tuple[Mapping[str, Any], ...]
    tools: tuple[Mapping[str, Any], ...]
    sampling: Mapping[str, Any]
    profile_id: str
    capability_profile_digest: str


@dataclass(frozen=True, slots=True)
class NormalizedResponse:
    proposal: Mapping[str, Any] | None
    failure: str | None = None
    usage: Mapping[str, Any] = field(default_factory=dict)
    raw_text: str = ""

    @property
    def ok(self) -> bool:
        return self.proposal is not None and self.failure is None


_SCHEMA = {"type": "object", "required": ["kind"], "properties": {
    "kind": {"enum": ["effect", "finish", "abstain"]},
    "action": {"type": "string"}, "args": {"type": "object"},
}}
_FENCE = re.compile(r"```(?:json)?\s*(.+?)\s*```", re.DOTALL | re.IGNORECASE)
_KIND = re.compile(r"^\s*KIND:\s*(\w+)\s*$", re.MULTILINE | re.IGNORECASE)
_ACTION = re.compile(r"^\s*ACTION:\s*(\S+)\s*$", re.MULTILINE | re.IGNORECASE)
_ARGS = re.compile(r"^\s*ARGS:\s*(\{.*\})\s*$", re.MULTILINE | re.IGNORECASE)


def _tools_prompt(tools: Sequence[Mapping[str, Any]]) -> str:
    return "\n".join(
        f"- {tool.get('name', tool.get('verb', ''))}: "
        f"{json.dumps(tool.get('parameters', tool.get('schema', {})), sort_keys=True)}"
        for tool in tools
    )


def compile_intent(intent: ModelIntent, profile: ModelCapabilityProfile | str | None = None) -> DialectRequest:
    resolved = profile if isinstance(profile, ModelCapabilityProfile) else profile_for(profile)
    extra = ""
    tools: tuple[Mapping[str, Any], ...] = ()
    sampling = dict(intent.sampling)
    sampling.pop("parallel_tool_calls", None)
    if resolved.supports_parallel_tool_calls:
        sampling["parallel_tool_calls"] = True
    if not resolved.supports_streaming:
        sampling["stream"] = False
    if resolved.tool_call_style is ToolCallStyle.NATIVE:
        tools = tuple({"type": "function", "function": {
            "name": tool.get("name", tool.get("verb", "")),
            "description": tool.get("description", ""),
            "parameters": tool.get("parameters", tool.get("schema", {"type": "object"})),
        }} for tool in intent.tools)
    elif resolved.tool_call_style is ToolCallStyle.JSON_SCHEMA:
        extra = f"Available actions:\n{_tools_prompt(intent.tools)}\nJSON schema: {json.dumps(intent.response_schema or _SCHEMA, sort_keys=True)}"
    elif resolved.tool_call_style is ToolCallStyle.FENCED_JSON:
        extra = f"Available actions:\n{_tools_prompt(intent.tools)}\nReply with one JSON object in a ```json fence. Schema: {json.dumps(intent.response_schema or _SCHEMA, sort_keys=True)}"
    else:
        extra = "Reply exactly as: KIND: <effect|finish|abstain>\nACTION: <name or ->\nARGS: <JSON object>"
    system = "\n\n".join(part for part in (intent.system, extra) if part)
    messages = tuple(({"role": "system", "content": system},) + tuple(dict(m) for m in intent.messages))
    if not resolved.supports_system_role:
        messages = tuple({"role": "user", "content": f"{system}\n\n{m.get('content', '')}"}
                         if i == 0 and m.get("role") == "user" else dict(m)
                         for i, m in enumerate(intent.messages))
    return DialectRequest(messages, tools, sampling, resolved.model_id, resolved.identity)


def _balanced(text: str) -> str | None:
    start, depth, quote, escaped = text.find("{"), 0, False, False
    if start < 0:
        return None
    for i in range(start, len(text)):
        ch = text[i]
        if quote:
            if escaped: escaped = False
            elif ch == "\\": escaped = True
            elif ch == '"': quote = False
        elif ch == '"': quote = True
        elif ch == "{": depth += 1
        elif ch == "}" and (depth := depth - 1) == 0: return text[start:i + 1]
    return None


def normalize_response(raw: Any, profile: ModelCapabilityProfile | str | None = None) -> NormalizedResponse:
    resolved = profile if isinstance(profile, ModelCapabilityProfile) else profile_for(profile)
    usage = dict(raw.get("usage", {})) if isinstance(raw, Mapping) and isinstance(raw.get("usage"), Mapping) else {}
    if isinstance(raw, Mapping) and "kind" in raw:
        return NormalizedResponse(dict(raw), usage=usage)
    text = raw if isinstance(raw, str) else ""
    if isinstance(raw, Mapping):
        choices = raw.get("choices")
        if isinstance(choices, Sequence) and choices and isinstance(choices[0], Mapping):
            message = choices[0].get("message", {})
            if isinstance(message, Mapping):
                calls = message.get("tool_calls")
                if isinstance(calls, Sequence) and calls and isinstance(calls[0], Mapping):
                    fn = calls[0].get("function", calls[0])
                    if isinstance(fn, Mapping) and fn.get("name"):
                        args = fn.get("arguments", {})
                        if isinstance(args, str):
                            try: args = json.loads(args)
                            except (TypeError, ValueError): return NormalizedResponse(None, "not_json", usage)
                        return NormalizedResponse({"kind": "effect", "action": fn["name"], "args": args}, usage=usage)
                text = str(message.get("content") or "")
    if resolved.tool_call_style is ToolCallStyle.TEXT_GRAMMAR:
        kind = _KIND.search(text)
        if kind:
            payload: dict[str, Any] = {"kind": kind.group(1).lower()}
            action = _ACTION.search(text)
            if action and action.group(1).lower() not in {"-", "none", "null"}:
                payload["action"] = action.group(1)
            args = _ARGS.search(text)
            if args:
                try:
                    parsed = json.loads(args.group(1))
                    if isinstance(parsed, Mapping):
                        payload["args"] = dict(parsed)
                except (TypeError, ValueError):
                    return NormalizedResponse(None, "not_json", usage, text)
            return NormalizedResponse(payload, usage=usage, raw_text=text)
    candidate = (_FENCE.search(text).group(1) if _FENCE.search(text) else _balanced(text)) or text.strip()
    try: payload = json.loads(candidate)
    except (TypeError, ValueError):
        return NormalizedResponse(None, "truncated" if text.count("{") > text.count("}") else "not_json", usage, text)
    if not isinstance(payload, Mapping): return NormalizedResponse(None, "not_an_object", usage, text)
    if "kind" not in payload: return NormalizedResponse(None, "missing_kind", usage, text)
    return NormalizedResponse(dict(payload), usage=usage, raw_text=text)
