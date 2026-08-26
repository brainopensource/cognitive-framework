"""Executable contract coverage for the newly prepared exterior seams."""

from __future__ import annotations

import unittest

from vanguard.packages.domain.ledger.agent_view import AgentView
from vanguard.packages.domain.ledger.progress import ConfidenceRecord, ProgressView
from vanguard.packages.ports.meta_controller import StrategyDirective
from vanguard.packages.runtime.memory import InMemoryMemoryPort, MemoryAccess
from vanguard.packages.runtime.meta_controller import consult
from vanguard.packages.runtime.scheduler import ReadyOperation, SequentialScheduler, safe_read_only_group
from vanguard.packages.runtime.skill_lifecycle import CompositionRegistry, EvaluationReport, PromotionEvidence
from vanguard.packages.runtime.topology import TopologyError, parse_topology


class SeamsTests(unittest.TestCase):
    def test_controller_is_opt_in_and_attributed(self) -> None:
        self.assertIsNone(consult(None, AgentView("a"), ProgressView()))

        class Controller:
            controller_id = "c"
            def assess(self, view, progress, confidence):
                return StrategyDirective("request_context", "c", "missing knowledge")

        record = ConfidenceRecord("behavioral", .4, "goal", ("event-1",), {"method": "held-out"})
        proposal = consult(Controller(), AgentView("a"), ProgressView(), (record,))
        self.assertEqual(proposal.kind, "request_context")
        self.assertEqual(proposal.attribution["confidenceRefs"], (record.digest(),))

    def test_topology_rejects_cycles_and_scheduler_is_sequential(self) -> None:
        raw = {"topologyId": "t", "version": "1", "entryRole": "a",
               "roles": [{"id": "a", "policyRef": "p"}, {"id": "b", "policyRef": "p"}],
               "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "a"}]}
        with self.assertRaises(TopologyError): parse_topology(raw)
        decisions = SequentialScheduler().decide((ReadyOperation("b"), ReadyOperation("a")))
        self.assertEqual(tuple(d.operation_id for d in decisions), ("a", "b"))
        self.assertFalse(any(d.parallel for d in decisions))
        self.assertEqual(safe_read_only_group(()), ())

    def test_memory_isolation_provenance_and_lifecycle_rollback(self) -> None:
        access = MemoryAccess("grant", {"kind": "project"}, "tenant", "p1")
        other = MemoryAccess("grant", {"kind": "project"}, "tenant", "p2")
        memory = InMemoryMemoryPort("knowledge")
        rid = memory.write({"text": "shared fact"}, access)
        self.assertEqual(memory.recall("fact", other).record_ids, ())
        result = memory.recall("fact", access)
        self.assertEqual(result.record_ids, (rid,))
        self.assertTrue(result.provenance.digest())
        registry = CompositionRegistry("v1")
        report = EvaluationReport("c", True, True, True, True, True, "report")
        evidence = PromotionEvidence("c", "report", "operator", "sig", "v1", "v2")
        registry.promote(evidence, report)
        self.assertEqual(registry.rollback(), "v1")


if __name__ == "__main__":
    unittest.main()
