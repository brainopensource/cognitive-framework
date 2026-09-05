"""Change Surface and Multi-File Dependency Graph Indexer.

Analyzes tracebacks, task briefs, and import graphs to estimate the required multi-file
change surface for a given bug or feature.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class ChangeSurfaceEstimate:
    """Estimated set of files requiring inspection or modification."""

    primary_files: tuple[str, ...]
    related_files: tuple[str, ...]
    test_files: tuple[str, ...]
    coverage_ratio: float = 0.0
    reasons: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    truncated: bool = False


class ChangeSurfaceEstimator:
    """Extracts implicated file paths from tracebacks, briefs, and import references."""

    PYTHON_FILE_REGEX = re.compile(r"([a-zA-Z0-9_/-]+\.py)", re.IGNORECASE)
    TRACEBACK_LINE_REGEX = re.compile(r'File "([^"]+\.py)", line \d+', re.IGNORECASE)

    def estimate(
        self,
        brief: str,
        workspace_files: Sequence[str] = (),
        traceback_text: str = "",
        modified_files: Sequence[str] = (),
        implicated_files: Mapping[str, Sequence[str]] | None = None,
        dependency_edges: Sequence[tuple[str, str]] = (),
        test_associations: Sequence[tuple[str, str]] = (),
        max_related_files: int = 128,
    ) -> ChangeSurfaceEstimate:
        candidates: set[str] = set()
        test_candidates: set[str] = set()
        reasons: dict[str, set[str]] = {}

        def add(path: str, reason: str) -> None:
            reasons.setdefault(path, set()).add(reason)

        # 1. Extract from traceback
        for match in self.TRACEBACK_LINE_REGEX.finditer(traceback_text):
            path = match.group(1).strip()
            if not path.startswith("/usr/") and not path.startswith("lib/"):
                candidates.add(path)
                add(path, "traceback")

        # 2. Extract from brief text
        for match in self.PYTHON_FILE_REGEX.finditer(brief):
            path = match.group(1).strip()
            if "test" in path.lower():
                test_candidates.add(path)
                add(path, "brief_test_path")
            else:
                candidates.add(path)
                add(path, "brief_path")

        for path, file_reasons in (implicated_files or {}).items():
            if "test" in path.lower():
                test_candidates.add(path)
            else:
                candidates.add(path)
            for reason in file_reasons:
                add(path, reason)

        # Filter against actual workspace files if available
        if workspace_files:
            ws_set = set(workspace_files)
            primary = tuple(sorted(c for c in candidates if c in ws_set or any(c.endswith(f) for f in ws_set)))
            tests = tuple(sorted(t for t in test_candidates if t in ws_set or any(t.endswith(f) for f in ws_set)))
        else:
            primary = tuple(sorted(candidates))
            tests = tuple(sorted(test_candidates))

        # Related files heuristic (matching directory prefix)
        related: set[str] = set()
        for p in primary:
            dir_prefix = p.rsplit("/", 1)[0] if "/" in p else ""
            if dir_prefix and workspace_files:
                for f in workspace_files:
                    if f.startswith(dir_prefix) and f != p and not f.endswith("_test.py") and "test" not in f:
                        related.add(f)
        for source, target in dependency_edges:
            if source in primary:
                related.add(target)
                add(target, f"dependency_of:{source}")
            if target in primary:
                related.add(source)
                add(source, f"dependent_of:{target}")
        for test_path, source_path in test_associations:
            if source_path in primary or source_path in related:
                test_candidates.add(test_path)
                add(test_path, f"test_for:{source_path}")
        if workspace_files:
            tests = tuple(sorted(t for t in test_candidates if t in ws_set or any(t.endswith(f) for f in ws_set)))
        else:
            tests = tuple(sorted(test_candidates))
        related.difference_update(primary)
        related_truncated = len(related) > max_related_files
        related = set(sorted(related)[:max_related_files])

        # Calculate coverage ratio
        mod_set = set(modified_files)
        touched = sum(1 for p in primary if p in mod_set or any(m.endswith(p) for m in mod_set))
        coverage = touched / len(primary) if primary else 0.0

        return ChangeSurfaceEstimate(
            primary_files=primary,
            related_files=tuple(sorted(related)),
            test_files=tests,
            coverage_ratio=coverage,
            reasons={path: tuple(sorted(reasons.get(path, ()))) for path in sorted(set(primary) | related | set(tests))},
            truncated=related_truncated,
        )
