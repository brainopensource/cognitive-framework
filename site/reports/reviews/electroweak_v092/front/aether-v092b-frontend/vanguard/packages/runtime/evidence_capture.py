"""What one run actually captured, for the `mhf.trajectory/2` writer (EVO-06).

Extracted from `HarnessSession._capture_evidence`: a pure function of the
artifact writer and provenance sink a session already holds, with no other
session state involved. Kept duck-typed (`Any`) rather than importing
`ArtifactWriter`/`RuntimeProvenanceSink` concretely -- `provenance.py`
already imports from `artifacts.py`, and a concrete import here in the
other direction would cycle.
"""

from __future__ import annotations

from typing import Any

__all__ = ["capture_evidence"]


def capture_evidence(artifacts: Any, provenance: Any) -> dict[str, Any]:
    """Empty on the legacy path, and deliberately so.

    `assemble_trajectory` renders an absent artifact index and a null
    capture status rather than synthesising a complete one, so a run that
    captured nothing says that instead of claiming it captured everything
    it was asked to.
    """
    if artifacts is None:
        return {}
    trajectory_provenance = provenance.trajectory_provenance()
    return {
        "artifact_index": list(artifacts.index_entries()),
        "context_provenance": trajectory_provenance["context"],
        "compaction_provenance": trajectory_provenance["compaction"],
        "cache_provenance": trajectory_provenance["cache"],
        "capture_status": artifacts.capture_state(),
    }
