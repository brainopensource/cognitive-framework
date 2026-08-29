"""Protocol Recovery State Machine for Agency Episodes.

Implements bounded recovery policies when model outputs deviate from required wire contracts,
such as emitting conversational text when a diff is mandatory, malformed tool arguments, or
truncated completion strings.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping, Sequence

RecoveryActionKind = Literal[
    "accept",
    "retry_model",
    "fail_instrument",
]

RecoveryStatus = RecoveryActionKind


@dataclass(slots=True)
class RecoveryState:
    """Track retries for protocol drift within a single episode."""

    protocol_retries: int = 0
    truncation_retries: int = 0
    max_protocol_retries: int = 2
    max_truncation_retries: int = 1

    def with_protocol_retry(self) -> RecoveryState:
        return RecoveryState(
            protocol_retries=self.protocol_retries + 1,
            truncation_retries=self.truncation_retries,
            max_protocol_retries=self.max_protocol_retries,
            max_truncation_retries=self.max_truncation_retries,
        )


ProtocolRecoveryState = RecoveryState


@dataclass(frozen=True, slots=True)
class RecoveryDecision:
    """Decision emitted by the protocol recovery policy."""

    action: str = "accept"
    status: str = "accept"
    reason: str = "ok"
    retry_reason: str | None = None
    retry_feedback: Any = None
    feedback_message: str | None = None
    continuation: bool = False
    proposal: Any = None


class ProtocolRecoveryPolicy:
    """Evaluates proposals against recovery rules and produces actionable feedback."""

    def __init__(self, max_protocol_retries: int = 2, max_truncation_retries: int = 1) -> None:
        self.max_protocol_retries = max_protocol_retries
        self.max_truncation_retries = max_truncation_retries

    def evaluate(
        self,
        proposal: Mapping[str, Any],
        state: RecoveryState,
        *,
        patch_required: bool = False,
        allowed_tools: Sequence[str] = (),
    ) -> RecoveryDecision:
        text = str(proposal.get("text") or "")
        tool_calls = proposal.get("toolCalls") or ()
        finish_reason = proposal.get("finishReason")

        # 1. Valid proposal with tool calls -> Accept immediately
        if tool_calls:
            return RecoveryDecision(action="accept", status="accept", reason="valid_tool_calls", proposal=proposal)

        # 2. Truncation recovery
        if finish_reason in {"length", "max_tokens"} and state.truncation_retries < self.max_truncation_retries:
            state.truncation_retries += 1
            return RecoveryDecision(
                action="retry_model",
                status="retry_model",
                reason="OUTPUT_TRUNCATED",
                retry_reason="OUTPUT_TRUNCATED",
                feedback_message="Your previous response was truncated due to token limits. Please continue where you left off.",
                continuation=True,
            )

        # 3. Patch required but model produced only conversational text
        if patch_required and not tool_calls and state.protocol_retries < self.max_protocol_retries:
            state.protocol_retries += 1
            return RecoveryDecision(
                action="retry_model",
                status="retry_model",
                reason="PATCH_REQUIRED_BUT_TEXT_EMITTED",
                retry_reason="PATCH_REQUIRED_BUT_TEXT_EMITTED",
                feedback_message=(
                    "Conversational text alone is insufficient to resolve this task. "
                    "You MUST invoke `patch.apply` or `fs.write` with the source modification."
                ),
            )

        # 4. Unknown or unrecognized tool attempt
        attempted_unknown = proposal.get("unknownTool")
        if attempted_unknown and state.protocol_retries < self.max_protocol_retries:
            state.protocol_retries += 1
            tools_snip = ", ".join(allowed_tools) if allowed_tools else "none"
            return RecoveryDecision(
                action="retry_model",
                status="retry_model",
                reason="UNKNOWN_TOOL_NAME",
                retry_reason="UNKNOWN_TOOL_NAME",
                feedback_message=f"Tool '{attempted_unknown}' is not available. Allowed tools: [{tools_snip}].",
            )

        # 5. Default: Accept as conversational completion if no patch is strictly required
        return RecoveryDecision(action="accept", status="accept", reason="conversational_accepted", proposal=proposal)


def recover_proposal(
    raw_value: Any,
    state: RecoveryState,
    *,
    allowed_tools: Sequence[str] = (),
    decoders: Sequence[Any] = (),
    patch_detector: Any = None,
    truncation_detector: Any = None,
) -> tuple[RecoveryDecision, RecoveryState]:
    policy = ProtocolRecoveryPolicy()
    decision = policy.evaluate(
        raw_value if isinstance(raw_value, dict) else {},
        state,
        allowed_tools=allowed_tools,
    )
    return decision, state
