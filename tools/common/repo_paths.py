#!/usr/bin/env python3
"""Canonical repository-root-relative path map (S6B-GOV-001).

Every governance, contract, baseline, audit and CI helper must resolve
locations through this module. Callers must not scatter replacement
literals for the documentation move:

    old numbered/module paths -> the authority-ordered docs tree

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
    "docs_law": "docs/01_law",
    "docs_decisions": "docs/02_decisions",
    "docs_execution": "docs/03_execution",
    "docs_architecture": "docs/04_architecture",
    "docs_contracts": "docs/05_contracts",
    "docs_protocols": "docs/06_protocols",
    "docs_engineering": "docs/07_engineering",
    "docs_theory": "docs/08_theory",
    "docs_diagrams": "docs/09_diagrams",
    "docs_archive": "docs/_archive",
    "docs_references": "docs/_archive/references",
    "docs_reviews": "docs/_archive/reviews",
    # Compatibility names retained for callers; they resolve to the new owners.
    "docs_main_v4": "docs/02_decisions",
    "docs_scrum": "docs/03_execution",
    "docs_sprints": "docs/03_execution",
    "docs_development_guides": "docs/07_engineering",
}

# Pre-restructure layout, retained for resolution fallback only.
LEGACY = {
    "docs_scrum": "docs/agile",
    "docs_sprints": "docs/agile",
    "docs_development_guides": "docs/development_guides",
}

# Live prefixes that must not be flagged as stale.
LIVE_PREFIXES = tuple(CANONICAL.values())

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
    Path("tools") / "common" / "repo_paths.py",
    Path("docs") / "SPEC.md",
    Path(".github") / "workflows" / "ci.yml",
)
_ROOT_SENTINELS_ALT = (
    Path("pyproject.toml"),
    Path(".github") / "workflows" / "ci.yml",
)
_ROOT_SENTINELS_LEGACY = (
    Path("vanguard") / "packages",
    Path(".github") / "workflows" / "ci.yml",
)
_ROOT_SENTINELS_SPEC = (
    Path("docs") / "SPEC.md",
    Path(".github") / "workflows" / "ci.yml",
)


def repo_root(start: Path | None = None) -> Path:
    """Return the repository root even when invoked from a foreign cwd."""

    search: list[Path] = []
    here = Path(__file__).resolve().parent.parent.parent
    search.append(here)
    search.append(here.parent)
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
        "cannot locate repository root: expected pyproject.toml or docs/SPEC.md"
    )


def repo_path(*parts: str | os.PathLike[str]) -> Path:
    return repo_root().joinpath(*parts)


def docs_main_v4(*parts: str | os.PathLike[str]) -> Path:
    root = repo_root()
    return root.joinpath(CANONICAL["docs_decisions"], *parts)


def docs_scrum(*parts: str | os.PathLike[str]) -> Path:
    root = repo_root()
    if (root / CANONICAL["docs_execution"]).exists():
        return root.joinpath(CANONICAL["docs_execution"], *parts)
    if (root / LEGACY["docs_scrum"]).exists():
        return root.joinpath(LEGACY["docs_scrum"], *parts)
    return root.joinpath("docs", *parts)


def docs_sprint(sprint: str, *parts: str | os.PathLike[str]) -> Path:
    """Resolve a sprint directory. Sprints live under `docs/scrum/sprints/`."""

    root = repo_root()
    if (root / CANONICAL["docs_execution"]).exists():
        return root.joinpath(CANONICAL["docs_execution"], sprint, *parts)
    if (root / LEGACY["docs_sprints"]).exists():
        return root.joinpath(LEGACY["docs_sprints"], sprint, *parts)
    return root.joinpath("docs", sprint, *parts)


def docs_reviews(*parts: str | os.PathLike[str]) -> Path:
    root = repo_root()
    return root.joinpath(CANONICAL["docs_reviews"], *parts)


def docs_development_guides(*parts: str | os.PathLike[str]) -> Path:
    root = repo_root()
    if (root / CANONICAL["docs_engineering"]).exists():
        return root.joinpath(CANONICAL["docs_engineering"], *parts)
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
    """Return the canonical path to the preregistered oracle registry.

    Wave 0 (ADR-0075 F-20): restored to test/fixtures/ as the stable,
    test-suite-owned location. Fallback to docs/03_sprints/evidence/ for
    historical compatibility. The sprint6B fallback is retired — that path
    no longer exists in the tree.
    """
    root = repo_root()
    # Primary canonical: test-suite-owned (Wave 0 restoration, ADR-0075 F-20).
    test_fixtures = root / "test" / "fixtures" / "preregistered_oracles.json"
    if test_fixtures.exists():
        return test_fixtures
    # Legacy docs location (v0.5.1 baseline, deleted at commit caaa7af).
    docs_evidence = root / "docs" / "03_execution" / "evidence" / "preregistered_oracles.json"
    if docs_evidence.exists():
        return docs_evidence
    # Return canonical test/fixtures path even if missing so callers get a
    # deterministic error rather than a ghost sprint6B path.
    return test_fixtures


def kernel_tcb_budget() -> Path:
    p = repo_path("tools", "linters", "kernel-tcb-budget.json")
    if p.exists():
        return p
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
