"""Fact-level repository diff for LDA (``lda diff``).

Answers "what changed since the last index run (or a given commit)" without
re-indexing: compares the live workspace against the fact graph, or classifies
git-known changes for ``--since <sha>``. Read-only and deterministic.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

from .gitinfo import current_head_sha

_SKIP_DIRS = {".git", ".lda", "node_modules", "__pycache__", ".venv", "dist", "build", "site"}
_MAX_LISTED = 100
_MAX_SCANNED = 200


def _file_hash(path: Path) -> Optional[str]:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _index_diff(root: Path, storage: Any) -> Dict[str, Any]:
    """Workspace-vs-index comparison: added / modified / deleted files."""
    states = storage.get_all_file_states()
    indexed: Dict[str, str] = {
        path: meta["content_hash"] for path, meta in states.items()
    }
    deleted: List[str] = []
    modified: List[str] = []
    unchanged = 0
    for path, old_hash in indexed.items():
        fp = root / path
        if not fp.exists():
            deleted.append(path)
            continue
        new_hash = _file_hash(fp)
        if new_hash and new_hash != old_hash:
            modified.append(path)
        else:
            unchanged += 1

    # Added: indexed-relevant files on disk absent from the index (bounded).
    from .standardizer import detect_language

    added: List[str] = []
    indexed_set = set(indexed)
    for p in sorted(root.rglob("*")):
        if len(added) >= _MAX_SCANNED:
            break
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if any(part in _SKIP_DIRS for part in p.parts):
            continue
        if rel in indexed_set:
            continue
        if detect_language(rel) in ("unknown", "text", ""):
            continue
        added.append(rel)

    stale_count = len(deleted) + len(modified)
    return {
        "mode": "workspace_vs_index",
        "added_files": added[:_MAX_LISTED],
        "modified_files": modified[:_MAX_LISTED],
        "deleted_files": deleted[:_MAX_LISTED],
        "added_count": len(added),
        "modified_count": len(modified),
        "deleted_count": len(deleted),
        "unchanged_files": unchanged,
        "stale_fact_files": stale_count,
        "action_hint": (
            "index matches workspace" if stale_count == 0 and not added
            else "run 'lda index --incremental' to refresh stale facts"
        ),
    }


def _git_diff_since(root: Path, since: str) -> Optional[Dict[str, Any]]:
    """Classify git-known changes since *since* (cross-references the index head)."""
    from .runner import run_command

    try:
        code, out, _ = run_command(["git", "diff", "--name-status", since, "HEAD"], root)
    except OSError:
        return None
    if code != 0:
        return None
    added: List[str] = []
    modified: List[str] = []
    deleted: List[str] = []
    renamed: List[str] = []
    for line in out.splitlines():
        parts = line.split("\t")
        if not parts or not parts[0]:
            continue
        status, path = parts[0][0], parts[-1]
        if status == "A":
            added.append(path)
        elif status == "M":
            modified.append(path)
        elif status == "D":
            deleted.append(path)
        elif status == "R":
            renamed.append(line)
    head = current_head_sha(root)
    changed = bool(added or modified or deleted)
    return {
        "mode": "git_since",
        "since": since,
        "head": head,
        "added_files": added[:_MAX_LISTED],
        "modified_files": modified[:_MAX_LISTED],
        "deleted_files": deleted[:_MAX_LISTED],
        "renamed": renamed[:50],
        "added_count": len(added),
        "modified_count": len(modified),
        "deleted_count": len(deleted),
        "action_hint": (
            "run 'lda index --incremental' after reviewing this range"
            if changed else "no file-level changes in range"
        ),
    }


def compute_diff(root: Path, storage: Any, since: Optional[str] = None) -> Dict[str, Any]:
    """Fact-level diff: workspace-vs-index, or git range when ``since`` given."""
    root = Path(root)
    if since:
        result = _git_diff_since(root, since)
        if result is not None:
            return result
    return _index_diff(root, storage)


__all__ = ["compute_diff"]
