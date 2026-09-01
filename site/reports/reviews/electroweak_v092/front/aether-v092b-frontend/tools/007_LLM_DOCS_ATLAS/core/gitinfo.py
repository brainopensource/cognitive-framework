"""Git revision provenance: HEAD binding for context packets (fail-closed freshness)."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from .runner import run_command


def current_head_sha(root: Path) -> Optional[str]:
    """Return the resolved HEAD commit SHA for *root*, or None outside a git work tree.

    Capture is fail-open (None when git is unavailable), but the freshness
    invariant itself is fail-closed: context packets record ``source_head_sha``
    in their provenance and consumers MUST compare it against the live
    workspace SHA, recompiling or refusing to serve on mismatch.
    """
    try:
        code, out, _err = run_command(["git", "rev-parse", "HEAD"], Path(root))
    except OSError:
        return None
    if code != 0:
        return None
    sha = out.strip()
    return sha or None