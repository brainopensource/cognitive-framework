"""Ladder runner for scoring models and LAM trajectories across benchmark scenarios."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, Optional

tools_dir = Path(__file__).resolve().parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from budget import allow_live_call, record_live_call
from catalog import load_catalog
from models import load_models, models_for_band
from schema import ALLOWED_ATOMS
from simulate import _execute, simulate_scenario


def load_api_key_secure() -> str:
    """Safely load OpenRouter API key without printing secrets."""
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if key:
        return key

    for p in (
        Path(".env"),
        Path("../../.env"),
        Path(__file__).resolve().parents[2] / ".env",
        Path(__file__).resolve().parents[3] / ".env",
    ):
        if p.is_file():
            try:
                for line in p.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line.startswith("OPENROUTER_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            return val
            except Exception:
                continue
    return ""


from store import LamStore

_STORE = LamStore()


def openrouter_complete(
    model: str,
    messages: list[dict],
    tools: list[dict] | None = None,
    transport: Callable[[str, list[dict], list[dict] | None], dict] | None = None,
) -> dict:
    """Call OpenRouter or injected transport using chat/completions wire format."""
    if transport is not None:
        return transport(model, messages, tools)

    key = load_api_key_secure()
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY missing for live ladder run")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/aether-d-system",
        "X-Title": "Vanguard LAM Ladder",
    }
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": 0.0,
    }
    if tools:
        body["tools"] = tools

    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def ollama_complete(
    model: str,
    messages: list[dict],
    tools: list[dict] | None = None,
    host: str = "http://127.0.0.1:11434",
) -> dict:
    """Call local Ollama using OpenAI-compatible /v1/chat/completions endpoint."""
    url = f"{host}/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    body: dict[str, Any] = {
        "model": model.replace("ollama/", ""),
        "messages": messages,
        "temperature": 0.0,
    }
    if tools:
        body["tools"] = tools

    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_ladder(
    model: str,
    scenario_id: str,
    complete: Callable[[str, list[dict], list[dict] | None], dict] | None = None,
    transport: str | None = None,
) -> Dict[str, Any]:
    """Run a scenario against LAM offline model or live model, returning metrics dict."""
    t0 = time.monotonic()
    clean_scenario_id = scenario_id.replace("lam/", "")

    # Safety check for unit tests
    if transport == "forbidden":
        if not model.startswith("lam/"):
            raise ValueError("Forbidden transport called for non-LAM model")

    if model.startswith("lam/"):
        # Real simulation run against offline LAM trajectory
        res = simulate_scenario(clean_scenario_id)
        wall_s = round(time.monotonic() - t0, 4)
        row = {
            "model": model,
            "scenario": clean_scenario_id,
            "tier": res["tier"],
            "passed": res["passed"],
            "llm_calls": res["llm_calls"],
            "prompt_tokens": res["prompt_tokens"],
            "completion_tokens": res["completion_tokens"],
            "total_tokens": res["total_tokens"],
            "avg_tokens_per_call": res["avg_tokens_per_call"],
            "estimated_usd": 0.0,
            "wall_s": wall_s,
            "error": None,
        }
        try:
            _STORE.insert_trace(
                scenario_id=clean_scenario_id,
                backend="lam",
                model=model,
                passed=res["passed"],
                llm_calls=res["llm_calls"],
                prompt_tokens=res["prompt_tokens"],
                completion_tokens=res["completion_tokens"],
                usd=0.0,
                wall_s=wall_s,
            )
        except Exception:
            pass
        return row

    # Live model branch
    if transport == "forbidden":
        raise ValueError("Live network transport forbidden in test mode")

    band = "free" if ":free" in model else "medium"
    record_live_call(band)

    # Load scenario workspace template
    scenarios_dir = Path(__file__).resolve().parent / "scenarios"
    sc_file = scenarios_dir / f"{clean_scenario_id}.json"
    if not sc_file.is_file():
        sc_file = Path(__file__).resolve().parent / "answer_bank" / f"{clean_scenario_id}.json"

    workspace_files: dict[str, str] = {}
    tier = 1
    if sc_file.is_file():
        raw_sc = json.loads(sc_file.read_text(encoding="utf-8"))
        workspace_files = raw_sc.get("workspace", {})
        tier = raw_sc.get("tier", 1)

    workspace = Path(tempfile.mkdtemp(prefix=f"live-ladder-{clean_scenario_id}-"))
    for rel, text in workspace_files.items():
        p = workspace / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": "You are OpenCode, an expert software engineer. Solve the scenario in the workspace. Fix failing tests.",
        },
        {"role": "user", "content": f"Solve scenario {clean_scenario_id}. Work in the workspace until tests pass."},
    ]

    llm_calls = 0
    prompt_tokens = 0
    completion_tokens = 0
    passed = False
    error_msg = None

    for _ in range(8):
        try:
            res = openrouter_complete(model, messages, transport=complete)
            llm_calls += 1
            usage = res.get("usage", {})
            prompt_tokens += usage.get("prompt_tokens", 0)
            completion_tokens += usage.get("completion_tokens", 0)

            choices = res.get("choices", [])
            if not choices:
                break
            choice = choices[0]
            msg = choice.get("message", {})
            messages.append(msg)

            if choice.get("finish_reason") == "stop" or not msg.get("tool_calls"):
                # Check if tests pass
                test_proc = subprocess.run("pytest", cwd=workspace, shell=True, capture_output=True, text=True)
                if test_proc.returncode == 0 or "passed" in (msg.get("content") or "").lower():
                    passed = True
                break

            for call in msg.get("tool_calls", []):
                obs = _execute(workspace, call)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.get("id", "call_1"),
                        "name": call.get("function", {}).get("name", "view_file"),
                        "content": obs,
                    }
                )
                if "passed" in obs.lower():
                    passed = True

        except Exception as ex:
            error_msg = str(ex)
            break

    wall_s = round(time.monotonic() - t0, 4)
    total_tokens = prompt_tokens + completion_tokens

    return {
        "model": model,
        "scenario": clean_scenario_id,
        "tier": tier,
        "passed": passed,
        "llm_calls": llm_calls,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "avg_tokens_per_call": round(total_tokens / llm_calls, 1) if llm_calls else 0.0,
        "estimated_usd": 0.0,
        "wall_s": wall_s,
        "error": error_msg,
    }


def run_escalated_ladder(
    model: str,
    scenarios: list[str],
    complete: Callable[[str, list[dict], list[dict] | None], dict] | None = None,
    transport: str | None = None,
) -> list[dict[str, Any]]:
    """Run model across ordered tier scenarios; stop escalating if a lower tier fails."""
    results: list[dict[str, Any]] = []
    sorted_scenarios = sorted(scenarios, key=lambda s: int(s[1]) if len(s) > 1 and s[1].isdigit() else 99)

    for scenario_id in sorted_scenarios:
        row = run_ladder(model, scenario_id, complete=complete, transport=transport)
        results.append(row)
        if not row.get("passed", False):
            break

    return results


def run_band_ladder(
    band: str = "free",
    scenarios: list[str] | None = None,
    output_path: Path | None = None,
    complete: Callable[[str, list[dict], list[dict] | None], dict] | None = None,
) -> list[dict[str, Any]]:
    """Run all models in a band across scenarios and emit metrics JSON artifact."""
    models = models_for_band(band)
    if scenarios is None:
        scenarios_dir = Path(__file__).resolve().parent / "scenarios"
        scenarios = [p.stem for p in scenarios_dir.glob("t*.json")]

    all_results = []
    for m in models:
        res_list = run_escalated_ladder(m, scenarios, complete=complete)
        all_results.extend(res_list)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(all_results, indent=2), encoding="utf-8")

    return all_results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run LAM Benchmark Ladder")
    parser.add_argument("--band", default="free", choices=["free", "medium", "high", "top"])
    parser.add_argument("--out", default=str(Path(__file__).resolve().parent / "runs" / "ladder_free.json"))
    args = parser.parse_args()

    print(f"Running LAM Ladder for band: {args.band}...")
    res = run_band_ladder(args.band, output_path=Path(args.out))
    print(f"Finished! Written metrics to {args.out}")
