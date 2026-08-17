"""Declarative Manifest Loader & Alias Engine (REQ-HARN-001, GTS-13C §7.3).

Parses pure-data harness manifests and provides bidirectional tool verb translation
between model-specific tool aliases and canonical kernel verbs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from ...domain.artifacts.manifest import HarnessManifest, parse_manifest

try:
    import jsonschema  # type: ignore
    _HAS_JSONSCHEMA = True
except ImportError:
    _HAS_JSONSCHEMA = False

SCHEMA_PATH = Path(__file__).resolve().parents[3] / "schemas" / "v4" / "harness-manifest.schema.json"


class ManifestLoadError(ValueError):
    """Error loading or validating a manifest pack."""
    pass


# Registered component consumers for fail-closed manifest composition (S7-B-02 / S8-B-02..04)
REGISTERED_COMPONENT_CONSUMERS: Mapping[str, str] = {
    "system_prompt": "runtime.root:system_core",
    "tools": "runtime.root:tool_schemas",
    "context_policy": "vanguard.packages.agency.context.compaction",
    "routing_policy": "vanguard.packages.adapters.models.routing",
    "approval_policy": "vanguard.packages.runtime.governance.approvals",
}


@dataclass(frozen=True, slots=True)
class AliasTranslator:
    """Bidirectional verb translator for a manifest pack.

    Translates between model-visible tool names (e.g., 'Read', 'view_file', 'bash')
    and canonical kernel verbs (e.g., 'fs.read', 'patch.apply', 'proc.exec').
    """

    to_canonical_map: Mapping[str, str]
    to_wire_map: Mapping[str, str]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "AliasTranslator":
        """Construct translator from flat dict format: model_alias -> canonical_verb."""
        if not isinstance(data, Mapping):
            raise ManifestLoadError("aliases must be a JSON object mapping alias names to canonical verbs")
        if "to_canonical" in data or "aliases" in data:
            raise ManifestLoadError("aliases must use canonical flat shape {'alias': 'verb'}")

        to_canon: dict[str, str] = {}
        to_wire: dict[str, str] = {}
        for key, val in data.items():
            if not isinstance(key, str) or not isinstance(val, str):
                raise ManifestLoadError(f"alias mapping entries must be str -> str, got {key!r}: {val!r}")
            to_canon[key] = val
            if val not in to_wire:
                to_wire[val] = key

        return cls(to_canon, to_wire)

    def to_canonical(self, tool_name: str) -> str:
        """Translate model tool alias -> canonical verb."""
        if tool_name not in self.to_canonical_map:
            raise KeyError(f"Unknown tool alias: {tool_name!r}")
        return self.to_canonical_map[tool_name]

    def to_wire(self, canonical_verb: str) -> str:
        """Translate canonical verb -> model tool alias."""
        if canonical_verb not in self.to_wire_map:
            raise KeyError(f"Unknown canonical verb: {canonical_verb!r}")
        return self.to_wire_map[canonical_verb]


@dataclass(frozen=True, slots=True)
class LoadedManifestPack:
    """A fully loaded manifest pack containing the parsed manifest and alias translator."""

    manifest: HarnessManifest
    raw_manifest: Mapping[str, Any]
    translator: AliasTranslator
    pack_dir: Path
    components_data: Mapping[str, Sequence[Mapping[str, Any] | str]]

    @property
    def name(self) -> str:
        return self.manifest.harness

    def to_canonical(self, tool_name: str) -> str:
        """Helper delegation to translator."""
        return self.translator.to_canonical(tool_name)

    def to_wire(self, canonical_verb: str) -> str:
        """Helper delegation to translator."""
        return self.translator.to_wire(canonical_verb)


class ManifestLoader:
    """Dynamic manifest pack loader and validator."""

    def __init__(self, manifests_base_dir: str | Path | None = None) -> None:
        if manifests_base_dir is None:
            manifests_base_dir = Path(__file__).resolve().parent
        self.base_dir = Path(manifests_base_dir).resolve()
        self._schema_cache: dict[str, Any] | None = None

    def _load_schema(self) -> dict[str, Any] | None:
        if self._schema_cache is None and SCHEMA_PATH.exists():
            try:
                with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                    self._schema_cache = json.load(f)
            except Exception:
                self._schema_cache = None
        return self._schema_cache

    def validate_schema(self, raw_manifest: Mapping[str, Any]) -> None:
        """Validate raw manifest dict against harness-manifest.schema.json if available."""
        schema = self._load_schema()
        if _HAS_JSONSCHEMA and schema:
            try:
                jsonschema.validate(instance=dict(raw_manifest), schema=schema)
            except Exception as exc:
                raise ManifestLoadError(f"Schema validation failed: {exc}") from exc

    def load_pack(self, pack_name_or_path: str | Path, validate: bool = True) -> LoadedManifestPack:
        """Load a manifest pack by name (relative to base_dir) or explicit Path."""
        pack_path = Path(pack_name_or_path)
        if not pack_path.is_absolute():
            if pack_path.resolve().is_dir() and (pack_path.resolve() / "manifest.json").exists():
                pack_path = pack_path.resolve()
            elif (self.base_dir / pack_path).exists():
                pack_path = (self.base_dir / pack_path).resolve()
            else:
                pack_path = (self.base_dir / pack_path).resolve()

        if not pack_path.exists() or not pack_path.is_dir():
            raise ManifestLoadError(f"Manifest pack directory does not exist: {pack_path}")

        manifest_file = pack_path / "manifest.json"
        if not manifest_file.exists():
            raise ManifestLoadError(f"manifest.json missing in pack: {pack_path}")

        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                raw_manifest = json.load(f)
        except Exception as exc:
            raise ManifestLoadError(f"Failed to parse JSON in {manifest_file}: {exc}") from exc

        if validate:
            self.validate_schema(raw_manifest)

        # Parse using domain manifest parser
        try:
            parsed_manifest = parse_manifest(raw_manifest)
        except Exception as exc:
            raise ManifestLoadError(f"Invalid harness manifest in {manifest_file}: {exc}") from exc

        declared_verbs = {cap.verb for cap in parsed_manifest.capabilities}

        # Load aliases.json if present
        aliases_file = pack_path / "aliases.json"
        if aliases_file.exists():
            try:
                with open(aliases_file, "r", encoding="utf-8") as f:
                    raw_aliases = json.load(f)
                translator = AliasTranslator.from_dict(raw_aliases)
            except Exception as exc:
                raise ManifestLoadError(f"Failed to parse {aliases_file}: {exc}") from exc

            # Fail-closed: every alias target must be a declared capability verb
            for alias_name, target_verb in translator.to_canonical_map.items():
                if target_verb not in declared_verbs:
                    raise ManifestLoadError(
                        f"Alias target {target_verb!r} for alias {alias_name!r} is not a declared capability verb: {sorted(declared_verbs)}"
                    )
        else:
            # Default identity translator based on declared capabilities
            canon_map = {cap.verb: cap.verb for cap in parsed_manifest.capabilities}
            translator = AliasTranslator(canon_map, canon_map)

        # Read auxiliary component data (tools, system prompts, etc.)
        components_data: dict[str, list[Any]] = {}
        for role, paths in parsed_manifest.components:
            # Fail-closed: every component role must have a registered consumer (S7-B-02)
            if role not in REGISTERED_COMPONENT_CONSUMERS:
                raise ManifestLoadError(
                    f"Unconsumed component role {role!r} has no registered consumer; unread components are forbidden at composition"
                )

            role_items: list[Any] = []
            for item_path_str in paths:
                item_path = self.base_dir / item_path_str
                if not item_path.exists():
                    item_path = pack_path / item_path_str
                if not item_path.exists():
                    item_path = pack_path / Path(item_path_str).name
                if not item_path.exists():
                    raise ManifestLoadError(f"Component file does not exist: {item_path_str}")

                if item_path.suffix == ".json":
                    try:
                        with open(item_path, "r", encoding="utf-8") as f:
                            role_items.append(json.load(f))
                    except Exception as exc:
                        raise ManifestLoadError(f"Failed to parse component JSON in {item_path}: {exc}") from exc
                else:
                    role_items.append(item_path.read_text(encoding="utf-8"))
            components_data[role] = role_items

        # Fail-closed: validate tool schemas against declared aliases union capabilities
        valid_tool_names = set(translator.to_canonical_map.keys()) | declared_verbs
        for tool_schema in components_data.get("tools", []):
            if isinstance(tool_schema, Mapping):
                func = tool_schema.get("function")
                source = func if isinstance(func, Mapping) else tool_schema
                s_name = source.get("name") if isinstance(source, Mapping) else None
                s_verb = tool_schema.get("verb")

                verb_resolved = bool(s_verb and s_verb in declared_verbs)
                name_resolved = bool(s_name and (s_name in valid_tool_names or s_name in declared_verbs))

                if s_verb and not verb_resolved:
                    raise ManifestLoadError(
                        f"Tool schema verb {s_verb!r} is not a declared capability verb: {sorted(declared_verbs)}"
                    )
                if s_name and not name_resolved and not verb_resolved:
                    raise ManifestLoadError(
                        f"Tool schema name {s_name!r} is neither a declared verb nor a known alias: {sorted(valid_tool_names)}"
                    )
                if not s_name and not s_verb:
                    raise ManifestLoadError("Tool schema must declare a 'name' or 'verb'")

        return LoadedManifestPack(
            manifest=parsed_manifest,
            raw_manifest=raw_manifest,
            translator=translator,
            pack_dir=pack_path,
            components_data=components_data,
        )

    def list_available_packs(self) -> tuple[str, ...]:
        """List names of all subdirectories containing manifest.json."""
        packs: list[str] = []
        if self.base_dir.exists():
            for child in sorted(self.base_dir.iterdir()):
                if child.is_dir() and (child / "manifest.json").exists():
                    packs.append(child.name)
        return tuple(packs)
