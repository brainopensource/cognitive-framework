"""Capability grants: issuance, point-of-effect verification, revocation.

Grant *structure* is owned by `04 §5.2`; this module holds the kernel's
obligations over it (`05 §3`).

The load-bearing rule is `K-18` / `CT-51`: a grant carries `descriptorDigest`
and authorises **exactly that call**. S8 compares the descriptor recomputed at
S3 against it, and any mismatch is `F-14`. A grant without the field cannot be
issued — which is checked here, at issuance, so that no code path downstream
has to remember to look. `MF-KRN-003` fails against a grant that omits or
bypasses the binding; `MF-KRN-005` against a forged, replayed or expired one.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, replace
from typing import Any, Mapping

from ..domain.canonicalisation.digest import digest_of
from ..domain.canonicalisation.jcs import canonicalise
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
    """`K-18`: a grant that binds no descriptor cannot be issued.

    Refusing at issuance rather than at use is deliberate. `05 [K-18]` says the
    point-of-effect check has nothing to compare without this field, and
    `ADR-0039` records that its absence stayed invisible for exactly as long as
    nothing refused to construct the object.
    """


def descriptor_of(action: str, args: Mapping[str, Any]) -> str:
    """S3 DESCRIBE — `digest(canonical(name, normalisedArgs))` (`04 §5.5`).

    `D-3`: the provider-assigned call identifier is excluded, because it
    differs between otherwise identical calls. `D-5`: absent optional
    arguments are omitted rather than sent as null, so presence-with-null and
    absence cannot produce two digests for one call.
    """
    normalised = {
        key: value for key, value in args.items()
        if value is not None and key not in ("toolCallId", "callId", "requestId")
    }
    return digest_of({"action": action, "args": normalised})


@dataclass(frozen=True, slots=True)
class Grant:
    """One grant, authorising one call (`CT-51`)."""

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
        """The bytes an authenticator covers: the grant's full contents
        (`K-20`), canonicalised so two processes agree on them (`SC-2`)."""
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
    """`K-20`. A grant crossing a process boundary carries a MAC over its full
    contents; an in-process grant may remain an opaque reference."""

    def __init__(self, key: bytes) -> None:
        self._key = key

    def sign(self, payload: Mapping[str, Any]) -> str:
        return hmac.new(self._key, canonicalise(payload).encode("utf-8"),
                        hashlib.sha256).hexdigest()

    def verify(self, payload: Mapping[str, Any], authenticator: str) -> bool:
        return hmac.compare_digest(self.sign(payload), authenticator or "")


@dataclass(frozen=True, slots=True)
class GrantVerification:
    """S8's answer. `ok` is only true when every check passed."""

    ok: bool
    failure: FailurePath | None = None
    detail: str = ""


class GrantIssuer:
    """S6 GRANT and S8 VERIFY, plus revocation (`K-49`).

    Consumption and revocation state live here rather than on the grant: a
    frozen value that knows whether it has been spent is a value that can be
    copied into a fresh, unspent one.
    """

    def __init__(self, authenticator: HmacAuthenticator | None = None) -> None:
        self._authenticator = authenticator
        self._id_counter = 0
        self._consumed: set[str] = set()
        self._revoked: set[str] = set()
        self._children: dict[str, set[str]] = {}
        self._issued: dict[str, Grant] = {}

    def next_grant_id(self) -> str:
        """Return an issuer-unique id across kernel instances.

        Runtime approval resumption creates a fresh Kernel while retaining the
        issuer state. IDs must therefore be owned by the issuer, not by each
        short-lived dispatch facade, or the resumed grant can replay the first
        grant's identifier.
        """
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
            # Purpose is the brief the effect serves; descriptor is the exact
            # call. `CT-51` is explicit that they are different fields.
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
        """S8 VERIFY, at the point of effect — not at issuance (`K-05`)."""
        if cross_process or grant.authenticator is not None:
            # `F-17`, alertable: a forged authenticator is an attack, not a bug.
            if self._authenticator is None or not self._authenticator.verify(
                    grant.payload(), grant.authenticator or ""):
                return GrantVerification(False, FailurePath.GRANT_FORGED,
                                         "authenticator invalid across a process boundary")
        if grant.grant_id in self._revoked:
            return GrantVerification(False, FailurePath.GRANT_REPLAY, "grant revoked")
        if grant.descriptor_digest != descriptor_digest:
            # `F-14`. This is the descriptor-substitution defence: approve A,
            # mutate the arguments to B, and B is rejected here.
            return GrantVerification(False, FailurePath.GRANT_MISMATCH,
                                     f"grant binds {grant.descriptor_digest}, "
                                     f"call is {descriptor_digest}")
        if now >= grant.expires_at:
            # Timestamps are lexicographically ordered by `CT-08`, so string
            # comparison is instant comparison here.
            return GrantVerification(False, FailurePath.GRANT_EXPIRED,
                                     f"expired at {grant.expires_at}")
        if grant.single_use and grant.grant_id in self._consumed:
            return GrantVerification(False, FailurePath.GRANT_REPLAY, "grant already consumed")
        return GrantVerification(True)

    def consume(self, grant: Grant) -> None:
        """`K-19`: single use whenever the effect has no safe idempotency key."""
        if grant.single_use:
            self._consumed.add(grant.grant_id)

    def revoke(self, grant_id: str) -> tuple[str, ...]:
        """`K-49`: immediate, transitive over descendants, and it emits.

        Returns every revoked identifier so the caller can emit one
        `CapabilityRevoked` per grant — a revocation leaving no event is
        indistinguishable from a grant that was never issued.
        """
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
