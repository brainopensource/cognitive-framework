"""Application workflow for a Vanguard coding run (`REQ-TRUST-001`).

This module deliberately schedules episodes through an injected runner.  It
does not know how to dispatch effects, invoke a sandbox, or grade a model:
those responsibilities remain in ``HarnessSession`` and the exterior verifier.
The seam keeps unit tests deterministic and lets the product entrypoint bind
the real session without a second effect loop.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Mapping

from .coding_plan import CodingPlan, CodingPlanError, StepStatus, ready_steps, transition_step
from ...runtime.tier_escalation import ModelRole, RouteDecision, RoleAwareRouter

__all__ = [
    "CodingPhase", "CodingRunConfig", "CodingRunCoordinator", "CodingRunResult",
    "CodingRunSnapshot", "ExplainRunConfig", "explain_repository", "resume_coding_task",
    "run_coding_task",
]


class CodingPhase(str, Enum):
    DISCOVER = "discover"
    PLAN = "plan"
    EXECUTE = "execute"
    VERIFY = "verify"
    DIAGNOSE = "diagnose"
    REPLAN = "replan"
    REVIEW = "review"
    FINAL_VERIFY = "final_verify"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class CodingRunConfig:
    run_id: str
    workspace: Path
    brief: str
    planner_model: str = "deepseek/deepseek-v4-flash"
    executor_models: tuple[str, ...] = ()
    recovery_models: tuple[str, ...] = ("deepseek/deepseek-v4-flash",)
    reviewer_model: str | None = None
    max_turns_per_episode: int = 8
    max_episodes: int = 12
    max_replans: int = 2
    max_paid_calls: int = 0
    budget_usd_micros: int = 0
    interactive: bool = False


@dataclass(frozen=True, slots=True)
class ExplainRunConfig:
    run_id: str
    workspace: Path
    question: str
    max_turns_per_episode: int = 4


@dataclass(frozen=True, slots=True)
class CodingRunResult:
    run_id: str
    outcome: str
    phase: str
    attempts: int
    turns: int
    plan_digest: str | None
    active_step_id: str | None
    verified_step_ids: tuple[str, ...]
    model_routes: tuple[Mapping[str, object], ...]
    prompt_tokens: int | None
    completion_tokens: int | None
    spent_usd_micros: int | None
    detail: str


@dataclass(frozen=True, slots=True)
class CodingRunSnapshot:
    """Serializable coordinator state; callers persist it in ledger evidence."""

    run_id: str
    workspace: str
    workspace_digest: str | None
    plan: CodingPlan
    phase: CodingPhase
    active_step_id: str | None
    attempts: int
    routes: tuple[Mapping[str, object], ...]


EpisodeRunner = Callable[[ModelRole, str, str, str], Any]
PlanFactory = Callable[[str], CodingPlan]
Verifier = Callable[[CodingPlan, str | None], bool]


class CodingRunCoordinator:
    """Finite workflow around canonical episodes and exterior verification."""

    def __init__(self, config: CodingRunConfig, *, planner: PlanFactory,
                 run_episode: EpisodeRunner, verify_step: Verifier,
                 verify_final: Verifier, router: RoleAwareRouter | None = None,
                 workspace_digest: Callable[[Path], str] | None = None) -> None:
        self.config = config
        self._planner = planner
        self._run_episode = run_episode
        self._verify_step = verify_step
        self._verify_final = verify_final
        self._router = router
        self._workspace_digest = workspace_digest
        self.phase = CodingPhase.DISCOVER
        self.plan: CodingPlan | None = None
        self.active_step_id: str | None = None
        self.attempts = 0
        self.turns = 0
        self.routes: list[Mapping[str, object]] = []

    def _episode_id(self) -> str:
        return f"{self.config.run_id}-episode-{self.attempts + 1}"

    def _route(self, role: ModelRole, reason: str) -> RouteDecision | None:
        if self._router is None:
            return None
        decision = self._router.choose(
            role, episode_id=self._episode_id(), reason=reason,
            healthy_free_models=self.config.executor_models,
            allow_paid=self.config.max_paid_calls > 0 and self.config.budget_usd_micros > 0,
        )
        self.routes.append(decision.to_dict())
        return decision

    def _run(self, role: ModelRole, brief: str, reason: str) -> Any:
        if self.attempts >= self.config.max_episodes:
            raise RuntimeError("episodes_exhausted")
        decision = self._route(role, reason)
        model = decision.resolved_model if decision is not None else "configured"
        episode_id = self._episode_id()
        self.attempts += 1
        result = self._run_episode(role, model, episode_id, brief)
        telemetry = getattr(result, "telemetry", None)
        self.turns += int(getattr(telemetry, "turns", 0) or 0)
        return result

    def run(self) -> CodingRunResult:
        try:
            if self.plan is None:
                self.phase = CodingPhase.PLAN
                self._run(ModelRole.ARCHITECT, self.config.brief, "initial_plan")
                self.plan = self._planner(self.config.brief)
                # The planner callback supplies an already parsed, validated plan.
                if not self.plan.steps:
                    raise CodingPlanError("planner returned no steps")
                for step in ready_steps(self.plan):
                    self.plan = transition_step(self.plan, step.step_id, StepStatus.READY)

            # A crash after implementation but before a durable verification
            # receipt must not invent success. Re-run that exterior check on
            # resume, then continue only from its fresh result.
            if self.phase is CodingPhase.VERIFY and self.active_step_id is not None:
                interrupted = self.plan.step(self.active_step_id)
                if interrupted.status is StepStatus.IMPLEMENTED:
                    if not self._verify_step(self.plan, interrupted.step_id):
                        return self._result("verification_failed", "resumed exterior check failed")
                    self.plan = transition_step(
                        self.plan, interrupted.step_id, StepStatus.VERIFIED,
                        exterior_verified=True)

            while True:
                if self.plan is None:
                    raise CodingPlanError("plan missing")
                candidates = ready_steps(self.plan)
                if not candidates:
                    break
                step = candidates[0]
                if step.status is StepStatus.PENDING:
                    self.plan = transition_step(self.plan, step.step_id, StepStatus.READY)
                self.active_step_id = step.step_id
                self.plan = transition_step(self.plan, step.step_id, StepStatus.IN_PROGRESS)
                self.phase = CodingPhase.EXECUTE
                self._run(ModelRole.EXECUTOR, self._executor_brief(step), "ready_step")
                self.plan = transition_step(self.plan, step.step_id, StepStatus.IMPLEMENTED)
                self.phase = CodingPhase.VERIFY
                if not self._verify_step(self.plan, step.step_id):
                    return self._result("verification_failed", "focused exterior check failed")
                self.plan = transition_step(self.plan, step.step_id, StepStatus.VERIFIED,
                                            exterior_verified=True)

            if self.plan is None or any(step.status is not StepStatus.VERIFIED
                                        for step in self.plan.steps):
                return self._result("plan_deadlock", "no dependency-ready required step")
            self.phase = CodingPhase.REVIEW
            self._run(ModelRole.REVIEWER, "Review the completed plan against the brief.", "review")
            self.phase = CodingPhase.FINAL_VERIFY
            if not self._verify_final(self.plan, None):
                return self._result("oracle_failed", "final exterior oracle failed")
            self.phase = CodingPhase.COMPLETE
            return self._result("oracle_green", "all required steps and final oracle passed")
        except (CodingPlanError, ValueError) as exc:
            self.phase = CodingPhase.FAILED
            return self._result("invalid_plan_or_route", str(exc))
        except RuntimeError as exc:
            self.phase = CodingPhase.FAILED
            return self._result(str(exc), str(exc))

    def _executor_brief(self, step: Any) -> str:
        files = ", ".join(step.files) if step.files else "no predeclared file"
        return (f"Current plan step: {step.step_id} — {step.title}\n"
                f"Intent: {step.intent}\nAllowed files: {files}\n"
                "Propose exactly one Vanguard effect. The runtime, not you, verifies completion.")

    def snapshot(self) -> CodingRunSnapshot:
        if self.plan is None:
            raise RuntimeError("cannot snapshot before a plan exists")
        digest = self._workspace_digest(self.config.workspace) if self._workspace_digest else None
        return CodingRunSnapshot(self.config.run_id, str(self.config.workspace), digest,
                                 self.plan, self.phase, self.active_step_id,
                                 self.attempts, tuple(self.routes))

    def _result(self, outcome: str, detail: str) -> CodingRunResult:
        plan = self.plan
        verified = tuple(step.step_id for step in plan.steps
                         if step.status is StepStatus.VERIFIED) if plan else ()
        return CodingRunResult(
            run_id=self.config.run_id, outcome=outcome, phase=self.phase.value,
            attempts=self.attempts, turns=self.turns,
            plan_digest=plan.digest if plan else None,
            active_step_id=self.active_step_id, verified_step_ids=verified,
            model_routes=tuple(self.routes), prompt_tokens=None,
            completion_tokens=None, spent_usd_micros=None, detail=detail)


def run_coding_task(config: CodingRunConfig, **dependencies: Any) -> CodingRunResult:
    return CodingRunCoordinator(config, **dependencies).run()


def resume_coding_task(run_id: str, *, workspace: Path, snapshot: CodingRunSnapshot,
                       **dependencies: Any) -> CodingRunResult:
    """Resume only an explicitly supplied ledger-derived snapshot.

    The product persistence adapter supplies the snapshot; this module never
    invents a completion merely because a file survived an interruption.
    """
    if snapshot.run_id != run_id or Path(snapshot.workspace) != workspace:
        raise ValueError("resume identity does not match the supplied snapshot")
    digest_fn = dependencies.get("workspace_digest")
    if snapshot.workspace_digest is not None and digest_fn is not None:
        if digest_fn(workspace) != snapshot.workspace_digest:
            raise ValueError("workspace identity changed since the run snapshot")
    config = dependencies.pop("config")
    coordinator = CodingRunCoordinator(config, **dependencies)
    coordinator.plan = snapshot.plan
    coordinator.phase = snapshot.phase
    coordinator.active_step_id = snapshot.active_step_id
    coordinator.attempts = snapshot.attempts
    coordinator.routes = list(snapshot.routes)
    return coordinator.run()


def explain_repository(config: ExplainRunConfig, *, run_episode: EpisodeRunner) -> CodingRunResult:
    """Read-only explanation uses the same episode runner, not a raw model call."""
    result = run_episode(ModelRole.EXECUTOR, "read-only", f"{config.run_id}-episode-1",
                         "Explain the repository using observed paths and symbols only: " + config.question)
    telemetry = getattr(result, "telemetry", None)
    return CodingRunResult(config.run_id, "completed", CodingPhase.COMPLETE.value, 1,
                           int(getattr(telemetry, "turns", 0) or 0), None, None, (), (),
                           None, None, None, getattr(result, "detail", ""))
