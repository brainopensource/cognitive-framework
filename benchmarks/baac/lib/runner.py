"""BaaC Challenge Execution and Telemetry Orchestrator.

Implements:
1. Complete Scientific BaaC pipeline:
   verify_zero -> clean_cache -> materialize_scratch -> execute_harness -> run_external_oracle -> cleanup -> attribute.
2. Multi-Provider Execution:
   - `lam`: hermetic $0.00 sub-millisecond offline replay via LLM API Mock.
   - `live`: OpenRouter execution (Free, Cheap, Frontier SOTA) with strict pre-call budget checks.
   - `ollama`: Local open-weight models with $0.00 local execution.
3. Artifact recording (events, trajectory, telemetry, patch, metadata).
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple
import yaml

from vanguard.packages.runtime.root import (
    FORGE_PRESET_NAME,
    ForgeConfig,
    ForgeFacade,
    GoalContract,
    get_default_paid_model,
    get_pricing_usd_table,
    resolve_model,
)

from ..schema import ChallengeMetadata
from .budget import BudgetCapConfig, BudgetTracker, BudgetExceededError
from .cache import clean_scratch_directories, purge_bytecode_caches
from .eval_judge import evaluate_challenge
from .models import LAMModelPort, OllamaModelPort, OpenRouterModelPort, load_openrouter_api_key
from .oracle import OracleResult, run_external_oracle
from .report import ChallengeExecutionResult, classify_attribution
from .state import (
    clean_scratch_workspace,
    materialize_scratch_workspace,
    verify_challenge_zero_state,
)


ROOT = Path(__file__).resolve().parents[3]
BAAC_RUNS_DIR = ROOT / "benchmarks" / "baac" / "runs"


def compute_directory_diff(pristine_dir: Path, modified_dir: Path) -> str:
    """Compute unified diff between pristine challenge source and modified workspace."""
    diff_lines: List[str] = []
    pristine_files = {p.relative_to(pristine_dir): p for p in pristine_dir.rglob("*") if p.is_file() and not p.name.startswith(".")}
    modified_files = {p.relative_to(modified_dir): p for p in modified_dir.rglob("*") if p.is_file() and not p.name.startswith(".")}

    all_rel_paths = sorted(set(pristine_files.keys()) | set(modified_files.keys()))

    for rel in all_rel_paths:
        p_file = pristine_files.get(rel)
        m_file = modified_files.get(rel)

        p_text = p_file.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True) if p_file else []
        m_text = m_file.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True) if m_file else []

        if p_text != m_text:
            diff = difflib.unified_diff(
                p_text,
                m_text,
                fromfile=f"a/{rel}",
                tofile=f"b/{rel}",
            )
            diff_lines.extend(diff)

    return "".join(diff_lines)


class BaaCRunner:
    """Coordinates the BaaC execution cycle for one or more challenges."""

    def __init__(
        self,
        preset: str = "vg-1-forge",
        model_name: Optional[str] = None,
        mode: str = "lam",
        budget_config: Optional[BudgetCapConfig] = None,
        run_id: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.preset = preset
        self.mode = mode
        self.model_name = model_name or ("lam-mock" if mode == "lam" else "deepseek/deepseek-v4-flash-0731")
        self.budget_config = budget_config or BudgetCapConfig()
        self.run_id = run_id or f"baac-run-{int(time.time())}"
        self.extra_metadata = extra_metadata or {}
        # One tracker spans the whole campaign, not one tracker per challenge.
        # This makes the $0.10/1M-token/500-call ceiling cumulative.
        self.campaign_budget = BudgetTracker(self.budget_config)
        self.api_key = load_openrouter_api_key() if mode == "live" else ""
        self.run_dir = BAAC_RUNS_DIR / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def load_challenge_metadata(self, challenge_dir: Path) -> ChallengeMetadata:
        """Parse challenge.yaml or construct default metadata."""
        yaml_file = challenge_dir / "challenge.yaml"
        if yaml_file.is_file():
            try:
                raw = yaml.safe_load(yaml_file.read_text(encoding="utf-8")) or {}
                return ChallengeMetadata.from_dict(raw)
            except Exception:
                pass

        # Fallback default inferred from path
        cid = challenge_dir.name
        tier_name = challenge_dir.parent.name if "tier-" in challenge_dir.parent.name else "tier-1"
        return ChallengeMetadata(
            id=cid,
            name=cid.replace("_", " ").title(),
            scope="single" if "single" in cid else "multi",
            context_bracket="2K" if "2K" in cid else "8K",
            tier=tier_name,
            difficulty=int(tier_name.split("-")[-1]) if "-" in tier_name and tier_name.split("-")[-1].isdigit() else 1,
            timeout_seconds=30,
        )

    def run_challenge(self, challenge_dir: Path, keep_scratch: bool = False) -> ChallengeExecutionResult:
        """Run the full BaaC cycle for a single challenge."""
        t_start = time.perf_counter()
        meta = self.load_challenge_metadata(challenge_dir)
        cid = meta.id

        # 1. Step 1: Verify Zero-State of challenge directory against manifest
        is_zero_ok, drifts = verify_challenge_zero_state(challenge_dir)
        if not is_zero_ok:
            return ChallengeExecutionResult(
                challenge_id=cid,
                tier=meta.tier,
                scope=meta.scope,
                context_bracket=meta.context_bracket,
                preset=self.preset,
                model=self.model_name,
                mode=self.mode,
                status="FAIL",
                attribution="DATASET_INVALID",
                turns=0,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost_usd=0.0,
                duration_seconds=0.0,
                diagnosis=f"Zero-state verification failed: {'; '.join(drifts)}",
                metadata=meta.to_dict(),
            )

        # 2. Step 2: Read Task Brief
        task_md_file = challenge_dir / "TASK.md"
        task_brief = task_md_file.read_text(encoding="utf-8") if task_md_file.is_file() else f"Challenge {cid}"

        # 3. Step 3: Materialize Ephemeral Scratch Workspace
        scratch_dir = Path(tempfile.mkdtemp(prefix=f"baac-scratch-{cid}-"))
        try:
            materialize_scratch_workspace(challenge_dir, scratch_dir)

            budget_tracker = self.campaign_budget
            before_prompt = budget_tracker.total_prompt_tokens
            before_completion = budget_tracker.total_completion_tokens
            before_cost = budget_tracker.total_cost_usd
            cassettes: List[Dict[str, Any]] = []

            # 4. Step 4: Setup ModelPort based on mode
            if self.mode == "live":
                if not self.api_key:
                    raise RuntimeError("OPENROUTER_API_KEY is required for --mode live")
                model_port: Any = OpenRouterModelPort(
                    model_name=self.model_name,
                    budget_tracker=budget_tracker,
                    api_key=self.api_key,
                    cassettes=cassettes,
                )
            elif self.mode == "ollama":
                model_port = OllamaModelPort(
                    model_name=self.model_name,
                    budget_tracker=budget_tracker,
                )
            else:
                model_port = LAMModelPort(
                    challenge_id=cid,
                    budget_tracker=budget_tracker,
                    model_name=self.model_name,
                )

            # 5. Step 5: Execute Agent Harness
            def local_command_runner(cmd: str, cwd: Path) -> Tuple[int, str]:
                env = {
                    **os.environ,
                    "PYTHONPATH": f"{str(cwd.resolve())}:{str((cwd / 'src').resolve())}",
                    "PYTHONDONTWRITEBYTECODE": "1",
                }
                proc = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=cwd,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=meta.timeout_seconds,
                )
                return proc.returncode, (proc.stdout + "\n" + proc.stderr).strip()

            cfg = ForgeConfig(
                max_turns=self.budget_config.max_turns,
                budget_limit_usd=self.budget_config.max_cost_usd,
                require_patch_for_write=True,
                model_name=self.model_name,
                preset_name=self.preset,
            )
            goal = GoalContract(
                task_digest=hashlib.sha256(cid.encode()).hexdigest(),
                mode="write",
            )
            engine = ForgeFacade.create_engine(
                workspace_root=scratch_dir,
                model_port=model_port,
                config=cfg,
                command_runner=local_command_runner,
            )

            harness_status = "COMPLETED"
            turns = 0
            changed_files: tuple[str, ...] = ()
            trajectory: list[dict[str, Any]] = []
            budget_exceeded = False

            try:
                outcome = engine.run_episode(task_brief=task_brief, goal_contract=goal)
                harness_status = outcome.status
                turns = outcome.turns
                changed_files = outcome.changed_files
                trajectory = outcome.trajectory
            except BudgetExceededError:
                harness_status = "BUDGET_EXHAUSTED"
                budget_exceeded = True
            except Exception as h_exc:
                harness_status = "INSTRUMENT_ERROR"

            # Compute unified diff patch
            diff_patch = compute_directory_diff(challenge_dir / "src", scratch_dir / "src" if (scratch_dir / "src").exists() else scratch_dir)

            # 6. Step 6: Execute Ground-Truth Evaluation (Oracle / Judge)
            eval_outcome = evaluate_challenge(
                eval_type=meta.eval_type,
                challenge_dir=challenge_dir,
                scratch_dir=scratch_dir,
                diff_patch=diff_patch,
                timeout_seconds=meta.timeout_seconds,
            )

            status = eval_outcome.status
            attribution = classify_attribution(
                oracle=eval_outcome.oracle_result,
                harness_status=harness_status,
                turns=turns,
                max_turns=self.budget_config.max_turns,
                budget_exceeded=budget_exceeded,
                changed_files=changed_files,
            )

            total_duration = round(time.perf_counter() - t_start, 2)
            diagnosis = "All falsifiers green" if status == "PASS" else eval_outcome.feedback

            merged_meta = dict(meta.to_dict())
            merged_meta.update(self.extra_metadata)

            result = ChallengeExecutionResult(
                challenge_id=cid,
                tier=meta.tier,
                scope=meta.scope,
                context_bracket=meta.context_bracket,
                preset=self.preset,
                model=self.model_name,
                mode=self.mode,
                status=status,
                attribution=attribution,
                turns=turns,
                prompt_tokens=budget_tracker.total_prompt_tokens - before_prompt,
                completion_tokens=budget_tracker.total_completion_tokens - before_completion,
                total_tokens=(budget_tracker.total_prompt_tokens - before_prompt
                              + budget_tracker.total_completion_tokens - before_completion),
                cost_usd=budget_tracker.total_cost_usd - before_cost,
                duration_seconds=total_duration,
                changed_files=changed_files,
                diff_patch=diff_patch,
                oracle_result=eval_outcome.oracle_result,
                ai_judge_score=eval_outcome.score if meta.eval_type == "ai_judge" else None,
                diagnosis=diagnosis,
                metadata=merged_meta,
                trajectory=tuple(trajectory),
            )

            # 7. Step 7: Record Run Artifacts
            res_file = self.run_dir / f"{cid}_result.json"
            res_file.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")

            if cassettes:
                cas_file = self.run_dir / f"{cid}_cassettes.json"
                cas_file.write_text(json.dumps(cassettes, indent=2), encoding="utf-8")

            return result

        finally:
            # 8. Step 8: Reset / Clean Ephemeral Workspace
            if not keep_scratch:
                clean_scratch_workspace(scratch_dir)
