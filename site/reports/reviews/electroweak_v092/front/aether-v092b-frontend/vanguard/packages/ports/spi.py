"""Frozen SPI protocols (SPEC §2.2, ADR-M0-03).

Owning contract: Wave-2 2.1-C. Moved from `layer0/spi/interfaces.py`
(ADR-0069, ADR-0072): the six Protocols are client conveniences of the wire,
not a new authority surface, so they land here as ports -- interfaces only,
importing only the generated wire types and the SPI `Result` ADT from
`domain/wire/`. The completion policy is the pack-composed admission seam.
"""

from __future__ import annotations

from typing import Any, ClassVar, Mapping, Protocol, Sequence, runtime_checkable

from ..domain.wire.result import Result
from ..domain.wire.types_gen import (
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
    "ICompletionPolicy",
    "IContextManager",
    "IEvaluationGate",
    "IMemoryEngine",
    "IPlanner",
    "IToolkit",
]


@runtime_checkable
class ICompletionPolicy(Protocol):
    """Composed admission policy for terminal task completion.

    The runtime supplies observations only; the pack-owned implementation
    returns an ``AdmissionVerdict``-shaped value without gaining effect
    authority. Keyword arguments keep the seam extensible for repository
    closure, greenfield, and future task-specific evidence.
    """

    spi_version: ClassVar[str]

    def evaluate(self, **observations: Any) -> Any: ...


@runtime_checkable
class IPlanner(Protocol):
    """Turn-level cognition. Inner planners emit Proposals."""

    spi_version: ClassVar[str]

    def plan(self, view: EpisodeView, budget: Reservation) -> Result[Proposal]: ...

    def observe(self, receipts: Sequence[Receipt], view: EpisodeView) -> None: ...

    def reflect(
        self, outcome: EpisodeOutcome, trajectory: TrajectoryRef,
    ) -> Result[Reflection | None]: ...


@runtime_checkable
class IContextManager(Protocol):
    """Prefix-stable prompt assembly. L1–L3 frozen at composition."""

    spi_version: ClassVar[str]

    def compile(self, view: EpisodeView, budget_tokens: int) -> Result[ContextBundle]: ...

    def ingest(self, receipts: Sequence[Receipt]) -> None: ...

    def compact(self, pressure: float) -> Result[CompactionReport]: ...

    def reground(self, error: EffectFailure) -> Result[ContextBundle]: ...


@runtime_checkable
class IToolkit(Protocol):
    """Effect adapters. Toolkits never see grants — only verified, leased work."""

    spi_version: ClassVar[str]

    def verbs(self) -> Mapping[str, ToolSchema]: ...

    def execute(self, request: EffectRequest, ctx: EffectContext) -> Result[Receipt]: ...

    def compensate(self, receipt: Receipt) -> Result[Receipt]: ...

    def health(self) -> Health: ...


@runtime_checkable
class IMemoryEngine(Protocol):
    """Episodic and semantic memory. Graph is a negotiated capability, not a sixth SPI."""

    spi_version: ClassVar[str]

    def write(self, record: MemoryRecord) -> Result[MemoryId]: ...

    def recall(self, query: MemoryQuery, budget_tokens: int) -> Result[tuple[MemoryHit, ...]]: ...

    def consolidate(self, since: int) -> Result[ConsolidationReport]: ...

    def invalidate(self, claim: ClaimRef, reason: str) -> Result[None]: ...

    def capabilities(self) -> frozenset[str]: ...


@runtime_checkable
class IEvaluationGate(Protocol):
    """Agent-side evidence plane. Requests judgment; never renders it."""

    spi_version: ClassVar[str]

    def request(self, subject: EvaluationSubject) -> Result[EvaluationRequestId]: ...

    def gate(self, verdicts: Sequence[SignedVerdict]) -> GateDecision: ...

    def preregister(self, oracle: OracleSpec) -> Result[PreregistrationId]: ...
