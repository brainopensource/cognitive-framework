#!/usr/bin/env python3
"""SWE Verified Pro Benchmark Runner using Live OpenRouter Models.

Executes live, multi-file zero-hint challenges with real OpenRouter LLM API calls.
Enforces strict 30-call ceiling to ensure total spend is below $0.50.
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


def get_default_model_for_tier(tier: int) -> str:
    if tier == 1:
        return "llama3.2:3b"
    elif tier == 2:
        return "qwen3.6:27b"
    elif tier == 3:
        return "openrouter/free"
    elif tier in (4, 5):
        return "deepseek/deepseek-v4-flash"
    else:
        return "openai/gpt-5.6-luna"


def run_live_challenge(
    challenge_id: str,
    model_name: str | None = None,
    max_calls: int = 30,
) -> dict[str, Any]:
    if challenge_id not in CHALLENGES:
        raise ValueError(f"Unknown challenge_id: {challenge_id}")

    challenge: SWEProChallenge = CHALLENGES[challenge_id]
    if model_name is None:
        model_name = get_default_model_for_tier(challenge.tier)

    print("\n" + "=" * 68)
    print(f"🚀 SWE VERIFIED PRO LIVE BENCHMARK: [{challenge.challenge_id}]")
    print(f"🎯 Tier {challenge.tier}: {challenge.title}")
    print(f"🤖 Model: {model_name} (Max budget: {max_calls} calls)")
    print(f"📋 Brief (Zero Hint):\n{challenge.brief}")
    print("=" * 68)

    api_key_res = load_api_key(ROOT)
    if not api_key_res.ok or not api_key_res.value:
        raise RuntimeError("OPENROUTER_API_KEY not found in environment or .env")

    model_adapter = OpenRouterModel(
        model=model_name,
        environ={"OPENROUTER_API_KEY": api_key_res.value},
        stream=False,
    )

    with tempfile.TemporaryDirectory(prefix=f"swe-pro-{challenge_id}-") as td:
        root_td = Path(td)
        repo = root_td / "workspace"
        repo.mkdir(parents=True, exist_ok=True)
        sealed_oracle_dir = root_td / "sealed_oracle"
        sealed_oracle_dir.mkdir(parents=True, exist_ok=True)

        # Write initial repository files (workspace ONLY contains project files)
        for rel_path, content in challenge.files.items():
            full_p = repo / rel_path
            full_p.parent.mkdir(parents=True, exist_ok=True)
            full_p.write_text(content, encoding="utf-8")

        # Write sealed test oracle outside workspace
        oracle_path = sealed_oracle_dir / "test_oracle.py"
        oracle_path.write_text(challenge.oracle_code, encoding="utf-8")

        # Initialize Git repo in workspace
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Vanguard Benchmark"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "benchmark@vanguard.dev"], cwd=repo, check=True)
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "initial state with bug"], cwd=repo, check=True)

        # Prove pre-repair fails closed
        test_env = {**os.environ, "PYTHONPATH": str(repo)}
        pre_test = subprocess.run(
            [sys.executable, str(oracle_path)],
            cwd=repo,
            env=test_env,
            capture_output=True,
            text=True,
        )
        pre_passed = (pre_test.returncode == 0)
        print(f"🔴 Pre-Repair Oracle Check: {'PASSED (Anomaly)' if pre_passed else 'FAILS CLOSED (Expected)'}")

        # Multi-turn interaction loop
        dialogue: list[dict[str, Any]] = []
        dialogue.append({
            "role": "user",
            "content": (
                f"You are an expert autonomous software engineer resolving an issue in a multi-file Python project.\n\n"
                f"Task Brief:\n{challenge.brief}\n\n"
                f"Repository layout:\n" + "\n".join(f"- {f}" for f in challenge.files) + "\n\n"
                f"CRITICAL INSTRUCTIONS:\n"
                f"1. You MUST call tools (`fs.read`, `fs.write`) using function calls to inspect and modify files.\n"
                f"2. Issue EXACTLY ONE tool call per response. Do NOT call multiple tools simultaneously.\n"
                f"3. When writing fixed files, use `fs.write` with the full corrected content.\n"
                f"4. Do NOT explain or talk in plain text until all files have been written.\n"
                f"5. Finish only AFTER you have written all corrected files."
            ),
        })

        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_cost_usd = 0.0
        llm_calls_made = 0
        turn_logs: list[dict[str, Any]] = []

        start_time = time.monotonic()

        while llm_calls_made < max_calls:
            llm_calls_made += 1
            print(f"\n--- Turn {llm_calls_made} [LLM Call #{llm_calls_made}/{max_calls}] ---")

            # Context bundle
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
                print(f"⚠️ Model proposal error: {res.error.message}")
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
                print(f"📊 Tokens: +{p_tok} prompt, +{c_tok} completion. Cumulative cost: ${total_cost_usd:.6f}")

            kind = val.get("kind") if isinstance(val, dict) else getattr(val, "kind", None)
            action = val.get("action") if isinstance(val, dict) else getattr(val, "action", None)
            args = val.get("args") if isinstance(val, dict) else getattr(val, "args", {})
            note = val.get("note") if isinstance(val, dict) else getattr(val, "note", "")

            # Fallback text parsing if model emits tool format in plaintext
            if action is None and note:
                import re
                m = re.search(r"Action:\s*([a-zA-Z0-9_.]+)\s*(?:Arguments|Args)?:\s*(\{.*\})", note, re.DOTALL)
                if m:
                    action = m.group(1).strip()
                    try:
                        args = json.loads(m.group(2).strip())
                        kind = "effect"
                    except Exception:
                        pass

            print(f"📥 Proposal: kind={kind}, action={action}, args={list(args.keys()) if isinstance(args, dict) else args}")

            turn_logs.append({
                "turn": llm_calls_made,
                "kind": kind,
                "action": action,
                "args": args,
                "note": note,
            })

            if kind == "finish" or action is None:
                print(f"✅ Agent completed interaction: {note}")
                break

            # Execute tool in repository
            tool_observation = ""
            if action == "fs.read":
                target_p = repo / args.get("path", "")
                if target_p.exists() and target_p.is_file():
                    tool_observation = target_p.read_text(encoding="utf-8")
                else:
                    tool_observation = f"File not found: {args.get('path')}"
                print(f"👁️ Read {args.get('path')} ({len(tool_observation)} chars)")

            elif action == "fs.write":
                target_p = repo / args.get("path", "")
                target_p.parent.mkdir(parents=True, exist_ok=True)
                content_to_write = args.get("content", "")
                target_p.write_text(content_to_write, encoding="utf-8")
                tool_observation = f"Successfully wrote {len(content_to_write)} bytes to {args.get('path')}"
                print(f"✏️ Wrote {args.get('path')} ({len(content_to_write)} bytes)")

            elif action == "proc.exec":
                argv = args.get("argv", [])
                if argv:
                    cmd_res = subprocess.run(argv, cwd=repo, capture_output=True, text=True)
                    tool_observation = f"Exit code {cmd_res.returncode}\nStdout:\n{cmd_res.stdout}\nStderr:\n{cmd_res.stderr}"
                    print(f"⚙️ Executed {argv} -> exit {cmd_res.returncode}")
                else:
                    tool_observation = "No argv specified"
            else:
                tool_observation = f"Unknown action {action}"

            # Feed observation back into dialogue for next turn
            dialogue.append({
                "role": "assistant",
                "content": f"Action: {action}\nArguments: {json.dumps(args)}",
            })
            dialogue.append({
                "role": "user",
                "content": f"Tool Result ({action}):\n{tool_observation}\n\nContinue fixing any remaining files or finish if done.",
            })

        duration = time.monotonic() - start_time

        # Capture git diff of agent changes
        diff_res = subprocess.run(["git", "diff"], cwd=repo, capture_output=True, text=True)
        patch_text = diff_res.stdout

        # Post-repair Exterior Oracle Test Execution
        post_test = subprocess.run(
            [sys.executable, str(oracle_path)],
            cwd=repo,
            env=test_env,
            capture_output=True,
            text=True,
        )
        post_passed = (post_test.returncode == 0)

        verdict_status = "PASSED" if post_passed else "FAILED"
        print("\n" + "=" * 68)
        print(f"🏁 FINAL VERDICT: [{verdict_status}]")
        print(f"📊 Oracle Test Status: Exit Code {post_test.returncode}")
        if not post_passed:
            print(f"❌ Oracle Failure Output:\n{post_test.stdout}\n{post_test.stderr}")
        print(f"⏱️ Duration: {duration:.2f}s")
        print(f"📞 LLM API Calls: {llm_calls_made}/{max_calls}")
        print(f"🪙 Total Tokens: {total_prompt_tokens + total_completion_tokens} ({total_prompt_tokens} prompt, {total_completion_tokens} completion)")
        print(f"💵 Total Spend: ${total_cost_usd:.6f} USD (Ceiling: $0.50)")
        print("=" * 68)

        result_summary = {
            "challenge_id": challenge.challenge_id,
            "tier": challenge.tier,
            "title": challenge.title,
            "model": model_name,
            "verdict": verdict_status,
            "oracle_passed": post_passed,
            "llm_calls": llm_calls_made,
            "max_calls": max_calls,
            "total_tokens": total_prompt_tokens + total_completion_tokens,
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "cost_usd": total_cost_usd,
            "duration_s": duration,
            "patch": patch_text,
            "turns": turn_logs,
        }

        # Save result artifact
        out_file = ROOT / "benchmarkings" / "swe_pro_tiers" / f"result_{challenge_id}.json"
        out_file.write_text(json.dumps(result_summary, indent=2), encoding="utf-8")
        print(f"💾 Result saved to {out_file.relative_to(ROOT)}\n")
        return result_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Live SWE Verified Pro Benchmark Challenge")
    parser.add_argument(
        "--challenge",
        default="tier1_lru_ttl_cache",
        choices=list(CHALLENGES.keys()),
        help="Challenge ID to execute",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model identifier (defaults to tier routing: Ollama qwen3.6 for Tier 1-2, openrouter/free for Tier 3, deepseek-v4-flash-0731 for Tier 4+)",
    )
    parser.add_argument(
        "--max-calls",
        type=int,
        default=30,
        help="Maximum LLM API call ceiling (default 30)",
    )
    args = parser.parse_args()

    res = run_live_challenge(args.challenge, model_name=args.model, max_calls=args.max_calls)
    return 0 if res["oracle_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
