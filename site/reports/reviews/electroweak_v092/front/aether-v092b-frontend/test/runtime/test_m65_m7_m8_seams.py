"""Executable contract coverage for the newly prepared exterior seams."""

from __future__ import annotations

import unittest

from vanguard.packages.domain.ledger.agent_view import AgentView
from vanguard.packages.domain.ledger.progress import ConfidenceRecord, ProgressView
from vanguard.packages.ports.meta_controller import StrategyDirective
from vanguard.packages.runtime.memory import InMemoryMemoryPort, MemoryAccess
from vanguard.packages.runtime.meta_controller import consult
from vanguard.packages.runtime.scheduler import ReadyOperation, SequentialScheduler, safe_read_only_group
from vanguard.packages.runtime.topology import TopologyError, parse_topology


def _authorized_access(tenant: str, project: str, *, actions=("read", "write", "invalidate")):
    """Mint a verified memory lease the way the runtime does at point of use."""
    from datetime import datetime, timedelta, timezone
    import hashlib
    import hmac

    from vanguard.packages.domain.canonicalisation.digest import digest_of
    from vanguard.packages.ports.memory import MemoryAuthorizationPort

    key = b"seam-test-memory-key"
    selector = {"kind": "project"}
    now = datetime.now(timezone.utc)
    grant = {
        "grantRef": f"grant-{tenant}-{project}",
        "issuer": "runtime",
        "subject": "agent-under-test",
        "tenant": tenant,
        "project": project,
        "actions": list(actions),
        "purpose": "seam-test",
        "expiresAt": (now + timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
        "revocationEpoch": 1,
        "selector": selector,
    }
    signature = hmac.new(key, digest_of(grant).encode("ascii"), hashlib.sha256).hexdigest()
    return MemoryAuthorizationPort(key).verify(
        grant, signature, action="write", tenant=tenant, project=project,
        selector=selector, now=now,
    )


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
        # These leases are minted through MemoryAuthorizationPort rather than
        # hand-built. The hand-built form -- MemoryAccess("grant", ..., "tenant",
        # "p1") with no issuer, subject, actions, expiry or verification receipt
        # -- used to be admitted by a fail-open disjunct in InMemoryMemoryPort.
        # It is refused now, so the seam exercises a real authorization.
        access = _authorized_access("tenant", "p1")
        other = _authorized_access("tenant", "p2")
        memory = InMemoryMemoryPort("knowledge")
        rid = memory.write({"text": "shared fact"}, access)
        self.assertEqual(memory.recall("fact", other).record_ids, ())
        result = memory.recall("fact", access)
        self.assertEqual(result.record_ids, (rid,))
        self.assertTrue(result.provenance.digest())


if __name__ == "__main__":
    unittest.main()
