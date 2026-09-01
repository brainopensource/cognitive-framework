"""Canonical provider-to-domain proposal translation.

Provider output is untrusted data. This module validates its shape, resolves
only manifest-declared tools, and binds a non-authoritative resource selector.
Capabilities, scope, reservations and approvals remain kernel/runtime-owned.
"""

from __future__ import annotations

import json
import re
import shlex
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Mapping, MutableMapping, Sequence

from ...ports.event_store import Result

__all__ = ["ModelInvocation", "ProposalTranslator", "validate_proposal_schema"]


@dataclass(frozen=True)
class ModelInvocation:
    invocation_id: str
    model: str
    context_digest: str
    tool_schemas: tuple[Mapping[str, Any], ...]
    sampling: Mapping[str, Any]
    created_at: str
    source: str = "context_compiler"


class ProposalTranslator:
    """Translate raw provider DTOs into the canonical proposal mapping."""

    #: Provider tool-calling vocabulary, keyed by the *declared schema
    #: property* it fills. This is adapter knowledge, not domain knowledge:
    #: knowing that one provider writes `file_path` where another writes `path`
    #: is precisely what a model adapter is for. It names no Vanguard verb, so
    #: a new domain adds nothing here (`S10-A-01`, `C-01`).
    #:
    #: A synonym is consulted only when the tool's own schema declares the
    #: target property and the model did not supply it.
    PROVIDER_SYNONYMS: Mapping[str, tuple[str, ...]] = {
        "path": ("file_path", "filepath", "path_prefix"),
        "pattern": ("query", "regex"),
    }

    #: Free-text command forms a provider may send where the schema declares an
    #: argument vector. Split with `shlex`, never with `str.split`.
    COMMAND_SYNONYMS: tuple[str, ...] = ("command", "cmd")

    @classmethod
    def translate(
        cls,
        proposal: Mapping[str, Any],
        *,
        tool_schemas: Sequence[Mapping[str, Any]] = (),
        aliases: Mapping[str, Any] | Any | None = None,
        resource_root: str = "/workspace",
        capabilities: Sequence[Mapping[str, Any]] = (),
    ) -> Result[Mapping[str, Any]]:
        checked = validate_proposal_schema(proposal)
        if not checked.ok:
            return Result.fail(checked.error.kind, checked.error.message)

        text = proposal.get("text", "")
        calls = list(proposal.get("toolCalls", []) or [])
        if not calls:
            calls = _lift_fenced_tool_calls(text, tool_schemas)
        if not calls:
            calls = _lift_text_tool_calls(text)
        if not calls:
            truncated = _unclosed_fence(text, tool_schemas)
            if truncated is not None:
                return Result.fail(
                    "instrument_error",
                    f"the '{truncated}' block was opened but never closed — the reply "
                    "was cut off before the closing fence. Send the action again with "
                    "a shorter payload.")
            return Result.success({"kind": "finish", "note": text or "Task completed."})
        if len(calls) != 1:
            return Result.fail("instrument_error", "multiple actions in one proposal are unsupported")

        call = calls[0]
        name = str(call["name"])

        # An explicit completion tool. Under `tool_choice="required"` -- which
        # the phase ladder sets on every turn -- the model is obliged to emit a
        # tool call, so the text-only path below that produces a `finish` is
        # unreachable and a run literally cannot terminate successfully. A
        # declared completion verb gives the model a way to say "done" inside
        # the protocol it is being forced to speak.
        if name in {"finish", "agency.finish"}:
            raw_args = call.get("arguments") or {}
            if isinstance(raw_args, str):
                try:
                    raw_args = json.loads(raw_args)
                except (TypeError, ValueError):
                    raw_args = {}
            note = ""
            if isinstance(raw_args, Mapping):
                note = str(raw_args.get("summary") or raw_args.get("note") or "")
            return Result.success({"kind": "finish", "note": note or "Task completed."})

        declared: dict[str, str] = {}

        if aliases is not None:
            if hasattr(aliases, "to_canonical_map"):
                declared.update({str(k): str(v) for k, v in aliases.to_canonical_map.items()})
            elif isinstance(aliases, Mapping):
                if "to_canonical" in aliases and isinstance(aliases["to_canonical"], Mapping):
                    declared.update({str(k): str(v) for k, v in aliases["to_canonical"].items()})
                elif "aliases" in aliases and isinstance(aliases["aliases"], Mapping):
                    declared.update({str(k): str(v) for k, v in aliases["aliases"].items()})
                else:
                    declared.update({str(k): str(v) for k, v in aliases.items() if isinstance(v, str)})

        # verb -> declared args schema, and verb -> declared selector. Both are
        # manifest data; the translator reads them and knows nothing else.
        schema_of: dict[str, Mapping[str, Any]] = {}
        selector_of: dict[str, Mapping[str, Any]] = {}
        for schema in tool_schemas:
            if not isinstance(schema, Mapping):
                continue
            function = schema.get("function")
            source = function if isinstance(function, Mapping) else schema
            schema_name = source.get("name") if isinstance(source, Mapping) else None
            verb = schema.get("verb")
            if isinstance(schema_name, str) and isinstance(verb, str):
                declared[schema_name] = verb
            if isinstance(verb, str):
                args_schema = schema.get("schema")
                if not isinstance(args_schema, Mapping) and isinstance(source, Mapping):
                    args_schema = source.get("parameters")
                if isinstance(args_schema, Mapping):
                    schema_of[verb] = args_schema
                selector = schema.get("selector")
                if isinstance(selector, Mapping):
                    selector_of[verb] = selector
        for row in capabilities or ():
            if not isinstance(row, Mapping):
                continue
            verb, selector = row.get("verb"), row.get("selector")
            if isinstance(verb, str) and isinstance(selector, Mapping):
                selector_of.setdefault(verb, selector)

        # The manifest is the only authority on which verbs exist. There is no
        # builtin table to fall back to: a translator carrying its own list of
        # legal verbs is a second place a domain has to be registered, and the
        # two drift (`C-01`, `ADR-0060`).
        if declared:
            action = declared.get(name)
            if action is None and name in set(declared.values()):
                action = name
            if action is None:
                # Fails closed against the pack that *is* declared.
                return Result.fail("instrument_error",
                                   f"tool is not declared by manifest: {name}")
        elif _is_canonical_verb(name):
            # No pack was supplied. The translator has no opinion about which
            # verbs exist -- carrying a builtin list is what made this file the
            # second place a domain had to be registered (`C-01`) -- but it can
            # tell a canonical verb from an alias by *shape*: `namespace.verb`
            # is already canonical and passes through unresolved.
            action = name
        else:
            # A bare tool name is a pack alias, and only a pack can resolve it.
            # Rejecting here rather than guessing is what keeps a competitor's
            # tool vocabulary out of this file (`C-01`).
            return Result.fail(
                "instrument_error",
                f"{name!r} is an alias; no manifest was supplied to resolve it")

        raw_args = call.get("arguments", {})
        args = _coerce_tool_arguments(raw_args)
        if args is None:
            kind = type(raw_args).__name__
            return Result.fail("instrument_error", f"tool arguments must be an object, got {kind}")
        args = dict(args)

        try:
            encoded = json.dumps(args, ensure_ascii=False, separators=(",", ":"))
        except (TypeError, ValueError):
            return Result.fail("instrument_error", "tool arguments are not JSON data")
        if len(encoded.encode("utf-8")) > 1_048_576:
            return Result.fail("instrument_error", "tool arguments exceed 1MB")
        if not _within_depth(args):
            return Result.fail("instrument_error", "tool arguments exceed nesting limit")

        # Normalise provider vocabulary against the *declared* schema. Nothing
        # here knows which verb it is normalising: the tool's own schema says
        # which properties exist, and a synonym is consulted only for a
        # property that schema declares.
        properties = _declared_properties(schema_of.get(action))
        for target, synonyms in cls.PROVIDER_SYNONYMS.items():
            # When the pack declared a schema, only its properties are filled.
            # With no schema there is nothing to consult, so a synonym present
            # in the call is taken at face value.
            if (properties and target not in properties) or target in args:
                continue
            for synonym in synonyms:
                if synonym in args:
                    args[target] = args[synonym]
                    break
        wants_argv = "argv" in properties or (
            not properties and any(key in args for key in cls.COMMAND_SYNONYMS))
        if wants_argv and "argv" not in args:
            command = next((args[key] for key in cls.COMMAND_SYNONYMS
                            if isinstance(args.get(key), str)), None)
            if not isinstance(command, str) or not command.strip():
                return Result.fail("instrument_error", "action requires an argv array")
            try:
                args["argv"] = shlex.split(command)
            except ValueError:
                return Result.fail("instrument_error", "command is not valid argv text")
            for key in cls.COMMAND_SYNONYMS:
                args.pop(key, None)

        if "path" not in args:
            diff_text = args.get("diff") or args.get("patch")
            if isinstance(diff_text, str):
                match = re.search(r"^\+\+\+\s+(?:b/)?(\S+)", diff_text, re.MULTILINE) or re.search(r"^---\s+(?:a/)?(\S+)", diff_text, re.MULTILINE)
                if match:
                    args["path"] = match.group(1)

        missing = _missing_required(schema_of.get(action), args)
        if missing:
            return Result.fail(
                "instrument_error",
                f"{name}: missing required argument(s): {', '.join(missing)}")

        selector = selector_of.get(action) or _selector_from_schema(
            properties or frozenset(args))
        resource = _bind_resource(selector, args, resource_root)
        if not resource.ok:
            return Result.fail(resource.error.kind, resource.error.message)
        return Result.success({
            "kind": "effect",
            "action": action,
            "resource": resource.value,
            "args": args,
            # Null is intentional: the provider has no reservation authority.
            # The episode parser normalises this to an empty runtime request.
            "reservation": None,
        })


def validate_proposal_schema(proposal: Mapping[str, Any]) -> Result[None]:
    if not isinstance(proposal, Mapping):
        return Result.fail("instrument_error", "provider proposal must be an object")

    allowed = {"text", "toolCalls", "usage", "cost_usd", "usd_micros",
               "pricing_known", "pricing_source", "resolved_model", "model_fingerprint"}
    unknown = set(proposal) - allowed
    if unknown:
        return Result.fail("instrument_error", f"proposal contains unsupported fields: {sorted(unknown)}")

    text = proposal.get("text", "")
    if not isinstance(text, str):
        return Result.fail("instrument_error", "proposal text must be a string")
    calls = proposal.get("toolCalls", [])
    if not isinstance(calls, list):
        return Result.fail("instrument_error", "toolCalls must be an array")
    if not text and not calls:
        return Result.fail("instrument_error", "proposal must contain text or a tool call")

    forbidden = {"capability", "scope", "reservation", "approval", "approvalIdentity",
                 "evaluator", "grant", "principal", "resource"}
    for call in calls:
        if not isinstance(call, Mapping):
            return Result.fail("instrument_error", "each tool call must be an object")
        if set(call) - {"id", "name", "arguments"}:
            return Result.fail("instrument_error", "tool call contains unsupported fields")
        if forbidden.intersection(call):
            return Result.fail("instrument_error", "provider cannot supply authority fields")
        name = call.get("name")
        if not isinstance(name, str) or not name:
            return Result.fail("instrument_error", "tool name must be a non-empty string")
        call_id = call.get("id")
        if call_id is not None and (not isinstance(call_id, str) or not call_id):
            return Result.fail("instrument_error", "tool call id must be a non-empty string")
        arguments = call.get("arguments", {})
        if not isinstance(arguments, (Mapping, str)):
            return Result.fail("instrument_error", "tool arguments must be an object or JSON string")

    return Result.success(None)


def _within_depth(value: Any, depth: int = 0) -> bool:
    if depth > 20:
        return False
    if isinstance(value, Mapping):
        return all(_within_depth(item, depth + 1) for item in value.values())
    if isinstance(value, list):
        return all(_within_depth(item, depth + 1) for item in value)
    return True


def _workspace_relative(path: str, root: str) -> Result[str]:
    if not isinstance(path, str) or "\x00" in path:
        return Result.fail("instrument_error", "filesystem action requires a path")
    if path in {"", ".", "/"}:
        return Result.success(".")
    pure = PurePosixPath(path)
    if pure.is_absolute():
        try:
            pure = pure.relative_to(PurePosixPath(root))
        except ValueError:
            return Result.fail("instrument_error", "filesystem path escapes workspace")
    if ".." in pure.parts:
        return Result.fail("instrument_error", "filesystem path escapes workspace")
    return Result.success("." if str(pure) == "." else str(pure))


#: `namespace.verb`, both segments non-empty and dot-free. A shape test, not a
#: list: it admits any `namespace`-qualified verb and enumerates none of them.
_CANONICAL_VERB = re.compile(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$")


def _coerce_tool_arguments(raw: Any) -> Mapping[str, Any] | None:
    """Accept objects or JSON strings; unwrap double-encoded JSON once or twice."""
    value: Any = {} if raw is None else raw
    for _ in range(3):
        if isinstance(value, Mapping):
            return value
        if not isinstance(value, str):
            return None
        text = value.strip()
        if not text:
            return {}
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return None
    return value if isinstance(value, Mapping) else None


def _is_canonical_verb(name: str) -> bool:
    return bool(_CANONICAL_VERB.match(name))


#: ```<tool> key=value key="value with spaces"
#: <payload lines>
#: ```
_FENCE = re.compile(r"^[ \t]*```[ \t]*(\S+)([^\n]*)\n(.*?)^[ \t]*```[ \t]*$",
                    re.DOTALL | re.MULTILINE)
_KV = re.compile(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\S+))')


def _payload_arguments(tool_schemas: Sequence[Mapping[str, Any]]) -> dict[str, tuple[str, str]]:
    """`tool name -> (payload argument, canonical verb)` for schemas that declare one.

    A tool schema opts in with `"payloadArgument": "<property>"`. Nothing here
    knows which verb or which domain that is: the pack says which of its own
    declared properties is too big or too quote-heavy to survive a JSON string,
    and this reader believes it (`C-01` — the translator carries no builtin
    vocabulary).
    """
    payloads: dict[str, tuple[str, str]] = {}
    for schema in tool_schemas:
        if not isinstance(schema, Mapping):
            continue
        argument = schema.get("payloadArgument")
        name, verb = schema.get("name"), schema.get("verb")
        if isinstance(argument, str) and argument and isinstance(name, str):
            payloads[name] = (argument, verb if isinstance(verb, str) else name)
    return payloads


def _lift_fenced_tool_calls(
    text: str, tool_schemas: Sequence[Mapping[str, Any]] = (),
) -> list[dict[str, Any]]:
    """Recover a tool call whose bulk argument rode *outside* the JSON.

    Asking a model to place source code inside a JSON string value is asking it
    to escape every quote, backslash and newline in a program while it is also
    writing the program. Models that solve the task correctly still lose the
    edit to a single unescaped quote, and the failure is silent -- the call
    parses as prose. Observed across three local models and two families: all
    three produced correct algorithms, none produced valid JSON.

    So the payload travels as a fenced block and only the small, structural
    arguments travel as `key=value`:

        ```patch path=pkg/stats.py
        def mean(values):
            if not values:
                raise ValueError("empty")      <- no escaping, ever
        ```

    This is the Aider lesson in `docs/SPEC.md` §4.1 -- match the edit format to
    model competence -- expressed as pack data rather than a code path: the
    fence is only consulted for a tool whose own schema names a
    `payloadArgument`, so a pack that does not want this behaviour never gets
    it, and adding a pack that does requires no change here.
    """
    payloads = _payload_arguments(tool_schemas)
    if not payloads or not isinstance(text, str) or not text.strip():
        return []
    for match in _FENCE.finditer(text):
        head, rest, body = match.group(1), match.group(2) or "", match.group(3)
        if head not in payloads:
            # A plain ```python block is a code fence, not a call. Only a fence
            # whose info string opens with a declared tool name is an action.
            continue
        argument, _verb = payloads[head]
        arguments: dict[str, Any] = {}
        for key, dq, sq, bare in _KV.findall(rest):
            arguments[key] = dq or sq or bare
        # The body is the payload verbatim, minus the trailing newline the
        # closing fence sits on. Nothing is stripped from inside it.
        arguments[argument] = body[:-1] if body.endswith("\n") else body
        return [{"name": head, "arguments": arguments}]
    return []


def _unclosed_fence(text: str, tool_schemas: Sequence[Mapping[str, Any]]) -> str | None:
    """Name the tool whose fence was opened and never closed.

    A response cut off by the completion-token ceiling ends mid-payload, so the
    closing fence never arrives and the whole action degrades to prose — the
    model is told nothing, and the turn is spent. Reporting the truncation is
    the difference between a model that shortens its next reply and one that
    repeats the same over-long one. The partial payload is deliberately *not*
    used: writing half a file is worse than writing none.
    """
    payloads = _payload_arguments(tool_schemas)
    if not payloads or not isinstance(text, str):
        return None
    if _FENCE.search(text):
        return None
    for match in re.finditer(r"^[ \t]*```[ \t]*(\S+)", text, re.MULTILINE):
        if match.group(1) in payloads:
            return match.group(1)
    return None


def _lift_text_tool_calls(text: str) -> list[dict[str, Any]]:
    """Recover a single tool call from model text when `toolCalls` is empty.

    Local models often emit Markdown/JSON tool blocks instead of provider
    function-calling. The kernel still admits only one effect per turn.
    """
    if not isinstance(text, str) or not text.strip():
        return []
    found: list[dict[str, Any]] = []
    for match in re.finditer(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL):
        parsed = _tool_object_from_json(match.group(1))
        if parsed is not None:
            found.append(parsed)
    if not found:
        decoder = json.JSONDecoder()
        idx = 0
        while idx < len(text):
            start = text.find("{", idx)
            if start < 0:
                break
            try:
                obj, end = decoder.raw_decode(text, start)
            except json.JSONDecodeError:
                idx = start + 1
                continue
            idx = end
            parsed = _tool_object_from_mapping(obj) if isinstance(obj, Mapping) else None
            if parsed is not None:
                found.append(parsed)
    return found[:1]


def _tool_object_from_json(raw: str) -> dict[str, Any] | None:
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return _tool_object_from_mapping(obj) if isinstance(obj, Mapping) else None


def _tool_object_from_mapping(obj: Mapping[str, Any]) -> dict[str, Any] | None:
    name = obj.get("name") or obj.get("verb")
    if not isinstance(name, str) or not name:
        return None
    # Plain JSON in a finish note is not a tool unless it names a verb or
    # carries tool-call arguments. This keeps F-09's translator conservative.
    # `parameters` is the third call spelling small models emit (F-21): it is
    # the key OpenAI's tool *schema* uses for the argument object, and
    # instruction-tuned models copy it into the call itself.
    has_call_shape = "arguments" in obj or "args" in obj or "parameters" in obj or "verb" in obj
    if not has_call_shape and not _is_canonical_verb(name):
        return None
    if "arguments" in obj:
        arguments = obj.get("arguments")
    elif "args" in obj:
        arguments = obj.get("args")
    elif "parameters" in obj:
        arguments = obj.get("parameters")
    else:
        arguments = {key: value for key, value in obj.items()
                     if key not in {"name", "verb", "id", "arguments", "args", "parameters"}}
    if arguments is None:
        arguments = {}
    return {"name": name, "arguments": arguments}


def _declared_properties(args_schema: Any) -> frozenset[str]:
    """Property names the tool's own schema declares. Empty when undeclared."""
    if not isinstance(args_schema, Mapping):
        return frozenset()
    properties = args_schema.get("properties")
    if not isinstance(properties, Mapping):
        return frozenset()
    return frozenset(str(key) for key in properties)


def _missing_required(args_schema: Any, args: Mapping[str, Any]) -> tuple[str, ...]:
    """Required properties the call did not supply.

    Refusing at translation tells the model what it left out. Letting it
    through means the failure surfaces states later, naming an adapter instead
    of the argument.
    """
    if not isinstance(args_schema, Mapping):
        return ()
    required = args_schema.get("required")
    if not isinstance(required, (list, tuple)):
        return ()
    return tuple(str(key) for key in required
                 if str(key) not in args or args.get(str(key)) is None)


def _selector_from_schema(properties: frozenset[str]) -> Mapping[str, Any] | None:
    """Infer a selector when the manifest declared none for this verb.

    Still property-driven, never verb-driven: an argument vector binds a
    process selector, a path or pattern binds a filesystem selector. Callers
    that pass only an alias table (no tool schemas) fall back to the argument
    keys actually supplied, which is the weakest signal available and is used
    only when the manifest offered nothing stronger.

    A manifest that supplies a real selector always wins.
    """
    if "argv" in properties:
        # `kind: process` is not in the domain selector algebra (ADR-0076 §2,
        # P1-17). An argv-based call binds `generic`, the same as any other
        # undeclared-selector verb.
        return {"kind": "generic", "uriPattern": ""}
    if "path" in properties or "pattern" in properties:
        return {"kind": "fs"}
    return {"kind": "generic"}


def _bind_resource(selector: Any, args: MutableMapping[str, Any],
                   root: str) -> Result[Mapping[str, Any]]:
    """Bind the declared selector to this call's arguments.

    Dispatch is on the **selector kind the manifest declares**, never on the
    verb. Workspace containment is a property of a filesystem selector, not of
    any particular filesystem verb, so a new domain declaring its own selector
    kind binds through the generic branch without a line changing here
    (`S10-A-01`, `C-01`).
    """
    if not isinstance(root, str) or not root or "\x00" in root:
        return Result.fail("instrument_error", "invalid resource root")
    if not isinstance(selector, Mapping):
        return Result.fail("instrument_error",
                           "manifest declares no selector for this verb")

    kind = str(selector.get("kind") or "generic")

    if kind == "fs":
        path = _workspace_relative(str(args.get("path", ".")), root)
        if not path.ok:
            return path
        args["path"] = path.value
        relative = path.value
        # Selector algebra admits only kind/root/paths. Extra keys (path,
        # pattern) make the request unparsable, which the classifier treats
        # as widening — and F-09 then denies after any untrusted receipt.
        bound: dict[str, Any] = {"kind": "fs", "root": root,
                                 "paths": [root if relative in {".", ""} else f"{root.rstrip('/')}/{relative}"]}
        pattern = args.get("pattern")
        if isinstance(pattern, str) and "\x00" in pattern:
            return Result.fail("instrument_error", "pattern contains NUL")
        return Result.success(bound)

    argv = args.get("argv")
    if isinstance(argv, list):
        if not argv or not all(isinstance(item, str) and item for item in argv):
            return Result.fail("instrument_error", "action requires a non-empty argv array")
        if any("\x00" in item for item in argv):
            return Result.fail("instrument_error", "argv contains NUL")
        # There is no `process` selector kind in the domain algebra (ADR-0076
        # §2, P1-17): an argv-based call binds `generic`, carrying only the
        # declared `uriPattern` the manifest granted — never a `root` or
        # `executable` field the algebra's `generic` branch cannot parse
        # (`parse_selector` admits kind/uriPattern only).
        return Result.success({"kind": "generic", "uriPattern": str(selector.get("uriPattern", ""))})

    bound = {"kind": kind}
    for key in ("uriPattern", "paths"):
        if key in selector:
            bound[key] = selector[key]
    return Result.success(bound)
