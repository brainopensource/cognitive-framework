"""Deterministic SPI fakes. No ambient I/O, clock, or randomness."""

from __future__ import annotations

from typing import ClassVar, Mapping, Sequence

from .interfaces import (
    IContextManager,
    IEvaluationGate,
    IMemoryEngine,
    IPlanner,
    IToolkit,
)
from .result import Err, Ok, Result
from .types_gen import (
    ClaimRef,
    CompactionReport,
    ConsolidationReport,
    ContextBundle,
    EffectContext,
    EffectFailure,
    EffectRequest,
    EpisodeOutcome,
    EpisodeView,
    EvaluationRequestId,
    EvaluationSubject,
    GateDecision,
    Health,
    MemoryHit,
    MemoryId,
    MemoryQuery,
    MemoryRecord,
    OracleSpec,
    PreregistrationId,
    Proposal,
    Receipt,
    Reflection,
    Reservation,
    SignedVerdict,
    ToolSchema,
    TrajectoryRef,
)

__all__ = [
    "EchoToolkit",
    "FixedGate",
    "IdentityContext",
    "InMemoryEngine",
    "ScriptedPlanner",
]


class ScriptedPlanner:
    spi_version: ClassVar[str] = "1.0"

    def __init__(self, proposals: Sequence[Proposal]) -> None:
        self._proposals = list(proposals)
        self.observed: list[tuple[Receipt, ...]] = []
        self.reflections: list[Reflection] = []

    def plan(self, view: EpisodeView, budget: Reservation) -> Result[Proposal]:
        if not self._proposals:
            return Err("empty_script", "no remaining proposals")
        if budget.turns <= 0:
            return Err("budget_exhausted", "no turns remaining")
        _ = view
        return Ok(self._proposals.pop(0))

    def observe(self, receipts: Sequence[Receipt], view: EpisodeView) -> None:
        _ = view
        self.observed.append(tuple(receipts))

    def reflect(
        self, outcome: EpisodeOutcome, trajectory: TrajectoryRef,
    ) -> Result[Reflection | None]:
        _ = outcome, trajectory
        if self.reflections:
            return Ok(self.reflections.pop(0))
        return Ok(None)


class EchoToolkit:
    spi_version: ClassVar[str] = "1.0"

    def verbs(self) -> Mapping[str, ToolSchema]:
        return {"echo": ToolSchema(verb="echo", schema={"type": "object"})}

    def execute(self, request: EffectRequest, ctx: EffectContext) -> Result[Receipt]:
        _ = ctx
        return Ok(Receipt(
            request_digest="sha256:" + "0" * 64,
            outcome="completed",
            cost=request.reservation,
        ))

    def compensate(self, receipt: Receipt) -> Result[Receipt]:
        return Ok(receipt)

    def health(self) -> Health:
        return Health(ok=True)


class InMemoryEngine:
    spi_version: ClassVar[str] = "1.0"

    def __init__(self) -> None:
        self._records: dict[str, MemoryRecord] = {}
        self._counter = 0

    def write(self, record: MemoryRecord) -> Result[MemoryId]:
        self._counter += 1
        ident = f"mem-{self._counter}"
        self._records[ident] = record
        return Ok(ident)

    def recall(self, query: MemoryQuery, budget_tokens: int) -> Result[tuple[MemoryHit, ...]]:
        _ = budget_tokens
        hits = []
        for ident, record in self._records.items():
            if query.text in record.text:
                hits.append(MemoryHit(id=ident, text=record.text, score=1.0))
        return Ok(tuple(hits[: query.limit or len(hits)]))

    def consolidate(self, since: int) -> Result[ConsolidationReport]:
        _ = since
        return Ok(ConsolidationReport(merged=0, dropped=0))

    def invalidate(self, claim: ClaimRef, reason: str) -> Result[None]:
        _ = claim, reason
        return Ok(None)

    def capabilities(self) -> frozenset[str]:
        return frozenset({"kv"})


class IdentityContext:
    spi_version: ClassVar[str] = "1.0"

    def compile(self, view: EpisodeView, budget_tokens: int) -> Result[ContextBundle]:
        _ = budget_tokens
        return Ok(ContextBundle(prefix=view.goal, suffix="", token_count=0))

    def ingest(self, receipts: Sequence[Receipt]) -> None:
        _ = receipts

    def compact(self, pressure: float) -> Result[CompactionReport]:
        _ = pressure
        return Ok(CompactionReport(removed_tokens=0, strategy="identity"))

    def reground(self, error: EffectFailure) -> Result[ContextBundle]:
        return Ok(ContextBundle(prefix=error.detail, suffix="", token_count=0))


class FixedGate:
    spi_version: ClassVar[str] = "1.0"

    def __init__(self, decision: GateDecision = GateDecision.PASS) -> None:
        self._decision = decision
        self.requested: list[EvaluationSubject] = []

    def request(self, subject: EvaluationSubject) -> Result[EvaluationRequestId]:
        self.requested.append(subject)
        return Ok(f"eval-{len(self.requested)}")

    def gate(self, verdicts: Sequence[SignedVerdict]) -> GateDecision:
        _ = verdicts
        return self._decision

    def preregister(self, oracle: OracleSpec) -> Result[PreregistrationId]:
        return Ok(oracle.id)
