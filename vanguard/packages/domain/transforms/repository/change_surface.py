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
    ) -> ChangeSurfaceEstimate:
        candidates: set[str] = set()
        test_candidates: set[str] = set()

        # 1. Extract from traceback
        for match in self.TRACEBACK_LINE_REGEX.finditer(traceback_text):
            path = match.group(1).strip()
            if not path.startswith("/usr/") and not path.startswith("lib/"):
                candidates.add(path)

        # 2. Extract from brief text
        for match in self.PYTHON_FILE_REGEX.finditer(brief):
            path = match.group(1).strip()
            if "test" in path.lower():
                test_candidates.add(path)
            else:
                candidates.add(path)

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

        # Calculate coverage ratio
        mod_set = set(modified_files)
        touched = sum(1 for p in primary if p in mod_set or any(m.endswith(p) for m in mod_set))
        coverage = touched / len(primary) if primary else 1.0

        return ChangeSurfaceEstimate(
            primary_files=primary,
            related_files=tuple(sorted(related)),
            test_files=tests,
            coverage_ratio=coverage,
        )
