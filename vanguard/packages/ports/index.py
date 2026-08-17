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

__all__ = ["IndexPort", "Symbol"]


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


@runtime_checkable
class IndexPort(Protocol):
    """What is in the workspace, as observations."""

    def index(self, root: str) -> Result[int]:
        """(Re)build the index for `root`. Returns the file count indexed."""

    def files(self, *, prefix: str = "") -> Result[Sequence[str]]:
        """Workspace-relative paths, sorted, optionally filtered by prefix."""

    def symbols(self, *, name: str = "", path: str = "") -> Result[Sequence[Symbol]]:
        """Definitions matching `name` and/or `path`. Empty is not a failure."""
