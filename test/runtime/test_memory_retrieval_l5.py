"""Contract tests and falsifiers for C3: Memory retrieval into L5.

Verifies:
1. Authorization precedes memory retrieval.
2. Verified provenance via `require_retrieval_provenance`.
3. Memory fragments land exclusively in Layer.DIALOGUE (L5).
4. Memory fragments never perturb the frozen L1–L3 prefix digest.
5. Unauthorized or unverified memory results fail closed (PermissionError) and never reach context.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
import unittest

from vanguard.packages.agency.context.compiler import ContextCompiler
from vanguard.packages.agency.context.layers import Layer, PREFIX_LAYERS
from vanguard.packages.ports.memory import (
    MemoryAccess,
    MemoryBinding,
    MemoryResult,
    RetrievalProvenance,
)
from vanguard.packages.runtime.compose import TaskContext
from vanguard.packages.runtime.prompt_assembler import PromptAssembler


class FakeClock:
    def __init__(self, now_iso: str = "2026-09-13T12:00:00Z") -> None:
        self.now_iso = now_iso

    def now(self) -> datetime:
        return datetime.fromisoformat(self.now_iso.replace("Z", "+00:00")).astimezone(timezone.utc)


class FakeMemoryPort:
    def __init__(self, records: dict[str, str] | None = None) -> None:
        self.records = records or {"rec-1": "Fact A: auth must precede recall", "rec-2": "Fact B: L5 holds memories"}
        self.recalled_queries: list[str] = []

    def recall(self, query: str, access: MemoryAccess, limit: int = 20) -> MemoryResult:
        if not access.permitted():
            raise PermissionError("unauthorized access")
        self.recalled_queries.append(query)
        selected_ids = tuple(list(self.records.keys())[:limit])
        texts = tuple(self.records[rid] for rid in selected_ids)
        provenance = RetrievalProvenance(
            query_digest="sha256:" + "1" * 64,
            policy_identity="policy-v1",
            source_record_digests=("sha256:" + "2" * 64, "sha256:" + "3" * 64),
            selected_ids=selected_ids,
            dropped_ids=(),
            cache_identity=None,
            context_selection_digest="sha256:" + "4" * 64,
            redacted=False,
        )
        return MemoryResult(
            record_ids=selected_ids,
            provenance=provenance,
            texts=texts,
        )

    def write(self, value: Mapping[str, Any], access: MemoryAccess) -> str:
        if not access.permitted():
            raise PermissionError("unauthorized write")
        return "rec-new"


def _make_valid_access(expires_at: str = "2026-09-14T00:00:00Z") -> MemoryAccess:
    return MemoryAccess(
        grant_ref="grant-1",
        selector={"category": "knowledge"},
        tenant="tenant-default",
        project="proj-mem",
        issuer="gov-1",
        subject="principal-test",
        actions=("read", "write"),
        purpose="task-context",
        expires_at=expires_at,
        verification_receipt="receipt-ok",
    )


class TestMemoryRetrievalL5(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock()
        self.task = TaskContext(
            brief="memory retrieval test",
            repo_path=Path("/workspace"),
            project_id="proj-mem",
            run_id="run-mem",
            episode_id="ep-mem",
            principal="principal-test",
        )
        self.compiler = ContextCompiler(
            system_core="System core instructions.",
            capability_cards="[CAPABILITY: memory active]",
            token_ceiling=8000,
        )

    def test_authorized_memory_lands_in_l5_only(self) -> None:
        port = FakeMemoryPort()
        binding = MemoryBinding(
            port=port,
            access=_make_valid_access(),
            selector={"category": "knowledge"},
            query="auth fact",
            limit=2,
        )
        assembler = PromptAssembler(
            compiler=self.compiler,
            task=self.task,
            clock=self.clock,
            memory=binding,
        )

        bundle, compiled = assembler.assemble(view={}, turn=0)

        # 1. Retrieval happened
        self.assertEqual(port.recalled_queries, ["auth fact"])

        # 2. Memories are present in Layer.DIALOGUE (L5)
        l5_blocks = compiled.layer_blocks(Layer.DIALOGUE)
        l5_labels = [b.label for b in l5_blocks]
        self.assertIn("memory:rec-1", l5_labels)
        self.assertIn("memory:rec-2", l5_labels)

        # 3. Memories are NOT in L1-L3 prefix
        for layer in PREFIX_LAYERS:
            for b in compiled.layer_blocks(layer):
                self.assertNotIn("memory:rec-", b.label)
                self.assertNotIn("Fact A", b.text)
                self.assertNotIn("Fact B", b.text)

    def test_memory_does_not_perturb_prefix_digest(self) -> None:
        """Comparing turn without memory vs turn with memory proves prefix is byte-identical."""
        # Baseline without memory
        assembler_no_mem = PromptAssembler(
            compiler=self.compiler,
            task=self.task,
            clock=self.clock,
            memory=None,
        )
        _, compiled_no_mem = assembler_no_mem.assemble(view={}, turn=0)
        baseline_prefix_digest = compiled_no_mem.prefix_digest

        # With memory
        port = FakeMemoryPort()
        binding = MemoryBinding(
            port=port,
            access=_make_valid_access(),
            selector={"category": "knowledge"},
            query="auth fact",
            limit=2,
        )
        assembler_with_mem = PromptAssembler(
            compiler=self.compiler,
            task=self.task,
            clock=self.clock,
            memory=binding,
        )
        _, compiled_with_mem = assembler_with_mem.assemble(view={}, turn=0)
        with_mem_prefix_digest = compiled_with_mem.prefix_digest

        self.assertEqual(
            baseline_prefix_digest,
            with_mem_prefix_digest,
            "Memory retrieval must not alter the frozen prefix digest",
        )

    def test_unauthorized_memory_fails_closed(self) -> None:
        """Expired grant must fail closed and raise PermissionError before compilation."""
        port = FakeMemoryPort()
        # Expired token in the past relative to clock (2026-09-13T12:00:00Z)
        expired_access = _make_valid_access(expires_at="2026-09-01T00:00:00Z")
        binding = MemoryBinding(
            port=port,
            access=expired_access,
            selector={"category": "knowledge"},
            query="test",
            limit=2,
        )
        assembler = PromptAssembler(
            compiler=self.compiler,
            task=self.task,
            clock=self.clock,
            memory=binding,
        )

        with self.assertRaises(PermissionError):
            assembler.assemble(view={}, turn=0)

    def test_missing_provenance_fails_closed(self) -> None:
        """Memory recall result lacking valid provenance must raise PermissionError."""
        class TamperedMemoryPort:
            def recall(self, query: str, access: MemoryAccess, limit: int = 20) -> MemoryResult:
                return MemoryResult(
                    record_ids=("r1",),
                    provenance=None,  # type: ignore[arg-type]
                    texts=("tampered text",),
                )

        binding = MemoryBinding(
            port=TamperedMemoryPort(),
            access=_make_valid_access(),
            selector={"category": "knowledge"},
            query="test",
            limit=1,
        )
        assembler = PromptAssembler(
            compiler=self.compiler,
            task=self.task,
            clock=self.clock,
            memory=binding,
        )

        with self.assertRaises(PermissionError):
            assembler.assemble(view={}, turn=0)


if __name__ == "__main__":
    unittest.main()
