"""Canonical provider-to-domain proposal translation.

Provider output is untrusted data. This module validates its shape, resolves
only manifest-declared tools, and binds a non-authoritative resource selector.
Capabilities, scope, reservations and approvals remain kernel/runtime-owned.
"""

from __future__ import annotations

import json
import shlex
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Mapping, Sequence

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

    KNOWN_TOOLS = {
        "fs.read": "fs.read",
        "fs.search": "fs.search",
        "fs.write": "fs.write",
        "patch.apply": "patch.apply",
        "fs.patch": "patch.apply",
        "proc.exec": "proc.exec",
        "proc.test": "proc.test",
    }

    @classmethod
    def translate(
        cls,
        proposal: Mapping[str, Any],
        *,
        tool_schemas: Sequence[Mapping[str, Any]] = (),
        aliases: Mapping[str, Any] | Any | None = None,
        resource_root: str = "/workspace",
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

        for schema in tool_schemas:
            if not isinstance(schema, Mapping):
                continue
            function = schema.get("function")
            source = function if isinstance(function, Mapping) else schema
            schema_name = source.get("name") if isinstance(source, Mapping) else None
            verb = schema.get("verb")
            if isinstance(schema_name, str) and isinstance(verb, str):
                declared[schema_name] = verb

        if declared:
            action = declared.get(name)
            if action is None:
                return Result.fail("instrument_error", f"tool is not declared by manifest: {name}")
            if action not in set(cls.KNOWN_TOOLS.values()):
                return Result.fail("instrument_error", f"manifest declares unsupported tool: {action}")
        else:
            action = cls.KNOWN_TOOLS.get(name)
            if action is None:
                return Result.fail("instrument_error", f"unknown tool name: {name}")

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

        if action in {"fs.read", "fs.write", "patch.apply"}:
            if "path" not in args and "file_path" in args:
                args["path"] = args["file_path"]

        if action == "fs.search":
            if "pattern" not in args and "query" in args:
                args["pattern"] = args["query"]
            if "path" not in args and "path_prefix" in args:
                args["path"] = args["path_prefix"]

        if action in {"proc.exec", "proc.test"} and "argv" not in args:
            command = args.get("command") or args.get("cmd")
            if not isinstance(command, str) or not command.strip():
                return Result.fail("instrument_error", "process action requires argv array")
            try:
                args["argv"] = shlex.split(command)
            except ValueError:
                return Result.fail("instrument_error", "process command is not valid argv text")
            args.pop("command", None)
            args.pop("cmd", None)

        resource = _bind_resource(action, args, resource_root)
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


def _bind_resource(action: str, args: Mapping[str, Any], root: str) -> Result[Mapping[str, Any]]:
    if not isinstance(root, str) or not root or "\x00" in root:
        return Result.fail("instrument_error", "invalid resource root")
    if action in {"fs.read", "fs.write", "patch.apply"}:
        path = args.get("path", ".")
        if not isinstance(path, str) or not path or "\x00" in path:
            return Result.fail("instrument_error", "filesystem action requires a path")
        pure = PurePosixPath(path)
        if pure.is_absolute() or ".." in pure.parts:
            return Result.fail("instrument_error", "filesystem path escapes workspace")
        return Result.success({"kind": "fs", "root": root, "path": str(pure)})
    if action == "fs.search":
        path = args.get("path", ".")
        pattern = args.get("pattern")
        if not isinstance(path, str) or not isinstance(pattern, str) or "\x00" in path + pattern:
            return Result.fail("instrument_error", "search requires safe path and pattern")
        pure = PurePosixPath(path)
        if pure.is_absolute() or ".." in pure.parts:
            return Result.fail("instrument_error", "search path escapes workspace")
        return Result.success({"kind": "fs", "root": root, "path": str(pure), "pattern": pattern})
    if action in {"proc.exec", "proc.test"}:
        argv = args.get("argv")
        if not isinstance(argv, list) or not argv or not all(isinstance(x, str) and x for x in argv):
            return Result.fail("instrument_error", "process action requires argv array")
        if any("\x00" in x for x in argv):
            return Result.fail("instrument_error", "process argv contains NUL")
        return Result.success({"kind": "process", "root": root, "executable": argv[0]})
    return Result.fail("instrument_error", f"unsupported action: {action}")
