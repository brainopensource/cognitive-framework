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
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence

from ..adapters.stores.event_store import SqliteEventStore
from ..adapters.stores.repo_index import FileRepoIndex
from .mock_coding_tape import (
    brief_from_task_dir,
    coding_tape,
    verify_argv_from_task,
)
from .determinism import SystemClock
from .model_selection import ModelUnavailable, select_model
from .outcome_labels import classify_instrument_error
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
    approve_writes: bool = False,
    isolate: bool = True,
    tier_escalation: bool = False,
    tiers: Sequence[str] | None = None,
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

    # Keep the caller's task identity in the report.  `task_path` becomes an
    # ephemeral isolated copy below, and must never escape as a dangling path.
    reported_task_path = task_path

    harness_preview = Runtime.compose(pack_name, episode_id="lab-episode-1")
    if not tape and model_port == "mock":
        # `S18-A-01`. An empty tape proposes nothing, so every MOCK run
        # reported `turns: 0 / model_not_invoked` -- a failure of the brain
        # binding, not a measurement. The scripted tape takes real turns and
        # still cannot fix anything, which is the correct MOCK.
        # One pass per attempt, or attempt 2 exhausts the tape and reports
        # `tape_exhausted` -- a true statement about the fake, and a
        # useless one about the loop.
        tape = coding_tape(verbs=harness_preview.verbs,
                           attempts=max(int(max_attempts), 1))

    # Every run gets its own copy. Running in place would let one run inherit
    # the previous run's edits -- the second arm would then be scored on work
    # the first arm did, which is the quietest way to fake a result.
    cleanup_roots: list[Path] = []
    if isolate:
        staging = Path(tempfile.mkdtemp(prefix="vg-lab-ws-"))
        cleanup_roots.append(staging)
        task_path = Path(shutil.copytree(task_path, staging / task_path.name))

    try:
        selected = select_model(
            model_port,
            model_name=model_name or (tiers[0] if tier_escalation and tiers else None),
            tape=tape,
        )
    except ModelUnavailable as unavailable:
        # Fail closed with a named reason. Not a skip, not a pass.
        result = {
            "harness": pack_name, "taskDir": str(reported_task_path),
            "outcome": classify_instrument_error(unavailable.reason),
            "modelPort": unavailable.port,
            "detail": unavailable.reason, "turns": 0, "session": [],
        }
        for root in reversed(cleanup_roots):
            shutil.rmtree(root, ignore_errors=True)
        return result

    # `--approve-writes` is a **labelled lab departure**, never a default.
    # BENCHMARK denies privileged verbs with no human (`K-17`), so a repair can
    # only be measured with an approver in the loop. Recording that in
    # `labDepartures` is what stops an assisted run being read as an
    # unattended one.
    departures: list[str] = []
    if not isolate:
        # `S050-C-02`: mutating the caller's own workspace is a labelled lab
        # departure for the same reason `--approve-writes` is one -- a run
        # that silently wrote outside its own sandbox copy is not the
        # measurement the isolated default exists to produce.
        departures.append("in_place")
    approver = None
    approval_key = None
    if approve_writes:
        from .governance.approvals import OperatorSigner

        signer = OperatorSigner(b"vanguard-lab-operator-key")
        approver = lambda challenge: signer.approve(challenge, reviewer="lab-operator")
        approval_key = signer.public_bytes
        interactive = True
        departures.append("auto_approved_writes")

    harness = harness_preview
    store = SqliteEventStore(":memory:")
    # The task states its own goal (`TASK.md`); the harness telling the model
    # what the task is would be a different experiment.
    brief = brief_from_task_dir(task_path) or brief

    def run_once(attempt: int) -> Any:
        # Each attempt is its own **episode**, not a re-entry into the last
        # one. Re-using one episode id across attempts restarted the ledger's
        # sequence counter and wrote duplicate seqs, which `reduce_event`
        # correctly refused with `Non-monotonic sequence`. An attempt starts
        # from the workspace as it stands, so it is a new episode; the run id
        # is what groups them.
        episode_id = f"lab-episode-{attempt}"
        ports = SessionPorts(
            model=selected.model,
            environment=_environment_for(task_path, cleanup_roots),
            clock=SystemClock(), store=store,
            index=FileRepoIndex() if harness.index_component is not None else None,
            interactive=interactive,
            approver=approver, approval_key=approval_key)
        task = TaskContext(
            brief=brief, repo_path=task_path,
            run_id="lab-run", episode_id=episode_id, max_turns=max_turns)
        return HarnessSession(harness, ports, task).run()

    # The oracle runs the task's **own** declared command, after the episode,
    # through the same sandbox. Reading the agent's `proc.exec` receipts
    # instead would let a model exit 0 on any trivial command and score green.
    verify_argv = verify_argv_from_task(task_path)
    environment_for_oracle = _environment_for(task_path, cleanup_roots)

    def declared_oracle(_result: Any) -> bool:
        if verify_argv is None:
            return False
        return _verify(environment_for_oracle, verify_argv)

    outcome = drive_until_green(
        run_once,
        oracle=oracle or (declared_oracle if verify_argv else _verdict_is_green),
        max_attempts=max_attempts,
    )

    # `S20-A-01`. When a run produced no turn, the *provider's* reason is the
    # finding -- `model_not_invoked` is only the shape of the failure, not its
    # cause, and reporting the shape made a timeout read like a model that
    # scored zero.
    last = outcome.results[-1] if outcome.results else None
    detail = outcome.detail
    stop_reason = outcome.stop_reason
    if stop_reason == StopReason.INSTRUMENT_ERROR:
        if last is not None:
            detail = getattr(last, "detail", "") or detail
        # `S21-A-01`. `instrument_error` is a category, not a finding: the
        # provider never answering, a local backend timing out, and a model emitting
        # a shape the translator refuses are different facts that all reduced
        # to one word, and each of them read like the model scoring zero.
        stop_reason = classify_instrument_error(detail)

    events = last.events if last is not None else ()
    log = session_log(events)
    if jsonl_out is not None:
        # Exported by run, so every attempt's episode is in the one file.
        _write_jsonl(Path(jsonl_out), store, "lab-run")

    result = {
        "harness": harness.harness,
        "taskDir": str(reported_task_path),
        "outcome": stop_reason,
        "attempts": outcome.attempts,
        "turns": outcome.telemetry.turns,
        "promptTokens": outcome.telemetry.prompt_tokens,
        "completionTokens": outcome.telemetry.completion_tokens,
        "mode": "interactive" if interactive else "benchmark",
        "session": [entry.to_dict() for entry in log.entries],
        "deadEnds": [dict(entry) for entry in log.dead_end_details],
        "cacheMissAttribution": [dict(e) for e in log.cache_miss_attribution()],
        "detail": detail,
        "verifyArgv": verify_argv,
        "labDepartures": departures,
        # `C-01`: a refusal that produced no turn is still on the ledger.
        "terminalRefusal": log.terminal_refusal,
        **selected.to_dict(),
    }
    # A benchmark may launch hundreds of sessions.  The isolated workspace and
    # sealed worker bundle are per-run state, never evidence, so retaining them
    # after the ledger has been exported is both a disk leak and a needless
    # exposure window.  `ignore_errors` keeps an already-complete measurement
    # from being rewritten as a cleanup failure.
    for root in reversed(cleanup_roots):
        shutil.rmtree(root, ignore_errors=True)
    return result


def _verify(environment: Any, argv: Sequence[str]) -> bool:
    """Run the declared command in the sandbox and read its exit code.

    Exterior to the episode: the model cannot choose it, cannot see it, and
    cannot make it pass by running something else.
    """
    from ..ports.environment import EffectRequest as EnvironmentRequest

    result = environment.apply(EnvironmentRequest(
        verb="proc.exec", action="exec", args={"argv": list(argv)},
        command=list(argv)))
    if not result.ok or result.value is None:
        return False
    return getattr(result.value, "outcome", "") == "ok"


def _verdict_is_green(result: Any) -> bool:
    """The oracle is the run's own exterior verdict, never a suite run here."""
    verdict = getattr(result, "verdict", None)
    return bool(verdict is not None and getattr(verdict, "passed", False))


def _environment_for(task_path: Path, cleanup_roots: list[Path] | None = None) -> Any:
    """The sandboxed environment, exactly as `execute_harness` composes it.

    This used to return `GitEnvironmentAdapter`, which runs `proc.exec` through
    `subprocess.run` **on the host**. Every lab run was therefore executing the
    task's test command uncontained, and a benchmark whose commands escape the
    sandbox is measuring the host, not the harness (`N-06`). It is also the
    first anti-cheat condition: host `pytest` is not the oracle.

    The bubblewrap worker also reports `outcome="failed"` on a non-zero exit,
    which is what makes a ledger-derived oracle possible at all.
    """
    from ..adapters.environment.sandboxed import SandboxedEnvironmentAdapter
    from ..adapters.sandbox.rootless import RootlessSandboxRunner
    from ..adapters.sandbox.worker import WorkerProtocol
    from .root import _bwrap_path

    repo = task_path.resolve()
    sealed_dir = Path(tempfile.mkdtemp(prefix="vg-lab-sealed-"))
    if cleanup_roots is not None:
        cleanup_roots.append(sealed_dir)
    sealed_bundle = sealed_dir / "bundle"
    sealed_bundle.write_bytes(
        b"sealed evaluator mount is intentionally unavailable to worker\n")
    worker = WorkerProtocol(RootlessSandboxRunner(
        repo, evaluator_bundle=sealed_bundle, runtime=_bwrap_path()))
    return SandboxedEnvironmentAdapter(
        worker, repo, environment_id=f"workspace:{repo}")


def _write_jsonl(target: Path, store: Any, run_id: str) -> int:
    """Export the **ledger**, not the in-process trace.

    `RunResult.events` are kernel `Event` objects; the store holds `vg.4`
    `EventEnvelope`s. Writing the former produced a file
    `tools/export_coding_session.py` refused with
    `must be 'vg.4', got None` -- correctly, because it was not a ledger
    export. The store is the ledger, so the export reads the store.
    """
    from ..adapters.stores.ledger_jsonl import export_jsonl
    from ..ports.event_store import EventRange

    read = store.read(EventRange(run_id=run_id))
    envelopes = read.value if read.ok and read.value is not None else ()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as writer:
        return export_jsonl(envelopes, writer)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one task against a frozen harness")
    parser.add_argument("--pack", required=True)
    parser.add_argument("--task-dir", required=True)
    parser.add_argument("--model", default="mock",
                        choices=("mock", "ollama", "openrouter", "deepseek", "router"))
    parser.add_argument("--model-name", default=None)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--interactive", action="store_true")
    mode.add_argument("--benchmark", action="store_true")
    parser.add_argument("--max-turns", type=int, default=8)
    parser.add_argument("--max-attempts", type=int, default=4)
    parser.add_argument("--jsonl-out", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--in-place", action="store_true",
                        help="Mutate --task-dir directly instead of an isolated copy "
                             "(labelled lab departure, recorded in labDepartures)")
    parser.add_argument("--tier-escalation", action="store_true",
                        help="Select the initial tier; outcome-driven escalation is coordinated externally")
    parser.add_argument("--tiers", nargs="+", default=None,
                        help="Ordered list of models for tier escalation")

    args = parser.parse_args()
    result = run_lab_task(
        args.pack, args.task_dir,
        model_port=args.model, model_name=args.model_name,
        interactive=args.interactive, max_turns=args.max_turns,
        max_attempts=args.max_attempts, jsonl_out=args.jsonl_out,
        tier_escalation=args.tier_escalation, tiers=args.tiers,
        isolate=not args.in_place,
    )
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result["outcome"])
    return 0 if result["outcome"] == StopReason.ORACLE_GREEN else 1


if __name__ == "__main__":
    raise SystemExit(main())
