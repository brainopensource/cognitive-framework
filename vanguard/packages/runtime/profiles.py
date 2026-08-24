"""`ExecutionProfile` — identity-bearing deployment/assurance config (`ADR-0089 §Decision 1,5`).

`D_H` says what was composed; `D_R` says what environment it ran in. Before
W-3D, deployment (`sandbox_mode`) and release-ness (`release: bool`) were
selected inline in `root.py`/`lab_driver.py` and only partially reached
`D_R` through `environment`/`store`/`model_route`. `ExecutionProfile`
consolidates the remaining axes — approval, persistence, evaluation,
assurance, capture — into one resolved, versioned, digested value that MUST
enter `RunPlan`/`D_R` (`RF-87`).

Three axes are kept explicitly separate and never merged into a single
scalar `trust_tier`:

* **containment** — what the process backend and workspace access are;
* **approval** — who authorizes an effect before it runs;
* **assurance** — what a resulting run is eligible to prove or promote.

The effective ceiling for any run is the monotonic intersection of
organization ceiling, selected profile, harness ceiling, agent policy, and
request — an override may only narrow, never widen (`ADR-0089 §4.2`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..domain.canonicalisation.digest import digest_of

__all__ = [
    "ExecutionProfileError",
    "SandboxUnavailable",
    "ExecutionProfile",
    "EffectiveExecutionProfile",
    "PRESETS",
    "resolve_profile",
]


class ExecutionProfileError(ValueError):
    """A profile request or resolution that must not proceed."""


class SandboxUnavailable(ExecutionProfileError):
    """`sandboxed`/`hermetic` was requested and the backend is not qualified.

    There is no silent fallback to `host`/`local`. The caller may construct
    and run a *new*, separately identified `local` profile explicitly — that
    is a new `D_R`, never a substitution under the same one (`ADR-0089 §4.3`).
    """


@dataclass(frozen=True, slots=True)
class ExecutionProfile:
    """One named, versioned deployment/assurance configuration (`mhf.execution-profile/1`)."""

    id: str
    workspace_mode: str  # "in-place" | "sealed"
    workspace_access: str  # "read-only" | "workspace-write"
    process_backend: str  # "host" | "platform-sandbox"
    approval_default: str  # "allow" | "ask" | "deny"
    persistence_mode: str  # "sqlite-wal" | "memory"
    persistence_durable: bool
    evaluation_mode: str  # "none" | "exterior"
    assurance_level: str  # "recorded" | "hermetic"
    attestation_required: bool
    promotion_eligible: bool
    capture_content: str = "redacted"  # "redacted" | "full"
    evaluation_absence_reason: str = ""
    network_mode: str = "inherited"

    def __post_init__(self) -> None:
        if self.process_backend not in {"host", "platform-sandbox"}:
            raise ExecutionProfileError(f"unknown process backend {self.process_backend!r}")
        if self.assurance_level == "hermetic" and not self.attestation_required:
            raise ExecutionProfileError("hermetic assurance requires attestation")
        if self.promotion_eligible and self.assurance_level != "hermetic":
            raise ExecutionProfileError("only hermetic assurance may be promotion-eligible")
        if self.evaluation_mode == "none" and not self.evaluation_absence_reason:
            raise ExecutionProfileError("evaluation:none requires an absence_reason")

    def to_dict(self) -> Mapping[str, Any]:
        """The canonical JSON form; also the `profile_digest` preimage."""
        return {
            "api": "mhf.execution-profile/1",
            "id": self.id,
            "workspace": {"mode": self.workspace_mode, "access": self.workspace_access},
            "process": {"backend": self.process_backend, "fallback": "deny"},
            "network": {"mode": self.network_mode, "allow": []},
            "approval": {"default": self.approval_default, "rules": []},
            "persistence": {"mode": self.persistence_mode, "durable": self.persistence_durable},
            "evaluation": {
                "mode": self.evaluation_mode,
                **({"absence_reason": self.evaluation_absence_reason} if self.evaluation_mode == "none" else {}),
            },
            "assurance": {
                "level": self.assurance_level,
                "attestation_required": self.attestation_required,
                "promotion_eligible": self.promotion_eligible,
            },
            "capture": {"content": self.capture_content, "trainability": "prohibited"},
        }

    @property
    def digest(self) -> str:
        """`profile_digest` — the value that MUST change whenever effective execution does."""
        return digest_of(self.to_dict())


PRESETS: Mapping[str, ExecutionProfile] = {
    "local": ExecutionProfile(
        id="local",
        workspace_mode="in-place",
        workspace_access="workspace-write",
        process_backend="host",
        approval_default="ask",
        persistence_mode="sqlite-wal",
        persistence_durable=True,
        evaluation_mode="none",
        evaluation_absence_reason="local product run: no exterior evaluator engaged",
        assurance_level="recorded",
        attestation_required=False,
        promotion_eligible=False,
    ),
    "sandboxed": ExecutionProfile(
        id="sandboxed",
        workspace_mode="in-place",
        workspace_access="workspace-write",
        process_backend="platform-sandbox",
        approval_default="ask",
        persistence_mode="sqlite-wal",
        persistence_durable=True,
        evaluation_mode="none",
        evaluation_absence_reason="sandboxed product run: evaluator optional, not engaged by default",
        assurance_level="recorded",
        attestation_required=False,
        promotion_eligible=False,
    ),
    "hermetic": ExecutionProfile(
        id="hermetic",
        workspace_mode="sealed",
        workspace_access="workspace-write",
        process_backend="platform-sandbox",
        approval_default="deny",
        persistence_mode="sqlite-wal",
        persistence_durable=True,
        evaluation_mode="exterior",
        assurance_level="hermetic",
        attestation_required=True,
        promotion_eligible=True,
    ),
}


@dataclass(frozen=True, slots=True)
class EffectiveExecutionProfile:
    """A resolved profile bound to observed host facts.

    `requested` is what the caller/config asked for; `host_facts` is what a
    capability probe (`adapters/sandbox/platform.py`) actually found. The two
    are kept distinct: a profile is never silently rewritten to match a
    weaker host. If the host cannot satisfy the requested profile,
    resolution raises `SandboxUnavailable` — it does not downgrade.
    """

    requested: ExecutionProfile
    host_facts: Mapping[str, Any] = field(default_factory=dict)

    @property
    def digest(self) -> str:
        return digest_of({"profile": self.requested.to_dict(), "host": dict(self.host_facts)})

    def to_run_plan_fields(self) -> Mapping[str, Any]:
        """The subset of the effective profile that enters `RunPlan`/`D_R`."""
        return {
            "profileId": self.requested.id,
            "profileDigest": self.digest,
            "assuranceLevel": self.requested.assurance_level,
            "promotionEligible": self.requested.promotion_eligible,
        }


def resolve_profile(
    profile_id: str,
    *,
    host_qualifies: bool = True,
    host_facts: Mapping[str, Any] | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> EffectiveExecutionProfile:
    """Resolve a named preset (or override) to one `EffectiveExecutionProfile`.

    `local` never fails here: host is the backend it asked for, so there is
    no fallback question. `sandboxed`/`hermetic` raise `SandboxUnavailable`
    if `host_qualifies` is false — the caller must request a new profile
    explicitly (typically `local`, with its own approval) rather than
    receive a silent substitution (`RF-88`).
    """
    try:
        base = PRESETS[profile_id]
    except KeyError:
        raise ExecutionProfileError(f"unknown execution profile {profile_id!r}") from None
    if overrides:
        base = _narrow(base, overrides)
    if base.process_backend == "platform-sandbox" and not host_qualifies:
        raise SandboxUnavailable(
            f"profile {profile_id!r} requires a qualified platform-sandbox backend; "
            "the host did not qualify and there is no silent fallback"
        )
    return EffectiveExecutionProfile(requested=base, host_facts=dict(host_facts or {}))


def _narrow(base: ExecutionProfile, overrides: Mapping[str, Any]) -> ExecutionProfile:
    """Apply a one-shot override. Overrides may only narrow, never widen, access."""
    if overrides.get("workspace_access") == "workspace-write" and base.workspace_access == "read-only":
        raise ExecutionProfileError("an override cannot widen workspace access")
    if overrides.get("process_backend") == "host" and base.process_backend == "platform-sandbox":
        raise ExecutionProfileError("an override cannot widen process backend containment")
    allowed = {"workspace_access", "approval_default"}
    unknown = set(overrides) - allowed
    if unknown:
        raise ExecutionProfileError(f"override fields not permitted: {sorted(unknown)}")
    fields = {f: getattr(base, f) for f in base.__dataclass_fields__}
    fields.update(overrides)
    return ExecutionProfile(**fields)
