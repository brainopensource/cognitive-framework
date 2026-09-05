"""WorkspaceEpoch: frozen bind of tree, index snapshot, revision, and turn.

Law names: treeHash, indexDigest, sourceRevision, compiledAtTurn.
Python fields are the snake_case mapping of those four names.
Stdlib + RFC 8785 JCS only. No I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .canonicalisation.digest import digest_of

__all__ = ["WorkspaceEpoch"]


@dataclass(frozen=True, slots=True)
class WorkspaceEpoch:
    """Bind a packet to one workspace snapshot.

    Mapping: ``tree_hash`` ← treeHash, ``index_digest`` ← indexDigest,
    ``source_revision`` ← sourceRevision, ``compiled_at_turn`` ← compiledAtTurn.
    """

    tree_hash: str
    index_digest: str
    source_revision: str
    compiled_at_turn: int

    def __post_init__(self) -> None:
        if not self.tree_hash or not self.index_digest or not self.source_revision:
            raise ValueError("WorkspaceEpoch requires tree_hash, index_digest, and source_revision")
        if self.compiled_at_turn < 0:
            raise ValueError("compiled_at_turn must be non-negative")

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "treeHash": self.tree_hash,
            "indexDigest": self.index_digest,
            "sourceRevision": self.source_revision,
            "compiledAtTurn": self.compiled_at_turn,
        }

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "WorkspaceEpoch":
        return cls(
            tree_hash=str(raw.get("treeHash", raw.get("tree_hash", "")) or ""),
            index_digest=str(raw.get("indexDigest", raw.get("index_digest", "")) or ""),
            source_revision=str(raw.get("sourceRevision", raw.get("source_revision", "")) or ""),
            compiled_at_turn=int(raw.get("compiledAtTurn", raw.get("compiled_at_turn", 0)) or 0),
        )
