"""Filters out redundant file observations when artifact content is unchanged."""

from __future__ import annotations

import hashlib
from typing import Mapping


def filter_redundant_observation(
    file_path: str,
    content: str,
    observed_digests: Mapping[str, str],  # file_path -> sha256
) -> tuple[bool, str, str]:
    """Check if file content matches previously observed digest.

    Returns (is_duplicate, digest, feedback_text).
    """
    digest = f"sha256:{hashlib.sha256(content.encode('utf-8')).hexdigest()}"
    prev_digest = observed_digests.get(file_path)
    if prev_digest == digest:
        return True, digest, f"[File '{file_path}' unchanged (digest: {digest[:16]}...)]"
    return False, digest, content
