"""Anchored AST patch toolkit (mhf.toolkit.ast-patch). Python stdlib `ast` only."""

from __future__ import annotations

import ast
import difflib
import hashlib
import os
import stat
from pathlib import Path
from typing import ClassVar, Mapping

from vanguard.packages.adapters.environment.hunks import (
    HunkFailure,
    apply_unified_to_text,
    declared_preimages,
)
from vanguard.packages.domain.canonicalisation.digest import digest_bytes
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
                        "expected_preimage": {"type": "string"},
                        "expected_preimages": {"type": "object"},
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
        prior_mode = stat.S_IMODE(target.stat().st_mode) if target.is_file() else None
        pre_digest = digest_bytes(before.encode("utf-8")) if target.is_file() else None
        declared = declared_preimages(request.args)
        want = declared.get(rel) or declared.get("")
        if want and pre_digest and want != pre_digest:
            return Err("conflict", f"stale preimage for {rel}")
        try:
            after = _apply(before, request.args, rel)
        except ValueError as exc:
            return Err("invalid_request", str(exc))
        except HunkFailure as exc:
            return Err(exc.kind, exc.message)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(after, encoding="utf-8")
        if prior_mode is not None:
            os.chmod(target, prior_mode)
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


def _apply(before: str, args: Mapping[str, object], path: str = "<patch>") -> str:
    replacement = args.get("replacement")
    qualified = args.get("qualified_name")
    node_kind = args.get("node_kind")
    if isinstance(replacement, str) and isinstance(qualified, str) and isinstance(node_kind, str):
        return _anchored(before, node_kind, qualified, str(args.get("anchor_digest") or ""), replacement)
    old, new = args.get("old"), args.get("new")
    if isinstance(old, str) and isinstance(new, str):
        count = before.count(old)
        if count == 0:
            raise ValueError("search text not found")
        if count > 1:
            raise ValueError("ambiguous search text matches multiple locations")
        return before.replace(old, new, 1)
    diff = args.get("diff")
    if isinstance(diff, str) and diff.strip():
        try:
            return apply_unified_to_text(before, diff, path)
        except HunkFailure as exc:
            raise ValueError(exc.message) from exc
    content = args.get("content")
    if isinstance(content, str):
        return content
    raise ValueError("unsupported patch shape")


def _anchored(before: str, node_kind: str, qualified: str, anchor: str, replacement: str) -> str:
    try:
        tree = ast.parse(before)
    except SyntaxError as exc:
        raise ValueError(f"cannot parse target: {exc}") from exc
    named: list[str] = []
    digest_hits: list[str] = []
    for node in ast.walk(tree):
        name = getattr(node, "name", None)
        kind = type(node).__name__
        if name != qualified or (node_kind and kind != node_kind):
            continue
        segment = ast.get_source_segment(before, node)
        if segment is None:
            continue
        digest = "sha256:" + hashlib.sha256(segment.encode("utf-8")).hexdigest()
        named.append(segment)
        if not anchor or anchor == digest:
            digest_hits.append(segment)
    if not named:
        raise ValueError(f"anchor {qualified!r} not found")
    if anchor and not digest_hits:
        raise ValueError("anchor digest mismatch")
    matches = digest_hits
    if len(matches) > 1:
        raise ValueError(f"ambiguous anchor {qualified!r} matches {len(matches)} locations")
    return before.replace(matches[0], replacement.rstrip() + "\n", 1)
