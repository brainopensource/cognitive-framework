"""CMX-06 localizer role: bounded repository-index composition layer."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of

READ_ONLY_TOOLS = ("fs.read", "fs.search")
MAX_HITS = 20
ROLE_ID = "localizer"


def localize(
    artifact_writer: Any, *, task_digest: str, snapshot_digest: str,
    ranked_hits: Sequence[Mapping[str, Any]],
) -> Any:
    """Emit at most twenty ranked file references, never file contents."""
    if not task_digest or not snapshot_digest:
        raise ValueError("localizer requires task and snapshot digests")
    if len(ranked_hits) > MAX_HITS:
        raise ValueError(f"localizer output exceeds {MAX_HITS} entries")
    hits = []
    for hit in ranked_hits:
        if not isinstance(hit, Mapping) or not isinstance(hit.get("path"), str):
            raise ValueError("localizer hits require a file path")
        hits.append({"path": hit["path"], "score": float(hit.get("score", 0.0))})
    payload = {"schema": "cmx06.localizer-hits/1", "taskDigest": task_digest,
               "snapshotDigest": snapshot_digest, "hits": hits,
               "resultDigest": digest_of({"taskDigest": task_digest,
                                           "snapshotDigest": snapshot_digest,
                                           "hits": hits})}
    return artifact_writer.capture("context_bundle", payload, required=True)


def contract() -> Mapping[str, Any]:
    return {"role": ROLE_ID, "tools": READ_ONLY_TOOLS, "writes": False,
            "input": ("task-digest", "snapshot-digest"), "maxEntries": MAX_HITS,
            "output": "context_bundle"}
