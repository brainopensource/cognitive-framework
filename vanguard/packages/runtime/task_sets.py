"""The task sets W13/W16 run, and where their workspaces are looked for.

`W16-A`. BETA owns the task directories; this owns the paths and the honesty
about their absence. A set is a list of `(id, workspace)` rows, resolved
against the repository root, and a row whose directory is not there is
**still a row**: `inconclusive:workspace_missing`, kept in the denominator.

Declaring the set here rather than discovering it by glob is deliberate. A glob
reports a smaller task set when a directory is missing and calls it a full run;
a declared set reports the same task set every time and says which parts of it
could not be run.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, Sequence

__all__ = ["DOGFOOD_SET", "GREENFIELD_SET", "resolve_task_set", "missing_tasks"]

#: BETA's dogfood workspaces. Paths are the contract; the dirs may not exist yet.
DOGFOOD_SET: tuple[Mapping[str, str], ...] = (
    {"id": "DOGFOOD-01", "workspace": "benchmarkings/dogfood/DOGFOOD-01"},
    {"id": "DOGFOOD-02", "workspace": "benchmarkings/dogfood/DOGFOOD-02"},
    {"id": "DOGFOOD-03", "workspace": "benchmarkings/dogfood/DOGFOOD-03"},
)

#: One greenfield task: a Python HTTP API plus a static HTML page. No Svelte,
#: no build step, no network. The fixture in `test/runtime/fixtures/` is the
#: reference shape; BETA may land a richer one at the same id.
GREENFIELD_SET: tuple[Mapping[str, str], ...] = (
    {"id": "GREENFIELD-01",
     "workspace": "test/runtime/fixtures/greenfield_api"},
)


def resolve_task_set(
    tasks: Sequence[Mapping[str, str]],
    *,
    root: str | Path,
) -> tuple[Mapping[str, str], ...]:
    """Absolute-ise workspaces against `root`. Existence is not checked here.

    Resolution and existence are separate on purpose: the driver reports a
    missing workspace as an outcome, and a resolver that silently dropped it
    would take that reporting away.
    """
    base = Path(root)
    return tuple({"id": task["id"], "workspace": str(base / task["workspace"])}
                 for task in tasks)


def missing_tasks(tasks: Sequence[Mapping[str, str]]) -> tuple[str, ...]:
    """Ids whose workspace is not on disk. For reporting, never for filtering."""
    return tuple(task["id"] for task in tasks
                 if not Path(task["workspace"]).is_dir())
