"""LAM for the coding instrument: MOCK over pre-registered task dirs.

Does not compose a second episode loop. Does not call the host test runner as an
oracle. Does not drop missing workspaces from the denominator.

When a dir is absent: termination=inconclusive:workspace_missing, in_denominator=True.
When a dir is present but ALFA's driver is not bound here: inconclusive:driver_not_bound
(still in the denominator). oracle_green is only True when a session record says so.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from tools.telemetry.coding_instrument import (
    CODING_ARMS,
    CODING_FAMILY,
    PREREGISTERED_TASKS,
    instrument_tuple,
    mock_must_not_wear_live_label,
)


def _empty_row(task_id: str, termination: str, *, model_port: str) -> dict[str, Any]:
    return {
        "taskId": task_id,
        "termination": termination,
        "turnCount": 0,
        "verbs": [],
        "denialCount": 0,
        "cacheMissAttribution": "unattributed",
        "compactCount": 0,
        "deadEnds": [],
        "oracle_green": False,
        "modelPort": model_port,
        "inDenominator": True,
    }


def run_coding_lam(
    workspaces: Mapping[str, Path | str | None],
    *,
    arm: str = "mock",
    model_port: str = "mock",
    sessions: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Evaluate the pre-registered split.

    ``workspaces`` maps task id → directory or None. Unknown extra keys are ignored.
    ``sessions`` optionally supplies a vg.coding-session.v1 dict per task (ledger projection).
    """
    if not mock_must_not_wear_live_label(model_port, arm):
        raise ValueError("MOCK ModelPort cannot wear a live arm label")
    if arm not in CODING_ARMS:
        raise ValueError(f"unknown arm {arm!r}")

    rows: list[dict[str, Any]] = []
    session_map = sessions or {}
    for task_id in PREREGISTERED_TASKS:
        raw = workspaces.get(task_id)
        path = Path(raw) if raw else None
        if path is None or not path.is_dir():
            rows.append(_empty_row(task_id, "inconclusive:workspace_missing", model_port=model_port))
            continue
        session = session_map.get(task_id)
        if session is None:
            row = _empty_row(task_id, "inconclusive:driver_not_bound", model_port=model_port)
            row["workspace"] = str(path)
            rows.append(row)
            continue
        if session.get("schema") != "vg.coding-session.v1":
            row = _empty_row(task_id, "inconclusive:instrument_error", model_port=model_port)
            rows.append(row)
            continue
        termination = str(session.get("termination") or session.get("outcome") or "abandoned")
        oracle = bool(session.get("oracle_green", False))
        rows.append({
            "taskId": task_id,
            "termination": termination,
            "turnCount": int(session.get("turnCount") or 0),
            "verbs": list(session.get("verbs") or []),
            "denialCount": int(session.get("denialCount") or 0),
            "cacheMissAttribution": session.get("cacheMissAttribution") or "unattributed",
            "compactCount": int(session.get("compactCount") or 0),
            "deadEnds": list(session.get("deadEnds") or []),
            "oracle_green": oracle,
            "modelPort": model_port,
            "inDenominator": True,
            "workspace": str(path),
        })

    denominator = len(rows)
    green = sum(1 for row in rows if row["oracle_green"])
    missing = sum(1 for row in rows if row["termination"] == "inconclusive:workspace_missing")
    return {
        "instrument": instrument_tuple(arm=arm),
        "family": CODING_FAMILY,
        "arm": arm,
        "modelPort": model_port,
        "denominator": denominator,
        "oracleGreenCount": green,
        "workspaceMissingCount": missing,
        "passRateNumerator": green,
        "passRateDenominator": denominator,
        "tasks": rows,
        "q2": False,
        "publishedLift": None,
    }


def default_workspace_map(repo_root: Path) -> dict[str, Path | None]:
    """BETA's layout, read from the one declared task set. Absence is None.

    This used to spell the directories itself (`lab/tasks/DOGFOOD-01`), which
    is not what BETA landed (`lab/tasks/dogfood-01-multi-turn-file-rollback`),
    so every task resolved to `None` and the whole split reported
    `inconclusive:workspace_missing`. The instrument was behaving correctly --
    a wrong constant surfaced as a named absence rather than a smaller task set
    -- but there were **two** copies of the constant, here and in
    `runtime/task_sets.py`, and two copies of a path is one copy that is wrong.

    The declared set is now the single source. Existence is still evaluated
    here, and a missing directory is still `None` rather than omitted.
    """
    import sys

    root = str(repo_root)
    if root not in sys.path:
        sys.path.insert(0, root)
    from vanguard.packages.runtime.task_sets import (  # noqa: E402
        DOGFOOD_SET,
        GREENFIELD_SET,
        resolve_task_set,
    )

    resolved = resolve_task_set(DOGFOOD_SET + GREENFIELD_SET, root=repo_root)
    return {task["id"]: (Path(task["workspace"])
                         if Path(task["workspace"]).is_dir() else None)
            for task in resolved}
