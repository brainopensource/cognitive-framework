"""Deterministic doubles for the kernel suite.

Every one of these is substitutable in its **failure behaviour** as well as
its signature (`01 §2`, Liskov): the adapter returns a typed outcome rather
than raising for an ordinary failure, the clock is injected rather than read
from the environment, and the ledger either persists or raises.

The same builders are used by the must-fail counterparts in
`test/broken/fixtures/kernel/`, so a planted defect is injected at exactly one
seam and the rest of the kernel is the real thing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from vanguard.packages.kernel import (
    AdapterOutcome,
    Constraints,
    EffectRequest,
    Event,
    Governor,
    GrantIssuer,
    HeldAuthority,
    Kernel,
    Mode,
    Occurrence,
    Reservation,
    Scope,
    SinkClass,
    SinkRegistry,
    Span,
    StandardClassifier,
    StandardPolicy,
    Trust,
)

WORKSPACE = {"kind": "fs", "root": "/workspace", "paths": ["/workspace/src"]}
OUTSIDE = {"kind": "fs", "root": "/workspace", "paths": ["/workspace/../etc"]}
ETC = {"kind": "fs", "root": "/etc", "paths": ["/etc/shadow"]}
EGRESS = {"kind": "network", "hosts": ["evil.example.com"], "ports": [443]}

FAR_FUTURE = "2099-01-01T00:00:00.000Z"


class FakeClock:
    """Injected, monotone, and advanceable — which is what makes expiry
    testable without sleeping (`MF-KRN-005`)."""

    def __init__(self, start: str = "2026-08-15T09:00:00.000Z") -> None:
        self._now = start

    def now(self) -> str:
        return self._now

    def set(self, moment: str) -> None:
        self._now = moment


class FakeAdapter:
    """One typed effect, coordinating nothing (`ICD §3`)."""

    def __init__(
        self,
        name: str,
        *,
        outcome: AdapterOutcome | None = None,
        raises: Exception | None = None,
        healthy: bool = True,
        cost: Mapping[str, int] | None = None,
    ) -> None:
        self.name = name
        self._outcome = outcome
        self._raises = raises
        self._healthy = healthy
        self._cost = dict(cost or {"usd_micros": 100})
        self.calls: list[EffectRequest] = []

    def healthy(self) -> bool:
        return self._healthy

    def execute(self, request: EffectRequest) -> AdapterOutcome:
        self.calls.append(request)
        if self._raises is not None:
            raise self._raises
        if self._outcome is not None:
            return self._outcome
        return AdapterOutcome("ok", Occurrence.OCCURRED, self._cost,
                              result_digest="sha256:" + "1" * 64)


class RecordingLedger:
    """Durable intent. `append_intent` either persists or raises (`F-21a`)."""

    def __init__(self, *, fails: bool = False) -> None:
        self.entries: list[Event] = []
        self._fails = fails

    def append_intent(self, event: Event) -> None:
        if self._fails:
            raise OSError("fsync failed")
        self.entries.append(event)


class RecordingSink:
    """Event sink that records order, so `K-06` is checkable."""

    def __init__(self, *, fails: bool = False) -> None:
        self.events: list[Event] = []
        self._fails = fails

    def emit(self, event: Event) -> None:
        if self._fails:
            raise RuntimeError("event store unavailable")
        self.events.append(event)


class TracingGovernor(Governor):
    """Records the order of reserve/commit/release against emission."""

    def __init__(self, ceilings: Mapping[str, int], *,
                 release_fails: bool = False, trace: list[str] | None = None) -> None:
        super().__init__(ceilings)
        self.trace = trace if trace is not None else []
        self._release_fails = release_fails

    def reserve(self, run_id, reservation, parent_lease_id=None):
        lease = super().reserve(run_id, reservation, parent_lease_id)
        self.trace.append("reserve")
        return lease

    def commit(self, lease, actual):
        self.trace.append("commit")
        return super().commit(lease, actual)

    def release(self, lease):
        if self._release_fails:
            raise RuntimeError("release failed")
        if lease.state.value != "released":
            self.trace.append("release")
        super().release(lease)


def operator_span(span_id: str = "brief-1") -> Span:
    return Span(span_id, Trust.OPERATOR, "operator_brief")


def untrusted_result_span(span_id: str = "tool-result-1") -> Span:
    """`K-30`: a tool or environment result is untrusted-external **at
    construction**, never at consumption."""
    return Span(span_id, Trust.UNTRUSTED_EXTERNAL, "tool_result")


def constraints(**overrides: Any) -> Constraints:
    base = {
        "expires_at": FAR_FUTURE,
        "max_uses": 4,
        "budget_usd_micros": 1_000_000,
        "max_bytes": 1_048_576,
        "risk_ceiling": "high",
        "max_depth": 4,
        "network_policy": "deny",
    }
    base.update(overrides)
    return Constraints(**base)


def parent_scope(**overrides: Any) -> Scope:
    return Scope(
        actions=frozenset({"fs.read", "fs.write"}),
        resources=(WORKSPACE,),
        constraints=constraints(**overrides),
        depth=0,
    )


def request(**overrides: Any) -> EffectRequest:
    base: dict[str, Any] = {
        "action": "fs.write",
        "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace/src/a.ts"]},
        "args": {"path": "/workspace/src/a.ts", "bytes": "12"},
        "principal": "agent-1",
        "run_id": "run-1",
        "depth": 1,
        "justifying_spans": (operator_span(),),
        "declared_sink_class": SinkClass.PRIVILEGED,
    }
    base.update(overrides)
    return EffectRequest(**base)


@dataclass
class Harness:
    """A fully wired kernel plus the doubles, for assertions after dispatch."""

    kernel: Kernel
    clock: FakeClock
    ledger: RecordingLedger
    sink: RecordingSink
    governor: TracingGovernor
    issuer: GrantIssuer
    adapter: FakeAdapter
    trace: list[str]
    scope: Scope


def build(
    *,
    adapter: FakeAdapter | None = None,
    classifier: Any = None,
    policy: Any = None,
    ledger: RecordingLedger | None = None,
    sink: RecordingSink | None = None,
    governor: TracingGovernor | None = None,
    issuer: GrantIssuer | None = None,
    mode: Mode = Mode.INTERACTIVE,
    held_actions: frozenset[str] = frozenset({"fs.read", "fs.write"}),
    held_resources: Sequence[Mapping[str, Any]] = (WORKSPACE,),
    ceilings: Mapping[str, int] | None = None,
    approval_required_above: str | None = None,
    risk_of: Mapping[str, str] | None = None,
    scope: Scope | None = None,
) -> Harness:
    """Wire a kernel from real components and injectable seams."""
    trace: list[str] = []
    clock = FakeClock()
    adapter = adapter or FakeAdapter("fs.write")
    ledger = ledger or RecordingLedger()
    sink = sink or RecordingSink()
    governor = governor or TracingGovernor(
        ceilings or {"usd_micros": 10_000, "millis": 60_000}, trace=trace)
    if governor.trace is not trace:
        trace = governor.trace
    issuer = issuer or GrantIssuer()
    scope = scope or parent_scope()
    classifier = classifier or StandardClassifier([
        HeldAuthority("agent-1", held_actions, tuple(held_resources), max_depth=4)])
    policy = policy or StandardPolicy(
        parent_scope=scope, mode=mode,
        approval_required_above=approval_required_above, risk_of=risk_of)
    registry = SinkRegistry()
    registry.register("fs.write", SinkClass.PRIVILEGED)
    registry.register("fs.read", SinkClass.OBSERVATION)
    kernel = Kernel(
        adapters={adapter.name: adapter},
        policy=policy,
        classifier=classifier,
        governor=governor,
        issuer=issuer,
        clock=clock,
        ledger=ledger,
        events=_OrderedSink(sink, trace),
        sinks=registry,
    )
    return Harness(kernel, clock, ledger, sink, governor, issuer, adapter, trace, scope)


class _OrderedSink:
    """Wraps the sink so emission lands in the same trace as the lease calls."""

    def __init__(self, sink: RecordingSink, trace: list[str]) -> None:
        self._sink = sink
        self._trace = trace

    def emit(self, event: Event) -> None:
        self._trace.append(f"emit:{event.kind}")
        self._sink.emit(event)


def child_scope(**overrides: Any) -> Scope:
    base: dict[str, Any] = {
        "actions": frozenset({"fs.write"}),
        "resources": ({"kind": "fs", "root": "/workspace", "paths": ["/workspace/src/a.ts"]},),
        "constraints": constraints(),
        "depth": 1,
    }
    base.update(overrides)
    return Scope(**base)


def reservation(**overrides: int) -> Reservation:
    base = {"usd_micros": 500, "millis": 1000}
    base.update(overrides)
    return Reservation(**base)
