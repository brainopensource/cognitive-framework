"""Anchored AST patch toolkit (mhf.toolkit.ast-patch). Python stdlib `ast` only."""

from __future__ import annotations

import ast
import difflib
import hashlib
from pathlib import Path
from typing import ClassVar, Mapping

from vanguard.packages.domain.wire.result import Err, Ok, Result
from vanguard.packages.domain.wire.types_gen import (
    ArtifactRef,
    EffectContext,
    EffectRequest,
    Health,
    Receipt,
    Reservation,
    ToolSchema,
)

__all__ = ["AstPatchToolkit", "structural_diff"]


class AstPatchToolkit:
    spi_version: ClassVar[str] = "1.0"

    def __init__(self, workspace: str | Path) -> None:
        self._root = Path(workspace)

    def verbs(self) -> Mapping[str, ToolSchema]:
        return {
            "patch.apply": ToolSchema(
                verb="patch.apply",
                schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "node_kind": {"type": "string"},
                        "qualified_name": {"type": "string"},
                        "anchor_digest": {"type": "string"},
                        "replacement": {"type": "string"},
                        "old": {"type": "string"},
                        "new": {"type": "string"},
                        "diff": {"type": "string"},
                    },
                },
            )
        }

    def execute(self, request: EffectRequest, ctx: EffectContext) -> Result[Receipt]:
        _ = ctx
        if request.verb != "patch.apply":
            return Err("unknown_verb", request.verb)
        rel = str(request.args.get("path") or "")
        target = (self._root / rel).resolve()
        try:
            target.relative_to(self._root.resolve())
        except ValueError:
            return Err("denied", "path escapes workspace")
        before = target.read_text(encoding="utf-8") if target.is_file() else ""
        try:
            after = _apply(before, request.args)
        except ValueError as exc:
            return Err("invalid_request", str(exc))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(after, encoding="utf-8")
        structural = structural_diff(before, after, rel)
        text_diff = "\n".join(difflib.unified_diff(
            before.splitlines(), after.splitlines(), fromfile="a/" + rel, tofile="b/" + rel, lineterm="",
        ))
        blob = hashlib.sha256(text_diff.encode("utf-8")).hexdigest()
        digest = hashlib.sha256(after.encode("utf-8")).hexdigest()
        return Ok(
            Receipt(
                request_digest="sha256:" + digest,
                outcome="completed",
                cost=request.reservation,
                artifacts=(ArtifactRef(digest="sha256:" + blob, kind="unified-diff"),),
            )
        )

    def compensate(self, receipt: Receipt) -> Result[Receipt]:
        return Ok(receipt)

    def health(self) -> Health:
        return Health(ok=True)


def structural_diff(before: str, after: str, path: str) -> dict[str, tuple[str, ...]]:
    _ = path
    before_names = _defs(before)
    after_names = _defs(after)
    return {
        "added": tuple(sorted(after_names - before_names)),
        "removed": tuple(sorted(before_names - after_names)),
        "changed": tuple(sorted(before_names & after_names)),
    }


def _defs(source: str) -> set[str]:
    if not source.strip():
        return set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            names.add("function:" + node.name)
        elif isinstance(node, ast.AsyncFunctionDef):
            names.add("function:" + node.name)
        elif isinstance(node, ast.ClassDef):
            names.add("class:" + node.name)
    return names


def _apply(before: str, args: Mapping[str, object]) -> str:
    replacement = args.get("replacement")
    qualified = args.get("qualified_name")
    node_kind = args.get("node_kind")
    if isinstance(replacement, str) and isinstance(qualified, str) and isinstance(node_kind, str):
        return _anchored(before, node_kind, qualified, str(args.get("anchor_digest") or ""), replacement)
    old, new = args.get("old"), args.get("new")
    if isinstance(old, str) and isinstance(new, str):
        if old not in before:
            raise ValueError("search text not found")
        return before.replace(old, new, 1)
    diff = args.get("diff")
    if isinstance(diff, str) and diff.strip():
        return _unified(before, diff)
    content = args.get("content")
    if isinstance(content, str):
        return content
    raise ValueError("unsupported patch shape")


def _anchored(before: str, node_kind: str, qualified: str, anchor: str, replacement: str) -> str:
    try:
        tree = ast.parse(before)
    except SyntaxError as exc:
        raise ValueError(f"cannot parse target: {exc}") from exc
    for node in ast.walk(tree):
        name = getattr(node, "name", None)
        kind = type(node).__name__
        if name != qualified or (node_kind and kind != node_kind):
            continue
        segment = ast.get_source_segment(before, node)
        if segment is None:
            continue
        digest = "sha256:" + hashlib.sha256(segment.encode("utf-8")).hexdigest()
        if anchor and anchor != digest:
            raise ValueError("anchor digest mismatch")
        return before.replace(segment, replacement.rstrip() + "\n", 1)
    raise ValueError(f"anchor {qualified!r} not found")


def _unified(before: str, diff: str) -> str:
    lines = before.splitlines(keepends=True)
    hunks = [line for line in diff.splitlines() if line[:1] in {"+", "-", " "} and not line.startswith(("+++", "---"))]
    if not hunks:
        raise ValueError("empty unified diff")
    # Last-resort: treat '+' lines as the new file body when old is empty.
    added = [line[1:] + "\n" for line in hunks if line.startswith("+")]
    removed = [line[1:] for line in hunks if line.startswith("-")]
    if not lines and added:
        return "".join(added)
    text = before
    for gone in removed:
        text = text.replace(gone, "", 1)
    if added and not removed:
        text = text + "".join(added)
    return text
