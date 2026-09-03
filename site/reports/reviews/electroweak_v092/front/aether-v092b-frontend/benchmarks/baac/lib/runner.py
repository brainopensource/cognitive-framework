"""BaaC Challenge Execution and Telemetry Runner.

Implements:
1. Complete BaaC execution pipeline:
   verify_zero -> materialize_scratch -> execute_harness -> run_external_oracle -> cleanup -> attribute.
2. Dual execution modes:
   - `lam`: hermetic $0.00 sub-millisecond offline replay via LLM API Mock.
   - `live`: OpenRouter execution with pre-call budget checks.
3. Support for presets: `vg-1-forge`, `vg-code-max`, `vg-code-max-v2`.
4. Artifact recording (events, trajectory, telemetry).
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
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
import urllib.error
import urllib.request

from vanguard.packages.runtime.root import (
    FORGE_PRESET_NAME,
    ForgeConfig,
    ForgeFacade,
    GoalContract,
    get_default_paid_model,
    get_pricing_usd_table,
    resolve_model,
)

from .budget import BudgetCapConfig, BudgetTracker, BudgetExceededError
from .oracle import OracleResult, run_external_oracle
from .report import ChallengeExecutionResult, classify_attribution
from .state import (
    clean_scratch_workspace,
    materialize_scratch_workspace,
    verify_challenge_zero_state,
)


ROOT = Path(__file__).resolve().parents[3]
BAAC_RUNS_DIR = ROOT / "benchmarks" / "baac" / "runs"


def load_openrouter_key() -> str:
    """Load OpenRouter API key securely without exposing it."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if key and not key.startswith("your_"):
        return key.strip()
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val and not val.startswith("your_"):
                    return val
    return ""


class OpenRouterLiveModelPort:
    """Live ModelPort communicating with OpenRouter with strict pre-call budget assertions."""

    def __init__(
        self,
        model_name: str,
        budget_tracker: BudgetTracker,
        api_key: str,
        cassettes: List[Dict[str, Any]],
    ) -> None:
        self.model_name = resolve_model(model_name)
        self.budget_tracker = budget_tracker
        self.api_key = api_key
        self.cassettes = cassettes
        self.turn_counter = 0

    def propose(self, context: Any, tools: Any, sampling: Any) -> Any:
        self.turn_counter += 1
        # Pre-call assertion
        self.budget_tracker.check_pre_call(self.model_name)

        messages = list(context.get("messages", []))
        payload = {
            "model": self.model_name,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "temperature": 0.0,
            "max_tokens": 2048,
        }
        req_bytes = json.dumps(payload).encode("utf-8")
        req_sha = hashlib.sha256(req_bytes).hexdigest()

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=req_bytes,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://vanguard.ai",
                "X-Title": "Vanguard-BaaC",
            },
        )

        t0 = time.perf_counter()
        with urllib.request.urlopen(req, timeout=35) as resp:
            resp_bytes = resp.read()
            duration_ms = int((time.perf_counter() - t0) * 1000)
            resp_json = json.loads(resp_bytes.decode("utf-8"))

        reply_sha = hashlib.sha256(resp_bytes).hexdigest()
        choice = resp_json.get("choices", [{}])[0]
        msg = choice.get("message", {})
        usage = resp_json.get("usage", {})
        p_tok = usage.get("prompt_tokens", 0)
        c_tok = usage.get("completion_tokens", 0)
        reported_cost = usage.get("cost", 0.0) or 0.0

        cost = self.budget_tracker.record_request(
            model=self.model_name,
            prompt_tokens=p_tok,
            completion_tokens=c_tok,
            reported_cost=reported_cost,
        )

        self.cassettes.append({
            "turn": self.turn_counter,
            "request_sha256": req_sha,
            "response_sha256": reply_sha,
            "prompt_tokens": p_tok,
            "completion_tokens": c_tok,
            "cost_usd": cost,
            "duration_ms": duration_ms,
        })

        usage["cost"] = cost
        return {"message": msg, "usage": usage}


class LamMockModelPort:
    """Hermetic $0.00 ModelPort using LLM API Mock engine or scripted cassettes."""

    FIB_SOLUTION = '''"""Fibonacci Module."""

from __future__ import annotations
import sys
import argparse


def fib(n: int) -> int:
    """Compute n-th Fibonacci number."""
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    args = parser.parse_args()
    if args.n < 0:
        sys.stderr.write("Error: negative n\\n")
        return 1
    print(fib(args.n))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(1)
'''

    TODO_SOLUTION = '''"""JSON-Backed Todo Store."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Optional


class TodoStore:
    def __init__(self, filepath: str | Path) -> None:
        self.filepath = Path(filepath)
        self.items: list[dict[str, Any]] = []
        if self.filepath.is_file():
            try:
                self.items = json.loads(self.filepath.read_text(encoding="utf-8"))
            except Exception:
                self.items = []
        else:
            self._save()

    def _save(self) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.filepath.write_text(json.dumps(self.items, indent=2), encoding="utf-8")

    def add(self, title: str, tags: list[str] | None = None) -> int:
        if not title or not title.strip():
            raise ValueError("title cannot be empty")
        next_id = max([item["id"] for item in self.items], default=0) + 1
        item = {
            "id": next_id,
            "title": title.strip(),
            "completed": False,
            "tags": list(tags or []),
        }
        self.items.append(item)
        self._save()
        return next_id

    def complete(self, item_id: int) -> bool:
        for item in self.items:
            if item["id"] == item_id:
                item["completed"] = True
                self._save()
                return True
        return False

    def get(self, item_id: int) -> dict | None:
        for item in self.items:
            if item["id"] == item_id:
                return dict(item)
        return None

    def list_pending(self) -> list[dict]:
        pending = [dict(item) for item in self.items if not item["completed"]]
        return sorted(pending, key=lambda x: x["id"])

    def list_by_tag(self, tag: str) -> list[dict]:
        matching = [dict(item) for item in self.items if tag in item.get("tags", [])]
        return sorted(matching, key=lambda x: x["id"])
'''

    QUIZ_SOLUTION = '''"""Quiz Game Engine."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, List, Optional


@dataclass
class Question:
    id: str
    prompt: str
    options: list[str]
    correct_choice: str
    points: int = 10


class QuizEngine:
    def __init__(self, questions: list[Question | dict]) -> None:
        if not questions:
            raise ValueError("questions list cannot be empty")
        self.questions: list[Question] = []
        for q in questions:
            if isinstance(q, Question):
                self.questions.append(q)
            elif isinstance(q, dict):
                self.questions.append(
                    Question(
                        id=str(q["id"]),
                        prompt=str(q["prompt"]),
                        options=list(q["options"]),
                        correct_choice=str(q["correct_choice"]),
                        points=int(q.get("points", 10)),
                    )
                )
        self.index = 0
        self.earned_points = 0
        self.answered_count = 0

    def current_question(self) -> Question | None:
        if self.index < len(self.questions):
            return self.questions[self.index]
        return None

    def submit_answer(self, choice: str) -> dict[str, Any]:
        if self.is_finished():
            raise RuntimeError("Quiz is already finished")
        q = self.questions[self.index]
        clean_choice = str(choice).strip().lower()
        is_correct = clean_choice == str(q.correct_choice).strip().lower()
        points = q.points if is_correct else 0
        self.earned_points += points
        self.answered_count += 1
        self.index += 1
        return {
            "correct": is_correct,
            "earned_points": points,
            "correct_choice": q.correct_choice,
            "question_id": q.id,
        }

    def get_score(self) -> dict[str, Any]:
        total_pts = sum(q.points for q in self.questions)
        pct = (self.earned_points / total_pts * 100.0) if total_pts > 0 else 0.0
        return {
            "total_points": total_pts,
            "earned_points": self.earned_points,
            "score_pct": pct,
            "answered": self.answered_count,
            "total_questions": len(self.questions),
        }

    def is_finished(self) -> bool:
        return self.index >= len(self.questions)

    def reset(self) -> None:
        self.index = 0
        self.earned_points = 0
        self.answered_count = 0

    @classmethod
    def load_from_json(cls, json_path: str | Path) -> QuizEngine:
        p = Path(json_path)
        data = json.loads(p.read_text(encoding="utf-8"))
        return cls(data)
'''

    def __init__(self, challenge_id: str, budget_tracker: BudgetTracker) -> None:
        self.challenge_id = challenge_id
        self.budget_tracker = budget_tracker
        self.turn_counter = 0

    def propose(self, context: Any, tools: Any, sampling: Any) -> Any:
        self.turn_counter += 1
        self.budget_tracker.check_pre_call("lam-mock")

        cid = self.challenge_id
        if cid == "fib_cli":
            target_path = "src/fib.py"
            code = self.FIB_SOLUTION
        elif cid == "json_todo_store":
            target_path = "src/todo.py"
            code = self.TODO_SOLUTION
        elif cid == "quiz_game":
            target_path = "src/quiz_engine.py"
            code = self.QUIZ_SOLUTION
        else:
            target_path = "src/main.py"
            code = "# Generated by LAM\\n"

        if self.turn_counter == 1:
            tool_calls = [
                {
                    "id": "call_1",
                    "function": {
                        "name": "view_file",
                        "arguments": {"path": "TASK.md"},
                    },
                }
            ]
            content = "Inspecting task requirements."
        elif self.turn_counter == 2:
            tool_calls = [
                {
                    "id": "call_2",
                    "function": {
                        "name": "edit_file",
                        "arguments": {
                            "path": target_path,
                            "content": code,
                        },
                    },
                }
            ]
            content = "Applying implementation."
        elif self.turn_counter == 3:
            tool_calls = [
                {
                    "id": "call_3",
                    "function": {
                        "name": "run_command",
                        "arguments": {"command": "python3 oracle/verify.py"},
                    },
                }
            ]
            content = "Running test oracle to verify implementation."
        else:
            tool_calls = [
                {
                    "id": "call_fin",
                    "function": {
                        "name": "finish_task",
                        "arguments": {"summary": f"Challenge {cid} completed and verified green."},
                    },
                }
            ]
            content = "Finished task."

        self.budget_tracker.record_request(
            model="lam-mock",
            prompt_tokens=150,
            completion_tokens=30,
            reported_cost=0.0,
        )

        return {
            "message": {
                "content": content,
                "tool_calls": tool_calls,
            },
            "usage": {"prompt_tokens": 150, "completion_tokens": 30, "cost": 0.0},
        }


class BaaCRunner:
    """Coordinates the BaaC cycle for one or more challenges."""

    def __init__(
        self,
        preset: str = "vg-1-forge",
        model_name: Optional[str] = None,
        mode: str = "lam",
        budget_config: Optional[BudgetCapConfig] = None,
        run_id: Optional[str] = None,
    ) -> None:
        self.preset = preset
        self.model_name = model_name or ("lam-mock" if mode == "lam" else get_default_paid_model())
        self.mode = mode
        self.budget_config = budget_config or BudgetCapConfig()
        self.run_id = run_id or f"baac-run-{int(time.time())}"
        self.api_key = load_openrouter_key() if mode == "live" else ""
        self.run_dir = BAAC_RUNS_DIR / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def run_challenge(self, challenge_dir: Path, keep_scratch: bool = False) -> ChallengeExecutionResult:
        """Run the full BaaC cycle for a single challenge."""
        t_start = time.perf_counter()
        cid = challenge_dir.name
        tier = challenge_dir.parent.name if challenge_dir.parent.name in ("easy", "medium", "hard", "greenfield") else "standard"

        # 1. Step 1: Verify Zero-State of challenge directory
        is_zero_ok, drifts = verify_challenge_zero_state(challenge_dir)
        if not is_zero_ok:
            return ChallengeExecutionResult(
                challenge_id=cid,
                tier=tier,
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
            )

        # 2. Step 2: Read Task Brief and Metadata
        task_md_file = challenge_dir / "TASK.md"
        task_brief = task_md_file.read_text(encoding="utf-8") if task_md_file.is_file() else f"Challenge {cid}"

        # 3. Step 3: Materialize Ephemeral Scratch Workspace
        scratch_dir = Path(tempfile.mkdtemp(prefix=f"baac-scratch-{cid}-"))
        try:
            materialize_scratch_workspace(challenge_dir, scratch_dir)

            budget_tracker = BudgetTracker(self.budget_config)
            cassettes: List[Dict[str, Any]] = []

            # 4. Step 4: Setup ModelPort
            if self.mode == "live":
                if not self.api_key:
                    raise RuntimeError("OPENROUTER_API_KEY is required for --mode live")
                model_port = OpenRouterLiveModelPort(
                    model_name=self.model_name,
                    budget_tracker=budget_tracker,
                    api_key=self.api_key,
                    cassettes=cassettes,
                )
            else:
                model_port = LamMockModelPort(challenge_id=cid, budget_tracker=budget_tracker)

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
                    timeout=30,
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
            except BudgetExceededError as b_err:
                harness_status = "BUDGET_EXHAUSTED"
                budget_exceeded = True
            except Exception as h_exc:
                harness_status = "INSTRUMENT_ERROR"

            # 6. Step 6: Execute Ground-Truth External Oracle
            oracle_script = challenge_dir / "oracle" / "verify.py"
            oracle_result = run_external_oracle(oracle_script, scratch_dir)

            status = "PASS" if oracle_result.passed else "FAIL"
            attribution = classify_attribution(
                oracle=oracle_result,
                harness_status=harness_status,
                turns=turns,
                max_turns=self.budget_config.max_turns,
                budget_exceeded=budget_exceeded,
                changed_files=changed_files,
            )

            total_duration = round(time.perf_counter() - t_start, 2)
            diagnosis = "All falsifiers green" if status == "PASS" else (oracle_result.error or harness_status)

            result = ChallengeExecutionResult(
                challenge_id=cid,
                tier=tier,
                preset=self.preset,
                model=self.model_name,
                mode=self.mode,
                status=status,
                attribution=attribution,
                turns=turns,
                prompt_tokens=budget_tracker.total_prompt_tokens,
                completion_tokens=budget_tracker.total_completion_tokens,
                total_tokens=budget_tracker.total_tokens,
                cost_usd=budget_tracker.total_cost_usd,
                duration_seconds=total_duration,
                oracle_result=oracle_result,
                diagnosis=diagnosis,
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
            # 8. Step 8: Reset / Clean Scratch Workspace
            if not keep_scratch:
                clean_scratch_workspace(scratch_dir)
