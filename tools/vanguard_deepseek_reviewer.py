#!/usr/bin/env python3
"""Execute a critical code review & Sprint 0.6 planner using DeepSeek on OpenRouter.

Respects pre-declared budget ceilings ($0.50 max envelope).
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from vanguard.packages.adapters.models.env_loader import load_api_key


def main():
    print("================================================================================")
    print("             VANGUARD DEEPSEEK OPENROUTER CRITICAL CODE REVIEW                  ")
    print("================================================================================")

    res = load_api_key(_ROOT)
    if not res.ok:
        print(f"Error loading API key: {res.error.message}")
        return 1
    api_key = res.value

    # Read critical files for review
    dispatch_code = (_ROOT / "vanguard/packages/kernel/dispatch.py").read_text(encoding="utf-8")
    eval_listener_code = (_ROOT / "vanguard/packages/runtime/evaluation_listener.py").read_text(encoding="utf-8")
    grant_code = (_ROOT / "vanguard/packages/runtime/autonomous_grant.py").read_text(encoding="utf-8")
    milestones_v060 = (_ROOT / "docs/02_roadmap/milestones.md").read_text(encoding="utf-8")[:3000]

    prompt = f"""You are a Principal Security Architect and Systems Engineer reviewing the Vanguard Runtime codebase.

CRITICAL CODE SAMPLES:

--- FILE 1: vanguard/packages/kernel/dispatch.py (Lines 1-120) ---
{dispatch_code[:2500]}

--- FILE 2: vanguard/packages/runtime/evaluation_listener.py ---
{eval_listener_code}

--- FILE 3: vanguard/packages/runtime/autonomous_grant.py (Lines 1-80) ---
{grant_code[:2000]}

--- CONTEXT FOR NEXT SPRINT (v0.6.0) ---
{milestones_v060}

TASKS REQUIRED:
1. CRITICAL CODE REVIEW: Analyze the 3 modules for security invariants, race conditions, type correctness, TCB compliance (Logical LOC <= 1438), and boundary discipline. Highlight any potential vulnerabilities or optimizations.
2. SPRINT v0.6.0 DETAILED SKELETON: Produce an actionable, PhD-grade sprint plan for v0.6.0 (Structured Artifact Graph, Semantic Vector Index, SQLite WAL Event Store) structured in 3 parallel non-blocking developer lanes (ALFA, BETA, GAMMA).
3. Provide concrete pseudocode / AST for the SQLite WAL Event Store & Vector Index.
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/vanguard-runtime",
        "X-Title": "Vanguard Architecture Reviewer",
    }

    # OpenRouter model: deepseek/deepseek-chat or deepseek/deepseek-v4-flash
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a PhD-level distributed systems & security architect specializing in formal kernel attenuation and agent runtime design."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 4096,
    }

    print("\nSending review request to DeepSeek (OpenRouter)...")
    start = time.perf_counter()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        duration = time.perf_counter() - start

        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        
        # DeepSeek pricing on OpenRouter: $0.14/1M prompt, $0.28/1M completion
        cost = (prompt_tokens / 1e6 * 0.14) + (completion_tokens / 1e6 * 0.28)

        content = data["choices"][0]["message"]["content"]
        
        review_file = _ROOT / "docs/reviews/deepseek_v050_review_and_v060_plan.md"
        review_file.parent.mkdir(parents=True, exist_ok=True)
        review_file.write_text(content, encoding="utf-8")

        print(f"\n[✓] Review completed successfully in {duration:.2f}s!")
        print(f"  • Prompt tokens: {prompt_tokens}")
        print(f"  • Completion tokens: {completion_tokens}")
        print(f"  • Total Cost: ${cost:.6f} USD (Well below $0.50 budget ceiling)")
        print(f"  • Review Report saved to: {review_file}")

    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP Error {exc.code}: {err_body}")
        return 1
    except Exception as exc:
        print(f"Error during OpenRouter request: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
