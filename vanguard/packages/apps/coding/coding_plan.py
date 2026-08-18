"""Validated, runtime-owned plans for coding runs (`REQ-TRUST-001`).

The plan is deliberately an application value, not a model assertion.  A
model can propose an ``implemented`` step, but only an exterior verifier may
move it to ``verified``.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from enum import Enum
from pathlib import PurePosixPath
from typing import Any, Mapping, Sequence

__all__ = [
    "CodingPlan", "CodingPlanError", "CodingPlanStep", "StepStatus",
    "parse_coding_plan", "ready_steps", "transition_step", "validate_plan",
]


class CodingPlanError(ValueError):
    """A model-proposed plan that cannot safely become run state."""


class StepStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    BLOCKED = "blocked"
    SUPERSEDED = "superseded"


_INITIAL = frozenset({StepStatus.PENDING, StepStatus.READY})
_TRANSITIONS = {
    StepStatus.PENDING: frozenset({StepStatus.READY, StepStatus.SUPERSEDED}),
    StepStatus.READY: frozenset({StepStatus.IN_PROGRESS, StepStatus.SUPERSEDED}),
    StepStatus.IN_PROGRESS: frozenset({StepStatus.IMPLEMENTED, StepStatus.BLOCKED,
                                       StepStatus.SUPERSEDED}),
    StepStatus.IMPLEMENTED: frozenset({StepStatus.VERIFIED, StepStatus.BLOCKED,
                                       StepStatus.IN_PROGRESS, StepStatus.SUPERSEDED}),
    StepStatus.BLOCKED: frozenset({StepStatus.READY, StepStatus.SUPERSEDED}),
    StepStatus.VERIFIED: frozenset(),
    StepStatus.SUPERSEDED: frozenset(),
}


@dataclass(frozen=True, slots=True)
class CodingPlanStep:
    step_id: str
    title: str
    depends_on: tuple[str, ...]
    files: tuple[str, ...]
    intent: str
    acceptance_checks: tuple[tuple[str, ...], ...]
    risk: str = "low"
    status: StepStatus = StepStatus.PENDING

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.step_id, "title": self.title,
            "dependsOn": list(self.depends_on), "files": list(self.files),
            "intent": self.intent,
            "acceptanceChecks": [list(check) for check in self.acceptance_checks],
            "risk": self.risk, "status": self.status.value,
        }


@dataclass(frozen=True, slots=True)
class CodingPlan:
    goal: str
    assumptions: tuple[str, ...]
    steps: tuple[CodingPlanStep, ...]
    final_checks: tuple[tuple[str, ...], ...]
    schema: str = "vg.coding-plan.v1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema, "goal": self.goal,
            "assumptions": list(self.assumptions),
            "steps": [step.to_dict() for step in self.steps],
            "finalChecks": [list(check) for check in self.final_checks],
        }

    @property
    def digest(self) -> str:
        raw = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def step(self, step_id: str) -> CodingPlanStep:
        for step in self.steps:
            if step.step_id == step_id:
                return step
        raise CodingPlanError(f"unknown plan step: {step_id}")


def _strings(value: Any, name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise CodingPlanError(f"{name} must be a list of non-empty strings")
    return tuple(value)


def _checks(value: Any, name: str) -> tuple[tuple[str, ...], ...]:
    if not isinstance(value, list) or not value:
        raise CodingPlanError(f"{name} must contain at least one command")
    checks: list[tuple[str, ...]] = []
    for command in value:
        if not isinstance(command, list) or not command or not all(
                isinstance(token, str) and token for token in command):
            raise CodingPlanError(f"{name} commands must be non-empty string lists")
        checks.append(tuple(command))
    return tuple(checks)


def parse_coding_plan(raw: Mapping[str, Any]) -> CodingPlan:
    """Parse untrusted model JSON; validation remains a separate explicit step."""
    if raw.get("schema") != "vg.coding-plan.v1":
        raise CodingPlanError("plan schema must be 'vg.coding-plan.v1'")
    goal = raw.get("goal")
    if not isinstance(goal, str) or not goal.strip():
        raise CodingPlanError("plan goal must be a non-empty string")
    raw_steps = raw.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise CodingPlanError("plan requires at least one step")
    steps: list[CodingPlanStep] = []
    for raw_step in raw_steps:
        if not isinstance(raw_step, Mapping):
            raise CodingPlanError("plan steps must be objects")
        identifier = raw_step.get("id")
        title = raw_step.get("title")
        intent = raw_step.get("intent")
        if not all(isinstance(item, str) and item.strip()
                   for item in (identifier, title, intent)):
            raise CodingPlanError("every step needs id, title, and intent")
        try:
            status = StepStatus(raw_step.get("status", StepStatus.PENDING.value))
        except ValueError as exc:
            raise CodingPlanError(f"unknown step status for {identifier!r}") from exc
        steps.append(CodingPlanStep(
            step_id=identifier, title=title,
            depends_on=_strings(raw_step.get("dependsOn", []), "dependsOn"),
            files=_strings(raw_step.get("files", []), "files"), intent=intent,
            acceptance_checks=_checks(raw_step.get("acceptanceChecks"), "acceptanceChecks"),
            risk=str(raw_step.get("risk", "low")), status=status,
        ))
    assumptions = raw.get("assumptions", [])
    if not isinstance(assumptions, list) or not all(isinstance(item, str) for item in assumptions):
        raise CodingPlanError("assumptions must be strings")
    return CodingPlan(goal=goal, assumptions=tuple(assumptions), steps=tuple(steps),
                      final_checks=_checks(raw.get("finalChecks"), "finalChecks"))


def _relative(path: str) -> bool:
    candidate = PurePosixPath(path)
    return bool(path) and not candidate.is_absolute() and ".." not in candidate.parts


def validate_plan(plan: CodingPlan, *, allowed_command_prefixes: Sequence[Sequence[str]]) -> None:
    """Validate plan topology and authority before it influences a run."""
    if plan.schema != "vg.coding-plan.v1" or not plan.goal.strip():
        raise CodingPlanError("invalid coding plan header")
    ids = [step.step_id for step in plan.steps]
    if len(ids) != len(set(ids)):
        raise CodingPlanError("plan step ids must be unique")
    known = set(ids)
    prefixes = tuple(tuple(prefix) for prefix in allowed_command_prefixes)
    for step in plan.steps:
        if step.status not in _INITIAL:
            raise CodingPlanError("model-proposed initial status may only be pending or ready")
        if not set(step.depends_on) <= known:
            raise CodingPlanError(f"step {step.step_id} has an unknown dependency")
        if any(not _relative(path) for path in step.files):
            raise CodingPlanError(f"step {step.step_id} has a non-workspace path")
        for command in step.acceptance_checks:
            if not any(command[:len(prefix)] == prefix for prefix in prefixes):
                raise CodingPlanError(f"step {step.step_id} check is not allowlisted")
    for command in plan.final_checks:
        if not any(command[:len(prefix)] == prefix for prefix in prefixes):
            raise CodingPlanError("final check is not allowlisted")
    visiting: set[str] = set()
    visited: set[str] = set()
    by_id = {step.step_id: step for step in plan.steps}

    def visit(identifier: str) -> None:
        if identifier in visiting:
            raise CodingPlanError("plan dependency graph contains a cycle")
        if identifier in visited:
            return
        visiting.add(identifier)
        for dependency in by_id[identifier].depends_on:
            visit(dependency)
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier in ids:
        visit(identifier)


def ready_steps(plan: CodingPlan) -> tuple[CodingPlanStep, ...]:
    """Return dependency-ready steps in declared, deterministic order."""
    states = {step.step_id: step.status for step in plan.steps}
    return tuple(step for step in plan.steps if step.status in {StepStatus.PENDING, StepStatus.READY}
                 and all(states[dependency] is StepStatus.VERIFIED
                         for dependency in step.depends_on))


def transition_step(plan: CodingPlan, step_id: str, target: StepStatus, *,
                    exterior_verified: bool = False) -> CodingPlan:
    """Apply a legal runtime transition; verification is exterior-only."""
    current = plan.step(step_id)
    if target is StepStatus.VERIFIED and not exterior_verified:
        raise CodingPlanError("only exterior verification may mark a step verified")
    if target not in _TRANSITIONS[current.status]:
        raise CodingPlanError(f"illegal transition {current.status.value}->{target.value}")
    if target is StepStatus.IN_PROGRESS and current.status is StepStatus.READY:
        if step_id not in {step.step_id for step in ready_steps(plan)}:
            raise CodingPlanError("step dependencies are not verified")
    return replace(plan, steps=tuple(
        replace(step, status=target) if step.step_id == step_id else step
        for step in plan.steps))
