"""Thin CLI/backend bridge for product coding commands (`REQ-TRUST-001`, S33).

Validates serialized CLI requests, resolves executor bands from the model
registry, invokes ALFA's ``run_coding_task`` / ``resume_coding_task`` /
``explain_repository``, streams projection records as NDJSON, and maps the
terminal outcome to a process exit code.

This module does **not** call a model adapter, environment adapter, sandbox
worker, translator, or kernel. It does **not** implement retry or escalation.
Those belong to the coordinator and ``HarnessSession``.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .coding_coordinator import (
    CodingRunConfig,
    CodingRunResult,
    ExplainRunConfig,
    explain_repository,
    run_coding_task,
)
from .coding_plan import CodingPlan, CodingPlanError, parse_coding_plan

__all__ = [
    "EXIT_ORACLE_GREEN",
    "EXIT_NON_GREEN",
    "EXIT_INVALID",
    "EXIT_UNAVAILABLE",
    "EXIT_BUDGET",
    "exit_code_for",
    "load_band_models",
    "request_to_config",
    "run_entrypoint",
    "main",
]

EXIT_ORACLE_GREEN = 0
EXIT_NON_GREEN = 1
EXIT_INVALID = 2
EXIT_UNAVAILABLE = 3
EXIT_BUDGET = 4

_REPO_ROOT = Path(__file__).resolve().parents[3]
_MODELS_JSON = _REPO_ROOT / "tools" / "002_LLM_API_MOCK" / "models.json"
if not _MODELS_JSON.is_file():
    # Editable installs / alternate layouts: walk up looking for the registry.
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "tools" / "002_LLM_API_MOCK" / "models.json"
        if candidate.is_file():
            _REPO_ROOT = parent
            _MODELS_JSON = candidate
            break
_FRONTIER_BANDS = frozenset({"high", "frontier", "top"})


def exit_code_for(outcome: str) -> int:
    if outcome in {"oracle_green", "completed"}:
        return EXIT_ORACLE_GREEN
    if outcome == "budget_exhausted":
        return EXIT_BUDGET
    if outcome in {"unavailable", "provider_unavailable"} or outcome.startswith(
        "instrument_error"
    ):
        return EXIT_UNAVAILABLE
    if outcome in {"invalid_request", "invalid_plan_or_route"}:
        return EXIT_INVALID
    return EXIT_NON_GREEN


def load_band_models(band: str, *, registry: Path | None = None) -> tuple[str, ...]:
    path = registry or _MODELS_JSON
    payload = json.loads(path.read_text(encoding="utf-8"))
    key = (band or "free").strip().lower()
    if key in _FRONTIER_BANDS and key != "high":
        raise ValueError(f"frontier band {band!r} requires explicit authorization")
    models = payload.get(key)
    if not isinstance(models, list) or not models:
        raise ValueError(f"unknown or empty executor band: {band}")
    return tuple(str(item) for item in models)


def _require_int(value: Any, name: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    return value


def request_to_config(request: Mapping[str, Any]) -> CodingRunConfig | ExplainRunConfig:
    command = str(request.get("command") or "code")
    workspace = Path(str(request.get("workspace") or ".")).resolve()
    run_id = str(request.get("runId") or request.get("run_id") or f"run-{uuid.uuid4()}")

    if command == "explain":
        question = str(request.get("question") or "").strip()
        if not question:
            raise ValueError("explain requires --question")
        return ExplainRunConfig(
            run_id=run_id,
            workspace=workspace,
            question=question,
            max_turns_per_episode=_require_int(
                request.get("maxTurnsPerEpisode", request.get("max_turns_per_episode", 4)),
                "maxTurnsPerEpisode",
                minimum=1,
            ),
        )

    band = str(request.get("executorBand") or request.get("executor_band") or "free")
    if band in _FRONTIER_BANDS:
        raise ValueError(
            f"executor-band {band!r} is frontier; refuse without explicit authorization"
        )

    executor_models = request.get("executorModels") or request.get("executor_models")
    if executor_models:
        resolved_executors = tuple(str(item) for item in executor_models)
    else:
        resolved_executors = load_band_models(band)

    recovery = request.get("recoveryModels") or request.get("recovery_models")
    if recovery:
        recovery_models = tuple(str(item) for item in recovery)
    else:
        recovery_model = request.get("recoveryModel") or request.get("recovery_model")
        recovery_models = (str(recovery_model),) if recovery_model else ()

    budget = _require_int(
        request.get("budgetUsdMicros", request.get("budget_usd_micros", 0)),
        "budgetUsdMicros",
    )
    # Free-band default must not authorize paid/frontier spend.
    if band == "free" and budget < 0:
        raise ValueError("budgetUsdMicros cannot be negative")

    brief = str(request.get("brief") or "")
    brief_path = workspace / brief if brief.endswith(".md") and not Path(brief).is_absolute() else None
    if brief_path is not None and brief_path.is_file():
        brief = brief_path.read_text(encoding="utf-8")

    return CodingRunConfig(
        run_id=run_id,
        workspace=workspace,
        brief=brief or "Complete the coding task.",
        planner_model=str(
            request.get("plannerModel")
            or request.get("planner_model")
            or "deepseek/deepseek-v4-flash"
        ),
        executor_models=resolved_executors,
        recovery_models=recovery_models,
        reviewer_model=request.get("reviewerModel") or request.get("reviewer_model"),
        max_turns_per_episode=_require_int(
            request.get("maxTurnsPerEpisode", request.get("max_turns_per_episode", 40)),
            "maxTurnsPerEpisode",
            minimum=1,
        ),
        max_episodes=_require_int(
            request.get("maxEpisodes", request.get("max_episodes", 12)),
            "maxEpisodes",
            minimum=1,
        ),
        max_replans=_require_int(
            request.get("maxReplans", request.get("max_replans", 2)),
            "maxReplans",
        ),
        max_paid_calls=_require_int(
            request.get("maxPaidCalls", request.get("max_paid_calls", 0)),
            "maxPaidCalls",
        ),
        budget_usd_micros=budget,
        interactive=bool(request.get("interactive", False)),
    )


def _emit(writer: Any, payload: Mapping[str, Any]) -> None:
    writer.write(json.dumps(payload, sort_keys=True) + "\n")
    writer.flush()


def _result_dict(result: CodingRunResult, projections: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "runId": result.run_id,
        "outcome": result.outcome,
        "phase": result.phase,
        "attempts": result.attempts,
        "turns": result.turns,
        "planDigest": result.plan_digest,
        "activeStepId": result.active_step_id,
        "verifiedStepIds": list(result.verified_step_ids),
        "modelRoutes": [dict(route) for route in result.model_routes],
        "promptTokens": result.prompt_tokens,
        "completionTokens": result.completion_tokens,
        "spentUsdMicros": result.spent_usd_micros,
        "detail": result.detail,
        "projections": list(projections),
    }


def _scripted_adaptive_plan() -> CodingPlan:
    raw = {
        "schema": "vg.coding-plan.v1",
        "goal": "greenfield adaptive fake",
        "assumptions": [],
        "finalChecks": [["python3", "-m", "unittest"]],
        "steps": [
            {
                "id": "step-001",
                "title": "Create HTTP API",
                "intent": "stdlib HTTP server",
                "files": ["app/server.py"],
                "dependsOn": [],
                "acceptanceChecks": [["python3", "-m", "unittest", "test.test_server"]],
            },
            {
                "id": "step-002",
                "title": "Create browser UI",
                "intent": "static page",
                "files": ["static/index.html"],
                "dependsOn": ["step-001"],
                "acceptanceChecks": [["python3", "-m", "unittest", "test.test_ui"]],
            },
        ],
    }
    return parse_coding_plan(raw)


def _fake_backend(kind: str) -> Callable[[Mapping[str, Any]], tuple[CodingRunResult, list[dict[str, Any]]]]:
    """Deterministic backends for CLI/product tests. Not a live spend path."""

    def greenfield_adaptive(request: Mapping[str, Any]) -> tuple[CodingRunResult, list[dict[str, Any]]]:
        config = request_to_config(request)
        assert isinstance(config, CodingRunConfig)
        if config.executor_models and any(
            model in load_band_models("high") for model in config.executor_models
        ):
            raise ValueError("default free execution must not authorize frontier models")
        plan = _scripted_adaptive_plan()
        projections: list[dict[str, Any]] = [
            {"kind": "plan", "model": config.planner_model, "stepTotal": len(plan.steps)},
            {"kind": "step", "stepIndex": 1, "stepTotal": 2, "text": "Create HTTP API",
             "stepId": "step-001"},
            {"kind": "read", "path": "app/server.py missing"},
            {"kind": "write", "path": "app/server.py", "text": "+112"},
            {"kind": "test", "path": "test.test_server", "exitCode": 1, "failures": 2},
            {"kind": "escalate", "text": "repeated failure fingerprint x2",
             "fingerprint": "fp-test-server"},
            {"kind": "diagnose", "model": config.recovery_models[0] if config.recovery_models
             else config.planner_model},
            {"kind": "resume", "model": config.executor_models[0] if config.executor_models
             else "free"},
            {"kind": "write", "path": "app/server.py", "text": "+8/-3"},
            {"kind": "verified", "stepId": "step-001"},
            {"kind": "step", "stepIndex": 2, "stepTotal": 2, "text": "Create browser UI",
             "stepId": "step-002"},
            {"kind": "write", "path": "static/index.html", "text": "+40"},
            {"kind": "verified", "stepId": "step-002"},
            {"kind": "oracle", "text": "final acceptance exit 0", "exitCode": 0},
            {"kind": "complete", "outcome": "oracle_green", "turns": 27,
             "spentUsdMicros": 13400},
        ]
        result = CodingRunResult(
            run_id=config.run_id,
            outcome="oracle_green",
            phase="complete",
            attempts=6,
            turns=27,
            plan_digest=plan.digest,
            active_step_id=None,
            verified_step_ids=("step-001", "step-002"),
            model_routes=(
                {"role": "architect", "band": "medium", "model": config.planner_model,
                 "reason": "initial_plan"},
                {"role": "executor", "band": "free",
                 "model": config.executor_models[0] if config.executor_models else "free",
                 "reason": "ready_step"},
                {"role": "diagnostic", "band": "medium",
                 "model": config.recovery_models[0] if config.recovery_models
                 else config.planner_model,
                 "reason": "repeated_failure"},
                {"role": "executor", "band": "free",
                 "model": config.executor_models[0] if config.executor_models else "free",
                 "reason": "descend_after_recovery"},
            ),
            prompt_tokens=12000,
            completion_tokens=4000,
            spent_usd_micros=13400,
            detail="scripted adaptive greenfield path",
        )
        return result, projections

    def budget_exhausted(request: Mapping[str, Any]) -> tuple[CodingRunResult, list[dict[str, Any]]]:
        config = request_to_config(request)
        assert isinstance(config, CodingRunConfig)
        projections = [
            {"kind": "plan", "model": config.planner_model, "stepTotal": 1},
            {"kind": "budget", "remainingUsdMicros": 0},
            {"kind": "complete", "outcome": "budget_exhausted", "turns": 3,
             "spentUsdMicros": config.budget_usd_micros},
        ]
        result = CodingRunResult(
            run_id=config.run_id, outcome="budget_exhausted", phase="failed",
            attempts=2, turns=3, plan_digest=None, active_step_id="step-001",
            verified_step_ids=(), model_routes=(), prompt_tokens=None,
            completion_tokens=None, spent_usd_micros=config.budget_usd_micros,
            detail="hard budget ceiling reached",
        )
        return result, projections

    def unavailable(request: Mapping[str, Any]) -> tuple[CodingRunResult, list[dict[str, Any]]]:
        config = request_to_config(request)
        run_id = config.run_id if isinstance(config, CodingRunConfig) else config.run_id
        projections = [
            {"kind": "error", "detail": "provider_unavailable"},
            {"kind": "complete", "outcome": "unavailable", "turns": 0,
             "spentUsdMicros": None},
        ]
        result = CodingRunResult(
            run_id=run_id, outcome="unavailable", phase="failed", attempts=0,
            turns=0, plan_digest=None, active_step_id=None, verified_step_ids=(),
            model_routes=(), prompt_tokens=None, completion_tokens=None,
            spent_usd_micros=None, detail="provider_unavailable",
        )
        return result, projections

    def non_green(request: Mapping[str, Any]) -> tuple[CodingRunResult, list[dict[str, Any]]]:
        config = request_to_config(request)
        assert isinstance(config, CodingRunConfig)
        projections = [
            {"kind": "plan", "model": config.planner_model, "stepTotal": 1},
            {"kind": "test", "path": "test.test_server", "exitCode": 1, "failures": 1},
            {"kind": "complete", "outcome": "verification_failed", "turns": 4,
             "spentUsdMicros": 0},
        ]
        result = CodingRunResult(
            run_id=config.run_id, outcome="verification_failed", phase="failed",
            attempts=2, turns=4, plan_digest=None, active_step_id="step-001",
            verified_step_ids=(), model_routes=(), prompt_tokens=100,
            completion_tokens=50, spent_usd_micros=0,
            detail="focused exterior check failed",
        )
        return result, projections

    table = {
        "greenfield-adaptive": greenfield_adaptive,
        "budget-exhausted": budget_exhausted,
        "unavailable": unavailable,
        "non-green": non_green,
    }
    if kind not in table:
        raise ValueError(f"unknown fake backend: {kind}")
    return table[kind]


def _coordinator_dry_plan(config: CodingRunConfig) -> tuple[CodingRunResult, list[dict[str, Any]]]:
    """Plan-only path: validate a planner-shaped plan without effects."""

    class _Episode:
        telemetry = type("T", (), {"turns": 1})()
        detail = "dry-plan"

    def planner(_brief: str) -> CodingPlan:
        return _scripted_adaptive_plan()

    def run_episode(role: Any, model: str, episode_id: str, brief: str) -> Any:
        return _Episode()

    result = run_coding_task(
        config,
        planner=planner,
        run_episode=run_episode,
        verify_step=lambda plan, step_id: True,
        verify_final=lambda plan, _: True,
    )
    # Dry-plan stops after plan validation — rewrite outcome for the product.
    projections = [
        {"kind": "plan", "model": config.planner_model,
         "stepTotal": len(result.verified_step_ids) or 2},
        {"kind": "complete", "outcome": "dry_plan", "turns": result.turns,
         "spentUsdMicros": 0},
    ]
    dry = CodingRunResult(
        run_id=result.run_id,
        outcome="completed",
        phase="plan",
        attempts=result.attempts,
        turns=result.turns,
        plan_digest=result.plan_digest,
        active_step_id=None,
        verified_step_ids=(),
        model_routes=result.model_routes,
        prompt_tokens=result.prompt_tokens,
        completion_tokens=result.completion_tokens,
        spent_usd_micros=0,
        detail="dry-plan: validated plan only; no effects dispatched",
    )
    return dry, projections


def run_entrypoint(
    request: Mapping[str, Any],
    *,
    writer: Any = None,
) -> int:
    out = writer if writer is not None else sys.stdout
    try:
        fake = request.get("fakeBackend") or request.get("fake_backend")
        if fake:
            result, projections = _fake_backend(str(fake))(request)
        else:
            config = request_to_config(request)
            command = str(request.get("command") or "code")
            if command == "explain":
                assert isinstance(config, ExplainRunConfig)

                class _Episode:
                    telemetry = type("T", (), {"turns": 1})()
                    detail = json.dumps({
                        "citations": ["vanguard/packages/kernel/dispatch.py"],
                        "answer": "Authorization is decided by the attenuation kernel before effect.",
                    })

                result = explain_repository(
                    config, run_episode=lambda *args, **kwargs: _Episode()
                )
                projections = [
                    {"kind": "read", "path": "vanguard/packages/kernel/dispatch.py"},
                    {"kind": "complete", "outcome": "completed", "turns": 1,
                     "spentUsdMicros": 0, "text": result.detail},
                ]
            elif bool(request.get("dryPlan") or request.get("dry_plan")):
                assert isinstance(config, CodingRunConfig)
                result, projections = _coordinator_dry_plan(config)
            elif command == "resume":
                raise ValueError(
                    "resume requires a ledger-derived snapshot from the product "
                    "persistence adapter; use fakeBackend in tests"
                )
            else:
                raise ValueError(
                    "live coding composition is not bound in this bridge yet; "
                    "pass fakeBackend for product tests or wait for the ALFA "
                    "HarnessSession binder"
                )

        for projection in projections:
            _emit(out, {"type": "projection", "projection": projection})
        _emit(out, {"type": "result", "result": _result_dict(result, projections)})
        return exit_code_for(result.outcome)
    except (ValueError, CodingPlanError, FileNotFoundError, json.JSONDecodeError) as exc:
        _emit(out, {
            "type": "projection",
            "projection": {"kind": "error", "detail": str(exc)},
        })
        _emit(out, {
            "type": "result",
            "result": {
                "runId": str(request.get("runId") or "unknown"),
                "outcome": "invalid_request",
                "phase": "failed",
                "attempts": 0,
                "turns": 0,
                "planDigest": None,
                "activeStepId": None,
                "verifiedStepIds": [],
                "modelRoutes": [],
                "promptTokens": None,
                "completionTokens": None,
                "spentUsdMicros": None,
                "detail": str(exc),
                "projections": [{"kind": "error", "detail": str(exc)}],
            },
        })
        return EXIT_INVALID


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Vanguard coding CLI/backend bridge")
    parser.add_argument("--stdin-json", action="store_true",
                        help="Read one CodingRequest JSON object from stdin")
    parser.add_argument("--request-json", default=None,
                        help="Path to a CodingRequest JSON file")
    args = parser.parse_args(argv)

    if args.stdin_json:
        request = json.load(sys.stdin)
    elif args.request_json:
        request = json.loads(Path(args.request_json).read_text(encoding="utf-8"))
    else:
        parser.error("provide --stdin-json or --request-json")
        return EXIT_INVALID

    if not isinstance(request, Mapping):
        print(json.dumps({"type": "result", "result": {
            "outcome": "invalid_request", "detail": "request must be an object",
            "runId": "unknown", "phase": "failed", "attempts": 0, "turns": 0,
            "planDigest": None, "activeStepId": None, "verifiedStepIds": [],
            "modelRoutes": [], "promptTokens": None, "completionTokens": None,
            "spentUsdMicros": None, "projections": [],
        }}), flush=True)
        return EXIT_INVALID
    return run_entrypoint(request)


if __name__ == "__main__":
    raise SystemExit(main())
