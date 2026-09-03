"""RF-25 / NOVA-2: hard-death continuation from a file-backed SQLite WAL."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.ledger.reducer import reconstruct_state
from vanguard.packages.ports.event_store import EventRange

ROOT = Path(__file__).resolve().parents[2]

_CRASH_WRITER = r"""
import os, sys
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.kernel.model import Event
from vanguard.packages.runtime.determinism import FixedClock, SeededRandom
from vanguard.packages.runtime.ledger_emitter import LedgerEmitter
from vanguard.packages.runtime.root import Runtime

db = sys.argv[1]
harness = Runtime.compose("vg-code-default", episode_id="ep-rf25")
store = SqliteEventStore(db)
emitter = LedgerEmitter(
    store, episode_id="ep-rf25", project_id="project-rf25",
    principal_id="agent-rf25", harness_digest=harness.composition_digest,
    clock=FixedClock(at="2026-08-21T12:00:00.000Z", step_ms=1),
    random=SeededRandom(seed=25), role="kernel")

def emit(kind, payload):
    emitter.emit(Event(kind=kind, reason="rf25", at="2026-08-21T12:00:00.000Z",
                       run_id="run-rf25", principal="agent-rf25", payload=payload))

emit("EpisodeStarted", {"kind": "EpisodeStarted", "episodeId": "ep-rf25",
                         "compositionDigest": harness.composition_digest})
emit("ProposalProduced", {"kind": "ProposalProduced", "episodeId": "ep-rf25",
                           "turn": 0, "proposalDigest": "sha256:" + "1" * 64})
emit("BudgetReserved", {"kind": "BudgetReserved", "leaseId": "lease-rf25",
                         "dimensions": {"tokens": 20}, "limits": {"tokens": 20}})
emit("BudgetCommitted", {"kind": "BudgetCommitted", "leaseId": "lease-rf25",
                          "debits": {"tokens": 7}})
emitter.append_intent(Event(
    kind="EffectStarted", reason="s8a", at="2026-08-21T12:00:00.000Z",
    run_id="run-rf25", principal="agent-rf25",
    payload={"kind": "EffectStarted", "idempotencyKey": "effect-rf25",
             "descriptorDigest": "sha256:" + "2" * 64}))
os._exit(91)
"""

_FRESH_CONTINUER = r"""
import sys
from pathlib import Path
from test.agency.doubles import ScriptedModel, finish
from test.runtime.test_harness_session import FakeClock, FakeEnvironment
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.runtime.root import HarnessSession, Runtime, SessionPorts, TaskContext

db = sys.argv[1]
harness = Runtime.compose("vg-code-default", episode_id="ep-rf25")
store = SqliteEventStore(db)
session = HarnessSession(
    harness,
    SessionPorts(model=ScriptedModel([finish("continue after recovery")]),
                 environment=FakeEnvironment(), clock=FakeClock(), store=store,
                 interactive=False),
    TaskContext(brief="continue", repo_path=Path("/workspace"),
                project_id="project-rf25", run_id="run-rf25",
                episode_id="ep-rf25", principal="agent-rf25", max_turns=4))
session.run()
store.close()
"""


class RF25ColdContinuation(unittest.TestCase):
    """Primary M-2 recovery gate from ADR-0082; intentionally red pre-NOVA-2."""

    def test_hard_death_folds_reconciles_and_continues_in_fresh_interpreter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "rf25.sqlite3"
            env = {**os.environ, "PYTHONPATH": str(ROOT)}

            crashed = subprocess.run(
                [sys.executable, "-c", _CRASH_WRITER, str(db)],
                cwd=ROOT,
                env=env,
                check=False,
            )
            self.assertEqual(crashed.returncode, 91, "fixture must die after durable S8a")

            continued = subprocess.run(
                [sys.executable, "-c", _FRESH_CONTINUER, str(db)],
                cwd=ROOT,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                continued.returncode,
                0,
                (continued.stdout or "") + (continued.stderr or ""),
            )

            store = SqliteEventStore(db)
            read = store.read(EventRange(run_id="run-rf25"))
            self.assertTrue(read.ok)
            events = list(read.value or ())
            state = reconstruct_state(events)
            store.close()
            kinds = [event.payload.get("kind") or event.mhf_kind for event in events]

            failures: list[str] = []
            if kinds.count("EpisodeStarted") != 1:
                failures.append("continuation repeated EpisodeStarted")
            if kinds.count("EffectStarted") != 1:
                failures.append("continuation repeated the open effect intent")
            if "EffectReconciled" not in kinds:
                failures.append("open S8a intent was not reconciled as undeterminable")
            if "RunRecovered" not in kinds:
                failures.append("fresh controller did not ledger RunRecovered")
            if kinds.count("EpisodeCompleted") != 1:
                failures.append("continued episode must terminate exactly once")
            if state.cumulative_budget_debits.get("tokens") != 7:
                failures.append("cold continuation did not preserve committed budget debits")
            effect = state.effects.get("sha256:" + "2" * 64)
            if effect is None or effect.outcome != "undeterminable":
                failures.append("uncertain effect was not durably classified undeterminable")

            self.assertEqual(failures, [], "RF-25 remains red:\n- " + "\n- ".join(failures))


if __name__ == "__main__":
    unittest.main()
