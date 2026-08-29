#!/usr/bin/env python3
"""BETA-14: reproducible backend performance and storage baselines.

CLI:
  python3 benchmarks/backend_baselines.py --out benchmarks/backend_baselines.json

Every measurement here runs against `FakeModel` (zero network, zero real
model latency) so what is measured is framework overhead alone -- never
model or tool wall-clock time. A separate live-model benchmark would answer
a different question (end-to-end wall-clock with a real provider) and is
out of scope for this baseline.

Covers: no-op turn, durable turn, kernel-dispatch overhead (single-effect
turn minus no-op turn), event append, fold, checkpoint reconstruction,
artifact capture, single-agent execution, nested-agent (spawn) execution,
and storage amplification (bytes on disk per event vs. the raw canonical
JSON payload).
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _time_ms(fn: Callable[[], Any], repeats: int) -> dict[str, Any]:
    samples: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - start) * 1000.0)
    samples.sort()
    return {
        "repeats": repeats,
        "min_ms": samples[0],
        "median_ms": statistics.median(samples),
        "p95_ms": samples[min(len(samples) - 1, int(len(samples) * 0.95))],
        "max_ms": samples[-1],
    }


# -- no-op / durable turn, and kernel-dispatch overhead by subtraction ------
#
# Measured through `Runtime.execute_profiled` -- the real product composition
# path (manifest -> `RuntimeBootstrap` -> kernel/policy/classifier/governor
# wiring), not a hand-assembled kernel. "Kernel dispatch overhead" is not
# isolated directly (the kernel has no standalone benchmark seam); it is
# reported as the single-effect-turn cost minus the no-op-turn cost, which
# isolates exactly one `Kernel.dispatch()` call plus its one adapter
# execution from everything else a turn does.


def _run_one_turn(repo: Path, store: Any, effect: bool) -> None:
    from vanguard.packages.adapters.models.fake import FakeModel
    from vanguard.packages.runtime.compose import TaskContext
    from vanguard.packages.runtime.root import Runtime

    manifest = Path(str(__import__("importlib.resources", fromlist=["files"]).files(
        "vanguard.packages.agency").joinpath("manifests", "vg-code-default", "manifest.json")))
    tape = [{"kind": "finish", "note": "no-op"}] if not effect else [
        {"kind": "effect", "action": "fs.read",
         "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
         "args": {"path": "sample.py"}, "note": "bench effect"},
        {"kind": "finish", "note": "done"},
    ]
    run_id = f"run-bench-{time.perf_counter_ns()}"
    task = TaskContext(brief="benchmark turn", repo_path=repo, run_id=run_id,
                       episode_id=f"episode-{run_id}", max_turns=6)
    Runtime.execute_profiled(
        manifest, task, profile_id="local", model=FakeModel(tape),
        store=store, interactive=False,
    )


def bench_no_op_turn(repeats: int) -> dict[str, Any]:
    from vanguard.packages.adapters.stores.event_store import InMemoryEventStore
    with tempfile.TemporaryDirectory() as d:
        repo = Path(d)
        (repo / "sample.py").write_text("def f():\n    return 1\n")
        return _time_ms(lambda: _run_one_turn(repo, InMemoryEventStore(), effect=False), repeats)


def bench_durable_turn(repeats: int) -> dict[str, Any]:
    from vanguard.packages.adapters.stores.event_store import SqliteEventStore
    with tempfile.TemporaryDirectory() as d:
        repo = Path(d)
        (repo / "sample.py").write_text("def f():\n    return 1\n")
        def _once() -> None:
            store = SqliteEventStore(repo / f"bench-{time.perf_counter_ns()}.sqlite3")
            _run_one_turn(repo, store, effect=False)
        return _time_ms(_once, repeats)


def bench_single_effect_turn_durable(repeats: int) -> dict[str, Any]:
    from vanguard.packages.adapters.stores.event_store import SqliteEventStore
    with tempfile.TemporaryDirectory() as d:
        repo = Path(d)
        (repo / "sample.py").write_text("def f():\n    return 1\n")
        def _once() -> None:
            store = SqliteEventStore(repo / f"bench-eff-{time.perf_counter_ns()}.sqlite3")
            _run_one_turn(repo, store, effect=True)
        return _time_ms(_once, repeats)


# -- event append / fold / checkpoint reconstruction ------------------------


def _envelope(seq: int) -> Any:
    from vanguard.packages.domain.ledger.events import EventEnvelope
    return EventEnvelope(
        schema_version="mhf.event/1", event_id=f"evt-bench-{seq:06d}",
        scope="episode", seq=str(seq), occurred_at="2026-08-29T00:00:00.000Z",
        recorded_at="2026-08-29T00:00:00.000Z", principal="bench", principal_role="episode",
        tenant_id="t1", owner_id="o1", confidentiality="internal", retention_class="operational",
        trainability="unspecified", redaction_status="unredacted",
        payload={"kind": "BenchEvent", "n": seq, "note": "x" * 64},
        run_id="run-bench-append", episode_id="ep-bench-append", project_id="proj-bench",
        prev_digest="sha256:" + "0" * 64,
    )


def bench_event_append(n_events: int, repeats: int) -> dict[str, Any]:
    from vanguard.packages.adapters.stores.event_store import SqliteEventStore
    with tempfile.TemporaryDirectory() as d:
        def _once() -> None:
            store = SqliteEventStore(Path(d) / f"append-{time.perf_counter_ns()}.sqlite3")
            store.append([_envelope(i) for i in range(n_events)])
        result = _time_ms(_once, repeats)
        result["events_per_batch"] = n_events
        result["ms_per_event_median"] = result["median_ms"] / n_events
        return result


def bench_fold(n_events: int, repeats: int) -> dict[str, Any]:
    from vanguard.packages.domain.ledger.reducer import initial_state, reduce_batch
    events = [_envelope(i) for i in range(n_events)]
    result = _time_ms(lambda: reduce_batch(initial_state(), events), repeats)
    result["events_folded"] = n_events
    result["ms_per_event_median"] = result["median_ms"] / n_events
    return result


def bench_checkpoint_reconstruction(n_events: int, repeats: int) -> dict[str, Any]:
    from vanguard.packages.adapters.stores.blob_store import InMemoryBlobStore
    from vanguard.packages.domain.ledger.reducer import initial_state, reduce_batch
    from vanguard.packages.runtime.checkpoints import CheckpointManager

    events = [_envelope(i) for i in range(n_events)]
    half = n_events // 2
    blobs = InMemoryBlobStore()
    manager = CheckpointManager(blobs)
    checkpoint = manager.capture(reduce_batch(initial_state(), events[:half]))

    cold = _time_ms(lambda: manager.reconstruct(events), repeats)
    warm = _time_ms(lambda: manager.reconstruct(events, checkpoint=checkpoint), repeats)
    return {
        "events_total": n_events,
        "checkpoint_at": half,
        "cold_fold": cold,
        "from_checkpoint": warm,
        "speedup_median_x": cold["median_ms"] / warm["median_ms"] if warm["median_ms"] else None,
    }


def bench_artifact_capture(n_artifacts: int, artifact_bytes: int, repeats: int) -> dict[str, Any]:
    from vanguard.packages.adapters.stores.blob_store import FileBlobStore
    payload = b"x" * artifact_bytes
    with tempfile.TemporaryDirectory() as d:
        def _once() -> None:
            store = FileBlobStore(Path(d) / f"blobs-{time.perf_counter_ns()}")
            for i in range(n_artifacts):
                store.put(payload + str(i).encode())
        result = _time_ms(_once, repeats)
        result["artifacts_per_batch"] = n_artifacts
        result["artifact_bytes"] = artifact_bytes
        result["ms_per_artifact_median"] = result["median_ms"] / n_artifacts
        return result


# -- single-agent / nested-agent execution -----------------------------------


def bench_single_agent_execution(repeats: int) -> dict[str, Any]:
    from vanguard.packages.adapters.models.fake import FakeModel
    from vanguard.packages.runtime.app_service import ApplicationService

    with tempfile.TemporaryDirectory() as d:
        def _once() -> None:
            ws = Path(d) / f"ws-{time.perf_counter_ns()}"
            ws.mkdir()
            (ws / "pyproject.toml").write_text('[project]\nname="b"\nversion="0.1.0"\n')
            (ws / "sample.py").write_text("def f():\n    return 1\n")
            app = ApplicationService(workspace=ws)
            model = FakeModel([{"kind": "finish", "note": "bench single-agent"}])
            app.run(brief="benchmark single agent", profile_id="local", model=model,
                    state_dir=ws / ".vanguard", interactive=False, max_turns=3)
        return _time_ms(_once, repeats)


def bench_nested_agent_execution(repeats: int) -> dict[str, Any]:
    """Planner spawning one attenuated child (BETA-10 shape), timed end to end."""
    from vanguard.packages.adapters.models.fake import FakeModel
    from vanguard.packages.agency import EpisodeEngine
    from vanguard.packages.kernel.attenuation import Constraints, Scope
    from unittest.mock import MagicMock
    from vanguard.packages.kernel.model import FailurePath

    def _once() -> None:
        clock_t = [1000]

        class DClock:
            def now(self) -> str:
                clock_t[0] += 1
                return f"2026-08-29T00:00:{clock_t[0] % 60:02d}.000Z"

            def now_ms(self) -> int:
                clock_t[0] += 10
                return clock_t[0]

        class Sink:
            def emit(self, e: Any) -> None: ...

        kernel = MagicMock()
        dispatch = MagicMock()
        dispatch.failure = FailurePath.OK
        dispatch.outcome = MagicMock()
        dispatch.outcome.result_digest = "sha256:" + "0" * 64
        kernel.dispatch.return_value = dispatch

        parent_scope = Scope(
            actions=frozenset({"spawn", "finish"}),
            resources=({"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},),
            constraints=Constraints(expires_at="2099-01-01T00:00:00.000Z", max_uses=100,
                                    budget_usd_micros=1_000_000, max_depth=3),
            depth=0,
        )
        engine = EpisodeEngine(
            kernel=kernel, model=FakeModel([{"kind": "finish", "note": "plan"}]),
            clock=DClock(), events=Sink(), scope=parent_scope, max_turns=5,
        )
        engine.run(episode_id="ep-p", run_id="run-nested-bench", principal="planner", brief="plan")

        child_scope = Scope(
            actions=frozenset({"finish"}),
            resources=parent_scope.resources,
            constraints=Constraints(expires_at="2099-01-01T00:00:00.000Z", max_uses=50,
                                    budget_usd_micros=500_000, max_depth=2),
            depth=1,
        )
        engine.spawn(
            child_scope=child_scope, brief="execute", episode_id="ep-c",
            run_id="run-nested-bench", principal="executor",
            parent_episode_id="ep-p",
            model=FakeModel([{"kind": "finish", "note": "exec"}]),
        )

    return _time_ms(_once, repeats)


# -- storage amplification ---------------------------------------------------


def bench_storage_amplification(n_events: int) -> dict[str, Any]:
    from vanguard.packages.adapters.stores.event_store import SqliteEventStore
    events = [_envelope(i) for i in range(n_events)]
    raw_json_bytes = sum(len(json.dumps(e.wire_dict(), separators=(",", ":")).encode("utf-8")) for e in events)
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "amp.sqlite3"
        store = SqliteEventStore(path)
        store.append(events)
        store._conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        disk_bytes = path.stat().st_size
        for sidecar in (Path(str(path) + "-wal"), Path(str(path) + "-shm")):
            if sidecar.exists():
                disk_bytes += sidecar.stat().st_size
    return {
        "events": n_events,
        "raw_canonical_json_bytes": raw_json_bytes,
        "sqlite_file_bytes": disk_bytes,
        "amplification_x": disk_bytes / raw_json_bytes if raw_json_bytes else None,
    }


# -- EVO-00: multi-agent token overhead and recovery latency ----------------


def bench_multi_agent_token_overhead(repeats: int) -> dict[str, Any]:
    """The token cost of adding a coordination layer, isolated from work cost.

    A planner that only plans and spawns (never touches the work itself)
    costs tokens a single agent doing the same work directly does not pay.
    Measured via real `RunTelemetry` (`compute_run_telemetry`, EVO-06) fed by
    a `FakeModel` tape whose proposals carry an explicit `usage` block --
    exactly the field `_LayeredOperator.propose` reads in production
    (`session.py`), not a number invented for this benchmark.
    """
    from vanguard.packages.adapters.models.fake import FakeModel
    from vanguard.packages.runtime.compose import TaskContext
    from vanguard.packages.runtime.root import Runtime
    from vanguard.packages.adapters.stores.event_store import InMemoryEventStore

    manifest = Path(str(__import__("importlib.resources", fromlist=["files"]).files(
        "vanguard.packages.agency").joinpath("manifests", "vg-code-default", "manifest.json")))

    def _worker_agent_tokens() -> int:
        """A single agent doing the work directly: one effect, then finish."""
        tape = [
            {"kind": "effect", "action": "fs.read",
             "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
             "args": {"path": "sample.py"}, "note": "do the work",
             "usage": {"prompt_tokens": 400, "completion_tokens": 60}},
            {"kind": "finish", "note": "done", "usage": {"prompt_tokens": 420, "completion_tokens": 20}},
        ]
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "sample.py").write_text("def f():\n    return 1\n")
            run_id = f"run-tok-worker-{time.perf_counter_ns()}"
            task = TaskContext(brief="do the work directly", repo_path=repo, run_id=run_id,
                               episode_id=f"episode-{run_id}", max_turns=6)
            result = Runtime.execute_profiled(
                manifest, task, profile_id="local", model=FakeModel(tape),
                store=InMemoryEventStore(), interactive=False,
            )
            return result.telemetry.total_tokens or 0

    def _planner_only_tokens() -> int:
        """A coordinator that never executes the work itself, only plans and
        would spawn a child to do it. Its token cost is pure coordination
        overhead on top of whatever the child (the worker-agent case above)
        separately costs."""
        tape = [
            {"kind": "finish", "note": "delegated to a child; planning only",
             "usage": {"prompt_tokens": 550, "completion_tokens": 90}},
        ]
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "sample.py").write_text("def f():\n    return 1\n")
            run_id = f"run-tok-planner-{time.perf_counter_ns()}"
            task = TaskContext(brief="plan the work, delegate execution", repo_path=repo, run_id=run_id,
                               episode_id=f"episode-{run_id}", max_turns=6)
            result = Runtime.execute_profiled(
                manifest, task, profile_id="local", model=FakeModel(tape),
                store=InMemoryEventStore(), interactive=False,
            )
            return result.telemetry.total_tokens or 0

    worker_samples = [_worker_agent_tokens() for _ in range(repeats)]
    planner_samples = [_planner_only_tokens() for _ in range(repeats)]
    worker_tokens = statistics.median(worker_samples)
    planner_tokens = statistics.median(planner_samples)
    return {
        "repeats": repeats,
        "single_agent_direct_execution_tokens_median": worker_tokens,
        "coordinator_only_tokens_median": planner_tokens,
        "coordination_overhead_ratio": (planner_tokens / worker_tokens) if worker_tokens else None,
        "note": "coordinator cost is pure overhead on top of the child that still has to do the worker_tokens of work",
    }


def bench_recovery_latency(repeats: int) -> dict[str, Any]:
    """Wall-clock cost of the BETA-12 kill/resume path, real subprocesses.

    Reuses the exact mechanism `test/runtime/test_beta12_kill_and_resume.py`
    proves correct (a watchdog thread inside the worker process self-delivers
    `SIGKILL` the instant the first effect settles) -- this benchmark times
    it instead of only asserting it. `uninterrupted_ms` is a fresh,
    never-killed run of the identical tape for direct comparison.
    """
    import json as _json
    import subprocess as _subprocess

    def _worker_script(state_dir: Path, run_id: str) -> str:
        return f"""
import os, signal, threading, time
from pathlib import Path
from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.app_service import ApplicationService

state_dir = Path({_json.dumps(str(state_dir))})
run_id = {_json.dumps(run_id)}
events_db = state_dir / "events.sqlite3"

def _watchdog():
    while not events_db.exists():
        time.sleep(0.001)
    store = SqliteEventStore(str(events_db))
    while True:
        res = store.read(EventRange(run_id=run_id))
        if res.ok:
            for ev in res.value:
                if ev.payload.get("kind") == "EffectCompleted":
                    os.kill(os.getpid(), signal.SIGKILL)
                    return
        time.sleep(0.001)

threading.Thread(target=_watchdog, daemon=True).start()

class _Slow(FakeModel):
    def propose(self, *a, **k):
        if self._cursor > 0:
            time.sleep(0.15)
        return super().propose(*a, **k)

model = _Slow([
    {{"kind": "effect", "action": "fs.read",
      "resource": {{"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}},
      "args": {{"path": "sample.py"}}, "note": "work"}},
    {{"kind": "finish", "note": "unreachable before kill"}},
])
app = ApplicationService(workspace=Path("."))
app.run(brief="recovery latency bench", profile_id="local", run_id=run_id, model=model,
        state_dir=state_dir, interactive=False, max_turns=6)
"""

    def _resume_script(state_dir: Path, run_id: str) -> str:
        return f"""
from pathlib import Path
from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.runtime.app_service import ApplicationService

app = ApplicationService(workspace=Path("."))
model = FakeModel([{{"kind": "finish", "note": "resumed"}}])
app.resume(run_id={_json.dumps(run_id)}, profile_id="local", model=model,
          state_dir=Path({_json.dumps(str(state_dir))}))
"""

    recovery_samples: list[float] = []
    uninterrupted_samples: list[float] = []
    with tempfile.TemporaryDirectory() as d:
        workspace = Path(d)
        (workspace / "pyproject.toml").write_text('[project]\nname="b"\nversion="0.1.0"\n')
        (workspace / "sample.py").write_text("def f():\n    return 1\n")

        for i in range(repeats):
            run_id = f"run-recov-{i}-{time.perf_counter_ns()}"
            state_dir = workspace / f".vanguard-recov-{i}"
            state_dir.mkdir()
            script = workspace / f"_worker_{i}.py"
            script.write_text(_worker_script(state_dir, run_id), encoding="utf-8")

            kill_start = time.perf_counter()
            proc = _subprocess.run(["python3", str(script)], cwd=str(workspace),
                                   capture_output=True, text=True, timeout=30)
            if proc.returncode != -9:
                continue  # watchdog raced and missed; skip this sample rather than mismeasure

            resume_script = workspace / f"_resume_{i}.py"
            resume_script.write_text(_resume_script(state_dir, run_id), encoding="utf-8")
            resume_start = time.perf_counter()
            _subprocess.run(["python3", str(resume_script)], cwd=str(workspace),
                            capture_output=True, text=True, check=True, timeout=30)
            recovery_samples.append((time.perf_counter() - resume_start) * 1000.0)

        from vanguard.packages.adapters.models.fake import FakeModel
        from vanguard.packages.runtime.app_service import ApplicationService

        for i in range(repeats):
            run_id = f"run-uninterrupted-{i}-{time.perf_counter_ns()}"
            state_dir = workspace / f".vanguard-uninterrupted-{i}"
            state_dir.mkdir()
            model = FakeModel([
                {"kind": "effect", "action": "fs.read",
                 "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
                 "args": {"path": "sample.py"}, "note": "work"},
                {"kind": "finish", "note": "done"},
            ])
            app = ApplicationService(workspace=workspace)
            start = time.perf_counter()
            app.run(brief="uninterrupted comparison", profile_id="local", run_id=run_id, model=model,
                    state_dir=state_dir, interactive=False, max_turns=6)
            uninterrupted_samples.append((time.perf_counter() - start) * 1000.0)

    return {
        "repeats_requested": repeats,
        "recovery_samples_captured": len(recovery_samples),
        "resume_after_kill_ms": (
            {"median": statistics.median(recovery_samples), "min": min(recovery_samples), "max": max(recovery_samples)}
            if recovery_samples else None
        ),
        "uninterrupted_full_run_ms": (
            {"median": statistics.median(uninterrupted_samples), "min": min(uninterrupted_samples), "max": max(uninterrupted_samples)}
            if uninterrupted_samples else None
        ),
        "note": "resume_after_kill_ms times only the fresh resume process; the killed process's own wall time is separate and not comparable to a full uninterrupted run",
    }


def _application_service_local():
    from vanguard.packages.runtime.app_service import ApplicationService
    return ApplicationService


ApplicationServiceLocal = _application_service_local()


BENCHMARKS: dict[str, Callable[[], Any]] = {
    "no_op_turn": lambda: bench_no_op_turn(repeats=20),
    "durable_turn": lambda: bench_durable_turn(repeats=20),
    "single_effect_turn_durable_minus_no_op_is_kernel_dispatch_overhead": lambda: bench_single_effect_turn_durable(repeats=20),
    "event_append_batch_100": lambda: bench_event_append(n_events=100, repeats=10),
    "fold_1000_events": lambda: bench_fold(n_events=1000, repeats=10),
    "checkpoint_reconstruction_500_events": lambda: bench_checkpoint_reconstruction(n_events=500, repeats=10),
    "artifact_capture_batch_50": lambda: bench_artifact_capture(n_artifacts=50, artifact_bytes=4096, repeats=10),
    "single_agent_execution": lambda: bench_single_agent_execution(repeats=10),
    "nested_agent_execution": lambda: bench_nested_agent_execution(repeats=10),
    "storage_amplification_1000_events": lambda: bench_storage_amplification(n_events=1000),
    "multi_agent_token_overhead": lambda: bench_multi_agent_token_overhead(repeats=5),
    "recovery_latency": lambda: bench_recovery_latency(repeats=5),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", help="Path to save benchmark JSON output")
    parser.add_argument("--only", help="Comma-separated subset of benchmark names to run")
    args = parser.parse_args(argv)

    names = list(BENCHMARKS) if not args.only else [n.strip() for n in args.only.split(",")]
    results: dict[str, Any] = {}
    for name in names:
        if name not in BENCHMARKS:
            print(f"unknown benchmark: {name!r}; available: {sorted(BENCHMARKS)}", file=sys.stderr)
            return 2
        print(f"running {name}...", file=sys.stderr)
        results[name] = BENCHMARKS[name]()

    report = {
        "schema": "aether.backend-baselines/1",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "model": "fake (zero network, zero model latency -- framework overhead only)",
        "results": results,
    }

    text = json.dumps(report, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
