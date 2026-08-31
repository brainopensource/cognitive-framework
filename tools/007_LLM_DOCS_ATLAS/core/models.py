"""Domain models for LDA with backwards compatibility and IR integration."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional
from .ir import ConfidenceTier, EntityKind, RelationKind, RepresentationKind, to_dict

@dataclass(frozen=True)
class Entity:
    id: str
    kind: str
    locator: str
    authority: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Relation:
    source: str
    target: str
    kind: str
    evidence: str | None = None

@dataclass(frozen=True)
class Diagnostic:
    severity: str
    code: str
    message: str
    locator: str | None = None
    provider: str = "lda"

@dataclass(frozen=True)
class Metric:
    name: str
    value: int | float
    unit: str
    locator: str | None = None

@dataclass
class ProviderResult:
    provider: str
    entities: list[Entity] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)
    metrics: list[Metric] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Candidate:
    locator: str
    kind: str
    title: str
    score: float
    tokens: int
    reason: str
    authority: str | None = None
    representation: str = "FULL"
    content: Optional[str] = None
    provenance_ref: Optional[str] = None

@dataclass
class ContextPacket:
    task: str
    budget: int
    estimated_tokens: int
    documents: list[Candidate] = field(default_factory=list)
    code: list[Candidate] = field(default_factory=list)
    symbols: list[Candidate] = field(default_factory=list)
    tests: list[Candidate] = field(default_factory=list)
    authority: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    callers: list[dict[str, Any]] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    token_accounting: dict[str, int] = field(default_factory=dict)

def serialise(value: Any) -> Any:
    return to_dict(value)
