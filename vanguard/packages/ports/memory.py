"""Capability-mediated memory value contracts shared by Runtime and adapters."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
from typing import Any, Mapping, Protocol

from ..domain.canonicalisation.digest import digest_of

__all__ = [
    "MemoryAccess",
    "MemoryAuthorizationPort",
    "MemoryResult",
    "RetrievalProvenance",
    "require_retrieval_provenance",
    "KnowledgePort",
    "ExperiencePort",
    "ProjectMemoryPort",
    "SkillLibrary",
    "validate_retrieval",
]


@dataclass(frozen=True, slots=True)
class MemoryAccess:
    grant_ref: str
    selector: Mapping[str, Any]
    tenant: str
    project: str
    revoked: bool = False
    issuer: str = ""
    subject: str = ""
    actions: tuple[str, ...] = ()
    purpose: str = ""
    expires_at: str = ""
    revocation_epoch: int = 0
    verification_receipt: str = ""

    def permitted(self) -> bool:
        if not (self.grant_ref and self.tenant and self.project and self.issuer and self.subject):
            return False
        if self.revoked or not self.verification_receipt or not self.actions:
            return False
        if not self.expires_at:
            return False
        try:
            expiry = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
            if expiry <= datetime.now(timezone.utc):
                return False
        except ValueError:
            return False
        return True


class MemoryAuthorizationPort:
    """Verify signed, scoped memory leases at the point of use."""

    def __init__(self, key: bytes, *, revoked_epochs: Mapping[str, int] | None = None) -> None:
        if not isinstance(key, bytes) or not key:
            raise ValueError("memory authorization key is required")
        self._key = key
        self._revoked_epochs = dict(revoked_epochs or {})

    def verify(self, grant: Mapping[str, Any], signature: str, *, action: str,
               tenant: str, project: str, selector: Mapping[str, Any],
               now: datetime | None = None) -> MemoryAccess:
        required = ("grantRef", "issuer", "subject", "tenant", "project", "actions",
                    "purpose", "expiresAt", "revocationEpoch", "selector")
        if any(not grant.get(name) and name != "revocationEpoch" for name in required):
            raise PermissionError("memory authorization is incomplete")
        payload = {key: grant[key] for key in required}
        expected = hmac.new(self._key, digest_of(payload).encode("ascii"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature or ""):
            raise PermissionError("memory authorization signature invalid")
        actions = tuple(str(item) for item in grant["actions"])
        if (action not in actions or grant["tenant"] != tenant or grant["project"] != project
                or dict(grant["selector"]) != dict(selector)):
            raise PermissionError("memory authorization scope denied")
        epoch = int(grant["revocationEpoch"])
        if epoch <= int(self._revoked_epochs.get(str(grant["grantRef"]), -1)):
            raise PermissionError("memory authorization revoked")
        access = MemoryAccess(
            grant_ref=str(grant["grantRef"]), selector=dict(selector), tenant=tenant,
            project=project, issuer=str(grant["issuer"]), subject=str(grant["subject"]),
            actions=actions, purpose=str(grant["purpose"]), expires_at=str(grant["expiresAt"]),
            revocation_epoch=epoch,
            verification_receipt=digest_of({"grant": payload, "signature": signature}),
        )
        if now is not None:
            try:
                expiry = datetime.fromisoformat(access.expires_at.replace("Z", "+00:00"))
                if expiry <= now.astimezone(timezone.utc):
                    raise PermissionError("memory authorization expired")
            except ValueError as exc:
                raise PermissionError("memory authorization expiry invalid") from exc
        if not access.permitted():
            raise PermissionError("memory authorization expired or invalid")
        return access

    def revoke(self, grant_ref: str, epoch: int) -> None:
        if not grant_ref or epoch < 0:
            raise ValueError("invalid revocation update")
        self._revoked_epochs[grant_ref] = max(epoch, self._revoked_epochs.get(grant_ref, -1))


@dataclass(frozen=True, slots=True)
class RetrievalProvenance:
    query_digest: str
    policy_identity: str
    source_record_digests: tuple[str, ...]
    selected_ids: tuple[str, ...]
    dropped_ids: tuple[str, ...]
    cache_identity: str | None
    context_selection_digest: str | None
    redacted: bool

    def digest(self) -> str:
        return digest_of({"query": self.query_digest, "policy": self.policy_identity,
                          "sources": self.source_record_digests, "selected": self.selected_ids,
                          "dropped": self.dropped_ids, "cache": self.cache_identity,
                          "context": self.context_selection_digest, "redacted": self.redacted})


@dataclass(frozen=True, slots=True)
class MemoryResult:
    record_ids: tuple[str, ...]
    provenance: RetrievalProvenance


def require_retrieval_provenance(result: MemoryResult) -> tuple[str, ...]:
    """Admit memory into model context only with a self-consistent receipt."""
    if not isinstance(result, MemoryResult) or not isinstance(result.provenance, RetrievalProvenance):
        raise PermissionError("memory context requires a retrieval provenance receipt")
    selected = tuple(result.provenance.selected_ids)
    if tuple(result.record_ids) != selected:
        raise PermissionError("memory records do not match retrieval receipt")
    if not result.provenance.policy_identity or not result.provenance.query_digest:
        raise PermissionError("memory retrieval receipt is incomplete")
    return selected


class _MemoryPort(Protocol):
    category: str

    def recall(self, query: str, access: MemoryAccess, limit: int = 20) -> MemoryResult: ...

    def write(self, value: Mapping[str, Any], access: MemoryAccess) -> str: ...


class KnowledgePort(_MemoryPort, Protocol):
    category: str = "knowledge"


class ExperiencePort(_MemoryPort, Protocol):
    category: str = "experience"


class ProjectMemoryPort(_MemoryPort, Protocol):
    category: str = "project"


class SkillLibrary(_MemoryPort, Protocol):
    category: str = "skills"


def validate_retrieval(query: str, access: MemoryAccess, limit: int) -> None:
    if not isinstance(query, str) or not query.strip():
        raise PermissionError("empty memory query denied")
    if not access.permitted():
        raise PermissionError("memory capability denied or revoked")
    if limit < 1 or limit > 100:
        raise ValueError("memory retrieval limit must be between 1 and 100")
