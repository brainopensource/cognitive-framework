---
id: report.electroweak.solution-a.full-code-forge-wave-8
class: report
authority: non-canonical
canonical_for: []
status: proposal
owner: repository-governance
version: 0.9.2a2
last_verified: 2026-08-31
---

# AETHER FORGE — Full Code Completion Manifest — Wave 8

## Real coding execution, patch application, verification receipts, benchmark integrity, release gates, and end-to-end acceptance

- Exact branch subject: `f242ced297216109736975376802f1e3dc4e29ce`.
- Backend FORGE only; frontend is excluded.
- This complement closes production integration omitted by waves 1–4.
- Code blocks contain complete affected modules or complete affected classes/functions so call sites can be changed without guessing signatures.
- Existing kernel invariants, authority, budgets, events, artifacts, and recovery remain authoritative.

## Required production delta

Replace every synthetic benchmark success path with a real task workspace,
actual tool loop, captured patch, patch application, targeted tests, external
evaluator verdict, and immutable evidence bundle.  A non-empty model response is
not success.  `grounded` and `verified` cannot derive from model prose.  Dry-run
may validate shape and accounting but must be labeled synthetic and excluded
from capability claims.  Baseline/oracle failure invalidates the task episode;
it does not become an agent failure or a success.  Preregister attempts, model,
temperature, budgets, task set, evaluator, environment image, selection policy,
and aggregation before execution.  Ensure driver attempt count equals the
preregistered primary attempt count.  Every result must be reproducible from
task subject, patch artifact, environment identity, receipts, evaluator verdict,
trajectory, and cost/token telemetry.

## Exact edit map

1. Modify `runtime/lab_driver.py`: run the composed harness against a controlled
   repository and require observed workspace change for patch tasks.
2. Modify `runtime/dogfood.py`: distinguish execution completion, patch
   production, verification, and evaluator success.
3. Modify benchmark runner: remove direct OpenRouter-only shortcut; inject the
   canonical model port and runtime composition.
4. Add `benchmarks/forge/task_spec.py`: immutable task and oracle contracts.
5. Add `benchmarks/forge/workspace.py`: checkout, reset, digest, patch capture,
   and hermetic environment identity.
6. Add `benchmarks/forge/evaluator.py`: external evaluator invocation and signed
   verdict binding to task/patch/workspace.
7. Add `benchmarks/forge/runner.py`: preregistration enforcement, episodes,
   aggregation, failure classification, and evidence export.
8. Add `benchmarks/forge/report.py`: resolved rate, pass@k, cost, latency,
   verification, patch, retry, recovery and ablation metrics.
9. Add canary, smoke, heldout, contamination, replay, provider-failure, and
   evaluator-failure tests.

## Truthful success invariant

```text
resolved =
task subject valid
and baseline/oracle valid
and runtime episode completed
and required patch exists
and patch applies to exact subject
and fresh local verification passes
and external evaluator returns a valid passing verdict
and verdict binds task + subject + patch + environment
```

## Complete affected code owners

### File: `vanguard/packages/runtime/lab_driver.py`

**Repository path:** `vanguard/packages/runtime/lab_driver.py`

```python
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
```

### File: `vanguard/packages/runtime/dogfood.py`

**Repository path:** `vanguard/packages/runtime/dogfood.py`

```python
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
```

### File: `vanguard/packages/runtime/evaluator_gateway.py`

**Repository path:** `vanguard/packages/runtime/evaluator_gateway.py`

```python
"""Evaluator gateway: the sole legal writer of `VerdictRecorded` (ADR-0076 §5/§6).

`LedgerEmitter` already refuses `VerdictRecorded` from every writer role but
`evaluator_gateway` (`PRIVILEGED_KIND_OWNERS` in `ledger_emitter.py`); this
module is the one call site that holds that facade. It never constructs a
verdict -- the exterior evaluator daemon does that, under its own signature
(`adapters/evaluators/daemon.py`) -- it only ledgers the bound `SignedVerdict`
a `Verdict` already carries, or refuses when there is nothing bound to ledger.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..domain.ledger.events import EventEnvelope
from ..ports.evaluator import Verdict
from .ledger_emitter import LedgerEmitter

__all__ = ["record_verdict", "signed_verdict_payload"]


def signed_verdict_payload(verdict: Verdict) -> Mapping[str, Any] | None:
    """The `SignedVerdict` object exactly as the daemon signed it, or `None`.

    `None` means the daemon never produced a bound, signed body -- no
    evaluator was reachable, or a legacy/unsigned response came back. Nothing
    here repairs that into a pass; the caller gets nothing to ledger.
    """
    if verdict.binding is None or not verdict.signature:
        return None
    return {**dict(verdict.binding), "signature": verdict.signature}


def record_verdict(
    emitter: LedgerEmitter,
    *,
    run_id: str,
    principal: str,
    episode_id: str,
    verdict: Verdict,
) -> EventEnvelope | None:
    """Ledger `VerdictRecorded{SignedVerdict}` for a bound, signed verdict.

    Returns the appended envelope, or `None` when `verdict` carries no bound
    signature -- F1 (a fabricated pass) cannot reach the ledger through this
    call because there is nothing here to fabricate: the payload is always
    the daemon's own signed bytes, never reconstructed from `outcome`/`claims`.
    """
    payload = signed_verdict_payload(verdict)
    if payload is None:
        return None
    return emitter.evaluator_gateway().emit_kind(
        "VerdictRecorded",
        run_id=run_id,
        principal=principal,
        episode_id=episode_id,
        payload={"signedVerdict": dict(payload)},
    )
```

### File: `vanguard/packages/runtime/trajectory.py`

**Repository path:** `vanguard/packages/runtime/trajectory.py`

```python
"""Assemble `mhf.trajectory/2` (and historical `/1`) at episode completion (1.3-D, F-12, RF-23, ADR-0078, ADR-0096 §14, ADR-0097 §1).

Production writers single-write `mhf.trajectory/2`, carrying:
- Complete artifact index (`artifacts`)
- Context, compaction, and cache provenance (`provenance`)
- Exact model input/output references per turn
- Proof-honest `reproducibility_at_run_close`
- Capture status and policy
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ..domain.canonicalisation.digest import digest_of
from ..kernel.model import Event
from .reproducibility import (
    ReproducibilityVector,
    assess_reproducibility,
)


def signed_verdict_object(verdict: Any) -> Mapping[str, Any] | None:
    binding = getattr(verdict, "binding", None)
    signature = getattr(verdict, "signature", None)
    if not binding or not signature:
        return None
    return {**dict(binding), "signature": signature}


def _resolve_model_route(model: Any, ctx: Mapping[str, Any] | None = None) -> dict[str, Any]:
    provider = getattr(model, "provider", None) or (ctx.get("provider") if ctx else None)
    model_name = getattr(model, "model", None) or getattr(model, "model_name", None) or (ctx.get("model") if ctx else None)
    if not provider:
        cls_name = type(model).__name__.lower() if model is not None else ""
        if "fake" in cls_name:
            provider = "fake"
            model_name = model_name or "fake-model"
        elif "scripted" in cls_name:
            provider = "scripted"
            model_name = model_name or "scripted-cassette"
        elif "ollama" in cls_name:
            provider = "ollama"
            model_name = model_name or "deepseek-r1"
        elif "openrouter" in cls_name:
            provider = "openrouter"
            model_name = model_name or "openrouter-default"
        else:
            provider = "scripted"
            model_name = model_name or "default-model"
    else:
        model_name = model_name or "default-model"

    fingerprint = getattr(model, "model_fingerprint", None) or (ctx.get("model_fingerprint") if ctx else None)
    reason = getattr(model, "fingerprint_unavailable_reason", None) or (ctx.get("fingerprint_unavailable_reason") if ctx else None)
    if not fingerprint and not reason:
        reason = "provider_did_not_report"

    return {
        "provider": str(provider),
        "model": str(model_name),
        "model_fingerprint": fingerprint,
        "fingerprint_unavailable_reason": reason,
    }


def _compute_turn_cost(
    ctx: Mapping[str, Any],
    proposal_payload: Mapping[str, Any],
    route: dict[str, Any],
) -> dict[str, Any]:
    prompt_tokens = ctx.get("prompt_tokens")
    completion_tokens = ctx.get("completion_tokens")
    if prompt_tokens is not None or completion_tokens is not None:
        tokens = int(prompt_tokens or 0) + int(completion_tokens or 0)
        tokens_status = "measured"
    else:
        ctx_tokens = len(str(ctx).split())
        prop_tokens = len(str(proposal_payload).split())
        tokens = max(ctx_tokens + prop_tokens, 1)
        tokens_status = "estimated"

    ctx_bytes = len(str(ctx).encode("utf-8"))
    prop_bytes = len(str(proposal_payload).encode("utf-8"))
    bytes_val = max(ctx_bytes + prop_bytes, 1)
    bytes_status = "measured"

    cost_micros = ctx.get("usd_micros") or ctx.get("cost_micros")
    if cost_micros is not None:
        usd_micros = int(cost_micros)
        usd_status = "measured"
    elif route["provider"] in ("scripted", "fake", "mock", "lam", "ollama"):
        usd_micros = 0
        usd_status = "measured"
    else:
        usd_micros = 0
        usd_status = "unavailable"

    duration_ms = ctx.get("duration_ms") or ctx.get("millis")
    if duration_ms is not None:
        millis_val = int(duration_ms)
        millis_status = "measured"
    else:
        millis_val = 1
        millis_status = "measured"

    measurement_status = {
        "usd_micros": {"status": usd_status, "reason": None if usd_status != "unavailable" else "unpriced_provider"},
        "tokens": {"status": tokens_status, "reason": None},
        "bytes": {"status": bytes_status, "reason": None},
        "millis": {"status": millis_status, "reason": None},
    }

    return {
        "usd_micros": usd_micros,
        "tokens": tokens,
        "bytes": bytes_val,
        "millis": millis_val,
        "measurement_status": measurement_status,
    }


def _zero_controller_cost() -> dict[str, Any]:
    """A policy-produced proposal made no provider invocation."""
    return {
        "usd_micros": 0,
        "tokens": 0,
        "bytes": 0,
        "millis": 0,
        "measurement_status": {
            dimension: {"status": "measured", "reason": "no_provider_invocation"}
            for dimension in ("usd_micros", "tokens", "bytes", "millis")
        },
    }


def assemble_trajectory(
    *,
    task: Any,
    harness_digest: str,
    terminal: str,
    receipts: Sequence[Any],
    contexts: Sequence[Mapping[str, Any]],
    events: Sequence[Any],
    verdict: Any,
    state_digest: str | None = None,
    model: Any = None,
    environment: Any = None,
    run_plan: Any = None,
    artifact_index: Sequence[Any] | None = None,
    provenance_claims: Sequence[Mapping[str, Any]] | None = None,
    context_provenance: Sequence[Mapping[str, Any]] | None = None,
    compaction_provenance: Sequence[Mapping[str, Any]] | None = None,
    cache_provenance: Sequence[Mapping[str, Any]] | None = None,
    reproducibility: ReproducibilityVector | Mapping[str, Any] | None = None,
    capture_status: Mapping[str, Any] | None = None,
    schema_version: str = "mhf.trajectory/2",
) -> dict[str, Any]:
    turns: list[dict[str, Any]] = []
    proposals = [
        e for e in events
        if (getattr(e, "kind", None) or (getattr(e, "payload", {}).get("kind") if hasattr(e, "payload") else None)) == "ProposalProduced"
    ]
    model_routes_used: list[dict[str, Any]] = []
    seen_routes: set[tuple[str, str]] = set()

    for index, proposal in enumerate(proposals):
        ctx = contexts[index] if index < len(contexts) else {}
        context_digest = digest_of(dict(ctx) if ctx else {"turn": index})
        proposal_payload = dict(proposal.payload) if hasattr(proposal, "payload") and isinstance(proposal.payload, Mapping) else dict(proposal)

        controller_produced = ctx.get("proposal_source") == "meta_controller"
        route = None if controller_produced else _resolve_model_route(model, ctx)
        if route is not None:
            route_key = (route["provider"], route["model"])
            if route_key not in seen_routes:
                seen_routes.add(route_key)
                model_routes_used.append({"tier": 1, **route})

        turn_cost = (
            _zero_controller_cost()
            if controller_produced else _compute_turn_cost(ctx, proposal_payload, route))

        turn_receipts = []
        if index < len(receipts):
            rec = receipts[index]
            outcome = rec.outcome if getattr(rec, "outcome", None) in (
                "completed", "failed", "rejected", "undeterminable",
            ) else ("completed" if getattr(rec, "outcome", None) == "ok" else "failed")
            turn_receipts.append({
                "request_digest": getattr(rec, "descriptor_digest", None) or getattr(rec, "request_digest", None) or digest_of({"turn": index}),
                "outcome": outcome,
                "grant_digest": getattr(rec, "grant_digest", None),
                "lease_id": getattr(rec, "lease_id", None),
                "stdout_ref": getattr(rec, "stdout_ref", None),
                "artifact_refs": [getattr(a, "digest", str(a)) for a in getattr(rec, "artifacts", ())] if hasattr(rec, "artifacts") else [],
            })

        turn_dict: dict[str, Any] = {
            "turn": index,
            "context_digest": context_digest,
            "context_ref": ctx.get("context_ref"),
            "proposal": proposal_payload,
            "receipts": turn_receipts,
            "invocations": ([] if controller_produced else [{
                "tier": 1,
                "route": route,
                "usage": {
                    "prompt_tokens": ctx.get("prompt_tokens"),
                    "completion_tokens": ctx.get("completion_tokens"),
                },
                "cost": turn_cost,
            }]),
            "cost": turn_cost,
        }
        if route is not None:
            turn_dict["model_route"] = route

        if schema_version == "mhf.trajectory/2":
            turn_dict["model_input_ref"] = ctx.get("model_input_ref") or ctx.get("prompt_digest")
            turn_dict["model_output_ref"] = ctx.get("model_output_ref") or ctx.get("output_digest")

        turns.append(turn_dict)

    if not model_routes_used and model is not None:
        default_route = _resolve_model_route(model)
        model_routes_used.append({"tier": 1, **default_route})
    elif not model_routes_used and turns:
        default_route = _resolve_model_route(None)
        model_routes_used.append({"tier": 1, **default_route})

    dimensions = ("usd_micros", "tokens", "bytes", "millis")
    total_cost: dict[str, Any] = {}
    total_measurement_status: dict[str, Any] = {}
    if not turns:
        for dim in dimensions:
            total_cost[dim] = 0
            total_measurement_status[dim] = {"status": "measured", "reason": None}
    else:
        for dim in dimensions:
            all_available = all(
                turn["cost"]["measurement_status"][dim]["status"] in ("measured", "estimated")
                for turn in turns
            )
            if all_available:
                total_cost[dim] = sum(turn["cost"][dim] for turn in turns)
                all_measured = all(
                    turn["cost"]["measurement_status"][dim]["status"] == "measured"
                    for turn in turns
                )
                total_measurement_status[dim] = {
                    "status": "measured" if all_measured else "estimated",
                    "reason": None,
                }
            else:
                total_cost[dim] = 0
                total_measurement_status[dim] = {
                    "status": "unavailable",
                    "reason": "turn_dimension_unavailable",
                }
    total_cost["measurement_status"] = total_measurement_status

    d_r_payload = {
        "harness_digest": harness_digest,
        "runtime": "vanguard-runtime/0.6.1",
        "environment": digest_of({
            "task": getattr(task, "brief", ""),
            "project": getattr(task, "project_id", ""),
        }),
        "models": [f"{r['provider']}:{r['model']}" for r in model_routes_used],
        "oracle": getattr(verdict, "oracle_id", "oracle-default") if verdict else "none",
    }
    execution_digest = getattr(run_plan, "run_digest", "") or digest_of(d_r_payload)

    seqs: list[int] = []
    for ev in events:
        s = getattr(ev, "seq", None)
        if s is None and hasattr(ev, "payload") and isinstance(ev.payload, Mapping):
            s = ev.payload.get("seq")
        if s is not None:
            try:
                seqs.append(int(s))
            except (ValueError, TypeError):
                pass

    if seqs:
        event_range = {
            "first_seq": min(seqs),
            "last_seq": max(seqs),
            "count": len(events),
        }
    else:
        event_range = {
            "first_seq": 0 if events else None,
            "last_seq": (len(events) - 1) if events else None,
            "count": len(events),
        }

    outcome_map = {
        "completed": "completed",
        "abandoned": "aborted",
        "budget_exhausted": "budget_exhausted",
        "runtime_error": "instrument_error",
        "cancelled": "aborted",
        "escalated": "aborted",
        "abstained": "completed",
    }
    terminal_name = getattr(terminal, "value", str(terminal)).lower()

    signed_verdict = signed_verdict_object(verdict)
    verdict_absence_reason = None if signed_verdict is not None else "no_evaluator_bound"

    if schema_version == "mhf.trajectory/1":
        return {
            "schema": "mhf.trajectory/1",
            "project_id": getattr(task, "project_id", "project-default"),
            "run_id": getattr(task, "run_id", "run-1"),
            "episode_id": getattr(task, "episode_id", "episode-1"),
            "parent_episode_id": getattr(task, "parent_episode_id", None),
            "principal_id": getattr(task, "principal", "agent-1"),
            "harness_digest": harness_digest,
            "execution_digest": execution_digest,
            "state_digest": state_digest,
            "event_range": event_range,
            "model_routes_used": model_routes_used,
            "turns": turns,
            "verdict": signed_verdict,
            "verdict_absence_reason": verdict_absence_reason,
            "cost": total_cost,
            "outcome": outcome_map.get(terminal_name, "aborted"),
        }

    # /2 payload assembly
    # Partition provenance claims if passed as unified list
    ctx_prov = list(context_provenance or [])
    cmp_prov = list(compaction_provenance or [])
    cch_prov = list(cache_provenance or [])
    extracted_repro = None

    if provenance_claims:
        for claim in provenance_claims:
            kind = claim.get("claimKind")
            if kind == "context_selection":
                ctx_prov.append(claim)
            elif kind == "compaction":
                cmp_prov.append(claim)
            elif kind == "cache_interaction":
                cch_prov.append(claim)
            elif kind == "reproducibility_at_run_close":
                extracted_repro = claim.get("vector") or claim

    # Prepare artifact index
    artifacts_list = []
    if artifact_index:
        for entry in artifact_index:
            if hasattr(entry, "to_dict"):
                artifacts_list.append(entry.to_dict())
            elif isinstance(entry, Mapping):
                artifacts_list.append(dict(entry))

    # Prepare reproducibility
    if reproducibility is not None:
        if isinstance(reproducibility, ReproducibilityVector):
            repro_dict = reproducibility.to_dict()
        elif isinstance(reproducibility, Mapping):
            repro_dict = dict(reproducibility)
        else:
            repro_dict = None
    elif extracted_repro is not None:
        repro_dict = dict(extracted_repro)
    else:
        profile_obj = getattr(run_plan, "profile", None) or getattr(task, "profile", None)
        computed_vector = assess_reproducibility(
            profile=profile_obj,
            model_route=model_routes_used[0] if model_routes_used else None,
            environment={"task": getattr(task, "brief", ""), "project_id": getattr(task, "project_id", "")},
            artifact_index=artifact_index,
            state_digest=state_digest,
            run_id=getattr(task, "run_id", "run-1"),
        )
        repro_dict = computed_vector.to_dict()

    # Prepare capture status
    if capture_status is not None:
        cap_dict = dict(capture_status)
    else:
        # `null`, not a synthesised `complete`. A run composed without a
        # capture subsystem captured nothing, and reporting "complete" for it
        # would make "we captured everything we were asked to" and "we were
        # never asked to capture anything" indistinguishable -- the same
        # fabrication the `/1` reader path is careful to avoid. The `/2`
        # schema types `capture` as nullable precisely so absence can be
        # stated rather than invented.
        cap_dict = None

    return {
        "schema": "mhf.trajectory/2",
        "project_id": getattr(task, "project_id", "project-default"),
        "run_id": getattr(task, "run_id", "run-1"),
        "episode_id": getattr(task, "episode_id", "episode-1"),
        "parent_episode_id": getattr(task, "parent_episode_id", None),
        "principal_id": getattr(task, "principal", "agent-1"),
        "harness_digest": harness_digest,
        "execution_digest": execution_digest,
        "run_digest": getattr(run_plan, "run_digest", None) or execution_digest,
        "activation_digest": getattr(run_plan, "activation_digest", None),
        "task_digest": getattr(run_plan, "task_digest", None),
        "preregistration_digest": getattr(run_plan, "preregistration_digest", None),
        "state_digest": state_digest,
        "event_range": event_range,
        "model_routes_used": model_routes_used,
        "turns": turns,
        "verdict": signed_verdict,
        "verdict_absence_reason": verdict_absence_reason,
        "cost": total_cost,
        "outcome": outcome_map.get(terminal_name, "aborted"),
        "artifacts": artifacts_list,
        "provenance": {
            "context": ctx_prov,
            "compaction": cmp_prov,
            "cache": cch_prov,
        },
        "reproducibility_at_run_close": repro_dict,
        "capture": cap_dict,
    }


class DelayedTerminalEmitter:
    """Hold `EpisodeCompleted` until the trajectory (and verdict) are known."""

    def __init__(self, inner: Any) -> None:
        self._inner = inner
        self.pending: Event | None = None

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def emit(self, event: Event) -> Any:
        if event.kind == "EpisodeCompleted":
            self.pending = event
            return None
        return self._inner.emit(event)

    def append_intent(self, event: Event) -> None:
        return self._inner.append_intent(event)

    def flush(self, trajectory: Mapping[str, Any]) -> None:
        if self.pending is None:
            return
        payload = {**dict(self.pending.payload), "trajectory": dict(trajectory)}
        flushed = Event(
            kind=self.pending.kind,
            reason=self.pending.reason,
            at=self.pending.at,
            run_id=self.pending.run_id,
            principal=self.pending.principal,
            payload=payload,
            alertable=self.pending.alertable,
        )
        self._inner.emit(flushed)
        self.pending = None
```

## Benchmark failure taxonomy

- `TASK_INVALID`: task subject or test contract cannot be established;
- `ORACLE_INVALID`: gold/baseline environment does not pass required checks;
- `INSTRUMENT_ERROR`: provider, parser, sandbox, store, or evaluator protocol;
- `NO_PATCH`: write-required task completed without workspace modification;
- `PATCH_REJECTED`: patch cannot apply to the exact task subject;
- `LOCAL_VERIFICATION_FAILED`: fresh local receipt is non-passing;
- `EVALUATOR_FAILED`: evaluator executed and returned a valid failing verdict;
- `EVALUATOR_INVALID`: missing, stale, unsigned, or mismatched verdict;
- `BUDGET_EXHAUSTED`: typed resource ceiling reached;
- `ABANDONED`: harness stopped without an admissible completion;
- `RESOLVED`: all truthful success predicates hold.

## Minimum experimental program before claims

1. deterministic unit tasks for tool and patch correctness;
2. three repository smoke tasks with known oracle validity;
3. paired `vg-code-default` versus `vg-code-forge` canary;
4. ablation of stop gate, reflex rules, distillation, ToolScript and forks;
5. repeated episodes using fixed preregistered seeds/policies;
6. heldout suite never used for prompt/rule tuning;
7. replay from stored trajectories and artifacts;
8. clean-machine packaging run outside source checkout;
9. cost/latency regression gate;
10. independent evaluator/evidence audit.

## Required focused tests

- prose-only answer is never resolved;
- patch-required task with no patch is `NO_PATCH`;
- dry-run result is synthetic and excluded from resolved rate;
- failing oracle marks task invalid;
- invalid evaluator response cannot become pass;
- verdict for another patch/workspace/task is rejected;
- attempt count matches preregistration exactly;
- patch artifact bytes reproduce the evaluated workspace;
- provider retry accounting is conserved;
- evaluator is outside the worker trust boundary;
- restart preserves attempt number and prevents duplicate settlement;
- report denominator excludes invalid tasks transparently;
- secrets never appear in prompts, logs, trajectories, or reports.

## Final focused validation ladder

```bash
python3 -m unittest test.runtime.test_lab_driver -v
python3 -m unittest test.runtime.test_dogfood_driver -v
python3 -m unittest test.runtime.test_evidence_capture -v
python3 -m unittest test.benchmarks.test_m8_heldout_runner -v
python3 tools/linters/check_boundaries.py
python3 tools/linters/check_domain_blindness.py
python3 tools/linters/check_isolation_policy.py
python3 tools/linters/scan_secrets.py
```

## Final definition of done

FORGE is code-complete only when the preset can install on a clean machine,
open a real repository, inspect relevant code, apply a controlled patch, run
targeted verification, reject premature completion, recover from a failed
attempt, optionally fork under conserved budget, select evidence-first, resume
after crash, emit a complete trajectory, invoke an external evaluator, and
report success only from a valid bound verdict.  Benchmark score remains an
empirical result, never a guarantee produced by the manifest itself.
