"""Canonical ModelInvocation and provider-to-domain proposal translation.

Owning contract: S6B-MD-001, REQ-PORT-006, CT-33.
The runtime, never the model, supplies authoritative resource identity,
scope, reservation and capability.
"""

from dataclasses import dataclass
from typing import Any, Mapping
import json
from ...ports.event_store import Result

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
    KNOWN_TOOLS = {
        "fs.read": "read",
        "fs.search": "search",
        "patch.apply": "patch",
        "proc.test": "test"
    }

    @classmethod
    def translate(cls, proposal: Mapping[str, Any]) -> Result[Mapping[str, Any]]:
        text = proposal.get("text", "")
        tool_calls = proposal.get("toolCalls", [])
        
        if not tool_calls:
            if not text:
                return Result.fail(kind="instrument_error", message="Proposal has neither tool calls nor text.")
            return Result.success({"kind": "finish", "note": text})
            
        if len(tool_calls) > 1:
            return Result.fail(kind="instrument_error", message="Multiple actions in a single proposal are not supported.")
            
        call = tool_calls[0]
        name = call.get("name", "")
        if name not in cls.KNOWN_TOOLS:
            return Result.fail(kind="instrument_error", message=f"Unknown tool name: {name}")
            
        action = cls.KNOWN_TOOLS[name]
        args = call.get("arguments", {})
        
        if not isinstance(args, dict):
            return Result.fail(kind="instrument_error", message="Malformed JSON arguments.")
            
        try:
            args_str = json.dumps(args)
            if len(args_str.encode('utf-8')) > 1048576:
                return Result.fail(kind="instrument_error", message="Tool arguments exceed 1MB size limit.")
        except Exception:
            return Result.fail(kind="instrument_error", message="Malformed JSON arguments.")
            
        def check_depth(obj: Any, depth: int = 0) -> bool:
            if depth > 20:
                return False
            if isinstance(obj, dict):
                return all(check_depth(v, depth + 1) for v in obj.values())
            if isinstance(obj, list):
                return all(check_depth(v, depth + 1) for v in obj)
            return True
            
        if not check_depth(args):
            return Result.fail(kind="instrument_error", message="Tool arguments exceed 20 levels of nesting.")
            
        return Result.success({
            "kind": "effect",
            "action": action,
            "resource": {},
            "args": args
        })

def validate_proposal_schema(proposal: Mapping[str, Any]) -> Result[None]:
    return Result.success(None)
