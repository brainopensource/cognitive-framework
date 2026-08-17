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

#: BETA's dogfood workspaces. **Protocol ids are stable; directory names are
#: not.** These pointed at `benchmarkings/dogfood/DOGFOOD-0N` and reported 3 of
#: 3 missing -- the instrument working exactly as intended, because a wrong
#: constant surfaced as a named absence rather than as a smaller task set.
#: Corrected to BETA's paths (`2a793c4`).
DOGFOOD_SET: tuple[Mapping[str, str], ...] = (
    {"id": "DOGFOOD-01",
     "workspace": "lab/tasks/dogfood-01-multi-turn-file-rollback"},
    {"id": "DOGFOOD-02",
     "workspace": "lab/tasks/dogfood-02-subprocess-timeout-censoring"},
    {"id": "DOGFOOD-03",
     "workspace": "lab/tasks/dogfood-03-manifest-alias-shadowing"},
)

#: One greenfield task: a Python HTTP API plus a static HTML page. No Svelte,
#: no build step, no network. Starts red, by design.
GREENFIELD_SET: tuple[Mapping[str, str], ...] = (
    {"id": "GREENFIELD-API-HTML", "workspace": "lab/tasks/greenfield-api-html"},
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
