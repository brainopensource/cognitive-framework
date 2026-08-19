#!/usr/bin/env python3
"""Canonical repository-root-relative path map (S6B-GOV-001).

Every governance, contract, baseline, audit and CI helper must resolve
locations through this module. Callers must not scatter replacement
literals for the documentation move:

    docs/v4            -> docs/main_v4
    docs/sprintN       -> docs/scrum/sprints/sprintN
    docs/agile/sprintN -> docs/scrum/sprints/sprintN
    docs/review        -> docs/reviews
    docs/development   -> docs/scrum/development_guides

Commands are independent of the process working directory: ``repo_root()``
walks from this file (and, if needed, from cwd) until the live layout is
found. A missing file is never treated as satisfied evidence.

S7-A-07: the `docs/agile` -> `docs/scrum` restructure moved every sprint
directory under `docs/scrum/sprints/`. The pre-restructure layout is kept as a
resolution fallback only; it is never the answer on a live tree.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

CANONICAL = {
    "docs_main_v4": "docs/main_v4",
    "docs_scrum": "docs/scrum",
    "docs_sprints": "docs/scrum/sprints",
    "docs_reviews": "docs/reviews",
    "docs_development_guides": "docs/scrum/development_guides",
}

# Pre-restructure layout, retained for resolution fallback only.
LEGACY = {
    "docs_scrum": "docs/agile",
    "docs_sprints": "docs/agile",
    "docs_development_guides": "docs/development_guides",
}

# Live prefixes that must not be flagged as stale.
LIVE_PREFIXES = tuple(CANONICAL.values()) + (
    "docs/agile/",
    "docs/main_v4/",
    "docs/reviews/",
    "docs/scrum/",
)

# Obsolete layouts left behind by the documentation move.
# Negative lookaheads keep live `docs/reviews` and `docs/development_guides`.
_STALE_TOKEN = re.compile(
    r"(?P<path>"
    r"docs/v4(?:/|\b)"
    r"|docs/sprint\d+[A-Za-z]*(?:/|\b)"
    r"|docs/review(?:/|\b)(?!s)"
    r"|docs/development(?:/|\b)(?!_guides)"
    r")"
)

_ROOT_SENTINELS_LIVE = (
    Path("tools") / "repo_paths.py",
    Path("docs") / "01_specs",
    Path(".github") / "workflows" / "ci.yml",
)
_ROOT_SENTINELS_ALT = (
    Path("tools") / "repo_paths.py",
    Path("docs") / "main_v4",
    Path(".github") / "workflows" / "ci.yml",
)
_ROOT_SENTINELS_LEGACY = (
    Path("tools") / "repo_paths.py",
    Path("docs") / "v4",
    Path(".github") / "workflows" / "ci.yml",
)
# Foundation Lock (v0.5.0 concept lock): docs/01_specs is archived under
# docs/archive/v045/ once docs/SPEC.md lands. This sentinel keeps repo_root()
# resolving after that move without touching the pre-lock sentinels above.
_ROOT_SENTINELS_SPEC = (
    Path("tools") / "repo_paths.py",
    Path("docs") / "SPEC.md",
    Path(".github") / "workflows" / "ci.yml",
)


def repo_root(start: Path | None = None) -> Path:
    """Return the repository root even when invoked from a foreign cwd."""

    search: list[Path] = []
    here = Path(__file__).resolve().parent.parent
    search.append(here)
    cwd = (start or Path.cwd()).resolve()
    search.append(cwd)
    search.extend(cwd.parents)
    env_root = os.environ.get("VANGUARD_ROOT")
    if env_root:
        search.insert(0, Path(env_root).resolve())

    seen: set[Path] = set()
    for candidate in search:
        if candidate in seen:
            continue
        seen.add(candidate)
        if all((candidate / sentinel).exists() for sentinel in _ROOT_SENTINELS_LIVE):
            return candidate
        if all((candidate / sentinel).exists() for sentinel in _ROOT_SENTINELS_ALT):
            return candidate
        if all((candidate / sentinel).exists() for sentinel in _ROOT_SENTINELS_LEGACY):
            return candidate
        if all((candidate / sentinel).exists() for sentinel in _ROOT_SENTINELS_SPEC):
            return candidate
    raise FileNotFoundError(
        "cannot locate repository root: expected docs/main_v4 or docs/v4 plus tools/repo_paths.py"
    )


def repo_path(*parts: str | os.PathLike[str]) -> Path:
    return repo_root().joinpath(*parts)


def docs_main_v4(*parts: str | os.PathLike[str]) -> Path:
    root = repo_root()
    if (root / "docs" / "01_specs" / "backend").exists():
        return root.joinpath("docs", "01_specs", "backend", *parts)
    if (root / "docs" / "archive" / "v045" / "01_specs" / "backend").exists():
        return root.joinpath("docs", "archive", "v045", "01_specs", "backend", *parts)
    if (root / "docs" / "05_adr").exists():
        return root.joinpath("docs", "05_adr", *parts)
    base = CANONICAL["docs_main_v4"] if (root / CANONICAL["docs_main_v4"]).exists() else "docs"
    return root.joinpath(base, *parts)


def docs_scrum(*parts: str | os.PathLike[str]) -> Path:
    root = repo_root()
    if (root / CANONICAL["docs_scrum"]).exists():
        return root.joinpath(CANONICAL["docs_scrum"], *parts)
    if (root / LEGACY["docs_scrum"]).exists():
        return root.joinpath(LEGACY["docs_scrum"], *parts)
    return root.joinpath("docs", *parts)


def docs_sprint(sprint: str, *parts: str | os.PathLike[str]) -> Path:
    """Resolve a sprint directory. Sprints live under `docs/scrum/sprints/`."""

    root = repo_root()
    if (root / CANONICAL["docs_sprints"]).exists():
        return root.joinpath(CANONICAL["docs_sprints"], sprint, *parts)
    if (root / LEGACY["docs_sprints"]).exists():
        return root.joinpath(LEGACY["docs_sprints"], sprint, *parts)
    return root.joinpath("docs", sprint, *parts)


def docs_reviews(*parts: str | os.PathLike[str]) -> Path:
    root = repo_root()
    if (root / CANONICAL["docs_reviews"]).exists():
        return root.joinpath(CANONICAL["docs_reviews"], *parts)
    return root.joinpath("docs", "review", *parts)


def docs_development_guides(*parts: str | os.PathLike[str]) -> Path:
    root = repo_root()
    if (root / CANONICAL["docs_development_guides"]).exists():
        return root.joinpath(CANONICAL["docs_development_guides"], *parts)
    if (root / LEGACY["docs_development_guides"]).exists():
        return root.joinpath(LEGACY["docs_development_guides"], *parts)
    return root.joinpath("docs", "development", *parts)


def active_mvp_contract() -> Path:
    return docs_sprint("sprint0", "active-mvp-contract.json")


def baseline_manifest() -> Path:
    return docs_sprint("sprint0", "baseline-manifest.json")


def schema_archaeology_traces() -> Path:
    return docs_sprint("sprint0", "schema-archaeology", "traces")


def preregistered_oracles() -> Path:
    return docs_sprint("sprint6B", "preregistered_oracles.json")


def kernel_tcb_budget() -> Path:
    p = repo_path("tools", "kernel-tcb-budget.json")
    if p.exists():
        return p
    return docs_sprint("sprint2", "kernel-tcb-budget.json")


def rewrite_legacy_doc_path(value: str) -> str:
    """Map a single obsolete docs path to the live layout. Identity if already live."""

    text = value.replace("\\", "/")
    if text.startswith("docs/scrum"):
        return value
    if text.startswith("docs/reviews"):
        return value
    if text.startswith("docs/main_v4"):
        return value
    if text.startswith("docs/v4"):
        return "docs/main_v4" + text[len("docs/v4") :]
    if text.startswith("docs/agile/sprint"):
        return "docs/scrum/sprints/" + text[len("docs/agile/") :]
    if text.startswith("docs/agile/"):
        return "docs/scrum/" + text[len("docs/agile/") :]
    if text.startswith("docs/sprint"):
        return "docs/scrum/sprints/" + text[len("docs/") :]
    if text.startswith("docs/development_guides"):
        return "docs/scrum/development_guides" + text[len("docs/development_guides") :]
    if text.startswith("docs/review"):
        return "docs/reviews" + text[len("docs/review") :]
    if text.startswith("docs/development"):
        return "docs/scrum/development_guides" + text[len("docs/development") :]
    return value


def stale_path_matches(text: str) -> list[str]:
    """Return obsolete path tokens. Live prefixes are not reported."""

    return [match.group("path").rstrip("/") for match in _STALE_TOKEN.finditer(text)]


def require_file(path: Path, *, label: str | None = None) -> Path:
    if not path.is_file():
        name = label or str(path)
        raise FileNotFoundError(f"missing evidence file: {name}")
    return path
