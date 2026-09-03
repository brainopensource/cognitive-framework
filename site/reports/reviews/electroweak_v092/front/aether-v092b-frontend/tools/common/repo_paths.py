#!/usr/bin/env python3
"""Canonical repository-root-relative path map (S6B-GOV-001).

Every governance, contract, baseline, audit and CI helper must resolve
locations through this module. Callers must not scatter replacement
literals for the documentation move:

    old numbered/module paths -> the authority-ordered docs tree

Commands are independent of the process working directory: ``repo_root()``
walks from this file (and, if needed, from cwd) until the live layout is
found. A missing file is never treated as satisfied evidence.
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
_ROOT_SENTINELS_PYPROJECT = (
    Path("pyproject.toml"),
    Path("vanguard") / "packages",
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
    env_root = os.environ.get("VANGUARD_ROOT") or os.environ.get("AETHER_REPO_ROOT")
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
        if all((candidate / sentinel).exists() for sentinel in _ROOT_SENTINELS_PYPROJECT):
            return candidate
    raise FileNotFoundError(
        "cannot locate repository root: expected pyproject.toml or docs/SPEC.md"
    )


def repo_path(*parts: str | os.PathLike[str]) -> Path:
    return repo_root().joinpath(*parts)


def get_docs_root() -> Path:
    return repo_root() / "docs"


def get_schemas_root() -> Path:
    return repo_root() / "schemas"


def get_packs_root() -> Path:
    return repo_root() / "packs"


def get_test_root() -> Path:
    return repo_root() / "test"


def get_generated_root() -> Path:
    return repo_root() / ".generated"


def get_tools_root() -> Path:
    return repo_root() / "tools"


def get_vanguard_root() -> Path:
    return repo_root() / "vanguard"


# Export module-level aliases for convenient direct access
REPO_ROOT = repo_root()
DOCS_ROOT = REPO_ROOT / "docs"
SCHEMAS_ROOT = REPO_ROOT / "schemas"
PACKS_ROOT = REPO_ROOT / "packs"
TEST_ROOT = REPO_ROOT / "test"
GENERATED_ROOT = REPO_ROOT / ".generated"
TOOLS_ROOT = REPO_ROOT / "tools"
VANGUARD_ROOT = REPO_ROOT / "vanguard"


def docs_main_v4(*parts: str | os.PathLike[str]) -> Path:
    root = repo_root()
    return root.joinpath(CANONICAL["docs_decisions"], *parts)


def docs_scrum(*parts: str | os.PathLike[str]) -> Path:
    root = repo_root()
    if (root / "docs" / "execution").exists():
        return root.joinpath("docs", "execution", *parts)
    if (root / CANONICAL["docs_execution"]).exists():
        return root.joinpath(CANONICAL["docs_execution"], *parts)
    if (root / LEGACY["docs_scrum"]).exists():
        return root.joinpath(LEGACY["docs_scrum"], *parts)
    return root.joinpath("docs", *parts)


def docs_sprint(sprint: str, *parts: str | os.PathLike[str]) -> Path:
    """Resolve a sprint directory. Sprints live under `docs/execution/`."""
    root = repo_root()
    if (root / "docs" / "execution").exists():
        return root.joinpath("docs", "execution", sprint, *parts)
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
    if (root / "docs" / "engineering").exists():
        return root.joinpath("docs", "engineering", *parts)
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
    """Return the canonical path to the preregistered oracle registry."""
    root = repo_root()
    test_fixtures = root / "test" / "fixtures" / "preregistered_oracles.json"
    if test_fixtures.exists():
        return test_fixtures
    docs_evidence = root / "docs" / "03_execution" / "evidence" / "preregistered_oracles.json"
    if docs_evidence.exists():
        return docs_evidence
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
