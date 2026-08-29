#!/usr/bin/env python3
"""AUTO-GENERATED: SWE Challenge Runner

Executes SWE challenges against the Vanguard coding engine.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import difflib
import hashlib
import json
import os
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Mapping

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

from benchmarks.swe_bench.challenges import CHALLENGES
from vanguard.packages.adapters.models.env_loader import load_api_key
from vanguard.packages.runtime.compose import TaskContext
from vanguard.packages.runtime.root import Runtime
from vanguard.packages.runtime.autonomous_grant import create_autonomous_grant
from vanguard.packages.runtime.governance.approvals import OperatorSigner
from vanguard.packages.adapters.models.openrouter import OpenRouterModel
from vanguard.packages.adapters.stores.blob_store import FileBlobStore

SMOKE_CHALLENGES = (
    "tier1_lru_ttl_cache",
    "tier1_version_semver_parser",
    "tier2_event_bus",
    "tier2_fsm_workflow_engine",
    "tier2_retry_exponential_backoff",
    "tier3_token_bucket",
    "tier3_connection_pool",
    "tier4_dag_resolver",
    "tier4_stream_window_aggregator",
    "tier5_datalog_engine",
    "tier6_raft_state_machine",
    "tier7_greenfield_kv_lsm_tree",
)

# A benchmark instrument must have a finite provider budget.  One initial
# request plus one retry at a bounded transport timeout gives the evaluator a
# deterministic upper bound and preserves a typed instrument_error when the
# provider or network is unavailable.
BENCHMARK_MAX_RETRIES = 2
BENCHMARK_REQUEST_TIMEOUT_SECONDS = 45.0
BENCHMARK_RUN_TIMEOUT_SECONDS = 300.0
WORKER_PROTOCOL = "vanguard.swe-worker/1"


@dataclass(frozen=True)
class _WorkerTelemetry:
    """JSON-safe subset of runtime telemetry returned across the worker IPC."""

    turns: int = 0
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    usd_micros: int | None = None

    @property
    def total_tokens(self) -> int | None:
        if self.prompt_tokens is None or self.completion_tokens is None:
            return None
        return self.prompt_tokens + self.completion_tokens


@dataclass(frozen=True)
class _WorkerOutcome:
    """Small result DTO; runtime objects never cross the process boundary."""

    terminal: str
    detail: str = ""
    instrument_error: str = ""
    telemetry: _WorkerTelemetry = _WorkerTelemetry()
    trajectory: dict[str, Any] | None = None


def _runtime_result_payload(result: Any) -> dict[str, Any]:
    """Reduce a RunResult to the stable, JSON-only worker protocol."""
    terminal = getattr(result, "terminal", None)
    terminal_value = getattr(terminal, "value", str(terminal)).lower()
    telemetry = getattr(result, "telemetry", None)
    telemetry_payload = {
        "turns": getattr(telemetry, "turns", 0),
        "prompt_tokens": getattr(telemetry, "prompt_tokens", None),
        "completion_tokens": getattr(telemetry, "completion_tokens", None),
        "usd_micros": getattr(telemetry, "usd_micros", None),
    }
    trajectory = getattr(result, "trajectory", None)
    if not isinstance(trajectory, dict):
        trajectory = None
    payload = {
        "protocol": WORKER_PROTOCOL,
        "terminal": terminal_value,
        "detail": str(getattr(result, "detail", "")),
        "instrument_error": str(getattr(result, "instrument_error", "") or ""),
        "telemetry": telemetry_payload,
        "trajectory": trajectory,
    }
    # Refuse to smuggle Python objects or NaN values over the wire. The caller
    # classifies an unserialisable runtime result as an instrument failure.
    json.dumps(payload, allow_nan=False)
    return payload


def _runtime_worker(config: Mapping[str, Any]) -> dict[str, Any]:
    """Construct and execute one runtime episode inside the child process."""
    repo_path = Path(str(config["repo_path"])).resolve()
    store_path = Path(str(config["store_path"])).resolve()
    blob_path = Path(str(config["blob_path"])).resolve()
    task = TaskContext(
        brief=str(config["brief"]),
        repo_path=repo_path,
        run_id=str(config["run_id"]),
        episode_id=str(config["episode_id"]),
        project_id=str(config["project_id"]),
        max_turns=int(config["max_turns"]),
    )
    seed_key = secrets.token_bytes(32)
    grant = create_autonomous_grant(
        repo_path,
        allowed_verbs=("fs.read", "fs.search", "patch.apply", "proc.exec"),
        max_turns=task.max_turns,
        max_attempts=1,
        seed_key=seed_key,
    )
    signer = OperatorSigner(seed_key)
    model = OpenRouterModel(
        model=str(config["model"]),
        stream=True,
        # The secret remains in the child's inherited environment and is not
        # placed in the IPC payload, command line, report, or exception text.
        environ={"OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY", "")},
        max_retries=BENCHMARK_MAX_RETRIES,
        request_timeout=BENCHMARK_REQUEST_TIMEOUT_SECONDS,
    )
    manifest_path = _REPO_ROOT / "vanguard/packages/agency/manifests/vg-code-default/manifest.json"
    store_path.parent.mkdir(parents=True, exist_ok=True)
    blob_path.mkdir(parents=True, exist_ok=True)
    result = Runtime.execute_profiled(
        manifest_path,
        task,
        profile_id="product",
        model=model,
        store_path=str(store_path),
        blobs=FileBlobStore(blob_path),
        interactive=True,
        approver=lambda challenge: signer.approve(challenge, reviewer=grant.reviewer),
        approval_key=signer.public_bytes,
    )
    return _runtime_result_payload(result)


def _instrument_worker_failure(kind: str, detail: str) -> _WorkerOutcome:
    """Create an explicit non-measurement outcome for parent-side failures."""
    return _WorkerOutcome(
        terminal="instrument_error",
        detail=detail,
        instrument_error=kind,
    )


def _decode_worker_payload(raw: str) -> _WorkerOutcome:
    """Decode the child response, failing closed on protocol drift/noise."""
    candidates = [line for line in raw.splitlines() if line.strip()]
    if not candidates:
        return _instrument_worker_failure("worker_empty_output", "worker returned no JSON")
    try:
        payload = json.loads(candidates[-1])
    except (TypeError, json.JSONDecodeError):
        return _instrument_worker_failure("worker_invalid_json", "worker returned invalid JSON")
    if not isinstance(payload, Mapping) or payload.get("protocol") != WORKER_PROTOCOL:
        return _instrument_worker_failure("worker_protocol_error", "worker protocol mismatch")
    telemetry_raw = payload.get("telemetry")
    if not isinstance(telemetry_raw, Mapping):
        return _instrument_worker_failure("worker_protocol_error", "worker telemetry is not an object")

    def integer_or_none(name: str) -> int | None:
        value = telemetry_raw.get(name)
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"worker telemetry field {name} is not an integer")
        return value

    try:
        turns = integer_or_none("turns")
        if turns is None:
            turns = 0
        telemetry = _WorkerTelemetry(
            turns=turns,
            prompt_tokens=integer_or_none("prompt_tokens"),
            completion_tokens=integer_or_none("completion_tokens"),
            usd_micros=integer_or_none("usd_micros"),
        )
    except ValueError as exc:
        return _instrument_worker_failure("worker_protocol_error", str(exc))
    terminal = payload.get("terminal")
    if not isinstance(terminal, str) or not terminal:
        return _instrument_worker_failure("worker_protocol_error", "worker terminal is invalid")
    trajectory = payload.get("trajectory")
    if trajectory is not None and not isinstance(trajectory, dict):
        return _instrument_worker_failure("worker_protocol_error", "worker trajectory is invalid")
    return _WorkerOutcome(
        terminal=terminal,
        detail=str(payload.get("detail", "")),
        instrument_error=str(payload.get("instrument_error", "") or ""),
        telemetry=telemetry,
        trajectory=trajectory,
    )


def _kill_worker(process: subprocess.Popen[str]) -> None:
    """Kill the worker and every process it spawned for proc.exec."""
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
            return
        except (ProcessLookupError, OSError):
            pass
    try:
        process.kill()
    except ProcessLookupError:
        pass


def _execute_runtime_in_child(
    task: TaskContext,
    model: str,
    store_path: Path,
    blob_path: Path,
    run_timeout: float,
) -> _WorkerOutcome:
    """Run the benchmark episode behind a killable OS process boundary.

    A signal alarm cannot interrupt every blocked native/TLS read and cannot
    reliably clean up descendants. The parent owns the hard deadline, kills
    the worker process group, drains its pipes, and returns a typed outcome.
    """
    if run_timeout <= 0:
        raise ValueError("run timeout must be positive")
    config = {
        "repo_path": str(Path(task.repo_path).resolve()),
        "store_path": str(store_path.resolve()),
        "blob_path": str(blob_path.resolve()),
        "brief": task.brief,
        "run_id": task.run_id,
        "episode_id": task.episode_id,
        "project_id": task.project_id,
        "max_turns": task.max_turns,
        "model": model,
    }
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "tools.runners.run_swe_challenge", "--worker"],
            cwd=_REPO_ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=os.environ.copy(),
            start_new_session=(os.name == "posix"),
        )
    except OSError as exc:
        return _instrument_worker_failure("worker_spawn_error", type(exc).__name__)
    try:
        stdout, _stderr = process.communicate(
            json.dumps(config, sort_keys=True), timeout=run_timeout,
        )
    except subprocess.TimeoutExpired:
        _kill_worker(process)
        stdout, _stderr = process.communicate()
        # This is the authoritative parent-side timeout record. It is later
        # emitted in the report as instrument_error JSON, never as a task fail.
        return _instrument_worker_failure(
            "worker_timeout", f"child process exceeded {run_timeout:.1f}s deadline",
        )
    if process.returncode != 0:
        return _instrument_worker_failure(
            "worker_exit_error", f"child process exited with status {process.returncode}",
        )
    return _decode_worker_payload(stdout)


def _worker_main() -> int:
    """Child entrypoint; always emits one JSON protocol record."""
    try:
        config = json.load(sys.stdin)
        if not isinstance(config, Mapping):
            raise ValueError("worker config must be an object")
        payload = _runtime_worker(config)
    except Exception as exc:
        payload = {
            "protocol": WORKER_PROTOCOL,
            "terminal": "instrument_error",
            "detail": f"worker raised {type(exc).__name__}",
            "instrument_error": "runtime_exception",
            "telemetry": {"turns": 0},
            "trajectory": None,
        }
    sys.stdout.write(json.dumps(payload, sort_keys=True, allow_nan=False) + "\n")
    sys.stdout.flush()
    return 0


@contextmanager
def _execution_deadline(seconds: float):
    """Bound one benchmark episode, including non-HTTP runtime work.

    The model adapter bounds socket operations, but an episode can also wait
    in a child/runtime boundary or a provider iterator.  A benchmark driver
    must emit a typed instrument result instead of hanging indefinitely.  The
    POSIX timer is intentionally scoped to this process-local runner and is a
    no-op on platforms without ``SIGALRM``.
    """
    if seconds <= 0:
        raise ValueError("run timeout must be positive")
    if not hasattr(signal, "SIGALRM") or not hasattr(signal, "setitimer"):
        yield
        return

    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.getitimer(signal.ITIMER_REAL)

    def raise_timeout(_signum: int, _frame: Any) -> None:
        raise TimeoutError(f"benchmark episode exceeded {seconds:.1f}s deadline")

    signal.signal(signal.SIGALRM, raise_timeout)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
        if previous_timer[0] > 0:
            signal.setitimer(signal.ITIMER_REAL, *previous_timer)


def _snapshot_tree(root: Path) -> dict[str, bytes]:
    """Return the immutable baseline file map used for patch accounting.

    Benchmark runs must not depend on Git being installed or on repository
    metadata.  A content-addressed snapshot also makes the evaluated subject
    explicit and portable to an empty environment.
    """
    snapshot: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "oracle_test.py":
            continue
        rel = path.relative_to(root).as_posix()
        # Runtime state and CAS artifacts are evidence outputs, not the
        # submitted source patch.  Including SQLite/WAL bytes here made a
        # zero-turn run look like a very large code change.
        if ".vanguard" in Path(rel).parts or "__pycache__" in Path(rel).parts:
            continue
        if path.suffix == ".pyc":
            continue
        snapshot[rel] = path.read_bytes()
    return snapshot


def _snapshot_digest(snapshot: dict[str, bytes]) -> str:
    manifest = {
        path: hashlib.sha256(content).hexdigest()
        for path, content in sorted(snapshot.items())
    }
    body = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(body).hexdigest()


def setup_challenge(challenge_id: str, scratch_dir: Path) -> dict[str, bytes]:
    """Set up a challenge and return its content-addressed baseline."""
    challenge = CHALLENGES[challenge_id]
    
    # Write files
    for filepath, content in challenge.files.items():
        full_path = scratch_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        
    # Write TASK.md
    task_path = scratch_dir / "TASK.md"
    task_path.write_text(f"# {challenge.title}\n\n{challenge.brief}\n", encoding="utf-8")
    
    return _snapshot_tree(scratch_dir)


def evaluate_oracle(challenge_id: str, scratch_dir: Path) -> bool:
    """Run the oracle test code to evaluate the challenge."""
    challenge = CHALLENGES[challenge_id]
    oracle_path = scratch_dir / "oracle_test.py"
    oracle_path.write_text(challenge.oracle_code, encoding="utf-8")
    
    # Run the oracle test
    res = subprocess.run(
        [sys.executable, "-m", "unittest", "oracle_test.py"],
        cwd=scratch_dir,
        capture_output=True,
        text=True,
    )
    return res.returncode == 0


def _changed_files(scratch_dir: Path, baseline: dict[str, bytes]) -> list[str]:
    current = _snapshot_tree(scratch_dir)
    return sorted(
        path for path in set(baseline) | set(current)
        if baseline.get(path) != current.get(path)
    )


def get_diff_size(scratch_dir: Path, baseline: dict[str, bytes]) -> int:
    """Count changed patch lines against the captured subject snapshot."""
    total = 0
    for rel in _changed_files(scratch_dir, baseline):
        before = baseline.get(rel, b"").decode("utf-8", errors="replace")
        after = ""
        path = scratch_dir / rel
        if path.is_file():
            after = path.read_bytes().decode("utf-8", errors="replace")
        total += len(list(difflib.unified_diff(
            before.splitlines(), after.splitlines(),
            fromfile=f"a/{rel}", tofile=f"b/{rel}", lineterm="")))
    return total


def _benchmark_identity(challenge_id: str, scratch_dir: Path,
                        baseline: dict[str, bytes], model: str,
                        run_timeout: float = BENCHMARK_RUN_TIMEOUT_SECONDS) -> dict[str, Any]:
    challenge = CHALLENGES.get(challenge_id)
    return {
        "benchmark": "vanguard-swe-challenge/1",
        "task_id": challenge_id,
        "tier": challenge.tier if challenge else "VERIFIED",
        "kind": challenge.kind if challenge else "repository-instance",
        "subject_digest": _snapshot_digest(baseline),
        "source_manifest": {
            path: hashlib.sha256(baseline[path]).hexdigest()
            for path in sorted(baseline)
        },
        "model_requested": model,
        "provider": "openrouter",
        "transport_policy": {
            "request_timeout_seconds": BENCHMARK_REQUEST_TIMEOUT_SECONDS,
            "max_retries": BENCHMARK_MAX_RETRIES,
        },
        "run_timeout_seconds": run_timeout,
        "runtime_boundary": {
            "kind": "child_process",
            "protocol": WORKER_PROTOCOL,
            "deadline_owner": "parent",
            "kill_scope": "worker_process_group",
        },
        "contamination": {
            "source": "greenfield-preregistered",
            "status": "declared_clean",
            "excluded": False,
        },
    }


def _enrich_result(result_row: dict[str, Any], runtime_result: Any) -> dict[str, Any]:
    """Bind returned provider identity and runtime truth to the benchmark row."""
    terminal = getattr(runtime_result, "terminal", None)
    if terminal is None:
        # An exception or missing runtime result is an instrument failure, not
        # an implicit success and not a synthetic completed trajectory.
        result_row.setdefault("terminal", "instrument_error")
        result_row.setdefault("terminal_detail", "runtime returned no terminal state")
        result_row.setdefault("instrument_error", "runtime_result_missing")
    else:
        result_row["terminal"] = getattr(terminal, "value", str(terminal)).lower()
        result_row["terminal_detail"] = str(getattr(runtime_result, "detail", ""))
        result_row["instrument_error"] = str(getattr(runtime_result, "instrument_error", "") or "")
    trajectory = getattr(runtime_result, "trajectory", None)
    if isinstance(trajectory, dict):
        routes = trajectory.get("model_routes_used")
        if isinstance(routes, list):
            result_row["model_routes_used"] = routes
        for key in ("execution_digest", "state_digest", "run_id", "episode_id"):
            if key in trajectory:
                result_row[key] = trajectory[key]
    return result_row


def _diagnose_result(
    completed: bool,
    changed_files: list[str],
    oracle_passed: bool,
) -> str:
    """Explain why the patch/oracle gate did or did not pass.

    A completed episode is runtime evidence only.  In particular, a model can
    terminate normally after deciding that no edit is needed; that must remain
    a task failure, but it is materially different from an instrument failure
    or an oracle-rejected patch.
    """
    if not completed:
        return "terminal_not_completed"
    if not changed_files:
        return "completed_without_source_patch"
    if not oracle_passed:
        return "source_patch_failed_oracle"
    return "completed_patch_passed_oracle"


def _write_report(path: str, results: list[dict[str, Any]]) -> None:
    """Write one immutable JSON report; never replace a prior measurement."""
    destination = Path(path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "vanguard.swe-report/1",
        "results": results,
        "summary": {
            "count": len(results),
            "passed": sum(1 for row in results if row["passed"]),
        },
    }
    with destination.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def run_challenge(
    challenge_id: str,
    model: str,
    keep_dir: bool,
    run_timeout: float = BENCHMARK_RUN_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Run a single SWE challenge."""
    challenge = CHALLENGES[challenge_id]
    scratch_dir = Path(tempfile.mkdtemp(prefix=f"vanguard_swe_{challenge_id}_"))
    print(f"Setting up {challenge_id} in {scratch_dir}...")
    
    try:
        baseline = setup_challenge(challenge_id, scratch_dir)
        
        task = TaskContext(
            brief=challenge.brief,
            repo_path=scratch_dir,
            run_id=f"run-{challenge_id}",
            episode_id=f"episode-{challenge_id}",
            project_id="swe-challenge",
            max_turns=20,
        )
        
        db_path = scratch_dir / ".vanguard" / "events.sqlite3"
        blob_path = scratch_dir / ".vanguard" / "blobs"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        blob_path.mkdir(parents=True, exist_ok=True)

        print(f"Running Vanguard engine with model {model}...")
        t0 = time.time()
        result = _execute_runtime_in_child(task, model, db_path, blob_path, run_timeout)
        elapsed = time.time() - t0
        
        # Parse result
        turns = 0
        tokens = None
        cost = None
        if result and getattr(result, "telemetry", None):
            turns = getattr(result.telemetry, "turns", 0)
            tokens = getattr(result.telemetry, "total_tokens", None)
            cost = getattr(result.telemetry, "usd_micros", None)

        print("Evaluating oracle...")
        oracle_passed = evaluate_oracle(challenge_id, scratch_dir)
        changed_files = _changed_files(scratch_dir, baseline)
        terminal = getattr(result, "terminal", None)
        completed = getattr(terminal, "value", str(terminal)).lower() == "completed"
        # A passing oracle over the unmodified fixture is not a coding-agent
        # success.  Require a completed canonical run and a real source patch.
        passed = completed and bool(changed_files) and oracle_passed
        diff_size = get_diff_size(scratch_dir, baseline)
        
        return _enrich_result({
            "challenge": challenge_id,
            "tier": challenge.tier,
            "passed": passed,
            "oracle_passed": oracle_passed,
            "changed_files": changed_files,
            "diagnosis": _diagnose_result(completed, changed_files, oracle_passed),
            "elapsed": elapsed,
            "turns": turns,
            "tokens": tokens,
            "cost_micros": cost,
            "diff_size": diff_size,
            "scratch_dir": str(scratch_dir),
            "benchmark_identity": _benchmark_identity(
                challenge_id, scratch_dir, baseline, model, run_timeout,
            ),
        }, result)
    finally:
        if not keep_dir:
            shutil.rmtree(scratch_dir, ignore_errors=True)


def run_verified_challenge(
    instance_id: str,
    model: str,
    keep_dir: bool,
    run_timeout: float = BENCHMARK_RUN_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Run a real SWE-bench Verified instance."""
    verified_repo = _REPO_ROOT / "tools/005_SWE_VERIFIED_REPO" / instance_id
    if not verified_repo.exists():
        raise ValueError(f"Verified repo {verified_repo} does not exist.")
        
    scratch_dir = Path(tempfile.mkdtemp(prefix=f"vanguard_verified_{instance_id}_"))
    print(f"Setting up {instance_id} in {scratch_dir}...")
    
    try:
        # Copy public contents
        public_dir = verified_repo / "public"
        shutil.copytree(public_dir, scratch_dir, dirs_exist_ok=True)
        
        # Read context.md
        context_path = verified_repo / "context.md"
        brief = ""
        if context_path.exists():
            brief = context_path.read_text("utf-8")
            task_path = scratch_dir / "TASK.md"
            task_path.write_text(f"# {instance_id}\n\n{brief}\n", encoding="utf-8")
            
        baseline = _snapshot_tree(scratch_dir)
        
        task = TaskContext(
            brief=brief if brief else f"Fix {instance_id}",
            repo_path=scratch_dir,
            run_id=f"run-{instance_id}",
            episode_id=f"episode-{instance_id}",
            project_id="swe-verified",
            max_turns=20,
        )
        
        db_path = scratch_dir / ".vanguard" / "events.sqlite3"
        blob_path = scratch_dir / ".vanguard" / "blobs"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        blob_path.mkdir(parents=True, exist_ok=True)

        print(f"Running Vanguard engine with model {model}...")
        t0 = time.time()
        result = _execute_runtime_in_child(task, model, db_path, blob_path, run_timeout)
        elapsed = time.time() - t0
        
        turns = 0
        tokens = None
        cost = None
        if result and getattr(result, "telemetry", None):
            turns = getattr(result.telemetry, "turns", 0)
            tokens = getattr(result.telemetry, "total_tokens", None)
            cost = getattr(result.telemetry, "usd_micros", None)

        # Evaluate oracle
        passed = False
        print("Evaluating oracle...")
        if instance_id == "pallets__flask-5014":
            oracle_code = """import unittest
from flask.blueprints import Blueprint

class TestFlask(unittest.TestCase):
    def test_blueprint_empty_name(self):
        with self.assertRaises(ValueError):
            Blueprint("", "test")
        
        # should work
        Blueprint("valid", "test")

if __name__ == "__main__":
    unittest.main()
"""
            oracle_path = scratch_dir / "oracle_test.py"
            oracle_path.write_text(oracle_code, encoding="utf-8")
            test_env = {**os.environ, "PYTHONPATH": f"{scratch_dir}/src:{scratch_dir}"}
            res = subprocess.run([sys.executable, "-m", "unittest", "oracle_test.py"], cwd=scratch_dir, capture_output=True, text=True, env=test_env)
            passed = (res.returncode == 0)
            if not passed:
                print("Oracle failure stderr:", res.stderr)
                print("Oracle failure stdout:", res.stdout)
        elif instance_id == "psf__requests-1142":
            oracle_code = """import unittest
from requests.models import PreparedRequest

class TestRequests(unittest.TestCase):
    def test_get_content_length(self):
        p = PreparedRequest()
        p.prepare_content_length('')
        self.assertNotIn("Content-Length", p.headers)

if __name__ == "__main__":
    unittest.main()
"""
            oracle_path = scratch_dir / "oracle_test.py"
            oracle_path.write_text(oracle_code, encoding="utf-8")
            test_env = {**os.environ, "PYTHONPATH": f"{scratch_dir}/src:{scratch_dir}"}
            res = subprocess.run([sys.executable, "-m", "unittest", "oracle_test.py"], cwd=scratch_dir, capture_output=True, text=True, env=test_env)
            passed = (res.returncode == 0)
            if not passed:
                print("Oracle failure stderr:", res.stderr)
                print("Oracle failure stdout:", res.stdout)
        else:
            print(f"No oracle defined for {instance_id}")

        oracle_passed = passed
        changed_files = _changed_files(scratch_dir, baseline)
        terminal = getattr(result, "terminal", None)
        completed = getattr(terminal, "value", str(terminal)).lower() == "completed"
        passed = completed and bool(changed_files) and oracle_passed
        diff_size = get_diff_size(scratch_dir, baseline)
        print("\n=== CONTENT SNAPSHOT ===")
        print(json.dumps({
            "subject_digest": _snapshot_digest(baseline),
            "changed_files": _changed_files(scratch_dir, baseline),
        }, sort_keys=True))
        
        print("\n=== TELEMETRY ===")
        if result and getattr(result, "telemetry", None):
            print(result.telemetry)
            
        return _enrich_result({
            "challenge": instance_id,
            "tier": "VERIFIED",
            "passed": passed,
            "oracle_passed": oracle_passed,
            "changed_files": changed_files,
            "diagnosis": _diagnose_result(completed, changed_files, oracle_passed),
            "elapsed": elapsed,
            "turns": turns,
            "tokens": tokens,
            "cost_micros": cost,
            "diff_size": diff_size,
            "scratch_dir": str(scratch_dir),
            "benchmark_identity": _benchmark_identity(
                instance_id, scratch_dir, baseline, model, run_timeout,
            ),
        }, result)
    finally:
        if not keep_dir:
            shutil.rmtree(scratch_dir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SWE challenges against Vanguard.")
    parser.add_argument("--challenge", type=str, help="Specific challenge ID to run")
    parser.add_argument("--tiers", type=str, help="Comma-separated list of tiers to run (e.g. 1,2,3)")
    parser.add_argument("--smoke", action="store_true",
                        help="Run the fixed 12-task preregistered smoke set")
    parser.add_argument("--verified", type=str, default=None, help="Run a real SWE-bench Verified instance from tools/005_SWE_VERIFIED_REPO (e.g. pallets__flask-5014, psf__requests-1142)")
    # Resolved from the registry rather than hardcoded: a literal here is a
    # second source of `D_R` model identity that drifts from the registry the
    # other runners resolve, so two runs can disagree about what "default" meant.
    from vanguard.packages.adapters.models.config import get_default_model

    parser.add_argument("--model", type=str, default=get_default_model(), help="Model to use")
    parser.add_argument("--keep-dir", action="store_true", help="Keep temporary scratch directories")
    parser.add_argument(
        "--run-timeout", type=float, default=BENCHMARK_RUN_TIMEOUT_SECONDS,
        help="Maximum seconds for one runtime episode (default: 300)",
    )
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--report", type=str, default=None,
                        help="Write an immutable JSON measurement report (must not already exist)")
    args = parser.parse_args()

    if args.worker:
        return _worker_main()

    # Load API key
    res = load_api_key(_REPO_ROOT)
    if res.ok and res.value:
        os.environ["OPENROUTER_API_KEY"] = res.value
    else:
        print(f"Warning: Failed to load OPENROUTER_API_KEY from .env: {res.error}", file=sys.stderr)

    results = []
    
    if args.verified:
        print(f"\n{'=' * 60}\nRunning VERIFIED {args.verified}...\n{'=' * 60}")
        res_data = run_verified_challenge(
            args.verified, args.model, args.keep_dir, args.run_timeout,
        )
        results.append(res_data)
    else:
        # Determine which challenges to run
        to_run = []
        selectors = sum(bool(value) for value in (args.challenge, args.tiers, args.smoke))
        if selectors > 1:
            print("Error: choose only one of --challenge, --tiers, or --smoke", file=sys.stderr)
            return 1
        if args.challenge:
            if args.challenge not in CHALLENGES:
                print(f"Error: Unknown challenge {args.challenge}", file=sys.stderr)
                return 1
            to_run.append(args.challenge)
        elif args.tiers:
            try:
                tiers = {int(t.strip()) for t in args.tiers.split(",")}
            except ValueError:
                print("Error: --tiers must be a comma-separated list of integers", file=sys.stderr)
                return 1
            to_run = [c for c, obj in CHALLENGES.items() if obj.tier in tiers]
        elif args.smoke:
            to_run = list(SMOKE_CHALLENGES)
        else:
            print("Error: Must specify --challenge, --tiers, --smoke, or --verified", file=sys.stderr)
            return 1
    
        if not to_run:
            print("No challenges matched criteria.", file=sys.stderr)
            return 0
    
        print(f"Running {len(to_run)} challenges...")
        
        for cid in to_run:
            print(f"\n{'=' * 60}\nRunning {cid}...\n{'=' * 60}")
            res_data = run_challenge(cid, args.model, args.keep_dir, args.run_timeout)
            results.append(res_data)

    # Print summary report
    print("\n\n" + "=" * 80)
    print(f"{'Challenge':<35} | {'Tier':<8} | {'Score':<6} | {'Time(s)':<8} | {'Turns':<6} | {'Tokens':<8} | {'Cost(µ$)':<9} | {'Diff':<6}")
    print("-" * 80)
    for r in results:
        score = "PASS" if r["passed"] else "FAIL"
        print(
            f"{r['challenge']:<35} | {str(r['tier']):<8} | {score:<6} | "
            f"{r['elapsed']:<8.1f} | {str(r['turns']):<6} | "
            f"{str(r['tokens']):<8} | {str(r['cost_micros']):<9} | "
            f"{str(r['diff_size']):<6}"
        )
    
    passed_count = sum(1 for r in results if r["passed"])
    print("=" * 80)
    print(f"Total Passed: {passed_count}/{len(results)} ({(passed_count/len(results))*100:.1f}%)")
    
    if args.keep_dir:
        print("\nScratch directories kept:")
        for r in results:
            print(f"  {r['challenge']}: {r['scratch_dir']}")

    if args.report:
        try:
            _write_report(args.report, results)
        except FileExistsError:
            print(f"Refusing to overwrite existing report: {args.report}", file=sys.stderr)
            return 2

    return 0 if passed_count == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
