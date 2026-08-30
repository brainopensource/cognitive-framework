from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

@dataclass(frozen=True)
class RepositoryProfile:
    name: str = "repository"
    docs_roots: tuple[str, ...] = ("docs", "documentation", "doc")
    source_roots: tuple[str, ...] = ("src", "lib", "packages", "apps")
    test_roots: tuple[str, ...] = ("tests", "test")
    schema_roots: tuple[str, ...] = ("schemas", "schema")
    generated_root: str = ".generated"
    cache_root: str = ".generated/lda-cache"
    document_extensions: tuple[str, ...] = (".md", ".mdx", ".rst")
    excluded_dirs: tuple[str, ...] = (
        ".git", ".venv", "node_modules", "dist", "dist-browser", "build", "site", ".site", "out",
        "__pycache__", ".tox", ".coverage", "coverage", ".pytest_cache", ".ruff_cache"
    )
    preferred_authority: tuple[str, ...] = ()
    secondary_authority: tuple[str, ...] = ()
    excluded_authority: tuple[str, ...] = ()
    validation_commands: tuple[tuple[str, ...], ...] = ()
    knowledge_adapter: str | None = None
    labels: dict[str, str] = field(default_factory=dict)

    def authority_score(self, value: str | None) -> int:
        if value in self.preferred_authority: return 80 - self.preferred_authority.index(value)
        if value in self.secondary_authority: return 30 - self.secondary_authority.index(value)
        if value in self.excluded_authority: return -40
        return 0

    def is_excluded(self, path: Path) -> bool:
        name = path.name.lower()
        if name.endswith((".min.js", ".min.css", ".bundle.js", ".map")):
            return True
        return any(
            part in self.excluded_dirs or
            part.startswith(("dist-", "build-", ".venv-", ".cache", "site-"))
            for part in path.parts
        )
