"""Shared unified-diff hunk application for permitted environment adapters.

This is the existing Git/Fake in-memory applier extracted once so both
adapters and the AST patch toolkit share TC-E-061 fail-closed semantics.
It is not a second patcher or transaction engine.
"""

from __future__ import annotations

import os
import re
from typing import Mapping, Sequence

__all__ = [
    "HunkFailure",
    "apply_hunk_sequence",
    "apply_unified_to_text",
    "collect_hunk_body",
    "declared_preimages",
    "parse_hunk_header",
    "require_complete_hunk",
    "stale_preimage_kind_message",
]

_HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


class HunkFailure(Exception):
    """Fail-closed hunk/preimage refusal with a typed Result kind."""

    def __init__(self, kind: str, message: str) -> None:
        super().__init__(message)
        self.kind = kind
        self.message = message


def parse_hunk_header(line: str) -> int | None:
    """Return a 0-based location hint, or None for a bare ``@@`` header."""
    match = _HUNK_HEADER.match(line)
    if match:
        hunk_start = int(match.group(1))
        return max(hunk_start - 1, 0) if hunk_start else 0
    if line.strip() in ("@@", "@@@"):
        return None
    raise HunkFailure("invalid_request", f"malformed hunk header: {line}")


def collect_hunk_body(lines: Sequence[str], index: int) -> tuple[list[str], int]:
    """Collect one hunk body. Blank lines end the body; other junk is malformed."""
    body: list[str] = []
    while index < len(lines) and not lines[index].startswith(
        ("@@", "--- ", "diff --git")
    ):
        hline = lines[index]
        if not hline.strip():
            break
        if hline[:1] not in ("+", "-", " ", "\\"):
            raise HunkFailure(
                "invalid_request",
                f"malformed hunk body: unexpected line {hline!r}",
            )
        body.append(hline)
        index += 1
    return body, index


def require_complete_hunk(body: Sequence[str], path: str) -> None:
    if not body:
        raise HunkFailure("invalid_request", f"incomplete hunk in {path}: empty body")
    if not any(line[:1] in "+-" for line in body):
        raise HunkFailure(
            "invalid_request",
            f"incomplete hunk in {path}: no insertions or deletions",
        )


def apply_hunk_sequence(
    orig_lines: list[str],
    hunks: Sequence[tuple[int | None, Sequence[str]]],
    path: str,
) -> list[str]:
    """Apply collected hunks by unique context. Line numbers are hints only."""
    new_file_lines: list[str] = []
    orig_idx = 0
    for hint, body in hunks:
        expected_old = [line[1:] for line in body if line[:1] in ("-", " ")]

        def _matches(at: int, expected: list[str] = expected_old) -> bool:
            if at < 0 or at + len(expected) > len(orig_lines):
                return False
            return all(
                orig_lines[at + n].rstrip("\r\n") == want.rstrip("\r\n")
                for n, want in enumerate(expected)
            )

        if not expected_old:
            target_idx = hint if hint is not None else orig_idx
            if target_idx > len(orig_lines):
                raise HunkFailure(
                    "conflict",
                    f"hunk starts past end of {path} at line {target_idx}",
                )
        else:
            candidates = [
                at
                for at in range(orig_idx, len(orig_lines) - len(expected_old) + 1)
                if _matches(at)
            ]
            if not candidates:
                head = expected_old[0].rstrip("\r\n")
                raise HunkFailure(
                    "conflict",
                    f"patch context not found in {path}: no location "
                    f"matches the hunk beginning {head!r}",
                )
            if hint is None and len(candidates) > 1:
                raise HunkFailure(
                    "conflict",
                    f"ambiguous hunk in {path}: its context matches "
                    f"{len(candidates)} locations; supply a hunk header "
                    "with line numbers or add distinguishing context",
                )
            target_idx = (
                min(candidates, key=lambda at: abs(at - hint))
                if hint is not None
                else candidates[0]
            )

        if target_idx < orig_idx:
            raise HunkFailure(
                "invalid_request",
                f"hunks out of order in {path} at line {target_idx + 1}",
            )
        while orig_idx < target_idx:
            new_file_lines.append(orig_lines[orig_idx])
            orig_idx += 1

        for hline in body:
            marker, text = hline[:1], hline[1:]
            if marker == "+":
                new_file_lines.append(text + "\n")
            elif marker == "\\":
                continue
            elif marker in ("-", " "):
                if orig_idx >= len(orig_lines):
                    raise HunkFailure(
                        "conflict",
                        f"patch context extends past end of {path}",
                    )
                actual = orig_lines[orig_idx].rstrip("\r\n")
                if actual != text.rstrip("\r\n"):
                    raise HunkFailure(
                        "conflict",
                        f"patch context mismatch in {path}: "
                        f"expected {text!r}, got {actual!r}",
                    )
                if marker == " ":
                    new_file_lines.append(orig_lines[orig_idx])
                orig_idx += 1

    while orig_idx < len(orig_lines):
        new_file_lines.append(orig_lines[orig_idx])
        orig_idx += 1
    return new_file_lines


def apply_unified_to_text(before: str, diff: str, path: str = "<patch>") -> str:
    """Apply a single-file unified diff to ``before``. Raises ``HunkFailure``."""
    if not diff.strip():
        raise HunkFailure("invalid_request", "empty unified diff")
    lines = diff.splitlines()
    index = 0
    hunks: list[tuple[int | None, list[str]]] = []
    while index < len(lines):
        line = lines[index]
        if line.startswith("diff --git "):
            index += 1
            continue
        if line.startswith("--- "):
            index += 1
            if index < len(lines) and lines[index].startswith("+++ "):
                index += 1
            continue
        if line.startswith("@@"):
            hint = parse_hunk_header(line)
            index += 1
            body, index = collect_hunk_body(lines, index)
            require_complete_hunk(body, path)
            hunks.append((hint, body))
            continue
        index += 1
    if not hunks:
        raise HunkFailure("invalid_request", f"patch file {path} contained no hunks")
    orig_lines = before.splitlines(keepends=True)
    return "".join(apply_hunk_sequence(orig_lines, hunks, path))


def declared_preimages(args: Mapping[str, object]) -> dict[str, str]:
    """Extract caller-declared preimage digests from effect args."""
    mapping: dict[str, str] = {}
    raw = args.get("expected_preimages") or args.get("preimageDigests")
    if isinstance(raw, Mapping):
        for key, value in raw.items():
            if isinstance(key, str) and isinstance(value, str) and value:
                mapping[os.path.normpath(key).replace("\\", "/")] = value
    single = (
        args.get("expected_preimage")
        or args.get("preimage_digest")
        or args.get("preimageDigest")
    )
    path = args.get("path")
    if isinstance(single, str) and single:
        if isinstance(path, str) and path:
            mapping.setdefault(os.path.normpath(path).replace("\\", "/"), single)
        else:
            mapping.setdefault("", single)
    return mapping


def stale_preimage_kind_message(
    affected: Sequence[object],
    args: Mapping[str, object],
) -> tuple[str, str] | None:
    """Return ``(kind, message)`` when a declared preimage no longer matches."""
    declared = declared_preimages(args)
    if not declared:
        return None

    def _pre_digest(resource: object) -> str | None:
        digest = getattr(resource, "pre_digest", None)
        return digest if isinstance(digest, str) else None

    def _name(resource: object) -> str:
        name = getattr(resource, "resource", "")
        return name if isinstance(name, str) else ""

    if "" in declared:
        want = declared[""]
        named = [item for item in affected if _pre_digest(item)]
        if len(affected) == 1 or len(named) == 1:
            target = named[0] if named else affected[0]
            actual = _pre_digest(target)
            if actual and actual != want:
                return ("conflict", f"stale preimage for {_name(target)}")
        declared = {key: value for key, value in declared.items() if key}

    for resource in affected:
        want = declared.get(_name(resource))
        actual = _pre_digest(resource)
        if want and actual and want != actual:
            return ("conflict", f"stale preimage for {_name(resource)}")
    return None
