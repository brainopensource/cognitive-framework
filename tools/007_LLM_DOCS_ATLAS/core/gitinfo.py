"""Git revision provenance and working tree intelligence (<20ms)."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .runner import run_command


def current_head_sha(root: Path) -> Optional[str]:
    """Return the resolved HEAD commit SHA for *root*, or None outside a git work tree."""
    try:
        code, out, _err = run_command(["git", "rev-parse", "HEAD"], Path(root))
    except OSError:
        return None
    if code != 0:
        return None
    sha = out.strip()
    return sha or None


def get_repo_status(root: Path) -> Dict[str, Any]:
    """Return structured git state, branch, HEAD, dirty files and diffstat in <20ms."""
    root_path = Path(root)
    head_sha = current_head_sha(root_path) or "UNBORN"
    branch = "DETACHED"
    try:
        code, out, _ = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], root_path)
        if code == 0 and out.strip():
            branch = out.strip()
    except Exception:
        pass

    # Upstream tracking
    upstream = None
    try:
        code, out, _ = run_command(["git", "rev-parse", "--abbrev-ref", "@{upstream}"], root_path)
        if code == 0 and out.strip():
            upstream = out.strip()
    except Exception:
        pass

    # Status porcelain
    staged: List[str] = []
    unstaged: List[str] = []
    untracked: List[str] = []
    dirty_summary: List[Dict[str, Any]] = []

    try:
        code, out, _ = run_command(["git", "status", "--porcelain"], root_path)
        if code == 0 and out:
            for line in out.splitlines():
                if len(line) < 3:
                    continue
                xy = line[:2]
                fpath = line[3:].strip()
                if " -> " in fpath:
                    fpath = fpath.split(" -> ", 1)[1].strip()
                x, y = xy[0], xy[1]
                if x == "?" and y == "?":
                    untracked.append(fpath)
                else:
                    if x not in (" ", "?"):
                        staged.append(fpath)
                    if y not in (" ", "?"):
                        unstaged.append(fpath)
    except Exception:
        pass

    # Diffstat for unstaged & staged
    diff_stats: Dict[str, Dict[str, int]] = {}
    try:
        code, out, _ = run_command(["git", "diff", "--numstat", "HEAD"], root_path)
        if code == 0 and out:
            for line in out.splitlines():
                parts = line.split("\t")
                if len(parts) >= 3:
                    added_str, removed_str, fpath = parts[0], parts[1], parts[2]
                    added = int(added_str) if added_str.isdigit() else 0
                    removed = int(removed_str) if removed_str.isdigit() else 0
                    diff_stats[fpath] = {"lines_added": added, "lines_removed": removed}
    except Exception:
        pass

    all_dirty = sorted(list(set(staged + unstaged)))
    for f in all_dirty:
        stat = diff_stats.get(f, {"lines_added": 0, "lines_removed": 0})
        status_char = "M"
        if f in staged and f not in unstaged:
            status_char = "S"
        elif f in unstaged and f not in staged:
            status_char = "M"
        dirty_summary.append({
            "file": f,
            "status": status_char,
            "lines_added": stat["lines_added"],
            "lines_removed": stat["lines_removed"],
        })

    # Recent commits (up to 3)
    latest_commits: List[Dict[str, str]] = []
    try:
        code, out, _ = run_command(["git", "log", "-n", "3", "--pretty=format:%h%x09%an%x09%s"], root_path)
        if code == 0 and out:
            for line in out.splitlines():
                parts = line.split("\t")
                if len(parts) == 3:
                    latest_commits.append({
                        "sha": parts[0],
                        "author": parts[1],
                        "message": parts[2],
                    })
    except Exception:
        pass

    # Draft handoffs in .draft/logs/ if present
    draft_handoffs: List[str] = []
    draft_dir = root_path / ".draft" / "logs"
    if draft_dir.exists():
        for p in draft_dir.glob("*"):
            if p.is_file():
                draft_handoffs.append(str(p.relative_to(root_path)))

    return {
        "branch": branch,
        "head_sha": head_sha[:8] if head_sha != "UNBORN" else "UNBORN",
        "full_head_sha": head_sha,
        "upstream": upstream,
        "dirty_files_count": len(all_dirty),
        "dirty_files": all_dirty,
        "dirty_summary": dirty_summary,
        "staged_files": staged,
        "unstaged_files": unstaged,
        "untracked_files": untracked[:50],
        "latest_commits": latest_commits,
        "draft_handoffs": draft_handoffs,
    }