"""Atlas context: repository-rooted configuration with explicit profile selection."""
from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional

from .gitinfo import current_head_sha
from .paths import find_root
from .profile import RepositoryProfile
from .profile_loader import resolve_profile


def _optional_yaml():
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        return None
    return yaml


def _simple_yaml_fallback(text: str) -> dict[str, Any]:
    """Lightweight fallback parser for basic YAML when PyYAML is not installed."""
    res: dict[str, Any] = {}
    curr_dict: dict[str, Any] = res
    curr_key: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            parts = line.split(":", 1)
            k = parts[0].strip()
            v = parts[1].strip()
            if not v:
                curr_key = k
                res[k] = {}
                curr_dict = res[k]
            else:
                val: Any
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    val = v[1:-1]
                elif v.lower() == "true":
                    val = True
                elif v.lower() == "false":
                    val = False
                elif v.isdigit():
                    val = int(v)
                else:
                    val = v
                if curr_key and raw_line.startswith(("  ", "\t")):
                    curr_dict[k] = val
                else:
                    curr_key = None
                    curr_dict = res
                    res[k] = val
    return res


def load_repo_config(base: Path) -> Mapping[str, Any]:
    """Load lda.yaml / lda.yml / lda.toml from the repository root (empty if absent)."""
    config_yaml = base / "lda.yaml"
    config_yml = base / "lda.yml"
    config_toml = base / "lda.toml"
    if config_yaml.is_file() or config_yml.is_file():
        path = config_yaml if config_yaml.is_file() else config_yml
        yaml = _optional_yaml()
        if yaml is None:
            # Zero-dependency fallback for simple lda.yaml files
            return _simple_yaml_fallback(path.read_text(encoding="utf-8"))
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if config_toml.is_file():
        with config_toml.open("rb") as handle:
            return tomllib.load(handle)
    return {}


@dataclass(frozen=True)
class AtlasContext:
    root: Path
    knowledge: Path
    cache: Path
    include_research: bool = False
    profile: RepositoryProfile = RepositoryProfile()
    head_sha: Optional[str] = None

    @classmethod
    def discover(cls, root: Path | None = None, include_research: bool = False) -> "AtlasContext":
        base = find_root(root)
        data = load_repo_config(base)

        # Explicit profile selection ONLY (lda.yaml 'profile:' / $LDA_PROFILE /
        # generic default). Never inferred from project artifacts: that
        # side-channel made authority metadata silently wrong for any project
        # that happened to contain a similarly-named generated directory.
        profile = resolve_profile(base, data)

        project = data.get("project", {})
        paths = data.get("paths", {})
        auth = data.get("authority", {})
        knowledge = data.get("knowledge", {})

        # Default docs_roots resolution: check if docs/ exists, else documentation/
        default_docs = profile.docs_roots
        if (base / "docs").exists():
            default_docs = ("docs",)
        elif (base / "documentation").exists():
            default_docs = ("documentation",)

        configured_docs = tuple(paths.get("docs", default_docs))
        configured_source = tuple(paths.get("source", profile.source_roots))

        selected = RepositoryProfile(
            name=project.get("name", profile.name),
            docs_roots=configured_docs,
            source_roots=configured_source,
            test_roots=tuple(paths.get("tests", profile.test_roots)),
            schema_roots=tuple(paths.get("schemas", profile.schema_roots)),
            generated_root=paths.get("generated", profile.generated_root),
            cache_root=paths.get("cache", profile.cache_root),
            excluded_dirs=tuple(profile.excluded_dirs),
            document_extensions=tuple(paths.get("document_extensions", profile.document_extensions)),
            code_extensions=tuple(paths.get("code_extensions", profile.code_extensions)),
            preferred_authority=tuple(auth.get("preferred", profile.preferred_authority)),
            secondary_authority=tuple(auth.get("secondary", profile.secondary_authority)),
            excluded_authority=tuple(auth.get("excluded_by_default", profile.excluded_authority)),
            knowledge_adapter=knowledge.get("adapter", profile.knowledge_adapter),
            validation_commands=profile.validation_commands,
            non_canonical_prefixes=tuple(
                paths.get("non_canonical_prefixes", profile.non_canonical_prefixes)
            ),
            low_signal_patterns=profile.low_signal_patterns,
            max_global_symbols=int(paths.get("max_global_symbols", profile.max_global_symbols)),
            require_head_match=bool(paths.get("require_head_match", profile.require_head_match)),
            labels=dict(profile.labels),
        )
        return cls(
            base,
            base / selected.generated_root / "knowledge",
            base / selected.cache_root,
            include_research,
            selected,
            current_head_sha(base),
        )
