"""Repository profile: the single configuration point that adapts LDA to any project.

A profile is pure data (a TOML/YAML file or the built-in generic default).
Core modules must never hard-code project-specific paths, documentation
taxonomies, or authority vocabularies — everything project-specific belongs
in a profile. The AETHER integration is just one profile among many.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

# Generic, project-agnostic low-signal locator fragments. Project-specific
# noise patterns (benchmark runs, workspace dirs, answer banks) belong to
# project profiles, never to this default.
DEFAULT_LOW_SIGNAL_PATTERNS: tuple[str, ...] = (
    "__init__.py",
    "node_modules",
    "/dist",
    "/build/",
    "__pycache__",
    ".min.js",
    "/vendor/",
)


@dataclass(frozen=True)
class RepositoryProfile:
    name: str = "generic"
    docs_roots: tuple[str, ...] = ("docs", "documentation", "doc")
    source_roots: tuple[str, ...] = ("src", "lib", "packages")
    test_roots: tuple[str, ...] = ("tests", "test")
    schema_roots: tuple[str, ...] = ("schemas", "schema")
    generated_root: str = ".generated"
    cache_root: str = ".generated/lda-cache"
    document_extensions: tuple[str, ...] = (".md", ".mdx", ".rst", ".txt")
    code_extensions: tuple[str, ...] = (".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go", ".java", ".kt", ".cs", ".c", ".h", ".cpp", ".hpp", ".sh", ".rb", ".php", ".sql")
    excluded_dirs: tuple[str, ...] = (
        ".git", ".venv", "node_modules", "dist", "dist-browser", "build", "site", ".site", "out",
        "__pycache__", ".tox", ".coverage", "coverage", ".pytest_cache", ".ruff_cache"
    )
    preferred_authority: tuple[str, ...] = ()
    secondary_authority: tuple[str, ...] = ()
    excluded_authority: tuple[str, ...] = ()
    validation_commands: tuple[tuple[str, ...], ...] = ()
    knowledge_adapter: str | None = None
    # Directory tiers that a repository conventionally treats as non-canonical
    # even when document frontmatter omits an excluded authority value.
    non_canonical_prefixes: tuple[str, ...] = ()
    # Locator fragments that are never useful agent context (benchmark runs,
    # test fixtures, package shells, build artifacts).
    low_signal_patterns: tuple[str, ...] = DEFAULT_LOW_SIGNAL_PATTERNS
    # Bounded-growth invariant: global repo maps / rankings cap ranked symbols
    # at Top-K; fine-grained definitions remain available via targeted zoom
    # queries (lda symbol / lda callers / lda references).
    max_global_symbols: int = 500
    # Context packets must bind to the live workspace git HEAD and fail closed
    # (or recompile) on mismatch instead of serving stale facts.
    require_head_match: bool = True
    # Optional intent -> [docs_frac, code_frac, tests_frac] override for the
    # context packet budget mix (intents: bugfix/feature/research/test/explain).
    budget_mix: dict[str, Any] = field(default_factory=dict)
    labels: dict[str, str] = field(default_factory=dict)

    def authority_score(self, value: str | None) -> int:
        if value in self.preferred_authority: return 80 - self.preferred_authority.index(value)
        if value in self.secondary_authority: return 30 - self.secondary_authority.index(value)
        if value in self.excluded_authority: return -40
        return 0

    def is_excluded_authority(self, value: str | None) -> bool:
        return value is not None and value in self.excluded_authority

    def is_excluded(self, path: Path) -> bool:
        name = path.name.lower()
        if name.endswith((".min.js", ".min.css", ".bundle.js", ".map")):
            return True
        return any(
            part in self.excluded_dirs or
            part.startswith(("dist-", "build-", ".venv-", ".cache", "site-"))
            for part in path.parts
        )

    def is_low_signal(self, locator: str) -> bool:
        return any(pattern in locator for pattern in self.low_signal_patterns)

    def is_non_canonical_path(self, locator: str) -> bool:
        return any(locator.startswith(prefix) for prefix in self.non_canonical_prefixes)


def profile_from_mapping(mapping: Mapping[str, Any]) -> RepositoryProfile:
    """Build a profile from parsed TOML/YAML data (profiles are data, not code)."""
    known = set(getattr(RepositoryProfile, "__dataclass_fields__").keys())
    kwargs: dict[str, Any] = {}
    for key, value in dict(mapping).items():
        if key not in known or value is None:
            continue
        if isinstance(value, list):
            if key == "validation_commands":
                value = tuple(tuple(str(item) for item in command) for command in value)
            elif key == "labels":
                value = dict(value)
            else:
                value = tuple(str(item) for item in value)
        kwargs[key] = value
    return RepositoryProfile(**kwargs)
