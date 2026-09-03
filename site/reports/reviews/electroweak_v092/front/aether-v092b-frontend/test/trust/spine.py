"""The composition root for the no-model trust spine (`REQ-TRUST-001`).

`ADR-0048`: model behaviour must not become a prerequisite of kernel
verification. So the whole trajectory here is a **tape** — an ordered list of
proposals written by hand. Nothing in this module or anything it imports
reaches a provider, and `test_spine.py` asserts that as a property of the
loaded module graph rather than as a promise.

Everything below the tape is the real thing: the real `Kernel`, the real
`Governor`, `GrantIssuer`, `StandardPolicy`, `StandardClassifier` and
`SinkRegistry`, and a real `InMemoryEventStore` behind the shared ledger. The
only doubles are the seams the architecture already requires to be injected —
the clock (`MF-KRN-005`), the effect adapters, and the tape that stands where
a `ModelPort` would.

`margin: zero model imports on the gate path`. That is why the tape is a
literal list and not a cassette player: a cassette is still a provider-shaped
component, and this gate is meant to hold when no provider exists at all.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from vanguard.packages.agency import EpisodeEngine
from vanguard.packages.kernel import (
    AdapterOutcome,
    Constraints,
    Governor,
    GrantIssuer,
    HeldAuthority,
    Kernel,
    Occurrence,
    Scope,
    SinkClass,
    SinkRegistry,
    Span,
    StandardClassifier,
    StandardPolicy,
    Trust,
)

from test.support.composition import SharedLedger

__all__ = [
    "PRINCIPAL",
    "EVALUATOR_PRINCIPAL",
    "SECRET_REFERENCE",
    "SECRET_VALUE",
    "WORKSPACE",
    "Spine",
    "SecretAdapter",
    "StaticAdapter",
    "ETC",
    "Tape",
    "build",
    "receipt_span",
]

PRINCIPAL = "agent-1"
#: `ICD §6`: the evaluator is a separate identity. Only the *principal* is
#: modelled here — OS-level isolation is Sprint 5, and pretending otherwise
#: would be exactly the inferred containment `ICD §6` refuses.
EVALUATOR_PRINCIPAL = "evaluator-1"

WORKSPACE: Mapping[str, Any] = {
    "kind": "fs", "root": "/workspace", "paths": ["/workspace/src"]}
ETC: Mapping[str, Any] = {"kind": "fs", "root": "/etc", "paths": ["/etc/shadow"]}

#: A secret is held by *reference* in everything the run can observe or
#: record; only the adapter can resolve one (`REQ-PORT-006` margin: zero
#: secrets in events or exports).
SECRET_REFERENCE = "secret://provider/api-key"
SECRET_VALUE = "sk-live-do-not-record-4f2b9c"

FAR_FUTURE = "2099-01-01T00:00:00.000Z"


class Clock:
    """Injected and advanceable, so expiry and lease timeout are testable
    without sleeping (`MF-KRN-005`)."""

    def __init__(self, start: str = "2026-08-15T10:00:00.000Z") -> None:
        self._now = start

    def now(self) -> str:
        return self._now

    def set(self, moment: str) -> None:
        self._now = moment


class Tape:
    """A hand-written proposal sequence. Not a provider, and not a port.

    Exhaustion returns a typed failure rather than raising, because the loop
    must reduce it to `instrument_error` and never to a task verdict
    (`VG-03 §6.2`, `CT-33`).
    """

    def __init__(self, proposals: Sequence[Any]) -> None:
        self._proposals = list(proposals)
        self._cursor = 0
        self.views: list[Mapping[str, Any]] = []

    def propose(self, context: Mapping[str, Any], tools: Any, sampling: Any) -> Any:
        self.views.append(dict(context))
        if self._cursor >= len(self._proposals):
            return _Result(False, error=_Failure("instrument_error", "tape exhausted"))
        proposal = self._proposals[self._cursor]
        self._cursor += 1
        return _Result(True, value=proposal)


@dataclass(frozen=True, slots=True)
class _Failure:
    kind: str
    message: str
    retryable: bool = False


@dataclass(frozen=True, slots=True)
class _Result:
    ok: bool
    value: Any = None
    error: _Failure | None = None


class StaticAdapter:
    """One typed effect that coordinates nothing (`ICD §3`)."""

    def __init__(self, name: str, *, cost: Mapping[str, int] | None = None,
                 outcome: AdapterOutcome | None = None,
                 raises: Exception | None = None) -> None:
        self.name = name
        self._cost = dict(cost or {"usd_micros": 100, "millis": 10})
        self._outcome = outcome
        self._raises = raises
        self.calls: list[Any] = []

    def healthy(self) -> bool:
        return True

    def execute(self, request: Any) -> AdapterOutcome:
        self.calls.append(request)
        if self._raises is not None:
            raise self._raises
        if self._outcome is not None:
            return self._outcome
        return AdapterOutcome("ok", Occurrence.OCCURRED, self._cost,
                              result_digest="sha256:" + "1" * 64)


class SecretAdapter(StaticAdapter):
    """Resolves a secret reference. The value exists **only** in here.

    The adapter is the boundary the secret does not cross: it never returns
    the value, never puts it in `detail`, and never puts it in the result
    digest. A run therefore cannot disclose what it was never given.
    """

    def __init__(self, name: str = "secret.send") -> None:
        super().__init__(name)
        self.resolved: list[str] = []

    def execute(self, request: Any) -> AdapterOutcome:
        self.calls.append(request)
        reference = request.args.get("secretRef")
        if reference != SECRET_REFERENCE:
            return AdapterOutcome("error", Occurrence.DID_NOT_OCCUR,
                                  {"usd_micros": 1}, detail="unknown secret reference")
        self.resolved.append(SECRET_VALUE)
        return AdapterOutcome("ok", Occurrence.OCCURRED, {"usd_micros": 100, "millis": 10},
                              result_digest="sha256:" + "2" * 64)


def constraints(**overrides: Any) -> Constraints:
    base: dict[str, Any] = {
        "expires_at": FAR_FUTURE,
        "max_uses": 8,
        "budget_usd_micros": 1_000_000,
        "max_bytes": 1_048_576,
        "risk_ceiling": "high",
        "max_depth": 4,
        "network_policy": "deny",
    }
    base.update(overrides)
    return Constraints(**base)


def parent_scope(**overrides: Any) -> Scope:
    base: dict[str, Any] = {
        "actions": frozenset({"fs.read", "fs.write", "secret.send"}),
        "resources": (WORKSPACE,),
        "constraints": constraints(),
        "depth": 0,
    }
    base.update(overrides)
    return Scope(**base)


def requested_scope(**overrides: Any) -> Scope:
    base: dict[str, Any] = {
        "actions": frozenset({"fs.write", "secret.send"}),
        "resources": (WORKSPACE,),
        "constraints": constraints(),
        "depth": 1,
    }
    base.update(overrides)
    return Scope(**base)


def operator_span(span_id: str = "brief-1") -> Span:
    return Span(span_id, Trust.OPERATOR, "operator_brief")


def receipt_span(turn: int, outcome: Any) -> Span:
    """Label a receipt at its **source class** (`K-30`).

    An effect receipt is external content: it may inform the next turn and it
    may never authorise one. The label is fixed here, in the composition root,
    rather than decided by the loop at the point of consumption (`K-31`).
    """
    return Span(f"receipt-{turn}", Trust.UNTRUSTED_EXTERNAL, "tool_result")


@dataclass
class Spine:
    """Everything the trajectory needs to assert against, wired once."""

    engine: EpisodeEngine
    kernel: Kernel
    ledger: SharedLedger
    governor: Governor
    clock: Clock
    tape: Tape
    adapters: Mapping[str, StaticAdapter]
    scope: Scope

    def run(self, **overrides: Any) -> Any:
        kwargs: dict[str, Any] = {
            "episode_id": "episode-trust",
            "run_id": "run-trust",
            "principal": PRINCIPAL,
            "brief": "scripted trust-spine trajectory",
            "spans": (operator_span(),),
            "receipt_labeller": receipt_span,
        }
        kwargs.update(overrides)
        return self.engine.run(**kwargs)


def build(
    proposals: Sequence[Any],
    *,
    ceilings: Mapping[str, int] | None = None,
    adapters: Mapping[str, StaticAdapter] | None = None,
    scope: Scope | None = None,
    parent: Scope | None = None,
    held_actions: frozenset[str] = frozenset({"fs.write", "secret.send"}),
    held_resources: Sequence[Mapping[str, Any]] = (WORKSPACE,),
    ledger: SharedLedger | None = None,
    max_turns: int = 8,
) -> Spine:
    """Wire the spine. This is the only place that knows a concrete adapter."""
    clock = Clock()
    ledger = ledger if ledger is not None else SharedLedger(episode_id="episode-trust")
    wired: dict[str, StaticAdapter] = dict(adapters or {
        "fs.write": StaticAdapter("fs.write"),
        "fs.delete": StaticAdapter("fs.delete"),
        "secret.send": SecretAdapter(),
    })
    governor = Governor(dict(ceilings or {"usd_micros": 10_000, "millis": 60_000}))
    registry = SinkRegistry()
    for action in wired:
        registry.register(action, SinkClass.PRIVILEGED)

    kernel = Kernel(
        adapters=wired,
        policy=StandardPolicy(parent_scope=parent or parent_scope()),
        classifier=StandardClassifier([
            HeldAuthority(PRINCIPAL, held_actions, tuple(held_resources), max_depth=4)]),
        governor=governor,
        issuer=GrantIssuer(),
        clock=clock,
        ledger=ledger,
        events=ledger,
        sinks=registry,
    )
    tape = Tape(proposals)
    granted = scope or requested_scope()
    engine = EpisodeEngine(
        kernel=kernel,
        model=tape,
        clock=clock,
        events=ledger,
        scope=granted,
        max_turns=max_turns,
    )
    return Spine(engine=engine, kernel=kernel, ledger=ledger, governor=governor,
                 clock=clock, tape=tape, adapters=wired, scope=granted)


# -- tape vocabulary ---------------------------------------------------

def effect(action: str = "fs.write", *, path: str = "/workspace/src/a.ts",
           args: Mapping[str, Any] | None = None, **reservation: int) -> Mapping[str, Any]:
    return {
        "kind": "effect",
        "action": action,
        "resource": {"kind": "fs", "root": "/workspace", "paths": [path]},
        "args": dict(args) if args is not None else {"path": path, "bytes": "12"},
        "reservation": dict(reservation) or {"usd_micros": 500, "millis": 1000},
    }


def send_secret(**reservation: int) -> Mapping[str, Any]:
    """A privileged effect that needs a secret it is never given."""
    return effect("secret.send", args={"secretRef": SECRET_REFERENCE,
                                       "path": "/workspace/src/a.ts"}, **reservation)


def finish(note: str = "done") -> Mapping[str, Any]:
    return {"kind": "finish", "note": note}
