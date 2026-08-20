"""Merkle workspace index + token-budgeted repo map (mhf.toolkit.index / mhf.context.repo-map)."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import ClassVar, Mapping, Sequence

from vanguard.packages.domain.wire.result import Ok, Result
from vanguard.packages.domain.wire.types_gen import (
    CompactionReport,
    ContextBundle,
    EffectContext,
    EffectFailure,
    EffectRequest,
    EpisodeView,
    Health,
    Receipt,
    ToolSchema,
)

__all__ = ["IndexToolkit", "RepoMapContext"]

_DEFINITIONS: tuple[tuple[str, str, re.Pattern[str]], ...] = (
    (".py", "function", re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)")),
    (".py", "class", re.compile(r"^\s*class\s+([A-Za-z_]\w*)")),
)
_IGNORED = {".git", "__pycache__", "node_modules", ".venv"}


class IndexToolkit:
    spi_version: ClassVar[str] = "1.0"

    def __init__(self, workspace: str | Path) -> None:
        self._root = Path(workspace)
        self._files: dict[str, str] = {}
        self._symbols: list[dict[str, object]] = []
        self._dirty: set[str] = set()
        self._merkle = ""

    def verbs(self) -> Mapping[str, ToolSchema]:
        return {"index.refresh": ToolSchema(verb="index.refresh", schema={"type": "object"})}

    def execute(self, request: EffectRequest, ctx: EffectContext) -> Result[Receipt]:
        _ = ctx
        if request.verb == "index.refresh":
            self.scan()
        return Ok(Receipt(request_digest="sha256:" + (self._merkle or "0" * 64),
                          outcome="completed", cost=request.reservation))

    def compensate(self, receipt: Receipt) -> Result[Receipt]:
        return Ok(receipt)

    def health(self) -> Health:
        return Health(ok=True)

    def ingest(self, receipts: Sequence[Receipt]) -> None:
        for receipt in receipts:
            for artifact in receipt.artifacts:
                self._dirty.add(artifact.kind)

    def scan(self) -> str:
        files: dict[str, str] = {}
        kept = {item["path"]: item for item in self._symbols if isinstance(item.get("path"), str)}
        symbols: list[dict[str, object]] = []
        rescan_all = (not self._dirty) or ("*" in self._dirty) or (not self._files)
        if self._root.is_dir():
            for path in sorted(self._root.rglob("*")):
                if not path.is_file() or set(path.parts) & _IGNORED:
                    continue
                rel = path.relative_to(self._root).as_posix()
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                files[rel] = digest
                dirty = rescan_all or rel in self._dirty
                if not dirty and rel in self._files:
                    symbols.extend(item for item in self._symbols if item.get("path") == rel)
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
                suffix = path.suffix
                for want, kind, pattern in _DEFINITIONS:
                    if want != suffix:
                        continue
                    for lineno, line in enumerate(text.splitlines(), start=1):
                        match = pattern.match(line)
                        if match:
                            symbols.append({"name": match.group(1), "kind": kind, "path": rel, "line": lineno})
        self._files = files
        self._symbols = symbols
        self._dirty.clear()
        _ = kept
        payload = json.dumps({"files": files, "symbols": symbols}, sort_keys=True)
        self._merkle = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return self._merkle

    def render(self, token_budget: int) -> str:
        if not self._files:
            self.scan()
        lines = [f"{path} {digest[:8]}" for path, digest in list(self._files.items())[:64]]
        for symbol in self._symbols[:64]:
            lines.append(f"{symbol['kind']} {symbol['name']} {symbol['path']}:{symbol['line']}")
        text = "\n".join(lines)
        budget = max(0, token_budget * 4)
        return text if len(text) <= budget else text[:budget]


class RepoMapContext:
    spi_version: ClassVar[str] = "1.0"

    def __init__(self, *, system_prefix: str, index: IndexToolkit, token_budget: int = 4000,
                 compaction: str = "recency-window") -> None:
        self._prefix = system_prefix
        self._index = index
        self._token_budget = token_budget
        self._compaction = compaction
        self._notes: list[str] = []

    def compile(self, view: EpisodeView, budget_tokens: int) -> Result[ContextBundle]:
        mapped = self._index.render(min(self._token_budget, budget_tokens))
        suffix = "\n".join([view.goal, mapped, *self._notes])
        return Ok(ContextBundle(prefix=self._prefix, suffix=suffix, token_count=(len(self._prefix) + len(suffix) + 3) // 4))

    def ingest(self, receipts: Sequence[Receipt]) -> None:
        self._index.ingest(receipts)
        for receipt in receipts:
            self._notes.append(receipt.outcome)

    def compact(self, pressure: float) -> Result[CompactionReport]:
        removed = len(self._notes)
        if pressure >= 1.0 or self._compaction == "recency-window":
            self._notes = self._notes[-2:]
        return Ok(CompactionReport(removed_tokens=removed, strategy=self._compaction))

    def reground(self, error: EffectFailure) -> Result[ContextBundle]:
        return Ok(ContextBundle(prefix=self._prefix, suffix=error.detail, token_count=1))
