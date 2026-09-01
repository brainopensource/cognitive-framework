#!/usr/bin/env python3
"""Truthful, provider-neutral runner for the preregistered M-8 workload.

Dry-run is a structural preflight. It never calls a model, executes a task,
or fabricates empirical measurements. Live execution is driven through
injected runtime and exterior-evaluator seams, never a second provider client.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef, Verdict
from vanguard.packages.ports.event_store import Result
from benchmarks.m8_heldout.receipts import PromotionReceipt, RollbackReceipt

__all__ = [
    "BudgetLimits", "Disposition", "ExecutionRecord", "TaskAttempt",
    "TaskTelemetry", "WorkloadDefinition", "digest_of", "execute_empirical_run",
    "load_workload", "RuntimeTaskExecutor", "verify_bundle",
    "PromotionReceipt", "RollbackReceipt",
]


class Disposition(str, Enum):
    """Closed vocabulary for benchmark observations and missingness."""

    NOT_RUN = "NOT_RUN"
    INVALID_TASK = "INVALID_TASK"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    TIMED_OUT = "TIMED_OUT"
    MODEL_PROTOCOL_ERROR = "MODEL_PROTOCOL_ERROR"
    NO_PATCH = "NO_PATCH"
    PATCH_REJECTED = "PATCH_REJECTED"
    EVALUATOR_UNAVAILABLE = "EVALUATOR_UNAVAILABLE"
    EVALUATOR_FAILED = "EVALUATOR_FAILED"
    PASSED = "PASSED"


def digest_of(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class BudgetLimits:
    """Hard ceilings checked before every model/evaluator call."""

    per_task_usd_micros: int = 250_000
    aggregate_usd_micros: int = 1_000_000
    per_task_tokens: int = 2_000_000
    aggregate_tokens: int = 2_000_000
    per_task_turns: int = 1
    aggregate_turns: int = 10_000
    per_task_wall_clock_seconds: float = 60.0

    def __post_init__(self) -> None:
        if any(value < 0 for value in (
            self.per_task_usd_micros, self.aggregate_usd_micros,
            self.per_task_tokens, self.aggregate_tokens,
            self.per_task_turns, self.aggregate_turns,
        )) or self.per_task_wall_clock_seconds <= 0:
            raise ValueError("benchmark ceilings must be non-negative and timeout must be positive")


@dataclass(frozen=True, slots=True)
class WorkloadDefinition:
    dev: tuple[str, ...]
    held_out: tuple[str, ...]
    adversarial: tuple[str, ...] = ()
    transfer: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.held_out:
            raise ValueError("a held-out split is required")
        splits = {"dev": self.dev, "held-out": self.held_out,
                  "adversarial": self.adversarial, "transfer": self.transfer}
        seen: set[str] = set()
        for name, tasks in splits.items():
            if any(not isinstance(task, str) or not task for task in tasks):
                raise ValueError(f"{name} task ids must be non-empty strings")
            if len(set(tasks)) != len(tasks):
                raise ValueError(f"{name} split contains duplicate task ids")
            overlap = seen.intersection(tasks)
            if overlap:
                raise ValueError(f"tasks {sorted(overlap)} are contaminated across splits")
            seen.update(tasks)

    def digest(self) -> str:
        return digest_of({
            "dev": sorted(self.dev), "heldOut": sorted(self.held_out),
            "adversarial": sorted(self.adversarial), "transfer": sorted(self.transfer),
        })


def load_workload(workload_file: Path | None = None) -> tuple[WorkloadDefinition, list[dict[str, Any]]]:
    path = workload_file or (_REPO_ROOT / "benchmarks/m8_heldout/fixtures/workload.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks = data.get("tasks")
    if not isinstance(tasks, list) or any(not isinstance(task, Mapping) for task in tasks):
        raise ValueError("workload tasks must be an array of objects")
    dev = tuple(t["id"] for t in tasks if t.get("split") == "dev")
    held_out = tuple(t["id"] for t in tasks if t.get("split") == "held_out")
    adversarial = tuple(t["id"] for t in tasks if t.get("split") == "adversarial")
    transfer = tuple(t["id"] for t in tasks if t.get("split") == "transfer")
    return WorkloadDefinition(dev, held_out, adversarial, transfer), [dict(t) for t in tasks]


@dataclass(frozen=True, slots=True)
class TaskAttempt:
    """One actual runtime episode result, supplied by the official executor."""

    output: Any = ""
    patch: str | None = None
    trajectory_digest: str | None = None
    usage: Mapping[str, Any] | None = None
    route_identity: Mapping[str, Any] | None = None
    attempts: int = 1
    elapsed_seconds: float | None = None


class TaskExecutor(Protocol):
    def execute(self, task: Mapping[str, Any], workspace: Path, arm: str) -> TaskAttempt | Mapping[str, Any]:
        ...


class ExteriorEvaluator(Protocol):
    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol) -> Result[Verdict] | Verdict:
        ...


class RuntimeTaskExecutor:
    """Small benchmark adapter over the existing runtime composition root.

    The class intentionally returns the runtime's captured trajectory and
    usage, but never interprets model prose as a successful patch. A caller
    that captures a patch artifact can provide it through a richer executor
    implementation without changing the benchmark driver.
    """

    def __init__(self, model: Any = None, *, model_name: str | None = None,
                 profile_id: str = "local", manifest_path: Path | None = None) -> None:
        self._model = model
        self._model_name = model_name
        self._profile_id = profile_id
        self._manifest_path = manifest_path

    def execute(self, task: Mapping[str, Any], workspace: Path, arm: str) -> TaskAttempt:
        from vanguard.packages.runtime.root import Runtime, TaskContext

        model = self._model
        # Model selection remains the runtime's composition responsibility.
        # This seam accepts an already selected ModelPort; it never handles
        # provider credentials or model-policy literals itself.
        manifest = self._manifest_path or (_REPO_ROOT / "vanguard/packages/agency/manifests/vg-code-default/manifest.json")
        task_id = str(task["id"])
        context = TaskContext(
            brief=str(task.get("prompt") or task.get("title") or task_id),
            repo_path=workspace, run_id=f"m8:{task_id}:{arm}",
            episode_id=f"m8:{task_id}:{arm}", max_turns=1,
            project_id="m8-heldout",
            preregistration={"task_digest": _task_digest(task)},
        )
        started = time.monotonic()
        result = Runtime.execute_profiled(
            manifest, context, profile_id=self._profile_id, interactive=False, model=model)
        telemetry = result.telemetry
        route = {
            "provider": getattr(model, "provider", None),
            "model": getattr(model, "model", None),
            "compositionDigest": result.composition_digest,
        }
        trajectory_digest = digest_of(result.trajectory) if result.trajectory is not None else None
        return TaskAttempt(
            output=result.detail, trajectory_digest=trajectory_digest,
            usage={"prompt_tokens": telemetry.prompt_tokens,
                   "completion_tokens": telemetry.completion_tokens,
                   "usd_micros": telemetry.usd_micros,
                   "turns": telemetry.turns},
            route_identity=route, elapsed_seconds=time.monotonic() - started)


@dataclass(frozen=True, slots=True)
class TaskTelemetry:
    task_id: str
    split: str
    arm: str
    composition_version: str
    disposition: Disposition
    invoked: bool = False
    grounded: bool = False
    verified: bool = False
    turns: int | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    usd_micros: int | None = None
    latency_seconds: float | None = None
    task_digest: str = ""
    base_commit: str | None = None
    workspace_preimage_digest: str | None = None
    postimage_digest: str | None = None
    patch_digest: str | None = None
    trajectory_digest: str | None = None
    evaluator_identity_digest: str | None = None
    route_identity: Mapping[str, Any] | None = None

    @property
    def passed(self) -> bool:
        return self.disposition is Disposition.PASSED

    def to_dict(self) -> dict[str, Any]:
        usage: dict[str, Any] = {
            "turns": self.turns, "promptTokens": self.prompt_tokens,
            "completionTokens": self.completion_tokens, "usdMicros": self.usd_micros,
        }
        if self.usd_micros is not None:
            usage["costUsd"] = round(self.usd_micros / 1_000_000, 6)
        return {
            "taskId": self.task_id, "split": self.split, "arm": self.arm,
            "compositionVersion": self.composition_version,
            "disposition": self.disposition.value, "passed": self.passed,
            "invoked": self.invoked, "grounded": self.grounded, "verified": self.verified,
            "usage": usage, "latencySeconds": self.latency_seconds,
            "taskDigest": self.task_digest, "baseCommit": self.base_commit,
            "workspacePreimageDigest": self.workspace_preimage_digest,
            "postimageDigest": self.postimage_digest, "patchDigest": self.patch_digest,
            "trajectoryDigest": self.trajectory_digest,
            "evaluatorIdentityDigest": self.evaluator_identity_digest,
            "routeIdentity": dict(self.route_identity or {}),
        }


ExecutionRecord = TaskTelemetry


def _task_digest(task: Mapping[str, Any]) -> str:
    return digest_of(dict(task))


def verify_bundle(bundle: Mapping[str, Any]) -> bool:
    """Verify the content address of a returned evidence/preflight bundle."""
    recorded = bundle.get("bundleDigest") or bundle.get("bundle_digest")
    if not isinstance(recorded, str):
        return False
    body = dict(bundle)
    body.pop("bundleDigest", None)
    body.pop("bundle_digest", None)
    return recorded == digest_of(body)


def _safe_relative(path: str) -> str:
    candidate = Path(path.replace("\\", "/"))
    if candidate.is_absolute() or ".." in candidate.parts or not str(candidate):
        raise ValueError(f"patch path escapes workspace: {path!r}")
    return candidate.as_posix().removeprefix("a/").removeprefix("b/")


def _patch_files(patch: str) -> list[tuple[str, str, list[str]]]:
    if not isinstance(patch, str) or not patch.strip():
        raise ValueError("patch is empty")
    lines = patch.splitlines()
    result: list[tuple[str, str, list[str]]] = []
    index = 0
    while index < len(lines):
        if lines[index].startswith("diff --git "):
            index += 1
            continue
        if not lines[index].startswith("--- ") or index + 1 >= len(lines):
            index += 1
            continue
        old = lines[index][4:].split("\t", 1)[0].split(" ", 1)[0]
        new_line = lines[index + 1]
        if not new_line.startswith("+++ "):
            raise ValueError("unified patch is missing its new-file header")
        new = new_line[4:].split("\t", 1)[0].split(" ", 1)[0]
        index += 2
        hunk_lines: list[str] = []
        while index < len(lines) and not lines[index].startswith("--- "):
            if lines[index].startswith(("@@ ", " ", "+", "-", "\\")):
                hunk_lines.append(lines[index])
            index += 1
        if not any(line.startswith("@@ ") for line in hunk_lines):
            raise ValueError("unified patch has no hunks")
        result.append((old, new, hunk_lines))
    if not result:
        raise ValueError("output is not a unified patch")
    return result


def _apply_patch(root: Path, patch: str) -> None:
    for old_raw, new_raw, hunk_lines in _patch_files(patch):
        old = None if old_raw == "/dev/null" else _safe_relative(old_raw)
        new = None if new_raw == "/dev/null" else _safe_relative(new_raw)
        target = new or old
        if target is None:
            raise ValueError("patch has no target")
        if not (root / target).resolve().is_relative_to(root.resolve()):
            raise ValueError("patch target escapes workspace")
        original = [] if old is None else (root / old).read_text(encoding="utf-8").splitlines()
        output: list[str] = []
        cursor = 0
        for line in hunk_lines:
            if line.startswith("@@") or line.startswith("\\"):
                continue
            if not line:
                raise ValueError("malformed empty patch line")
            marker, content = line[0], line[1:]
            if marker == " ":
                if cursor >= len(original) or original[cursor] != content:
                    raise ValueError(f"patch context mismatch in {target}")
                output.append(content)
                cursor += 1
            elif marker == "-":
                if cursor >= len(original) or original[cursor] != content:
                    raise ValueError(f"patch deletion mismatch in {target}")
                cursor += 1
            elif marker == "+":
                output.append(content)
            else:
                raise ValueError("malformed unified patch hunk")
        output.extend(original[cursor:])
        if new is None:
            if old is not None and (root / old).exists():
                (root / old).unlink()
            continue
        destination = root / new
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("\n".join(output) + ("\n" if output else ""), encoding="utf-8")


def _workspace_digest(root: Path) -> str:
    entries: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"workspace contains symlink: {path.relative_to(root)}")
        if path.is_file():
            entries.append({"path": path.relative_to(root).as_posix(),
                            "digest": "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()})
    return digest_of(entries)


def _materialize(source: Path | None, task: Mapping[str, Any]) -> tuple[tempfile.TemporaryDirectory[str], Path, str]:
    temp = tempfile.TemporaryDirectory(prefix="aether-m8-task-")
    root = Path(temp.name)
    if source is not None:
        source = source.resolve()
        if not source.is_dir():
            temp.cleanup()
            raise ValueError(f"workspace is not a directory: {source}")
        for entry in source.rglob("*"):
            if entry.is_symlink():
                temp.cleanup()
                raise ValueError(f"workspace contains symlink: {entry.relative_to(source)}")
        shutil.copytree(source, root, dirs_exist_ok=True)
    return temp, root, _workspace_digest(root)


def _normalise_attempt(raw: TaskAttempt | Mapping[str, Any]) -> TaskAttempt:
    if isinstance(raw, TaskAttempt):
        return raw
    if not isinstance(raw, Mapping):
        raise TypeError("task executor must return TaskAttempt or an object mapping")
    usage = raw.get("usage")
    if usage is None:
        usage = {key: raw[key] for key in ("prompt_tokens", "completion_tokens", "usd_micros", "turns") if key in raw}
    return TaskAttempt(
        output=raw.get("output", raw.get("content", "")), patch=raw.get("patch"),
        trajectory_digest=raw.get("trajectory_digest", raw.get("trajectoryDigest")),
        usage=usage if isinstance(usage, Mapping) else {},
        route_identity=raw.get("route_identity", raw.get("routeIdentity", {})),
        attempts=int(raw.get("attempts", 1)), elapsed_seconds=raw.get("elapsed_seconds", raw.get("latency_seconds")),
    )


def _usage(attempt: TaskAttempt) -> tuple[int | None, int | None, int | None, int | None]:
    raw = attempt.usage or {}
    def integer(*names: str) -> int | None:
        for name in names:
            if name in raw and raw[name] is not None:
                value = raw[name]
                if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
                    return None
                return int(value)
        return None
    return integer("prompt_tokens", "promptTokens"), integer("completion_tokens", "completionTokens"), integer("usd_micros", "usdMicros"), integer("turns")


def _evaluator_verdict(result: Result[Verdict] | Verdict) -> Verdict | None:
    if isinstance(result, Verdict):
        return result
    return result.value if isinstance(result, Result) and result.ok and isinstance(result.value, Verdict) else None


def _claims_pass(verdict: Verdict) -> bool:
    if verdict.outcome != "claims" or not verdict.claims:
        return False
    claims = [claim for claim in verdict.claims if isinstance(claim, Mapping)]
    collected = any(int(claim.get("tests_collected", claim.get("testsCollected", 0)) or 0) > 0 for claim in claims)
    passed = any(bool(claim.get("passed", claim.get("pass", False))) for claim in claims)
    return collected and passed


def _planned_records(workload: WorkloadDefinition, tasks: Mapping[str, Mapping[str, Any]], base_commit: str | None) -> list[TaskTelemetry]:
    rows: list[TaskTelemetry] = []
    planned = [*((task, "control", "composition-v1") for task in sorted(workload.held_out)),
               *((task, "treatment", "composition-v2") for task in sorted(workload.held_out)),
               *((task, "treatment", "composition-v2") for task in sorted(workload.adversarial)),
               *((task, "treatment", "composition-v2") for task in sorted(workload.transfer))]
    for task_id, arm, version in planned:
        meta = tasks[task_id]
        rows.append(TaskTelemetry(task_id, str(meta["split"]), arm, version, Disposition.NOT_RUN,
                                  task_digest=_task_digest(meta), base_commit=base_commit))
    return rows


def execute_empirical_run(
    workload: WorkloadDefinition,
    tasks_meta: Sequence[Mapping[str, Any]],
    *,
    candidate_id: str = "candidate",
    baseline_version: str = "composition-v1",
    candidate_version: str = "composition-v2",
    generator_id: str = "runtime-backed-benchmark",
    evaluator_id: str = "exterior-evaluator",
    promoter_id: str = "independent-promoter",
    promoter_key: bytes | None = None,
    mode: str = "dry-run",
    model: str | None = None,
    api_key: str | None = None,
    executor: TaskExecutor | Callable[[Mapping[str, Any], Path, str], TaskAttempt | Mapping[str, Any]] | None = None,
    evaluator: ExteriorEvaluator | None = None,
    workspace_root: Path | None = None,
    base_commit: str | None = None,
    limits: BudgetLimits | None = None,
    **_legacy: Any,
) -> dict[str, Any]:
    """Run structural preflight or actual attempts through supplied seams.

    ``api_key`` is accepted only for source compatibility and intentionally
    ignored. Credentials belong to the official adapter's environment.
    """
    del api_key, model, generator_id, promoter_id, promoter_key
    if mode not in {"dry-run", "live", "cassette"}:
        raise ValueError("mode must be dry-run, cassette, or live")
    limits = limits or BudgetLimits()
    tasks = {str(task.get("id")): dict(task) for task in tasks_meta if isinstance(task, Mapping) and task.get("id")}
    expected = set(workload.dev) | set(workload.held_out) | set(workload.adversarial) | set(workload.transfer)
    if set(tasks) != expected:
        missing, extra = sorted(expected - set(tasks)), sorted(set(tasks) - expected)
        rows = _planned_records(workload, tasks, base_commit) if not missing else []
        return {"schema": "aether.m8-evidence-bundle/1", "mode": mode, "evidenceKind": "structural_preflight",
                "workloadDigest": workload.digest(), "workload_digest": workload.digest(),
                "disposition": Disposition.INVALID_TASK.value, "error": f"task metadata mismatch missing={missing} extra={extra}",
                "records": [row.to_dict() for row in rows], "promotionEvidence": None}
    if mode == "dry-run":
        records = _planned_records(workload, tasks, base_commit)
        body = {"schema": "aether.m8-evidence-bundle/1", "mode": "dry-run",
                "evidenceKind": "structural_preflight", "workloadDigest": workload.digest(),
                "workload_digest": workload.digest(),
                "candidate": {"candidateId": candidate_id, "baselineVersion": baseline_version, "candidateVersion": candidate_version},
                "empirical": {"success": None, "lift": None, "regression": None, "cost": None, "tokens": None, "latency": None},
                "evaluation": {"status": Disposition.NOT_RUN.value, "promotable": None},
                "promotionEvidence": None, "rollbackEvidence": None,
                "records": [row.to_dict() for row in records]}
        body["bundleDigest"] = digest_of(body)
        body["bundle_digest"] = body["bundleDigest"]
        return body
    if executor is None:
        raise ValueError("live benchmark execution requires an injected official runtime executor")
    if evaluator is None:
        raise ValueError("live benchmark execution requires an injected exterior evaluator")

    records: list[TaskTelemetry] = []
    aggregate_cost = aggregate_tokens = aggregate_turns = 0
    cost_observed = tokens_observed = turns_observed = False
    planned = [*((task, "control", baseline_version) for task in sorted(workload.held_out)),
               *((task, "treatment", candidate_version) for task in sorted(workload.held_out)),
               *((task, "treatment", candidate_version) for task in sorted(workload.adversarial)),
               *((task, "treatment", candidate_version) for task in sorted(workload.transfer))]
    for task_id, arm, version in planned:
        task = tasks[task_id]
        temp, root, preimage = _materialize(workspace_root, task)
        started = time.monotonic()
        try:
            if aggregate_cost >= limits.aggregate_usd_micros or aggregate_tokens >= limits.aggregate_tokens or aggregate_turns >= limits.aggregate_turns:
                records.append(TaskTelemetry(task_id, str(task["split"]), arm, version, Disposition.BUDGET_EXHAUSTED,
                                              task_digest=_task_digest(task), base_commit=base_commit, workspace_preimage_digest=preimage))
                continue
            try:
                call = executor.execute(task, root, arm) if hasattr(executor, "execute") else executor(task, root, arm)  # type: ignore[misc]
                attempt = _normalise_attempt(call)
            except TimeoutError:
                records.append(TaskTelemetry(task_id, str(task["split"]), arm, version, Disposition.TIMED_OUT, invoked=True,
                                              task_digest=_task_digest(task), base_commit=base_commit, workspace_preimage_digest=preimage,
                                              latency_seconds=time.monotonic() - started))
                continue
            except (ConnectionError, OSError, RuntimeError) as exc:
                records.append(TaskTelemetry(task_id, str(task["split"]), arm, version, Disposition.PROVIDER_UNAVAILABLE, invoked=True,
                                              task_digest=_task_digest(task), base_commit=base_commit, workspace_preimage_digest=preimage,
                                              latency_seconds=time.monotonic() - started, route_identity={"failure": type(exc).__name__}))
                continue
            except (TypeError, ValueError) as exc:
                records.append(TaskTelemetry(task_id, str(task["split"]), arm, version, Disposition.MODEL_PROTOCOL_ERROR, invoked=True,
                                              task_digest=_task_digest(task), base_commit=base_commit, workspace_preimage_digest=preimage,
                                              latency_seconds=time.monotonic() - started, route_identity={"failure": str(exc)}))
                continue
            prompt, completion, cost, turns = _usage(attempt)
            if attempt.attempts != 1:
                records.append(TaskTelemetry(task_id, str(task["split"]), arm, version, Disposition.MODEL_PROTOCOL_ERROR, invoked=True,
                                              task_digest=_task_digest(task), base_commit=base_commit, workspace_preimage_digest=preimage,
                                              latency_seconds=time.monotonic() - started, prompt_tokens=prompt, completion_tokens=completion,
                                              usd_micros=cost, turns=turns, route_identity={"failure": "second_episode_rejected", **dict(attempt.route_identity or {})}))
                continue
            elapsed = attempt.elapsed_seconds if attempt.elapsed_seconds is not None else time.monotonic() - started
            common = dict(task_digest=_task_digest(task), base_commit=base_commit, workspace_preimage_digest=preimage,
                          latency_seconds=elapsed, prompt_tokens=prompt, completion_tokens=completion, usd_micros=cost, turns=turns,
                          route_identity=attempt.route_identity)
            # Provider-reported usage is authoritative when present. Count it
            # immediately after the model call so a NO_PATCH or rejected patch
            # cannot make the next task appear cheaper than it was.
            aggregate_cost += cost or 0
            aggregate_tokens += (prompt or 0) + (completion or 0)
            aggregate_turns += turns or 0
            cost_observed = cost_observed or cost is not None
            tokens_observed = tokens_observed or (prompt is not None and completion is not None)
            turns_observed = turns_observed or turns is not None
            if elapsed > limits.per_task_wall_clock_seconds:
                records.append(TaskTelemetry(task_id, str(task["split"]), arm, version, Disposition.TIMED_OUT, invoked=True, **common))
                continue
            if ((cost is not None and cost > limits.per_task_usd_micros) or
                (prompt is not None and completion is not None and prompt + completion > limits.per_task_tokens) or
                (turns is not None and turns > limits.per_task_turns)):
                records.append(TaskTelemetry(task_id, str(task["split"]), arm, version, Disposition.BUDGET_EXHAUSTED, invoked=True, **common))
                continue
            if aggregate_cost > limits.aggregate_usd_micros or aggregate_tokens > limits.aggregate_tokens or aggregate_turns > limits.aggregate_turns:
                records.append(TaskTelemetry(task_id, str(task["split"]), arm, version, Disposition.BUDGET_EXHAUSTED, invoked=True, **common))
                continue
            output = attempt.output if isinstance(attempt.output, str) else ""
            patch = attempt.patch
            if patch is None and isinstance(attempt.output, Mapping):
                patch = attempt.output.get("patch") or attempt.output.get("diff")
            if not patch and output:
                possible = output[output.find("--- "):] if "--- " in output else ""
                patch = possible if "+++ " in possible and "@@ " in possible else None
            if not isinstance(patch, str) or not patch.strip():
                records.append(TaskTelemetry(task_id, str(task["split"]), arm, version, Disposition.NO_PATCH, invoked=True,
                                              trajectory_digest=attempt.trajectory_digest, **common))
                continue
            patch_digest = digest_of(patch)
            try:
                _apply_patch(root, patch)
                postimage = _workspace_digest(root)
            except (OSError, UnicodeError, ValueError) as exc:
                records.append(TaskTelemetry(task_id, str(task["split"]), arm, version, Disposition.PATCH_REJECTED, invoked=True,
                                              patch_digest=patch_digest, trajectory_digest=attempt.trajectory_digest,
                                              route_identity={"failure": str(exc), **dict(attempt.route_identity or {})}, **{k: v for k, v in common.items() if k != "route_identity"}))
                continue
            protocol = EvaluationProtocol("m8-heldout-exterior/1", {
                "task_digest": _task_digest(task), "workspace_preimage_digest": preimage,
                "postimage_digest": postimage, "patch_digest": patch_digest})
            eval_ref = RunRef(run_id=f"m8:{task_id}:{arm}", episode_id=f"m8:{task_id}:{arm}")
            try:
                verdict = _evaluator_verdict(evaluator.evaluate(eval_ref, protocol))
            except (ConnectionError, OSError, TimeoutError):
                verdict = None
            evaluator_digest = digest_of({"identity": evaluator_id, "protocol": protocol.name})
            disposition = (Disposition.PASSED if verdict is not None and _claims_pass(verdict)
                           else Disposition.EVALUATOR_FAILED if verdict is not None and verdict.outcome == "claims"
                           else Disposition.EVALUATOR_UNAVAILABLE)
            records.append(TaskTelemetry(task_id, str(task["split"]), arm, version, disposition, invoked=True, grounded=True,
                                          verified=disposition is Disposition.PASSED, postimage_digest=postimage,
                                          patch_digest=patch_digest, trajectory_digest=attempt.trajectory_digest,
                                          evaluator_identity_digest=evaluator_digest, **common))
        finally:
            temp.cleanup()

    treatment = [row for row in records if row.arm == "treatment" and row.split == "held_out"]
    control = {row.task_id: row for row in records if row.arm == "control" and row.split == "held_out"}
    baseline_passes = sum(row.passed for row in control.values())
    candidate_passes = sum(row.passed for row in treatment)
    gains = sorted(row.task_id for row in treatment if row.passed and not control[row.task_id].passed)
    regressions = sorted(row.task_id for row in treatment if not row.passed and control[row.task_id].passed)
    evaluated = [row for row in treatment if row.disposition in {Disposition.PASSED, Disposition.EVALUATOR_FAILED}]
    measured_rows = list(control.values()) + treatment
    complete_measurement = bool(measured_rows) and all(
        row.disposition in {Disposition.PASSED, Disposition.EVALUATOR_FAILED} for row in measured_rows)
    body = {"schema": "aether.m8-evidence-bundle/1", "mode": mode, "evidenceKind": "empirical_execution",
            "workloadDigest": workload.digest(), "workload_digest": workload.digest(),
            "candidate": {"candidateId": candidate_id},
            "empirical": {"baselinePasses": baseline_passes if complete_measurement else None,
                           "candidatePasses": candidate_passes if complete_measurement else None,
                           "heldOutTotal": len(treatment),
                           "heldOutLift": (candidate_passes - baseline_passes) / len(treatment) if complete_measurement and treatment else None,
                           "regressionRate": len(regressions) / len(treatment) if complete_measurement and treatment else None,
                           "grossGains": gains if complete_measurement else None,
                           "regressions": regressions if complete_measurement else None,
                           "evaluatedMeasurements": len(evaluated),
                           "totalCostUsdMicros": aggregate_cost if cost_observed else None,
                           "totalTokens": aggregate_tokens if tokens_observed else None,
                           "totalTurns": aggregate_turns if turns_observed else None},
            "evaluation": {"status": "COMPLETE" if complete_measurement else Disposition.NOT_RUN.value, "promotable": False},
            "promotionEvidence": None, "rollbackEvidence": None, "records": [row.to_dict() for row in records]}
    body["bundleDigest"] = digest_of(body)
    body["bundle_digest"] = body["bundleDigest"]
    return body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workload", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--mode", choices=["dry-run", "cassette", "live"], default="dry-run")
    parser.add_argument("--dry-run", action="store_true", help="explicit structural preflight alias for --mode dry-run")
    args = parser.parse_args()
    workload, tasks_meta = load_workload(args.workload)
    bundle = execute_empirical_run(workload, tasks_meta, mode="dry-run" if args.dry_run else args.mode)
    out_json = json.dumps(bundle, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(out_json, encoding="utf-8")
        print(f"Wrote structural/empirical bundle to {args.out} (digest: {bundle['bundleDigest']})")
    else:
        print(out_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
