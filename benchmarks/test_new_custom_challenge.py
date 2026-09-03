"""Live validation runner for a brand new, unseen challenge: distributed_task_dag_scheduler."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks._env import load_benchmark_env


from vanguard.packages.runtime.root import (
    Runtime,
    application_service,
    OpenRouterModel,
)

TASK_BRIEF = """Build a Greenfield Asynchronous Task DAG Scheduler in Python under `dag_scheduler/`.

Requirements:
1. Module `dag_scheduler/models.py`:
   - `TaskState` (Enum): `PENDING = "PENDING"`, `RUNNING = "RUNNING"`, `COMPLETED = "COMPLETED"`, `FAILED = "FAILED"`, `SKIPPED = "SKIPPED"`
   - `CycleError` (Exception): inherits from `ValueError`
   - `Task` (dataclass):
     - `task_id: str`
     - `fn: typing.Callable[..., typing.Any]`
     - `dependencies: set[str]` (default empty set)
     - `max_retries: int = 0`
     - `retry_delay_s: float = 0.0`
   - `TaskResult` (dataclass):
     - `task_id: str`
     - `state: TaskState`
     - `result: typing.Any = None`
     - `error: str | None = None`
     - `retries_used: int = 0`

2. Module `dag_scheduler/engine.py`:
   - `DAGScheduler`:
     - `__init__()`: initialize DAG state
     - `add_task(task: Task) -> None`: registers task. Raises `ValueError` if `task.task_id` already exists.
     - `get_task(task_id: str) -> Task`: returns task or raises `KeyError` if not found.
     - `detect_cycles() -> None`: validates dependency graph. Raises `CycleError` if a dependency cycle is detected.
     - `get_critical_path() -> list[str]`: returns the longest dependency path (list of task_ids from root to leaf).
     - `execute_all(concurrency: int = 4) -> dict[str, TaskResult]`:
       - Executes tasks in topological dependency order.
       - If a task raises an Exception, retries up to `task.max_retries`.
       - If all retries fail, marks task as `TaskState.FAILED` with error message.
       - Any downstream task that depends on a failed task must NOT be executed, and must be marked as `TaskState.SKIPPED` with `error="Dependency failed"`.
       - Returns a mapping of `task_id -> TaskResult`.

3. Self-TDD:
   - Create your own test suite (e.g. `tests/test_scheduler.py`) covering all features.
   - Run `test` with `{"argv": ["python3", "-m", "unittest", "discover", "-s", "."]}` to confirm all tests pass before calling `finish`.
"""

ORACLE_TEST_CODE = """
import unittest
from dag_scheduler.models import Task, TaskState, TaskResult, CycleError
from dag_scheduler.engine import DAGScheduler

class TestDAGSchedulerOracle(unittest.TestCase):
    def test_add_and_duplicate(self):
        sched = DAGScheduler()
        t1 = Task(task_id="t1", fn=lambda: 42)
        sched.add_task(t1)
        self.assertEqual(sched.get_task("t1").task_id, "t1")
        with self.assertRaises(ValueError):
            sched.add_task(t1)
        with self.assertRaises(KeyError):
            sched.get_task("nonexistent")

    def test_cycle_detection(self):
        sched = DAGScheduler()
        sched.add_task(Task(task_id="a", fn=lambda: 1, dependencies={"b"}))
        sched.add_task(Task(task_id="b", fn=lambda: 2, dependencies={"c"}))
        sched.add_task(Task(task_id="c", fn=lambda: 3, dependencies={"a"}))
        with self.assertRaises(CycleError):
            sched.detect_cycles()

    def test_diamond_dag_execution(self):
        results_collector = {}
        sched = DAGScheduler()
        sched.add_task(Task(task_id="root", fn=lambda: 10))
        sched.add_task(Task(task_id="branch_a", fn=lambda: 20, dependencies={"root"}))
        sched.add_task(Task(task_id="branch_b", fn=lambda: 30, dependencies={"root"}))
        sched.add_task(Task(task_id="leaf", fn=lambda: 40, dependencies={"branch_a", "branch_b"}))

        res = sched.execute_all(concurrency=2)
        self.assertEqual(len(res), 4)
        self.assertEqual(res["root"].state, TaskState.COMPLETED)
        self.assertEqual(res["root"].result, 10)
        self.assertEqual(res["branch_a"].state, TaskState.COMPLETED)
        self.assertEqual(res["branch_b"].state, TaskState.COMPLETED)
        self.assertEqual(res["leaf"].state, TaskState.COMPLETED)
        self.assertEqual(res["leaf"].result, 40)

    def test_retry_on_failure(self):
        attempts = 0
        def flaky():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise RuntimeError("Transient network issue")
            return "SUCCESS"

        sched = DAGScheduler()
        sched.add_task(Task(task_id="flaky_task", fn=flaky, max_retries=3))
        res = sched.execute_all()
        self.assertEqual(res["flaky_task"].state, TaskState.COMPLETED)
        self.assertEqual(res["flaky_task"].result, "SUCCESS")
        self.assertEqual(res["flaky_task"].retries_used, 2)

    def test_cascading_dependency_skip(self):
        def bad_fn():
            raise ValueError("Fatal failure")

        sched = DAGScheduler()
        sched.add_task(Task(task_id="step1", fn=bad_fn, max_retries=1))
        sched.add_task(Task(task_id="step2", fn=lambda: "ok", dependencies={"step1"}))
        sched.add_task(Task(task_id="step3", fn=lambda: "ok", dependencies={"step2"}))
        sched.add_task(Task(task_id="independent", fn=lambda: "unaffected"))

        res = sched.execute_all()
        self.assertEqual(res["step1"].state, TaskState.FAILED)
        self.assertEqual(res["step2"].state, TaskState.SKIPPED)
        self.assertIn("Dependency failed", res["step2"].error)
        self.assertEqual(res["step3"].state, TaskState.SKIPPED)
        self.assertEqual(res["independent"].state, TaskState.COMPLETED)
        self.assertEqual(res["independent"].result, "unaffected")

    def test_critical_path(self):
        sched = DAGScheduler()
        sched.add_task(Task(task_id="A", fn=lambda: 1))
        sched.add_task(Task(task_id="B", fn=lambda: 2, dependencies={"A"}))
        sched.add_task(Task(task_id="C", fn=lambda: 3, dependencies={"B"}))
        sched.add_task(Task(task_id="D", fn=lambda: 4, dependencies={"A"}))

        crit = sched.get_critical_path()
        self.assertEqual(crit, ["A", "B", "C"])

if __name__ == "__main__":
    load_benchmark_env()
    unittest.main()
"""


def main() -> int:
    print("=" * 80)
    print("CHIMERA SOTA VALIDATION: UNSEEN GREENFIELD TASK DAG SCHEDULER")
    print("=" * 80)

    model_name = "deepseek/deepseek-v4-flash-0731"
    manifest_name = "vg-chimera-v1"

    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        print(f"Isolated Test Workspace: {ws}")

        manifest_path = ROOT / f"vanguard/packages/agency/manifests/{manifest_name}/manifest.json"
        live_model = OpenRouterModel(model=model_name, stream=False, reasoning_effort="none")
        app = application_service(workspace=ws)

        t_start = time.perf_counter()
        print(f"\nLaunching {manifest_name} on unseen challenge via {model_name}...")

        outcome = app.run(
            brief=TASK_BRIEF,
            manifest_path=manifest_path,
            model=live_model,
            interactive=True,
            autonomous_approval=True,
            max_turns=15,
        )

        t_duration = time.perf_counter() - t_start

        print(f"\n[Agent Execution Completed in {t_duration:.2f}s]")
        print(f"Outcome:       {getattr(outcome, 'outcome', outcome)}")
        print(f"Terminal State:{getattr(outcome, 'terminal_state', None)}")
        print(f"Turns:         {getattr(outcome, 'turns', 0)}")
        print(f"Token Usage:   {getattr(outcome, 'token_usage', {})}")
        print(f"Cost (USD):    ${getattr(outcome, 'cost_usd', 0.0) or 0.0:.6f}")
        print(f"Detail:        {getattr(outcome, 'detail', '')}")

        # Verify against independent Oracle Test
        print("\n" + "=" * 80)
        print("RUNNING INDEPENDENT ORACLE TEST SUITE")
        print("=" * 80)

        oracle_p = ws / "test_oracle_verifier.py"
        oracle_p.write_text(ORACLE_TEST_CODE, encoding="utf-8")

        import subprocess
        p = subprocess.run(
            [sys.executable, "-m", "unittest", "test_oracle_verifier.py"],
            cwd=str(ws),
            capture_output=True,
            text=True,
            timeout=30,
        )

        print("Oracle Exit Code:", p.returncode)
        print("Oracle Output:")
        print(p.stdout or "")
        print(p.stderr or "")

        if p.returncode == 0:
            print("\n>>> OVERALL RESULT: 100% PASS (ORACLE GREEN) <<<")
            return 0
        else:
            print("\n>>> OVERALL RESULT: FAIL (ORACLE FAILED) <<<")
            return 1


if __name__ == "__main__":
    load_benchmark_env()
    sys.exit(main())
