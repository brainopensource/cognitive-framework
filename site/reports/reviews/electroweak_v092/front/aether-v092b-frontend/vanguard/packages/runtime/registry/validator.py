"""Fail-closed validation for plugin metadata (packages authority)."""

from __future__ import annotations

import re
from typing import Any, Mapping

class ManifestValidationError(ValueError):
    pass

ISOLATION_TIERS = frozenset({"in_process", "subprocess", "container", "wasm"})
SPI_KINDS = frozenset({"IPlanner", "IMemoryEngine", "IToolkit", "IContextManager", "IEvaluationGate"})
_SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:[-+][0-9A-Za-z.-]+)?$")

def parse_semver(value: str) -> tuple[int, int, int]:
    match = _SEMVER.fullmatch(value.strip())
    if not match:
        raise ManifestValidationError(f"not a semver: {value!r}")
    return tuple(int(x) for x in match.groups())  # type: ignore[return-value]

def _version(value: str) -> tuple[int, int, int]:
    parts = value.strip().split(".")
    if len(parts) in (1, 2) and all(p.isdigit() for p in parts):
        return parse_semver(".".join((*parts, *("0",) * (3 - len(parts)))))
    return parse_semver(value)

def satisfies(version: str, spec: str) -> bool:
    v = _version(version)
    clauses = [x.strip() for x in spec.split(",") if x.strip()]
    if not clauses:
        raise ManifestValidationError("empty version spec")
    for clause in clauses:
        if clause.startswith("^"):
            base = _version(clause[1:])
            upper = (base[0] + 1, 0, 0) if base[0] else (0, base[1] + 1, 0)
            if not (base <= v < upper):
                return False
            continue
        matched_op = None
        for op in (">=", "<=", "==", ">", "<", "="):
            if clause.startswith(op):
                matched_op = op
                break
        if matched_op is not None:
            rhs = _version(clause[len(matched_op):].strip())
            op_fn = {
                ">=": v >= rhs,
                "<=": v <= rhs,
                ">": v > rhs,
                "<": v < rhs,
                "=": v == rhs,
                "==": v == rhs,
            }
            if not op_fn[matched_op]:
                return False
        else:
            rhs = _version(clause)
            if v != rhs:
                return False
    return True

def compatible(plugin_id: str, version: str, spec: str) -> bool:
    _ = plugin_id
    try:
        return satisfies(version, spec)
    except ManifestValidationError:
        return False

def validate_tool_schema(schema: Mapping[str, Any]) -> None:
    if schema.get("type") not in {None, "object", "string", "number", "integer", "boolean", "array", "null"}:
        raise ManifestValidationError("invalid tool schema type")
    props = schema.get("properties", {})
    if not isinstance(props, Mapping):
        raise ManifestValidationError("properties must be an object")
    required = schema.get("required", [])
    if not isinstance(required, list) or any(not isinstance(x, str) or x not in props for x in required):
        raise ManifestValidationError("required must name declared properties")
    for value in props.values():
        if not isinstance(value, Mapping):
            raise ManifestValidationError("property schema must be an object")
        validate_tool_schema(value)

def validate_plugin_manifest(manifest: Mapping[str, Any], *, hosted_spi_version: str = "1.0") -> None:
    allowed = {"api","id","version","provides","requires","isolation","capabilities","entry","tools","implementation","config","interfaces","profiles","ceiling"}
    unknown = set(manifest) - allowed
    if unknown:
        raise ManifestValidationError(f"unread authority-bearing fields: {sorted(unknown)}")
    if manifest.get("api") != "mhf.plugin/1":
        raise ManifestValidationError("api must be mhf.plugin/1")
    if not isinstance(manifest.get("id"), str) or not manifest["id"]:
        raise ManifestValidationError("id is required")
    parse_semver(str(manifest.get("version", "")))
    if manifest.get("isolation") not in ISOLATION_TIERS:
        raise ManifestValidationError("invalid isolation")
    provides = manifest.get("provides")
    if not isinstance(provides, list) or not provides:
        raise ManifestValidationError("provides must be non-empty")
    for item in provides:
        if not isinstance(item, Mapping) or item.get("spi") not in SPI_KINDS:
            raise ManifestValidationError("unknown SPI kind")
        if not satisfies(hosted_spi_version, str(item.get("spi_version", ""))):
            raise ManifestValidationError("incompatible SPI")
    for item in manifest.get("requires", []) or []:
        if not isinstance(item, Mapping) or not item.get("id") or not item.get("version"):
            raise ManifestValidationError("invalid requirement")
        satisfies("0.0.0", str(item["version"]))
    if not isinstance(manifest.get("entry"), str) or not manifest["entry"]:
        raise ManifestValidationError("entry is required")
    tools = manifest.get("tools", {})
    if not isinstance(tools, Mapping):
        raise ManifestValidationError("tools must be an object")
    for schema in tools.values():
        if not isinstance(schema, Mapping):
            raise ManifestValidationError("tool schema must be an object")
        validate_tool_schema(schema)

def validate_manifest(manifest: Mapping[str, Any], *, hosted_spi_version: str = "1.0") -> None:
    validate_plugin_manifest(manifest, hosted_spi_version=hosted_spi_version)
