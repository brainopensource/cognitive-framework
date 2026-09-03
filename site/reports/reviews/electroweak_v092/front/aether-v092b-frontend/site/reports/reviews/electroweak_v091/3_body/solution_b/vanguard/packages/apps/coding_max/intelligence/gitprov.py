"""Git-backed repository intelligence (`spec §8`).

Git answers a question no static analysis can: *what has actually been
changing*. Recency and churn are strong localisation priors -- a bug reported
today is far more likely to live in a file touched this month than in one
untouched for three years -- and they cost one subprocess call.

This provider is deliberately read-only. Effects on the repository go through
the existing `GitEnvironment` adapter under kernel authorisation
(`spec §40`); nothing here may write.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Sequence

from .protocol import (
    DependencyResult,
    Provenance,
    RepoScope,
    RepoSummary,
    SearchHit,
    SearchQuery,
    SearchResult,
    SymbolResult,
    TestMapping,
)

__all__ = ["GitProvider"]


class GitProvider:
    """Read-only git queries. Degrades to empty results outside a repo."""

    name = "git"

    def __init__(self, root: Path | str, *, timeout_s: float = 15.0) -> None:
        self._root = Path(root).resolve()
        self._timeout = timeout_s
        self._available: bool | None = None

    def available(self) -> bool:
        if self._available is None:
            result = self._git("rev-parse", "--is-inside-work-tree")
            self._available = result.strip() == "true"
        return self._available

    # -- git-specific surface used by the repo map and context scorer ----

    def head(self) -> str:
        return self._git("rev-parse", "HEAD").strip()

    def branch(self) -> str:
        return self._git("rev-parse", "--abbrev-ref", "HEAD").strip()

    def dirty(self) -> bool:
        return bool(self._git("status", "--porcelain").strip())

    def diff(self, *, staged: bool = False, paths: Sequence[str] = ()) -> str:
        args = ["diff", "--unified=3"]
        if staged:
            args.append("--cached")
        if paths:
            args += ["--", *paths]
        return self._git(*args)

    def changed_files(self) -> tuple[str, ...]:
        """Working-tree changes. This is the harness's own edit footprint."""
        lines = self._git("status", "--porcelain").splitlines()
        return tuple(line[3:].strip() for line in lines if len(line) > 3)

    def recent_files(self, limit: int = 60, since: str = "3.months") -> tuple[str, ...]:
        raw = self._git("log", f"--since={since}", "--name-only",
                        "--pretty=format:", "-n", "400")
        counts: dict[str, int] = {}
        for line in raw.splitlines():
            name = line.strip()
            if name:
                counts[name] = counts.get(name, 0) + 1
        ranked = sorted(counts.items(), key=lambda kv: -kv[1])
        return tuple(name for name, _ in ranked[:limit])

    def churn(self, path: str, since: str = "1.year") -> int:
        raw = self._git("log", f"--since={since}", "--oneline", "--", path)
        return len([line for line in raw.splitlines() if line.strip()])

    def blame_head(self, path: str, line: int) -> str:
        raw = self._git("blame", "-L", f"{line},{line}", "--porcelain", "--", path)
        return raw.splitlines()[0].split()[0] if raw.strip() else ""

    # -- RepositoryIntelligence surface ----------------------------------

    def search(self, query: SearchQuery) -> SearchResult:
        """`git grep`: index-aware, so it never walks ignored files."""
        started = time.monotonic()
        if not self.available():
            return SearchResult(provenance=Provenance(provider=self.name, confidence=0.0))
        args = ["grep", "--line-number", "--no-color",
                "-C", str(max(0, query.context_lines))]
        if not query.case_sensitive:
            args.append("--ignore-case")
        if not query.regex:
            args.append("--fixed-strings")
        else:
            args.append("--extended-regexp")
        args += ["-e", query.pattern]
        if query.glob:
            args += ["--", query.glob]

        raw = self._git(*args)
        hits: list[SearchHit] = []
        for line in raw.splitlines():
            parts = line.split(":", 2)
            if len(parts) != 3 or not parts[1].isdigit():
                continue
            hits.append(SearchHit(path=parts[0], line=int(parts[1]),
                                  text=parts[2][:500], score=1.0))
            if len(hits) >= query.max_results:
                break
        return SearchResult(
            hits=tuple(hits),
            truncated=len(hits) >= query.max_results,
            provenance=Provenance(
                provider=f"{self.name}:grep", confidence=0.65,
                elapsed_ms=int((time.monotonic() - started) * 1000),
            ),
        )

    def symbol(self, name: str) -> SymbolResult:
        """Git has no symbol table; the composite falls through to AST."""
        return SymbolResult(provenance=Provenance(provider=self.name, confidence=0.0))

    def dependencies(self, target: str) -> DependencyResult:
        """Co-change coupling: files that historically change *with* the target.

        This is a genuinely different dependency signal from imports. A file
        with no import edge to the target but a 0.8 co-change rate is usually
        an interface partner, and missing it is a common source of the
        `INCOMPLETE_PATCH` failure class.
        """
        if not self.available():
            return DependencyResult(target=target,
                                    provenance=Provenance(provider=self.name, confidence=0.0))
        started = time.monotonic()
        commits = [c for c in self._git(
            "log", "--pretty=format:%H", "-n", "120", "--", target).splitlines() if c]
        counts: dict[str, int] = {}
        for commit in commits:
            for name in self._git("show", "--name-only", "--pretty=format:",
                                  commit).splitlines():
                name = name.strip()
                if name and name != target:
                    counts[name] = counts.get(name, 0) + 1
        coupled = tuple(
            name for name, n in sorted(counts.items(), key=lambda kv: -kv[1])[:15]
            if n >= 2
        )
        return DependencyResult(
            target=target, imported_by=coupled,
            provenance=Provenance(
                provider=f"{self.name}:cochange", confidence=0.5,
                elapsed_ms=int((time.monotonic() - started) * 1000),
            ),
        )

    def tests_for(self, target: str) -> TestMapping:
        """Tests that historically changed alongside the target."""
        coupled = self.dependencies(target).imported_by
        tests = tuple(
            path for path in coupled
            if "test" in Path(path).parts or Path(path).name.startswith("test_")
        )
        return TestMapping(
            target=target, direct=tests,
            command_hint=f"pytest {' '.join(tests[:6])}" if tests else "",
            provenance=Provenance(provider=f"{self.name}:cochange",
                                  confidence=0.45 if tests else 0.0),
        )

    def summarize(self, scope: RepoScope) -> RepoSummary:
        return RepoSummary(provenance=Provenance(provider=self.name, confidence=0.0))

    # -- internals -------------------------------------------------------

    def _git(self, *args: str) -> str:
        try:
            proc = subprocess.run(
                ["git", "-C", str(self._root), *args],
                capture_output=True, text=True,
                timeout=self._timeout, check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return ""
        # `git grep` exits 1 on no matches; treat any nonzero as an empty
        # answer rather than an error, so a missing repo degrades silently.
        return proc.stdout if proc.returncode in (0, 1) else ""
