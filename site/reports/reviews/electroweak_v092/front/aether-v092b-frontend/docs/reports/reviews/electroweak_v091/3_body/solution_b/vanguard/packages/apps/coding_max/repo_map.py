"""The compact repository map (`spec §10`).

`spec §10`: *"Avoid dumping the full repository. Use hierarchical detail."*
The map is a routing layer, not a copy of the tree. It answers "where would
this kind of change live" in a few hundred tokens, so the worker can spend its
context on the two or three files that actually matter.

`recently_relevant_files` is the highest-value field and the cheapest: git
churn is a strong localisation prior, and it is the one signal no amount of
static analysis can reconstruct.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of
from .intelligence.composite import CompositeIntelligence
from .intelligence.protocol import RepoScope

__all__ = ["RepositoryMap", "build_repository_map"]

#: Rendering ceiling. A map that grows without bound stops being a map.
_MAX_MODULES = 24
_MAX_RECENT = 20
_MAX_SYMBOLS = 24


@dataclass(frozen=True, slots=True)
class RepositoryMap:
    """`spec §10` shape, with the identity fields needed to cache it."""

    languages: tuple[str, ...] = ()
    modules: tuple[Mapping[str, Any], ...] = ()
    entrypoints: tuple[str, ...] = ()
    test_roots: tuple[str, ...] = ()
    build_system: str = ""
    important_symbols: tuple[Mapping[str, Any], ...] = ()
    dependencies: tuple[str, ...] = ()
    recently_relevant_files: tuple[str, ...] = ()
    file_count: int = 0
    head: str = ""
    branch: str = ""
    dirty: bool = False

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "languages": list(self.languages),
            "modules": [dict(m) for m in self.modules],
            "entrypoints": list(self.entrypoints),
            "testRoots": list(self.test_roots),
            "buildSystem": self.build_system,
            "importantSymbols": [dict(s) for s in self.important_symbols],
            "dependencies": list(self.dependencies),
            "recentlyRelevantFiles": list(self.recently_relevant_files),
            "fileCount": self.file_count,
            "head": self.head,
            "branch": self.branch,
            "dirty": self.dirty,
        }

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())

    def render(self, *, max_chars: int = 2400) -> str:
        """Token-bounded text for the ENVIRONMENT context layer.

        Written as terse structured prose rather than JSON: the same
        information costs roughly 40% fewer tokens without the quoting and
        bracket overhead, and models localise from it just as well.
        """
        lines: list[str] = ["# Repository map"]
        if self.branch or self.head:
            state = "dirty" if self.dirty else "clean"
            lines.append(f"branch={self.branch} head={self.head[:12]} tree={state}")
        if self.languages:
            lines.append(f"languages: {', '.join(self.languages[:6])}")
        if self.build_system:
            lines.append(f"build: {self.build_system}")
        lines.append(f"files: {self.file_count}")

        if self.modules:
            lines.append("\n## Modules (by size)")
            for module in self.modules[:_MAX_MODULES]:
                lines.append(f"  {module.get('path')}/  ({module.get('files')} files)")
        if self.test_roots:
            lines.append(f"\ntest roots: {', '.join(self.test_roots)}")
        if self.entrypoints:
            lines.append(f"entrypoints: {', '.join(self.entrypoints[:8])}")
        if self.recently_relevant_files:
            lines.append("\n## Recently changed (localisation prior)")
            for path in self.recently_relevant_files[:_MAX_RECENT]:
                lines.append(f"  {path}")
        if self.important_symbols:
            lines.append("\n## Notable symbols")
            for symbol in self.important_symbols[:_MAX_SYMBOLS]:
                lines.append(
                    f"  {symbol.get('name')} ({symbol.get('kind')}) "
                    f"— {symbol.get('path')}:{symbol.get('line')}"
                )
        if self.dependencies:
            lines.append(f"\nexternal deps: {', '.join(self.dependencies[:20])}")

        text = "\n".join(lines)
        if len(text) <= max_chars:
            return text
        # Truncate on a line boundary so the tail is never a half-path that
        # the model might read as a real file name.
        clipped = text[:max_chars].rsplit("\n", 1)[0]
        return clipped + "\n  … (map truncated)"


def build_repository_map(
    intelligence: CompositeIntelligence,
    *,
    focus_symbols: Sequence[str] = (),
    max_entries: int = 200,
) -> RepositoryMap:
    """Assemble the map from whatever providers are live.

    Every field degrades independently. A repository with no git history still
    gets languages, modules, and test roots; it simply loses the churn prior.
    """
    summary = intelligence.summarize(RepoScope(max_entries=max_entries))
    git = intelligence.git

    recent: tuple[str, ...] = ()
    head = branch = ""
    dirty = False
    if git.available():
        head, branch = git.head(), git.branch()
        dirty = git.dirty()
        # Working-tree changes rank above historical churn: they are this
        # run's own edits, and the worker almost always needs to see them.
        changed = git.changed_files()
        recent = tuple(dict.fromkeys(changed + git.recent_files(limit=_MAX_RECENT)))

    symbols: list[Mapping[str, Any]] = []
    for name in focus_symbols[:8]:
        for definition in intelligence.symbol(name).definitions[:3]:
            symbols.append({
                "name": definition.name, "kind": definition.kind.value,
                "path": definition.path, "line": definition.line,
                "signature": definition.signature,
            })

    return RepositoryMap(
        languages=summary.languages,
        modules=summary.modules[:_MAX_MODULES],
        entrypoints=summary.entrypoints,
        test_roots=summary.test_roots,
        build_system=summary.build_system,
        important_symbols=tuple(symbols[:_MAX_SYMBOLS]),
        dependencies=_declared_dependencies(intelligence.root),
        recently_relevant_files=recent[:_MAX_RECENT],
        file_count=summary.file_count,
        head=head, branch=branch, dirty=dirty,
    )


def _declared_dependencies(root: Path) -> tuple[str, ...]:
    """External dependencies as *declared*, not as resolved.

    Reading the manifest rather than the installed environment is deliberate:
    the harness needs to know what the project claims it needs, which is what
    a dependency task will edit. The installed set is a separate question and
    belongs to verification.
    """
    names: list[str] = []
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        try:
            import tomllib

            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            project = data.get("project", {})
            for entry in project.get("dependencies", []) or []:
                names.append(str(entry).split("[")[0].split(">")[0]
                             .split("<")[0].split("=")[0].strip())
        except Exception:  # noqa: BLE001 - a malformed manifest is not fatal
            pass
    package_json = root / "package.json"
    if package_json.is_file():
        try:
            import json

            data = json.loads(package_json.read_text(encoding="utf-8"))
            names.extend(sorted((data.get("dependencies") or {}).keys()))
        except Exception:  # noqa: BLE001
            pass
    return tuple(dict.fromkeys(name for name in names if name))
