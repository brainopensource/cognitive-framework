"""Falsifiers for the truthful M-8 benchmark driver."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from benchmarks.m8_heldout.runner import (
    BudgetLimits,
    Disposition,
    TaskAttempt,
    WorkloadDefinition,
    execute_empirical_run,
    load_workload,
    verify_bundle,
)
from vanguard.packages.ports.evaluator import Verdict
from vanguard.packages.ports.event_store import Result


PATCH = """--- a/src/value.py
+++ b/src/value.py
@@ -1 +1 @@
-value = 1
+value = 2
"""


class _Executor:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def execute(self, task, workspace, arm):
        self.calls += 1
        return self.result(task, workspace, arm) if callable(self.result) else self.result


class _Evaluator:
    def __init__(self, verdict):
        self.verdict = verdict
        self.calls = []

    def evaluate(self, run_ref, protocol):
        self.calls.append((run_ref, protocol))
        return Result.success(self.verdict)


class M8HeldOutBenchmarkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workload, self.tasks_meta = load_workload()

    def test_workload_splits_and_counts(self) -> None:
        self.assertEqual((len(self.workload.dev), len(self.workload.held_out),
                          len(self.workload.adversarial), len(self.workload.transfer)), (2, 40, 1, 1))
        self.assertEqual(len(self.tasks_meta), 44)

    def test_preregistration_artifact_integrity(self) -> None:
        data = json.loads(Path("benchmarks/m8_heldout/artifacts/preregistration.json").read_text())
        self.assertEqual(data["schema"], "aether.m8-preregistration/1")
        self.assertEqual(data["split_counts"]["total_unique_tasks"], 44)
        self.assertEqual(data["attempt_policy"]["max_attempts"], 1)
        self.assertEqual(data["workload_digest"], self.workload.digest())

    def test_workload_rejects_contamination(self) -> None:
        with self.assertRaises(ValueError):
            WorkloadDefinition(dev=("dev_01", "held_out_01"), held_out=self.workload.held_out)

    def test_dry_run_is_structural_only_and_has_no_fake_trajectory(self) -> None:
        executor = _Executor(TaskAttempt(patch=PATCH))
        bundle = execute_empirical_run(self.workload, self.tasks_meta, executor=executor)
        self.assertEqual(bundle["evidenceKind"], "structural_preflight")
        self.assertIsNone(bundle["empirical"]["success"])
        self.assertIsNone(bundle["evaluation"]["promotable"])
        self.assertIsNone(bundle["promotionEvidence"])
        self.assertTrue(all(row["disposition"] == "NOT_RUN" for row in bundle["records"]))
        self.assertTrue(all(row["trajectoryDigest"] is None for row in bundle["records"]))
        self.assertEqual(executor.calls, 0)
        self.assertTrue(verify_bundle(bundle))

    def test_non_empty_prose_is_no_patch(self) -> None:
        executor = _Executor(TaskAttempt(output="I inspected the repository and have a plan."))
        evaluator = _Evaluator(Verdict(outcome="claims", claims=({"passed": True, "tests_collected": 1},)))
        bundle = execute_empirical_run(self.workload, self.tasks_meta, mode="live", executor=executor, evaluator=evaluator)
        self.assertEqual(bundle["records"][0]["disposition"], Disposition.NO_PATCH.value)
        self.assertEqual(len(evaluator.calls), 0)

    def test_malformed_task_is_rejected_before_model_call(self) -> None:
        executor = _Executor(TaskAttempt(patch=PATCH))
        metadata = [task for task in self.tasks_meta if task["id"] != "held_out_01"]
        bundle = execute_empirical_run(self.workload, metadata, mode="live", executor=executor, evaluator=_Evaluator(Verdict("inconclusive")))
        self.assertEqual(bundle["disposition"], Disposition.INVALID_TASK.value)
        self.assertEqual(executor.calls, 0)

    def test_valid_patch_failing_evaluator_is_not_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src/value.py").write_text("value = 1\n")
            evaluator = _Evaluator(Verdict(outcome="claims", claims=({"passed": False, "tests_collected": 2},)))
            bundle = execute_empirical_run(self.workload, self.tasks_meta, mode="live",
                                           executor=_Executor(TaskAttempt(patch=PATCH, trajectory_digest="sha256:real")),
                                           evaluator=evaluator, workspace_root=root)
            self.assertEqual(bundle["records"][0]["disposition"], Disposition.EVALUATOR_FAILED.value)
            self.assertEqual(bundle["records"][0]["trajectoryDigest"], "sha256:real")

    def test_zero_tests_cannot_pass(self) -> None:
        evaluator = _Evaluator(Verdict(outcome="claims", claims=({"passed": True, "tests_collected": 0},)))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src/value.py").write_text("value = 1\n")
            bundle = execute_empirical_run(self.workload, self.tasks_meta, mode="live",
                                           executor=_Executor(TaskAttempt(patch=PATCH)), evaluator=evaluator,
                                           workspace_root=root)
        self.assertEqual(bundle["records"][0]["disposition"], Disposition.EVALUATOR_FAILED.value)

    def test_provider_absence_is_typed(self) -> None:
        def unavailable(task, workspace, arm):
            raise ConnectionError("provider unavailable")
        bundle = execute_empirical_run(self.workload, self.tasks_meta, mode="live",
                                       executor=_Executor(unavailable), evaluator=_Evaluator(Verdict("inconclusive")))
        self.assertEqual(bundle["records"][0]["disposition"], Disposition.PROVIDER_UNAVAILABLE.value)

    def test_budget_is_checked_before_call(self) -> None:
        executor = _Executor(TaskAttempt(patch=PATCH))
        bundle = execute_empirical_run(self.workload, self.tasks_meta, mode="live", executor=executor,
                                       evaluator=_Evaluator(Verdict("inconclusive")),
                                       limits=BudgetLimits(aggregate_turns=0))
        self.assertEqual(bundle["records"][0]["disposition"], Disposition.BUDGET_EXHAUSTED.value)
        self.assertEqual(executor.calls, 0)

    def test_second_episode_request_is_rejected(self) -> None:
        bundle = execute_empirical_run(self.workload, self.tasks_meta, mode="live",
                                       executor=_Executor(TaskAttempt(patch=PATCH, attempts=2)),
                                       evaluator=_Evaluator(Verdict("inconclusive")))
        self.assertEqual(bundle["records"][0]["disposition"], Disposition.MODEL_PROTOCOL_ERROR.value)
        self.assertEqual(bundle["records"][0]["routeIdentity"]["failure"], "second_episode_rejected")

    def test_bundle_tampering_is_detected(self) -> None:
        bundle = execute_empirical_run(self.workload, self.tasks_meta)
        for field in ("taskDigest", "baseCommit", "patchDigest", "trajectoryDigest"):
            tampered = copy.deepcopy(bundle)
            tampered["records"][0][field] = "tampered"
            self.assertFalse(verify_bundle(tampered), field)


if __name__ == "__main__":
    unittest.main()
