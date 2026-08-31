"""The runtime composition root (`REQ-DOG-001`, `ADR-0057`, `ADR-0058`).

Public facade after 2.2-C. Composition is `compose.py`, a run is `session.py`,
port bridges are `wiring.py`, envelopes are `ledger_emitter.py`. One
composition path, one runtime authority, one writer, one evaluator table.
"""

from __future__ import annotations

import json
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
from .workspace import (
    controlled_environment,
    get_workspace_path,
    get_workspace_root,
    validate_workspace_path,
)
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
from ..ports.event_store import Result
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
        completion_policy: Any = None,
    ) -> RunResult:
        """Compose, run one episode, resolve approvals, and evaluate exterior.

        `interactive=False` is `Mode.BENCHMARK` and is **not** "approve
        everything": `K-17` fails approval closed there, because a run that
        blocks for a human has unbounded wall-clock *and* a human contributing
        to the measured outcome.

        **EVO-02: retired from every production path.** No product code
        calls this anymore -- `ApplicationService`, the CLI, and the service
        daemon all go through `execute_profiled`/`RuntimeBootstrap`, the sole
        concrete-adapter construction authority (`ADR-0089 §Decision 2`).
        This method survives only because falsifier coverage (the M7
        topology suite) deliberately exercises its `sandbox_mode="host-dev"`
        escape hatch -- a host without a qualifying rootless perimeter, which
        `execute_profiled`'s `local`/`product` profiles also reach via
        `RuntimeBootstrap`, but changing which entrypoint an already-signed
        evidence bundle's pinned material digest points at is a change to
        that evidence, not a refactor, so it is left alone here. New product
        code must call `execute_profiled`, never this.
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
            sealed_dir = Path(tempfile.mkdtemp(prefix="vg-sealed-worker-", dir=get_workspace_path("sandboxes")))
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
                harness, ports, task_context, on_terminal=on_terminal, release=release,
                completion_policy=completion_policy,
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
        completion_policy: Any = None,
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
                completion_policy=completion_policy,
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
        completion_policy: Any = None,
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
            settled: frozenset[str] = frozenset()
            while len(settled) < len(operations):
                scheduled = SequentialScheduler().decide(operations, settled)
                if not scheduled:
                    raise RunPlanError(
                        "topology contains operations that are not sequentially schedulable"
                    )
                settled = settled | frozenset(item.operation_id for item in scheduled)
            extensions = (lowered,)
            if len(operations) > 1:
                # Topology is an execution plan, not a second model/runtime.
                # The root episode emits one ordinary spawn proposal per
                # lowered role; Session routes it through Kernel.dispatch and
                # the existing RuntimeChildRunner. Child calls delegate to
                # the supplied model, so role work remains normal agent work.
                ports = replace(ports, model=_TopologyModel(
                    ports.model, task_context, lowered, harness, ports.blobs))
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
        if completion_policy is not None:
            ports = replace(ports, completion_policy=completion_policy)
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


class _TopologyModel:
    """Turn a lowered topology into ordinary, sequential spawn proposals.

    Topology lowering is deliberately data-only.  This small model decorator
    is the execution bridge: it emits the next role as a normal
    ``agent.spawn`` proposal, so the session, kernel, grant, lease, child
    runtime and ledger remain exactly the same as for a model-originated
    delegation.  Child episodes delegate to the wrapped model unchanged.
    """

    def __init__(self, model: Any, task: TaskContext,
                 lowered: Mapping[str, Any], harness: Harness,
                 blobs: Any = None) -> None:
        self._model = model
        self._root_episode = task.episode_id
        self._brief = task.brief
        self._harness = harness
        self._blobs = blobs
        self._operations = tuple(lowered.get("roleOperations", ()))
        self._roles = {
            str(item["role"]): item
            for item in lowered.get("lineageTemplates", ())
        }
        self._topology_digest = str(lowered.get("topologyDigest", ""))
        self._cursor = 0
        self._flow_digests: dict[str, str] = {}
        self._last_role: str | None = None

    def __getattr__(self, name: str) -> Any:
        # Preserve provider identity and optional adapter metadata used by
        # release admission and trajectory assembly.
        return getattr(self._model, name)

    def to_dict(self) -> Mapping[str, Any]:
        delegate = getattr(self._model, "to_dict", None)
        return delegate() if callable(delegate) else {}

    @property
    def child_model(self) -> Any:
        """The provider children use after the root emits a role request."""
        return self._model

    def propose(self, context: Mapping[str, Any], tools: Any,
                sampling: Mapping[str, Any]) -> Any:
        if self._cursor >= len(self._operations):
            return Result.success({
                "kind": "finish",
                "note": "all lowered topology roles completed",
            })

        operation = self._operations[self._cursor]
        role_id = str(operation["role"])
        template = self._roles[role_id]
        budget = {
            dimension: int(amount)
            for dimension, amount in dict(template.get("budget", {})).items()
            if dimension in {"usd_micros", "millis", "tokens", "bytes"}
        }
        max_turns = int(template.get("budget", {}).get(
            "maxTurns", template.get("budget", {}).get("turns", 1)))
        max_turns = max(max_turns, 1)
        # The generic selector is declared by the manifest for agent.spawn;
        # it is selected from that declaration, never fabricated as authority.
        resource: Mapping[str, Any] | None = None
        for selector in self._harness.capability_ceiling:
            try:
                candidate = json.loads(selector)
            except (TypeError, ValueError):
                continue
            if (candidate.get("kind") == "generic"
                    and str(candidate.get("uriPattern", "")).startswith("agent://spawn/")):
                resource = candidate
                break
        if resource is None:
            return Result.fail(
                "instrument_error",
                "topology requires a declared agent.spawn resource selector",
            )

        # Topology scope is routing data, never a source of authority.  The
        # child may request only selectors already declared by the parent
        # composition; the SpawnAdapter applies the real attenuation check.
        # The spawn selector itself is deliberately omitted from the role's
        # working scope, so a role cannot recursively manufacture topology
        # children.
        role_resources: list[Mapping[str, Any]] = []
        for raw_selector in self._harness.capability_ceiling:
            try:
                selector = json.loads(raw_selector)
            except (TypeError, ValueError):
                continue
            if (isinstance(selector, Mapping)
                    and selector != resource
                    and selector not in role_resources):
                role_resources.append(dict(selector))

        role_context = json.dumps({
            "role": role_id,
            "policyRef": template.get("policyRef", ""),
            "context": template.get("context", {}),
            "causalPredecessors": operation.get("causalPredecessors", ()),
            "artifactRefs": [
                {"artifact": artifact, "digest": self._flow_digests[artifact]}
                for artifact in operation.get("inputArtifacts", ())
                if artifact in self._flow_digests
            ],
        }, sort_keys=True, separators=(",", ":"))
        artifact_refs = tuple(
            {"artifact": artifact, "digest": self._flow_digests[artifact]}
            for artifact in operation.get("inputArtifacts", ())
            if artifact in self._flow_digests)
        missing_artifacts = tuple(
            str(artifact) for artifact in operation.get("inputArtifacts", ())
            if str(artifact) not in self._flow_digests)
        if missing_artifacts:
            return Result.fail(
                "instrument_error",
                "required topology artifacts are unavailable: "
                + ", ".join(missing_artifacts),
            )
        self._cursor += 1
        args: dict[str, Any] = {
            "brief": f"{self._brief}\n\nExecute topology role {role_id}. "
                     f"Routing context: {role_context}",
            "authority": [verb for verb in self._harness.verbs
                          if verb != SPAWN_VERB],
            "resources": role_resources,
            "budget": budget,
            "maxTurns": max_turns,
        }
        if artifact_refs:
            args["artifactRefs"] = list(artifact_refs)
        self._last_role = role_id
        return Result.success({
            "kind": "effect",
            "action": SPAWN_VERB,
            "resource": dict(resource),
            "args": args,
            "reservation": dict(budget),
            "idempotencyKey": f"topology:{self._topology_digest}:{role_id}",
            "note": f"execute lowered topology role {role_id}",
        })

    def observe_dispatch(self, result: Any) -> None:
        """Bind a settled child result to the next declared artifact flow.

        Only the persisted child result digest crosses the role boundary. The
        transcript, handles and child ports remain private to the child.
        """
        if self._last_role is None:
            return
        hint = getattr(getattr(result, "outcome", None), "result_digest", None)
        digest = (hint if isinstance(hint, str) and hint.startswith("sha256:")
                  and self._blobs is not None and self._blobs.has(hint)
                  else None)
        if not isinstance(digest, str) or not digest.startswith("sha256:"):
            return
        operation = self._operations[self._cursor - 1]
        for artifact in operation.get("outputArtifacts", ()):
            self._flow_digests[str(artifact)] = digest


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
    "controlled_environment",
    "get_workspace_path",
    "get_workspace_root",
    "validate_workspace_path",
]
