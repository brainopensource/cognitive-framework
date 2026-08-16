"""Live episode runner for zero-hint tasks.

Uses ``Runtime.execute_harness`` with a live OpenAI-compatible model.
Does not modify ``benchmarkings/tasks_phase2`` or LAM cassettes.
Never prints API keys.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vanguard.packages.adapters.models.env_loader import load_api_key
from vanguard.packages.adapters.models.openrouter import OpenRouterModel
from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef, Verdict
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.governance.approvals import OperatorSigner
from vanguard.packages.runtime.root import Runtime, TaskContext

SUITE = Path(__file__).resolve().parent
TASKS_DIR = SUITE / "tasks"
MANIFEST = ROOT / "vanguard/packages/agency/manifests/vg-code-default/manifest.json"

LIVE_TOOL_SCHEMAS: tuple[dict[str, Any], ...] = (
    {
        "name": "read",
        "verb": "fs.read",
        "description": "Read a workspace file.",
        "schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Workspace-relative path"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "search",
        "verb": "fs.search",
        "description": "Search workspace files for a pattern.",
        "schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Workspace-relative directory or file"},
                "pattern": {"type": "string", "description": "Literal or regex pattern"},
            },
            "required": ["path", "pattern"],
            "additionalProperties": False,
        },
    },
    {
        "name": "patch",
        "verb": "patch.apply",
        "description": "Apply a unified diff to the workspace.",
        "schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Primary file touched by the diff"},
                "diff": {"type": "string", "description": "Unified diff text"},
            },
            "required": ["path", "diff"],
            "additionalProperties": False,
        },
    },
    {
        "name": "test",
        "verb": "proc.exec",
        "description": "Run an allowed process (python3, pytest, git, ruff).",
        "schema": {
            "type": "object",
            "properties": {
                "argv": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Argument vector; argv[0] is the executable",
                }
            },
            "required": ["argv"],
            "additionalProperties": False,
        },
    },
)


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    title: str
    allowed_source: str
    prompt: str
    fixture: Path
    oracle: Path
    public_cmd: tuple[str, ...]
    oracle_cmd: tuple[str, ...]


class SkipEvaluator:
    """Lab stand-in: IsolatedEvaluator is not this suite's claim."""

    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol) -> Result[Verdict]:
        return Result.success(
            Verdict(
                outcome="inconclusive",
                reason="zero_hint_v1 evaluates public tests and oracle after the episode",
            )
        )


class LiveModel:
    """Inject sampling and OpenAI tool parameters; do not change the kernel."""

    def __init__(self, inner: OpenRouterModel, *, max_tokens: int) -> None:
        self._inner = inner
        self._max_tokens = max_tokens

    def propose(self, context: Mapping[str, Any], tools: Any, sampling: Mapping[str, Any]) -> Any:
        merged = dict(sampling)
        merged.setdefault("temperature", 0.0)
        merged["maxTokens"] = max(int(merged.get("maxTokens") or 0), self._max_tokens)
        return self._inner.propose(context, LIVE_TOOL_SCHEMAS, merged)


class CountingModel:
    def __init__(self, inner: LiveModel) -> None:
        self._inner = inner
        self.calls = 0
        self.errors: list[str] = []
        self.kinds: list[str] = []

    def propose(self, context: Mapping[str, Any], tools: Any, sampling: Mapping[str, Any]) -> Any:
        self.calls += 1
        result = self._inner.propose(context, tools, sampling)
        if not getattr(result, "ok", False):
            error = getattr(result, "error", None)
            self.errors.append(getattr(error, "message", "") or "provider failure")
            return result
        value = getattr(result, "value", {}) or {}
        self.kinds.append(str(value.get("kind") or value.get("action") or "unknown"))
        return result


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _run_tests(cwd: Path, argv: tuple[str, ...]) -> dict[str, Any]:
    completed = subprocess.run(list(argv), cwd=cwd, capture_output=True, text=True)
    return {
        "argv": list(argv),
        "returncode": completed.returncode,
        "passed": completed.returncode == 0,
        "stdout_tail": (completed.stdout or "")[-4000:],
        "stderr_tail": (completed.stderr or "")[-4000:],
    }


def _load_secret() -> tuple[str | None, str]:
    env_value = os.environ.get("OPENROUTER_API_KEY")
    if env_value:
        return env_value, "environ"
    loaded = load_api_key(ROOT)
    if loaded.ok and loaded.value:
        return loaded.value, "dotenv"
    return None, "missing"


def _ollama_models() -> list[str]:
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return []
    names = []
    for item in body.get("models") or ():
        name = item.get("name")
        if isinstance(name, str) and name:
            names.append(name)
    return names


def _pick_model(requested: str | None) -> dict[str, str]:
    if requested:
        if requested.startswith("ollama/") or ":" in requested and "/" not in requested:
            name = requested.removeprefix("ollama/")
            return {
                "provider": "ollama",
                "model": name,
                "endpoint": "http://127.0.0.1:11434/v1/chat/completions",
            }
        return {
            "provider": "openrouter",
            "model": requested,
            "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        }
    local = _ollama_models()
    preferred = ("qwen2.5:7b", "qwen2.5:3b", "qwen2.5:1.5b", "llama3.2:3b", "deepseek-r1:14b")
    for name in preferred:
        if any(item == name or item.startswith(name) for item in local):
            return {
                "provider": "ollama",
                "model": name,
                "endpoint": "http://127.0.0.1:11434/v1/chat/completions",
            }
    if local:
        return {
            "provider": "ollama",
            "model": local[0],
            "endpoint": "http://127.0.0.1:11434/v1/chat/completions",
        }
    return {
        "provider": "openrouter",
        "model": os.environ.get("VG_LIVE_MODEL", "google/gemini-2.0-flash-001"),
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
    }


def load_task(task_id: str) -> TaskSpec:
    path = TASKS_DIR / task_id
    meta = json.loads((path / "preregistration.json").read_text(encoding="utf-8"))
    prompt = (path / "prompt.txt").read_text(encoding="utf-8").strip()
    workspace = meta["workspace"]
    return TaskSpec(
        task_id=meta["taskId"],
        title=meta["title"],
        allowed_source=workspace["allowedChangedPaths"][0],
        prompt=prompt,
        fixture=path / "fixture" / "initial",
        oracle=path / "oracle",
        public_cmd=tuple(workspace["publicTestCommand"]),
        oracle_cmd=tuple(workspace["oracleTestCommand"]),
    )


def _prepare_repo(root: Path, fixture: Path) -> Path:
    repo = root / "workspace"
    shutil.copytree(fixture, repo)
    _git(repo, "init")
    _git(repo, "config", "user.name", "Zero Hint Lab")
    _git(repo, "config", "user.email", "lab@vanguard.local")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial failing fixture")
    return repo


def _event_summary(events: Any) -> list[dict[str, Any]]:
    rows = []
    for event in events:
        payload = getattr(event, "payload", {}) or {}
        rows.append(
            {
                "kind": getattr(event, "kind", ""),
                "reason": getattr(event, "reason", ""),
                "action": payload.get("action") or payload.get("verb"),
            }
        )
    return rows


def run_task(task: TaskSpec, *, model_cfg: Mapping[str, str], max_turns: int) -> dict[str, Any]:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = TASKS_DIR / task.task_id / "runs" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    secret, secret_source = _load_secret()
    if model_cfg["provider"] == "openrouter" and not secret:
        record = {
            "taskId": task.task_id,
            "status": "instrument_error",
            "error": "OPENROUTER_API_KEY unset",
            "model": dict(model_cfg),
        }
        (out_dir / "result.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        return record

    environ = dict(os.environ)
    if model_cfg["provider"] == "ollama":
        environ["OPENROUTER_API_KEY"] = secret or "ollama-local"
    elif secret:
        environ["OPENROUTER_API_KEY"] = secret

    signer = OperatorSigner(b"zero-hint-v1-operator-key")
    inner = OpenRouterModel(
        model=model_cfg["model"],
        endpoint=model_cfg["endpoint"],
        environ=environ,
        stream=False,
        max_retries=2,
        jitter=False,
    )
    model = CountingModel(LiveModel(inner, max_tokens=2048))

    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix=f"vg-zero-{task.task_id}-") as tmp:
        root = Path(tmp)
        repo = _prepare_repo(root, task.fixture)
        public_before = _run_tests(repo, task.public_cmd)
        try:
            result = Runtime.execute_harness(
                MANIFEST,
                TaskContext(
                    brief=task.prompt,
                    repo_path=repo,
                    run_id=f"zero-hint-{task.task_id}-{run_id}",
                    episode_id=f"zero-hint-episode-{task.task_id}",
                    principal="zero-hint-agent",
                    max_turns=max_turns,
                ),
                interactive=True,
                model=model,
                approver=lambda challenge: signer.approve(challenge, reviewer="lab-auto"),
                verifier=SkipEvaluator(),
                approval_key=signer.public_bytes,
            )
            terminal = result.terminal.value
            detail = result.detail
            receipts = [
                {
                    "verb": receipt.verb,
                    "outcome": receipt.outcome,
                    "detail_tail": (receipt.detail or "")[-1500:],
                }
                for receipt in result.receipts
            ]
            events = _event_summary(result.events)
        except Exception as exc:
            terminal = "runner_error"
            detail = f"{type(exc).__name__}: {exc}"
            receipts = []
            events = []
            result = None

        public_after = _run_tests(repo, task.public_cmd)
        eval_root = root / "eval"
        shutil.copytree(repo, eval_root)
        shutil.copytree(task.oracle, eval_root / "oracle")
        oracle_after = _run_tests(
            eval_root,
            ("python3", "-m", "unittest", "discover", "-s", "oracle", "-p", "test_*.py"),
        )
        diff = subprocess.run(
            ["git", "diff", "--binary"],
            cwd=repo,
            check=False,
            capture_output=True,
        ).stdout
        (out_dir / "final.diff").write_bytes(diff)
        changed = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=repo,
            check=False,
            capture_output=True,
            text=True,
        ).stdout.splitlines()

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    passed = (
        terminal == "completed"
        and public_after["passed"]
        and oracle_after["passed"]
        and set(changed) <= {task.allowed_source}
    )
    record = {
        "schemaVersion": "1.0",
        "taskId": task.task_id,
        "title": task.title,
        "runId": run_id,
        "status": "PASS" if passed else "FAIL",
        "agentic": True,
        "lamReplay": False,
        "singleShotGenerate": False,
        "labDepartures": [
            "auto_approve_privileged_diff",
            "oracle_after_episode_not_isolated_evaluator",
            "provider_tool_json_schema_injected",
            "maxTokens_2048",
        ],
        "model": {
            **dict(model_cfg),
            "secretSource": secret_source if model_cfg["provider"] == "openrouter" else "ollama-local",
            "calls": model.calls,
            "proposalKinds": model.kinds,
            "providerErrors": model.errors[:8],
        },
        "bwrapPresent": Path("/usr/bin/bwrap").exists(),
        "terminal": terminal,
        "detail": detail,
        "elapsedMs": elapsed_ms,
        "receipts": receipts,
        "events": events,
        "changedPaths": changed,
        "publicTestsBefore": {"passed": public_before["passed"], "returncode": public_before["returncode"]},
        "publicTestsAfter": public_after,
        "oracleAfter": oracle_after,
        "hashes": {
            "finalDiff": "sha256:" + hashlib.sha256(diff).hexdigest(),
        },
    }
    (out_dir / "result.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    (out_dir / "events.sanitized.json").write_text(json.dumps(events, indent=2) + "\n", encoding="utf-8")
    (out_dir / "public_tests_after.txt").write_text(
        public_after["stdout_tail"] + "\n" + public_after["stderr_tail"],
        encoding="utf-8",
    )
    (out_dir / "oracle_after.txt").write_text(
        oracle_after["stdout_tail"] + "\n" + oracle_after["stderr_tail"],
        encoding="utf-8",
    )
    return record


def write_preregistration() -> None:
    specs = [
        {
            "taskId": "test002_rate_window",
            "title": "Per-key request admission over any closed window",
            "taskShape": "one-file admission control; tumbling window is insufficient",
            "allowed": ["rate_limit.py"],
            "oracle": "oracle/test_rate_limit_oracle.py",
        },
        {
            "taskId": "test003_invoice_cents",
            "title": "Invoice totals as exact integer cents",
            "taskShape": "one-file money arithmetic; binary float is insufficient",
            "allowed": ["invoicing.py"],
            "oracle": "oracle/test_invoicing_oracle.py",
        },
        {
            "taskId": "test004_busy_merge",
            "title": "Merge closed busy intervals including abutting ends",
            "taskShape": "one-file interval merge; exclusive-end fencepost is insufficient",
            "allowed": ["busy.py"],
            "oracle": "oracle/test_calendar_oracle.py",
        },
    ]
    for spec in specs:
        task_dir = TASKS_DIR / spec["taskId"]
        oracle_path = task_dir / spec["oracle"]
        payload = {
            "schemaVersion": "1.0",
            "taskId": spec["taskId"],
            "title": spec["title"],
            "status": "preregistered_not_executed",
            "taskShape": spec["taskShape"],
            "zeroHint": True,
            "oracleVisibleToModel": False,
            "workspace": {
                "initialFixture": "fixture/initial",
                "allowedTools": ["fs.read", "fs.search", "patch.apply", "proc.exec"],
                "allowedChangedPaths": spec["allowed"],
                "publicTestCommand": ["python3", "-m", "unittest", "discover", "-s", "tests"],
                "oracleTestCommand": ["python3", "-m", "unittest", "discover", "-s", "oracle", "-p", "test_*.py"],
            },
            "limits": {
                "maxTurns": 16,
                "maxModelCalls": 16,
                "maxCompletionTokens": 2048,
            },
            "evaluation": {
                "oraclePath": "oracle",
                "oracleVisibleToModel": False,
                "humanSourceEditsAllowed": 0,
                "oracleDigests": {spec["oracle"]: _sha256(oracle_path)},
            },
        }
        (task_dir / "preregistration.json").write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run zero-hint live coding tasks")
    parser.add_argument("--task", action="append", dest="tasks")
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-turns", type=int, default=16)
    parser.add_argument("--write-preregistration", action="store_true")
    parser.add_argument("--check-fixtures", action="store_true")
    args = parser.parse_args(argv)

    if args.write_preregistration:
        write_preregistration()
        print("wrote preregistration.json for zero_hint_v1 tasks")
        return 0

    task_ids = args.tasks or [
        "test002_rate_window",
        "test003_invoice_cents",
        "test004_busy_merge",
    ]
    if args.check_fixtures:
        failed = 0
        for task_id in task_ids:
            task = load_task(task_id)
            public = _run_tests(task.fixture, task.public_cmd)
            print(f"{task_id} public tests initially passing={public['passed']} code={public['returncode']}")
            if public["passed"]:
                failed += 1
        return 1 if failed else 0

    model_cfg = _pick_model(args.model)
    print(f"model {model_cfg['provider']}:{model_cfg['model']}")
    print(f"bwrap {Path('/usr/bin/bwrap').exists()}")
    overall = 0
    for task_id in task_ids:
        task = load_task(task_id)
        print(f"running {task.task_id}...")
        record = run_task(task, model_cfg=model_cfg, max_turns=args.max_turns)
        print(
            f"  -> {record.get('status')} terminal={record.get('terminal')} "
            f"calls={record.get('model', {}).get('calls')} "
            f"public={record.get('publicTestsAfter', {}).get('passed')} "
            f"oracle={record.get('oracleAfter', {}).get('passed')}"
        )
        if record.get("status") != "PASS":
            overall = 1
    return overall


if __name__ == "__main__":
    raise SystemExit(main())
