"""Proof-honest reproducibility assessment and vector derivation (`ADR-0096 §8, §14.4`, `ADR-0097 §1`, `EVIDENCE.md`).

Reproducibility in AETHER is a computed, multidimensional, time-aware vector separating
capability from executed verification.

Rules:
1. WAL presence establishes state reconstruction capability (full_cold), but leaves verification unverified.
2. Pin presence establishes semantic replay capability (pinned), but leaves verification unverified.
3. `verified` requires an immutable executed receipt bound to:
   - the run identity;
   - input history or checkpoint digest;
   - reducer/schema pins;
   - reconstructed output/state digest.
4. `reproducibility_at_run_close` is immutable historical evidence.
5. Later assessment produces a new `reproducibility_current` claim and never overwrites run-close evidence.
6. The executing episode cannot self-certify its reproducibility.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ..domain.ledger.reducer import REDUCER_VERSION

__all__ = [
    "REPRO_DOMAINS",
    "StateReconstructionAssessment",
    "SemanticReplayAssessment",
    "ReproducibilityVector",
    "assess_reproducibility",
    "reassess_current_reproducibility",
    "verify_reconstruction_receipt",
    "verify_replay_receipt",
]

REPRO_DOMAINS: Mapping[str, tuple[str, ...]] = {
    "state_reconstruction_capability": ("none", "from_checkpoint", "full_cold"),
    "state_reconstruction_verification": ("unverified", "verified"),
    "semantic_replay_capability": ("unpinned", "pinned"),
    "semantic_replay_verification": ("unverified", "verified"),
    "external_reexecution": ("unavailable", "degraded", "available"),
    "artifact_retention": ("digests_only", "partial", "full"),
    "environment_capture": ("none", "declared", "snapshot"),
    "provider_model_identity": ("unattributed", "attributed", "attested"),
}


@dataclass(frozen=True, slots=True)
class StateReconstructionAssessment:
    """Assessment of state reconstruction capability and executed verification."""

    capability: str  # "none" | "from_checkpoint" | "full_cold"
    verification: str  # "unverified" | "verified"
    receipt: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.capability not in REPRO_DOMAINS["state_reconstruction_capability"]:
            raise ValueError(f"invalid state reconstruction capability {self.capability!r}")
        if self.verification not in REPRO_DOMAINS["state_reconstruction_verification"]:
            raise ValueError(f"invalid state reconstruction verification {self.verification!r}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability": self.capability,
            "verification": self.verification,
            **({"receipt": dict(self.receipt)} if self.receipt else {}),
        }


@dataclass(frozen=True, slots=True)
class SemanticReplayAssessment:
    """Assessment of semantic replay capability and executed verification."""

    capability: str  # "unpinned" | "pinned"
    verification: str  # "unverified" | "verified"
    receipt: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.capability not in REPRO_DOMAINS["semantic_replay_capability"]:
            raise ValueError(f"invalid semantic replay capability {self.capability!r}")
        if self.verification not in REPRO_DOMAINS["semantic_replay_verification"]:
            raise ValueError(f"invalid semantic replay verification {self.verification!r}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability": self.capability,
            "verification": self.verification,
            **({"receipt": dict(self.receipt)} if self.receipt else {}),
        }


@dataclass(frozen=True, slots=True)
class ReproducibilityVector:
    """Multidimensional proof-honest reproducibility vector."""

    state_reconstruction: StateReconstructionAssessment
    semantic_replay: SemanticReplayAssessment
    external_reexecution: str
    artifact_retention: str
    environment_capture: str
    provider_model_identity: str
    assessed_at: str
    basis: tuple[str, ...]
    reducer_version: str
    schema_versions: Mapping[str, str]
    state_reconstruction_receipt: Mapping[str, Any] | None = None
    semantic_replay_receipt: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.external_reexecution not in REPRO_DOMAINS["external_reexecution"]:
            raise ValueError(f"invalid external_reexecution {self.external_reexecution!r}")
        if self.artifact_retention not in REPRO_DOMAINS["artifact_retention"]:
            raise ValueError(f"invalid artifact_retention {self.artifact_retention!r}")
        if self.environment_capture not in REPRO_DOMAINS["environment_capture"]:
            raise ValueError(f"invalid environment_capture {self.environment_capture!r}")
        if self.provider_model_identity not in REPRO_DOMAINS["provider_model_identity"]:
            raise ValueError(f"invalid provider_model_identity {self.provider_model_identity!r}")

    def to_dict(self) -> dict[str, Any]:
        res: dict[str, Any] = {
            "values": {
                "state_reconstruction": {
                    "capability": self.state_reconstruction.capability,
                    "verification": self.state_reconstruction.verification,
                },
                "semantic_replay": {
                    "capability": self.semantic_replay.capability,
                    "verification": self.semantic_replay.verification,
                },
                "external_reexecution": self.external_reexecution,
                "artifact_retention": self.artifact_retention,
                "environment_capture": self.environment_capture,
                "provider_model_identity": self.provider_model_identity,
            },
            "assessed_at": self.assessed_at,
            "basis": list(self.basis),
            "reducer_version": self.reducer_version,
            "schema_versions": dict(self.schema_versions),
        }
        if self.state_reconstruction_receipt:
            res["state_reconstruction_receipt"] = dict(self.state_reconstruction_receipt)
        if self.semantic_replay_receipt:
            res["semantic_replay_receipt"] = dict(self.semantic_replay_receipt)
        return res

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ReproducibilityVector:
        vals = data.get("values", {})
        sr_val = vals.get("state_reconstruction", {})
        sr_rec = data.get("state_reconstruction_receipt") or sr_val.get("receipt")
        sr = StateReconstructionAssessment(
            capability=sr_val.get("capability", "none"),
            verification=sr_val.get("verification", "unverified"),
            receipt=sr_rec,
        )

        rp_val = vals.get("semantic_replay", {})
        rp_rec = data.get("semantic_replay_receipt") or rp_val.get("receipt")
        rp = SemanticReplayAssessment(
            capability=rp_val.get("capability", "unpinned"),
            verification=rp_val.get("verification", "unverified"),
            receipt=rp_rec,
        )

        return cls(
            state_reconstruction=sr,
            semantic_replay=rp,
            external_reexecution=vals.get("external_reexecution", "unavailable"),
            artifact_retention=vals.get("artifact_retention", "digests_only"),
            environment_capture=vals.get("environment_capture", "none"),
            provider_model_identity=vals.get("provider_model_identity", "unattributed"),
            assessed_at=data.get("assessed_at", ""),
            basis=tuple(data.get("basis", ())),
            reducer_version=data.get("reducer_version", ""),
            schema_versions=dict(data.get("schema_versions", {})),
            state_reconstruction_receipt=sr_rec,
            semantic_replay_receipt=rp_rec,
        )


def verify_reconstruction_receipt(
    receipt: Mapping[str, Any] | None,
    *,
    expected_run_id: str | None = None,
    expected_state_digest: str | None = None,
    expected_reducer_version: str | None = None,
) -> bool:
    """Verify an executed state reconstruction receipt."""
    if not receipt:
        return False
    if not receipt.get("verified", False) and not receipt.get("reconstructed", False):
        return False
    if expected_run_id and receipt.get("run_id") != expected_run_id:
        return False
    if expected_state_digest:
        reconstructed_digest = receipt.get("reconstructed_state_digest") or receipt.get("state_digest")
        if reconstructed_digest != expected_state_digest:
            return False
    if expected_reducer_version and receipt.get("reducer_version"):
        if receipt.get("reducer_version") != expected_reducer_version:
            return False
    return bool(receipt.get("input_history_digest") or receipt.get("checkpoint_digest") or receipt.get("event_count"))


def verify_replay_receipt(
    receipt: Mapping[str, Any] | None,
    *,
    expected_run_id: str | None = None,
    expected_output_digest: str | None = None,
    expected_pins: Mapping[str, str] | None = None,
) -> bool:
    """Verify an executed semantic replay receipt."""
    if not receipt:
        return False
    if not receipt.get("verified", False) and not receipt.get("replayed", False):
        return False
    if expected_run_id and receipt.get("run_id") != expected_run_id:
        return False
    if expected_output_digest:
        replayed_output = receipt.get("replayed_output_digest") or receipt.get("output_digest")
        if replayed_output != expected_output_digest:
            return False
    if expected_pins and receipt.get("pins"):
        for k, v in expected_pins.items():
            if receipt["pins"].get(k) != v:
                return False
    return True


def assess_reproducibility(
    *,
    profile: Any,
    model_route: Mapping[str, Any] | None = None,
    environment: Mapping[str, Any] | None = None,
    artifact_index: Sequence[Any] | None = None,
    pins: Mapping[str, str] | None = None,
    wal_durable: bool = True,
    state_reconstruction_receipt: Mapping[str, Any] | None = None,
    semantic_replay_receipt: Mapping[str, Any] | None = None,
    assessed_at: str | None = None,
    reducer_version: str = REDUCER_VERSION,
    schema_versions: Mapping[str, str] | None = None,
    state_digest: str | None = None,
    run_id: str | None = None,
) -> ReproducibilityVector:
    """Derive proof-honest reproducibility from observable execution facts.

    Pure function with zero ambient I/O.
    """
    basis: list[str] = []

    # 1. State reconstruction
    if wal_durable:
        sr_cap = "full_cold"
        basis.append("wal_durable:full_cold")
    else:
        sr_cap = "none"
        basis.append("wal_ephemeral:none")

    sr_verified = "unverified"
    valid_sr_rec = None
    if verify_reconstruction_receipt(
        state_reconstruction_receipt,
        expected_run_id=run_id,
        expected_state_digest=state_digest,
        expected_reducer_version=reducer_version,
    ):
        sr_verified = "verified"
        valid_sr_rec = state_reconstruction_receipt
        basis.append("state_reconstruction_receipt:verified")
    else:
        basis.append("state_reconstruction:unverified")

    sr_assessment = StateReconstructionAssessment(
        capability=sr_cap,
        verification=sr_verified,
        receipt=valid_sr_rec,
    )

    # 2. Semantic replay
    effective_pins = dict(pins or {})
    pins_complete = bool(effective_pins.get("reducer") and effective_pins.get("schemas"))
    if pins_complete:
        rp_cap = "pinned"
        basis.append("pins_complete:pinned")
    else:
        rp_cap = "unpinned"
        basis.append("pins_incomplete:unpinned")

    rp_verified = "unverified"
    valid_rp_rec = None
    if verify_replay_receipt(
        semantic_replay_receipt,
        expected_run_id=run_id,
        expected_pins=effective_pins,
    ):
        rp_verified = "verified"
        valid_rp_rec = semantic_replay_receipt
        basis.append("semantic_replay_receipt:verified")
    else:
        basis.append("semantic_replay:unverified")

    rp_assessment = SemanticReplayAssessment(
        capability=rp_cap,
        verification=rp_verified,
        receipt=valid_rp_rec,
    )

    # 3. External reexecution
    route = dict(model_route or {})
    provider = str(route.get("provider", "")).lower()
    if provider in ("fake", "mock"):
        external_reexec = "unavailable"
        basis.append(f"provider_{provider}:unavailable")
    elif provider in ("scripted", "cassette", "lam", "replay"):
        external_reexec = "degraded"
        basis.append(f"provider_{provider}:degraded")
    elif provider and route.get("model"):
        external_reexec = "available"
        basis.append(f"provider_{provider}:available")
    else:
        external_reexec = "unavailable"
        basis.append("provider_unknown:unavailable")

    # 4. Artifact retention
    retention_val = getattr(profile, "retention", None)
    if not retention_val and hasattr(profile, "requested"):
        retention_val = getattr(profile.requested, "retention", None)
    if not retention_val and isinstance(profile, Mapping):
        retention_val = profile.get("retention")
    retention_str = str(retention_val or "standard").replace("-", "_")

    if retention_str == "full":
        art_ret = "full"
    elif retention_str == "standard":
        art_ret = "partial"
    else:
        art_ret = "digests_only"
    basis.append(f"retention_{retention_str}:{art_ret}")

    # 5. Environment capture
    env = dict(environment or {})
    if env.get("snapshot_digest"):
        env_cap = "snapshot"
        basis.append("env_snapshot:snapshot")
    elif env.get("task") or env.get("project_id") or env.get("brief"):
        env_cap = "declared"
        basis.append("env_declared:declared")
    else:
        env_cap = "none"
        basis.append("env_none:none")

    # 6. Provider/model identity
    if route.get("attestation_signature"):
        prov_id = "attested"
        basis.append("model_attested:attested")
    elif route.get("provider") and route.get("model"):
        prov_id = "attributed"
        basis.append("model_attributed:attributed")
    else:
        prov_id = "unattributed"
        basis.append("model_unattributed:unattributed")

    timestamp = assessed_at or "1970-01-01T00:00:00.000Z"
    default_schemas = {
        "mhf.trajectory": "2",
        "mhf.execution-profile": "2",
        "mhf.event": "1",
    }
    schemas = dict(schema_versions or default_schemas)

    return ReproducibilityVector(
        state_reconstruction=sr_assessment,
        semantic_replay=rp_assessment,
        external_reexecution=external_reexec,
        artifact_retention=art_ret,
        environment_capture=env_cap,
        provider_model_identity=prov_id,
        assessed_at=timestamp,
        basis=tuple(basis),
        reducer_version=reducer_version,
        schema_versions=schemas,
        state_reconstruction_receipt=valid_sr_rec,
        semantic_replay_receipt=valid_rp_rec,
    )


def reassess_current_reproducibility(
    run_close: ReproducibilityVector,
    current_facts: Mapping[str, Any],
) -> ReproducibilityVector:
    """Compute a new reproducibility_current claim.

    The historical run_close vector is immutable and is never modified.
    """
    new_basis = list(run_close.basis)
    new_basis.append("reassessed_current")

    # Check if external provider availability changed
    ext_reexec = current_facts.get("external_reexecution", run_close.external_reexecution)
    if "provider_retired" in current_facts and current_facts["provider_retired"]:
        ext_reexec = "unavailable"
        new_basis.append("provider_retired:unavailable")

    # Check if a new state reconstruction verification was executed
    sr_receipt = current_facts.get("state_reconstruction_receipt", run_close.state_reconstruction_receipt)
    sr_cap = run_close.state_reconstruction.capability
    sr_ver = run_close.state_reconstruction.verification
    if verify_reconstruction_receipt(sr_receipt):
        sr_ver = "verified"
        new_basis.append("current_state_reconstruction_verified")

    sr = StateReconstructionAssessment(
        capability=sr_cap,
        verification=sr_ver,
        receipt=sr_receipt,
    )

    # Check if a new semantic replay verification was executed
    rp_receipt = current_facts.get("semantic_replay_receipt", run_close.semantic_replay_receipt)
    rp_cap = run_close.semantic_replay.capability
    rp_ver = run_close.semantic_replay.verification
    if verify_replay_receipt(rp_receipt):
        rp_ver = "verified"
        new_basis.append("current_semantic_replay_verified")

    rp = SemanticReplayAssessment(
        capability=rp_cap,
        verification=rp_ver,
        receipt=rp_receipt,
    )

    now_ts = current_facts.get("assessed_at") or "1970-01-01T00:00:00.000Z"

    return ReproducibilityVector(
        state_reconstruction=sr,
        semantic_replay=rp,
        external_reexecution=ext_reexec,
        artifact_retention=current_facts.get("artifact_retention", run_close.artifact_retention),
        environment_capture=current_facts.get("environment_capture", run_close.environment_capture),
        provider_model_identity=current_facts.get("provider_model_identity", run_close.provider_model_identity),
        assessed_at=now_ts,
        basis=tuple(new_basis),
        reducer_version=current_facts.get("reducer_version", run_close.reducer_version),
        schema_versions=current_facts.get("schema_versions", run_close.schema_versions),
        state_reconstruction_receipt=sr_receipt,
        semantic_replay_receipt=rp_receipt,
    )
