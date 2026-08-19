"""SemVer caret-compat and JSON Schema checks for plugin manifests (SPEC §2.1)."""

from __future__ import annotations

import re
from typing import Any, Mapping

__all__ = [
    "ManifestValidationError",
    "compatible",
    "parse_semver",
    "satisfies",
    "validate_manifest",
    "validate_tool_schema",
]

_ISOLATION = frozenset({"in_process", "subprocess", "container", "wasm"})
_SPI_NAMES = frozenset(
    {"IPlanner", "IMemoryEngine", "IToolkit", "IContextManager", "IEvaluationGate"}
)
_JSON_TYPES = frozenset({"object", "string", "number", "integer", "boolean", "array", "null"})
_VERSION = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:[-+][0-9A-Za-z.-]+)?$")


class ManifestValidationError(ValueError):
    pass


def parse_semver(value: str) -> tuple[int, int, int]:
    match = _VERSION.match(value.strip())
    if match is None:
        raise ManifestValidationError(f"not a semver: {value!r}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def satisfies(version: str, spec: str) -> bool:
    parsed = parse_semver(_coerce_version(version))
    clauses = [clause.strip() for clause in spec.split(",") if clause.strip()]
    if not clauses:
        raise ManifestValidationError(f"empty version spec: {spec!r}")
    return all(_clause(parsed, clause) for clause in clauses)


def compatible(plugin_id: str, version: str, spec: str) -> bool:
    _ = plugin_id
    try:
        return satisfies(version, spec)
    except ManifestValidationError:
        return False


def validate_tool_schema(schema: Mapping[str, Any]) -> None:
    _schema(schema, path="schema")


def validate_manifest(
    manifest: Mapping[str, Any],
    *,
    hosted_spi_version: str = "1.0",
) -> None:
    if manifest.get("api") != "mhf.plugin/1":
        raise ManifestValidationError("api must be mhf.plugin/1")
    if not isinstance(manifest.get("id"), str) or not manifest["id"]:
        raise ManifestValidationError("id is required")
    parse_semver(str(manifest.get("version", "")))
    isolation = manifest.get("isolation")
    if isolation not in _ISOLATION:
        raise ManifestValidationError(f"unknown isolation {isolation!r}")
    provides = manifest.get("provides")
    if not isinstance(provides, list) or not provides:
        raise ManifestValidationError("provides must be a non-empty list")
    hosted = _coerce_version(hosted_spi_version)
    for item in provides:
        if not isinstance(item, Mapping):
            raise ManifestValidationError("provides entries must be objects")
        spi = item.get("spi")
        if spi not in _SPI_NAMES:
            raise ManifestValidationError(f"unknown spi {spi!r}")
        range_spec = str(item.get("spi_version", ""))
        if not satisfies(hosted, range_spec):
            raise ManifestValidationError(
                f"hosted SPI {hosted_spi_version} does not satisfy {range_spec}"
            )
    requires = manifest.get("requires") or []
    if not isinstance(requires, list):
        raise ManifestValidationError("requires must be a list")
    for item in requires:
        if not isinstance(item, Mapping) or "id" not in item or "version" not in item:
            raise ManifestValidationError("requires entries need id and version")
        _parse_spec(str(item["version"]))
    capabilities = manifest.get("capabilities") or []
    if not isinstance(capabilities, list):
        raise ManifestValidationError("capabilities must be a list")
    for item in capabilities:
        if not isinstance(item, Mapping) or "verb" not in item:
            raise ManifestValidationError("capability must name a verb")
    if not isinstance(manifest.get("entry"), str) or not manifest["entry"]:
        raise ManifestValidationError("entry is required")
    tools = manifest.get("tools") or {}
    if not isinstance(tools, Mapping):
        raise ManifestValidationError("tools must be an object")
    for name, schema in tools.items():
        if not isinstance(schema, Mapping):
            raise ManifestValidationError(f"tool {name!r} schema must be an object")
        validate_tool_schema(schema)


def _coerce_version(value: str) -> str:
    text = value.strip()
    if _VERSION.match(text):
        return text
    parts = text.split(".")
    if len(parts) == 1 and parts[0].isdigit():
        return f"{parts[0]}.0.0"
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        return f"{parts[0]}.{parts[1]}.0"
    raise ManifestValidationError(f"not a semver: {value!r}")


def _parse_spec(spec: str) -> None:
    for clause in spec.split(","):
        _clause((0, 0, 0), clause.strip(), validate_only=True)


def _clause(
    version: tuple[int, int, int],
    clause: str,
    *,
    validate_only: bool = False,
) -> bool:
    text = clause.strip()
    if not text:
        raise ManifestValidationError("empty version clause")
    if text.startswith("^"):
        base = parse_semver(_coerce_version(text[1:]))
        if validate_only:
            return True
        upper = _caret_upper(base)
        return base <= version < upper
    for op in (">=", "<=", ">", "<", "==", "="):
        if text.startswith(op):
            rhs = parse_semver(_coerce_version(text[len(op) :].strip()))
            if validate_only:
                return True
            if op in {"=", "=="}:
                return version == rhs
            if op == ">=":
                return version >= rhs
            if op == "<=":
                return version <= rhs
            if op == ">":
                return version > rhs
            return version < rhs
    parse_semver(_coerce_version(text))
    if validate_only:
        return True
    return version == parse_semver(_coerce_version(text))


def _caret_upper(base: tuple[int, int, int]) -> tuple[int, int, int]:
    major, minor, patch = base
    if major > 0:
        return (major + 1, 0, 0)
    if minor > 0:
        return (0, minor + 1, 0)
    return (0, 0, patch + 1)


def _schema(schema: Mapping[str, Any], *, path: str) -> None:
    declared = schema.get("type")
    if declared is not None:
        if isinstance(declared, list):
            if any(item not in _JSON_TYPES for item in declared):
                raise ManifestValidationError(f"{path}: invalid type")
        elif declared not in _JSON_TYPES:
            raise ManifestValidationError(f"{path}: invalid type {declared!r}")
    properties = schema.get("properties")
    if properties is not None:
        if not isinstance(properties, Mapping):
            raise ManifestValidationError(f"{path}: properties must be an object")
        for name, sub in properties.items():
            if not isinstance(sub, Mapping):
                raise ManifestValidationError(f"{path}.{name}: schema must be object")
            _schema(sub, path=f"{path}.{name}")
    required = schema.get("required")
    if required is not None:
        if not isinstance(required, list) or any(not isinstance(item, str) for item in required):
            raise ManifestValidationError(f"{path}: required must be a string list")
        names = set(properties or {})
        missing = [item for item in required if item not in names]
        if missing:
            raise ManifestValidationError(f"{path}: required {missing} not in properties")
    additional = schema.get("additionalProperties")
    if additional is not None and not isinstance(additional, (bool, Mapping)):
        raise ManifestValidationError(f"{path}: additionalProperties must be bool or schema")
    if isinstance(additional, Mapping):
        _schema(additional, path=f"{path}.additionalProperties")
    items = schema.get("items")
    if isinstance(items, Mapping):
        _schema(items, path=f"{path}.items")
