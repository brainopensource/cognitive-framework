"""Bounded real-model coding collection for the LAM replay laboratory.

This module deliberately stays outside Vanguard.  It runs a small coding agent
against a temporary copy of a challenge, records complete model/tool traffic,
and emits exact-request cassettes that LAM can replay later.
"""

from __future__ import annotations

import argparse
import base64
import difflib
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

LAM_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(LAM_DIR.parents[1]))
from vanguard.packages.adapters.models.config import get_default_model
from vanguard.packages.domain.workspace import controlled_environment, get_workspace_path
DEFAULT_CHALLENGE_ROOT = Path("/home/rocha/Coding/LEX_LLM_EXECUTION/lab")
DEFAULT_MODEL = get_default_model()
DEFAULT_MAX_CALLS = 60
DEFAULT_MAX_USD = 0.10

# Conservative fallback rates in USD per million tokens.  OpenRouter's usage
# cost is preferred; these rates prevent an absent cost field from bypassing
# the spending guard.
FALLBACK_INPUT_USD_PER_MILLION = 1.00
FALLBACK_OUTPUT_USD_PER_MILLION = 2.00


class CollectionLimit(RuntimeError):
    """Raised before a request that would exceed the collection budget."""


@dataclass(frozen=True)
class Challenge:
    key: str
    root: Path
    problem: str
    is_swe_fixture: bool = False
    public_root: Path | None = None
    private_root: Path | None = None
@dataclass
class Budget:
    max_calls: int = DEFAULT_MAX_CALLS
    max_usd: float = DEFAULT_MAX_USD
    calls: int = 0
    spent_usd: float = 0.0
    reserved_usd: float = 0.0

    def reserve(self, estimated_usd: float = 0.0) -> None:
        if self.calls >= self.max_calls:
            raise CollectionLimit(f"call budget exhausted ({self.max_calls})")
        if self.spent_usd + self.reserved_usd + estimated_usd > self.max_usd:
            raise CollectionLimit(
                f"estimated spend budget exhausted (${self.spent_usd + self.reserved_usd + estimated_usd:.6f} > ${self.max_usd:.6f})"
            )
        self.calls += 1
        self.reserved_usd += max(0.0, estimated_usd)

    def charge(self, amount: float) -> None:
        self.spent_usd += max(0.0, amount)
        self.reserved_usd = 0.0
        if self.spent_usd > self.max_usd:
            raise CollectionLimit(
                f"spend budget exhausted (${self.spent_usd:.6f} > ${self.max_usd:.6f})"
            )


def load_dotenv_value(path: Path, name: str) -> str:
    """Read one dotenv value without printing or exposing the file contents."""
    if not path.is_file():
        return ""
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == name:
            return value.strip().strip('"').strip("'")
    return ""


def resolve_api_key(dotenv_path: Path) -> str:
    return os.environ.get("OPENROUTER_API_KEY", "") or load_dotenv_value(
        dotenv_path, "OPENROUTER_API_KEY"
    )


def load_challenge(root: Path, key: str) -> Challenge:
    challenge_root = (root / key).resolve()
    root_resolved = root.resolve()
    if root_resolved not in challenge_root.parents and challenge_root != root_resolved:
        raise ValueError(f"challenge escapes root: {key}")
    if not challenge_root.is_dir():
        raise FileNotFoundError(f"challenge not found: {challenge_root}")

    # Check for SWE-style fixture (challenge.json + context.md + public/)
    context_md = challenge_root / "context.md"
    challenge_json = challenge_root / "challenge.json"
    public_dir = challenge_root / "public"
    private_dir = challenge_root / "private"
    if context_md.is_file() and public_dir.is_dir():
        problem_text = context_md.read_text(encoding="utf-8")
        return Challenge(
            key=key,
            root=challenge_root,
            problem=problem_text,
            is_swe_fixture=True,
            public_root=public_dir,
            private_root=private_dir if private_dir.is_dir() else None,
        )

    problem_path = challenge_root / "problem.md"
    if not problem_path.is_file():
        raise FileNotFoundError(f"challenge has no problem.md or context.md: {challenge_root}")
    return Challenge(
        key=key,
        root=challenge_root,
        problem=problem_path.read_text(encoding="utf-8"),
        is_swe_fixture=False,
    )


def _safe_path(workspace: Path, raw_path: str) -> Path:
    candidate = (workspace / raw_path).resolve()
    if candidate != workspace and workspace not in candidate.parents:
        raise ValueError("path escapes the task workspace")
    return candidate


def _run_command(workspace: Path, command: str, timeout: int = 30) -> str:
    if not command.strip():
        return "error: empty command"
    # Shell metacharacters are unnecessary for this harness and would make
    # model-generated commands harder to contain.
    if any(token in command for token in (";", "&&", "||", ">", "<", "`", "$(", "|")):
        return "error: shell operators are disabled"
    try:
        argv = shlex.split(command)
    except ValueError as exc:
        return f"error: invalid command syntax: {exc}"
    if not argv or argv[0] not in {
        "cat", "find", "git", "grep", "ls", "python", "python3", "pytest", "pwd", "rg", "sed"
    }:
        return f"error: command not allowed: {argv[0] if argv else '<empty>'}"
    try:
        result = subprocess.run(
            argv,
            cwd=workspace,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
            env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": ""},
        )
    except subprocess.TimeoutExpired:
        return f"error: command timed out after {timeout}s"
    output = (result.stdout + result.stderr).strip()
    return f"exit={result.returncode}\n{output}"[:12000]


TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "view_file",
            "description": "Read a UTF-8 file in the task workspace.",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace a UTF-8 file in the task workspace with complete contents.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a safe, non-interactive inspection or test command in the workspace.",
            "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files below a workspace directory.",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        },
    },
]


def execute_tool(workspace: Path, name: str, arguments: Mapping[str, Any]) -> str:
    try:
        if name == "view_file":
            path = _safe_path(workspace, str(arguments.get("path", "")))
            return path.read_text(encoding="utf-8")[:16000]
        if name == "edit_file":
            path = _safe_path(workspace, str(arguments.get("path", "")))
            content = str(arguments.get("content", ""))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return f"edited {path.relative_to(workspace)}"
        if name == "run_command":
            return _run_command(workspace, str(arguments.get("command", "")))
        if name == "list_dir":
            path = _safe_path(workspace, str(arguments.get("path", ".")))
            return "\n".join(sorted(str(item.relative_to(workspace)) for item in path.rglob("*") if item.is_file())[:500])
        return f"error: unknown tool {name}"
    except Exception as exc:
        return f"error: {type(exc).__name__}: {exc}"


def _tool_calls(message: Mapping[str, Any]) -> list[dict[str, Any]]:
    calls = message.get("tool_calls") or []
    return [call for call in calls if isinstance(call, Mapping)]


def _parse_arguments(raw: Any) -> dict[str, Any]:
    if isinstance(raw, Mapping):
        return dict(raw)
    try:
        parsed = json.loads(str(raw or "{}"))
        return dict(parsed) if isinstance(parsed, Mapping) else {}
    except json.JSONDecodeError:
        return {}


class OpenRouterClient:
    def __init__(self, api_key: str, model: str, budget: Budget, timeout_s: int = 25) -> None:
        self.api_key = api_key
        self.model = model
        self.budget = budget
        self.timeout_s = timeout_s

    def complete(self, messages: Sequence[Mapping[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], bytes]:
        import urllib.request

        request_body = {
            "model": self.model,
            "messages": list(messages),
            "tools": TOOLS,
            "tool_choice": "auto",
            "temperature": 0.2,
            "max_tokens": 600,
            "stream": False,
        }
        if self.model.startswith("stealth/"):
            request_body["reasoning"] = {"effort": "low"}
        raw_request = json.dumps(request_body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        estimated_usd = (
            (len(raw_request) / 4) * FALLBACK_INPUT_USD_PER_MILLION
            + 600 * FALLBACK_OUTPUT_USD_PER_MILLION
        ) / 1_000_000
        self.budget.reserve(estimated_usd)
        request = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=raw_request,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/aether-d-system",
                "X-Title": "AETHER LAM coding collection",
            },
            method="POST",
        )
        last_exc: Exception | None = None
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                    raw_response = response.read()
                break
            except urllib.error.HTTPError as exc:
                last_exc = exc
                if exc.code in (429, 500, 502, 503, 504) and attempt < 3:
                    time.sleep(2 ** attempt + 1)
                    continue
                raise
            except Exception as exc:
                last_exc = exc
                if attempt < 3:
                    time.sleep(2 ** attempt + 1)
                    continue
                raise
        else:
            if last_exc:
                raise last_exc
            raise RuntimeError("Request failed after retries")

        payload = json.loads(raw_response.decode("utf-8"))
        usage = payload.get("usage") or {}
        cost = usage.get("cost")
        if cost is None:
            cost = (
                int(usage.get("prompt_tokens") or 0) * FALLBACK_INPUT_USD_PER_MILLION
                + int(usage.get("completion_tokens") or 0) * FALLBACK_OUTPUT_USD_PER_MILLION
            ) / 1_000_000
        self.budget.charge(float(cost))
        payload["lam_collection"] = {
            "request_sha256": hashlib.sha256(raw_request).hexdigest(),
            "response_sha256": hashlib.sha256(raw_response).hexdigest(),
            "cost_usd": float(cost),
        }
        return request_body, payload, raw_response


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _snapshot(workspace: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in sorted(item for item in workspace.rglob("*") if item.is_file()):
        if ".pytest_cache" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            snapshot[str(path.relative_to(workspace))] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            snapshot[str(path.relative_to(workspace))] = "<binary>"
    return snapshot


def _text_diff(before: Mapping[str, str], after: Mapping[str, str]) -> str:
    lines: list[str] = []
    for name in sorted(set(before) | set(after)):
        old = before.get(name, "").splitlines(keepends=True)
        new = after.get(name, "").splitlines(keepends=True)
        if old != new:
            lines.extend(
                difflib.unified_diff(old, new, fromfile=f"a/{name}", tofile=f"b/{name}")
            )
    return "".join(lines)[:50000]


def collect_challenge(
    challenge: Challenge,
    client: OpenRouterClient,
    output_root: Path,
    max_turns: int = 20,
) -> dict[str, Any]:
    run_id = f"{challenge.key}-{uuid.uuid4().hex[:10]}"
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    started = time.time()
    trajectory: list[dict[str, Any]] = []
    cassette_lines: list[str] = []
    passed = False
    stop_reason = "max_turns"

    with tempfile.TemporaryDirectory(prefix="lam-task-", dir=get_workspace_path("tmp")) as temp_dir:
        workspace = Path(temp_dir) / challenge.key
        if challenge.is_swe_fixture and challenge.public_root:
            shutil.copytree(challenge.public_root, workspace)
        else:
            shutil.copytree(challenge.root, workspace)
        before_snapshot = _snapshot(workspace)
        system = (
            "You are a careful repository coding agent. Solve the user's bug in the provided "
            "workspace. Do not edit tests or problem.md. Inspect files first, make the smallest "
            "correct implementation change, run tests, and stop only after verification."
        )
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system},
            {"role": "user", "content": challenge.problem},
        ]

        for turn in range(max_turns):
            try:
                request_body, response, raw_response = client.complete(messages)
            except CollectionLimit as exc:
                stop_reason = f"budget_stop: {exc}"
                break
            raw_request = json.dumps(request_body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            cassette_lines.append(
                json.dumps(
                    {
                        "request_sha256": hashlib.sha256(raw_request).hexdigest(),
                        "response_b64": base64.b64encode(raw_response).decode("ascii"),
                        "status_code": 200,
                        "content_type": "application/json",
                        "is_stream": False,
                    },
                    separators=(",", ":"),
                )
            )
            choice = (response.get("choices") or [{}])[0]
            message = dict(choice.get("message") or {})
            trajectory.append(
                {
                    "turn": turn,
                    "request": request_body,
                    "response": response,
                    "tool_results": [],
                }
            )
            messages.append({"role": "assistant", **message})
            calls = _tool_calls(message)
            if not calls:
                stop_reason = str(choice.get("finish_reason") or "stop")
                break
            for call in calls:
                function = call.get("function") or {}
                name = str(function.get("name") or "")
                result = execute_tool(workspace, name, _parse_arguments(function.get("arguments")))
                trajectory[-1]["tool_results"].append(
                    {"tool_call_id": call.get("id", f"call-{turn}"), "name": name, "content": result}
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.get("id", f"call-{turn}"),
                        "name": name,
                        "content": result,
                    }
                )
        else:
            stop_reason = "max_turns"

        # Verification in isolated evaluator space if private root exists
        if challenge.is_swe_fixture and challenge.private_root:
            eval_workspace = Path(temp_dir) / f"{challenge.key}-eval"
            shutil.copytree(workspace, eval_workspace)
            # Apply private test files/patches only into eval_workspace
            for p_file in challenge.private_root.rglob("*"):
                if p_file.is_file():
                    target_p = eval_workspace / p_file.relative_to(challenge.private_root)
                    target_p.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p_file, target_p)
            verification = _run_command(eval_workspace, "python3 -m pytest -q", timeout=60)
        else:
            verification = _run_command(workspace, "python3 -m pytest -q", timeout=60)

        passed = verification.startswith("exit=0")
        diff = _text_diff(before_snapshot, _snapshot(workspace))

    _write_json(run_dir / "trajectory.json", trajectory)
    (run_dir / "cassette.jsonl").write_text("\n".join(cassette_lines) + "\n", encoding="utf-8")
    _write_json(
        run_dir / "result.json",
        {
            "run_id": run_id,
            "challenge": challenge.key,
            "model": client.model,
            "passed": passed,
            "stop_reason": stop_reason,
            "calls": client.budget.calls,
            "spent_usd": client.budget.spent_usd,
            "verification": verification,
            "diff": diff,
            "wall_s": round(time.time() - started, 3),
            "evidence_label": "real-openrouter",
        },
    )
    return json.loads((run_dir / "result.json").read_text(encoding="utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect bounded real-model coding traces for LAM replay.")
    parser.add_argument("--challenge-root", type=Path, default=DEFAULT_CHALLENGE_ROOT)
    parser.add_argument("--split-manifest", type=Path, default=LAM_DIR / "calibration_split.json")
    parser.add_argument("--split", choices=["all", "real_calibration", "real_audit", "real_all", "synthetic"], default=None)
    parser.add_argument("--challenge", action="append", dest="challenges")
    parser.add_argument("--dotenv", type=Path, default=Path("/home/rocha/Coding/LEX_LLM_EXECUTION/.env"))
    parser.add_argument("--output", type=Path, default=LAM_DIR / "runs" / "live_captures")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-calls", type=int, default=DEFAULT_MAX_CALLS)
    parser.add_argument("--max-usd", type=float, default=DEFAULT_MAX_USD)
    parser.add_argument("--request-timeout", type=int, default=25)
    args = parser.parse_args(argv)

    api_key = resolve_api_key(args.dotenv)
    if not api_key:
        print("OPENROUTER_API_KEY is unavailable", file=sys.stderr)
        return 2

    keys: list[str] = []
    if args.challenges:
        keys = args.challenges
    elif args.split and args.split_manifest.is_file():
        manifest = json.loads(args.split_manifest.read_text(encoding="utf-8"))
        if args.split == "real_calibration":
            keys = manifest.get("real_calibration_task_ids", [])
        elif args.split == "real_audit":
            keys = manifest.get("real_audit_task_ids", [])
        elif args.split == "real_all":
            keys = manifest.get("real_task_ids", [])
        elif args.split == "synthetic":
            keys = manifest.get("synthetic_task_ids", [])
        elif args.split == "all":
            keys = [t["id"] for t in manifest.get("tasks", [])]
    else:
        keys = ["semver_parser", "isolated_coding_test", "plugin_dag", "token_bucket", "circuit_breaker"]

    challenges = [load_challenge(args.challenge_root, key) for key in keys]
    args.output.mkdir(parents=True, exist_ok=True)
    budget = Budget(max_calls=args.max_calls, max_usd=args.max_usd)
    client = OpenRouterClient(api_key=api_key, model=args.model, budget=budget, timeout_s=args.request_timeout)
    results: list[dict[str, Any]] = []
    for challenge in challenges:
        try:
            results.append(collect_challenge(challenge, client, args.output))
        except CollectionLimit as exc:
            results.append({"challenge": challenge.key, "status": "budget_stop", "reason": str(exc)})
            break
        except Exception as exc:
            results.append({"challenge": challenge.key, "status": "error", "reason": f"{type(exc).__name__}: {exc}"})
    _write_json(
        args.output / "collection_summary.json",
        {"model": args.model, "calls": budget.calls, "spent_usd": budget.spent_usd, "results": results},
    )
    print(json.dumps({"calls": budget.calls, "spent_usd": budget.spent_usd, "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
