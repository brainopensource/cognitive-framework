"""Capability grants: issuance, point-of-effect verification, revocation."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, replace
from typing import Any, Mapping

from layer0.events.canonical import canonicalise, digest_of
from .attenuation import Scope
from .model import FailurePath

__all__ = [
    "Grant",
    "GrantIssuer",
    "GrantVerification",
    "HmacAuthenticator",
    "MissingDescriptorBinding",
    "descriptor_of",
]


class MissingDescriptorBinding(ValueError):
    """K-18: a grant that binds no descriptor cannot be issued."""


def descriptor_of(action: str, args: Mapping[str, Any]) -> str:
    normalised = {
        key: value for key, value in args.items()
        if value is not None and key not in ("toolCallId", "callId", "requestId")
    }
    return digest_of({"action": action, "args": normalised})


@dataclass(frozen=True, slots=True)
class Grant:
    grant_id: str
    principal: str
    descriptor_digest: str
    scope: Scope
    expires_at: str
    purpose_digest: str
    single_use: bool = True
    parent_grant_id: str | None = None
    authenticator: str | None = None
    approval_ref: str | None = None

    def payload(self) -> Mapping[str, Any]:
        return {
            "grantId": self.grant_id,
            "principal": self.principal,
            "descriptorDigest": self.descriptor_digest,
            "expiresAt": self.expires_at,
            "purposeDigest": self.purpose_digest,
            "singleUse": self.single_use,
            "parentGrantId": self.parent_grant_id,
            "actions": sorted(self.scope.actions),
            "resources": [dict(resource) for resource in self.scope.resources],
            "depth": self.scope.depth,
        }


class HmacAuthenticator:
    def __init__(self, key: bytes) -> None:
        self._key = key

    def sign(self, payload: Mapping[str, Any]) -> str:
        return hmac.new(self._key, canonicalise(payload).encode("utf-8"),
                        hashlib.sha256).hexdigest()

    def verify(self, payload: Mapping[str, Any], authenticator: str) -> bool:
        return hmac.compare_digest(self.sign(payload), authenticator or "")


@dataclass(frozen=True, slots=True)
class GrantVerification:
    ok: bool
    failure: FailurePath | None = None
    detail: str = ""


class GrantIssuer:
    def __init__(self, authenticator: HmacAuthenticator | None = None) -> None:
        self._authenticator = authenticator
        self._id_counter = 0
        self._consumed: set[str] = set()
        self._revoked: set[str] = set()
        self._children: dict[str, set[str]] = {}
        self._issued: dict[str, Grant] = {}

    def next_grant_id(self) -> str:
        self._id_counter += 1
        return f"grant-{self._id_counter}"

    def issue(
        self,
        *,
        grant_id: str,
        principal: str,
        descriptor_digest: str,
        scope: Scope,
        expires_at: str,
        purpose_digest: str,
        single_use: bool = True,
        parent_grant_id: str | None = None,
        cross_process: bool = False,
        approval_ref: str | None = None,
    ) -> Grant:
        if not descriptor_digest:
            raise MissingDescriptorBinding(
                "K-18/CT-51: a grant must bind the descriptor of the one call it "
                "authorises; point-of-effect verification has nothing to compare without it")
        if not purpose_digest:
            raise MissingDescriptorBinding("K-18/CT-51: purposeDigest is required and is "
                                           "not the descriptor binding")
        grant = Grant(
            grant_id=grant_id,
            principal=principal,
            descriptor_digest=descriptor_digest,
            scope=scope,
            expires_at=expires_at,
            purpose_digest=purpose_digest,
            single_use=single_use,
            parent_grant_id=parent_grant_id,
            approval_ref=approval_ref,
        )
        if cross_process:
            if self._authenticator is None:
                raise MissingDescriptorBinding(
                    "K-20: a grant crossing a process boundary requires an authenticator")
            grant = replace(grant, authenticator=self._authenticator.sign(grant.payload()))
        self._issued[grant_id] = grant
        if parent_grant_id is not None:
            self._children.setdefault(parent_grant_id, set()).add(grant_id)
        return grant

    def verify(
        self,
        grant: Grant,
        *,
        descriptor_digest: str,
        now: str,
        cross_process: bool = False,
    ) -> GrantVerification:
        if cross_process or grant.authenticator is not None:
            if self._authenticator is None or not self._authenticator.verify(
                    grant.payload(), grant.authenticator or ""):
                return GrantVerification(False, FailurePath.GRANT_FORGED,
                                         "authenticator invalid across a process boundary")
        if grant.grant_id in self._revoked:
            return GrantVerification(False, FailurePath.GRANT_REPLAY, "grant revoked")
        if grant.descriptor_digest != descriptor_digest:
            return GrantVerification(False, FailurePath.GRANT_MISMATCH,
                                     f"grant binds {grant.descriptor_digest}, "
                                     f"call is {descriptor_digest}")
        if now >= grant.expires_at:
            return GrantVerification(False, FailurePath.GRANT_EXPIRED,
                                     f"expired at {grant.expires_at}")
        if grant.single_use and grant.grant_id in self._consumed:
            return GrantVerification(False, FailurePath.GRANT_REPLAY, "grant already consumed")
        return GrantVerification(True)

    def consume(self, grant: Grant) -> None:
        if grant.single_use:
            self._consumed.add(grant.grant_id)

    def revoke(self, grant_id: str) -> tuple[str, ...]:
        revoked: list[str] = []
        frontier = [grant_id]
        while frontier:
            current = frontier.pop()
            if current in self._revoked:
                continue
            self._revoked.add(current)
            revoked.append(current)
            frontier.extend(self._children.get(current, ()))
        return tuple(revoked)

    def is_revoked(self, grant_id: str) -> bool:
        return grant_id in self._revoked

    def issued(self) -> Mapping[str, Grant]:
        return dict(self._issued)
