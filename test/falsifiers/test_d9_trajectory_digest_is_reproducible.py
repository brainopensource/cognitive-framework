"""D9: a trajectory's `state_digest` must be reproducible from the durable log.

RF-100 separates capability from proof: a `verified` reconstruction needs a
receipt bound to the run. The receipt here is the state digest -- a fresh
process folds the events the trajectory names and compares. That only works if
the recorded digest is the fold of the recorded range.

It was not. Two bugs compounded:

* the digest folded the *pending terminal event* in. That event's payload
  carries the trajectory, which carries the digest, so the value summarised a
  state containing itself -- unreproducible by construction;
* it was then overwritten a few lines later with a third value taken after the
  terminal event had been appended.

So the number in `state_digest` matched no fold of the log at any prefix, and
reconstruction had nothing honest to check against. This pins the fix: the
digest is the fold of exactly `event_range`.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.stores.blob_store import FileBlobStore
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.ledger.reducer import compute_state_digest, reconstruct_state
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.compose import TaskContext
from vanguard.packages.runtime.governance.approvals import OperatorSigner
from vanguard.packages.runtime.root import Runtime

from test.agency.doubles import ScriptedModel, finish

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "packs/formal-sat"


class TrajectoryDigestMatchesItsDeclaredRange(unittest.TestCase):
    def _run(self, repo: Path):
        for argv in (["git", "init", "-b", "main"],
                     ["git", "config", "user.email", "d9@test"],
                     ["git", "config", "user.name", "d9"]):
            subprocess.run(argv, cwd=repo, capture_output=True, check=True)
        (repo / "formula.cnf").write_text(
            (PACK / "tasks/sat-001.cnf").read_text(encoding="utf-8"), encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "i"], cwd=repo,
                       capture_output=True, check=True)
        signer = OperatorSigner(b"vanguard-autonomous-operator-seed-key")
        script = [
            {"kind": "effect", "action": "patch.apply",
             "resource": {"kind": "fs", "root": str(repo),
                          "paths": [str(repo / "witness.json")]},
             "args": {"path": "witness.json",
                      "content": '{"assignment": {"1": true, "2": true}}'},
             "text": ""},
            finish("witness written"),
        ]
        db = repo / ".vanguard" / "events.sqlite3"
        result = Runtime.execute_profiled(
            str(PACK),
            TaskContext(brief="write witness.json", repo_path=repo, run_id="r-d9",
                        episode_id="e-d9", principal="agent-1", max_turns=4),
            profile_id="product",
            model=ScriptedModel(script),
            store_path=str(db),
            blobs=FileBlobStore(repo / ".vanguard" / "blobs"),
            interactive=True,
            approver=lambda c: signer.approve(c, reviewer="autonomous-operator"),
            approval_key=signer.public_bytes,
        )
        events = list(SqliteEventStore(db).read(
            EventRange(episode_id="e-d9")).value or [])
        trajectory = next(
            e.payload["trajectory"] for e in events
            if e.payload.get("kind") == "EpisodeCompleted")
        return result, events, trajectory

    def test_a_fresh_fold_of_the_declared_range_reproduces_the_digest(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _, events, trajectory = self._run(repo)
            last = trajectory["event_range"]["last_seq"]
            named = [e for e in events if int(e.seq) <= int(last)]
            reproduced = compute_state_digest(reconstruct_state(named))

        self.assertEqual(reproduced, trajectory["state_digest"])

    def test_the_declared_count_matches_the_events_actually_named(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _, events, trajectory = self._run(repo)
            rng = trajectory["event_range"]
            named = [e for e in events if int(e.seq) <= int(rng["last_seq"])]

        self.assertEqual(len(named), rng["count"])

    def test_the_range_stops_before_the_event_that_carries_the_trajectory(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _, events, trajectory = self._run(repo)
            terminal = next(e for e in events
                            if e.payload.get("kind") == "EpisodeCompleted")
            last = int(trajectory["event_range"]["last_seq"])

        # A digest that included the terminal event would summarise a state
        # containing itself. The range must stop short of it.
        self.assertLess(last, int(terminal.seq))

    def test_the_digest_is_not_the_fold_of_the_whole_log(self) -> None:
        # Guards the obvious "fix": folding everything makes the self-reference
        # come straight back.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _, events, trajectory = self._run(repo)
            whole = compute_state_digest(reconstruct_state(events))

        self.assertNotEqual(whole, trajectory["state_digest"])


if __name__ == "__main__":
    unittest.main()
