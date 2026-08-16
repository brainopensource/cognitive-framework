"""Meta-Harness Loop Engineering & Self-Correction Engine (Sprint 9).

Orchestrates autonomous multi-turn coding agent execution with context compaction,
error-driven self-reflection on test failure, and dynamic tier escalation.
"""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional

from ..coordination import EpisodeCoordinator


@dataclass
class LoopResult:
    task_id: str
    passed: bool
    turns_executed: int
    prompt_tokens: int
    completion_tokens: int
    wall_latency_s: float
    error_trace: Optional[str] = None
    telemetry: Dict[str, Any] = field(default_factory=dict)


class MetaLoopEngine:
    """Autonomous Meta-Harness Loop with context compaction and test-driven self-correction."""

    def __init__(
        self,
        coordinator: EpisodeCoordinator,
        max_turns: int = 8,
        enable_self_reflection: bool = True,
    ) -> None:
        self.coordinator = coordinator
        self.max_turns = max_turns
        self.enable_self_reflection = enable_self_reflection

    def compact_context(self, files: Mapping[str, str], max_bytes: int = 8192) -> Dict[str, str]:
        """Prune workspace noise to retain prefix stability and high information density."""
        compacted = {}
        for path, content in files.items():
            if path.endswith((".pyc", ".lock", ".log")) or "__pycache__" in path:
                continue
            if len(content) > max_bytes:
                lines = content.splitlines()
                compacted[path] = "\n".join(lines[:100]) + f"\n# ... [truncated {len(lines)-100} lines]"
            else:
                compacted[path] = content
        return compacted

    def run_loop(
        self,
        task_id: str,
        workspace_dir: Path,
        complete_fn: Callable[[list[dict]], dict],
        system_prompt: str = "You are an autonomous software engineering agent. Fix failing tests in the workspace.",
        budget_tokens: int = 20000,
        test_runner: Optional[Callable[[Path], tuple[int, str]]] = None,
    ) -> LoopResult:
        """Execute autonomous meta-harness loop until pytest passes or max_turns exceeded."""
        t0 = time.monotonic()
        episode = self.coordinator.open_episode(task_id=task_id, budget_tokens=budget_tokens)

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Task: {task_id}. Inspect workspace and ensure all unit tests pass."},
        ]

        turns_executed = 0
        prompt_tokens_total = 0
        completion_tokens_total = 0
        passed = False
        last_error = None

        for turn in range(self.max_turns):
            turns_executed += 1
            # Step model completion
            res = complete_fn(messages)
            usage = res.get("usage", {})
            prompt_tokens_total += usage.get("prompt_tokens", 0)
            completion_tokens_total += usage.get("completion_tokens", 0)

            choice = res.get("choices", [{}])[0]
            msg = choice.get("message", {})
            messages.append(msg)

            # Check if model made tool calls or stopped
            tool_calls = msg.get("tool_calls", [])
            if not tool_calls or choice.get("finish_reason") == "stop":
                # Execute test evaluation
                if test_runner is not None:
                    exit_code, output_text = test_runner(workspace_dir)
                else:
                    test_proc = subprocess.run(
                        [sys.executable, "-m", "pytest"],
                        cwd=workspace_dir,
                        capture_output=True,
                        text=True,
                    )
                    exit_code, output_text = test_proc.returncode, test_proc.stdout or test_proc.stderr

                if exit_code == 0:
                    passed = True
                    break

                last_error = output_text
                if self.enable_self_reflection and turn < self.max_turns - 1:
                    # Provide feedback loop with diagnostic error trace
                    messages.append({
                        "role": "user",
                        "content": f"Pytest failed (exit {exit_code}):\n{last_error}\nDiagnose the error and apply the necessary fix.",
                    })
                else:
                    break

        wall_s = round(time.monotonic() - t0, 3)
        try:
            self.coordinator.consume(episode["episode_id"], prompt_tokens_total + completion_tokens_total)
        except Exception:
            pass

        cei = round(completion_tokens_total / max(1, prompt_tokens_total), 3)

        return LoopResult(
            task_id=task_id,
            passed=passed,
            turns_executed=turns_executed,
            prompt_tokens=prompt_tokens_total,
            completion_tokens=completion_tokens_total,
            wall_latency_s=wall_s,
            error_trace=last_error if not passed else None,
            telemetry={
                "cei": cei,
                "fpsr": 1.0 if passed and turns_executed == 1 else 0.0,
                "episode_id": episode["episode_id"],
                "depth_label": episode["depth_label"],
            },
        )
