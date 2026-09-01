"""Public Facade exposing the vg-chimera-v1 / vg-code-chimera unified interface."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from ...ports.model import ModelPort
from ..forge.engine import GoalContract
from .compiler import ChimeraContextCompiler
from .engine import ChimeraEngine, ChimeraOutcome
from .governor import GovernorPolicy, MetaCognitiveGovernor
from .patcher import ChimeraAtomicPatcher
from .retrieval import RetrievalMarket
from .router import CognitiveRouter
from .skills import SkillRegistry


CHIMERA_PRESET_V1 = "vg-chimera-v1"
CHIMERA_PRESET_CODE = "vg-code-chimera"


@dataclass(frozen=True, slots=True)
class ChimeraConfig:
    """Configuration options for the Chimera Neuro-Symbolic Agent."""

    max_turns: int = 15
    token_ceiling: int = 64_000
    budget_limit_usd: float = 0.20
    require_patch_for_write: bool = True
    model_name: str | None = None
    preset_name: str = CHIMERA_PRESET_V1
    enable_branch_search: bool = True
    enable_symbolic_solving: bool = True


class ChimeraFacade:
    """Unified public facade for CHIMERA."""

    @classmethod
    def create_engine(
        cls,
        workspace_root: Path | str,
        model_port: Any,
        config: ChimeraConfig | None = None,
        sandbox_runner: Any = None,
        command_runner: Callable[[str, Path], Tuple[int, str]] | None = None,
    ) -> ChimeraEngine:
        """Construct and wire a full ChimeraEngine instance."""
        cfg = config or ChimeraConfig()
        compiler = ChimeraContextCompiler(token_ceiling=cfg.token_ceiling)
        patcher = ChimeraAtomicPatcher(workspace_root=workspace_root)
        governor_policy = GovernorPolicy(
            enable_branch_search=cfg.enable_branch_search,
            enable_symbolic_solving=cfg.enable_symbolic_solving,
        )
        governor = MetaCognitiveGovernor(policy=governor_policy)
        router = CognitiveRouter()
        retrieval_market = RetrievalMarket(workspace_root=workspace_root)

        return ChimeraEngine(
            workspace_root=workspace_root,
            model_port=model_port,
            compiler=compiler,
            patcher=patcher,
            governor=governor,
            router=router,
            retrieval_market=retrieval_market,
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
        config: ChimeraConfig | None = None,
        goal_contract: GoalContract | None = None,
        sandbox_runner: Any = None,
        command_runner: Callable[[str, Path], Tuple[int, str]] | None = None,
    ) -> ChimeraOutcome:
        """Run an autonomous episode using CHIMERA."""
        engine = cls.create_engine(
            workspace_root=workspace_root,
            model_port=model_port,
            config=config,
            sandbox_runner=sandbox_runner,
            command_runner=command_runner,
        )
        return engine.run_episode(task_brief=task_brief, goal_contract=goal_contract)
