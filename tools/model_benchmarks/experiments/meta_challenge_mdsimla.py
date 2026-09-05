#!/usr/bin/env python3
"""MDSIMLA: Meta Desafio Self Improvement Multi Local Agent
Uses local LLMs via the vg-code-explain harness paradigm:
1. Phase 1: Reasoning / Architect explains T-75 (LdaRepoIndex) & derives invariants.
2. Phase 2: Coding / Worker synthesizes the prototype adapter solution based on Phase 1.
Zero production code changes.
"""

import json
import os
import re
import subprocess
import time
import urllib.request
from pathlib import Path

LLAMA_SERVER = "/home/rock-dev/.local/bin/llama-server"
ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"
HEALTH_URL = "http://127.0.0.1:8080/health"
MODELS_DIR = Path("/home/rock-dev/Models")

def kill_server():
    subprocess.run(["pkill", "-9", "-f", "llama-server"], capture_output=True)
    time.sleep(1)

def start_server(model_file: str, context: int = 4096):
    kill_server()
    cmd = [
        LLAMA_SERVER,
        "-m", str(MODELS_DIR / model_file),
        "-c", str(context),
        "-ngl", "99",
        "--host", "127.0.0.1",
        "--port", "8080",
        "--alias", "local-model",
        "--reasoning", "off",
        "--jinja"
    ]
    print(f"\n[SERVER] Launching {model_file} (ctx={context})...", flush=True)
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    for _ in range(60):
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=1) as resp:
                if json.loads(resp.read().decode()).get("status") == "ok":
                    ready_time = time.time() - t0
                    print(f"[SERVER] Ready in {ready_time:.2f}s", flush=True)
                    return proc, ready_time
        except Exception:
            time.sleep(0.5)
            
    proc.kill()
    raise TimeoutError(f"Server {model_file} timed out")

def call_api(messages: list, max_tokens: int = 2048, temperature: float = 0.2):
    payload = {
        "model": "local-model",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=data_bytes, headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as resp:
        res = json.loads(resp.read().decode())
    dur = time.time() - t0
    return res, dur

# Load context from codebase: IndexPort, tasks T-75 specification, and sqlite schema
INDEX_PORT_CODE = """
class IndexPort(Protocol):
    def index(self, root: str) -> Result[int]: ...
    def files(self, *, prefix: str = "") -> Result[Sequence[str]]: ...
    def symbols(self, *, name: str = "", path: str = "") -> Result[Sequence[Symbol]]: ...
    def dependencies(self, *, path: str = "") -> Result[Sequence[DependencyEdge]]: ...
    def tests(self, *, path: str = "") -> Result[Sequence[TestAssociation]]: ...
    def repo_map(self, *, token_budget: int = 4000) -> Result[RepositoryMap]: ...
"""

T75_SPEC = """
T-75: LdaRepoIndex adapter (Package: IDX-01, subsystem: adapters)
- Goal: Implement the existing IndexPort structurally over `.lda/index.db`.
- Return value-only symbols, dependency edges, and test associations.
- Fail-closed: missing or stale indexes fail deterministically without a partial map (preserving T-45 fallback).
- Invariant: Ranking does NOT enter the port or adapter. Pure deterministic queries only.
- Boundaries: Adapters must NOT import kernel or agency.
"""

EXPLAIN_SYSTEM_PROMPT = """You are the official Vanguard codebase comprehension and explanation agent (`vg-code-explain`).
Analyze the codebase thoroughly and answer the user's architectural inquiry accurately.
Explain code structure, control flow, design decisions, invariants, and implementation strategy clearly with direct citations."""

REASONING_PROMPT = f"""[CONTEXT: NEXT BACKLOG TASK T-75 FROM docs/execution/tasks.md]
{T75_SPEC}

[PORT SPECIFICATION: vanguard/packages/ports/index.py]
{INDEX_PORT_CODE}

[TARGET DATABASE SCHEMA: .lda/index.db]
- `symbols`: (id, entity_id, name, qualified_name, kind, language, file_path, start_line, end_line)
- `relations`: (id, source_id, target_id, kind, confidence_tier, source_path) where kind IN ('calls', 'imports', 'tests')
- `index_runs`: (id, head_sha, timestamp)
- `files`: (id, path, size_bytes, last_modified)

[INQUIRY FOR vg-code-explain]
Explain how to design `LdaRepoIndex` to satisfy T-75 without breaking any Vanguard architectural law:
1. Explain the architectural role of `LdaRepoIndex` in the Hexagonal lattice.
2. Detail the exact SQL queries needed for `files()`, `symbols()`, `dependencies()`, and `tests()`.
3. Detail how to enforce the Fail-Closed invariant when `.lda/index.db` is missing or when `head_sha` differs from the current git revision.
4. Explain why ranking/heuristics are strictly forbidden in this adapter.
Provide a clear, structured design specification that a junior coder can translate into Python."""

def run_mdsimla():
    print("==================================================================")
    print("MDSIMLA: Meta Desafio Self Improvement Multi Local Agent")
    print("==================================================================")
    
    # PHASE 1: REASONING WITH 14B MODEL AS vg-code-explain
    print("\n--- PHASE 1: ARCHITECTURAL EXPLANATION (Qwen2.5-Coder-14B) ---")
    p1, warmup1 = start_server("Qwen2.5-Coder-14B-Instruct-Q4_K_M.gguf", context=4096)
    
    res1, dur1 = call_api([
        {"role": "system", "content": EXPLAIN_SYSTEM_PROMPT},
        {"role": "user", "content": REASONING_PROMPT}
    ], max_tokens=1500)
    
    explanation = res1["choices"][0]["message"]["content"]
    toks1 = res1["usage"]["completion_tokens"]
    speed1 = toks1 / dur1
    print(f"\n[PHASE 1 COMPLETE] Generated {toks1} tokens in {dur1:.2f}s ({speed1:.1f} tok/s)")
    kill_server()
    
    with open("tools/model_benchmarks/results/mdsimla_explanation.txt", "w") as f:
        f.write(explanation)
        
    print("\n=== EXPLANATION PREVIEW ===")
    print(explanation[:800] + "\n...")

    # PHASE 2: SYNTHESIS WITH WORKER MODEL (Qwen2.5-Coder-1.5B)
    print("\n--- PHASE 2: IMPLEMENTATION SYNTHESIS (Qwen2.5-Coder-1.5B) ---")
    p2, warmup2 = start_server("Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf", context=4096)
    
    WORKER_PROMPT = f"""[ARCHITECTURAL EXPLANATION FROM vg-code-explain]
{explanation}

[TASK]
Based on the architectural explanation above, write the clean, typed Python implementation of `LdaRepoIndex` implementing `IndexPort`.
Rules:
1. Zero external dependencies outside standard library (`sqlite3`, `pathlib`, `typing`, `dataclasses`).
2. Implement methods: `__init__`, `files()`, `symbols()`, `dependencies()`, `tests()`, and `_validate_freshness()`.
3. Return `Result.ok(...)` or `Result.failure(...)` following `IndexPort`.
4. Output only clean Python code in a ```python ... ``` block."""

    res2, dur2 = call_api([
        {"role": "system", "content": "You are a precise Python systems engineer. You implement architectural specifications faithfully."},
        {"role": "user", "content": WORKER_PROMPT}
    ], max_tokens=1500)
    
    code = res2["choices"][0]["message"]["content"]
    toks2 = res2["usage"]["completion_tokens"]
    speed2 = toks2 / dur2
    print(f"\n[PHASE 2 COMPLETE] Generated {toks2} tokens in {dur2:.2f}s ({speed2:.1f} tok/s)")
    kill_server()
    
    with open("tools/model_benchmarks/results/mdsimla_synthesis.py", "w") as f:
        f.write(code)
        
    print("\n=== SYNTHESIS CODE PREVIEW ===")
    print(code[:800] + "\n...")
    
    # Record telemetry
    summary = {
        "challenge": "MDSIMLA (Meta Desafio Self Improvement Multi Local Agent)",
        "target_task": "T-75: LdaRepoIndex adapter (IDX-01)",
        "harness": "vg-code-explain",
        "phase1_reasoning": {
            "model": "Qwen2.5-Coder-14B-Instruct",
            "time_sec": round(dur1, 2),
            "tokens": toks1,
            "speed_tok_s": round(speed1, 1),
            "output_file": "tools/model_benchmarks/results/mdsimla_explanation.txt"
        },
        "phase2_coding": {
            "model": "Qwen2.5-Coder-1.5B-Instruct",
            "time_sec": round(dur2, 2),
            "tokens": toks2,
            "speed_tok_s": round(speed2, 1),
            "output_file": "tools/model_benchmarks/results/mdsimla_synthesis.py"
        },
        "total_time_sec": round(dur1 + dur2, 2),
        "total_tokens": toks1 + toks2
    }
    with open("tools/model_benchmarks/results/mdsimla_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n==================================================================")
    print("MDSIMLA EXECUTION COMPLETED SUCCESSFULLY!")
    print(f"Total Latency: {summary['total_time_sec']}s | Total Tokens: {summary['total_tokens']}")
    print("Artifacts saved in tools/model_benchmarks/results/")
    print("==================================================================")

if __name__ == "__main__":
    run_mdsimla()
