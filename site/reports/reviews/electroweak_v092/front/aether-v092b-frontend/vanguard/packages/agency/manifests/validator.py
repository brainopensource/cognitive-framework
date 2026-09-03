"""Native Manifest Logical Validator & Linter (EVO-10, GTS-13C §7.3, REQ-HARN-001).

Validates that action-to-tool bindings, resource selectors, budget allocations,
constraints, and risk tiers are logically consistent before runtime composition.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .loader import LoadedManifestPack, ManifestLoader

__all__ = [
    "ManifestValidationError",
    "validate_manifest",
    "validate_manifest_pack",
]

VALID_RISK_TIERS = frozenset({"low", "medium", "high", "critical", "none"})
VALID_SINKS = frozenset({"observation", "privileged", "control", "sink", "kernel", "meta", "audit"})
VALID_JSON_SCHEMA_TYPES = frozenset({"object", "string", "number", "integer", "boolean", "array", "null"})


class ManifestValidationError(ValueError):
    """Raised when an agent manifest fails logical validation rules."""
    pass


def _validate_json_schema(schema: Any, context_label: str) -> None:
    """Validate that a schema object conforms to basic JSON Schema structure."""
    if not isinstance(schema, Mapping):
        raise ManifestValidationError(f"{context_label}: Tool schema must be a JSON object, got {type(schema).__name__}")
    
    schema_type = schema.get("type")
    if schema_type is not None:
        if isinstance(schema_type, str):
            if schema_type not in VALID_JSON_SCHEMA_TYPES:
                raise ManifestValidationError(f"{context_label}: Invalid JSON schema type {schema_type!r}")
        elif isinstance(schema_type, list):
            for t in schema_type:
                if t not in VALID_JSON_SCHEMA_TYPES:
                    raise ManifestValidationError(f"{context_label}: Invalid JSON schema type in union: {t!r}")
        else:
            raise ManifestValidationError(f"{context_label}: 'type' must be str or list, got {type(schema_type).__name__}")

    properties = schema.get("properties")
    if properties is not None:
        if not isinstance(properties, Mapping):
            raise ManifestValidationError(f"{context_label}: 'properties' must be an object")
        for prop_name, prop_schema in properties.items():
            _validate_json_schema(prop_schema, f"{context_label}.properties[{prop_name}]")


def _validate_budget(budget_data: Mapping[str, Any], context_label: str) -> None:
    """Ensure all budget allocations are non-negative integers."""
    if not isinstance(budget_data, Mapping):
        raise ManifestValidationError(f"{context_label}: Budget allocation must be a JSON object")

    for key, value in budget_data.items():
        if isinstance(value, Mapping):
            _validate_budget(value, f"{context_label}.{key}")
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            if value < 0:
                raise ManifestValidationError(f"{context_label}: Budget {key!r} cannot be negative ({value})")
            if isinstance(value, float) and not value.is_integer():
                raise ManifestValidationError(f"{context_label}: Budget {key!r} must be an integer ({value})")
        elif value is None:
            continue
        elif not isinstance(value, (str, list, tuple)):
            raise ManifestValidationError(f"{context_label}: Invalid budget value for {key!r}: {value!r}")


def _validate_constraints(constraints_data: Mapping[str, Any], context_label: str) -> None:
    """Validate agent recursion and depth constraints."""
    if not isinstance(constraints_data, Mapping):
        raise ManifestValidationError(f"{context_label}: Constraints must be a JSON object")

    max_depth = constraints_data.get("max_depth", constraints_data.get("maxDepth"))
    if max_depth is not None:
        if not isinstance(max_depth, int) or isinstance(max_depth, bool):
            raise ManifestValidationError(f"{context_label}: max_depth must be an integer, got {type(max_depth).__name__}")
        if max_depth < 1 or max_depth > 16:
            raise ManifestValidationError(f"{context_label}: max_depth must be between 1 and 16, got {max_depth}")


def validate_manifest(
    manifest_or_pack: LoadedManifestPack | Mapping[str, Any] | Path | str,
    base_dir: Path | str | None = None,
) -> None:
    """Validate an agent manifest against all logical consistency rules.

    Rules enforced:
    1. Every verb declared in capabilities must have a valid registered sink and risk tier.
    2. Initial budget allocations (tokens, micros, steps) must be non-negative integers.
    3. constraints.max_depth must be between 1 and 16.
    4. Tool parameter schemas must be valid JSON Schema objects.
    5. Resource selectors must declare valid structure.
    """
    if isinstance(manifest_or_pack, LoadedManifestPack):
        validate_manifest_pack(manifest_or_pack)
        return

    if isinstance(manifest_or_pack, (str, Path)):
        p = Path(manifest_or_pack).resolve()
        loader = ManifestLoader(manifests_base_dir=base_dir or (p.parent if p.is_file() else p))
        if p.is_dir():
            pack = loader.load_pack(p.name)
            validate_manifest_pack(pack)
            return
        elif p.is_file():
            raw = json.loads(p.read_text(encoding="utf-8"))
            validate_manifest_dict(raw, base_dir=p.parent)
            return

    if isinstance(manifest_or_pack, Mapping):
        validate_manifest_dict(manifest_or_pack, base_dir=Path(base_dir).resolve() if base_dir else None)
        return

    raise ManifestValidationError(f"Unsupported manifest type: {type(manifest_or_pack).__name__}")


def validate_manifest_dict(raw: Mapping[str, Any], base_dir: Path | None = None) -> None:
    """Validate a raw manifest dictionary and any linked component files."""
    if not isinstance(raw, Mapping):
        raise ManifestValidationError(f"Manifest must be a JSON object, got {type(raw).__name__}")

    # Check api / schema version
    api = raw.get("api")
    if api == "mhf.manifest/2":
        # /2 named manifest validation
        _validate_named_manifest_dict(raw, base_dir)
        return

    # Capabilities validation
    capabilities = raw.get("capabilities", [])
    if not isinstance(capabilities, (list, tuple)):
        raise ManifestValidationError("'capabilities' must be an array")

    declared_verbs: set[str] = set()
    for idx, cap in enumerate(capabilities):
        if not isinstance(cap, Mapping):
            raise ManifestValidationError(f"capabilities[{idx}] must be an object")
        verb = cap.get("verb")
        if not isinstance(verb, str) or not verb.strip():
            raise ManifestValidationError(f"capabilities[{idx}]: missing or empty 'verb'")
        declared_verbs.add(verb.strip())

        sink = cap.get("sink")
        if not isinstance(sink, str) or sink not in VALID_SINKS:
            raise ManifestValidationError(f"capabilities[{idx}] ({verb}): invalid sink {sink!r}, expected one of {sorted(VALID_SINKS)}")

        risk = cap.get("risk")
        if not isinstance(risk, str) or risk not in VALID_RISK_TIERS:
            raise ManifestValidationError(f"capabilities[{idx}] ({verb}): invalid risk tier {risk!r}, expected one of {sorted(VALID_RISK_TIERS)}")

        selector = cap.get("selector")
        if not isinstance(selector, Mapping) and not isinstance(selector, str):
            raise ManifestValidationError(f"capabilities[{idx}] ({verb}): selector must be object or string")

    # Constraints validation
    constraints = raw.get("constraints")
    if constraints is not None:
        _validate_constraints(constraints, "constraints")

    # Scope validation
    scope = raw.get("scope")
    if isinstance(scope, Mapping):
        scope_actions = scope.get("actions")
        if isinstance(scope_actions, (list, tuple)):
            for action in scope_actions:
                if not isinstance(action, str) or not action.strip():
                    raise ManifestValidationError(f"scope.actions contains empty action: {action!r}")
                if declared_verbs and action not in declared_verbs:
                    raise ManifestValidationError(f"scope.actions declares verb {action!r} not in manifest capabilities")

    # Budget policy validation
    budget = raw.get("budget")
    if isinstance(budget, Mapping):
        _validate_budget(budget, "budget")

    # Components validation (e.g. tools, budget-policy)
    components = raw.get("components", {})
    if isinstance(components, Mapping):
        tools_refs = components.get("tools", [])
        if isinstance(tools_refs, (list, tuple)) and base_dir:
            for tool_ref in tools_refs:
                if isinstance(tool_ref, str):
                    tool_path = base_dir / tool_ref if not Path(tool_ref).is_absolute() else Path(tool_ref)
                    if tool_path.exists() and tool_path.is_file():
                        try:
                            tool_data = json.loads(tool_path.read_text(encoding="utf-8"))
                            _validate_tool_definition(tool_data, str(tool_ref), declared_verbs)
                        except json.JSONDecodeError as exc:
                            raise ManifestValidationError(f"Tool file {tool_ref} has invalid JSON: {exc}") from exc
                elif isinstance(tool_ref, Mapping):
                    _validate_tool_definition(tool_ref, "inline_tool", declared_verbs)


def _validate_named_manifest_dict(raw: Mapping[str, Any], base_dir: Path | None = None) -> None:
    """Validate mhf.manifest/2 named manifest dictionary."""
    budget = raw.get("budget")
    if isinstance(budget, Mapping):
        _validate_budget(budget, "budget")

    guardrails = raw.get("guardrails")
    if isinstance(guardrails, Mapping):
        constraints = guardrails.get("constraints")
        if isinstance(constraints, Mapping):
            _validate_constraints(constraints, "guardrails.constraints")


def _validate_tool_definition(tool_data: Mapping[str, Any], label: str, declared_verbs: set[str]) -> None:
    """Validate a single tool definition object."""
    if not isinstance(tool_data, Mapping):
        raise ManifestValidationError(f"Tool {label} must be a JSON object")

    verb = tool_data.get("verb")
    name = tool_data.get("name")
    if not verb and not name:
        raise ManifestValidationError(f"Tool {label} must specify at least 'verb' or 'name'")

    if verb and declared_verbs and verb not in declared_verbs:
        raise ManifestValidationError(f"Tool {label} specifies verb {verb!r} which is not in declared capabilities")

    schema = tool_data.get("schema") or tool_data.get("parameters")
    if schema is not None:
        _validate_json_schema(schema, f"Tool {label} schema")


def validate_manifest_pack(pack: LoadedManifestPack) -> None:
    """Validate an already-loaded LoadedManifestPack."""
    validate_manifest_dict(pack.raw_manifest, base_dir=pack.pack_dir)
