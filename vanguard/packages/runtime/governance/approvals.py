"""Descriptor-bound human approvals for privileged ``fs.patch`` / ``patch.apply`` effects.

Owning contract: REQ-APP-001, VG-05 F-08/K-13..K-16, ADR-0062, DEC-6B-022.

This module never dispatches an effect. It verifies durable human approval
evidence and wraps the normal S5 policy decision; an approved request then
re-enters ``Kernel.dispatch`` at S1 and follows the sole S1--S12 path.

Authority Model:
- The Operator (CLI / Key Agent) holds the private Ed25519 signing key (`OperatorSigner`).
- The Runtime holds strictly the public verification keys (`ApprovalAuthority`).
- Verification is cryptographic, descriptor-bound, and evaluated against canonical bytes.
- The Runtime cannot mint signatures (`GOV-01`).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519

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
    Span,
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
    "OperatorSigner",
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
    key_id: str = "operator-key-default"

    def signed_payload(self) -> Mapping[str, str]:
        return {
            "approvalId": self.approval_id,
            "argsDigest": self.args_digest,
            "descriptorDigest": self.descriptor_digest,
            "expiresAt": self.expires_at,
            "keyId": self.key_id,
            "resolution": self.resolution,
            "reviewer": self.reviewer,
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


class OperatorSigner:
    """Operator-held Ed25519 signing agent. Lives outside the runtime (e.g. in CLI)."""

    def __init__(
        self,
        private_key: ed25519.Ed25519PrivateKey | bytes | None = None,
        *,
        key_id: str = "operator-key-default",
    ) -> None:
        self.key_id = key_id
        if private_key is None:
            self._private_key = ed25519.Ed25519PrivateKey.generate()
        elif isinstance(private_key, bytes):
            if len(private_key) == 32:
                self._private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key)
            else:
                derived = hashlib.sha256(private_key).digest()
                self._private_key = ed25519.Ed25519PrivateKey.from_private_bytes(derived)
        elif isinstance(private_key, ed25519.Ed25519PrivateKey):
            self._private_key = private_key
        else:
            raise TypeError("unsupported private key type")

    @property
    def public_key(self) -> ed25519.Ed25519PublicKey:
        return self._private_key.public_key()

    @property
    def public_bytes(self) -> bytes:
        from cryptography.hazmat.primitives import serialization

        return self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

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
            key_id=self.key_id,
            signature="",
        )
        msg = canonical_bytes(unsigned.signed_payload())
        sig_bytes = self._private_key.sign(msg)
        return ApprovalDecision(
            approval_id=unsigned.approval_id,
            resolution=unsigned.resolution,
            reviewer=unsigned.reviewer,
            args_digest=unsigned.args_digest,
            descriptor_digest=unsigned.descriptor_digest,
            expires_at=unsigned.expires_at,
            key_id=self.key_id,
            signature=sig_bytes.hex(),
        )

    def reject(self, challenge: ApprovalChallenge, *, reviewer: str) -> ApprovalDecision:
        if not reviewer:
            raise ApprovalFormatError("reviewer is required")
        unsigned = ApprovalDecision(
            approval_id=challenge.approval_id,
            resolution="rejected",
            reviewer=reviewer,
            args_digest=challenge.args_digest,
            descriptor_digest=challenge.descriptor_digest,
            expires_at=challenge.expires_at,
            key_id=self.key_id,
            signature="",
        )
        msg = canonical_bytes(unsigned.signed_payload())
        sig_bytes = self._private_key.sign(msg)
        return ApprovalDecision(
            approval_id=unsigned.approval_id,
            resolution=unsigned.resolution,
            reviewer=unsigned.reviewer,
            args_digest=unsigned.args_digest,
            descriptor_digest=unsigned.descriptor_digest,
            expires_at=unsigned.expires_at,
            key_id=self.key_id,
            signature=sig_bytes.hex(),
        )


class ApprovalAuthority:
    """Runtime-held verification authority. Holds STRICTLY public keys (`GOV-01`, `ADR-0062`)."""

    def __init__(
        self,
        public_keys: Mapping[str, ed25519.Ed25519PublicKey | bytes]
        | ed25519.Ed25519PublicKey
        | bytes
        | None = None,
        *,
        default_key_id: str = "operator-key-default",
    ) -> None:
        self._keys: dict[str, ed25519.Ed25519PublicKey] = {}
        self.default_key_id = default_key_id

        if public_keys is None:
            pass
        elif isinstance(public_keys, ed25519.Ed25519PublicKey):
            self._keys[default_key_id] = public_keys
        elif isinstance(public_keys, bytes):
            if len(public_keys) == 32:
                try:
                    self._keys[default_key_id] = ed25519.Ed25519PublicKey.from_public_bytes(
                        public_keys
                    )
                except Exception:
                    derived = hashlib.sha256(public_keys).digest()
                    self._keys[default_key_id] = ed25519.Ed25519PublicKey.from_public_bytes(
                        derived
                    )
            else:
                derived = hashlib.sha256(public_keys).digest()
                self._keys[default_key_id] = ed25519.Ed25519PublicKey.from_public_bytes(
                    derived
                )
        elif isinstance(public_keys, Mapping):
            for kid, key in public_keys.items():
                if isinstance(key, ed25519.Ed25519PublicKey):
                    self._keys[kid] = key
                elif isinstance(key, bytes):
                    if len(key) == 32:
                        try:
                            self._keys[kid] = ed25519.Ed25519PublicKey.from_public_bytes(key)
                        except Exception:
                            derived = hashlib.sha256(key).digest()
                            self._keys[kid] = ed25519.Ed25519PublicKey.from_public_bytes(derived)
                    else:
                        derived = hashlib.sha256(key).digest()
                        self._keys[kid] = ed25519.Ed25519PublicKey.from_public_bytes(derived)
                else:
                    raise ValueError(f"invalid public key for key ID {kid!r}")
        else:
            raise TypeError("unsupported public_keys specification")

    def register_public_key(self, key_id: str, key: ed25519.Ed25519PublicKey | bytes) -> None:
        if isinstance(key, ed25519.Ed25519PublicKey):
            self._keys[key_id] = key
        elif isinstance(key, bytes):
            if len(key) == 32:
                try:
                    self._keys[key_id] = ed25519.Ed25519PublicKey.from_public_bytes(key)
                except Exception:
                    derived = hashlib.sha256(key).digest()
                    self._keys[key_id] = ed25519.Ed25519PublicKey.from_public_bytes(derived)
            else:
                derived = hashlib.sha256(key).digest()
                self._keys[key_id] = ed25519.Ed25519PublicKey.from_public_bytes(derived)
        else:
            raise ValueError(f"invalid public key for key ID {key_id!r}")

    def verify(self, decision: ApprovalDecision) -> bool:
        public_key = self._keys.get(decision.key_id)
        if public_key is None:
            return False
        try:
            sig_bytes = bytes.fromhex(decision.signature)
            if len(sig_bytes) != 64:
                return False
        except (ValueError, TypeError):
            return False

        msg = canonical_bytes(decision.signed_payload())
        try:
            public_key.verify(sig_bytes, msg)
            return True
        except InvalidSignature:
            return False


class ApprovalFlow:
    """Create approval challenges and verify decisions without model state."""

    def __init__(
        self,
        authority: ApprovalAuthority,
        *,
        patch_verb: str = "fs.patch",
    ) -> None:
        self._authority = authority
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
        if request.declared_sink_class is not SinkClass.PRIVILEGED:
            raise ApprovalFormatError(
                "only privileged effects use this approval flow"
            )
        descriptor_digest = descriptor_of(request.action, request.args)
        if suspension.descriptor_digest != descriptor_digest:
            raise ApprovalFormatError("suspension token does not bind this request")
        if suspension.principal != request.principal:
            raise ApprovalFormatError("suspension principal does not bind this request")
        normalized_diff = (_diff_from(request)
                           if request.action == self._patch_verb
                           else _request_material(request))
        return ApprovalChallenge(
            approval_id=suspension.token_id,
            process_id=process_id,
            action=request.action,
            normalized_diff=normalized_diff,
            args_digest=_material_digest(normalized_diff),
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
            expected_material = (_diff_from(request)
                                 if request.action == self._patch_verb
                                 else _request_material(request))
        except (ApprovalFormatError, TypeError, ValueError):
            return _denied(challenge, "resumed_request_invalid")

        checks = (
            (challenge.action == request.action, "action_binding_mismatch"),
            (challenge.principal == request.principal, "principal_binding_mismatch"),
            (
                _material_digest(challenge.normalized_diff) == challenge.args_digest,
                "challenge_args_digest_mismatch",
            ),
            (decision.resolution == "approved", "approval_rejected"),
            (decision.approval_id == challenge.approval_id, "approval_id_mismatch"),
            (decision.expires_at == challenge.expires_at, "expiry_binding_mismatch"),
            (now < challenge.expires_at, "approval_expired"),
            (decision.args_digest == challenge.args_digest, "decision_args_digest_mismatch"),
            (_material_digest(expected_material) == challenge.args_digest,
             "resumed_args_digest_mismatch"),
            (
                decision.descriptor_digest == challenge.descriptor_digest,
                "decision_descriptor_mismatch",
            ),
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
        for envelope in events:
            payload = envelope.payload
            kind = payload.get("kind")
            if kind == "ApprovalRequested":
                challenge_data = (
                    payload.get("challenge")
                    if isinstance(payload.get("challenge"), Mapping)
                    else payload
                )
                try:
                    requested = ApprovalChallenge(
                        approval_id=str(challenge_data["approvalId"]),
                        process_id=str(challenge_data.get("processId", process_id)),
                        action=str(challenge_data["action"]),
                        normalized_diff=str(challenge_data["normalizedDiff"]),
                        args_digest=str(challenge_data["argsDigest"]),
                        descriptor_digest=str(challenge_data["descriptorDigest"]),
                        principal=str(challenge_data["principal"]),
                        expires_at=str(challenge_data["expiresAt"]),
                    )
                except KeyError:
                    requested = None
                    continue
            elif kind == "ApprovalResolved" and requested is not None:
                decision_data = (
                    payload.get("decision")
                    if isinstance(payload.get("decision"), Mapping)
                    else payload
                )
                try:
                    decision = ApprovalDecision(
                        approval_id=str(decision_data["approvalId"]),
                        resolution=str(decision_data["resolution"]),
                        reviewer=str(decision_data["reviewer"]),
                        args_digest=str(decision_data["argsDigest"]),
                        descriptor_digest=str(decision_data["descriptorDigest"]),
                        expires_at=str(decision_data["expiresAt"]),
                        signature=str(decision_data["signature"]),
                        key_id=str(decision_data.get("keyId", "operator-key-default")),
                    )
                except KeyError:
                    continue
                if requested.approval_id == suspension.token_id:
                    return self.verify(requested, decision, request, now=now)
        return _denied(
            ApprovalChallenge(
                approval_id=suspension.token_id,
                process_id=process_id,
                action=request.action,
                normalized_diff="",
                args_digest="",
                descriptor_digest=suspension.descriptor_digest,
                principal=request.principal,
                expires_at="",
            ),
            "no_approval_decision_in_ledger",
        )


class DescriptorBoundApprovalPolicy:
    """Wraps an existing policy and admits the exact pre-approved request."""

    def __init__(
        self,
        base_policy: Any,
        authorization: ApprovalAuthorization,
    ) -> None:
        self._base = base_policy
        self._auth = authorization

    def authorize(
        self,
        request: EffectRequest,
        *,
        widens_capability: bool,
        requested_scope: Any,
        spans: Sequence[Span] | None = None,
    ) -> Decision:
        decision: Decision = self._base.authorize(
            request,
            widens_capability=widens_capability,
            requested_scope=requested_scope,
            spans=spans,
        )
        if not self._auth.approved:
            return Decision(
                outcome=Outcome.REJECT,
                failure=FailurePath.DENIED_REJECT,
                reason=f"approval_denied: {self._auth.reason}",
            )
        if decision.outcome != Outcome.REQUIRE_APPROVAL:
            return decision
        target_descriptor = descriptor_of(request.action, request.args)
        if target_descriptor == self._auth.descriptor_digest:
            return Decision(
                outcome=Outcome.ALLOW,
                failure=None,
                reason="descriptor_bound_approval_verified",
                granted_scope=decision.granted_scope,
            )
        return Decision(
            outcome=Outcome.REJECT,
            failure=FailurePath.DENIED_REJECT,
            reason="descriptor_mismatch",
        )


def normalise_unified_diff(diff: str) -> str:
    """Canonicalize a unified diff for unambiguous human display and signing."""
    if not isinstance(diff, str) or not diff.strip():
        raise ApprovalFormatError("unified diff must be non-empty string")
    lines = diff.splitlines()
    if not lines:
        raise ApprovalFormatError("empty diff lines")
    has_header = False
    for line in lines:
        if line.startswith(("--- ", "+++ ", "@@ ")):
            has_header = True
            break
    if not has_header:
        raise ApprovalFormatError("diff must contain unified diff headers")
    normalized_lines = [line.rstrip("\r\n") for line in lines]
    return "\n".join(normalized_lines) + "\n"


def _diff_from(request: EffectRequest) -> str:
    diff = request.args.get("diff") or request.args.get("patch")
    if not isinstance(diff, str):
        raise ApprovalFormatError("privileged patch request must supply diff or patch argument")
    return normalise_unified_diff(diff)


def _material_digest(normalized_diff: str) -> str:
    return digest_of({"normalizedDiff": normalized_diff})


def _request_material(request: EffectRequest) -> str:
    """Canonical human-review material for non-patch privileged effects."""
    try:
        return json.dumps(
            {"action": request.action, "args": dict(request.args)},
            sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        )
    except (TypeError, ValueError) as exc:
        raise ApprovalFormatError("privileged request arguments are not JSON data") from exc


def _denied(challenge: ApprovalChallenge, reason: str) -> ApprovalAuthorization:
    return ApprovalAuthorization(
        approved=False,
        reason=reason,
        approval_id=challenge.approval_id,
        args_digest=challenge.args_digest,
        descriptor_digest=challenge.descriptor_digest,
    )
