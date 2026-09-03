"""MOCK dogfood driver: run a task set and export what actually happened (`W13-A`).

Runs each workspace through the repair loop until the allowlisted `proc.exec`
suite is green or the budget is spent, then writes one session JSON per task.

Three properties this file exists to keep:

**A missing workspace is reported, not skipped.** A task set that silently
drops the workspaces it could not find reports a pass rate over the tasks that
happened to be present, which is the denominator problem the retraction sweep
was for. An absent task is `inconclusive:workspace_missing` and stays in the
denominator.

**The oracle is exterior.** This module never runs a test itself. It is handed
a callable that reads the run's verdict, so the driver cannot become the second
judge (`A-05`).

**Every number comes from the ledger.** Turns, verbs, receipts, dead ends and
cache-miss attribution are the session-log projection; nothing is counted here
a second time (`A-07`).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .repair import RepairOutcome, StopReason, drive_until_green
from .session_log import session_log

__all__ = ["TaskReport", "DogfoodReport", "run_task_set"]

#: A task whose workspace is not on disk. Named, and kept in the denominator.
WORKSPACE_MISSING = "inconclusive:workspace_missing"


@dataclass(frozen=True, slots=True)
class TaskReport:
    task_id: str
    workspace: str
    outcome: str
    attempts: int = 0
    turns: int = 0
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    session: tuple[Mapping[str, Any], ...] = ()
    dead_ends: tuple[Mapping[str, Any], ...] = ()
    cache_misses: tuple[Mapping[str, Any], ...] = ()
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "taskId": self.task_id,
            "workspace": self.workspace,
            "outcome": self.outcome,
            "attempts": self.attempts,
            "turns": self.turns,
            "promptTokens": self.prompt_tokens,
            "completionTokens": self.completion_tokens,
            "session": [dict(entry) for entry in self.session],
            "deadEnds": [dict(entry) for entry in self.dead_ends],
            "cacheMissAttribution": [dict(entry) for entry in self.cache_misses],
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class DogfoodReport:
    label: str
    tasks: tuple[TaskReport, ...] = field(default_factory=tuple)

    @property
    def resolved(self) -> int:
        return sum(1 for task in self.tasks if task.outcome == StopReason.ORACLE_GREEN)

    @property
    def denominator(self) -> int:
        """Every task attempted, including the ones whose workspace was absent."""
        return len(self.tasks)

    @property
    def inconclusive(self) -> tuple[str, ...]:
        return tuple(task.task_id for task in self.tasks
                     if task.outcome.startswith("inconclusive:")
                     or task.outcome.startswith(StopReason.INSTRUMENT_ERROR))

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "resolved": self.resolved,
            "denominator": self.denominator,
            "inconclusive": list(self.inconclusive),
            "tasks": [task.to_dict() for task in self.tasks],
        }

    def write(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n",
                          encoding="utf-8")
        return target


def run_task_set(
    tasks: Sequence[Mapping[str, str]],
    *,
    run_session: Callable[[Mapping[str, str], int], Any],
    oracle: Callable[[Any], bool],
    events_of: Callable[[Any], Sequence[Any]],
    label: str = "mock-dogfood",
    max_attempts: int = 4,
    max_tokens: int | None = None,
) -> DogfoodReport:
    """Drive every task; return one report per task, absent ones included."""

    reports: list[TaskReport] = []
    for task in tasks:
        task_id = str(task.get("id", "")) or "unnamed"
        workspace = str(task.get("workspace", ""))

        if not workspace or not Path(workspace).is_dir():
            reports.append(TaskReport(
                task_id=task_id, workspace=workspace, outcome=WORKSPACE_MISSING,
                detail="workspace does not exist; counted, not skipped"))
            continue

        last: list[Any] = []

        def _run(attempt: int, _task: Mapping[str, str] = task) -> Any:
            result = run_session(_task, attempt)
            last.append(result)
            return result

        outcome: RepairOutcome = drive_until_green(
            _run, oracle=oracle, max_attempts=max_attempts, max_tokens=max_tokens)

        log = session_log(events_of(last[-1])) if last else session_log([])
        reports.append(TaskReport(
            task_id=task_id,
            workspace=workspace,
            outcome=outcome.stop_reason,
            attempts=outcome.attempts,
            turns=outcome.telemetry.turns,
            prompt_tokens=outcome.telemetry.prompt_tokens,
            completion_tokens=outcome.telemetry.completion_tokens,
            session=tuple(entry.to_dict() for entry in log.entries),
            dead_ends=log.dead_end_details,
            cache_misses=log.cache_miss_attribution(),
            detail=outcome.detail,
        ))

    return DogfoodReport(label=label, tasks=tuple(reports))
