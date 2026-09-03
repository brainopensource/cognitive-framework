"""RF-96: AgentView survives process destruction and fresh-process replay."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.ledger.agent_view import fold_agent_view
from vanguard.packages.domain.ledger.events import EventEnvelope

ROOT = Path(__file__).resolve().parents[2]


def _event(seq: int, kind: str, **payload: object) -> EventEnvelope:
    return EventEnvelope(
        schema_version="mhf.event/2",
        event_id=f"rf96-{seq}",
        scope="episode",
        seq=str(seq),
        occurred_at=f"2026-08-25T00:00:{seq:02d}.000Z",
        recorded_at=f"2026-08-25T00:00:{seq:02d}.000Z",
        principal="agent-1",
        principal_role="episode",
        tenant_id="tenant-default",
        owner_id="owner-platform",
        confidentiality="internal",
        retention_class="standard",
        trainability="prohibited",
        redaction_status="none",
        payload={"kind": kind, **payload},
        run_id="rf96-run",
        episode_id="rf96-episode",
        project_id="rf96-project",
        principal_id="rf96-lineage",
        authority_source="orchestrator-policy",
        policy_version="rf96-test",
    )


class ColdReconstruction(unittest.TestCase):
    def test_fresh_process_rebuilds_identical_agent_view_from_wal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db_path = str(Path(directory) / "rf96.sqlite")
            writer = SqliteEventStore(db_path)
            writer.append([
                _event(0, "GoalDeclared", goalDigest="sha256:" + "a" * 64),
                _event(1, "PlanRevised", revision=0, planDigest="sha256:" + "b" * 64),
                _event(2, "ProposalProduced", operationId="op-1", verb="proc.exec"),
                _event(3, "EffectFailed", operationId="op-1", idempotencyKey="idem-1", outcome="failed"),
                _event(4, "StrategyChanged", **{"from": "depth", "to": "breadth", "trigger": "regressing"}),
                _event(5, "ProgressAssessed", assessment="stalled", signals={"tests": "red"}, basis=["rf96-3"]),
                _event(6, "ContextCompacted", inputDigest="sha256:" + "c" * 64, outputDigest="sha256:" + "d" * 64),
                _event(7, "EpisodeCompleted", outcome="abandoned"),
            ])
            local = fold_agent_view(None, list(writer.read().value or ()))
            writer.close()

            script = (
                "import sys; "
                "from vanguard.packages.adapters.stores.event_store import SqliteEventStore; "
                "from vanguard.packages.domain.ledger.agent_view import fold_agent_view; "
                "s=SqliteEventStore(sys.argv[1]); "
                "v=fold_agent_view(None, list(s.read().value or ())); "
                "print(v.digest())"
            )
            result = subprocess.run(
                [sys.executable, "-c", script, db_path],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), local.digest())


if __name__ == "__main__":
    unittest.main()
