"""Qualification test for C6: Long session extension, index/memory resumption, and hermetic PromptCodec.

Verifies:
1. Index rebinds on restart matching WorkspaceEpoch and index_snapshot_digest.
2. Memory access is re-authorized upon resumption rather than assumed.
3. Compaction under pressure preserves critical state (prefix, sigma, task).
4. PromptCodec cache negotiation:
   - Supported routes ('anthropic/*') receive explicit cache breakpoints.
   - Unsupported routes ('deepseek/*', 'google/*', etc.) receive unmarked byte-identical messages.
   - Prefix equality demonstrates deterministic byte stability without claiming synthetic cache hits.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any, Mapping
import unittest

from vanguard.packages.adapters.models.prompt_codec import (
    PromptCodec,
    supports_cache_control,
)
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.adapters.stores.repo_index import InMemoryRepoIndex
from vanguard.packages.agency.context.compiler import ContextCompiler
from vanguard.packages.agency.context.compaction import ResultEvictionStrategy
from vanguard.packages.agency.context.layers import Layer, PREFIX_LAYERS
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.ports.memory import (
    MemoryAccess,
    MemoryBinding,
    MemoryResult,
    RetrievalProvenance,
)
from vanguard.packages.runtime.compose import TaskContext
from vanguard.packages.runtime.prompt_assembler import PromptAssembler
from vanguard.packages.runtime.root import (
    HarnessSession,
    Runtime,
    SessionPorts,
)
from test.agency.doubles import ScriptedModel, finish
from test.runtime.test_harness_session import FakeEnvironment

class FakeClock:
    def __init__(self, now_iso: str = "2026-09-13T12:00:00Z") -> None:
        self.now_iso = now_iso

    def now(self) -> datetime:
        return datetime.fromisoformat(self.now_iso.replace("Z", "+00:00")).astimezone(timezone.utc)


class TestLongSessionIndexAndMemory(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self._tmp, True)
        self.repo = Path(self._tmp)
        (self.repo / "src").mkdir()
        (self.repo / "src" / "main.py").write_text("def run(): return 1\n", encoding="utf-8")
        (self.repo / "tests").mkdir()
        (self.repo / "tests" / "test_main.py").write_text("def test_run(): pass\n", encoding="utf-8")

    def test_prompt_codec_cache_control_negotiation(self) -> None:
        """Hermetically verify PromptCodec negotiation across model routes."""
        codec = PromptCodec()
        body = {
            "model": "anthropic/claude-3-7-sonnet",
            "messages": [
                {"role": "system", "content": "You are Vanguard."},
                {"role": "user", "content": "Run tests."},
            ],
        }

        # 1. Anthropic route receives 1 breakpoint
        self.assertTrue(supports_cache_control("anthropic/claude-3-7-sonnet"))
        serialized_anthropic = codec.serialize(body, model="anthropic/claude-3-7-sonnet")
        self.assertEqual(serialized_anthropic.cache_breakpoints, 1)
        payload_anthropic = json.loads(serialized_anthropic.payload.decode("utf-8"))
        first_msg = payload_anthropic["messages"][0]
        # First message content or object has cache_control
        if isinstance(first_msg.get("content"), list):
            self.assertTrue(any(isinstance(c, dict) and "cache_control" in c for c in first_msg["content"]))
        else:
            self.assertIn("cache_control", first_msg)

        # 2. Unsupported route (DeepSeek / OpenAI / etc.) receives unmarked byte-identical messages
        self.assertFalse(supports_cache_control("deepseek/deepseek-v4-flash"))
        self.assertFalse(supports_cache_control("openai/gpt-4o"))
        serialized_deepseek = codec.serialize(body, model="deepseek/deepseek-v4-flash")
        self.assertEqual(serialized_deepseek.cache_breakpoints, 0)
        payload_deepseek = json.loads(serialized_deepseek.payload.decode("utf-8"))
        for msg in payload_deepseek["messages"]:
            self.assertNotIn("cache_control", msg)
            if isinstance(msg.get("content"), list):
                for part in msg["content"]:
                    if isinstance(part, dict):
                        self.assertNotIn("cache_control", part)

        # 3. Determinism: serializing same messages in two turns produces identical bytes
        turn0 = codec.serialize(body, model="deepseek/deepseek-v4-flash")
        turn1 = codec.serialize(body, model="deepseek/deepseek-v4-flash")
        self.assertEqual(turn0.payload, turn1.payload)
        self.assertEqual(turn0.input_tokens, turn1.input_tokens)

    def test_memory_must_be_reauthorized_on_session_restart(self) -> None:
        """Memory leases must be verified at the point of use on restart, not inherited."""
        class ExpirableMemoryPort:
            def __init__(self) -> None:
                self.calls = 0

            def recall(self, query: str, access: MemoryAccess, limit: int = 20) -> MemoryResult:
                self.calls += 1
                return MemoryResult(
                    record_ids=("m1",),
                    provenance=RetrievalProvenance(
                        query_digest="sha256:" + "0" * 64,
                        policy_identity="pol-1",
                        source_record_digests=("sha256:" + "1" * 64,),
                        selected_ids=("m1",),
                        dropped_ids=(),
                        cache_identity=None,
                        context_selection_digest=None,
                        redacted=False,
                    ),
                    texts=("Memory fact",),
                )

        # Session 1: valid memory lease expires at 2026-09-13T12:30:00Z
        clock_turn0 = FakeClock(now_iso="2026-09-13T12:00:00Z")
        access_valid = MemoryAccess(
            grant_ref="grant-t6",
            selector={"category": "knowledge"},
            tenant="tenant-default",
            project="proj-t6",
            issuer="gov-1",
            subject="agent-1",
            actions=("read",),
            purpose="task-context",
            expires_at="2026-09-13T12:30:00Z",
            verification_receipt="receipt-valid",
        )
        port = ExpirableMemoryPort()
        binding1 = MemoryBinding(
            port=port,
            access=access_valid,
            selector={"category": "knowledge"},
            query="knowledge query",
        )
        compiler = ContextCompiler(system_core="Core prompt", token_ceiling=8000)
        task = TaskContext(
            brief="task with memory",
            repo_path=self.repo,
            project_id="proj-t6",
            run_id="run-t6-1",
            episode_id="ep-t6-1",
            principal="agent-1",
        )
        assembler1 = PromptAssembler(compiler=compiler, task=task, clock=clock_turn0, memory=binding1)
        _, compiled1 = assembler1.assemble(view={}, turn=0)
        self.assertEqual(port.calls, 1)
        self.assertTrue(any("memory:m1" in b.label for b in compiled1.layer_blocks(Layer.DIALOGUE)))

        # Session 2 (restart later at 2026-09-13T13:00:00Z): the lease has expired!
        clock_restart = FakeClock(now_iso="2026-09-13T13:00:00Z")
        assembler_restart = PromptAssembler(compiler=compiler, task=task, clock=clock_restart, memory=binding1)
        # Point of use check must fail closed
        with self.assertRaises(PermissionError):
            assembler_restart.assemble(view={}, turn=0)

    def test_compaction_preserves_critical_state_under_pressure(self) -> None:
        """Forced compaction evicts dialogue outcomes while retaining frozen prefix and sigma."""
        compiler = ContextCompiler(
            system_core="System Core Instructions",
            compaction_strategy=ResultEvictionStrategy(),
            token_ceiling=120,
        )
        task = TaskContext(
            brief="long episode task",
            repo_path=self.repo,
            project_id="proj-t6",
            run_id="run-t6-comp",
            episode_id="ep-t6-comp",
            principal="agent-1",
            resume_state={"sigma": "important_checkpoint", "turn": 20},
        )
        assembler = PromptAssembler(
            compiler=compiler,
            task=task,
            clock=FakeClock(),
            task_state={"sigma": "important_checkpoint", "turn": 20},
        )

        # Compile baseline before flooding dialogue
        _, compiled0 = assembler.assemble(view={}, turn=0)
        baseline_prefix_digest = compiled0.prefix_digest

        # Populate many dialogue turns to trigger compaction pressure
        for i in range(30):
            assembler.note(
                label=f"tool-result-{i}",
                source="tool_result",
                text=f"Verbose tool output {i} " * 50,
                evictable=True,
            )

        _, compiled = assembler.assemble(view={}, turn=21)

        # 1. Prefix is completely intact and bit-identical to turn 0
        self.assertEqual(compiled.prefix_digest, baseline_prefix_digest)
        self.assertGreater(len(compiled.layer_blocks(Layer.SYSTEM)), 0)

        # 2. Task state (sigma) is preserved
        task_blocks = compiled.layer_blocks(Layer.TASK)
        self.assertTrue(any("important_checkpoint" in b.text for b in task_blocks))

        # 3. Oldest verbose tool outputs were evicted to stay within budget
        dialogue_labels = [b.label for b in compiled.layer_blocks(Layer.DIALOGUE)]
        self.assertNotIn("tool-result-0", dialogue_labels)
        # Recent tool output remains
        self.assertIn("tool-result-29", dialogue_labels)

    def test_index_rebinds_without_rereading_world_on_session_restart(self) -> None:
        """On session restart, index rebinds with matching WorkspaceEpoch without losing state."""
        index = InMemoryRepoIndex({"src/main.py": "def run(): return 1\n"})
        session1 = HarnessSession(
            Runtime.compose("vg-code-default", episode_id="ep-rebind-1"),
            SessionPorts(
                model=ScriptedModel([finish()]),
                environment=FakeEnvironment(),
                clock=FakeClock(),
                store=SqliteEventStore(":memory:"),
                index=index,
                interactive=False,
            ),
            TaskContext(
                brief="initial run",
                repo_path=self.repo,
                project_id="proj-rebind",
                run_id="run-rebind-1",
                episode_id="ep-rebind-1",
                principal="agent-1",
            ),
        )
        packet1 = session1.context_packet
        self.assertIsNotNone(packet1)
        epoch1 = packet1.workspace_epoch
        self.assertIsNotNone(epoch1)

        # Resume in a fresh session with resume_state carrying the recorded epoch and index digests
        session2 = HarnessSession(
            Runtime.compose("vg-code-default", episode_id="ep-rebind-2"),
            SessionPorts(
                model=ScriptedModel([finish()]),
                environment=FakeEnvironment(),
                clock=FakeClock(),
                store=SqliteEventStore(":memory:"),
                index=index,
                interactive=False,
            ),
            TaskContext(
                brief="resumed run",
                repo_path=self.repo,
                project_id="proj-rebind",
                run_id="run-rebind-2",
                episode_id="ep-rebind-2",
                principal="agent-1",
                resume_state={
                    "repositoryIdentity": packet1.repository_identity,
                    "indexSnapshotDigest": packet1.index_snapshot_digest,
                    "workspaceEpoch": epoch1.as_dict() if hasattr(epoch1, "as_dict") else dataclasses.asdict(epoch1),
                },
            ),
        )
        packet2 = session2.context_packet
        self.assertIsNotNone(packet2)
        # Index snapshot digest matches without re-reading
        self.assertEqual(packet2.index_snapshot_digest, packet1.index_snapshot_digest)
        self.assertEqual(packet2.repository_identity, packet1.repository_identity)


if __name__ == "__main__":
    unittest.main()
