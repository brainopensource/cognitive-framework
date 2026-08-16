#!/usr/bin/env python3
"""Paired 3-Harness x 2-Model Matrix Evaluation Benchmark Runner.

Evaluates 3 harness manifests:
  1. vg-code-default
  2. vg-code-claude-shaped
  3. vg-code-opencode-shaped

Across 2 models:
  1. deepseek/deepseek-v4-flash-0731 (Paid Low-Cost)
  2. google/gemma-4-26b-a4b-it:free (Verified Free)

Outputs complete comparative metadata, KPIs, tokens, spend, and oracle statuses.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarkings.swe_pro_tiers.challenges import CHALLENGES, SWEProChallenge
from vanguard.packages.adapters.models.openrouter import OpenRouterModel
from vanguard.packages.adapters.models.env_loader import load_api_key

MANIFEST_DIR = ROOT / "vanguard" / "packages" / "agency" / "manifests"

HARNESS_SPECS = {
    "vg-code-default": {
        "system_prompt": "You are an expert autonomous software engineer. Prefer reading files before writing. One tool per turn.",
        "tool_style": "canonical",
    },
    "vg-code-claude-shaped": {
        "system_prompt": "You are a coding CLI. Prefer Read and Grep before Edit. Use Bash for tests and git only. Smallest patch that satisfies tests. One tool per turn. Do not invent file contents.",
        "tool_style": "claude",
    },
    "vg-code-opencode-shaped": {
        "system_prompt": "Use view_file, grep_file, edit_file, and run_command. Inspect before editing. Run tests after each change. One tool per turn. Do not invent file contents.",
        "tool_style": "opencode",
    },
}

TOOL_SCHEMAS = (
    {
        "name": "fs.read",
        "verb": "fs.read",
        "description": "Read file content from relative workspace path.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Relative file path"}},
            "required": ["path"],
        },
    },
    {
        "name": "fs.write",
        "verb": "fs.write",
        "description": "Write entire file content at relative workspace path.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative file path"},
                "content": {"type": "string", "description": "Full new content of file"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "proc.exec",
        "verb": "proc.exec",
        "description": "Execute a process command in the workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "argv": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Command and arguments list",
                },
            },
            "required": ["argv"],
        },
    },
)


def run_single_cell(
    challenge_id: str,
    harness_name: str,
    model_name: str,
    max_calls: int = 8,
) -> dict[str, Any]:
    challenge = CHALLENGES[challenge_id]
    harness_cfg = HARNESS_SPECS.get(harness_name, HARNESS_SPECS["vg-code-default"])

    print(f"\n====================================================================")
    print(f"🔬 MATRIX RUN: [{challenge_id}] | Harness: {harness_name} | Model: {model_name}")
    print(f"====================================================================")

    api_key_res = load_api_key(ROOT)
    if not api_key_res.ok or not api_key_res.value:
        raise RuntimeError("OPENROUTER_API_KEY not found in environment or .env")

    model_adapter = OpenRouterModel(
        model=model_name,
        environ={"OPENROUTER_API_KEY": api_key_res.value},
        stream=False,
    )

    with tempfile.TemporaryDirectory(prefix=f"matrix-{challenge_id}-{harness_name}-") as td:
        root_td = Path(td)
        repo = root_td / "workspace"
        repo.mkdir(parents=True, exist_ok=True)
        sealed_oracle_dir = root_td / "sealed_oracle"
        sealed_oracle_dir.mkdir(parents=True, exist_ok=True)

        for rel_path, content in challenge.files.items():
            full_p = repo / rel_path
            full_p.parent.mkdir(parents=True, exist_ok=True)
            full_p.write_text(content, encoding="utf-8")

        oracle_path = sealed_oracle_dir / "test_oracle.py"
        oracle_path.write_text(challenge.oracle_code, encoding="utf-8")

        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Matrix Runner"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "matrix@vanguard.dev"], cwd=repo, check=True)
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)

        test_env = {**os.environ, "PYTHONPATH": str(repo)}
        pre_test = subprocess.run(
            [sys.executable, str(oracle_path)],
            cwd=repo,
            env=test_env,
            capture_output=True,
            text=True,
        )
        pre_passed = (pre_test.returncode == 0)

        dialogue: list[dict[str, Any]] = [
            {"role": "system", "content": harness_cfg["system_prompt"]},
            {
                "role": "user",
                "content": (
                    f"Task Brief:\n{challenge.brief}\n\n"
                    f"Repository layout:\n" + "\n".join(f"- {f}" for f in challenge.files) + "\n\n"
                    f"CRITICAL INSTRUCTIONS:\n"
                    f"1. You MUST call tools (`fs.read`, `fs.write`) using function calls to inspect and modify files.\n"
                    f"2. Issue EXACTLY ONE tool call per response.\n"
                    f"3. When writing fixed files, use `fs.write` with the full corrected content.\n"
                    f"4. Finish only AFTER you have written all corrected files."
                ),
            },
        ]

        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_cost_usd = 0.0
        llm_calls_made = 0
        turn_logs: list[dict[str, Any]] = []

        start_time = time.monotonic()

        while llm_calls_made < max_calls:
            llm_calls_made += 1
            context_bundle = {
                "blocks": [
                    {"label": f"turn_{i}", "content": m["content"]}
                    for i, m in enumerate(dialogue)
                ]
            }

            res = model_adapter.propose(
                context_bundle,
                tools=TOOL_SCHEMAS,
                sampling={"temperature": 0.0, "maxTokens": 1500},
            )

            if not res.ok:
                print(f"⚠️ Turn {llm_calls_made} model error: {res.error.message}")
                break

            val = res.value
            if isinstance(val, dict):
                usage = val.get("usage", {})
                p_tok = usage.get("prompt_tokens", 0)
                c_tok = usage.get("completion_tokens", 0)
                total_prompt_tokens += p_tok
                total_completion_tokens += c_tok
                cost = usage.get("cost_usd", 0.0)
                total_cost_usd += cost

            kind = val.get("kind") if isinstance(val, dict) else getattr(val, "kind", None)
            action = val.get("action") if isinstance(val, dict) else getattr(val, "action", None)
            args = val.get("args") if isinstance(val, dict) else getattr(val, "args", {})
            note = val.get("note") if isinstance(val, dict) else getattr(val, "note", "")

            print(f"Turn {llm_calls_made}: kind={kind}, action={action}, args={list(args.keys()) if isinstance(args, dict) else args}")

            turn_logs.append({
                "turn": llm_calls_made,
                "kind": kind,
                "action": action,
                "args": args,
                "note": note,
            })

            if kind == "finish" or action is None:
                break

            tool_obs = ""
            if action == "fs.read":
                target_p = repo / args.get("path", "")
                if target_p.exists() and target_p.is_file():
                    tool_obs = target_p.read_text(encoding="utf-8")
                else:
                    tool_obs = f"File not found: {args.get('path')}"
            elif action == "fs.write":
                target_p = repo / args.get("path", "")
                target_p.parent.mkdir(parents=True, exist_ok=True)
                content_to_write = args.get("content", "")
                target_p.write_text(content_to_write, encoding="utf-8")
                tool_obs = f"Successfully wrote {len(content_to_write)} bytes to {args.get('path')}"
            elif action == "proc.exec":
                argv = args.get("argv", [])
                if argv:
                    cmd_res = subprocess.run(argv, cwd=repo, capture_output=True, text=True)
                    tool_obs = f"Exit code {cmd_res.returncode}\nStdout:\n{cmd_res.stdout}\nStderr:\n{cmd_res.stderr}"
                else:
                    tool_obs = "No argv specified"
            else:
                tool_obs = f"Unknown action {action}"

            dialogue.append({"role": "assistant", "content": f"Action: {action}\nArguments: {json.dumps(args)}"})
            dialogue.append({"role": "user", "content": f"Tool Result ({action}):\n{tool_obs}\n\nContinue fixing files or finish if done."})

        duration = time.monotonic() - start_time

        diff_res = subprocess.run(["git", "diff"], cwd=repo, capture_output=True, text=True)
        patch_text = diff_res.stdout

        post_test = subprocess.run(
            [sys.executable, str(oracle_path)],
            cwd=repo,
            env=test_env,
            capture_output=True,
            text=True,
        )
        post_passed = (post_test.returncode == 0)

        print(f"🏁 RESULT: {'PASSED' if post_passed else 'FAILED'} (Exit code {post_test.returncode}) | Turns: {llm_calls_made} | Tokens: {total_prompt_tokens + total_completion_tokens} | Cost: ${total_cost_usd:.6f}")

        return {
            "challenge_id": challenge_id,
            "harness": harness_name,
            "model": model_name,
            "oracle_passed": post_passed,
            "exit_code": post_test.returncode,
            "pre_passed": pre_passed,
            "turns": llm_calls_made,
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "total_tokens": total_prompt_tokens + total_completion_tokens,
            "cost_usd": total_cost_usd,
            "duration_s": duration,
            "patch_length": len(patch_text),
        }


def main():
    parser = argparse.ArgumentParser(description="Run 3-Harness x 2-Model Matrix Benchmark")
    parser.add_argument("--challenge", default="tier3_token_bucket")
    args = parser.parse_args()

    harnesses = ["vg-code-default", "vg-code-claude-shaped", "vg-code-opencode-shaped"]
    models = ["deepseek/deepseek-v4-flash-0731", "openrouter/free"]

    matrix_results = []
    for h in harnesses:
        for m in models:
            res = run_single_cell(args.challenge, h, m)
            matrix_results.append(res)

    out_path = ROOT / "benchmarkings" / "swe_pro_tiers" / f"matrix_results_{args.challenge}.json"
    out_path.write_text(json.dumps(matrix_results, indent=2), encoding="utf-8")
    print(f"\n💾 Saved full matrix results to {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
