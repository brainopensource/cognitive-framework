from dataclasses import dataclass
from pathlib import Path
import tomllib
try:
    import yaml
except ImportError:
    yaml = None

from .paths import find_root
from .profile import RepositoryProfile
from ..profiles.aether import profile as aether_profile

@dataclass(frozen=True)
class AtlasContext:
    root: Path
    knowledge: Path
    cache: Path
    include_research: bool = False
    profile: RepositoryProfile = RepositoryProfile()

    @classmethod
    def discover(cls, root: Path | None = None, include_research: bool = False) -> "AtlasContext":
        base = find_root(root)
        data = {}
        
        # Load configuration from lda.yaml, lda.yml, or lda.toml
        config_yaml = base / "lda.yaml"
        config_yml = base / "lda.yml"
        config_toml = base / "lda.toml"
        
        if config_yaml.exists() and yaml:
            with config_yaml.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        elif config_yml.exists() and yaml:
            with config_yml.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        elif config_toml.exists():
            with config_toml.open("rb") as handle:
                data = tomllib.load(handle)

        selected = aether_profile() if (base / ".generated/knowledge/catalog.jsonl").exists() else RepositoryProfile()
        project = data.get("project", {})
        paths = data.get("paths", {})
        auth = data.get("authority", {})

        # Default docs_roots resolution: check if docs/ exists, else documentation/
        default_docs = selected.docs_roots
        if (base / "docs").exists():
            default_docs = ("docs",)
        elif (base / "documentation").exists():
            default_docs = ("documentation",)

        configured_docs = tuple(paths.get("docs", default_docs))
        configured_source = tuple(paths.get("source", ("vanguard", "tools", "lab", "src", "packages")))

        selected = RepositoryProfile(
            name=project.get("name", selected.name),
            docs_roots=configured_docs,
            source_roots=configured_source,
            test_roots=tuple(paths.get("tests", selected.test_roots)),
            schema_roots=tuple(paths.get("schemas", selected.schema_roots)),
            generated_root=paths.get("generated", selected.generated_root),
            cache_root=paths.get("cache", selected.cache_root),
            preferred_authority=tuple(auth.get("preferred", selected.preferred_authority)),
            secondary_authority=tuple(auth.get("secondary", selected.secondary_authority)),
            excluded_authority=tuple(auth.get("excluded_by_default", selected.excluded_authority)),
            knowledge_adapter=selected.knowledge_adapter,
            validation_commands=selected.validation_commands,
        )
        return cls(base, base / selected.generated_root / "knowledge", base / selected.cache_root, include_research, selected)
