"""Public facade exposing the vg-1-forge preset and unified run interfaces."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

from ...ports.model import ModelPort
from .compiler import ForgeContextCompiler
from .engine import (
    ForgeAdmissionGate,
    ForgeEngine,
    ForgeOutcome,
    GoalContract,
    VerificationReceipt,
)
from .patcher import ForgeAtomicPatcher

FORGE_PRESET_NAME = "vg-1-forge"


@dataclass(frozen=True, slots=True)
class ForgeConfig:
    """Configuration for the 1-Forge reflexive agent."""

    max_turns: int = 8
    token_ceiling: int = 64_000
    budget_limit_usd: float = 0.20
    require_patch_for_write: bool = True
    model_name: str | None = None
    preset_name: str = FORGE_PRESET_NAME


class ForgeFacade:
    """Unified public facade for 1-Forge (Reflexive Agentic Micro-Forge)."""

    @classmethod
    def create_engine(
        cls,
        workspace_root: Path | str,
        model_port: Any,
        config: ForgeConfig | None = None,
        sandbox_runner: Any = None,
        command_runner: Any = None,
    ) -> ForgeEngine:
        """Create and configure a ForgeEngine instance."""
        cfg = config or ForgeConfig()
        compiler = ForgeContextCompiler(token_ceiling=cfg.token_ceiling)
        patcher = ForgeAtomicPatcher(workspace_root=workspace_root)
        admission_gate = ForgeAdmissionGate(require_patch_for_write=cfg.require_patch_for_write)

        return ForgeEngine(
            workspace_root=workspace_root,
            model_port=model_port,
            compiler=compiler,
            patcher=patcher,
            admission_gate=admission_gate,
            sandbox_runner=sandbox_runner,
            command_runner=command_runner,
            max_turns=cfg.max_turns,
            token_ceiling=cfg.token_ceiling,
            budget_limit_usd=cfg.budget_limit_usd,
        )

    @classmethod
    def run_task(
        cls,
        workspace_root: Path | str,
        task_brief: str,
        model_port: Any,
        config: ForgeConfig | None = None,
        goal_contract: GoalContract | None = None,
        sandbox_runner: Any = None,
        command_runner: Any = None,
    ) -> ForgeOutcome:
        """Execute a task using 1-Forge."""
        engine = cls.create_engine(
            workspace_root,
            model_port,
            config=config,
            sandbox_runner=sandbox_runner,
            command_runner=command_runner,
        )
        return engine.run_episode(task_brief=task_brief, goal_contract=goal_contract)
