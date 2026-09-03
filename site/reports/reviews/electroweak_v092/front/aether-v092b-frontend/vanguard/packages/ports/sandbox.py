"""SandboxRunner interface.

Owning contract: ICD §4 SandboxRunner, REQ-PORT-005, VG-05 §6.2.
Invariants:
- Containment is a report, never a boolean claim without probes.
- Unverified reports block publication.
- Zero concrete implementation in this package except the publication gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

from .event_store import Result

__all__ = [
    "ProbeResult",
    "ContainmentReport",
    "SandboxReceipt",
    "SandboxResult",
    "SandboxRunner",
    "publication_decision",
]


@dataclass(frozen=True, slots=True)
class ProbeResult:
    """One startup probe that was actually attempted (K-42)."""

    kind: str  # "mount" | "egress" | "syscall"
    attempted: str
    observed: str
    verified: bool


@dataclass(frozen=True, slots=True)
class ContainmentReport:
    """Structured perimeter report. A lone `contained=true` is not sufficient."""

    runtime: str
    runtime_version: str
    namespace: str
    syscall_profile: str
    network_enforcement: str
    writable_mounts: tuple[str, ...]
    exposed_sockets: tuple[str, ...]
    resource_limits: Mapping[str, Any]
    startup_probes: tuple[ProbeResult, ...]
    attested_at: str
    contained: bool
    verified: bool
    visibility_mark: str


@dataclass(frozen=True, slots=True)
class SandboxReceipt:
    exit_code: int
    stdout_digest: str = ""


@dataclass(frozen=True, slots=True)
class SandboxResult:
    receipt: SandboxReceipt
    containment: ContainmentReport


class SandboxRunner(Protocol):
    """Execute argv inside a perimeter and return receipt plus containment report."""

    def execute(self, argv: Sequence[str]) -> Result[SandboxResult]:
        ...


def publication_decision(report: ContainmentReport) -> Result[None]:
    """Refuse to publish when containment was not verified (K-44)."""

    if not report.verified:
        return Result.fail(
            kind="denied",
            message="unverified containment report blocks publication",
        )
    return Result.success(None)
