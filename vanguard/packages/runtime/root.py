"""The runtime composition root (`REQ-DOG-001`, `ADR-0057`, `ADR-0058`).

Public facade after 2.2-C. Composition is `compose.py`, a run is `session.py`,
port bridges are `wiring.py`, envelopes are `ledger_emitter.py`. One
composition path, one runtime authority, one writer, one evaluator table.
"""

from __future__ import annotations

import tempfile
import shutil
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable, Mapping

from ..adapters.environment.sandboxed import SandboxedEnvironmentAdapter
from ..adapters.environment.git import GitEnvironmentAdapter
from ..adapters.sandbox.rootless import RootlessSandboxRunner
from ..adapters.sandbox.worker import WorkerProtocol
from ..adapters.stores.event_store import SqliteEventStore
from ..domain.canonicalisation.digest import digest_of
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
    ComponentHandle,
    plan_activation,
)
from .assurance import AssurancePolicy
from .determinism import SystemClock
from .run_plan import RunPlan, RunPlanError, plan_run
from .topology import lower_topology, parse_topology
from .scheduler import ReadyOperation, SequentialScheduler
from .ledger_emitter import LedgerBridge, LedgerEmitter
from .artifacts import ArtifactWriter, CapturePolicy, resolve_capture_policy
from .session import HarnessSession, SessionPorts, _admit_turn_result
from ..ports.memory import MemoryBinding
from .child_runtime import RuntimeChildRunner
from .delegation import SPAWN_VERB
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
        release: bool = False,
        sandbox_mode: str = "rootless",
        blobs: Any = None,
        capture_policy: Any = None,
        meta_controller: Any = None,
        controller_confidence: tuple[Any, ...] = (),
        memory: MemoryBinding | None = None,
        experience: MemoryBinding | None = None,
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
        selected_store = store or SqliteEventStore(":memory:")
        if sandbox_mode not in {"rootless", "host-dev"}:
            raise ValueError("sandbox_mode must be 'rootless' or 'host-dev'")
        if release and sandbox_mode != "rootless":
            raise ValueError("release execution requires rootless containment")
        if release and (
            not isinstance(selected_store, SqliteEventStore)
            or not selected_store.durable
        ):
            raise ValueError(
                "release execution requires an explicit file-backed SQLite-WAL store"
            )

        sealed_dir: Path | None = None
        if sandbox_mode == "host-dev":
            # Explicit development escape hatch for local CLI work.  This
            # adapter preserves the EnvironmentPort, path checks, argv
            # allowlist, receipts, and compensation, but it is intentionally
            # not a containment attestation and is barred from release.
            environment = GitEnvironmentAdapter(
                repo, environment_id=f"workspace-host-dev:{repo}")
        else:
            # Runtime phase. Composition has already succeeded; a host
            # without bubblewrap is a failure of this rootless run, not of
            # the harness, so the probe lives here and not behind `compose`.
            bwrap = _bwrap_path()
            sealed_dir = Path(tempfile.mkdtemp(prefix="vg-sealed-worker-"))
            sealed_bundle = sealed_dir / "bundle"
            sealed_bundle.write_bytes(
                b"sealed evaluator mount is intentionally unavailable to worker\n")
            worker = WorkerProtocol(
                RootlessSandboxRunner(repo, evaluator_bundle=sealed_bundle, runtime=bwrap))
            environment = SandboxedEnvironmentAdapter(
                worker, repo, environment_id=f"workspace:{repo}")

            if release:
                qualified = environment.qualify()
                if not qualified.ok:
                    raise RuntimeError(
                        f"release containment qualification failed: {qualified.error.kind}: "
                        f"{qualified.error.message}")

        if model is None:
            from ..adapters.models.openrouter import OpenRouterModel

            model = OpenRouterModel()

        ports = SessionPorts(
            model=model,
            environment=environment,
            clock=clock or SystemClock(),
            store=selected_store,
            verifier=verifier,
            approver=approver,
            approval_key=approval_key,
            interactive=interactive,
            blobs=blobs,
            capture_policy=capture_policy,
            meta_controller=meta_controller,
            controller_confidence=tuple(controller_confidence),
            memory=memory,
            experience=experience,
        )
        try:
            return cls.run_composed(
                harness, ports, task_context, on_terminal=on_terminal, release=release
            )
        finally:
            if sealed_dir is not None:
                shutil.rmtree(sealed_dir, ignore_errors=True)

    @classmethod
    def execute_profiled(
        cls,
        manifest_path: str | Path,
        task_context: TaskContext,
        profile_id: str,
        interactive: bool = True,
        *,
        model: Any = None,
        approver: Callable[[Any], Any] | None = None,
        verifier: Any = None,
        store: Any = None,
        store_path: str | Path | None = None,
        bindings: Mapping[str, EffectBinding] | None = None,
        approval_key: bytes | None = None,
        on_terminal: Callable[[HarnessSession], Any] | None = None,
        host_qualifies: bool = True,
        host_facts: Mapping[str, Any] | None = None,
        blobs: Any = None,
        capture_policy: Any = None,
        meta_controller: Any = None,
        controller_confidence: tuple[Any, ...] = (),
        memory: MemoryBinding | None = None,
        experience: MemoryBinding | None = None,
    ) -> RunResult:
        """Compose and run one episode through the `RuntimeBootstrap` seam.

        This is the ADR-0089 target entrypoint: `Runtime` selects no adapter
        here — `RuntimeBootstrap.build()` does, from `profile_id` alone. A
        `sandboxed`/`hermetic` profile that the host cannot qualify raises
        `SandboxUnavailable`; it never silently executes on `host`
        (`RF-88`). `execute_harness` remains the legacy entrypoint until
        every caller has migrated and W3D-12 sunsets it.
        """
        from .bootstrap import RuntimeBootstrap

        harness = cls.compose(manifest_path, episode_id=task_context.episode_id,
                              bindings=bindings)
        deps = RuntimeBootstrap.build(
            profile_id=profile_id,
            repo_path=Path(task_context.repo_path),
            model=model,
            store=store,
            store_path=Path(store_path) if store_path is not None else None,
            host_qualifies=host_qualifies,
            host_facts=host_facts,
        )
        release = deps.profile.requested.assurance_level == "hermetic"
        ports = SessionPorts(
            model=deps.model,
            environment=deps.environment,
            clock=deps.clock,
            store=deps.store,
            verifier=verifier,
            approver=approver,
            approval_key=approval_key,
            interactive=interactive,
            blobs=blobs,
            capture_policy=capture_policy,
            meta_controller=meta_controller,
            controller_confidence=tuple(controller_confidence),
            memory=memory,
            experience=experience,
        )
        try:
            return cls.run_composed(
                harness, ports, task_context, on_terminal=on_terminal,
                release=release, profile=deps.profile,
            )
        finally:
            deps.cleanup()

    @classmethod
    def run_composed(
        cls,
        harness: Harness,
        ports: SessionPorts,
        task_context: TaskContext,
        *,
        on_terminal: Callable[[HarnessSession], Any] | None = None,
        release: bool = False,
        profile: Any | None = None,
    ) -> RunResult:
        """Run an already composed harness through the sole activation boundary.

        `profile`, when given, is an `EffectiveExecutionProfile`
        (`runtime/profiles.py`, typically produced by `RuntimeBootstrap`).
        It folds into `RunPlan`/`D_R` alongside `environment`/`store`/
        `model_route`; an optional meta-controller is bound there as a separate
        policy identity (`ADR-0089 §Decision 1`, `RF-87`). Omitting it leaves
        `RunPlan.profile_id` empty — legible for pre-W3D callers during
        migration, but never release/promotion eligible.
        """
        selected_store = ports.store
        if release and (
            not isinstance(selected_store, SqliteEventStore)
            or not selected_store.durable
        ):
            raise ValueError(
                "release execution requires an explicit file-backed SQLite-WAL store"
            )
        preregistration = dict(task_context.preregistration or {})
        preregistration_digest = str(
            preregistration.get("preregistration_digest")
            or preregistration.get("digest") or "")
        if release:
            preregistration_digest = _validate_release_inputs(
                ports, task_context, preregistration,
                expected_oracle=(harness.evaluators[0] if harness.evaluators else None))
        activation = plan_activation(harness.frozen)
        extensions: tuple[Mapping[str, Any], ...] = ()
        if task_context.topology is not None:
            topology = parse_topology(task_context.topology)
            lowered = lower_topology(topology, harness)
            operations = tuple(
                ReadyOperation(
                    operation_id=str(item["operationId"]),
                    causal_predecessors=tuple(str(x) for x in item.get("causalPredecessors", ())),
                ) for item in lowered["roleOperations"]
            )
            scheduled = SequentialScheduler().decide(operations)
            if len(scheduled) != len(operations):
                raise RunPlanError("topology contains operations that are not sequentially schedulable")
            extensions = (lowered,)
        run_plan = plan_run(
            activation,
            project_id=task_context.project_id,
            run_id=task_context.run_id,
            episode_id=task_context.episode_id,
            task=task_context.brief,
            task_digest=str(preregistration.get("task_digest") or "") or None,
            preregistration_digest=preregistration_digest,
            environment=_environment_identity(ports.environment),
            store={
                "kind": type(selected_store).__name__,
                "path": getattr(selected_store, "db_path", ""),
                "durable": bool(getattr(selected_store, "durable", False)),
                "journal_mode": getattr(selected_store, "journal_mode", "memory"),
            },
            model_route=_model_route_identity(ports.model),
            meta_controller=_meta_controller_identity(ports.meta_controller),
            oracle=harness.evaluators[0] if harness.evaluators else None,
            root_principal=task_context.principal,
            budget=harness.budget,
            profile=profile,
            extensions=extensions,
        )
        # `ADR-0096 §14.5`. The profile is the only thing that knows the
        # run's retention and capture-required posture, and `RunPlan` carries
        # only its scalars, so the policy is resolved here -- once, at the one
        # composition seam -- rather than rediscovered inside the session.
        if ports.blobs is not None and ports.capture_policy is None:
            ports = replace(ports, capture_policy=resolve_capture_policy(profile))
        # `M-6`. A composition that can spawn needs something that can run a
        # child, and the only admissible runner re-enters this same method.
        # Bound here rather than in `HarnessSession` so recursion stays an
        # edge of the public boundary and never a second activation authority.
        if ports.child_runtime is None and SPAWN_VERB in harness.verbs:
            ports = replace(ports, child_runtime=RuntimeChildRunner(
                run_composed=cls.run_composed,
                harness=harness, parent_ports=ports, parent_task=task_context,
                profile=profile, release=release,
            ))
        session = HarnessSession(
            harness, ports, task_context, on_terminal=on_terminal, run_plan=run_plan
        )
        session.begin_episode()
        with activate(
            activation,
            emitter=session.ledger.registry(),
            run_id=task_context.run_id,
            principal=task_context.principal,
            build=lambda step: _build_component_handle(
                step, harness=harness, ports=ports, run_id=task_context.run_id),
        ):
            result = session.run()
        # Teardown is part of the public run lineage.  ``session.run()`` takes
        # its immutable event snapshot before the activation context exits, so
        # refresh events and evidence after reverse-order retirement has been
        # durably emitted.
        result = replace(result, events=tuple(session.ledger.events))
        from .foundation_evidence import derive_foundation_bundle
        policy = AssurancePolicy.from_profile(profile)
        bundle = derive_foundation_bundle(
            run_plan=run_plan, result=result, store=selected_store,
        ) if policy.collects_foundation_evidence else None
        return replace(result, foundation_evidence=bundle)


def _validate_release_inputs(
    ports: SessionPorts,
    task_context: TaskContext,
    preregistration: Mapping[str, Any],
    expected_oracle: str | None = None,
) -> str:
    """Fail closed before the first event of an RF-85 candidate run."""
    digest = preregistration.get("preregistration_digest")
    task_digest = preregistration.get("task_digest")
    if not isinstance(digest, str) or not digest or not isinstance(task_digest, str) or not task_digest:
        raise ValueError("release execution requires immutable task/oracle preregistration")
    expected = digest_of({"task": task_context.brief})
    if task_digest != expected:
        raise ValueError("preregistered task digest does not bind the requested task")
    required = (
        "api", "task_digest", "oracle_id", "oracle_digest",
        "evaluator_key_id", "evaluator_public_key", "protocol",
        "subject_digest", "created_at", "metadata",
    )
    if any(key not in preregistration for key in required):
        raise ValueError("release preregistration is missing immutable trust bindings")
    identity = {key: preregistration[key] for key in required}
    if identity["api"] != "mhf.preregistration/1" or digest_of(identity) != digest:
        raise ValueError("release preregistration digest does not match its trust bindings")
    oracle = preregistration.get("oracle_id")
    if not isinstance(oracle, str) or not oracle:
        raise ValueError("release preregistration requires an exterior oracle identity")
    if expected_oracle is None or oracle != expected_oracle:
        raise ValueError("preregistered oracle does not match the composed evaluator")

    model = ports.model
    provider_value = getattr(model, "provider", None)
    mode_value = getattr(model, "mode", getattr(model, "_mode", None))
    if not isinstance(provider_value, str) or not provider_value or not isinstance(mode_value, str):
        raise ValueError("release provider must declare provider identity and execution mode")
    provider = provider_value.lower()
    mode = mode_value.lower()
    if any(label in provider for label in ("fake", "scripted", "cassette", "mock", "lam")) or mode != "live":
        raise ValueError("release execution requires a live non-fake/non-cassette provider")

    report = getattr(ports.environment, "containment_report", None)
    if report is None or not getattr(report, "verified", False) or not getattr(report, "contained", False):
        raise ValueError("release execution requires probe-verified rootless Bubblewrap containment")
    if "bubblewrap-rootless" != getattr(report, "runtime", ""):
        raise ValueError("release execution forbids host sandbox fallback")
    return digest


def _environment_identity(environment: Any) -> Mapping[str, Any]:
    report = getattr(environment, "containment_report", None)
    if report is None:
        return {"kind": type(environment).__name__, "containment": "unverified"}
    return {
        "kind": type(environment).__name__,
        "runtime": getattr(report, "runtime", ""),
        "runtime_version": getattr(report, "runtime_version", ""),
        "namespace": getattr(report, "namespace", ""),
        "syscall_profile": getattr(report, "syscall_profile", ""),
        "network_enforcement": getattr(report, "network_enforcement", ""),
        "writable_mounts": list(getattr(report, "writable_mounts", ())),
        "exposed_sockets": list(getattr(report, "exposed_sockets", ())),
        "resource_limits": dict(getattr(report, "resource_limits", {})),
        "startup_probes": [
            {"kind": probe.kind, "attempted": probe.attempted,
             "observed": probe.observed, "verified": probe.verified}
            for probe in getattr(report, "startup_probes", ())
        ],
        "attested_at": getattr(report, "attested_at", ""),
        "visibility_mark": getattr(report, "visibility_mark", ""),
        "verified": bool(getattr(report, "verified", False)),
        "contained": bool(getattr(report, "contained", False)),
    }


def _model_route_identity(model: Any) -> Mapping[str, Any]:
    declared = model.to_dict() if callable(getattr(model, "to_dict", None)) else {}
    return {
        **dict(declared),
        "adapter": type(model).__name__,
        "provider": str(getattr(model, "provider", "")),
        "model": str(getattr(model, "model", getattr(model, "model_name", ""))),
        "mode": str(getattr(model, "mode", getattr(model, "_mode", ""))),
    }


def _meta_controller_identity(controller: Any) -> Mapping[str, Any]:
    if controller is None:
        return {}
    controller_id = str(getattr(controller, "controller_id", ""))
    if not controller_id:
        raise ValueError("a bound meta-controller must declare controller_id")
    cls = type(controller)
    return {
        "controllerId": controller_id,
        "implementation": f"{cls.__module__}.{cls.__qualname__}",
        "version": str(getattr(controller, "version", "")),
    }


def _build_component_handle(
    step: ActivationStep,
    *,
    harness: Harness,
    ports: SessionPorts,
    run_id: str,
) -> ComponentHandle:
    """Materialize declared services from the already-wired runtime surface."""
    services: dict[str, Any] = {
        "system_prompt": harness.system_core,
        "tools": harness.tool_schemas,
        "context_policy": harness.system_core,
        "routing_policy": harness.bindings,
        "approval_policy": ports.approver,
        "skills": harness.skill_cards,
        "retrieval_policy": harness.index_component,
        "model": ports.model,
        "environment": ports.environment,
        "evaluator": ports.verifier,
        "store": ports.store,
        "meta_controller": ports.meta_controller,
    }
    service = services.get(step.interface)
    if service is None:
        service = {"component": step.name, "interface": step.interface}
    return ComponentHandle(step=step, run_id=run_id, service=service)


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
    "ArtifactWriter",
    "BindingContext",
    "CapturePolicy",
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
    "resolve_capture_policy",
    "TaskContext",
    "_admit_turn_result",
    "_bwrap_path",
    "_environment_effector",
    "_operator_span",
    "_reservation_for",
    "_sandbox_effector",
    "_span_for",
]
