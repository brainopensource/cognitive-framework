"""Activation planning and the runtime lifecycle walk (`ADR-0088 §1.3`).

`ActivationPlan` is an immutable *runtime projection* of one
`FrozenComposition`: it says which components exist, through which interface
each is consumed, what its effective ceiling is, what must be ready before it,
and — by construction — the order in which everything is torn down.

Two things it deliberately is not:

* **an authority.** Activation validates and orders what composition already
  froze. It cannot widen a ceiling, mint a grant, or admit a component the
  composition did not declare.
* **a scheduler.** The named component graph is static addressing. Edges order
  *initialization*, never runtime control flow; the turn loop stays unary and
  sequential (`I-11`). A graph edge that became a dispatch decision would be a
  workflow DAG under another name.

Its digest binds `D_H`, so an activation can never be attributed to a
composition it was not planned from.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, Mapping, Sequence

from ..domain.artifacts.manifest import FrozenComposition
from ..domain.canonicalisation.digest import digest_of
from .registry.lifecycle import PluginLifecycle


class ActivationError(RuntimeError):
    """An activation that must not proceed. Raised before any component runs."""


@dataclass(frozen=True, slots=True)
class ActivationStep:
    """One component's place in the activation order."""

    name: str
    #: The SPI the component is consumed through.
    interface: str
    isolation: str
    #: The component's effective ceiling, already attenuated at composition.
    ceiling: tuple[str, ...]
    #: Components that must be ready before this one. Eager edges only: a lazy
    #: binding is resolved on first use and therefore orders nothing.
    requires: tuple[str, ...]
    entrypoint: bool = False

    def identity(self) -> Mapping[str, Any]:
        return {
            "name": self.name,
            "interface": self.interface,
            "isolation": self.isolation,
            "ceiling": list(self.ceiling),
            "requires": list(self.requires),
            "entrypoint": self.entrypoint,
        }


@dataclass(frozen=True, slots=True)
class ActivationPlan:
    """The frozen order in which one composition is brought up and torn down."""

    composition_digest: str
    steps: tuple[ActivationStep, ...]
    activation_digest: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "activation_digest", digest_of({
            "compositionDigest": self.composition_digest,
            "steps": [step.identity() for step in self.steps],
        }))

    @property
    def order(self) -> tuple[str, ...]:
        """Initialization order: dependencies first."""
        return tuple(step.name for step in self.steps)

    @property
    def cleanup_order(self) -> tuple[str, ...]:
        """Teardown order.

        Exactly the reverse of initialization, always. A component is retired
        before anything it depended on, so nothing is ever quiesced while a
        live consumer still holds it.
        """
        return tuple(reversed(self.order))

    def step(self, name: str) -> ActivationStep:
        for item in self.steps:
            if item.name == name:
                return item
        raise ActivationError(f"activation plan has no component named {name!r}")


def plan_activation(frozen: FrozenComposition) -> ActivationPlan:
    """Project one frozen composition onto its activation order.

    Ordering is a deterministic topological sort over eager binding edges, with
    ties broken by name: the same composition must always plan to the same
    `activation_digest`, or the plan could not be evidence of anything.
    """
    components = {item.name: item for item in frozen.components}
    entrypoints = set(frozen.entrypoints)

    # `from` depends on `to`: a consumer needs its provider ready first.
    requires: dict[str, set[str]] = {name: set() for name in components}
    for binding in frozen.bindings:
        if binding.lazy:
            continue
        if binding.source not in components or binding.target not in components:
            raise ActivationError(
                f"binding {binding.source!r} -> {binding.target!r} names an "
                "undeclared component")
        requires[binding.source].add(binding.target)

    ordered: list[str] = []
    placed: set[str] = set()
    visiting: set[str] = set()

    def visit(name: str) -> None:
        if name in placed:
            return
        if name in visiting:
            raise ActivationError(f"eager activation cycle reaches {name!r}")
        visiting.add(name)
        for dependency in sorted(requires[name]):
            visit(dependency)
        visiting.discard(name)
        placed.add(name)
        ordered.append(name)

    for name in sorted(components):
        visit(name)

    steps = tuple(
        ActivationStep(
            name=name,
            interface=components[name].kind,
            isolation=components[name].isolation,
            ceiling=tuple(components[name].ceiling),
            requires=tuple(sorted(requires[name])),
            entrypoint=name in entrypoints,
        )
        for name in ordered
    )
    if not steps:
        raise ActivationError("a composition must declare at least one component")
    return ActivationPlan(frozen.composition_digest, steps)


@dataclass(frozen=True, slots=True)
class ActivatedComponent:
    """One live component and the lifecycle that owns its state."""

    step: ActivationStep
    lifecycle: PluginLifecycle
    cell: Any = None


@dataclass(slots=True)
class ComponentHandle:
    """Runtime-owned handle for a materialized component service."""

    step: ActivationStep
    run_id: str
    service: Any
    closed: bool = False

    def close(self) -> None:
        if self.closed:
            return
        closer = getattr(self.service, "close", None)
        if callable(closer):
            closer()
        self.closed = True


class ActivationSession:
    """The live components of one activation, addressed by name."""

    def __init__(self, plan: ActivationPlan, run_id: str) -> None:
        self.plan = plan
        self.run_id = run_id
        self._live: dict[str, ActivatedComponent] = {}

    def __contains__(self, name: object) -> bool:
        return name in self._live

    def __len__(self) -> int:
        return len(self._live)

    def __getitem__(self, name: str) -> ActivatedComponent:
        try:
            return self._live[name]
        except KeyError:
            raise ActivationError(f"component is not activated: {name!r}") from None

    @property
    def activated(self) -> tuple[str, ...]:
        """Live component names in activation order."""
        return tuple(name for name in self.plan.order if name in self._live)

    def _add(self, component: ActivatedComponent) -> None:
        self._live[component.step.name] = component

    def _drop(self, name: str) -> ActivatedComponent | None:
        return self._live.pop(name, None)


def _retire(component: ActivatedComponent, *, faulted: bool, reason: str) -> Exception | None:
    """Take one component to `RETIRED`, whatever state it is in.

    Cleanup is not allowed to fail: a teardown error must not mask the fault
    that caused the teardown, and it must not stop the components behind it
    from being retired. The lifecycle FSM is the only judge of which
    transitions are legal from here.
    """
    lifecycle = component.lifecycle
    try:
        closer = getattr(component.cell, "close", None)
        if callable(closer):
            closer()
        if faulted:
            lifecycle.fault(reason)
        else:
            lifecycle.quiesce()
        lifecycle.retire()
        return None
    except Exception as exc:  # noqa: BLE001 - all remaining components still retire
        return exc


@contextmanager
def activate(
    plan: ActivationPlan,
    *,
    emitter: Any,
    run_id: str,
    principal: str,
    build: Callable[[ActivationStep], Any] | None = None,
) -> Iterator[ActivationSession]:
    """Walk one activation and guarantee its teardown.

    Success walks `discover -> resolve -> verify -> activate` per component in
    plan order, yields, then `quiesce -> retire` in exact reverse order.

    Every fault path — a failing component, a raising body, cancellation, an
    evaluator failure, a crash — walks `fault -> cleanup -> retire` over
    precisely the components that were activated, newest first. A component
    that never activated is never retired, and one that did is always retired.

    Every component binds `run_id` and the composition digest, so the whole
    activation shares one run lineage and no component can be attributed to a
    composition it was not planned from.
    """
    session = ActivationSession(plan, run_id)
    #: The component currently being brought up. It has already emitted
    #: lifecycle events but has not joined the session, so it would otherwise be
    #: left stranded in `VERIFIED` by a failure — a component that announced
    #: itself and never resolved its own end state.
    pending: ActivatedComponent | None = None
    try:
        for step in plan.steps:
            lifecycle = PluginLifecycle(
                step.name, emitter, run_id=run_id, principal=principal,
                manifest_digest=plan.composition_digest,
            )
            pending = ActivatedComponent(step, lifecycle, None)
            lifecycle.resolve()
            lifecycle.verify(
                graph_digest=plan.composition_digest,
                ceiling_digest=digest_of(list(step.ceiling)),
            )
            cell = build(step) if build is not None else None
            lifecycle.activate()
            session._add(ActivatedComponent(step, lifecycle, cell))
            pending = None
        yield session
    except BaseException as exc:  # noqa: BLE001 - cancellation must clean up too
        reason = f"{type(exc).__name__}: {exc}"
        if pending is not None:
            pending_error = _retire(pending, faulted=True, reason=reason)
            if pending_error is not None:
                exc.add_note(f"pending component cleanup failed: {pending_error}")
        cleanup_errors = _teardown(session, faulted=True, reason=reason)
        for cleanup_error in cleanup_errors:
            exc.add_note(f"component cleanup failed: {cleanup_error}")
        raise
    else:
        cleanup_errors = _teardown(session, faulted=False, reason="")
        if cleanup_errors:
            raise ActivationError(
                "activation cleanup was not durably recorded: "
                + "; ".join(str(error) for error in cleanup_errors)
            )


def _teardown(session: ActivationSession, *, faulted: bool, reason: str) -> tuple[Exception, ...]:
    errors: list[Exception] = []
    for name in session.plan.cleanup_order:
        component = session._drop(name)
        if component is not None:
            error = _retire(component, faulted=faulted, reason=reason)
            if error is not None:
                errors.append(error)
    return tuple(errors)
