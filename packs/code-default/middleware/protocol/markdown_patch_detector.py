"""Detects unified diffs or patch candidate blocks emitted as markdown text."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class MarkdownPatchDetection:
    has_patch: bool
    patch_content: str | None = None
    candidate_digest: str | None = None
    target_file: str | None = None


_DIFF_BLOCK_PATTERN = re.compile(
    r"```(?:diff|patch)?\s*\n(--- [^\n]+\n\+\+\+ [^\n]+.+?)```",
    re.DOTALL,
)
_HEADER_PATTERN = re.compile(r"--- (?:a/)?([^\t\n\r]+)\n\+\+\+ (?:b/)?([^\t\n\r]+)")


def detect_markdown_patch(text: str) -> MarkdownPatchDetection:
    """Scan conversational text for embedded diff patches."""
    if not isinstance(text, str):
        return MarkdownPatchDetection(has_patch=False)

    match = _DIFF_BLOCK_PATTERN.search(text)
    patch_text: str | None = None
    if match:
        patch_text = match.group(1).strip()
    elif "--- " in text and "+++" in text and "@@ " in text:
        # Naked diff in text
        start_idx = text.find("--- ")
        patch_text = text[start_idx:].strip()

    if patch_text and ("--- " in patch_text and "+++" in patch_text):
        digest = f"sha256:{hashlib.sha256(patch_text.encode('utf-8')).hexdigest()}"
        target_file = None
        hdr = _HEADER_PATTERN.search(patch_text)
        if hdr:
            target_file = hdr.group(2).strip()
        return MarkdownPatchDetection(
            has_patch=True,
            patch_content=patch_text,
            candidate_digest=digest,
            target_file=target_file,
        )

    return MarkdownPatchDetection(has_patch=False)
