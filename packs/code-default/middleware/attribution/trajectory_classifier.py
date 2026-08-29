"""Deterministic failure attribution classifier (Invariant I10)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Mapping, Sequence

AttributionClass = Literal[
    "llm",
    "provider",
    "protocol",
    "harness",
    "framework",
    "dataset",
    "oracle",
    "mixed",
    "unknown",
]


@dataclass(frozen=True, slots=True)
class AttributionRecord:
    classification: AttributionClass
    confidence_ppm: int
    evidence_codes: tuple[str, ...] = field(default_factory=tuple)
    detail: str = ""


def classify_trajectory_failure(
    events: Sequence[Mapping[str, Any]],
    outcome: str,
    detail: str = "",
) -> AttributionRecord:
    """Classify the root origin of a run failure based on recorded event history."""
    evidence: list[str] = []

    # Check for dataset / preflight invalidity
    if "DATASET_INVALID" in detail or "dataset_invalid" in outcome:
        return AttributionRecord(
            classification="dataset",
            confidence_ppm=1_000_000,
            evidence_codes=("DATASET_BASELINE_INVALID",),
            detail="Baseline workspace failed preflight checks",
        )

    # Check for harness / permission denials
    if "command_disallowed" in detail or "verb_denied" in detail or "escapes" in detail:
        evidence.append("HARNESS_DENIAL")
        return AttributionRecord(
            classification="harness",
            confidence_ppm=950_000,
            evidence_codes=tuple(evidence),
            detail=f"Harness denied requested operation: {detail}",
        )

    # Check for provider transport errors (HTTP 429, 503, timeout, auth)
    if "HTTP 429" in detail or "rate_limit" in detail or "HTTP 50" in detail or "401" in detail:
        return AttributionRecord(
            classification="provider",
            confidence_ppm=990_000,
            evidence_codes=("PROVIDER_TRANSPORT_ERROR",),
            detail=detail,
        )

    # Check for protocol errors (truncation, malformed proposal, json parse error)
    if "OUTPUT_TRUNCATED" in detail or "PATCH_EMITTED_AS_TEXT" in detail or "PROPOSAL_MALFORMED" in detail:
        return AttributionRecord(
            classification="protocol",
            confidence_ppm=900_000,
            evidence_codes=("PROTOCOL_DEVIATION",),
            detail=detail,
        )

    # Check for oracle failures
    if outcome == "oracle_failed" or "ORACLE_FAILED" in detail:
        return AttributionRecord(
            classification="oracle",
            confidence_ppm=850_000,
            evidence_codes=("ORACLE_REJECTION",),
            detail="Task patch failed external oracle verification",
        )

    # Check for no-progress loops or logical LLM errors
    if "no progress" in detail or outcome == "no_progress":
        return AttributionRecord(
            classification="llm",
            confidence_ppm=800_000,
            evidence_codes=("NO_PROGRESS_LOOP",),
            detail="Model produced repeated identical transitions without progress",
        )

    # Invariant I10: Unknown must remain unknown, never defaulting to model failure
    return AttributionRecord(
        classification="unknown",
        confidence_ppm=500_000,
        evidence_codes=("ATTRIBUTION_INCONCLUSIVE",),
        detail=f"Inconclusive failure evidence: outcome={outcome}, detail={detail}",
    )
