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
        calls = proposal.get("toolCalls", [])
        if not calls:
            return Result.success({"kind": "finish", "note": text or "Task completed."})
        if len(calls) != 1:
            return Result.fail("instrument_error", "multiple actions in one proposal are unsupported")

        call = calls[0]
        name = str(call["name"])
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
        if isinstance(raw_args, str):
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                return Result.fail("instrument_error", "malformed JSON arguments")
        else:
            args = raw_args
        if not isinstance(args, Mapping):
            return Result.fail("instrument_error", "tool arguments must be an object")
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
               "pricing_known", "pricing_source", "resolved_model"}
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


def _is_canonical_verb(name: str) -> bool:
    return bool(_CANONICAL_VERB.match(name))


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
        return {"kind": "process", "uriPattern": ""}
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
    bound: dict[str, Any] = {"kind": kind, "root": root}

    if kind == "fs":
        path = _workspace_relative(str(args.get("path", ".")), root)
        if not path.ok:
            return path
        args["path"] = path.value
        bound["path"] = path.value
        pattern = args.get("pattern")
        if isinstance(pattern, str):
            if "\x00" in pattern:
                return Result.fail("instrument_error", "pattern contains NUL")
            bound["pattern"] = pattern
        return Result.success(bound)

    argv = args.get("argv")
    if isinstance(argv, list):
        if not argv or not all(isinstance(item, str) and item for item in argv):
            return Result.fail("instrument_error", "action requires a non-empty argv array")
        if any("\x00" in item for item in argv):
            return Result.fail("instrument_error", "argv contains NUL")
        # A selector naming an executable pattern binds the head of argv, which
        # is what the sandbox allowlist is checked against.
        bound["kind"] = "process" if selector.get("uriPattern") else kind
        bound["executable"] = argv[0]
        return Result.success(bound)

    for key in ("uriPattern", "paths"):
        if key in selector:
            bound[key] = selector[key]
    return Result.success(bound)
