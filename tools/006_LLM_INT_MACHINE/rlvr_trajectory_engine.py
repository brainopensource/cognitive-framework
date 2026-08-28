"""Reinforcement Learning from Verifiable Rewards (Agent-RLVR / SWE-RL) Trajectory Synthesis Engine.

Constructs training-ready dataset samples from empirical harness executions with verifiable step-level
reward signals:
A_hat = R_oracle * 1.0 + R_ast * 0.2 + R_mutation * 0.3 - lambda * diff_penalty.
"""

from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence


@dataclass
class RLVRStep:
    turn_index: int
    prompt_messages: list[dict[str, Any]]
    model_response_content: str
    tool_calls: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]
    ast_valid: bool
    intermediate_reward: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class RLVREpisodeTrajectory:
    trajectory_id: str
    challenge_id: str
    model_name: str
    config_name: str
    steps: list[RLVRStep] = field(default_factory=list)
    final_oracle_passed: bool = False
    mutation_score: float = 0.0
    total_cost_usd: float = 0.0
    total_tokens: int = 0
    total_reward: float = 0.0


class RLVREngine:
    """Records, evaluates, and exports fine-tuning datasets formatted for RLVR / GRPO algorithms."""

    def __init__(self, output_dir: Path | None = None):
        self.out_dir = output_dir or (Path(__file__).parent / "runs" / "rlvr_trajectories")
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.active_episodes: dict[str, RLVREpisodeTrajectory] = {}

    def start_episode(self, trajectory_id: str, challenge_id: str, model_name: str, config_name: str) -> RLVREpisodeTrajectory:
        traj = RLVREpisodeTrajectory(
            trajectory_id=trajectory_id,
            challenge_id=challenge_id,
            model_name=model_name,
            config_name=config_name,
        )
        self.active_episodes[trajectory_id] = traj
        return traj

    def record_step(
        self,
        trajectory_id: str,
        turn_index: int,
        prompt_messages: Sequence[Mapping[str, Any]],
        model_response_content: str,
        tool_calls: Sequence[Mapping[str, Any]],
        tool_results: Sequence[Mapping[str, Any]],
        ast_valid: bool,
    ) -> float:
        traj = self.active_episodes.get(trajectory_id)
        if not traj:
            return 0.0

        # Step-level reward: +0.2 for valid AST, -0.5 for malformed syntax
        step_reward = 0.2 if ast_valid else -0.5

        step = RLVRStep(
            turn_index=turn_index,
            prompt_messages=[dict(m) for m in prompt_messages],
            model_response_content=model_response_content,
            tool_calls=[dict(tc) for tc in tool_calls],
            tool_results=[dict(tr) for tr in tool_results],
            ast_valid=ast_valid,
            intermediate_reward=step_reward,
        )
        traj.steps.append(step)
        return step_reward

    def finalize_episode(
        self,
        trajectory_id: str,
        final_oracle_passed: bool,
        mutation_score: float = 1.0,
        total_cost_usd: float = 0.0,
        total_tokens: int = 0,
    ) -> float:
        traj = self.active_episodes.get(trajectory_id)
        if not traj:
            return 0.0

        traj.final_oracle_passed = final_oracle_passed
        traj.mutation_score = mutation_score
        traj.total_cost_usd = total_cost_usd
        traj.total_tokens = total_tokens

        # Composite Verifiable Advantage Reward:
        # +1.0 for oracle pass, +0.3 for mutation score >= 0.8, -0.05 per extra turn
        turn_penalty = len(traj.steps) * 0.05
        base_reward = (1.0 if final_oracle_passed else -1.0)
        mut_reward = 0.3 if mutation_score >= 0.80 else 0.0
        step_sum = sum(s.intermediate_reward for s in traj.steps)

        total_reward = round(base_reward + mut_reward + step_sum - turn_penalty, 4)
        traj.total_reward = total_reward

        # Auto-export JSONL sample
        sample_path = self.out_dir / f"{trajectory_id}.jsonl"
        with open(sample_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "trajectory_id": traj.trajectory_id,
                "challenge_id": traj.challenge_id,
                "model_name": traj.model_name,
                "config_name": traj.config_name,
                "turns": len(traj.steps),
                "oracle_passed": traj.final_oracle_passed,
                "mutation_score": traj.mutation_score,
                "total_tokens": traj.total_tokens,
                "cost_usd": traj.total_cost_usd,
                "verifiable_reward": traj.total_reward,
                "steps": [
                    {
                        "turn": s.turn_index,
                        "content": s.model_response_content,
                        "tool_calls": s.tool_calls,
                        "ast_valid": s.ast_valid,
                        "reward": s.intermediate_reward,
                    }
                    for s in traj.steps
                ],
            }) + "\n")

        return total_reward
