"""Dialect compiler and response normaliser.

The agency emits ONE canonical `AgentIntent`. This module is the only place
that knows a given provider wants `tools=[...]` versus a JSON schema pasted
into the system prompt versus a fenced block versus a line grammar. Every
provider conditional in the codebase belongs here and nowhere else.

Two directions:

* ``compile_intent(intent, profile)`` -> ``DialectRequest`` — the wire form.
* ``normalise_response(raw, profile)`` -> ``NormalisedResponse`` — a canonical
  proposal payload plus usage and a typed failure, so the episode loop sees
  the same shape regardless of who answered.

The normaliser NEVER raises on bad provider output. A model that returns prose
where JSON was demanded is a *typed failure* the recovery policy acts on, not
an exception that kills the run.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ...domain.models.profile import (
    JsonReliability,
    ModelBehaviorProfile,
    ToolCallStyle,
    profile_for,
)

__all__ = [
    "AgentIntent",
    "DialectRequest",
    "ModelBehaviorProfile",
    "NormalisedResponse",
    "NormalisationFailure",
    "ToolCallStyle",
    "compile_intent",
    "normalise_response",
    "profile_for",
]


# --------------------------------------------------------------------------
# Canonical intent — what the agency says, provider-blind.
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AgentIntent:
    """Provider-independent description of one inference request."""

    system: str
    #: Ordered transcript. Each entry is ``{"role": ..., "content": ...}`` with
    #: role in {user, assistant, tool}.
    messages: tuple[Mapping[str, Any], ...] = ()
    #: Canonical tool descriptors: ``{"name", "description", "parameters"}``.
    tools: tuple[Mapping[str, Any], ...] = ()
    sampling: Mapping[str, Any] = field(default_factory=dict)
    #: When set, the reply must be a single object of this JSON schema.
    response_schema: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        for message in self.messages:
            if not isinstance(message, Mapping) or "role" not in message:
                raise ValueError("each message needs a role")
            if message["role"] not in {"user", "assistant", "tool", "system"}:
                raise ValueError(f"unsupported role {message['role']!r}")
        for tool in self.tools:
            if not isinstance(tool, Mapping) or not tool.get("name"):
                raise ValueError("each tool needs a name")


@dataclass(frozen=True, slots=True)
class DialectRequest:
    """The provider-shaped payload plus how to read the answer back."""

    messages: tuple[Mapping[str, Any], ...]
    tools: tuple[Mapping[str, Any], ...]
    sampling: Mapping[str, Any]
    #: How the reply is expected to arrive — the normaliser reads this.
    expect: ToolCallStyle
    #: True when the schema was inlined into the prompt rather than sent
    #: structurally, so a caller can tell the two apart in the ledger.
    schema_inlined: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "messages": [dict(m) for m in self.messages],
            "tools": [dict(t) for t in self.tools],
            "sampling": dict(self.sampling),
            "expect": self.expect.value,
            "schema_inlined": self.schema_inlined,
        }


# --------------------------------------------------------------------------
# Compilation: canonical intent -> provider wire form.
# --------------------------------------------------------------------------


#: The canonical proposal schema every dialect ultimately asks for. Kept small
#: on purpose: the smaller the schema, the higher the parse rate on weak models.
CANONICAL_PROPOSAL_SCHEMA: Mapping[str, Any] = {
    "type": "object",
    "required": ["kind"],
    "properties": {
        "kind": {"enum": ["effect", "finish", "abstain", "escalate", "spawn"]},
        "action": {"type": "string"},
        "args": {"type": "object"},
        "note": {"type": "string"},
    },
}

#: The reduced schema used on retry for LOW-reliability models. Two keys only.
REDUCED_PROPOSAL_SCHEMA: Mapping[str, Any] = {
    "type": "object",
    "required": ["kind"],
    "properties": {
        "kind": {"enum": ["effect", "finish", "abstain"]},
        "action": {"type": "string"},
    },
}

_FENCE_INSTRUCTION = (
    "Reply with exactly one JSON object wrapped in a ```json fence. "
    "Emit no prose before or after the fence."
)

_GRAMMAR_INSTRUCTION = (
    "Reply using exactly these lines and nothing else:\n"
    "KIND: <effect|finish|abstain|escalate>\n"
    "ACTION: <tool name, or - if none>\n"
    "ARGS: <single-line JSON object, or {}>"
)


def _tools_as_prompt_text(tools: Sequence[Mapping[str, Any]]) -> str:
    """Render tools into prose for providers with no native tool array."""
    if not tools:
        return ""
    lines = ["Available actions:"]
    for tool in tools:
        description = str(tool.get("description", "")).strip()
        params = tool.get("parameters") or {}
        rendered = json.dumps(params, sort_keys=True, separators=(",", ":"))
        lines.append(f"- {tool['name']}: {description} params={rendered}")
    return "\n".join(lines)


def _native_tools(tools: Sequence[Mapping[str, Any]]) -> tuple[Mapping[str, Any], ...]:
    """OpenAI-compatible function array."""
    return tuple(
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get("parameters") or {"type": "object", "properties": {}},
            },
        }
        for tool in tools
    )


def _fold_system(intent: AgentIntent, profile: ModelBehaviorProfile,
                 extra: str) -> tuple[Mapping[str, Any], ...]:
    """Place the system text where the provider can actually see it.

    Models without a system role get the instructions prepended to the first
    user turn — silently dropping them would make the agent look brain-damaged
    on exactly the cheap models we most want to use.
    """
    system_text = "\n\n".join(part for part in (intent.system, extra) if part.strip())
    if not system_text:
        return tuple(dict(m) for m in intent.messages)

    if profile.supports_system_role:
        return ({"role": "system", "content": system_text},
                *(dict(m) for m in intent.messages))

    folded: list[Mapping[str, Any]] = []
    injected = False
    for message in intent.messages:
        if not injected and message["role"] == "user":
            folded.append({"role": "user",
                           "content": f"{system_text}\n\n{message.get('content', '')}"})
            injected = True
        else:
            folded.append(dict(message))
    if not injected:
        folded.insert(0, {"role": "user", "content": system_text})
    return tuple(folded)


def _strip_reasoning(messages: Sequence[Mapping[str, Any]],
                     profile: ModelBehaviorProfile) -> tuple[Mapping[str, Any], ...]:
    """Drop reasoning blocks from prior assistant turns.

    Replaying a reasoning model's own scratchpad back at it degrades quality
    and burns context. The visible answer is the transcript; the thinking is not.
    """
    if not profile.emits_reasoning:
        return tuple(dict(m) for m in messages)
    cleaned: list[Mapping[str, Any]] = []
    for message in messages:
        entry = dict(message)
        entry.pop("reasoning", None)
        entry.pop("reasoning_content", None)
        cleaned.append(entry)
    return tuple(cleaned)


def compile_intent(
    intent: AgentIntent,
    profile: ModelBehaviorProfile | str | None = None,
    *,
    reduced_schema: bool = False,
) -> DialectRequest:
    """Render a canonical intent into the dialect this model actually speaks.

    ``reduced_schema`` is set by the recovery policy on a retry: it swaps in a
    two-key schema, which materially lifts the parse rate on weak models.
    """
    resolved = profile if isinstance(profile, ModelBehaviorProfile) else profile_for(profile)
    schema = REDUCED_PROPOSAL_SCHEMA if reduced_schema else (
        intent.response_schema or CANONICAL_PROPOSAL_SCHEMA)

    sampling = dict(intent.sampling)
    if not profile_supports_parallel(resolved):
        sampling.pop("parallel_tool_calls", None)
    if not resolved.supports_streaming:
        sampling["stream"] = False

    style = resolved.tool_call_style
    extra = ""
    native: tuple[Mapping[str, Any], ...] = ()
    schema_inlined = False

    if style is ToolCallStyle.NATIVE:
        native = _native_tools(intent.tools)
        if resolved.supports_parallel_tool_calls:
            sampling.setdefault("parallel_tool_calls", True)
    elif style is ToolCallStyle.JSON_SCHEMA:
        extra = "\n\n".join(filter(None, [
            _tools_as_prompt_text(intent.tools),
            "Reply with a single JSON object matching this schema:",
            json.dumps(schema, sort_keys=True, separators=(",", ":")),
        ]))
        schema_inlined = True
    elif style is ToolCallStyle.FENCED_JSON:
        extra = "\n\n".join(filter(None, [
            _tools_as_prompt_text(intent.tools),
            _FENCE_INSTRUCTION,
            json.dumps(schema, sort_keys=True, separators=(",", ":")),
        ]))
        schema_inlined = True
    else:  # TEXT_GRAMMAR
        extra = "\n\n".join(filter(None, [
            _tools_as_prompt_text(intent.tools),
            _GRAMMAR_INSTRUCTION,
        ]))
        schema_inlined = True

    messages = _strip_reasoning(_fold_system(intent, resolved, extra), resolved)
    return DialectRequest(
        messages=messages,
        tools=native,
        sampling=sampling,
        expect=style,
        schema_inlined=schema_inlined,
    )


def profile_supports_parallel(profile: ModelBehaviorProfile) -> bool:
    return profile.supports_parallel_tool_calls


# --------------------------------------------------------------------------
# Normalisation: provider reply -> canonical proposal payload.
# --------------------------------------------------------------------------


class NormalisationFailure(str):
    """Typed failure label. A `str` subclass so it serialises transparently."""

    NO_CONTENT = "no_content"
    NOT_JSON = "not_json"
    NOT_AN_OBJECT = "not_an_object"
    MISSING_KIND = "missing_kind"
    TRUNCATED = "truncated"


@dataclass(frozen=True, slots=True)
class NormalisedResponse:
    """Canonical view of whatever the provider said."""

    proposal: Mapping[str, Any] | None
    usage: Mapping[str, Any] = field(default_factory=dict)
    failure: str | None = None
    #: Raw text kept for diagnostics; never written to a durable event.
    raw_text: str = ""

    @property
    def ok(self) -> bool:
        return self.proposal is not None and self.failure is None


_FENCE = re.compile(r"```(?:json)?\s*(.+?)\s*```", re.DOTALL)
#: Each field is matched independently. A single combined pattern with
#: optional groups silently matches them empty under lazy quantifiers, which
#: drops ACTION and ARGS whenever any prose sits between the lines.
_GRAMMAR_KIND = re.compile(r"^\s*KIND:\s*(\w+)\s*$", re.IGNORECASE | re.MULTILINE)
_GRAMMAR_ACTION = re.compile(r"^\s*ACTION:\s*(\S+)\s*$", re.IGNORECASE | re.MULTILINE)
_GRAMMAR_ARGS = re.compile(r"^\s*ARGS:\s*(\{.*\})\s*$", re.IGNORECASE | re.MULTILINE)


def _balanced_object(text: str) -> str | None:
    """Extract the first balanced ``{...}`` run, ignoring braces inside strings.

    Regex cannot do this correctly and chatty models love wrapping JSON in
    commentary, so this is a small scanner rather than a pattern.
    """
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return None


def _extract_json(text: str) -> tuple[Mapping[str, Any] | None, str | None]:
    """Best-effort object extraction. Returns (payload, failure)."""
    if not text or not text.strip():
        return None, NormalisationFailure.NO_CONTENT

    candidates: list[str] = []
    fenced = _FENCE.search(text)
    if fenced:
        candidates.append(fenced.group(1))
    balanced = _balanced_object(text)
    if balanced:
        candidates.append(balanced)
    candidates.append(text.strip())

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(parsed, Mapping):
            return parsed, None
        return None, NormalisationFailure.NOT_AN_OBJECT

    # An unterminated object means the reply was cut off — a truncation
    # failure, which recovers differently from plain unparseable prose.
    if text.count("{") > text.count("}"):
        return None, NormalisationFailure.TRUNCATED
    return None, NormalisationFailure.NOT_JSON


def _from_grammar(text: str) -> tuple[Mapping[str, Any] | None, str | None]:
    """Parse the line grammar. Tolerates prose interleaved between the lines."""
    body = text or ""
    kind = _GRAMMAR_KIND.search(body)
    if not kind:
        # The grammar was requested but the model answered in JSON anyway —
        # accept that rather than failing a turn we can plainly read.
        return _extract_json(body)

    payload: dict[str, Any] = {"kind": kind.group(1).strip().lower()}

    action = _GRAMMAR_ACTION.search(body)
    if action and action.group(1).strip() not in {"-", "none", "null"}:
        payload["action"] = action.group(1).strip()

    args = _GRAMMAR_ARGS.search(body)
    if args:
        try:
            decoded = json.loads(args.group(1))
            if isinstance(decoded, Mapping) and decoded:
                payload["args"] = dict(decoded)
        except (json.JSONDecodeError, ValueError):
            pass  # a malformed ARGS line degrades to no args, not a dead turn
    return payload, None


def _text_of(raw: Any) -> str:
    """Pull assistant text out of the several shapes providers return."""
    if isinstance(raw, str):
        return raw
    if not isinstance(raw, Mapping):
        return ""
    for key in ("text", "content", "output_text"):
        value = raw.get(key)
        if isinstance(value, str):
            return value
    choices = raw.get("choices")
    if isinstance(choices, Sequence) and choices:
        first = choices[0]
        if isinstance(first, Mapping):
            message = first.get("message")
            if isinstance(message, Mapping):
                content = message.get("content")
                if isinstance(content, str):
                    return content
    return ""


def _native_tool_call(raw: Any) -> Mapping[str, Any] | None:
    """Read a structured tool call out of an OpenAI-compatible reply."""
    if not isinstance(raw, Mapping):
        return None

    calls = raw.get("tool_calls")
    if not calls:
        choices = raw.get("choices")
        if isinstance(choices, Sequence) and choices and isinstance(choices[0], Mapping):
            message = choices[0].get("message")
            if isinstance(message, Mapping):
                calls = message.get("tool_calls")

    if not isinstance(calls, Sequence) or not calls:
        return None
    first = calls[0]
    if not isinstance(first, Mapping):
        return None
    function = first.get("function") if isinstance(first.get("function"), Mapping) else first
    name = function.get("name")
    if not name:
        return None
    arguments = function.get("arguments")
    args: Mapping[str, Any] = {}
    if isinstance(arguments, Mapping):
        args = arguments
    elif isinstance(arguments, str) and arguments.strip():
        try:
            decoded = json.loads(arguments)
            if isinstance(decoded, Mapping):
                args = decoded
        except (json.JSONDecodeError, ValueError):
            args = {}
    return {"kind": "effect", "action": str(name), "args": dict(args)}


def _usage_of(raw: Any) -> Mapping[str, Any]:
    if not isinstance(raw, Mapping):
        return {}
    usage = raw.get("usage")
    return dict(usage) if isinstance(usage, Mapping) else {}


def normalise_response(
    raw: Any,
    profile: ModelBehaviorProfile | str | None = None,
    *,
    expect: ToolCallStyle | None = None,
) -> NormalisedResponse:
    """Convert any provider reply into a canonical proposal payload.

    Never raises. A reply we cannot read becomes a typed `failure` the recovery
    policy classifies and acts on.
    """
    resolved = profile if isinstance(profile, ModelBehaviorProfile) else profile_for(profile)
    style = expect or resolved.tool_call_style
    usage = _usage_of(raw)
    text = _text_of(raw)

    # A native tool call always wins when present, whatever the declared style:
    # some providers emit one even when we asked for JSON.
    native = _native_tool_call(raw)
    if native is not None:
        return NormalisedResponse(proposal=native, usage=usage, raw_text=text)

    # Some adapters hand us an already-canonical dict.
    if isinstance(raw, Mapping) and "kind" in raw:
        return NormalisedResponse(proposal=dict(raw), usage=usage, raw_text=text)

    if style is ToolCallStyle.TEXT_GRAMMAR:
        payload, failure = _from_grammar(text)
    else:
        payload, failure = _extract_json(text)

    if payload is None:
        return NormalisedResponse(None, usage=usage, failure=failure, raw_text=text)

    if "kind" not in payload:
        # A bare tool-shaped object (name+arguments) is a common near-miss;
        # promote it rather than failing the turn.
        if payload.get("name"):
            promoted = {
                "kind": "effect",
                "action": str(payload["name"]),
                "args": dict(payload.get("arguments") or payload.get("args") or {}),
            }
            return NormalisedResponse(promoted, usage=usage, raw_text=text)
        return NormalisedResponse(
            None, usage=usage, failure=NormalisationFailure.MISSING_KIND, raw_text=text)

    canonical = dict(payload)
    canonical["kind"] = str(canonical["kind"]).strip().lower()
    return NormalisedResponse(canonical, usage=usage, raw_text=text)
