"""Hermetic tests for TrajectoryReader and diff_trajectories (M4-04)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from vanguard.packages.runtime.trajectory_reader import (
    TrajectoryDiff,
    TrajectoryReader,
    diff_trajectories,
)


def _sample_trajectory(
    *,
    run_id: str = "run-101",
    model: str = "openrouter/free",
    tokens: int = 150,
    outcome: str = "completed",
    harness_digest: str = "sha256:harness-aaa",
) -> dict[str, Any]:
    return {
        "schema": "mhf.trajectory/1",
        "project_id": "project-test",
        "run_id": run_id,
        "episode_id": f"episode-{run_id}",
        "harness_digest": harness_digest,
        "run_digest": f"sha256:run-digest-{run_id}",
        "activation_digest": "sha256:activation-aaa",
        "task_digest": "sha256:task-aaa",
        "preregistration_digest": "sha256:prereg-aaa",
        "state_digest": "sha256:state-aaa",
        "model_routes_used": [{"tier": 1, "provider": "openrouter", "model": model}],
        "turns": [
            {
                "turn": 0,
                "context_digest": "sha256:ctx-0",
                "proposal": {"requests": [{"verb": "fs.read", "args": {"path": "src/app.py"}}]},
                "receipts": [{"outcome": "ok", "descriptor_digest": "sha256:req-0"}],
                "cost": {"usd_micros": 10, "tokens": tokens // 2, "bytes": 100, "millis": 50},
                "model_route": {"provider": "openrouter", "model": model},
            },
            {
                "turn": 1,
                "context_digest": "sha256:ctx-1",
                "proposal": {"requests": [{"verb": "proc.exec", "args": {"argv": ["pytest"]}}]},
                "receipts": [{"outcome": "ok", "descriptor_digest": "sha256:req-1"}],
                "cost": {"usd_micros": 10, "tokens": tokens // 2, "bytes": 100, "millis": 50},
                "model_route": {"provider": "openrouter", "model": model},
            },
        ],
        "verdict": {"verdict": "pass", "oracle_id": "oracle-1"},
        "verdict_absence_reason": None,
        "cost": {
            "usd_micros": 20,
            "tokens": tokens,
            "bytes": 200,
            "millis": 100,
            "measurement_status": {
                "usd_micros": {"status": "measured", "reason": None},
                "tokens": {"status": "measured", "reason": None},
                "bytes": {"status": "measured", "reason": None},
                "millis": {"status": "measured", "reason": None},
            },
        },
        "outcome": outcome,
    }


class TestTrajectoryReader(unittest.TestCase):
    def test_load_from_mapping(self) -> None:
        raw = _sample_trajectory()
        loaded = TrajectoryReader.load(raw)
        self.assertEqual(loaded["schema"], "mhf.trajectory/1")
        self.assertEqual(loaded["run_id"], "run-101")

    def test_load_from_json_file(self) -> None:
        raw = _sample_trajectory()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tf:
            json.dump(raw, tf)
            tf.flush()
            loaded = TrajectoryReader.load(tf.name)
            self.assertEqual(loaded["run_id"], "run-101")

    def test_load_from_jsonl_event_log(self) -> None:
        raw = _sample_trajectory()
        event = {
            "kind": "EpisodeCompleted",
            "seq": 10,
            "payload": {"trajectory": raw, "outcome": "completed"},
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as tf:
            tf.write(json.dumps({"kind": "RunStarted", "seq": 1, "payload": {}}) + "\n")
            tf.write(json.dumps(event) + "\n")
            tf.flush()
            loaded = TrajectoryReader.load(tf.name)
            self.assertEqual(loaded["run_id"], "run-101")

    def test_extract_variables(self) -> None:
        raw = _sample_trajectory()
        vars_dict = TrajectoryReader.extract_variables(raw)
        self.assertEqual(vars_dict["schema"], "mhf.trajectory/1")
        self.assertEqual(vars_dict["harness_digest"], "sha256:harness-aaa")
        self.assertEqual(vars_dict["turns_count"], 2)
        self.assertEqual(len(vars_dict["turns"]), 2)
        self.assertEqual(vars_dict["cost"]["tokens"], 150)

    def test_diff_identical_trajectories_matches(self) -> None:
        t1 = _sample_trajectory(run_id="run-1")
        t2 = _sample_trajectory(run_id="run-2")
        diff = diff_trajectories(t1, t2)
        # run_id and run_digest are allowed to differ across runs without violating match
        # if other execution variables match
        self.assertEqual(diff.left_run_id, "run-1")
        self.assertEqual(diff.right_run_id, "run-2")

    def test_diff_detects_differing_variables(self) -> None:
        t1 = _sample_trajectory(run_id="run-1", model="model-a", tokens=100, outcome="completed")
        t2 = _sample_trajectory(run_id="run-2", model="model-b", tokens=200, outcome="aborted")
        diff = diff_trajectories(t1, t2)
        self.assertFalse(diff.match)
        self.assertIn("model_routes_used", diff.differing_variables)
        self.assertIn("cost.tokens", diff.differing_variables)
        self.assertIn("outcome", diff.differing_variables)
        self.assertEqual(diff.details["outcome"]["left"], "completed")
        self.assertEqual(diff.details["outcome"]["right"], "aborted")


if __name__ == "__main__":
    unittest.main()
