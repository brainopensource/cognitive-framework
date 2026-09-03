"""Provider-neutral bounded repository context values (W-092-3, TC-E-055/056)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of
from ...domain.workspace_epoch import WorkspaceEpoch

__all__ = ["ContextPacket", "ContextPacketError", "build_context_packet",
           "validate_resume_identity", "validate_completion_epoch", "SectionAddress"]


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
    # Optional W2 identity fields preserve replay of legacy packets while
    # preventing them from being used for new capability claims.
    selection_policy_identity: Mapping[str, Any] | None = None
    repository_identity: str | None = None
    workspace_epoch: WorkspaceEpoch | None = None

    def __post_init__(self) -> None:
        if self.estimated_tokens < 0:
            raise ContextPacketError("estimated_tokens must be non-negative")
        for name in ("task_digest", "repository_snapshot", "provider", "provider_version", "query_digest"):
            if not getattr(self, name):
                raise ContextPacketError(f"{name} is required")

    def to_canonical_dict(self) -> dict[str, Any]:
        value = {
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
        if self.selection_policy_identity is not None:
            value["selectionPolicyIdentity"] = dict(self.selection_policy_identity)
        if self.repository_identity is not None:
            value["repositoryIdentity"] = self.repository_identity
        if self.workspace_epoch is not None:
            value["workspaceEpoch"] = self.workspace_epoch.to_canonical_dict()
        return value

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
    selection_policy_identity: Mapping[str, Any] | None = None,
    repository_identity: str | None = None,
    workspace_epoch: WorkspaceEpoch | None = None,
    require_epoch: bool = False,
) -> ContextPacket:
    """Build a bounded packet, retaining explicit omissions and reserve."""
    if budget_tokens < 0 or reserve_tokens < 0 or reserve_tokens > budget_tokens:
        raise ContextPacketError("invalid context budget or recovery reserve")
    if require_epoch and workspace_epoch is None:
        raise ContextPacketError("product compile requires WorkspaceEpoch")
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
        selection_policy_identity=(dict(selection_policy_identity)
                                   if selection_policy_identity is not None else None),
        repository_identity=repository_identity,
        workspace_epoch=workspace_epoch,
    )


@dataclass(frozen=True, slots=True)
class SectionAddress:
    """Stable identity for a bounded large-file retrieval section."""

    path: str
    offset: int
    limit: int
    preimage_digest: str

    def __post_init__(self) -> None:
        if not self.path or self.offset < 0 or self.limit <= 0 or not self.preimage_digest:
            raise ContextPacketError("section address requires path, positive range, and preimage")

    def to_dict(self) -> dict[str, Any]:
        return {"path": self.path, "offset": self.offset, "limit": self.limit,
                "preimageDigest": self.preimage_digest}

    def digest(self) -> str:
        return digest_of(self.to_dict())


def validate_resume_identity(
    packet: ContextPacket,
    *,
    repository_identity: str,
    index_snapshot_digest: str | None,
    selection_policy_identity: Mapping[str, Any] | None,
    workspace_epoch: WorkspaceEpoch | None = None,
) -> None:
    """Reject resume drift; legacy packets remain replayable but unclaimable."""
    if packet.repository_identity is not None and packet.repository_identity != repository_identity:
        raise ContextPacketError("repository identity drifted during resume")
    if packet.index_snapshot_digest != index_snapshot_digest:
        raise ContextPacketError("index snapshot drifted during resume")
    if packet.selection_policy_identity is not None and dict(packet.selection_policy_identity) != dict(selection_policy_identity or {}):
        raise ContextPacketError("selection policy drifted during resume")
    if packet.workspace_epoch is not None and workspace_epoch is not None and packet.workspace_epoch != workspace_epoch:
        raise ContextPacketError("workspace epoch drifted during resume")


def validate_completion_epoch(packet: ContextPacket, current: WorkspaceEpoch) -> None:
    """Stale or missing epoch MUST NOT justify completed."""
    if packet.workspace_epoch is None:
        raise ContextPacketError("legacy packet cannot admit completed")
    if packet.workspace_epoch != current:
        raise ContextPacketError("stale WorkspaceEpoch; refresh required")
