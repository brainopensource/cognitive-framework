"""IndexPort-backed repository toolkit for the code-default pack."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Mapping, Sequence

from vanguard.packages.adapters.stores.repo_index import FileRepoIndex
from vanguard.packages.ports.index import IndexPort
from vanguard.packages.domain.wire.result import Ok, Result
from vanguard.packages.domain.wire.types_gen import CompactionReport, ContextBundle, EffectContext, EffectFailure, EffectRequest, EpisodeView, Health, Receipt, ToolSchema

__all__ = ["IndexToolkit", "RepoMapContext"]


class IndexToolkit:
    """SPI adapter that delegates repository observations to ``IndexPort``."""

    spi_version: ClassVar[str] = "1.0"

    def __init__(self, workspace: str | Path, index: IndexPort | None = None) -> None:
        self._index: IndexPort = index or FileRepoIndex()
        self._workspace = str(workspace)
        self._symbols: list[dict[str, object]] = []
        self._dirty: set[str] = set()

    def verbs(self) -> Mapping[str, ToolSchema]:
        return {"index.refresh": ToolSchema(verb="index.refresh", schema={"type": "object"})}

    def execute(self, request: EffectRequest, ctx: EffectContext) -> Result[Receipt]:
        del ctx
        if request.verb == "index.refresh":
            result = self._index.index(self._workspace)
            if not result.ok:
                return Result.fail(result.error.kind, result.error.message) if result.error else Result.fail("unavailable", "index unavailable")
            self._capture_symbols()
            self._dirty.clear()
        return Ok(Receipt(request_digest="sha256:" + "0" * 64, outcome="completed", cost=request.reservation))

    def compensate(self, receipt: Receipt) -> Result[Receipt]:
        return Ok(receipt)

    def health(self) -> Health:
        return Health(ok=True)

    def ingest(self, receipts: Sequence[Receipt]) -> None:
        for receipt in receipts:
            self._dirty.update(artifact.kind for artifact in receipt.artifacts)

    def _capture_symbols(self) -> None:
        symbols = self._index.symbols()
        self._symbols = (
            [{"name": item.name, "kind": item.kind, "path": item.path, "line": item.line}
             for item in (symbols.value or ())]
            if symbols.ok else []
        )

    def scan(self) -> str:
        result = self._index.index(self._workspace)
        if not result.ok:
            return ""
        mapped = self._index.repo_map(token_budget=1)
        self._capture_symbols()
        self._dirty.clear()
        return mapped.value.source_revision if mapped.ok and mapped.value else ""

    def render(self, token_budget: int) -> str:
        mapped = self._index.repo_map(token_budget=max(0, token_budget))
        if not mapped.ok or mapped.value is None:
            return ""
        summary = mapped.value
        lines = [path for path in summary.files]
        lines.extend(f"{symbol.kind} {symbol.name} {symbol.path}:{symbol.line}" for symbol in summary.symbols)
        return "\n".join(lines)


class RepoMapContext:
    spi_version: ClassVar[str] = "1.0"

    def __init__(self, *, system_prefix: str, index: IndexToolkit, token_budget: int = 4000, compaction: str = "recency-window") -> None:
        self._prefix, self._index = system_prefix, index
        self._token_budget, self._compaction = token_budget, compaction
        self._notes: list[str] = []

    def compile(self, view: EpisodeView, budget_tokens: int) -> Result[ContextBundle]:
        mapped = self._index.render(min(self._token_budget, budget_tokens))
        suffix = "\n".join([view.goal, mapped, *self._notes])
        return Ok(ContextBundle(prefix=self._prefix, suffix=suffix, token_count=(len(self._prefix) + len(suffix) + 3) // 4))

    def ingest(self, receipts: Sequence[Receipt]) -> None:
        self._index.ingest(receipts)
        self._notes.extend(receipt.outcome for receipt in receipts)

    def compact(self, pressure: float) -> Result[CompactionReport]:
        removed = len(self._notes)
        if pressure >= 1.0 or self._compaction == "recency-window":
            self._notes = self._notes[-2:]
        return Ok(CompactionReport(removed_tokens=removed, strategy=self._compaction))

    def reground(self, error: EffectFailure) -> Result[ContextBundle]:
        return Ok(ContextBundle(prefix=self._prefix, suffix=error.detail, token_count=1))
