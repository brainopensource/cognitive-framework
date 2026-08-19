"""Shared Layer-0 test harness. Injected clock, no ambient I/O."""

from __future__ import annotations

from layer0.events.store import MemoryLedger
from layer0.kernel.attenuation import Constraints, Scope
from layer0.kernel.budget import Governor
from layer0.kernel.classifier import HeldAuthority, SinkRegistry, StandardClassifier
from layer0.kernel.dispatch import Kernel
from layer0.kernel.grants import GrantIssuer
from layer0.kernel.model import AdapterOutcome
from layer0.kernel.policy import StandardPolicy
from layer0.spi.types_gen import EffectRequest, Reservation, SinkClass


class FakeClock:
    def __init__(self) -> None:
        self._n = 0

    def now(self) -> str:
        self._n += 1
        return f"1970-01-01T00:00:{self._n:02d}.000Z"


class EchoAdapter:
    name = "echo"

    def healthy(self) -> bool:
        return True

    def execute(self, request: object, ctx: object) -> AdapterOutcome:
        _ = request, ctx
        return AdapterOutcome("ok", actual_cost={"tokens": 1})


SELECTOR = {"kind": "generic", "uriPattern": "echo://x"}

CONSTRAINTS = Constraints(
    expires_at="9999-01-01T00:00:00.000Z",
    max_uses=32,
    budget_usd_micros=10**9,
    max_depth=4,
)


def parent_scope() -> Scope:
    return Scope(
        actions=frozenset({"echo"}),
        resources=(SELECTOR,),
        constraints=CONSTRAINTS,
        depth=0,
    )


def echo_request(*, turns: int = 1, depth: int = 1) -> EffectRequest:
    return EffectRequest(
        verb="echo",
        args={},
        selector=SELECTOR,
        sink=SinkClass.ADVISORY,
        reservation=Reservation(0, 0, 8, 0, turns, depth),
    )


def build_kernel(ledger: MemoryLedger | None = None) -> tuple[Kernel, MemoryLedger]:
    store = ledger or MemoryLedger()
    sinks = SinkRegistry()
    sinks.register("echo", SinkClass.ADVISORY)
    kernel = Kernel(
        adapters={"echo": EchoAdapter()},
        policy=StandardPolicy(parent_scope=parent_scope()),
        classifier=StandardClassifier((
            HeldAuthority("episode", frozenset({"echo"}), (SELECTOR,), max_depth=4),
        )),
        governor=Governor({
            "usd_micros": 10**9,
            "millis": 10**9,
            "tokens": 10**6,
            "bytes": 10**9,
            "turns": 40,
            "depth": 4,
        }),
        issuer=GrantIssuer(),
        clock=FakeClock(),
        ledger=store,
        events=store,
        sinks=sinks,
    )
    return kernel, store
