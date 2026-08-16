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
        """Construct translator from raw dict (supporting flat or nested format)."""
        if "to_canonical" in data and "to_wire" in data:
            to_canon = {str(k): str(v) for k, v in data["to_canonical"].items()}
            to_wire = {str(k): str(v) for k, v in data["to_wire"].items()}
            return cls(to_canon, to_wire)

        if "aliases" in data and isinstance(data["aliases"], Mapping):
            aliases = data["aliases"]
            to_canon = {str(k): str(v) for k, v in aliases.items() if isinstance(k, str) and isinstance(v, str)}
            to_wire = {}
            for k, v in to_canon.items():
                if v not in to_wire:
                    to_wire[v] = k
            return cls(to_canon, to_wire)

        # Flat dict format: model_name -> canonical_verb
        to_canon: dict[str, str] = {}
        to_wire: dict[str, str] = {}
        for key, val in data.items():
            if isinstance(key, str) and isinstance(val, str):
                to_canon[key] = val
                if val not in to_wire:
                    to_wire[val] = key

        return cls(to_canon, to_wire)

    def to_canonical(self, tool_name: str) -> str:
        """Translate model tool alias -> canonical verb."""
        return self.to_canonical_map.get(tool_name, tool_name)

    def to_wire(self, canonical_verb: str) -> str:
        """Translate canonical verb -> model tool alias."""
        return self.to_wire_map.get(canonical_verb, canonical_verb)


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
            pack_path = self.base_dir / pack_path

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

        # Load aliases.json if present
        aliases_file = pack_path / "aliases.json"
        if aliases_file.exists():
            try:
                with open(aliases_file, "r", encoding="utf-8") as f:
                    raw_aliases = json.load(f)
                translator = AliasTranslator.from_dict(raw_aliases)
            except Exception as exc:
                raise ManifestLoadError(f"Failed to parse {aliases_file}: {exc}") from exc
        else:
            # Default identity translator based on declared capabilities
            canon_map = {cap.verb: cap.verb for cap in parsed_manifest.capabilities}
            translator = AliasTranslator(canon_map, canon_map)

        # Read auxiliary component data (tools, system prompts, etc.)
        components_data: dict[str, list[Any]] = {}
        for role, paths in parsed_manifest.components:
            role_items: list[Any] = []
            for item_path_str in paths:
                item_path = self.base_dir / item_path_str
                if not item_path.exists():
                    item_path = pack_path / Path(item_path_str).name
                if item_path.exists():
                    if item_path.suffix == ".json":
                        try:
                            with open(item_path, "r", encoding="utf-8") as f:
                                role_items.append(json.load(f))
                        except Exception:
                            role_items.append(item_path.read_text(encoding="utf-8"))
                    else:
                        role_items.append(item_path.read_text(encoding="utf-8"))
            components_data[role] = role_items

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
