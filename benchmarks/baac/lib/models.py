"""BaaC Multi-Provider Model Execution Layer.

Supports:
1. `LAMModelPort`: $0.00 Sub-millisecond mock replay via LLM API Mock engine (`tools/002_LLM_API_MOCK`).
2. `OllamaModelPort`: Local open-weight models via Ollama API (`qwen2.5:7b`, `llama3.2:3b`, etc.).
3. `OpenRouterModelPort`: OpenRouter provider for Free models, Cheap models (DeepSeek, GLM), and Frontier SOTA ($1B+ Opus, Sonnet 3.7, GPT-4.5).
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple
import urllib.error
import urllib.request

from .budget import BudgetTracker, UnknownUsageError


ROOT = Path(__file__).resolve().parents[3]
MOCK_DIR = ROOT / "tools" / "002_LLM_API_MOCK"


def load_openrouter_api_key() -> str:
    """Load OpenRouter API key securely from environment or .env."""
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


class OpenRouterModelPort:
    """Live ModelPort for OpenRouter API with pre-call budget assertions and telemetry."""

    def __init__(
        self,
        model_name: str,
        budget_tracker: BudgetTracker,
        api_key: str,
        cassettes: Optional[List[Dict[str, Any]]] = None,
        timeout_seconds: int = 45,
    ) -> None:
        self.model_name = model_name
        self.budget_tracker = budget_tracker
        self.api_key = api_key
        self.cassettes = cassettes if cassettes is not None else []
        self.timeout_seconds = timeout_seconds
        self.turn_counter = 0

    def propose(self, context: Any, tools: Any, sampling: Any) -> Any:
        self.turn_counter += 1
        self.budget_tracker.check_pre_call(self.model_name)

        messages = list(context.get("messages", []))
        payload = {
            "model": self.model_name,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "temperature": getattr(sampling, "temperature", 0.0) if hasattr(sampling, "temperature") else 0.0,
            "max_tokens": getattr(sampling, "max_tokens", 4096) if hasattr(sampling, "max_tokens") else 4096,
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
                "X-Title": "Vanguard-BaaC-Scientific-Bench",
            },
        )

        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                resp_bytes = resp.read()
                duration_ms = int((time.perf_counter() - t0) * 1000)
                resp_json = json.loads(resp_bytes.decode("utf-8"))
        except Exception as exc:
            duration_ms = int((time.perf_counter() - t0) * 1000)
            raise RuntimeError(f"OpenRouter API call failed ({duration_ms}ms): {exc}") from exc

        reply_sha = hashlib.sha256(resp_bytes).hexdigest()
        choice = resp_json.get("choices", [{}])[0]
        msg = choice.get("message", {})
        usage = resp_json.get("usage", {})
        if not isinstance(usage, Mapping) or "prompt_tokens" not in usage or "completion_tokens" not in usage:
            raise UnknownUsageError("provider omitted prompt/completion usage")
        p_tok = usage["prompt_tokens"]
        c_tok = usage["completion_tokens"]
        cached_tok = usage.get("cached_tokens", 0)
        reported_cost = usage.get("cost", 0.0) or 0.0

        cost = self.budget_tracker.record_request(
            model=self.model_name,
            prompt_tokens=p_tok,
            completion_tokens=c_tok,
            cached_tokens=cached_tok,
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


class OllamaModelPort:
    """Local ModelPort for Ollama endpoints."""

    def __init__(
        self,
        model_name: str,
        budget_tracker: BudgetTracker,
        base_url: str = "http://127.0.0.1:11434",
        timeout_seconds: int = 60,
    ) -> None:
        self.model_name = model_name
        self.budget_tracker = budget_tracker
        self.base_url = os.environ.get("VANGUARD_OLLAMA_ENDPOINT", base_url).rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.turn_counter = 0

    def propose(self, context: Any, tools: Any, sampling: Any) -> Any:
        self.turn_counter += 1
        self.budget_tracker.check_pre_call(f"ollama/{self.model_name}")

        messages = list(context.get("messages", []))
        endpoint = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": messages,
            "tools": tools,
            "stream": False,
        }
        req_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=req_bytes,
            headers={"Content-Type": "application/json"},
        )

        t0 = time.perf_counter()
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
            resp_bytes = resp.read()
            resp_json = json.loads(resp_bytes.decode("utf-8"))

        choice = resp_json.get("choices", [{}])[0]
        msg = choice.get("message", {})
        usage = resp_json.get("usage", {})
        if not isinstance(usage, Mapping) or "prompt_tokens" not in usage or "completion_tokens" not in usage:
            raise UnknownUsageError("provider omitted prompt/completion usage")
        p_tok = usage["prompt_tokens"]
        c_tok = usage["completion_tokens"]
        cached_tok = usage.get("cached_tokens", 0)

        self.budget_tracker.record_request(
            model=f"ollama/{self.model_name}",
            prompt_tokens=p_tok,
            completion_tokens=c_tok,
            cached_tokens=cached_tok,
            reported_cost=0.0,
        )

        return {"message": msg, "usage": usage}


class LAMModelPort:
    """Hermetic $0.00 ModelPort powered by LLM API Mock engine or challenge oracle fallback."""

    def __init__(
        self,
        challenge_id: str,
        budget_tracker: BudgetTracker,
        model_name: str = "lam-mock",
        scenario_bank_dir: Optional[Path] = None,
    ) -> None:
        self.challenge_id = challenge_id
        self.budget_tracker = budget_tracker
        self.model_name = model_name
        self.turn_counter = 0
        self._engine: Any = None

        bank_dir = scenario_bank_dir or (MOCK_DIR / "scenarios")
        if bank_dir.exists() and (MOCK_DIR / "engine.py").exists():
            sys.path.insert(0, str(MOCK_DIR))
            try:
                from engine import LamEngine
                self._engine = LamEngine.from_directory(bank_dir)
            except Exception:
                self._engine = None

    def propose(self, context: Any, tools: Any, sampling: Any) -> Any:
        self.turn_counter += 1
        self.budget_tracker.check_pre_call(self.model_name)

        messages = list(context.get("messages", []))
        
        # 1. Check if LAM scenario bank has an exact match
        clean_cid = self.challenge_id.replace("bench_single_", "").replace("bench_multi_", "").replace("bench_greenfield_", "")
        scenario_match = None
        if self._engine:
            for s in self._engine.scenarios:
                if s.id in self.challenge_id or s.id in clean_cid or clean_cid.endswith(s.id):
                    scenario_match = s.id
                    break

        if scenario_match and self._engine:
            resp = self._engine.complete({"model": f"lam/{scenario_match}", "messages": messages})
            msg = resp["choices"][0]["message"]
            p_tok = resp["usage"]["prompt_tokens"]
            c_tok = resp["usage"]["completion_tokens"]
            self.budget_tracker.record_request(
                model=self.model_name,
                prompt_tokens=p_tok,
                completion_tokens=c_tok,
                reported_cost=0.0,
            )
            return {"message": msg, "usage": resp["usage"]}

        # 2. Dynamic Challenge Replay based on challenge id
        tool_calls: list[dict[str, Any]] = []
        content = ""

        if self.turn_counter == 1:
            tool_calls = [
                {
                    "id": f"call_read_{self.turn_counter}",
                    "type": "function",
                    "function": {
                        "name": "view_file",
                        "arguments": {"path": "TASK.md"},
                    },
                }
            ]
            content = "Inspecting task requirements and constraints."
        elif self.turn_counter == 2:
            target_path, code = self._get_challenge_solution()
            tool_calls = [
                {
                    "id": f"call_edit_{self.turn_counter}",
                    "type": "function",
                    "function": {
                        "name": "edit_file",
                        "arguments": {
                            "path": target_path,
                            "content": code,
                        },
                    },
                }
            ]
            content = f"Applying verified implementation to {target_path}."
        elif self.turn_counter == 3:
            tool_calls = [
                {
                    "id": f"call_test_{self.turn_counter}",
                    "type": "function",
                    "function": {
                        "name": "run_command",
                        "arguments": {"command": "python3 -m unittest discover -s . -p 'test_*.py'"},
                    },
                }
            ]
            content = "Running test assertions to verify zero regressions."
        else:
            tool_calls = [
                {
                    "id": f"call_fin_{self.turn_counter}",
                    "type": "function",
                    "function": {
                        "name": "finish_task",
                        "arguments": {"summary": f"Challenge {self.challenge_id} completed successfully."},
                    },
                }
            ]
            content = "Task complete and verified green."

        self.budget_tracker.record_request(
            model=self.model_name,
            prompt_tokens=150,
            completion_tokens=40,
            reported_cost=0.0,
        )

        return {
            "message": {
                "content": content,
                "tool_calls": tool_calls,
            },
            "usage": {"prompt_tokens": 150, "completion_tokens": 40, "cost": 0.0},
        }

    def _get_challenge_solution(self) -> Tuple[str, str]:
        cid = self.challenge_id.lower()
        if "fib" in cid:
            return "src/fib.py", '''"""Fibonacci Module."""
from __future__ import annotations
import sys
import argparse

def fib(n: int) -> int:
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
        elif "calculator" in cid:
            return "src/calculator.py", '''def calculate_value(A: float, B: float) -> float:
    return (A + B) * B
'''
        elif "clamp" in cid:
            return "src/clamp.py", '''def clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(val, max_val))
'''
        elif "todo" in cid:
            return "src/todo.py", '''"""JSON-Backed Todo Store."""
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
        elif "string_dedupe" in cid:
            return "src/dedupe.py", '''def remove_consecutive_duplicates(s: str) -> str:
    if not s:
        return ""
    res = [s[0]]
    for ch in s[1:]:
        if ch != res[-1]:
            res.append(ch)
    return "".join(res)
'''
        elif "quiz" in cid:
            return "src/quiz_engine.py", '''"""Quiz Game Engine."""
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
        elif "event_bus" in cid:
            return "src/event_bus.py", '''"""Asynchronous Event Bus."""
from typing import Callable, Any, Dict, List

class EventBus:
    def __init__(self):
        self._handlers = {}
        self._next_id = 1

    def subscribe(self, topic: str, handler: Callable[[Any], None]) -> int:
        sub_id = self._next_id
        self._next_id += 1
        if topic not in self._handlers:
            self._handlers[topic] = []
        self._handlers[topic].append((sub_id, handler))
        return sub_id

    def publish(self, topic: str, payload: Any) -> int:
        count = 0
        for top, handlers in list(self._handlers.items()):
            if top == topic or top == "*":
                for _, h in handlers:
                    h(payload)
                    count += 1
        return count

    def unsubscribe(self, sub_id: int) -> bool:
        for top in list(self._handlers.keys()):
            self._handlers[top] = [(sid, h) for sid, h in self._handlers[top] if sid != sub_id]
            if not self._handlers[top]:
                del self._handlers[top]
        return True
'''
        elif "circuit_breaker" in cid:
            return "src/circuit.py", '''class CircuitBreaker:
    def __init__(self, threshold: int = 2):
        self.threshold = threshold
        self.failures = 0
        self.state = "CLOSED"

    def call(self, func):
        if self.state == "OPEN":
            raise RuntimeError("Circuit is OPEN")
        try:
            res = func()
            self.failures = 0
            return res
        except Exception:
            self.failures += 1
            if self.failures >= self.threshold:
                self.state = "OPEN"
            raise
'''
        elif "immutable_trie" in cid:
            return "src/trie.py", '''from dataclasses import dataclass, field
from typing import Dict

@dataclass(frozen=True)
class TrieNode:
    is_end: bool = False
    children: Dict[str, "TrieNode"] = field(default_factory=dict)

def insert(root: TrieNode, word: str) -> TrieNode:
    if not word:
        return TrieNode(is_end=True, children=root.children)
    ch = word[0]
    child = root.children.get(ch, TrieNode())
    new_child = insert(child, word[1:])
    new_children = dict(root.children)
    new_children[ch] = new_child
    return TrieNode(is_end=root.is_end, children=new_children)
'''
        elif "mvcc" in cid:
            return "src/mvcc.py", '''class MVCCStore:
    def __init__(self):
        self.store = {}

    def put(self, key: str, val: str, tx_id: int):
        if key not in self.store:
            self.store[key] = []
        self.store[key].append((tx_id, val))

    def get(self, key: str, tx_id: int) -> str:
        versions = self.store.get(key, [])
        valid = [v for ver_tx, v in versions if ver_tx <= tx_id]
        return valid[-1] if valid else ""
'''
        return "src/main.py", "# Solution code\n"
