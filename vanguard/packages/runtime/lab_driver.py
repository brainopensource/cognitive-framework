#!/usr/bin/env python3
"""Run one task directory against one frozen harness pack (`W14-A`).

**Why this is not `lab/run.py`.** `lab/` must import nothing -- the boundary
checker enforces it, because `lab/` is disposable and nothing disposable may
become load-bearing. That rule is also the reason the old `lab/run.py` could
only ever fabricate: unable to reach the runtime, it returned a literal
`{"status": "completed", "turnCount": 1}` for every task, whatever happened.
A driver that cannot call the thing it claims to drive is a driver that lies.

So the driver lives here, in the composition layer that is allowed to know
concrete implementations, and `lab/run.py` is gone rather than left as a stub
that reports success.

  python3 -m vanguard.packages.runtime.lab_driver --pack … --task-dir …

**This driver used to fabricate its result.** It read the manifest, never
composed anything, never ran a turn, and returned
`{"status": "completed", "turnCount": 1}` regardless of what the task was or
whether any work happened. A harness that reports completion for work it did
not do is worse than one that reports nothing (`REQ-TRUST-001`).

It now composes a real `Harness`, runs a real `HarnessSession`, and reports
what the ledger says. Greenfield and bugfix are the same path: one compose, one
episode tree, tools, receipts, ledger. There is no second agent loop here --
the repair driver re-enters `HarnessSession.run()` and nothing else.

CLI:
  python3 -m vanguard.packages.runtime.lab_driver --pack vg-code-default --task-dir DIR
      [--model mock|ollama|openrouter|deepseek] [--model-name TAG]
      [--interactive | --benchmark] [--max-turns N] [--max-attempts N]
      [--jsonl-out FILE] [--json]

The JSONL is the ledger export; project it with
  python3 tools/export_coding_session.py --jsonl FILE
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from ..adapters.stores.event_store import SqliteEventStore
from .mock_coding_tape import brief_from_task_dir, coding_tape
from .determinism import SystemClock
from .model_selection import ModelUnavailable, select_model
from .repair import StopReason, drive_until_green
from .root import HarnessSession, Runtime, SessionPorts, TaskContext
from .session_log import session_log

DEFAULT_BRIEF = ("Inspect the workspace, make the failing suite pass, and run "
                 "the tests through the allowlisted process verb.")


def run_lab_task(
    pack_name: str,
    task_dir: Path | str,
    *,
    model_port: str = "mock",
    model_name: str | None = None,
    tape: Sequence[Any] = (),
    interactive: bool = False,
    max_turns: int = 8,
    max_attempts: int = 4,
    brief: str = DEFAULT_BRIEF,
    oracle: Any = None,
    jsonl_out: Path | str | None = None,
) -> dict[str, Any]:
    """Compose, run, and report from the ledger. Never from a literal."""

    task_path = Path(task_dir)
    if not task_path.is_dir():
        # Counted, not skipped -- the denominator lesson from W13-A.
        return {
            "harness": pack_name, "taskDir": str(task_path),
            "outcome": "inconclusive:workspace_missing",
            "detail": "task directory does not exist", "turns": 0, "session": [],
        }

    harness_preview = Runtime.compose(pack_name, episode_id="lab-episode-1")
    if not tape and model_port == "mock":
        # `S18-A-01`. An empty tape proposes nothing, so every MOCK run
        # reported `turns: 0 / model_not_invoked` -- a failure of the brain
        # binding, not a measurement. The scripted tape takes real turns and
        # still cannot fix anything, which is the correct MOCK.
        tape = coding_tape(verbs=harness_preview.verbs)

    try:
        selected = select_model(model_port, model_name=model_name, tape=tape)
    except ModelUnavailable as unavailable:
        # Fail closed with a named reason. Not a skip, not a pass.
        return {
            "harness": pack_name, "taskDir": str(task_path),
            "outcome": StopReason.INSTRUMENT_ERROR,
            "modelPort": unavailable.port,
            "detail": unavailable.reason, "turns": 0, "session": [],
        }

    harness = harness_preview
    store = SqliteEventStore(":memory:")
    # The task states its own goal (`TASK.md`); the harness telling the model
    # what the task is would be a different experiment.
    brief = brief_from_task_dir(task_path) or brief

    def run_once(attempt: int) -> Any:
        ports = SessionPorts(
            model=selected.model,
            environment=_environment_for(task_path),
            clock=SystemClock(), store=store, interactive=interactive)
        task = TaskContext(
            brief=brief, repo_path=task_path,
            run_id=f"lab-run-{attempt}", episode_id="lab-episode-1",
            max_turns=max_turns)
        return HarnessSession(harness, ports, task).run()

    outcome = drive_until_green(
        run_once,
        oracle=oracle or _verdict_is_green,
        max_attempts=max_attempts,
    )

    events = outcome.results[-1].events if outcome.results else ()
    log = session_log(events)
    if jsonl_out is not None:
        _write_jsonl(Path(jsonl_out), store, "lab-episode-1")

    return {
        "harness": harness.harness,
        "taskDir": str(task_path),
        "outcome": outcome.stop_reason,
        "attempts": outcome.attempts,
        "turns": outcome.telemetry.turns,
        "promptTokens": outcome.telemetry.prompt_tokens,
        "completionTokens": outcome.telemetry.completion_tokens,
        "mode": "interactive" if interactive else "benchmark",
        "session": [entry.to_dict() for entry in log.entries],
        "deadEnds": [dict(entry) for entry in log.dead_end_details],
        "cacheMissAttribution": [dict(e) for e in log.cache_miss_attribution()],
        "detail": outcome.detail,
        **selected.to_dict(),
    }


def _verdict_is_green(result: Any) -> bool:
    """The oracle is the run's own exterior verdict, never a suite run here."""
    verdict = getattr(result, "verdict", None)
    return bool(verdict is not None and getattr(verdict, "passed", False))


def _environment_for(task_path: Path) -> Any:
    from ..adapters.environment.git import GitEnvironmentAdapter

    return GitEnvironmentAdapter(str(task_path))


def _write_jsonl(target: Path, store: Any, episode_id: str) -> int:
    """Export the **ledger**, not the in-process trace.

    `RunResult.events` are kernel `Event` objects; the store holds `vg.4`
    `EventEnvelope`s. Writing the former produced a file
    `tools/export_coding_session.py` refused with
    `must be 'vg.4', got None` -- correctly, because it was not a ledger
    export. The store is the ledger, so the export reads the store.
    """
    from ..adapters.stores.ledger_jsonl import export_jsonl
    from ..ports.event_store import EventRange

    read = store.read(EventRange(episode_id=episode_id))
    envelopes = read.value if read.ok and read.value is not None else ()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as writer:
        return export_jsonl(envelopes, writer)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one task against a frozen harness")
    parser.add_argument("--pack", required=True)
    parser.add_argument("--task-dir", required=True)
    parser.add_argument("--model", default="mock",
                        choices=("mock", "ollama", "openrouter", "deepseek"))
    parser.add_argument("--model-name", default=None)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--interactive", action="store_true")
    mode.add_argument("--benchmark", action="store_true")
    parser.add_argument("--max-turns", type=int, default=8)
    parser.add_argument("--max-attempts", type=int, default=4)
    parser.add_argument("--jsonl-out", default=None)
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()
    result = run_lab_task(
        args.pack, args.task_dir,
        model_port=args.model, model_name=args.model_name,
        interactive=args.interactive, max_turns=args.max_turns,
        max_attempts=args.max_attempts, jsonl_out=args.jsonl_out,
    )
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result["outcome"])
    return 0 if result["outcome"] == StopReason.ORACLE_GREEN else 1


if __name__ == "__main__":
    raise SystemExit(main())
