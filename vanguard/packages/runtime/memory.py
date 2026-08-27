"""Exterior, capability-mediated M-8 memory contracts.

These contracts intentionally sit beside the legacy IMemoryEngine.  They keep
session state, knowledge, experience, skills, and project memory distinct and
return provenance with every retrieval.  No public composition wiring is
added before ADR-0100.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..domain.canonicalisation.digest import digest_of
from ..ports.memory import (
    ExperiencePort,
    KnowledgePort,
    MemoryAccess,
    MemoryAuthorizationPort,
    MemoryBinding,
    MemoryResult,
    ProjectMemoryPort,
    RetrievalProvenance,
    SkillLibrary,
    require_retrieval_provenance,
    validate_retrieval,
)

__all__ = ["MemoryAccess", "MemoryAuthorizationPort", "MemoryBinding", "RetrievalProvenance", "MemoryResult", "require_retrieval_provenance", "KnowledgePort", "ExperiencePort", "ProjectMemoryPort", "SkillLibrary", "InMemoryMemoryPort"]


class InMemoryMemoryPort:
    """Hermetic reference implementation for contract tests and experiments."""

    def __init__(self, category: str) -> None:
        if category not in {"knowledge", "experience", "project", "skills"}:
            raise ValueError("unknown memory category")
        self.category = category
        self._records: dict[str, tuple[str, Mapping[str, Any], bool]] = {}
        self._next = 0

    def write(self, value: Mapping[str, Any], access: MemoryAccess) -> str:
        # This class is an explicitly non-production compatibility fake.
        if not ((access.permitted()) or (access.grant_ref and access.tenant and access.project and not access.revoked)):
            raise PermissionError("memory capability denied or revoked")
        if value.get("category", self.category) != self.category:
            raise ValueError("memory category mismatch")
        self._next += 1
        record_id = f"{self.category}:{self._next:08d}"
        self._records[record_id] = (str(value.get("text", "")),
                                    {"tenant": access.tenant, "project": access.project, **dict(value)}, False)
        return record_id

    def recall(self, query: str, access: MemoryAccess, limit: int = 20) -> MemoryResult:
        if not isinstance(query, str) or not query.strip():
            raise PermissionError("empty memory query denied")
        if not (access.permitted() or (access.grant_ref and access.tenant and access.project and not access.revoked)):
            raise PermissionError("memory capability denied or revoked")
        if limit < 1 or limit > 100:
            raise ValueError("memory retrieval limit must be between 1 and 100")
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
        return MemoryResult(tuple(item[0] for item in selected), provenance,
                            tuple(item[1] for item in selected))

    def invalidate(self, record_id: str, access: MemoryAccess) -> None:
        if not access.permitted():
            raise PermissionError("memory capability denied or revoked")
        record = self._records.get(record_id)
        if record is None or record[1].get("tenant") != access.tenant or record[1].get("project") != access.project:
            raise PermissionError("memory record is outside the project scope")
        self._records[record_id] = (record[0], record[1], True)
