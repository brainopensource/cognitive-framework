"""Pure value objects and protocol definitions for deterministic artifact transforms."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Mapping, Protocol, runtime_checkable

TransformStatus = Literal[
    "accepted",
    "rejected",
    "unchanged",
    "retryable_error",
    "fatal_error",
]

DiagnosticSeverity = Literal["info", "warning", "error"]


@dataclass(frozen=True, slots=True)
class TransformSpec:
    """Immutable specification declaring transform capabilities and resource bounds."""

    transform_id: str
    version: str
    input_schema: str
    output_schema: str
    config_digest: str = ""
    deterministic: bool = True
    max_input_bytes: int = 10_000_000
    max_output_bytes: int = 10_000_000
    timeout_seconds: float = 30.0


@dataclass(frozen=True, slots=True)
class TransformInput:
    """Descriptor referencing a content-addressed input artifact."""

    artifact_digest: str
    schema_id: str
    labels: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TransformDiagnostic:
    """Structured diagnostic message emitted during transform execution."""

    code: str
    severity: DiagnosticSeverity
    message: str
    location: str | None = None


@dataclass(frozen=True, slots=True)
class TransformOutput:
    """In-memory payload and diagnostics produced by a pure transform implementation."""

    status: TransformStatus
    payload: bytes | None = None
    output_schema: str | None = None
    diagnostics: tuple[TransformDiagnostic, ...] = field(default_factory=tuple)
    confidence_ppm: int = 1_000_000


@dataclass(frozen=True, slots=True)
class TransformResult:
    """Settled, content-addressed result of an artifact transform execution."""

    status: TransformStatus
    output_digest: str | None
    output_schema: str | None
    diagnostics: tuple[TransformDiagnostic, ...]
    confidence_ppm: int = 1_000_000


@runtime_checkable
class ArtifactTransform(Protocol):
    """Protocol for pure, deterministic artifact transformations."""

    @property
    def spec(self) -> TransformSpec:
        ...

    def apply(
        self,
        payload: bytes,
        config: Mapping[str, object] | None = None,
    ) -> TransformOutput:
        ...


@runtime_checkable
class ProposalDecoderProtocol(Protocol):
    """Protocol for decoding model response dialects into proposal mappings (Invariant I3)."""

    def decode(self, raw: object) -> Mapping[str, object] | None:
        ...
