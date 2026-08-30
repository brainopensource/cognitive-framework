"""Provider-neutral bounded repository context values (W-092-3, TC-E-055/056)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of

__all__ = ["ContextPacket", "ContextPacketError", "build_context_packet"]


class ContextPacketError(ValueError):
    """A context packet cannot satisfy its identity or budget contract."""


@dataclass(frozen=True, slots=True)
class ContextPacket:
    task_digest: str
    repository_snapshot: str
    provider: str
    provider_version: str
    index_snapshot_digest: str | None
    query_digest: str
    documents: tuple[Mapping[str, Any], ...] = ()
    symbols: tuple[Mapping[str, Any], ...] = ()
    files: tuple[str, ...] = ()
    dependencies: tuple[Mapping[str, Any], ...] = ()
    tests: tuple[str, ...] = ()
    estimated_tokens: int = 0
    omissions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.estimated_tokens < 0:
            raise ContextPacketError("estimated_tokens must be non-negative")
        for name in ("task_digest", "repository_snapshot", "provider", "provider_version", "query_digest"):
            if not getattr(self, name):
                raise ContextPacketError(f"{name} is required")

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "taskDigest": self.task_digest,
            "repositorySnapshot": self.repository_snapshot,
            "provider": self.provider,
            "providerVersion": self.provider_version,
            "indexSnapshotDigest": self.index_snapshot_digest,
            "queryDigest": self.query_digest,
            "documents": [dict(v) for v in self.documents],
            "symbols": [dict(v) for v in self.symbols],
            "files": list(self.files),
            "dependencies": [dict(v) for v in self.dependencies],
            "tests": list(self.tests),
            "estimatedTokens": self.estimated_tokens,
            "omissions": list(self.omissions),
        }

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())


def build_context_packet(
    *,
    task_digest: str,
    repository_snapshot: str,
    provider: str,
    provider_version: str,
    query_digest: str,
    budget_tokens: int,
    selected: Sequence[Mapping[str, Any]] = (),
    index_snapshot_digest: str | None = None,
    reserve_tokens: int = 1,
) -> ContextPacket:
    """Build a bounded packet, retaining explicit omissions and reserve."""
    if budget_tokens < 0 or reserve_tokens < 0 or reserve_tokens > budget_tokens:
        raise ContextPacketError("invalid context budget or recovery reserve")
    usable = budget_tokens - reserve_tokens
    kept: list[Mapping[str, Any]] = []
    omissions: list[str] = []
    used = 0
    for item in selected:
        cost = item.get("estimated_tokens", item.get("tokens", 0))
        if isinstance(cost, bool) or not isinstance(cost, int) or cost < 0:
            raise ContextPacketError("selected item token estimate must be a non-negative integer")
        identity = str(item.get("identity") or item.get("path") or item.get("name") or "unknown")
        if used + cost > usable:
            omissions.append(identity)
            continue
        kept.append(dict(item))
        used += cost
    return ContextPacket(
        task_digest=task_digest,
        repository_snapshot=repository_snapshot,
        provider=provider,
        provider_version=provider_version,
        index_snapshot_digest=index_snapshot_digest,
        query_digest=query_digest,
        documents=tuple(v for v in kept if v.get("kind") == "document"),
        symbols=tuple(v for v in kept if v.get("kind") == "symbol"),
        files=tuple(str(v["path"]) for v in kept if v.get("kind") == "file" and "path" in v),
        dependencies=tuple(v for v in kept if v.get("kind") == "dependency"),
        tests=tuple(str(v["path"]) for v in kept if v.get("kind") == "test" and "path" in v),
        estimated_tokens=used,
        omissions=tuple(omissions),
    )
