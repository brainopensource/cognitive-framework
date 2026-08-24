"""The runtime composition root (`REQ-DOG-001`, `ADR-0057`, `ADR-0058`).

Public facade after 2.2-C. Composition is `compose.py`, a run is `session.py`,
port bridges are `wiring.py`, envelopes are `ledger_emitter.py`. One
composition path, one runtime authority, one writer, one evaluator table.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Callable, Mapping

from ..adapters.environment.sandboxed import SandboxedEnvironmentAdapter
from ..adapters.sandbox.rootless import RootlessSandboxRunner
from ..adapters.sandbox.worker import WorkerProtocol
from ..adapters.stores.event_store import SqliteEventStore
from .compose import (
    Harness,
    Receipt,
    RunResult,
    Runtime as _ComposedRuntime,
    TaskContext,
)
from .activation import (
    ActivationError,
    ActivationPlan,
    ActivationStep,
    activate,
    plan_activation,
)
from .determinism import SystemClock
from .run_plan import RunPlan, RunPlanError, plan_run
from .ledger_emitter import LedgerBridge, LedgerEmitter
from .session import HarnessSession, SessionPorts, _admit_turn_result
from .wiring import (
    BindingContext,
    BindingResolver,
    CompositionError,
    DEFAULT_BINDINGS,
    EVALUATOR_BINDINGS,
    EffectBinding,
    _bwrap_path,
    _environment_effector,
    _operator_span,
    _reservation_for,
    _sandbox_effector,
    _span_for,
)


class Runtime(_ComposedRuntime):
    """Public runtime: compose, then run one episode (`execute_harness`)."""

    @classmethod
    def execute_harness(
        cls,
        manifest_path: str | Path,
        task_context: TaskContext,
        interactive: bool = True,
        *,
        model: Any = None,
        approver: Callable[[Any], Any] | None = None,
        verifier: Any = None,
        store: Any = None,
        clock: Any = None,
        bindings: Mapping[str, EffectBinding] | None = None,
        approval_key: bytes | None = None,
        on_terminal: Callable[[HarnessSession], Any] | None = None,
    ) -> RunResult:
        """Compose, run one episode, resolve approvals, and evaluate exterior.

        `interactive=False` is `Mode.BENCHMARK` and is **not** "approve
        everything": `K-17` fails approval closed there, because a run that
        blocks for a human has unbounded wall-clock *and* a human contributing
        to the measured outcome.
        """
        harness = cls.compose(manifest_path, episode_id=task_context.episode_id,
                              bindings=bindings)
        repo = Path(task_context.repo_path).resolve()

        # Runtime phase. Composition has already succeeded; a host without
        # bubblewrap is a failure of *this* run, not of the harness, so the
        # probe lives here and not behind `compose`.
        bwrap = _bwrap_path()
        sealed_dir = Path(tempfile.mkdtemp(prefix="vg-sealed-worker-"))
        sealed_bundle = sealed_dir / "bundle"
        sealed_bundle.write_bytes(
            b"sealed evaluator mount is intentionally unavailable to worker\n")
        worker = WorkerProtocol(
            RootlessSandboxRunner(repo, evaluator_bundle=sealed_bundle, runtime=bwrap))
        environment = SandboxedEnvironmentAdapter(
            worker, repo, environment_id=f"workspace:{repo}")

        if model is None:
            from ..adapters.models.openrouter import OpenRouterModel

            model = OpenRouterModel()

        ports = SessionPorts(
            model=model,
            environment=environment,
            clock=clock or SystemClock(),
            store=store or SqliteEventStore(":memory:"),
            verifier=verifier,
            approver=approver,
            approval_key=approval_key,
            interactive=interactive,
        )
        return HarnessSession(harness, ports, task_context, on_terminal=on_terminal).run()


__all__ = [
    "DEFAULT_BINDINGS",
    "ActivationError",
    "ActivationPlan",
    "ActivationStep",
    "BindingResolver",
    "RunPlan",
    "RunPlanError",
    "activate",
    "plan_activation",
    "plan_run",
    "EVALUATOR_BINDINGS",
    "BindingContext",
    "CompositionError",
    "EffectBinding",
    "Harness",
    "HarnessSession",
    "LedgerBridge",
    "LedgerEmitter",
    "Receipt",
    "RunResult",
    "Runtime",
    "SessionPorts",
    "TaskContext",
    "_admit_turn_result",
    "_bwrap_path",
    "_environment_effector",
    "_operator_span",
    "_reservation_for",
    "_sandbox_effector",
    "_span_for",
]
