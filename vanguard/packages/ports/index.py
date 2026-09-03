"""Repository index: symbols and files as observations (`S10-A-03`).

Owning contract: `VG-03 §7`, `ICD §4`.

This is the slot a repo-map occupies. It is an **observation** source and
nothing more: the index answers "what is in this workspace" and the episode
decides what to do about it. It is explicitly not a second loop -- it proposes
nothing, ranks nothing on the agent's behalf, and holds no authority. A
retrieval component that decided what the agent should look at next would be a
second policy wearing the word "index" (`A-05`, `AT-01`).

Results are values, never handles: a caller cannot reach back through a symbol
into the indexer's state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence, runtime_checkable

from .event_store import Result

__all__ = ["DependencyEdge", "IndexPort", "RepositoryMap", "Symbol", "TestAssociation"]


@dataclass(frozen=True, slots=True)
class Symbol:
    """One named thing at one place. Value-only.

    `kind` is an open string rather than an enum: languages disagree about what
    a definition is, and an enum here would make adding a language a change to
    this port instead of a change to an indexer.
    """

    name: str
    kind: str
    path: str
    line: int


@dataclass(frozen=True, slots=True)
class DependencyEdge:
    """A normalized, value-only import/dependency observation."""

    source: str
    target: str
    kind: str = "import"


@dataclass(frozen=True, slots=True)
class TestAssociation:
    """A value-only association between a test and an affected source file."""

    test_path: str
    source_path: str


@dataclass(frozen=True, slots=True)
class RepositoryMap:
    """Bounded repository summary with explicit provenance and truncation."""

    files: tuple[str, ...]
    symbols: tuple[Symbol, ...]
    dependencies: tuple[DependencyEdge, ...]
    tests: tuple[TestAssociation, ...]
    adapter_id: str
    source_revision: str
    generated_at_source: str = "deterministic-index"
    truncated: bool = False
    token_estimate: int = 0
    tree_hash: str = ""
    index_digest: str = ""


@runtime_checkable
class IndexPort(Protocol):
    """What is in the workspace, as observations."""

    def index(self, root: str) -> Result[int]:
        """(Re)build the index for `root`. Returns the file count indexed."""

    def files(self, *, prefix: str = "") -> Result[Sequence[str]]:
        """Workspace-relative paths, sorted, optionally filtered by prefix."""

    def symbols(self, *, name: str = "", path: str = "") -> Result[Sequence[Symbol]]:
        """Definitions matching `name` and/or `path`. Empty is not a failure."""

    def dependencies(self, *, path: str = "") -> Result[Sequence[DependencyEdge]]:
        """Normalized import/dependency edges, optionally for one source path."""

    def tests(self, *, path: str = "") -> Result[Sequence[TestAssociation]]:
        """Test-to-source associations, optionally for one source path."""

    def repo_map(self, *, token_budget: int = 4000) -> Result[RepositoryMap]:
        """Return a bounded, attributable repository summary."""
