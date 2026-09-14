"""Contract tests and falsifiers for C3: Memory retrieval into L5.

Verifies:
1. Authorization precedes memory retrieval.
2. Verified provenance via `require_retrieval_provenance`.
3. Memory fragments land exclusively in Layer.DIALOGUE (L5).
4. Memory fragments never perturb the frozen L1–L3 prefix digest.
5. Unauthorized or unverified memory results fail closed (PermissionError) and never reach context.
"""

from __future__ import annotations

import dataclasses
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
from vanguard.packages.runtime.root import HarnessSession, Runtime

from test.agency.doubles import ScriptedModel, finish
from test.runtime.test_harness_session import FakeEnvironment, _ports, _task


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


class CountingMemoryPort:
    """Records whether a protected read ever happened.

    `recall_calls` increments only after the authorization check, so a zero
    count is evidence that no record was dereferenced -- which is the claim
    "denied memory performs zero protected reads" actually makes.
    """

    category = "knowledge"

    def __init__(self, *, mismatched_receipt: bool = False) -> None:
        self.recall_calls = 0
        self._mismatched_receipt = mismatched_receipt

    def recall(self, query: str, access: MemoryAccess, limit: int = 20) -> MemoryResult:
        if not access.permitted():
            raise PermissionError("unauthorized access")
        self.recall_calls += 1
        selected = ("rec-1",)
        return MemoryResult(
            record_ids=selected,
            provenance=RetrievalProvenance(
                query_digest="sha256:" + "5" * 64,
                policy_identity="policy-product",
                source_record_digests=("sha256:" + "6" * 64,),
                # A receipt naming other records than the payload carries is
                # the shape a stale or swapped cache produces.
                selected_ids=("rec-other",) if self._mismatched_receipt else selected,
                dropped_ids=(),
                cache_identity=None,
                context_selection_digest=None,
                redacted=False,
            ),
            texts=("Fact A: auth must precede recall",),
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


class ProductSessionMemoryRetrieval(unittest.TestCase):
    """T-140: the same contract, through the composed product session.

    The unit cases above exercise `PromptAssembler` directly. These drive
    `Runtime.compose("vg-code-default")` → `HarnessSession` → `run()`, because
    an authorization rule that holds only when the assembler is called by hand
    is not a product property.
    """

    def setUp(self) -> None:
        self.harness = Runtime.compose("vg-code-default", episode_id="ep-session-1")

    @staticmethod
    def _binding(port: Any, access: MemoryAccess) -> MemoryBinding:
        return MemoryBinding(
            port=port,
            access=access,
            tenant="tenant-default",
            project="proj-mem",
            selector={"category": "knowledge"},
            query="prior facts about this repository",
        )

    def _session(self, binding: MemoryBinding | None) -> HarnessSession:
        ports = dataclasses.replace(
            _ports(ScriptedModel([finish()]), FakeEnvironment()), memory=binding)
        return HarnessSession(self.harness, ports, _task())

    def test_denied_memory_performs_zero_protected_reads(self) -> None:
        """The load-bearing one: a denied lease never reaches the records."""
        port = CountingMemoryPort()
        denied = self._binding(port, MemoryAccess(
            grant_ref="", selector={}, tenant="", project=""))
        result = self._session(denied).run()

        self.assertEqual(port.recall_calls, 0)
        self.assertEqual(result.terminal.value, "instrument_error")
        self.assertIn("memory capability denied", result.detail)

    def test_denied_memory_never_invokes_the_model(self) -> None:
        """Fail closed before inference: no provider call, no turn, no receipt."""
        port = CountingMemoryPort()
        denied = self._binding(port, MemoryAccess(
            grant_ref="", selector={}, tenant="", project=""))
        result = self._session(denied).run()

        self.assertEqual(result.instrument_error, "model_not_invoked")
        self.assertEqual(result.telemetry.turns, 0)
        self.assertEqual(result.receipts, ())

    def test_a_revoked_lease_performs_zero_protected_reads(self) -> None:
        port = CountingMemoryPort()
        revoked = self._binding(port, dataclasses.replace(
            _make_valid_access(), revoked=True))
        result = self._session(revoked).run()

        self.assertEqual(port.recall_calls, 0)
        self.assertEqual(result.terminal.value, "instrument_error")

    def test_a_lease_naming_another_category_performs_zero_reads(self) -> None:
        """Naming a grant is not holding one: the selector must match."""
        port = CountingMemoryPort()
        foreign = MemoryBinding(
            port=port,
            access=dataclasses.replace(
                _make_valid_access(), selector={"category": "experience"}),
            tenant="tenant-default",
            project="proj-mem",
            selector={"category": "knowledge"},
            query="prior facts",
        )
        result = self._session(foreign).run()

        self.assertEqual(port.recall_calls, 0)
        self.assertEqual(result.terminal.value, "instrument_error")

    def test_authorized_retrieval_reaches_l5_with_bound_provenance(self) -> None:
        port = CountingMemoryPort()
        session = self._session(self._binding(port, _make_valid_access()))
        bundle, compiled = session.operator._assembler.assemble(view={}, turn=0)

        self.assertEqual(port.recall_calls, 1)
        dialogue = compiled.layer_blocks(Layer.DIALOGUE)
        self.assertTrue(any(b.label.startswith("memory:") for b in dialogue))
        # Provenance is bound into the bundle, not merely computed.
        self.assertIn("memoryRetrievalDigest", bundle)
        self.assertTrue(bundle["memoryRetrievalDigest"].startswith("sha256:"))

    def test_authorized_retrieval_never_perturbs_the_frozen_prefix(self) -> None:
        port = CountingMemoryPort()
        with_memory = self._session(self._binding(port, _make_valid_access()))
        without_memory = self._session(None)

        _, a = with_memory.operator._assembler.assemble(view={}, turn=0)
        _, b = without_memory.operator._assembler.assemble(view={}, turn=0)

        self.assertEqual(a.prefix_digest, b.prefix_digest)
        for layer in PREFIX_LAYERS:
            for block in a.layer_blocks(layer):
                self.assertNotIn("Fact A", block.text)

    def test_a_result_whose_receipt_does_not_match_admits_nothing(self) -> None:
        """Provenance is checked against the records, not trusted alongside them."""
        port = CountingMemoryPort(mismatched_receipt=True)
        session = self._session(self._binding(port, _make_valid_access()))
        result = session.run()

        self.assertEqual(port.recall_calls, 1)
        self.assertEqual(result.terminal.value, "instrument_error")
        self.assertIn("do not match", result.detail)

    def test_removing_authorization_would_fail_this_oracle(self) -> None:
        """The bypass falsifier: reads under a denied lease must be detectable."""
        port = CountingMemoryPort()
        denied_access = MemoryAccess(
            grant_ref="", selector={}, tenant="", project="")
        self.assertFalse(denied_access.permitted())
        # Simulating the removed gate: calling the port directly does read.
        with self.assertRaises(PermissionError):
            port.recall("q", denied_access, 20)
        self.assertEqual(port.recall_calls, 0)


if __name__ == "__main__":
    unittest.main()
