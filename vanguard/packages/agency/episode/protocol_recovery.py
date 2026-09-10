"""Protocol recovery state machine and retry policies for model responses."""

from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from enum import Enum
from types import MappingProxyType
from typing import Any, Literal, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of
from ...domain.canonicalisation.jcs import canonical_bytes, parse_json_text
from ...domain.transforms.contracts import ProposalDecoderProtocol
from .state import Proposal, ProposalKind, ProposalMalformed, parse_proposal

RecoveryStatus = Literal["accept", "retry_model", "fail_instrument"]

RECOVERY_STATE_SCHEMA = "aether.recovery-state/1"
MAX_DURABLE_ATTEMPTS = 12
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


class FailureClass(str, Enum):
    TRANSPORT = "transport"
    PROVIDER = "provider"
    PROTOCOL = "protocol"
    TRUNCATION = "truncation"
    TOOL = "tool"
    PATCH = "patch"
    VERIFICATION = "verification"
    PERMISSION = "permission"
    BUDGET = "budget"


def _natural(value: Any, field: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"invalid {field}")
    return value


def _require_digest(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise ValueError(f"malformed {field}")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")
    return value


_FAILURE_VALUES = {kind.value for kind in FailureClass}
_RECOVERY_ACTIONS = frozenset({"continue", "wait", "reground", "replan", "stop"})
_VERSIONED_REQUIRED = (
    "schema", "policyDigest", "history", "errors",
    "interventions", "decisions", "pendingOperation", "deadline",
)


@dataclass(frozen=True, slots=True)
class Attempt:
    """One durable recovery attempt in `aether.recovery-state/1` history."""

    fingerprint: str
    outcome: str
    progress_key: str
    failure: str | None = None

    def __post_init__(self) -> None:
        _require_digest(self.fingerprint, "attempt fingerprint")
        _require_text(self.outcome, "attempt outcome")
        _require_digest(self.progress_key, "attempt progress key")
        if self.failure is not None and self.failure not in _FAILURE_VALUES:
            raise ValueError("unknown failure classification")

    def to_dict(self) -> dict[str, Any]:
        return {
            "fingerprint": self.fingerprint,
            "outcome": self.outcome,
            "progressKey": self.progress_key,
            "failure": self.failure,
        }

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "Attempt":
        if not isinstance(raw, Mapping):
            raise TypeError("attempt must be an object")
        failure = raw.get("failure")
        if failure == "":
            failure = None
        return cls(
            fingerprint=raw.get("fingerprint", ""),
            outcome=str(raw.get("outcome", "")),
            progress_key=raw.get("progressKey", raw.get("progress_key", "")),
            failure=None if failure is None else str(failure),
        )


@dataclass(frozen=True, slots=True)
class SemanticRecoveryDecision:
    """NT-1.2 persisted recovery-policy decision.

    Distinct from the protocol-parser `RecoveryDecision` (`accept` /
    `retry_model` / `fail_instrument`). This value never consults.
    """

    action: str
    reason: str
    delay_ms: int
    state_digest: str
    remaining_budget_ref: str

    def __post_init__(self) -> None:
        if self.action not in _RECOVERY_ACTIONS:
            raise ValueError("unsupported recovery action")
        _require_text(self.reason, "recovery reason")
        _natural(self.delay_ms, "delay_ms")
        _require_digest(self.state_digest, "state digest")
        _require_digest(self.remaining_budget_ref, "remaining budget ref")

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "reason": self.reason,
            "delayMs": self.delay_ms,
            "stateDigest": self.state_digest,
            "remainingBudgetRef": self.remaining_budget_ref,
        }

    def encode(self) -> bytes:
        return canonical_bytes(self.to_dict())

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "SemanticRecoveryDecision":
        if not isinstance(raw, Mapping):
            raise TypeError("recovery decision must be an object")
        return cls(
            action=str(raw.get("action", "")),
            reason=str(raw.get("reason", "")),
            delay_ms=raw.get("delayMs", raw.get("delay_ms", 0)),
            state_digest=raw.get("stateDigest", raw.get("state_digest", "")),
            remaining_budget_ref=raw.get("remainingBudgetRef", raw.get("remaining_budget_ref", "")),
        )

    @classmethod
    def decode(cls, payload: bytes) -> "SemanticRecoveryDecision":
        payload_bytes = bytes(payload)
        raw = parse_json_text(payload_bytes.decode("utf-8"))
        if not isinstance(raw, Mapping):
            raise TypeError("recovery decision must be an object")
        decision = cls.from_mapping(raw)
        if decision.encode() != payload_bytes:
            raise ValueError("noncanonical recovery decision")
        return decision


def semantic_attempt_fingerprint(
    action: str, arguments: Mapping[str, Any] | None = None,
    workspace_digest: str = "",
) -> str:
    """Fingerprint the attempted operation, excluding transcript history."""
    return digest_of({
        "action": str(action),
        "arguments": dict(arguments or {}),
        "workspaceDigest": workspace_digest,
    })


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

    def __post_init__(self) -> None:
        object.__setattr__(self, "retry_feedback", MappingProxyType(dict(self.retry_feedback)))
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))

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
    #: Durable semantic attempt history. Tuple keeps checkpoint serialization
    #: deterministic and prevents an unchanged failed action from repeating.
    attempted_fingerprints: tuple[str, ...] = ()
    spent_decisions: tuple[str, ...] = ()
    policy_digest: str = ""
    history: tuple[Attempt, ...] = ()
    errors: Mapping[str, int] = field(default_factory=dict)
    interventions: int = 0
    decisions: int = 0
    pending_operation: str | None = None
    deadline: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "attempted_fingerprints", tuple(self.attempted_fingerprints))
        object.__setattr__(self, "spent_decisions", tuple(self.spent_decisions))
        object.__setattr__(self, "history", tuple(self.history))
        for name in (
            "transport_retries", "protocol_retries", "truncation_retries", "effect_retries",
            "max_transport_retries", "max_protocol_retries", "max_truncation_retries",
            "max_effect_retries", "interventions", "decisions",
        ):
            _natural(getattr(self, name), name.replace("_", " "))
        if self.policy_digest:
            _require_digest(self.policy_digest, "policy digest")
        if len(self.attempted_fingerprints) > MAX_DURABLE_ATTEMPTS:
            raise ValueError("durable attempt history exceeds bound")
        if len(self.history) > MAX_DURABLE_ATTEMPTS:
            raise ValueError("durable attempt history exceeds bound")
        for fingerprint in self.attempted_fingerprints:
            _require_digest(fingerprint, "attempt fingerprint")
        if not all(isinstance(item, str) and item for item in self.spent_decisions):
            raise ValueError("spent decisions must be nonempty strings")
        if not all(isinstance(item, Attempt) for item in self.history):
            raise TypeError("history must contain Attempt values")
        if self.history and self.attempted_fingerprints:
            if tuple(item.fingerprint for item in self.history) != self.attempted_fingerprints:
                raise ValueError("inconsistent recovery history and fingerprints")
        if self.history and self.spent_decisions:
            if tuple(item.outcome for item in self.history) != self.spent_decisions:
                raise ValueError("inconsistent recovery history and spent decisions")
        errors = {}
        for key, count in dict(self.errors).items():
            if key not in _FAILURE_VALUES:
                raise ValueError("unknown failure classification")
            errors[key] = _natural(count, "error count")
        object.__setattr__(self, "errors", MappingProxyType(errors))
        pending = self.pending_operation
        deadline = self.deadline
        if pending == "":
            pending = None
            object.__setattr__(self, "pending_operation", None)
        if deadline == "":
            deadline = None
            object.__setattr__(self, "deadline", None)
        if (pending is None) != (deadline is None):
            raise ValueError("pending operation requires a deadline")
        if pending is not None and not isinstance(pending, str):
            raise TypeError("pending operation must be a string")
        if deadline is not None and not isinstance(deadline, str):
            raise TypeError("deadline must be a string")

    def with_protocol_retry(self) -> ProtocolRecoveryState:
        return replace(self, protocol_retries=self.protocol_retries + 1)

    def with_truncation_retry(self) -> ProtocolRecoveryState:
        return replace(self, truncation_retries=self.truncation_retries + 1)

    def with_transport_retry(self) -> ProtocolRecoveryState:
        return replace(self, transport_retries=self.transport_retries + 1)

    def with_effect_retry(self) -> ProtocolRecoveryState:
        return replace(self, effect_retries=self.effect_retries + 1)

    def record_attempt(self, fingerprint: str, decision: str = "") -> ProtocolRecoveryState:
        if not fingerprint:
            raise ValueError("attempt fingerprint is required")
        _require_digest(fingerprint, "attempt fingerprint")
        if len(self.attempted_fingerprints) >= MAX_DURABLE_ATTEMPTS:
            raise ValueError("durable attempt history exceeds bound")
        spent = (self.spent_decisions + (decision,)) if decision else self.spent_decisions
        return replace(
            self,
            attempted_fingerprints=self.attempted_fingerprints + (fingerprint,),
            spent_decisions=spent,
        )

    def has_attempted(self, fingerprint: str) -> bool:
        return fingerprint in self.attempted_fingerprints

    def _policy_digest(self) -> str:
        if self.policy_digest:
            return self.policy_digest
        return digest_of({
            "maxTransportRetries": self.max_transport_retries,
            "maxProtocolRetries": self.max_protocol_retries,
            "maxTruncationRetries": self.max_truncation_retries,
            "maxEffectRetries": self.max_effect_retries,
        })

    def _history(self) -> tuple[Attempt, ...]:
        if self.history:
            return self.history
        items: list[Attempt] = []
        for index, fingerprint in enumerate(self.attempted_fingerprints):
            outcome = (
                self.spent_decisions[index]
                if index < len(self.spent_decisions)
                else "recorded"
            )
            items.append(Attempt(fingerprint, outcome, fingerprint, None))
        return tuple(items)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": RECOVERY_STATE_SCHEMA,
            "policyDigest": self._policy_digest(),
            "history": [item.to_dict() for item in self._history()],
            "errors": dict(self.errors),
            "interventions": self.interventions,
            "decisions": self.decisions,
            "pendingOperation": self.pending_operation,
            "deadline": self.deadline,
            "transportRetries": self.transport_retries,
            "protocolRetries": self.protocol_retries,
            "truncationRetries": self.truncation_retries,
            "effectRetries": self.effect_retries,
            "maxTransportRetries": self.max_transport_retries,
            "maxProtocolRetries": self.max_protocol_retries,
            "maxTruncationRetries": self.max_truncation_retries,
            "maxEffectRetries": self.max_effect_retries,
            "attemptedFingerprints": list(self.attempted_fingerprints),
            "spentDecisions": list(self.spent_decisions),
        }

    def encode(self) -> bytes:
        return canonical_bytes(self.to_dict())

    @classmethod
    def decode(cls, payload: bytes) -> "ProtocolRecoveryState":
        if not isinstance(payload, (bytes, bytearray)):
            raise TypeError("recovery payload must be bytes")
        payload_bytes = bytes(payload)
        raw = parse_json_text(payload_bytes.decode("utf-8"))
        if not isinstance(raw, Mapping):
            raise TypeError("recovery state must be an object")
        state = cls.from_dict(raw)
        if state.encode() != payload_bytes:
            raise ValueError("noncanonical or unknown recovery fields")
        return state

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ProtocolRecoveryState":
        if not isinstance(raw, Mapping):
            raise TypeError("recovery state must be an object")
        schema = raw.get("schema")
        if schema is None:
            return cls._from_legacy(raw)
        if schema != RECOVERY_STATE_SCHEMA:
            raise ValueError("unsupported recovery schema")
        missing = [key for key in _VERSIONED_REQUIRED if key not in raw]
        if missing:
            raise ValueError(f"incomplete recovery-state payload: missing {missing[0]}")
        history_raw = raw["history"]
        if not isinstance(history_raw, Sequence) or isinstance(history_raw, (str, bytes)):
            raise TypeError("history must be a sequence")
        errors_raw = raw["errors"]
        if not isinstance(errors_raw, Mapping):
            raise TypeError("errors must be an object")
        fingerprints_raw = raw.get("attemptedFingerprints", raw.get("attempted_fingerprints", ()))
        decisions_raw = raw.get("spentDecisions", raw.get("spent_decisions", ()))
        if not isinstance(fingerprints_raw, Sequence) or isinstance(fingerprints_raw, (str, bytes)):
            raise TypeError("attempted fingerprints must be a sequence")
        if not isinstance(decisions_raw, Sequence) or isinstance(decisions_raw, (str, bytes)):
            raise TypeError("spent decisions must be a sequence")
        return cls(
            transport_retries=_natural(
                raw.get("transportRetries", raw.get("transport_retries", 0)), "transport retries",
            ),
            protocol_retries=_natural(
                raw.get("protocolRetries", raw.get("protocol_retries", 0)), "protocol retries",
            ),
            truncation_retries=_natural(
                raw.get("truncationRetries", raw.get("truncation_retries", 0)), "truncation retries",
            ),
            effect_retries=_natural(
                raw.get("effectRetries", raw.get("effect_retries", 0)), "effect retries",
            ),
            max_transport_retries=_natural(
                raw.get("maxTransportRetries", raw.get("max_transport_retries", 2)),
                "max transport retries",
            ),
            max_protocol_retries=_natural(
                raw.get("maxProtocolRetries", raw.get("max_protocol_retries", 2)),
                "max protocol retries",
            ),
            max_truncation_retries=_natural(
                raw.get("maxTruncationRetries", raw.get("max_truncation_retries", 1)),
                "max truncation retries",
            ),
            max_effect_retries=_natural(
                raw.get("maxEffectRetries", raw.get("max_effect_retries", 2)),
                "max effect retries",
            ),
            attempted_fingerprints=tuple(str(item) for item in fingerprints_raw),
            spent_decisions=tuple(str(item) for item in decisions_raw),
            policy_digest=raw["policyDigest"] if "policyDigest" in raw else raw.get("policy_digest", ""),
            history=tuple(Attempt.from_mapping(item) for item in history_raw),
            errors={str(key): value for key, value in errors_raw.items()},
            interventions=_natural(raw["interventions"], "interventions"),
            decisions=_natural(raw["decisions"], "decisions"),
            pending_operation=raw["pendingOperation"],
            deadline=raw["deadline"],
        )

    @classmethod
    def _from_legacy(cls, raw: Mapping[str, Any]) -> "ProtocolRecoveryState":
        fingerprints_raw = raw.get("attemptedFingerprints", raw.get("attempted_fingerprints", ()))
        decisions_raw = raw.get("spentDecisions", raw.get("spent_decisions", ()))
        if fingerprints_raw in (None, ()):
            fingerprints_raw = ()
        if decisions_raw in (None, ()):
            decisions_raw = ()
        if not isinstance(fingerprints_raw, Sequence) or isinstance(fingerprints_raw, (str, bytes)):
            raise TypeError("attempted fingerprints must be a sequence")
        if not isinstance(decisions_raw, Sequence) or isinstance(decisions_raw, (str, bytes)):
            raise TypeError("spent decisions must be a sequence")
        return cls(
            transport_retries=_natural(
                raw.get("transportRetries", raw.get("transport_retries", 0)), "transport retries",
            ),
            protocol_retries=_natural(
                raw.get("protocolRetries", raw.get("protocol_retries", 0)), "protocol retries",
            ),
            truncation_retries=_natural(
                raw.get("truncationRetries", raw.get("truncation_retries", 0)), "truncation retries",
            ),
            effect_retries=_natural(
                raw.get("effectRetries", raw.get("effect_retries", 0)), "effect retries",
            ),
            max_transport_retries=_legacy_ceiling(
                raw, "maxTransportRetries", "max_transport_retries", 2, "max transport retries",
            ),
            max_protocol_retries=_legacy_ceiling(
                raw, "maxProtocolRetries", "max_protocol_retries", 2, "max protocol retries",
            ),
            max_truncation_retries=_legacy_ceiling(
                raw, "maxTruncationRetries", "max_truncation_retries", 1, "max truncation retries",
            ),
            max_effect_retries=_legacy_ceiling(
                raw, "maxEffectRetries", "max_effect_retries", 2, "max effect retries",
            ),
            attempted_fingerprints=tuple(str(item) for item in fingerprints_raw),
            spent_decisions=tuple(str(item) for item in decisions_raw),
        )


def _legacy_ceiling(
    raw: Mapping[str, Any], camel: str, snake: str, default: int, field: str,
) -> int:
    if camel in raw or snake in raw:
        return _natural(raw.get(camel, raw.get(snake)), field)
    return default


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

    def classify(self, detail: str) -> FailureClass:
        text = (detail or "").lower()
        for kind, markers in (
            (FailureClass.PERMISSION, ("permission", "forbidden", "denied")),
            (FailureClass.BUDGET, ("budget", "quota")),
            (FailureClass.TRUNCATION, ("truncated", "max_tokens", "length")),
            (FailureClass.PATCH, ("patch", "hunk")),
            (FailureClass.VERIFICATION, ("test", "verification")),
            (FailureClass.TOOL, ("tool", "command")),
            (FailureClass.TRANSPORT, ("timeout", "connection", "socket")),
            (FailureClass.PROVIDER, ("provider", "http ")),
        ):
            if any(marker in text for marker in markers):
                return kind
        return FailureClass.PROTOCOL

    def decide_failure(
        self, detail: str, state: ProtocolRecoveryState, *, action: str = "",
        arguments: Mapping[str, Any] | None = None, workspace_digest: str = "",
    ) -> tuple[RecoveryDecision, ProtocolRecoveryState]:
        kind = self.classify(detail)
        fingerprint = semantic_attempt_fingerprint(action or kind.value, arguments, workspace_digest)
        if state.has_attempted(fingerprint) or kind in {FailureClass.PERMISSION, FailureClass.BUDGET}:
            return RecoveryDecision(status="fail_instrument", failure_code=kind.value), state.record_attempt(fingerprint, "no_retry")
        next_state = state.record_attempt(fingerprint, "retry")
        if kind is FailureClass.TRUNCATION and next_state.truncation_retries <= self.max_truncation_retries:
            next_state = next_state.with_truncation_retry()
        elif next_state.protocol_retries < self.max_protocol_retries:
            next_state = next_state.with_protocol_retry()
        else:
            return RecoveryDecision(status="fail_instrument", failure_code=kind.value), next_state
        return RecoveryDecision(status="retry_model", retry_reason=kind.value), next_state


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
