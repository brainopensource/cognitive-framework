"""M-8 turn-loop memory retrieval and causal experience integration."""

from __future__ import annotations

import hashlib
import hmac
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from test.agency.doubles import ScriptedModel, finish
from test.runtime.test_harness_session import FakeClock, FakeEnvironment
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.ports.memory import (
    MemoryAuthorizationPort,
    MemoryBinding,
    MemoryResult,
    RetrievalProvenance,
)
from vanguard.packages.runtime.memory import MemoryAccess
from vanguard.packages.runtime.root import HarnessSession, Runtime, SessionPorts, TaskContext
from vanguard.packages.adapters.stores.event_store import SqliteEventStore


class RecordingMemory:
    def __init__(self) -> None:
        self.reads: list[tuple[str, MemoryAccess]] = []
        self.writes: list[tuple[Mapping[str, Any], MemoryAccess]] = []

    def recall(self, query: str, access: MemoryAccess, limit: int = 20) -> MemoryResult:
        self.reads.append((query, access))
        provenance = RetrievalProvenance(
            query_digest=digest_of({"query": query}),
            policy_identity="test-memory-policy/1",
            source_record_digests=("sha256:source",),
            selected_ids=("knowledge:1",),
            dropped_ids=(),
            cache_identity=None,
            context_selection_digest=None,
            redacted=False,
        )
        return MemoryResult(("knowledge:1",), provenance, ("authorized memory fact",))

    def write(self, value: Mapping[str, Any], access: MemoryAccess) -> str:
        self.writes.append((dict(value), access))
        return "experience:1"


def _binding(memory: RecordingMemory, *, category: str, action: str, query: str = "") -> MemoryBinding:
    key = b"m8-turn-loop-authority"
    grant = {
        "grantRef": f"grant-{category}",
        "issuer": "authority",
        "subject": "agent-1",
        "tenant": "tenant-1",
        "project": "project-1",
        "actions": [action],
        "purpose": "m8-test",
        "expiresAt": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        "revocationEpoch": 1,
        "selector": {"category": category},
    }
    signature = hmac.new(key, digest_of(grant).encode("ascii"), hashlib.sha256).hexdigest()
    return MemoryBinding(
        port=memory,
        authorization=MemoryAuthorizationPort(key),
        grant=grant,
        signature=signature,
        tenant="tenant-1",
        project="project-1",
        selector={"category": category},
        query=query,
    )


class M8TurnLoopIntegration(unittest.TestCase):
    def test_authorized_memory_is_compiled_into_each_turn_and_success_is_recorded(self) -> None:
        memory = RecordingMemory()
        store = SqliteEventStore(":memory:")
        harness = Runtime.compose("vg-code-default", episode_id="m8-turn")
        task = TaskContext(
            brief="use the memory fact",
            repo_path=Path("/workspace"),
            run_id="m8-run",
            episode_id="m8-turn",
            principal="agent-1",
            project_id="project-1",
            max_turns=2,
        )
        session = HarnessSession(
            harness,
            SessionPorts(
                model=ScriptedModel([finish()]),
                environment=FakeEnvironment(),
                clock=FakeClock(),
                store=store,
                interactive=False,
                memory=_binding(memory, category="knowledge", action="read", query="fact"),
                experience=_binding(memory, category="experience", action="write"),
            ),
            task,
        )

        result = session.run()

        self.assertEqual(result.terminal.value, "completed")
        self.assertEqual(len(memory.reads), 1)
        model_context = session.operator.contexts[0]
        self.assertIn("authorized memory fact", str(model_context["messages"]))
        self.assertEqual(len(memory.writes), 1)
        fact, access = memory.writes[0]
        self.assertEqual(fact["kind"], "episode_outcome")
        self.assertEqual(fact["causal"]["episodeId"], "m8-turn")
        self.assertEqual(access.project, "project-1")

    def test_memory_text_without_a_complete_result_is_not_injected(self) -> None:
        class IncompleteMemory(RecordingMemory):
            def recall(self, query: str, access: MemoryAccess, limit: int = 20) -> MemoryResult:
                result = super().recall(query, access, limit)
                return MemoryResult(result.record_ids, result.provenance)

        memory = IncompleteMemory()
        harness = Runtime.compose("vg-code-default", episode_id="m8-invalid")
        session = HarnessSession(
            harness,
            SessionPorts(
                model=ScriptedModel([finish()]),
                environment=FakeEnvironment(),
                clock=FakeClock(),
                store=SqliteEventStore(":memory:"),
                interactive=False,
                memory=_binding(memory, category="knowledge", action="read", query="fact"),
            ),
            TaskContext(brief="memory", repo_path=Path("/workspace"), episode_id="m8-invalid"),
        )

        result = session.run()

        self.assertEqual(result.terminal.value, "instrument_error")
        self.assertNotIn("authorized memory fact", str(session.operator.contexts))


if __name__ == "__main__":
    unittest.main()
