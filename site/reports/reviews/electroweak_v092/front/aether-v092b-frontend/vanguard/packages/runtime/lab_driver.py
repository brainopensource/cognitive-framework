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

It now composes a real `Harness`, enters the runtime-owned activation boundary, and reports
what the ledger says. Greenfield and bugfix are the same path: one compose, one
episode tree, tools, receipts, ledger. There is no second agent loop here --
the repair driver re-enters `Runtime.run_composed()` and nothing else.

CLI:
  python3 -m vanguard.packages.runtime.lab_driver --pack vg-code-default --task-dir DIR
      [--model mock|ollama|openrouter|deepseek] [--model-name TAG]
      [--interactive | --benchmark] [--max-turns N] [--max-attempts N]
      [--jsonl-out FILE] [--json]

The JSONL is the ledger export; project it with the session JSONL exporter.
"""

from __future__ import annotations

import argparse
import json
import secrets
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence

from ..adapters.stores.event_store import SqliteEventStore
from ..adapters.stores.blob_store import FileBlobStore
from ..adapters.stores.repo_index import FileRepoIndex
from ..ports.event_store import Result as PortResult
from ..domain.canonicalisation.digest import digest_of
from .mock_episode_tape import (
    brief_from_task_dir,
    episode_tape,
    verify_argv_from_task,
)
from .determinism import SystemClock
from .model_selection import ModelUnavailable, select_model
from .outcome_labels import classify_instrument_error
from .repair import StopReason, drive_until_green
from .root import Runtime, SessionPorts, TaskContext
from .session_log import session_log
from .state_contract import ensure_state_directory
from .workspace import get_workspace_path, validate_workspace_path

DEFAULT_BRIEF = ("Inspect the workspace, make the failing suite pass, and run "
                 "the tests through the allowlisted process verb.")


def _lab_operator_signer() -> Any:
    """The installation's operator key, or a run-scoped ephemeral identity.

    The lab is not an interactive product surface, so it must not *require*
    `vanguard init`; but it must also not fall back to a constant shared by
    every checkout. An ephemeral key is attributable to this run and to nothing
    else, which is the honest default when no operator identity is installed.
    """
    from .governance.approvals import OperatorSigner
    from .keys import KeyMaterialError, load_operator_signer

    try:
        return load_operator_signer(allow_create=False)
    except KeyMaterialError:
        return OperatorSigner(secrets.token_bytes(32), key_id="lab-ephemeral-operator")


def run_lab_task(
    pack_name: str,
    task_dir: Path | str,
    *,
    model_port: str = "mock",
    model_name: str | None = None,
    models: Sequence[str] | None = None,
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
    sandbox_mode: str = "rootless",
    allow_paid: bool = False,
    state_dir: Path | str | None = None,
    reasoning_effort: str | None = None,
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
        tape = episode_tape(verbs=harness_preview.verbs,
                           attempts=max(int(max_attempts), 1))

    # Every run gets its own copy. Running in place would let one run inherit
    # the previous run's edits -- the second arm would then be scored on work
    # the first arm did, which is the quietest way to fake a result.
    cleanup_roots: list[Path] = []
    if isolate:
        staging = Path(tempfile.mkdtemp(prefix="vg-lab-ws-", dir=get_workspace_path("tmp")))
        cleanup_roots.append(staging)
        task_path = Path(shutil.copytree(task_path, staging / task_path.name))

    try:
        selected = select_model(
            model_port,
            model_name=model_name or (tiers[0] if tier_escalation and tiers else None),
            models=models,
            tape=tape,
            allow_paid=allow_paid,
            reasoning_effort=reasoning_effort,
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
    grant = None
    if not isolate:
        # `S050-C-02`: mutating the caller's own workspace is a labelled lab
        # departure for the same reason `--approve-writes` is one -- a run
        # that silently wrote outside its own sandbox copy is not the
        # measurement the isolated default exists to produce.
        departures.append("in_place")
    approver = None
    approval_key = None
    if interactive and not isolate:
        # `S060-G-01` / `TSK-HAR-002`: INTERACTIVE `--in-place` mints a bounded
        # AutonomousGrant for the task workspace. BENCHMARK mode must not mint.
        from .autonomous_grant import create_autonomous_grant
        from .governance.approvals import OperatorSigner

        # The installation's operator key, or a run-scoped ephemeral identity
        # when none is initialised. A shared literal seed made every grant in
        # every checkout attributable to the same key, so the signature proved
        # nothing about who authorised the run.
        signer = _lab_operator_signer()
        grant = create_autonomous_grant(
            task_path,
            allowed_verbs=tuple(harness_preview.verbs),
            max_turns=max_turns,
            max_attempts=max_attempts,
            signer=signer,
        )
        max_turns = min(max_turns, grant.max_turns)
        max_attempts = min(max_attempts, grant.max_attempts)
        approver = lambda challenge: signer.approve(challenge, reviewer=grant.reviewer)
        approval_key = {signer.key_id: signer.public_bytes}
    elif approve_writes:
        from .governance.approvals import OperatorSigner
        from .autonomous_grant import create_autonomous_grant

        signer = OperatorSigner(secrets.token_bytes(32), key_id="lab-operator")
        grant = create_autonomous_grant(
            task_path,
            allowed_verbs=tuple(harness_preview.verbs),
            max_turns=max_turns,
            max_attempts=max_attempts,
            signer=signer,
        )
        max_turns = min(max_turns, grant.max_turns)
        max_attempts = min(max_attempts, grant.max_attempts)
        approver = lambda challenge: signer.approve(challenge, reviewer=grant.reviewer)
        approval_key = {signer.key_id: signer.public_bytes}
        interactive = True
        departures.append("auto_approved_writes")

    harness = harness_preview
    resolved_state: Path | None = None
    if state_dir is not None:
        resolved_state = validate_workspace_path(state_dir)
        ensure_state_directory(resolved_state)
    elif model_port != "mock":
        run_identifier = f"lab-run-{secrets.token_hex(6)}"
        resolved_state = get_workspace_path("state", run_identifier)
        ensure_state_directory(resolved_state)

    store = SqliteEventStore(
        resolved_state / "events.sqlite3" if resolved_state is not None else ":memory:")
    blobs = FileBlobStore(resolved_state / "blobs") if resolved_state is not None else None
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
            environment=_bind_grant(
                _environment_for(task_path, cleanup_roots, sandbox_mode=sandbox_mode),
                grant),
            clock=SystemClock(), store=store,
            blobs=blobs,
            index=FileRepoIndex() if harness.index_component is not None else None,
            interactive=interactive,
            approver=approver, approval_key=approval_key)
        task = TaskContext(
            brief=brief, repo_path=task_path,
            run_id="lab-run", episode_id=episode_id, max_turns=max_turns)
        return Runtime.run_composed(harness, ports, task)

    # The oracle runs the task's **own** declared command, after the episode,
    # through the same sandbox. Reading the agent's `proc.exec` receipts
    # instead would let a model exit 0 on any trivial command and score green.
    verify_argv = verify_argv_from_task(task_path)
    environment_for_oracle = _bind_grant(
        _environment_for(task_path, cleanup_roots, sandbox_mode=sandbox_mode), grant)

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

    episode_trajectories = [
        getattr(item, "trajectory", None)
        for item in outcome.results
        if isinstance(getattr(item, "trajectory", None), dict)
    ]
    cost_values = [
        trajectory.get("cost", {}).get("usd_micros")
        for trajectory in episode_trajectories
        if isinstance(trajectory.get("cost"), dict)
    ]
    cost_statuses = [
        trajectory.get("cost", {}).get("measurement_status", {})
        .get("usd_micros", {}).get("status")
        for trajectory in episode_trajectories
        if isinstance(trajectory.get("cost"), dict)
    ]
    observed_cost = (
        sum(int(value) for value in cost_values)
        if cost_values and len(cost_values) == len(episode_trajectories)
        and all(status == "measured" for status in cost_statuses)
        and all(isinstance(value, int) and not isinstance(value, bool) for value in cost_values)
        else None
    )
    result = {
        "harness": harness.harness,
        "taskDir": str(reported_task_path),
        "outcome": stop_reason,
        "attempts": outcome.attempts,
        "turns": outcome.telemetry.turns,
        "promptTokens": outcome.telemetry.prompt_tokens,
        "completionTokens": outcome.telemetry.completion_tokens,
        # Repair attempts are one durable run.  Expose their measured total
        # separately from the last episode trajectory so callers cannot
        # undercount a paid retry.
        "observedCostMicros": observed_cost,
        "costProvenance": "measured" if observed_cost is not None else "unknown",
        "mode": "interactive" if interactive else "benchmark",
        "session": [entry.to_dict() for entry in log.entries],
        "deadEnds": [dict(entry) for entry in log.dead_end_details],
        "cacheMissAttribution": [dict(e) for e in log.cache_miss_attribution()],
        "detail": detail,
        "verifyArgv": verify_argv,
        "labDepartures": departures,
        # `C-01`: a refusal that produced no turn is still on the ledger.
        "terminalRefusal": log.terminal_refusal,
        "grantId": grant.grant_id if grant is not None else None,
        "trajectory": getattr(last, "trajectory", None) if last is not None else None,
        "trajectoryDigest": (
            digest_of(getattr(last, "trajectory"))
            if last is not None and isinstance(getattr(last, "trajectory", None), dict)
            else None
        ),
        "eventStoreIdentity": digest_of({"db_path": store.db_path, "run_id": "lab-run"}),
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
    """The oracle is the run's own exterior verdict, never a suite run here.

    A `Verdict` carries no `passed` flag; the signed pass-signal is
    `outcome == "claims"` with every claim holding. An inconclusive verdict,
    a missing verdict, or an unsigned binding is not green (`ports/evaluator.py`).
    """
    verdict = getattr(result, "verdict", None)
    if verdict is None or getattr(verdict, "outcome", "") != "claims":
        return False
    claims = getattr(verdict, "claims", ()) or ()
    return bool(claims) and all(bool(claim.get("holds")) for claim in claims)


class _GrantBoundEnvironment:
    """Enforces `AutonomousGrant` at the environment port (`TSK-HAR-002`)."""

    def __init__(self, inner: Any, grant: Any) -> None:
        self._inner = inner
        self._grant = grant

    def profile(self) -> Any:
        return self._inner.profile()

    def snapshot(self) -> Any:
        return self._inner.snapshot()

    def observe(self, req: Any, grant: Any = None) -> Any:
        denied = self._deny(getattr(req, "action", "fs.read"), getattr(req, "path", None), None)
        if denied is not None:
            return denied
        return self._inner.observe(req, grant)

    def preview(self, req: Any, grant: Any = None) -> Any:
        denied = self._deny_effect(req)
        if denied is not None:
            return denied
        return self._inner.preview(req, grant)

    def apply(self, req: Any, grant: Any = None) -> Any:
        denied = self._deny_effect(req)
        if denied is not None:
            return denied
        return self._inner.apply(req, grant)

    def reconcile(self, receipt: Any, grant: Any = None) -> Any:
        return self._inner.reconcile(receipt, grant)

    def compensate(self, receipt: Any, grant: Any = None) -> Any:
        return self._inner.compensate(receipt, grant)

    def dispose(self) -> Any:
        return self._inner.dispose()

    def _deny_effect(self, req: Any) -> Any:
        args = getattr(req, "args", {}) or {}
        path = args.get("path") if isinstance(args, dict) else None
        command = getattr(req, "command", None)
        if command is None and isinstance(args, dict):
            command = args.get("argv") or args.get("command")
        verb = getattr(req, "verb", None) or getattr(req, "action", "")
        return self._deny(str(verb), path, command)

    def _deny(self, verb: str, path: Any, command: Any) -> Any:
        from .autonomous_grant import validate_grant_request

        mapped = verb
        if "." not in verb:
            mapped = {
                "read": "fs.read",
                "search": "fs.search",
                "list": "fs.read",
                "stat": "fs.read",
                "write": "fs.write",
                "patch": "patch.apply",
                "exec": "proc.exec",
            }.get(verb, verb)
        argv = tuple(command) if command else None
        ok, reason = validate_grant_request(
            self._grant, verb=mapped, target_path=path, command_argv=argv)
        if ok:
            return None
        return PortResult.fail("denied", reason)


def _bind_grant(environment: Any, grant: Any) -> Any:
    if grant is None:
        return environment
    return _GrantBoundEnvironment(environment, grant)


def _environment_for(
    task_path: Path,
    cleanup_roots: list[Path] | None = None,
    *,
    sandbox_mode: str = "rootless",
) -> Any:
    """The sandboxed environment, exactly as `execute_harness` composes it.

    This used to return `GitEnvironmentAdapter`, which runs `proc.exec` through
    `subprocess.run` **on the host**. Every lab run was therefore executing the
    task's test command uncontained, and a benchmark whose commands escape the
    sandbox is measuring the host, not the harness (`N-06`). It is also the
    first anti-cheat condition: host `pytest` is not the oracle.

    The bubblewrap worker also reports `outcome="failed"` on a non-zero exit,
    which is what makes a ledger-derived oracle possible at all.
    """
    if sandbox_mode == "host-dev":
        # Local CLI development only. This keeps the same EnvironmentPort and
        # receipts while making WSL/native development usable. It is not a
        # containment report and cannot be selected by RF-85 release code.
        from ..adapters.environment.git import GitEnvironmentAdapter
        return GitEnvironmentAdapter(
            task_path.resolve(),
            environment_id=f"workspace-host-dev:{task_path.resolve()}",
        )
    if sandbox_mode != "rootless":
        raise ValueError("sandbox_mode must be 'rootless' or 'host-dev'")

    from ..adapters.environment.sandboxed import SandboxedEnvironmentAdapter
    from ..adapters.sandbox.rootless import RootlessSandboxRunner
    from ..adapters.sandbox.worker import WorkerProtocol
    from .root import _bwrap_path

    repo = task_path.resolve()
    sealed_dir = Path(tempfile.mkdtemp(prefix="vg-lab-sealed-", dir=get_workspace_path("sandboxes")))
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
    the session JSONL exporter refused with
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
                        choices=("mock", "lam", "ollama", "openrouter", "deepseek", "router"))
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
    parser.add_argument(
        "--sandbox", choices=("rootless", "host-dev"), default="rootless",
        help="Execution boundary; host-dev is explicit, local-only, and not RF-85 eligible",
    )
    parser.add_argument(
        "--allow-paid", action="store_true",
        help="Authorise paid OpenRouter models (overrides free-band refusal)",
    )
    parser.add_argument(
        "--approve-writes", action="store_true",
        help="Auto-approve write proposals via lab operator signer (labelled lab departure)",
    )

    args = parser.parse_args()
    result = run_lab_task(
        args.pack, args.task_dir,
        model_port=args.model, model_name=args.model_name,
        interactive=args.interactive, max_turns=args.max_turns,
        max_attempts=args.max_attempts, jsonl_out=args.jsonl_out,
        tier_escalation=args.tier_escalation, tiers=args.tiers,
        sandbox_mode=args.sandbox,
        isolate=not args.in_place,
        allow_paid=args.allow_paid,
        approve_writes=args.approve_writes,
    )
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result["outcome"])
    return 0 if result["outcome"] == StopReason.ORACLE_GREEN else 1


if __name__ == "__main__":
    raise SystemExit(main())
