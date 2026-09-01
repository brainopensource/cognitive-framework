"""EnvironmentAdapter port interface.

Owning contract: ICD §4 EnvironmentAdapter, REQ-PORT-003, VG-03 §7.1.
Invariants:
- Ports accept and return domain/schema types only.
- Failures are typed Result objects, not arbitrary unclassified exceptions.
- Tests are argv arrays, never shell strings (slice-findings.md).
- Preview includes new files, modified files, deleted files, and diff.
- Zero path traversal escapes permitted.
- Zero concrete implementation in this package.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Protocol, Sequence

from .event_store import Result

__all__ = [
    "EnvironmentProfile",
    "EnvironmentSnapshot",
    "ObservationRequest",
    "Observation",
    "AffectedResource",
    "EffectRequest",
    "EffectPreview",
    "EffectReceipt",
    "Reconciliation",
    "EnvironmentAdapter",
]


@dataclass(frozen=True, slots=True)
class EnvironmentProfile:
    """Environment metadata and declared capabilities (VG-03 §7.1)."""

    environment_id: str
    kind: str  # "memory" | "git" | "tableworld"
    root: str
    capabilities: Sequence[str] = field(default_factory=tuple)
    properties: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EnvironmentSnapshot:
    """Versioned snapshot token binding the environment state (VG-03 §7.1)."""

    snapshot_id: str
    digest: str  # "sha256:..."
    created_at: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ObservationRequest:
    """Query to read or inspect workspace state."""

    action: str  # "read" | "search" | "list" | "stat"
    path: Optional[str] = None
    pattern: Optional[str] = None
    args: Mapping[str, Any] = field(default_factory=dict)
    selector: Optional[Mapping[str, Any]] = None


@dataclass(frozen=True, slots=True)
class Observation:
    """Typed observation result from inspecting the environment."""

    action: str
    content: Optional[str] = None
    matches: Sequence[Mapping[str, Any]] = field(default_factory=tuple)
    files: Sequence[str] = field(default_factory=tuple)
    output: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AffectedResource:
    """Individual resource change record matching Receipt schema."""

    resource: str
    change: str  # "created" | "modified" | "deleted" | "observed"
    pre_digest: Optional[str] = None
    post_digest: Optional[str] = None
    patch_ref: Optional[str] = None


@dataclass(frozen=True, slots=True)
class EffectRequest:
    """Effect proposal submitted to the environment boundary."""

    verb: str  # "fs.read" | "fs.write" | "patch.apply" | "proc.exec" | "test.run"
    action: str  # "write" | "patch" | "test" | "exec" | "delete"
    args: Mapping[str, Any] = field(default_factory=dict)
    patch: Optional[str] = None
    command: Optional[Sequence[str]] = None  # Must be argv array, NEVER a shell string
    working_directory: Optional[str] = None
    idempotency_key: Optional[str] = None
    selector: Optional[Mapping[str, Any]] = None


@dataclass(frozen=True, slots=True)
class EffectPreview:
    """Two-phase preview of proposed changes, including new files (VG-03 §7.5)."""

    diff: str
    affected_resources: Sequence[AffectedResource] = field(default_factory=tuple)
    new_files: Sequence[str] = field(default_factory=tuple)
    modified_files: Sequence[str] = field(default_factory=tuple)
    deleted_files: Sequence[str] = field(default_factory=tuple)
    stat: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EffectReceipt:
    """Verifiable receipt for an applied effect."""

    descriptor_digest: str
    outcome: str  # "ok" | "failed" | "undeterminable"
    observed_at: str
    result_digest: str
    affected_resources: Sequence[AffectedResource] = field(default_factory=tuple)
    exit_code: Optional[int] = None
    output: Optional[str] = None
    diff: Optional[str] = None
    grant_id: Optional[str] = None


@dataclass(frozen=True, slots=True)
class Reconciliation:
    """Reconciliation verdict comparing expected receipt against ground truth."""

    matched: bool
    current_digest: str
    expected_digest: str
    divergence: Optional[str] = None


class EnvironmentAdapter(Protocol):
    """Universal environment protocol (VG-03 §7.1, ICD §4)."""

    def profile(self) -> Result[EnvironmentProfile]:
        """Return environment profile and declared capabilities."""
        ...

    def snapshot(self) -> Result[EnvironmentSnapshot]:
        """Return a versioned snapshot token binding the environment state."""
        ...

    def observe(self, req: ObservationRequest, grant: Optional[Any] = None) -> Result[Observation]:
        """Perform a selector-checked observation."""
        ...

    def preview(self, req: EffectRequest, grant: Optional[Any] = None) -> Result[EffectPreview]:
        """Return a preview of the effect outcome including new files and diff."""
        ...

    def apply(self, req: EffectRequest, grant: Optional[Any] = None) -> Result[EffectReceipt]:
        """Apply the effect and return a verifiable receipt."""
        ...

    def reconcile(self, receipt: EffectReceipt, grant: Optional[Any] = None) -> Result[Reconciliation]:
        """Reconcile environment state against an effect receipt."""
        ...

    def compensate(self, receipt: EffectReceipt, grant: Optional[Any] = None) -> Result[EffectReceipt]:
        """Roll back or compensate an applied effect."""
        ...

    def dispose(self) -> Result[None]:
        """Clean up ephemeral resources associated with this adapter."""
        ...
