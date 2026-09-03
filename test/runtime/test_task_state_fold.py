"""T-10 / T-43 / T-44: one runtime fold, unknown ignored, resume parity."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from vanguard.packages.runtime.task_state import fold_task_state

ROOT = Path(__file__).resolve().parents[2]


def _event(kind: str, *, episode_id: str = "ep-real", **payload: object) -> SimpleNamespace:
    body = {"kind": kind, **payload}
    return SimpleNamespace(
        kind=kind,
        mhf_kind=kind,
        payload=body,
        episode_id=episode_id,
        run_id="run-1",
    )


class TestTaskStateFold(unittest.TestCase):
    def test_unknown_events_are_ignored(self) -> None:
        state = fold_task_state(
            [
                _event("EpisodeStarted", brief="keep going", budgetCeiling={"tokens": 9}),
                _event("TotallyUnknownKind", garbage=True, plan=["should-not-apply-via-kind-alone"]),
            ],
            objective="keep going",
        )
        self.assertEqual(state.objective, "keep going")
        self.assertEqual(state.plan, ())

    def test_proposal_does_not_infer_verification_from_test_substring(self) -> None:
        state = fold_task_state(
            [
                _event("EpisodeStarted", brief="fix it"),
                _event(
                    "ProposalProduced",
                    action="contest_notes",
                    diagnostics={"exit_code": 0, "invented": True},
                ),
            ],
            objective="fix it",
        )
        self.assertEqual(state.next_action, "contest_notes")
        self.assertEqual(dict(state.last_verification), {})

    def test_classified_hypothesis_and_obligation_events_fold(self) -> None:
        state = fold_task_state(
            [
                _event("EpisodeStarted", brief="repair parser", episodeId="ep-real"),
                _event("TaskClassified", taskClass="bugfix"),
                _event("HypothesisOpened", hypothesis="null deref in parser"),
                _event("HypothesisSupported", hypothesis="null deref in parser"),
                _event("HypothesisRejected", hypothesis="encoding mismatch"),
                _event("ObligationOpened", todoId="verify", description="run focused tests"),
                _event("ObligationSatisfied", todoId="verify", receiptDigest="sha256:ok"),
                _event("DeadEndRecorded", attempt="regex-only", reason="missed escapes"),
                _event("ChangeSurfaceUpdated", changeSurface=["src/parser.py"]),
                _event("VerificationRecorded", exit_code=0, executed_test_count=3),
                _event("NextActionSelected", nextAction="finish"),
            ],
            objective="repair parser",
        )
        self.assertEqual(state.task_class, "bugfix")
        self.assertIn("null deref in parser", state.hypotheses)
        self.assertIn("encoding mismatch", state.falsified_hypotheses)
        self.assertEqual(state.todo_items[0].status, "complete")
        self.assertEqual(state.change_surface, ("src/parser.py",))
        self.assertEqual(state.last_verification.get("exit_code"), 0)
        self.assertEqual(state.next_action, "finish")
        self.assertGreaterEqual(state.revision, 1)

    def test_revision_is_monotonic_across_prefixes(self) -> None:
        events = [
            _event("EpisodeStarted", brief="goal"),
            _event("TaskClassified", taskClass="feature"),
            _event("PlanDeclared", plan=["inspect", "patch"]),
            _event("HypothesisOpened", hypothesis="h1"),
        ]
        revisions = [fold_task_state(events[:k], objective="goal").revision for k in range(1, 5)]
        self.assertEqual(revisions, sorted(revisions))
        self.assertGreater(revisions[-1], revisions[0])

    def test_resume_after_patch_matches_uninterrupted_fold(self) -> None:
        prefix = [
            _event("EpisodeStarted", brief="goal"),
            _event("TaskClassified", taskClass="bugfix"),
            _event("EffectCompleted", action="patch.apply", path="src/a.py",
                   descriptorDigest="sha256:" + "b" * 64),
        ]
        suffix = [
            _event("ObservationProduced", path="src/a.py"),
            _event("NextActionSelected", nextAction="verify"),
        ]
        continuous = fold_task_state(prefix + suffix, objective="goal")
        resumed = fold_task_state(prefix + suffix, objective="goal")
        self.assertEqual(continuous.digest(), resumed.digest())
        self.assertIn("src/a.py", continuous.modified_files)

    def test_resume_after_verification_matches_uninterrupted_fold(self) -> None:
        events = [
            _event("EpisodeStarted", brief="goal"),
            _event("EffectCompleted", action="patch.apply", path="src/a.py"),
            _event("VerificationCompleted", exit_code=0, executed_test_count=4),
            _event("NextActionSelected", nextAction="finish"),
        ]
        self.assertEqual(
            fold_task_state(events, objective="goal").digest(),
            fold_task_state(events, objective="goal").digest(),
        )
        state = fold_task_state(events, objective="goal")
        self.assertEqual(state.last_verification.get("executed_test_count"), 4)

    def test_forty_turn_fresh_process_fold_parity(self) -> None:
        events = [_event("EpisodeStarted", brief="long run", episodeId="ep-40")]
        for turn in range(40):
            events.append(_event("ProposalProduced", action=f"step-{turn}", turn=turn))
            if turn % 7 == 0:
                events.append(_event(
                    "EffectCompleted", action="patch.apply",
                    path=f"src/f{turn}.py", descriptorDigest=f"sha256:{turn:064d}",
                ))
            if turn % 11 == 0:
                events.append(_event(
                    "VerificationRecorded", exit_code=0, executed_test_count=turn + 1,
                ))
            if turn % 13 == 0:
                events.append(_event("HypothesisRejected", hypothesis=f"dead-{turn}"))
        in_process = fold_task_state(events, objective="long run")

        payload = [{"payload": dict(event.payload), "episodeId": event.episode_id,
                    "runId": getattr(event, "run_id", "run-1")} for event in events]

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "events.json"
            source.write_text(json.dumps(payload), encoding="utf-8")
            script = r"""
import json, sys
from types import SimpleNamespace
from vanguard.packages.runtime.task_state import fold_task_state
raw = json.loads(open(sys.argv[1], encoding="utf-8").read())
events = []
for item in raw:
    body = item.get("payload") or item
    events.append(SimpleNamespace(
        kind=body.get("kind", ""), mhf_kind=body.get("kind", ""),
        payload=body, episode_id=item.get("episodeId"),
        run_id=item.get("runId") or "run-1"))
state = fold_task_state(events, objective="long run")
print(state.digest())
print(state.revision)
print(state.task_class)
"""
            env = {**os.environ, "PYTHONPATH": str(ROOT)}
            ran = subprocess.run(
                [sys.executable, "-c", script, str(source)],
                cwd=ROOT, env=env, check=False, capture_output=True, text=True,
            )
            self.assertEqual(ran.returncode, 0, ran.stdout + ran.stderr)
            digest, revision, _task_class = ran.stdout.strip().splitlines()
            self.assertEqual(digest, in_process.digest())
            self.assertEqual(int(revision), in_process.revision)


if __name__ == "__main__":
    unittest.main()
