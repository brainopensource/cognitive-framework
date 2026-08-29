"""Modular Staged Workflow Engine and Execution Nodes.

Implements the 4-stage Agentless paradigm (Localization -> Planning -> Patching -> Verification)
over Vanguard's hexagonal runtime, enabling pluggable workflow modes and node selectors.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ..domain.transforms.repository.change_surface import ChangeSurfaceEstimate, ChangeSurfaceEstimator
from ..domain.workflows.contracts import WorkflowNode, WorkflowSpec


@dataclass(frozen=True, slots=True)
class WorkflowStageResult:
    """Outcome from a single workflow stage node."""

    stage_id: str
    status: str
    outputs: Mapping[str, Any] = field(default_factory=dict)
    diagnostics: tuple[str, ...] = ()


class WorkflowNodeRunner:
    """Base class for pluggable workflow execution nodes."""

    node_kind: str = "generic"

    def execute(self, workspace: Path, context: Mapping[str, Any]) -> WorkflowStageResult:
        raise NotImplementedError


class LocalizationNodeRunner(WorkflowNodeRunner):
    """Stage 1: Codebase localization and file inspection node."""

    node_kind = "localization"

    def execute(self, workspace: Path, context: Mapping[str, Any]) -> WorkflowStageResult:
        brief = str(context.get("brief") or "")
        files = [p.relative_to(workspace).as_posix() for p in workspace.rglob("*") if p.is_file()]
        estimator = ChangeSurfaceEstimator()
        estimate = estimator.estimate(brief, workspace_files=files)

        return WorkflowStageResult(
            stage_id="localization",
            status="completed",
            outputs={
                "primary_files": list(estimate.primary_files),
                "related_files": list(estimate.related_files),
                "test_files": list(estimate.test_files),
            },
            diagnostics=(f"Localized {len(estimate.primary_files)} primary target files",),
        )


class PlanningNodeRunner(WorkflowNodeRunner):
    """Stage 2: Multi-file dependency planning and surface estimation node."""

    node_kind = "planning"

    def execute(self, workspace: Path, context: Mapping[str, Any]) -> WorkflowStageResult:
        primary_files = context.get("primary_files") or []
        related_files = context.get("related_files") or []

        all_targets = sorted(set(primary_files) | set(related_files))
        return WorkflowStageResult(
            stage_id="planning",
            status="completed",
            outputs={"target_surface": all_targets},
            diagnostics=(f"Planned change surface across {len(all_targets)} files",),
        )


class VerificationNodeRunner(WorkflowNodeRunner):
    """Stage 4: Verification and test suite assertion gate node."""

    node_kind = "verification"

    def __init__(self, test_runner: Callable[[Path], bool] | None = None) -> None:
        self.test_runner = test_runner

    def execute(self, workspace: Path, context: Mapping[str, Any]) -> WorkflowStageResult:
        if self.test_runner:
            passed = self.test_runner(workspace)
            status = "passed" if passed else "failed"
        else:
            status = "unverified"

        return WorkflowStageResult(
            stage_id="verification",
            status=status,
            outputs={"verified": status == "passed"},
            diagnostics=(f"Verification gate status: {status}",),
        )


class StagedWorkflowEngine:
    """Orchestrates pluggable staged execution nodes over task workspaces."""

    def __init__(
        self,
        nodes: Sequence[WorkflowNodeRunner] | None = None,
        mode: str = "auto",
    ) -> None:
        self.mode = mode
        self.nodes = tuple(nodes) if nodes is not None else (
            LocalizationNodeRunner(),
            PlanningNodeRunner(),
            VerificationNodeRunner(),
        )

    def run_workflow(
        self,
        workspace: Path,
        brief: str,
        *,
        test_callback: Callable[[Path], bool] | None = None,
    ) -> dict[str, Any]:
        context: dict[str, Any] = {"brief": brief}
        stage_results: list[dict[str, Any]] = []

        for node in self.nodes:
            if isinstance(node, VerificationNodeRunner) and test_callback:
                node.test_runner = test_callback

            res = node.execute(workspace, context)
            context.update(res.outputs)
            stage_results.append({
                "stage": res.stage_id,
                "status": res.status,
                "diagnostics": list(res.diagnostics),
            })

        return {
            "mode": self.mode,
            "context": context,
            "stages": stage_results,
        }
