"""Clean, exterior-oracle execution primitives for the v0.9 benchmark.

The agent workspace contains public task material only.  Hidden oracle source is
materialized in a distinct evaluator directory after agent execution and is
never passed to the executor callback.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import ExitStack
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping

from benchmarks.swe_bench.challenges import CHALLENGES, SWEProChallenge

SCHEMA = "aether.frontier-benchmark/2"
SUBSET = (
    "tier1_lru_ttl_cache",
    "tier2_web_reactive_signals",
    "tier3_api_idempotency_middleware",
)
_IGNORED_PARTS = frozenset({".git", ".vanguard", "__pycache__"})


def digest_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    return digest_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def evidence_digest(value: object) -> str:
    """Digest semantic evidence while excluding nondeterministic durations."""
    if isinstance(value, Mapping):
        stable = {key: evidence_digest_value(item) for key, item in value.items()
                  if key not in {"wall_ms", "stdout_digest", "stderr_digest",
                                 "row_digest", "report_digest"}}
        return canonical_digest(stable)
    return canonical_digest(evidence_digest_value(value))


def evidence_digest_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: evidence_digest_value(item) for key, item in value.items()
                if key not in {"wall_ms", "stdout_digest", "stderr_digest",
                               "row_digest", "report_digest"}}
    if isinstance(value, (list, tuple)):
        return [evidence_digest_value(item) for item in value]
    return value


def snapshot(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in _IGNORED_PARTS for part in path.parts):
            continue
        relative = path.relative_to(root).as_posix()
        result[relative] = digest_bytes(path.read_bytes())
    return result


@dataclass(frozen=True)
class ExecutionTelemetry:
    terminal: str
    terminal_reason: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    cached_tokens: int | None = None
    cost_usd: float | None = None
    cost_provenance: str = "unknown"
    trajectory_digest: str | None = None


@dataclass(frozen=True)
class PublicChallenge:
    """Model-facing challenge projection; evaluator material is excluded."""

    challenge_id: str
    tier: int
    title: str
    kind: str
    brief: str
    files: Mapping[str, str]


Executor = Callable[[Path, PublicChallenge], ExecutionTelemetry]


def _public_challenge(challenge: SWEProChallenge) -> PublicChallenge:
    return PublicChallenge(
        challenge_id=challenge.challenge_id,
        tier=challenge.tier,
        title=challenge.title,
        kind=challenge.kind,
        brief=challenge.brief,
        files=dict(challenge.files),
    )


def _materialize_public(challenge: SWEProChallenge, root: Path) -> None:
    for relative, content in challenge.files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    (root / "TASK.md").write_text(challenge.brief + "\n", encoding="utf-8")


def _evaluate(challenge: SWEProChallenge, workspace: Path, timeout: float) -> dict[str, object]:
    """Copy the submitted workspace and execute a sealed oracle externally."""
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="v090-evaluator-") as temp:
        evaluator_root = Path(temp)
        submitted = evaluator_root / "submitted"
        sealed = evaluator_root / "sealed"
        shutil.copytree(workspace, submitted, ignore=shutil.ignore_patterns(".git", ".vanguard", "__pycache__"))
        sealed.mkdir()
        oracle = sealed / "test_oracle.py"
        oracle.write_text(challenge.oracle_code, encoding="utf-8")
        oracle_digest = digest_bytes(oracle.read_bytes())
        try:
            completed = subprocess.run(
                [sys.executable, "-I", "-c",
                 "import runpy,sys;p=sys.argv[2];sys.path.insert(0,sys.argv[1]);sys.argv=[p];runpy.run_path(p,run_name='__main__')",
                 str(submitted), str(oracle)], cwd=submitted, env=dict(os.environ),
                capture_output=True, text=True, timeout=timeout, check=False,
            )
        except subprocess.TimeoutExpired:
            return {"instrument_valid": False, "result": None, "reason": "evaluator_timeout",
                    "oracle_digest": oracle_digest, "wall_ms": round((time.monotonic() - started) * 1000, 3)}
        return {
            "instrument_valid": True,
            "result": completed.returncode == 0,
            "reason": None if completed.returncode == 0 else "oracle_failed",
            "oracle_digest": oracle_digest,
            "exit_code": completed.returncode,
            "stdout_digest": digest_bytes(completed.stdout.encode()),
            "stderr_digest": digest_bytes(completed.stderr.encode()),
            "wall_ms": round((time.monotonic() - started) * 1000, 3),
        }


def run_row(challenge_id: str, preset: str, executor: Executor, *, timeout: float = 30.0,
            non_empirical: bool = True,
            workspace_root: Path | None = None) -> dict[str, object]:
    challenge = CHALLENGES[challenge_id]
    with ExitStack() as stack:
        if workspace_root is None:
            workspace = Path(stack.enter_context(
                tempfile.TemporaryDirectory(prefix="v090-agent-")))
        else:
            workspace_root.mkdir(parents=True, exist_ok=True)
            workspace = Path(tempfile.mkdtemp(
                prefix=f"{challenge_id}-{preset}-", dir=workspace_root))
        _materialize_public(challenge, workspace)
        public_files = snapshot(workspace)
        oracle_digest = digest_bytes(challenge.oracle_code.encode())
        if any(value == oracle_digest for value in public_files.values()):
            raise RuntimeError("hidden oracle leaked into agent workspace")

        baseline = _evaluate(challenge, workspace, timeout)
        identity = {
            "challenge_id": challenge_id,
            "difficulty": {1: "Easy", 2: "Medium", 3: "Hard"}.get(challenge.tier, f"Tier-{challenge.tier}"),
            "task_digest": canonical_digest({"brief": challenge.brief, "files": challenge.files}),
            "oracle_digest": oracle_digest,
            "preset": preset,
        }
        if not baseline["instrument_valid"]:
            return _row(identity, "INSTRUMENT_ERROR", "baseline_evaluator_invalid", baseline, None, public_files, public_files, non_empirical)
        if baseline["result"]:
            return _row(identity, "DATASET_INVALID", "baseline_already_passes", baseline, None, public_files, public_files, non_empirical)

        # The executor receives only the public projection.  The sealed oracle
        # remains available solely to the exterior evaluator below.
        telemetry = executor(workspace, _public_challenge(challenge))
        after = snapshot(workspace)
        changed = sorted(path for path in set(public_files) | set(after) if public_files.get(path) != after.get(path))
        if not changed:
            return _row(identity, "NO_PATCH", "completed_without_source_patch", baseline, telemetry, public_files, after, non_empirical)
        verdict = _evaluate(challenge, workspace, timeout)
        terminal = "COMPLETED" if verdict["instrument_valid"] and verdict["result"] else (
            "INSTRUMENT_ERROR" if not verdict["instrument_valid"] else "FAILED_ORACLE"
        )
        reason = "completed_patch_passed_oracle" if terminal == "COMPLETED" else str(verdict["reason"])
        return _row(identity, terminal, reason, verdict, telemetry, public_files, after, non_empirical)


def _row(identity: Mapping[str, object], terminal: str, reason: str,
         oracle: Mapping[str, object], telemetry: ExecutionTelemetry | None,
         before: Mapping[str, str], after: Mapping[str, str], non_empirical: bool = True) -> dict[str, object]:
    changed = sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))
    usage = {
        "prompt_tokens": telemetry.prompt_tokens if telemetry else None,
        "completion_tokens": telemetry.completion_tokens if telemetry else None,
        "cached_tokens": telemetry.cached_tokens if telemetry else None,
        "cost_usd": telemetry.cost_usd if telemetry else None,
        "cost_provenance": telemetry.cost_provenance if telemetry else "not_called",
    }
    body: dict[str, object] = {
        "schema": SCHEMA, **identity, "terminal": terminal, "terminal_reason": reason,
        "changed_files": changed, "before_digest": canonical_digest(before),
        "after_digest": canonical_digest(after), "oracle": dict(oracle), "usage": usage,
        "trajectory_digest": telemetry.trajectory_digest if telemetry else None,
        "non_empirical": non_empirical,
    }
    body["row_digest"] = evidence_digest(body)
    return body


def noop_executor(workspace: Path, challenge: PublicChallenge) -> ExecutionTelemetry:
    del workspace, challenge
    return ExecutionTelemetry("completed", "calibration_noop")


def validate_subset(executor: Executor = noop_executor) -> dict[str, object]:
    rows = [run_row(challenge_id, "instrument-calibration", executor) for challenge_id in SUBSET]
    body: dict[str, object] = {"schema": "aether.frontier-benchmark-subset/1", "non_empirical": True, "rows": rows}
    body["report_digest"] = evidence_digest(body)
    return body
