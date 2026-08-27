"""Cross-lane artifact and provenance fixtures for M-4 and M-5a (B-M4-01).

These fixtures define the frozen data structures and helper builders used across the
Dev A (Runtime capture/wiring) and Dev B (scientific contracts/verification) boundaries:
- Artifact index entries (prompt, model_output, context_bundle, compaction_input/output, snapshot, patch, report)
- Context-selection provenance records
- Compaction provenance records
- Cache provenance records
- Exact model-input and model-output references
- Complete capture state
- Degradation state (capture_incomplete)
- Conforming mhf.trajectory/2 fixture builder

Freeze on publication. Any subsequent semantic fixture change requires Tech Lead escalation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from vanguard.packages.domain.canonicalisation.digest import digest_of

__all__ = [
    "ARTIFACT_ROLES",
    "ArtifactIndexEntry",
    "ContextSelectionProvenance",
    "CompactionProvenance",
    "CacheProvenance",
    "ModelInputRef",
    "ModelOutputRef",
    "CaptureState",
    "sample_artifact_index_entry",
    "sample_context_selection_provenance",
    "sample_compaction_provenance",
    "sample_cache_provenance",
    "sample_model_input_ref",
    "sample_model_output_ref",
    "sample_complete_capture_state",
    "sample_capture_incomplete_state",
    "sample_conforming_trajectory_v1",
    "sample_conforming_trajectory_v2",
    "build_trajectory_v2_fixture",
]

ARTIFACT_ROLES = frozenset({
    "prompt",
    "model_output",
    "context_bundle",
    "compaction_input",
    "compaction_output",
    "workspace_snapshot",
    "patch",
    "verification_report",
    "checkpoint_state",
})


@dataclass(frozen=True, slots=True)
class ArtifactIndexEntry:
    """One entry in the trajectory artifact index."""

    artifact_id: str
    digest: str
    role: str
    schema_id: str
    size_bytes: int
    retention_class: str
    stored: bool
    produced_by: Mapping[str, str] = field(default_factory=dict)
    refs: Mapping[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifactId": self.artifact_id,
            "digest": self.digest,
            "role": self.role,
            "schemaId": self.schema_id,
            "sizeBytes": self.size_bytes,
            "retentionClass": self.retention_class,
            "stored": self.stored,
            "producedBy": dict(self.produced_by),
            "refs": dict(self.refs),
        }


@dataclass(frozen=True, slots=True)
class ContextSelectionProvenance:
    """Context selection claim provenance."""

    policy_id: str
    policy_version: str
    params_digest: str
    input_digest: str
    output_digest: str
    token_count: int
    layer_counts: Mapping[str, int]
    turn_index: int
    selected_labels: tuple[str, ...] = ()
    dropped_labels: tuple[str, ...] = ()
    elided_labels: tuple[str, ...] = ()
    input_artifacts: tuple[str, ...] = ()
    output_artifacts: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "claimKind": "context_selection",
            "policy": {
                "id": self.policy_id,
                "version": self.policy_version,
                "paramsDigest": self.params_digest,
            },
            "inputDigest": self.input_digest,
            "outputDigest": self.output_digest,
            "metrics": {
                "tokenCount": self.token_count,
                "layerCounts": dict(self.layer_counts),
            },
            "turnIndex": self.turn_index,
            "selectedLabels": list(self.selected_labels),
            "droppedLabels": list(self.dropped_labels),
            "elidedLabels": list(self.elided_labels),
            "inputArtifacts": list(self.input_artifacts),
            "outputArtifacts": list(self.output_artifacts),
        }


@dataclass(frozen=True, slots=True)
class CompactionProvenance:
    """Context compaction claim provenance."""

    strategy: str
    params_digest: str
    input_digest: str
    output_digest: str
    tokens_before: int
    tokens_after: int
    removed_tokens: int
    turn_index: int
    input_artifacts: tuple[str, ...] = ()
    output_artifacts: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "claimKind": "compaction",
            "policy": {
                "id": f"compaction:{self.strategy}",
                "version": "1.0.0",
                "paramsDigest": self.params_digest,
            },
            "inputDigest": self.input_digest,
            "outputDigest": self.output_digest,
            "metrics": {
                "tokensBefore": self.tokens_before,
                "tokensAfter": self.tokens_after,
                "removedTokens": self.removed_tokens,
            },
            "turnIndex": self.turn_index,
            "inputArtifacts": list(self.input_artifacts),
            "outputArtifacts": list(self.output_artifacts),
        }


@dataclass(frozen=True, slots=True)
class CacheProvenance:
    """Model / cassette cache interaction provenance."""

    cache_id: str
    key_digest: str
    source_artifact_digest: str
    hit: bool
    source_status: str
    turn_index: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "claimKind": "cache_interaction",
            "cacheId": self.cache_id,
            "keyDigest": self.key_digest,
            "sourceDigest": self.source_artifact_digest,
            "hit": self.hit,
            "sourceStatus": self.source_status,
            "turnIndex": self.turn_index,
        }


@dataclass(frozen=True, slots=True)
class ModelInputRef:
    """Exact model input reference captured immediately before invocation."""

    digest: str
    role: str = "prompt"
    schema_id: str = "mhf.prompt/1"
    capture_policy_id: str = "capture-standard@1"
    captured_at: str = "2026-08-25T12:00:00.000Z"

    def to_dict(self) -> dict[str, Any]:
        return {
            "digest": self.digest,
            "role": self.role,
            "schemaId": self.schema_id,
            "capturePolicyId": self.capture_policy_id,
            "capturedAt": self.captured_at,
        }


@dataclass(frozen=True, slots=True)
class ModelOutputRef:
    """Exact model output reference captured immediately after invocation."""

    digest: str
    role: str = "model_output"
    schema_id: str = "mhf.model-output/1"
    capture_policy_id: str = "capture-standard@1"
    captured_at: str = "2026-08-25T12:00:01.000Z"

    def to_dict(self) -> dict[str, Any]:
        return {
            "digest": self.digest,
            "role": self.role,
            "schemaId": self.schema_id,
            "capturePolicyId": self.capture_policy_id,
            "capturedAt": self.captured_at,
        }


@dataclass(frozen=True, slots=True)
class CaptureState:
    """Capture execution status and policy."""

    status: str  # "complete" | "incomplete"
    required: bool
    policy_id: str
    policy_version: str
    degradation_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "required": self.required,
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            **({"degradation_reason": self.degradation_reason} if self.degradation_reason else {}),
        }


def sample_artifact_index_entry(
    *,
    artifact_id: str = "art-001",
    role: str = "prompt",
    digest: str | None = None,
    size_bytes: int = 1024,
    retention_class: str = "standard",
    stored: bool = True,
) -> ArtifactIndexEntry:
    effective_digest = digest or digest_of({"role": role, "id": artifact_id})
    return ArtifactIndexEntry(
        artifact_id=artifact_id,
        digest=effective_digest,
        role=role,
        schema_id=f"mhf.{role}/1" if role in ("prompt", "model_output") else "text/plain;v=1",
        size_bytes=size_bytes,
        retention_class=retention_class,
        stored=stored,
        produced_by={"component": "context_compiler", "policy_id": "std-context", "policy_version": "1.0.0"},
        refs={"turn": "0"},
    )


def sample_context_selection_provenance(
    *,
    turn_index: int = 0,
    policy_id: str = "prefix-budget-fit",
    token_count: int = 250,
) -> ContextSelectionProvenance:
    return ContextSelectionProvenance(
        policy_id=policy_id,
        policy_version="1.0.0",
        params_digest=digest_of({"policy": policy_id, "budget_tokens": 4096}),
        input_digest=digest_of({"candidate_spans": ["span-1", "span-2"]}),
        output_digest=digest_of({"selected_spans": ["span-1"]}),
        token_count=token_count,
        layer_counts={"L1": 50, "L2": 100, "L3": 100},
        turn_index=turn_index,
        selected_labels=("system_prompt", "task_description"),
        dropped_labels=("stale_observation",),
        elided_labels=(),
        input_artifacts=(digest_of({"raw": "candidates"}),),
        output_artifacts=(digest_of({"raw": "selected"}),),
    )


def sample_compaction_provenance(
    *,
    turn_index: int = 1,
    strategy: str = "truncate_head",
    removed_tokens: int = 500,
) -> CompactionProvenance:
    return CompactionProvenance(
        strategy=strategy,
        params_digest=digest_of({"strategy": strategy, "target_reduction": 0.3}),
        input_digest=digest_of({"before_compaction": "large_bundle"}),
        output_digest=digest_of({"after_compaction": "compacted_bundle"}),
        tokens_before=2000,
        tokens_after=1500,
        removed_tokens=removed_tokens,
        turn_index=turn_index,
        input_artifacts=(digest_of({"blob": "before"}),),
        output_artifacts=(digest_of({"blob": "after"}),),
    )


def sample_cache_provenance(
    *,
    turn_index: int = 0,
    hit: bool = True,
) -> CacheProvenance:
    return CacheProvenance(
        cache_id="cassette-vanguard-01",
        key_digest=digest_of({"prompt_key": "turn-0"}),
        source_artifact_digest=digest_of({"cached_response": "completion-0"}),
        hit=hit,
        source_status="verified_hit" if hit else "miss",
        turn_index=turn_index,
    )


def sample_model_input_ref(*, digest: str | None = None) -> ModelInputRef:
    return ModelInputRef(digest=digest or digest_of({"prompt": "Solve the bug"}))


def sample_model_output_ref(*, digest: str | None = None) -> ModelOutputRef:
    return ModelOutputRef(digest=digest or digest_of({"output": "Patch created"}))


def sample_complete_capture_state() -> CaptureState:
    return CaptureState(
        status="complete",
        required=True,
        policy_id="capture-standard@1",
        policy_version="1.0.0",
        degradation_reason=None,
    )


def sample_capture_incomplete_state(*, reason: str = "optional_blob_write_failed") -> CaptureState:
    return CaptureState(
        status="incomplete",
        required=False,
        policy_id="capture-standard@1",
        policy_version="1.0.0",
        degradation_reason=reason,
    )


def sample_conforming_trajectory_v1(
    *,
    run_id: str = "run-hist-001",
    harness_digest: str = "sha256:0000000000000000000000000000000000000000000000000000000000000001",
) -> dict[str, Any]:
    """Return a strictly conforming historical mhf.trajectory/1 dictionary."""
    return {
        "schema": "mhf.trajectory/1",
        "project_id": "project-hist",
        "run_id": run_id,
        "episode_id": f"ep-{run_id}",
        "principal_id": "agent-hist",
        "harness_digest": harness_digest,
        "execution_digest": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
        "state_digest": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
        "event_range": {"first_seq": 0, "last_seq": 5, "count": 6},
        "model_routes_used": [{
            "tier": 1,
            "provider": "openrouter",
            "model": "deepseek/deepseek-v4-flash-0731",
            "model_fingerprint": "fp_deepseekv4flash",
            "fingerprint_unavailable_reason": None,
        }],
        "turns": [{
            "turn": 0,
            "context_digest": "sha256:3333333333333333333333333333333333333333333333333333333333333333",
            "context_ref": None,
            "proposal": {"thought": "Read file", "requests": [{"verb": "fs.read", "args": {"path": "src/app.py"}}]},
            "receipts": [{
                "request_digest": "sha256:4444444444444444444444444444444444444444444444444444444444444444",
                "outcome": "completed",
                "grant_digest": None,
                "lease_id": None,
                "stdout_ref": None,
                "artifact_refs": [],
            }],
            "model_route": {
                "tier": 1,
                "provider": "openrouter",
                "model": "deepseek/deepseek-v4-flash-0731",
                "model_fingerprint": "fp_deepseekv4flash",
                "fingerprint_unavailable_reason": None,
            },
            "invocations": [],
            "cost": {
                "usd_micros": 500,
                "tokens": 150,
                "bytes": 2048,
                "millis": 120,
                "measurement_status": {
                    "usd_micros": {"status": "measured", "reason": None},
                    "tokens": {"status": "measured", "reason": None},
                    "bytes": {"status": "measured", "reason": None},
                    "millis": {"status": "measured", "reason": None},
                },
            },
        }],
        "verdict": None,
        "verdict_absence_reason": "product_run_no_evaluator",
        "cost": {
            "usd_micros": 500,
            "tokens": 150,
            "bytes": 2048,
            "millis": 120,
            "measurement_status": {
                "usd_micros": {"status": "measured", "reason": None},
                "tokens": {"status": "measured", "reason": None},
                "bytes": {"status": "measured", "reason": None},
                "millis": {"status": "measured", "reason": None},
            },
        },
        "outcome": "completed",
    }


def build_trajectory_v2_fixture(
    *,
    run_id: str = "run-v2-001",
    harness_digest: str = "sha256:0000000000000000000000000000000000000000000000000000000000000002",
    artifacts: Sequence[ArtifactIndexEntry] | None = None,
    context_prov: Sequence[ContextSelectionProvenance] | None = None,
    compaction_prov: Sequence[CompactionProvenance] | None = None,
    cache_prov: Sequence[CacheProvenance] | None = None,
    capture_state: CaptureState | None = None,
    reproducibility: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a complete, conforming mhf.trajectory/2 dictionary."""
    arts = list(artifacts or [
        sample_artifact_index_entry(artifact_id="art-p0", role="prompt"),
        sample_artifact_index_entry(artifact_id="art-m0", role="model_output"),
    ])
    ctx_list = list(context_prov or [sample_context_selection_provenance(turn_index=0)])
    cmp_list = list(compaction_prov or [])
    cch_list = list(cache_prov or [])
    cap = capture_state or sample_complete_capture_state()

    repro = reproducibility or {
        "values": {
            "state_reconstruction": {"capability": "full_cold", "verification": "unverified"},
            "semantic_replay": {"capability": "pinned", "verification": "unverified"},
            "external_reexecution": "available",
            "artifact_retention": "partial",
            "environment_capture": "declared",
            "provider_model_identity": "attributed",
        },
        "assessed_at": "2026-08-25T12:00:00.000Z",
        "basis": ["wal_durable", "pins_complete", "live_attributable_provider", "profile_standard"],
        "reducer_version": "v1.0.0",
        "schema_versions": {
            "mhf.trajectory": "2",
            "mhf.execution-profile": "2",
            "mhf.event": "1",
        },
    }

    return {
        "schema": "mhf.trajectory/2",
        "project_id": "project-v2",
        "run_id": run_id,
        "episode_id": f"ep-{run_id}",
        "parent_episode_id": None,
        "principal_id": "agent-v2",
        "harness_digest": harness_digest,
        "execution_digest": "sha256:1111111111111111111111111111111111111111111111111111111111111112",
        "run_digest": "sha256:run0000000000000000000000000000000000000000000000000000000000002",
        "activation_digest": "sha256:act0000000000000000000000000000000000000000000000000000000000002",
        "task_digest": "sha256:task000000000000000000000000000000000000000000000000000000000002",
        "preregistration_digest": None,
        "state_digest": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
        "event_range": {"first_seq": 0, "last_seq": 8, "count": 9},
        "model_routes_used": [{
            "tier": 1,
            "provider": "openrouter",
            "model": "deepseek/deepseek-v4-flash-0731",
            "model_fingerprint": "fp_deepseekv4flash",
            "fingerprint_unavailable_reason": None,
        }],
        "turns": [{
            "turn": 0,
            "context_digest": "sha256:3333333333333333333333333333333333333333333333333333333333333333",
            "context_ref": "sha256:ctxref0000000000000000000000000000000000000000000000000000000001",
            "proposal": {"thought": "Read code", "requests": [{"verb": "fs.read", "args": {"path": "src/app.py"}}]},
            "receipts": [{
                "request_digest": "sha256:4444444444444444444444444444444444444444444444444444444444444444",
                "outcome": "completed",
                "grant_digest": None,
                "lease_id": None,
                "stdout_ref": None,
                "artifact_refs": [],
            }],
            "model_route": {
                "tier": 1,
                "provider": "openrouter",
                "model": "deepseek/deepseek-v4-flash-0731",
                "model_fingerprint": "fp_deepseekv4flash",
                "fingerprint_unavailable_reason": None,
            },
            "invocations": [{
                "tier": 1,
                "route": {
                    "provider": "openrouter",
                    "model": "deepseek/deepseek-v4-flash-0731",
                    "model_fingerprint": "fp_deepseekv4flash",
                    "fingerprint_unavailable_reason": None,
                },
                "usage": {"prompt_tokens": 100, "completion_tokens": 50},
                "cost": {
                    "usd_micros": 500,
                    "tokens": 150,
                    "bytes": 2048,
                    "millis": 120,
                    "measurement_status": {
                        "usd_micros": {"status": "measured", "reason": None},
                        "tokens": {"status": "measured", "reason": None},
                        "bytes": {"status": "measured", "reason": None},
                        "millis": {"status": "measured", "reason": None},
                    },
                },
            }],
            "cost": {
                "usd_micros": 500,
                "tokens": 150,
                "bytes": 2048,
                "millis": 120,
                "measurement_status": {
                    "usd_micros": {"status": "measured", "reason": None},
                    "tokens": {"status": "measured", "reason": None},
                    "bytes": {"status": "measured", "reason": None},
                    "millis": {"status": "measured", "reason": None},
                },
            },
            "model_input_ref": "sha256:prompt0000000000000000000000000000000000000000000000000000000001",
            "model_output_ref": "sha256:output0000000000000000000000000000000000000000000000000000000001",
        }],
        "verdict": None,
        "verdict_absence_reason": "product_run_no_evaluator",
        "cost": {
            "usd_micros": 500,
            "tokens": 150,
            "bytes": 2048,
            "millis": 120,
            "measurement_status": {
                "usd_micros": {"status": "measured", "reason": None},
                "tokens": {"status": "measured", "reason": None},
                "bytes": {"status": "measured", "reason": None},
                "millis": {"status": "measured", "reason": None},
            },
        },
        "outcome": "completed",
        "artifacts": [a.to_dict() if hasattr(a, "to_dict") else dict(a) for a in arts],
        "provenance": {
            "context": [c.to_dict() if hasattr(c, "to_dict") else dict(c) for c in ctx_list],
            "compaction": [c.to_dict() if hasattr(c, "to_dict") else dict(c) for c in cmp_list],
            "cache": [c.to_dict() if hasattr(c, "to_dict") else dict(c) for c in cch_list],
        },
        "reproducibility_at_run_close": dict(repro),
        "capture": cap.to_dict() if hasattr(cap, "to_dict") else dict(cap),
    }


def sample_conforming_trajectory_v2(**kwargs: Any) -> dict[str, Any]:
    """Alias for build_trajectory_v2_fixture for sample usage."""
    return build_trajectory_v2_fixture(**kwargs)
