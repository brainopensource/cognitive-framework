"""CMX-06 reviewer role: advisory, read-only, digest-addressed."""

from __future__ import annotations

import json
from typing import Any, Mapping

from ...domain.canonicalisation.digest import digest_of

READ_ONLY_TOOLS = ("fs.read", "fs.search")
ROLE_ID = "reviewer"


def review_diff(
    blobs: Any, artifact_writer: Any, diff_digest: str, *,
    approved: bool, findings: list[str] | tuple[str, ...] = (),
) -> Any:
    """Read an implementer's diff by digest and emit an advisory verdict.

    The diff bytes are deliberately never returned or copied into the verdict.
    A verifier may consume the verdict as context, but its approval has no
    authority over verification or admission.
    """
    if not isinstance(diff_digest, str) or not diff_digest.startswith("sha256:"):
        raise ValueError("reviewer requires a content-addressed diff digest")
    fetched = blobs.get(diff_digest)
    if not getattr(fetched, "ok", False) or fetched.value is None:
        raise ValueError("reviewer diff artifact is unavailable")
    if not isinstance(approved, bool):
        raise TypeError("review approval must be boolean")
    clean_findings = [str(item) for item in findings]
    payload = {
        "schema": "cmx06.reviewer-verdict/1",
        "approved": approved,
        "findings": clean_findings,
        "diffDigest": diff_digest,
        "verdictDigest": digest_of({"approved": approved, "findings": clean_findings,
                                    "diffDigest": diff_digest}),
    }
    return artifact_writer.capture("verification_report", payload, required=True)


def contract() -> Mapping[str, Any]:
    return {"role": ROLE_ID, "tools": READ_ONLY_TOOLS,
            "writes": False, "downstreamAuthority": "verifier",
            "input": "artifact-digest", "output": "verification_report"}
