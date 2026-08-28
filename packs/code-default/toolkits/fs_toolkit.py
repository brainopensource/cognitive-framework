"""Workspace file observation toolkit (mhf.toolkit.fs)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import ClassVar, Mapping

from vanguard.packages.domain.wire.result import Err, Ok, Result
from vanguard.packages.domain.wire.types_gen import EffectContext, EffectRequest, Health, Receipt, Reservation, ToolSchema

__all__ = ["FsToolkit"]


class FsToolkit:
    spi_version: ClassVar[str] = "1.0"

    def __init__(self, workspace: str | Path) -> None:
        self._root = Path(workspace)

    def verbs(self) -> Mapping[str, ToolSchema]:
        read_schema: dict[str, object] = {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        }
        # `execute()` has always read `request.args["pattern"]` for fs.search;
        # the exposed schema only ever declared `path`, so a model had no
        # contract-level hint that a search needs a term at all -- it could
        # only discover this by guessing or by the field going silently unused.
        search_schema: dict[str, object] = {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "pattern": {"type": "string"},
            },
            "required": ["pattern"],
        }
        return {
            "fs.read": ToolSchema(verb="fs.read", schema=read_schema),
            "fs.search": ToolSchema(verb="fs.search", schema=search_schema),
        }

    def execute(self, request: EffectRequest, ctx: EffectContext) -> Result[Receipt]:
        _ = ctx
        rel = str(request.args.get("path") or "")
        target = (self._root / rel).resolve()
        try:
            target.relative_to(self._root.resolve())
        except ValueError:
            return Err("denied", "path escapes workspace")
        if request.verb == "fs.search":
            needle = str(request.args.get("pattern") or "")
            hits = []
            if self._root.is_dir():
                for path in self._root.rglob("*"):
                    if path.is_file() and needle in path.read_text(encoding="utf-8", errors="ignore"):
                        hits.append(path.relative_to(self._root).as_posix())
            digest = hashlib.sha256("\n".join(hits).encode()).hexdigest()
            return Ok(_receipt(digest, request.reservation))
        if not target.is_file():
            return Err("not_found", rel)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        return Ok(_receipt(digest, request.reservation))

    def compensate(self, receipt: Receipt) -> Result[Receipt]:
        return Ok(receipt)

    def health(self) -> Health:
        return Health(ok=True)


def _receipt(digest: str, cost: Reservation) -> Receipt:
    return Receipt(request_digest="sha256:" + digest, outcome="completed", cost=cost)
