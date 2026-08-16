"""Run a scenario as a tiny harness: LAM complete → local tools → repeat."""

from __future__ import annotations

import json
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from engine import LamEngine
from pricing import sonnet_usd

_HERE = Path(__file__).resolve().parent
_ENGINE = LamEngine.from_directory(_HERE / "scenarios")

SYSTEM = (
    "You are OpenCode, an expert autonomous software engineer. "
    "Use provided tools to investigate and fix bugs. Never guess file contents."
)


def simulate_scenario(scenario_id: str) -> dict[str, Any]:
    scenario = _ENGINE.scenario(f"lam/{scenario_id}")
    workspace = Path(tempfile.mkdtemp(prefix=f"lam-{scenario_id}-"))
    for relative, text in scenario.workspace.items():
        path = workspace / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if text:
            path.write_text(text, encoding="utf-8")
        elif not path.exists():
            path.write_text("", encoding="utf-8")

    user = f"{scenario.title}. Work in the workspace until tests pass."
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user},
    ]
    started = time.perf_counter()
    calls = 0
    prompt_tokens = 0
    completion_tokens = 0
    transcript: list[dict[str, Any]] = []

    for _ in range(16):
        result = _ENGINE.complete({"model": f"lam/{scenario_id}", "messages": messages})
        calls += 1
        usage = result.get("usage") or {}
        prompt_tokens += int(usage.get("prompt_tokens") or 0)
        completion_tokens += int(usage.get("completion_tokens") or 0)
        choice = result["choices"][0]
        message = choice["message"]
        messages.append(message)
        transcript.append({"llm": result})
        if choice.get("finish_reason") == "stop" or not message.get("tool_calls"):
            break
        for call in message["tool_calls"]:
            observation = _execute(workspace, call)
            tool_msg = {
                "role": "tool",
                "tool_call_id": call.get("id"),
                "name": call["function"]["name"],
                "content": observation,
            }
            messages.append(tool_msg)
            transcript.append({"tool": tool_msg})
            if call["function"]["name"] == "run_command" and "passed" in observation.lower():
                messages.append(
                    {
                        "role": "user",
                        "content": f"Verification test runner output:\n{observation}",
                    }
                )

    wall_ms = (time.perf_counter() - started) * 1000
    return {
        "scenario": scenario_id,
        "tier": scenario.tier,
        "llm_calls": calls,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "avg_tokens_per_call": round((prompt_tokens + completion_tokens) / calls, 1) if calls else 0,
        "estimated_usd_lam": 0.0,
        "estimated_usd_if_sonnet": sonnet_usd(prompt_tokens, completion_tokens),
        "avg_usd_per_call_if_sonnet": round(
            sonnet_usd(prompt_tokens, completion_tokens) / calls, 6
        )
        if calls
        else 0.0,
        "wall_ms": round(wall_ms, 3),
        "workspace": str(workspace),
        "turns_recorded": len(transcript),
    }


def simulate_all() -> list[dict[str, Any]]:
    return [simulate_scenario(item.id) for item in _ENGINE.scenarios]


def _execute(workspace: Path, call: dict[str, Any]) -> str:
    name = call["function"]["name"]
    args = json.loads(call["function"]["arguments"] or "{}")
    if name == "view_file":
        path = workspace / args["path"]
        if not path.is_file():
            return f"error: not found: {args['path']}"
        return path.read_text(encoding="utf-8")
    if name == "edit_file":
        path = workspace / args["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        target = args.get("target") or ""
        replacement = args.get("replacement") or ""
        if not path.exists() or target == "":
            path.write_text(replacement, encoding="utf-8")
            return json.dumps({"status": "success", "message": f"wrote {args['path']}"})
        text = path.read_text(encoding="utf-8")
        if target not in text:
            return json.dumps({"status": "error", "message": "target not found"})
        path.write_text(text.replace(target, replacement, 1), encoding="utf-8")
        return json.dumps({"status": "success", "message": f"replaced 1 occurrence in {args['path']}"})
    if name == "run_command":
        completed = subprocess.run(
            args["command"],
            cwd=workspace,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        out = (completed.stdout or "") + (completed.stderr or "")
        if completed.returncode == 0:
            return out or "passed"
        return f"exit {completed.returncode}\n{out}"
    return f"error: unknown tool {name}"


if __name__ == "__main__":
    print(json.dumps(simulate_all(), indent=2))
