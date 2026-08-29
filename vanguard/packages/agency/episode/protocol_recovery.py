"""Protocol recovery state machine and retry policies for model responses."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Literal, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of
from ...domain.transforms.contracts import ProposalDecoderProtocol
from .state import Proposal, ProposalKind, ProposalMalformed, parse_proposal

RecoveryStatus = Literal["accept", "retry_model", "fail_instrument"]


@dataclass(frozen=True, slots=True)
class RecoveryDecision:
    """The outcome of evaluating a raw model response through protocol recovery."""

    status: RecoveryStatus
    proposal: Proposal | None = None
    retry_reason: str | None = None
    retry_feedback: Mapping[str, Any] = field(default_factory=dict)
    continuation: bool = False
    failure_code: str | None = None
    diagnostics: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ProtocolRecoveryState:
    """Tracks separate retry counters across distinct failure dimensions."""

    transport_retries: int = 0
    protocol_retries: int = 0
    truncation_retries: int = 0
    effect_retries: int = 0
    max_transport_retries: int = 2
    max_protocol_retries: int = 2
    max_truncation_retries: int = 1
    max_effect_retries: int = 2

    def with_protocol_retry(self) -> ProtocolRecoveryState:
        return replace(self, protocol_retries=self.protocol_retries + 1)

    def with_truncation_retry(self) -> ProtocolRecoveryState:
        return replace(self, truncation_retries=self.truncation_retries + 1)

    def with_transport_retry(self) -> ProtocolRecoveryState:
        return replace(self, transport_retries=self.transport_retries + 1)

    def with_effect_retry(self) -> ProtocolRecoveryState:
        return replace(self, effect_retries=self.effect_retries + 1)


def recover_proposal(
    raw_value: Any,
    state: ProtocolRecoveryState,
    *,
    allowed_tools: Sequence[str] | None = None,
    decoders: Sequence[ProposalDecoderProtocol] = (),
    patch_detector: Any | None = None,
    truncation_detector: Any | None = None,
) -> tuple[RecoveryDecision, ProtocolRecoveryState]:
    """Pass raw model payload through the injected recovery pipeline before declaring instrument error."""
    # 1. Direct parse check
    if isinstance(raw_value, Mapping):
        try:
            prop = parse_proposal(raw_value)
            if prop.kind == ProposalKind.EFFECT and allowed_tools and prop.action not in allowed_tools:
                if state.protocol_retries < state.max_protocol_retries:
                    return (
                        RecoveryDecision(
                            status="retry_model",
                            retry_reason="DISALLOWED_TOOL",
                            retry_feedback={"allowed_tools": list(allowed_tools), "requested": prop.action},
                        ),
                        state.with_protocol_retry(),
                    )
            return RecoveryDecision(status="accept", proposal=prop), state
        except ProposalMalformed:
            pass

    # 2. Check injected decoders (e.g. native tool call decoder, DSML decoder)
    for decoder in decoders:
        try:
            decoded = decoder.decode(raw_value)
            if decoded is not None:
                prop = parse_proposal(decoded)
                if prop.kind == ProposalKind.EFFECT and allowed_tools and prop.action not in allowed_tools:
                    if state.protocol_retries < state.max_protocol_retries:
                        return (
                            RecoveryDecision(
                                status="retry_model",
                                retry_reason="DISALLOWED_TOOL",
                                retry_feedback={"allowed_tools": list(allowed_tools), "requested": prop.action},
                            ),
                            state.with_protocol_retry(),
                        )
                return RecoveryDecision(status="accept", proposal=prop), state
        except Exception:
            continue

    # 3. Check for truncation if detector injected
    if truncation_detector is not None:
        try:
            if truncation_detector(raw_value) and state.truncation_retries < state.max_truncation_retries:
                return (
                    RecoveryDecision(
                        status="retry_model",
                        retry_reason="OUTPUT_TRUNCATED",
                        continuation=True,
                        retry_feedback={"continuation": True, "reason": "Response was truncated; continue generation"},
                    ),
                    state.with_truncation_retry(),
                )
        except Exception:
            pass

    # 4. Check for Markdown patch candidate if detector injected (Invariant I3: never execute directly)
    text_content = ""
    if isinstance(raw_value, str):
        text_content = raw_value
    elif isinstance(raw_value, Mapping):
        text_content = str(raw_value.get("content") or raw_value.get("text") or "")

    if text_content and patch_detector is not None:
        try:
            detection = patch_detector(text_content)
            if getattr(detection, "has_patch", False) and state.protocol_retries < state.max_protocol_retries:
                return (
                    RecoveryDecision(
                        status="retry_model",
                        retry_reason="PATCH_EMITTED_AS_TEXT",
                        retry_feedback={
                            "required_tool": "patch.apply",
                            "candidate_digest": getattr(detection, "candidate_digest", ""),
                            "target_file": getattr(detection, "target_file", ""),
                        },
                    ),
                    state.with_protocol_retry(),
                )
        except Exception:
            pass

    # Unrecoverable
    return (
        RecoveryDecision(
            status="fail_instrument",
            failure_code="PROPOSAL_MALFORMED_UNRECOVERABLE",
        ),
        state,
    )
