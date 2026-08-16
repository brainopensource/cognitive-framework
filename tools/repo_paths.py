#!/usr/bin/env python3
"""Canonical repository-root-relative path map (S6B-GOV-001).

Every governance, contract, baseline, audit and CI helper must resolve
locations through this module. Callers must not scatter replacement
literals for the documentation move:

    docs/v4            -> docs/main_v4
    docs/sprintN       -> docs/agile/sprintN
    docs/review        -> docs/reviews
    docs/development   -> docs/development_guides

Commands are independent of the process working directory: ``repo_root()``
walks from this file (and, if needed, from cwd) until the live layout is
found. A missing file is never treated as satisfied evidence.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

CANONICAL = {
    "docs_main_v4": "docs/main_v4",
    "docs_agile": "docs/agile",
    "docs_reviews": "docs/reviews",
    "docs_development_guides": "docs/development_guides",
}

# Live prefixes that must not be flagged as stale.
LIVE_PREFIXES = tuple(CANONICAL.values()) + (
    "docs/agile/",
    "docs/main_v4/",
    "docs/reviews/",
    "docs/development_guides/",
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
    Path("docs") / "main_v4",
    Path(".github") / "workflows" / "ci.yml",
)
_ROOT_SENTINELS_LEGACY = (
    Path("tools") / "repo_paths.py",
    Path("docs") / "v4",
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
        if all((candidate / sentinel).exists() for sentinel in _ROOT_SENTINELS_LEGACY):
            return candidate
    raise FileNotFoundError(
        "cannot locate repository root: expected docs/main_v4 or docs/v4 plus tools/repo_paths.py"
    )


def repo_path(*parts: str | os.PathLike[str]) -> Path:
    return repo_root().joinpath(*parts)


def docs_main_v4(*parts: str | os.PathLike[str]) -> Path:
    root = repo_root()
    base = CANONICAL["docs_main_v4"] if (root / CANONICAL["docs_main_v4"]).exists() else "docs/v4"
    return root.joinpath(base, *parts)


def docs_agile(*parts: str | os.PathLike[str]) -> Path:
    root = repo_root()
    if (root / CANONICAL["docs_agile"]).exists():
        return root.joinpath(CANONICAL["docs_agile"], *parts)
    return root.joinpath("docs", *parts)


def docs_reviews(*parts: str | os.PathLike[str]) -> Path:
    root = repo_root()
    if (root / CANONICAL["docs_reviews"]).exists():
        return root.joinpath(CANONICAL["docs_reviews"], *parts)
    return root.joinpath("docs", "review", *parts)


def docs_development_guides(*parts: str | os.PathLike[str]) -> Path:
    root = repo_root()
    if (root / CANONICAL["docs_development_guides"]).exists():
        return root.joinpath(CANONICAL["docs_development_guides"], *parts)
    return root.joinpath("docs", "development", *parts)


def active_mvp_contract() -> Path:
    return docs_agile("sprint0", "active-mvp-contract.json")


def baseline_manifest() -> Path:
    return docs_agile("sprint0", "baseline-manifest.json")


def schema_archaeology_traces() -> Path:
    return docs_agile("sprint0", "schema-archaeology", "traces")


def kernel_tcb_budget() -> Path:
    return docs_agile("sprint2", "kernel-tcb-budget.json")


def rewrite_legacy_doc_path(value: str) -> str:
    """Map a single obsolete docs path to the live layout. Identity if already live."""

    text = value.replace("\\", "/")
    if text.startswith("docs/development_guides"):
        return value
    if text.startswith("docs/reviews"):
        return value
    if text.startswith("docs/main_v4"):
        return value
    if text.startswith("docs/agile/"):
        return value
    if text.startswith("docs/v4"):
        return "docs/main_v4" + text[len("docs/v4") :]
    if text.startswith("docs/sprint"):
        return "docs/agile/" + text[len("docs/") :]
    if text.startswith("docs/review"):
        return "docs/reviews" + text[len("docs/review") :]
    if text.startswith("docs/development"):
        return "docs/development_guides" + text[len("docs/development") :]
    return value


def stale_path_matches(text: str) -> list[str]:
    """Return obsolete path tokens. Live prefixes are not reported."""

    return [match.group("path").rstrip("/") for match in _STALE_TOKEN.finditer(text)]


def require_file(path: Path, *, label: str | None = None) -> Path:
    if not path.is_file():
        name = label or str(path)
        raise FileNotFoundError(f"missing evidence file: {name}")
    return path
