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

    @property
    def action(self) -> str:
        return self.status

    @property
    def reason(self) -> str:
        return self.retry_reason or self.failure_code or "ok"

    @property
    def feedback_message(self) -> str | None:
        if isinstance(self.retry_feedback, Mapping):
            return self.retry_feedback.get("message")
        return None


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


RecoveryState = ProtocolRecoveryState


class ProtocolRecoveryPolicy:
    """Evaluates proposals against recovery rules and produces actionable feedback."""

    def __init__(self, max_protocol_retries: int = 2, max_truncation_retries: int = 1) -> None:
        self.max_protocol_retries = max_protocol_retries
        self.max_truncation_retries = max_truncation_retries

    def evaluate(
        self,
        proposal: Mapping[str, Any],
        state: ProtocolRecoveryState,
        *,
        patch_required: bool = False,
        allowed_tools: Sequence[str] = (),
    ) -> RecoveryDecision:
        text = str(proposal.get("text") or "")
        tool_calls = proposal.get("toolCalls") or ()
        finish_reason = proposal.get("finishReason") or proposal.get("finish_reason")

        # 1. Valid proposal with tool calls -> Accept immediately
        if tool_calls:
            return RecoveryDecision(status="accept", retry_reason="valid_tool_calls")

        # 2. Truncation recovery
        if finish_reason in {"length", "max_tokens"} and state.truncation_retries < self.max_truncation_retries:
            return RecoveryDecision(
                status="retry_model",
                retry_reason="OUTPUT_TRUNCATED",
                retry_feedback={"continuation": True, "reason": "OUTPUT_TRUNCATED", "message": "Your previous response was truncated due to token limits. Please continue where you left off."},
                continuation=True,
            )

        # 3. Patch required but model produced only conversational text
        if patch_required and not tool_calls and state.protocol_retries < self.max_protocol_retries:
            return RecoveryDecision(
                status="retry_model",
                retry_reason="PATCH_REQUIRED_BUT_TEXT_EMITTED",
                retry_feedback={
                    "required_tool": "patch.apply",
                    "message": (
                        "Conversational text alone is insufficient to resolve this task. "
                        "You MUST invoke `patch.apply` or `fs.write` with the source modification."
                    ),
                },
            )

        # 4. Unknown or unrecognized tool attempt
        attempted_unknown = proposal.get("unknownTool")
        if attempted_unknown and state.protocol_retries < self.max_protocol_retries:
            tools_snip = ", ".join(allowed_tools) if allowed_tools else "none"
            return RecoveryDecision(
                status="retry_model",
                retry_reason="UNKNOWN_TOOL_NAME",
                retry_feedback={
                    "allowed_tools": list(allowed_tools),
                    "message": f"Tool '{attempted_unknown}' is not available. Allowed tools: [{tools_snip}].",
                },
            )

        # 5. Default: Accept as conversational completion if no patch is strictly required
        return RecoveryDecision(status="accept", retry_reason="conversational_accepted")


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
                        retry_feedback={"continuation": True, "reason": "OUTPUT_TRUNCATED"},
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
