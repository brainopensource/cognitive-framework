"""Deterministic scripted backends for CLI/product tests (`S050-C-01`).

Moved out of `vanguard/packages/runtime/coding_entrypoint.py`: a production
composition-layer module that could fabricate a whole run outcome from a
string is exactly the failure `REQ-TRUST-001` exists to prevent (this table
used to live there and never touched a model, kernel, or adapter).
`coding_entrypoint.run_entrypoint` reaches this module only behind an
explicit `VANGUARD_ALLOW_FAKE=1` opt-in, never by default.

Not a live spend path. Never imported by anything under `vanguard/`.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping

from vanguard.packages.runtime.coding_coordinator import (
    CodingRunConfig,
    CodingRunResult,
)
from vanguard.packages.runtime.coding_entrypoint import (
    _scripted_adaptive_plan,
    request_to_config,
)

__all__ = ["scripted_backend", "fake_backend"]


def scripted_backend(kind: str) -> Callable[[Mapping[str, Any]], tuple[CodingRunResult, list[dict[str, Any]]]]:
    """Deterministic backends for CLI/product tests. Not a live spend path."""

    def greenfield_adaptive(request: Mapping[str, Any]) -> tuple[CodingRunResult, list[dict[str, Any]]]:
        from vanguard.packages.runtime.coding_entrypoint import load_band_models

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


fake_backend = scripted_backend

