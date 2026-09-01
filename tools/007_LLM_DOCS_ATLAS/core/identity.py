"""Repository identity snapshot for LDA (``lda identity``).

Answers the fixed identity/state question set in one deterministic command:
which repository, which branch, which exact commit, dirty state, submodules,
build system, language/runtime constraints, and whether the fact graph was
built for the same commit that is checked out right now.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .gitinfo import current_head_sha
from .profile import RepositoryProfile

# Well-known build/manifest files -> build system name
_BUILD_MARKERS = (
    ("pyproject.toml", "python"),
    ("package.json", "node"),
    ("Cargo.toml", "rust"),
    ("go.mod", "go"),
    ("pom.xml", "maven"),
    ("build.gradle", "gradle"),
    ("Makefile", "make"),
    ("justfile", "just"),
    ("Justfile", "just"),
    ("CMakeLists.txt", "cmake"),
)


def _git(root: Path, *args: str) -> tuple[int, str]:
    from .runner import run_command

    try:
        code, out, _ = run_command(["git", *args], root)
    except OSError:
        return 127, ""
    return code, (out or "").strip()


def _version_hints(root: Path, system: str) -> Dict[str, Any]:
    """Extract declared language/runtime version constraints, fail-open."""
    hints: Dict[str, Any] = {}
    pyproject = root / "pyproject.toml"
    if system == "python" and pyproject.is_file():
        for line in pyproject.read_text(encoding="utf-8", errors="replace").splitlines():
            if "requires-python" in line and "=" in line:
                hints["requires-python"] = line.split("=", 1)[1].strip().strip("\"'")
                break
    package_json = root / "package.json"
    if system == "node" and package_json.is_file():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
            if isinstance(data.get("engines"), dict):
                hints["engines"] = data["engines"]
        except (json.JSONDecodeError, OSError):
            pass
    cargo = root / "Cargo.toml"
    if system == "rust" and cargo.is_file():
        for line in cargo.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.strip().startswith("edition"):
                hints["edition"] = line.split("=", 1)[1].strip().strip("\"'")
                break
    return hints


def repo_identity(
    root: Path,
    storage: Any,
    profile: Optional[RepositoryProfile] = None,
) -> Dict[str, Any]:
    """Deterministic identity/state snapshot bound to the live workspace."""
    root = Path(root)
    active = profile or RepositoryProfile()
    head = current_head_sha(root)

    branch_code, branch = _git(root, "branch", "--show-current")
    dirty_code, porcelain = _git(root, "status", "--porcelain")
    # LDA's own store (.lda/) is derived state and must not make the
    # workspace report dirty.
    dirty_lines = [
        line for line in porcelain.splitlines()
        if line.strip() and not line.strip().endswith(("/.lda", ".lda"))
        and ".lda/" not in line
    ]
    dirty = bool(dirty_code == 0 and dirty_lines)
    dirty_count = len(dirty_lines)
    _sub_code, sub_out = _git(root, "submodule", "status")
    submodules = len(sub_out.splitlines()) if sub_out else 0

    build_systems: list[Dict[str, Any]] = []
    for marker, system in _BUILD_MARKERS:
        if (root / marker).is_file():
            entry: Dict[str, Any] = {"system": system, "manifest": marker}
            entry.update(_version_hints(root, system))
            build_systems.append(entry)

    run = storage.latest_index_run() if storage is not None else None
    index_head = (run or {}).get("head_sha")
    index_head = index_head[:12] if index_head else None
    stats = storage.get_stats() if storage is not None else {}

    if head and index_head:
        freshness = "FRESH" if head.startswith(index_head) else "STALE"
    elif head and not index_head:
        freshness = "UNKNOWN"  # indexed before head_sha was recorded
    else:
        freshness = "NO_GIT"

    return {
        "repository": root.name,
        "root": str(root),
        "branch": branch or None,
        "head_sha": head,
        "dirty": dirty,
        "local_changes": dirty_count,
        "submodules": submodules,
        "build_systems": build_systems,
        "profile": active.name,
        "index": {
            "files": stats.get("files", 0),
            "symbols": stats.get("symbols", 0),
            "relations": stats.get("relations", 0),
            "documents": stats.get("documents", 0),
            "latest_run": (run or {}).get("id"),
            "index_head_sha": index_head,
            "freshness_vs_head": freshness,
        },
        "action_hint": (
            "index matches HEAD" if freshness == "FRESH"
            else "run 'lda index' to bind the fact graph to the current commit"
            if freshness in ("STALE", "UNKNOWN")
            else "workspace has no git HEAD; freshness binding inactive"
        ),
    }


__all__ = ["repo_identity"]
