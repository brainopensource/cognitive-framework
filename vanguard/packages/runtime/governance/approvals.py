"""Descriptor-bound human approvals for privileged ``fs.patch`` effects.

Owning contract: REQ-APP-001, VG-05 F-08/K-13..K-16.

This module never dispatches an effect.  It verifies durable human approval
evidence and wraps the normal S5 policy decision; an approved request then
re-enters ``Kernel.dispatch`` at S1 and follows the sole S1--S12 path.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of
from ...domain.canonicalisation.jcs import canonical_bytes
from ...domain.ledger.events import EventEnvelope
from ...domain.primitives.primitives import ParseError, parse_timestamp
from ...kernel import (
    Decision,
    EffectRequest,
    FailurePath,
    Outcome,
    SinkClass,
    SuspensionToken,
    descriptor_of,
)

__all__ = [
    "ApprovalAuthority",
    "ApprovalAuthorization",
    "ApprovalChallenge",
    "ApprovalDecision",
    "ApprovalFlow",
    "ApprovalFormatError",
    "DescriptorBoundApprovalPolicy",
    "normalise_unified_diff",
]


class ApprovalFormatError(ValueError):
    """Approval input is ambiguous, malformed, or not an ``fs.patch`` diff."""


@dataclass(frozen=True, slots=True)
class ApprovalChallenge:
    approval_id: str
    process_id: str
    action: str
    normalized_diff: str
    args_digest: str
    descriptor_digest: str
    principal: str
    expires_at: str

    def payload(self) -> Mapping[str, str]:
        """Payload rendered to the client and persisted in the ledger."""
        return {
            "approvalId": self.approval_id,
            "processId": self.process_id,
            "action": self.action,
            "normalizedDiff": self.normalized_diff,
            "argsDigest": self.args_digest,
            "descriptorDigest": self.descriptor_digest,
            "principal": self.principal,
            "expiresAt": self.expires_at,
        }


@dataclass(frozen=True, slots=True)
class ApprovalDecision:
    approval_id: str
    resolution: str
    reviewer: str
    args_digest: str
    descriptor_digest: str
    expires_at: str
    signature: str

    def signed_payload(self) -> Mapping[str, str]:
        return {
            "approvalId": self.approval_id,
            "resolution": self.resolution,
            "reviewer": self.reviewer,
            "argsDigest": self.args_digest,
            "descriptorDigest": self.descriptor_digest,
            "expiresAt": self.expires_at,
        }

    def payload(self) -> Mapping[str, str]:
        return {**self.signed_payload(), "signature": self.signature}


@dataclass(frozen=True, slots=True)
class ApprovalAuthorization:
    approved: bool
    reason: str
    approval_id: str
    args_digest: str
    descriptor_digest: str


class ApprovalAuthority:
    """Operator-held HMAC authority used across the client/runtime boundary."""

    def __init__(self, key: bytes) -> None:
        if not isinstance(key, bytes) or len(key) < 16:
            raise ValueError("approval signing key must contain at least 16 bytes")
        self._key = key

    def approve(self, challenge: ApprovalChallenge, *, reviewer: str) -> ApprovalDecision:
        if not reviewer:
            raise ApprovalFormatError("reviewer is required")
        unsigned = ApprovalDecision(
            approval_id=challenge.approval_id,
            resolution="approved",
            reviewer=reviewer,
            args_digest=challenge.args_digest,
            descriptor_digest=challenge.descriptor_digest,
            expires_at=challenge.expires_at,
            signature="",
        )
        return ApprovalDecision(
            approval_id=unsigned.approval_id,
            resolution=unsigned.resolution,
            reviewer=unsigned.reviewer,
            args_digest=unsigned.args_digest,
            descriptor_digest=unsigned.descriptor_digest,
            expires_at=unsigned.expires_at,
            signature=self._sign(unsigned.signed_payload()),
        )

    def verify(self, decision: ApprovalDecision) -> bool:
        return hmac.compare_digest(
            self._sign(decision.signed_payload()), decision.signature
        )

    def _sign(self, payload: Mapping[str, str]) -> str:
        return hmac.new(self._key, canonical_bytes(payload), hashlib.sha256).hexdigest()


class ApprovalFlow:
    """Create approval challenges and verify decisions without model state."""

    def __init__(self, authority: ApprovalAuthority, *,
                 patch_verb: str = "fs.patch") -> None:
        self._authority = authority
        # Which verb carries the diff is a *manifest* fact, not a runtime one:
        # `vg-code-default` names it `patch.apply` while `VG-05` writes
        # `fs.patch`. The composition root supplies the harness's own verb; the
        # default keeps every existing caller on `fs.patch` unchanged.
        self._patch_verb = patch_verb

    def request(
        self,
        request: EffectRequest,
        suspension: SuspensionToken,
        *,
        process_id: str,
        expires_at: str,
    ) -> ApprovalChallenge:
        if not process_id or not expires_at:
            raise ApprovalFormatError("process_id and expires_at are required")
        try:
            parse_timestamp(expires_at)
        except ParseError as exc:
            raise ApprovalFormatError("expires_at must be an RFC 3339 timestamp") from exc
        if (request.action != self._patch_verb
                or request.declared_sink_class is not SinkClass.PRIVILEGED):
            raise ApprovalFormatError(
                f"only privileged {self._patch_verb} effects use this approval flow")
        descriptor_digest = descriptor_of(request.action, request.args)
        if suspension.descriptor_digest != descriptor_digest:
            raise ApprovalFormatError("suspension token does not bind this request")
        if suspension.principal != request.principal:
            raise ApprovalFormatError("suspension principal does not bind this request")
        normalized_diff = _diff_from(request)
        return ApprovalChallenge(
            approval_id=suspension.token_id,
            process_id=process_id,
            action=request.action,
            normalized_diff=normalized_diff,
            args_digest=_diff_digest(normalized_diff),
            descriptor_digest=descriptor_digest,
            principal=request.principal,
            expires_at=expires_at,
        )

    def verify(
        self,
        challenge: ApprovalChallenge,
        decision: ApprovalDecision,
        request: EffectRequest,
        *,
        now: str,
    ) -> ApprovalAuthorization:
        """Verify signature, expiry, and the exact request at resumption."""
        try:
            parse_timestamp(now)
            parse_timestamp(challenge.expires_at)
        except ParseError:
            return _denied(challenge, "approval_timestamp_invalid")
        expected_descriptor = descriptor_of(request.action, request.args)
        try:
            expected_args = _diff_digest(_diff_from(request))
        except (ApprovalFormatError, TypeError, ValueError):
            return _denied(challenge, "resumed_request_invalid")

        checks = (
            (challenge.action == request.action, "action_binding_mismatch"),
            (challenge.principal == request.principal, "principal_binding_mismatch"),
            (
                _diff_digest(challenge.normalized_diff) == challenge.args_digest,
                "challenge_args_digest_mismatch",
            ),
            (decision.resolution == "approved", "approval_rejected"),
            (decision.approval_id == challenge.approval_id, "approval_id_mismatch"),
            (decision.expires_at == challenge.expires_at, "expiry_binding_mismatch"),
            (now < challenge.expires_at, "approval_expired"),
            (decision.args_digest == challenge.args_digest, "decision_args_digest_mismatch"),
            (expected_args == challenge.args_digest, "resumed_args_digest_mismatch"),
            (decision.descriptor_digest == challenge.descriptor_digest, "decision_descriptor_mismatch"),
            (expected_descriptor == challenge.descriptor_digest, "resumed_descriptor_mismatch"),
        )
        for valid, reason in checks:
            if not valid:
                return _denied(challenge, reason)
        if not self._authority.verify(decision):
            return _denied(challenge, "signature_invalid")
        return ApprovalAuthorization(
            True,
            "approved",
            challenge.approval_id,
            challenge.args_digest,
            challenge.descriptor_digest,
        )

    def verify_from_ledger(
        self,
        events: Sequence[EventEnvelope],
        request: EffectRequest,
        suspension: SuspensionToken,
        *,
        process_id: str,
        now: str,
    ) -> ApprovalAuthorization:
        """Reconstruct approval solely from ordered durable ledger events."""
        requested: ApprovalChallenge | None = None
        resolved: ApprovalDecision | None = None
        for event in sorted(events, key=lambda item: int(item.seq)):
            payload = event.payload
            if event.scope != "governance" or payload.get("processId") != process_id:
                continue
            if payload.get("approvalId") != suspension.token_id:
                continue
            kind = payload.get("kind")
            try:
                if kind == "ApprovalRequested":
                    requested = _challenge_from_payload(payload)
                    resolved = None
                elif kind == "ApprovalResolved" and requested is not None:
                    resolved = _decision_from_payload(payload)
            except ApprovalFormatError:
                return ApprovalAuthorization(
                    False, "approval_evidence_invalid", suspension.token_id, "", ""
                )
        if requested is None or resolved is None:
            return ApprovalAuthorization(False, "approval_evidence_missing", suspension.token_id, "", "")
        return self.verify(requested, resolved, request, now=now)


class DescriptorBoundApprovalPolicy:
    """Allow one already-approved descriptor after normal policy checks.

    Scope attenuation and provenance checks still run in the delegate.  This
    wrapper changes only ``REQUIRE_APPROVAL``; an invalid authorization becomes
    a pre-lease rejection and can never reach grant issuance or S9.
    """

    def __init__(self, delegate: Any, authorization: ApprovalAuthorization) -> None:
        self._delegate = delegate
        self._authorization = authorization

    def authorize(
        self,
        request: EffectRequest,
        *,
        widens_capability: bool,
        requested_scope: Any,
        spans: Sequence[Any] | None = None,
    ) -> Decision:
        decision: Decision = self._delegate.authorize(
            request,
            widens_capability=widens_capability,
            requested_scope=requested_scope,
            spans=spans,
        )
        if decision.outcome is not Outcome.REQUIRE_APPROVAL:
            return decision
        authorization = self._authorization
        try:
            matches = (
                authorization.approved
                and authorization.args_digest == _diff_digest(_diff_from(request))
                and authorization.descriptor_digest == descriptor_of(request.action, request.args)
            )
        except (ApprovalFormatError, TypeError, ValueError):
            matches = False
        if not matches:
            return Decision(
                Outcome.REJECT,
                FailurePath.DENIED_REJECT,
                authorization.reason or "approval binding invalid",
                requested=decision.requested,
                grantable=decision.grantable,
            )
        return Decision(Outcome.ALLOW, granted_scope=decision.granted_scope)


def normalise_unified_diff(value: str) -> str:
    """Canonical line endings and final newline for a real unified diff."""
    if not isinstance(value, str) or "\x00" in value:
        raise ApprovalFormatError("diff must be non-binary text")
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    if normalized and not normalized.endswith("\n"):
        normalized += "\n"
    lines = normalized.splitlines()
    if not (
        any(line.startswith("--- ") for line in lines)
        and any(line.startswith("+++ ") for line in lines)
        and any(line.startswith("@@ ") for line in lines)
    ):
        raise ApprovalFormatError("fs.patch approval requires a unified diff")
    return normalized


def _diff_from(request: EffectRequest) -> str:
    candidates = [
        request.args[key]
        for key in ("diff", "patch", "unifiedDiff")
        if key in request.args
    ]
    if len(candidates) != 1:
        raise ApprovalFormatError("exactly one unified diff argument is required")
    return normalise_unified_diff(candidates[0])


def _diff_digest(normalized_diff: str) -> str:
    # EffectDescriptor.argsDigest is the digest of the canonical args object.
    return digest_of({"diff": normalized_diff})


def _denied(challenge: ApprovalChallenge, reason: str) -> ApprovalAuthorization:
    return ApprovalAuthorization(
        False,
        reason,
        challenge.approval_id,
        challenge.args_digest,
        challenge.descriptor_digest,
    )


def _required_string(payload: Mapping[str, Any], name: str) -> str:
    value = payload.get(name)
    if not isinstance(value, str) or not value:
        raise ApprovalFormatError(f"{name} must be a non-empty string")
    return value


def _challenge_from_payload(payload: Mapping[str, Any]) -> ApprovalChallenge:
    return ApprovalChallenge(
        approval_id=_required_string(payload, "approvalId"),
        process_id=_required_string(payload, "processId"),
        action=_required_string(payload, "action"),
        normalized_diff=normalise_unified_diff(_required_string(payload, "normalizedDiff")),
        args_digest=_required_string(payload, "argsDigest"),
        descriptor_digest=_required_string(payload, "descriptorDigest"),
        principal=_required_string(payload, "principal"),
        expires_at=_required_string(payload, "expiresAt"),
    )


def _decision_from_payload(payload: Mapping[str, Any]) -> ApprovalDecision:
    return ApprovalDecision(
        approval_id=_required_string(payload, "approvalId"),
        resolution=_required_string(payload, "resolution"),
        reviewer=_required_string(payload, "reviewer"),
        args_digest=_required_string(payload, "argsDigest"),
        descriptor_digest=_required_string(payload, "descriptorDigest"),
        expires_at=_required_string(payload, "expiresAt"),
        signature=_required_string(payload, "signature"),
    )
