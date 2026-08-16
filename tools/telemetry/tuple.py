"""Instrument tuple and comparability rule M-18.

Owning contract: VG-07 §5.6, §5.8, REQ-BENCH-001.

Every benchmark result carries an instrument tuple partitioned into four explicit algebraic subsets:
Tuple = < K_compat, D_treatment, S_strat, M_meta >

- K_compat: strictly equal (K_A == K_B) across compared arms.
- D_treatment: declared experimental axis under test.
- S_strat: controlled categorical dimensions.
- M_meta: observation metadata (excluded from equality check).

Rule M-18: Two results are comparable if and only if K_A == K_B and their tuples
differ in exactly the declared treatment dimensions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from vanguard.packages.domain.canonicalisation.digest import digest_of


@dataclass(frozen=True)
class CompatibilityKey:
    """K_compat: Immutable experimental substrate configuration."""

    benchmark_id: str
    split_hash: str
    model_fingerprint: str
    requested_model: str = ""
    resolved_model: str = ""
    pricing_source: str = ""
    pricing_as_of: str = ""
    sampling_params: Mapping[str, Any] = field(default_factory=dict)
    harness_commit: str = "v0.5.0"
    agent_hash: str = "default_agent"
    evaluator_image_digest: str = "sha256:evaluator_default"
    containment_digest: str = "sha256:containment_default"
    substrate_profile: str = "linux_x86_64"
    runner_version: str = "1.0.0"
    schema_version: str = "vg.4"

    def to_dict(self) -> dict[str, Any]:
        return {
            "benchmarkId": self.benchmark_id,
            "splitHash": self.split_hash,
            "modelFingerprint": self.model_fingerprint,
            "requestedModel": self.requested_model,
            "resolvedModel": self.resolved_model,
            "pricingSource": self.pricing_source,
            "pricingAsOf": self.pricing_as_of,
            "samplingParams": dict(sorted(self.sampling_params.items())),
            "harnessCommit": self.harness_commit,
            "agentHash": self.agent_hash,
            "evaluatorImageDigest": self.evaluator_image_digest,
            "containmentDigest": self.containment_digest,
            "substrateProfile": self.substrate_profile,
            "runnerVersion": self.runner_version,
            "schemaVersion": self.schema_version,
        }

    def digest(self) -> str:
        return digest_of(self.to_dict())

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CompatibilityKey):
            return False
        return self.digest() == other.digest()


@dataclass(frozen=True)
class TreatmentDimensions:
    """D_treatment: Declared experimental axes under test."""

    manifest: str
    cache_enabled: bool = True
    custom_axes: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = {
            "manifest": self.manifest,
            "cacheEnabled": self.cache_enabled,
        }
        if self.custom_axes:
            data["customAxes"] = dict(sorted(self.custom_axes.items()))
        return data

    def digest(self) -> str:
        return digest_of(self.to_dict())


@dataclass(frozen=True)
class StratificationFields:
    """S_strat: Controlled categorical dimensions (task tier, language)."""

    difficulty: str = "standard"
    language: str = "python"
    custom_fields: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = {
            "difficulty": self.difficulty,
            "language": self.language,
        }
        if self.custom_fields:
            data["customFields"] = dict(sorted(self.custom_fields.items()))
        return data


@dataclass(frozen=True)
class ObservationMetadata:
    """M_meta: Physical execution metadata excluded from strict comparability checks."""

    timestamp: str
    run_id: str
    data_source: str = "live"
    failure_count: int = 0
    node_id: str = "local"
    operator: str = "automated"

    def validate_provenance(self) -> None:
        if self.data_source not in {"live", "cassette", "synthetic"}:
            raise ValueError(f"invalid data_source: {self.data_source!r}; must be live, cassette, or synthetic")

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "runId": self.run_id,
            "dataSource": self.data_source,
            "failureCount": self.failure_count,
            "nodeId": self.node_id,
            "operator": self.operator,
        }


@dataclass(frozen=True)
class InstrumentTuple:
    """The complete 4-part instrument tuple of VG-07 §5.6."""

    compat_key: CompatibilityKey
    treatment: TreatmentDimensions
    stratification: StratificationFields
    meta: ObservationMetadata

    def to_dict(self) -> dict[str, Any]:
        return {
            "compatKey": self.compat_key.to_dict(),
            "treatment": self.treatment.to_dict(),
            "stratification": self.stratification.to_dict(),
            "meta": self.meta.to_dict(),
        }

    def validate_provenance(self) -> None:
        self.meta.validate_provenance()

    def is_comparable_with(self, other: InstrumentTuple) -> tuple[bool, str]:
        """Check the M-18 comparability rule against another run tuple.
        
        Returns:
            (True, "") if comparable.
            (False, reason_string) if comparison is rejected.
        """
        if not isinstance(other, InstrumentTuple):
            return False, "Other object is not an InstrumentTuple"

        if self.compat_key != other.compat_key:
            # Determine specific mismatch
            my_dict = self.compat_key.to_dict()
            other_dict = other.compat_key.to_dict()
            diffs = [k for k in my_dict if my_dict[k] != other_dict.get(k)]
            return False, f"Compatibility key mismatch (M-18 violation) on fields: {', '.join(diffs)}"

        if self.stratification.to_dict() != other.stratification.to_dict():
            return False, "Stratification fields mismatch across compared arms"

        if self.treatment == other.treatment:
            return False, "Treatment dimensions are identical (A/A comparison; no lift to compute)"

        return True, ""
