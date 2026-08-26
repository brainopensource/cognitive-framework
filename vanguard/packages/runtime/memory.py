"""Exterior, capability-mediated M-8 memory contracts.

These contracts intentionally sit beside the legacy IMemoryEngine.  They keep
session state, knowledge, experience, skills, and project memory distinct and
return provenance with every retrieval.  No public composition wiring is
added before ADR-0100.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

from ..domain.canonicalisation.digest import digest_of

__all__ = ["MemoryAccess", "RetrievalProvenance", "MemoryResult", "KnowledgePort", "ExperiencePort", "ProjectMemoryPort", "SkillLibrary", "InMemoryMemoryPort"]


@dataclass(frozen=True, slots=True)
class MemoryAccess:
    grant_ref: str
    selector: Mapping[str, Any]
    tenant: str
    project: str
    revoked: bool = False

    def permitted(self) -> bool:
        return bool(self.grant_ref and self.tenant and self.project and not self.revoked)


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


class _MemoryPort(Protocol):
    category: str
    def recall(self, query: str, access: MemoryAccess, limit: int = 20) -> MemoryResult: ...
    def write(self, value: Mapping[str, Any], access: MemoryAccess) -> str: ...


class KnowledgePort(_MemoryPort, Protocol): category: str = "knowledge"
class ExperiencePort(_MemoryPort, Protocol): category: str = "experience"
class ProjectMemoryPort(_MemoryPort, Protocol): category: str = "project"
class SkillLibrary(_MemoryPort, Protocol): category: str = "skills"


def validate_retrieval(query: str, access: MemoryAccess, limit: int) -> None:
    if not isinstance(query, str) or not query.strip():
        raise PermissionError("empty memory query denied")
    if not access.permitted():
        raise PermissionError("memory capability denied or revoked")
    if limit < 1 or limit > 100:
        raise ValueError("memory retrieval limit must be between 1 and 100")


class InMemoryMemoryPort:
    """Hermetic reference implementation for contract tests and experiments."""

    def __init__(self, category: str) -> None:
        if category not in {"knowledge", "experience", "project", "skills"}:
            raise ValueError("unknown memory category")
        self.category = category
        self._records: dict[str, tuple[str, Mapping[str, Any], bool]] = {}
        self._next = 0

    def write(self, value: Mapping[str, Any], access: MemoryAccess) -> str:
        if not access.permitted():
            raise PermissionError("memory capability denied or revoked")
        if value.get("category", self.category) != self.category:
            raise ValueError("memory category mismatch")
        self._next += 1
        record_id = f"{self.category}:{self._next:08d}"
        self._records[record_id] = (str(value.get("text", "")),
                                    {"tenant": access.tenant, "project": access.project, **dict(value)}, False)
        return record_id

    def recall(self, query: str, access: MemoryAccess, limit: int = 20) -> MemoryResult:
        validate_retrieval(query, access, limit)
        matches = [(rid, text, metadata) for rid, (text, metadata, invalidated) in self._records.items()
                   if not invalidated and metadata.get("tenant") == access.tenant
                   and metadata.get("project") == access.project and query.lower() in text.lower()]
        matches.sort(key=lambda item: item[0])
        selected = matches[:limit]
        dropped = matches[limit:]
        sources = tuple(digest_of({"id": rid, "text": text, "metadata": dict(metadata)}) for rid, text, metadata in matches)
        provenance = RetrievalProvenance(digest_of({"query": query, "category": self.category,
                                                     "tenant": access.tenant, "project": access.project}),
                                         "m8-reference-policy/1", sources,
                                         tuple(item[0] for item in selected), tuple(item[0] for item in dropped),
                                         None, None, False)
        return MemoryResult(tuple(item[0] for item in selected), provenance)

    def invalidate(self, record_id: str, access: MemoryAccess) -> None:
        if not access.permitted():
            raise PermissionError("memory capability denied or revoked")
        record = self._records.get(record_id)
        if record is None or record[1].get("tenant") != access.tenant or record[1].get("project") != access.project:
            raise PermissionError("memory record is outside the project scope")
        self._records[record_id] = (record[0], record[1], True)
