# Unified Substrate Benchmarking Suite

This directory contains the 3 consolidated benchmark suites preserved for evaluating and validating the AETHER / Vanguard recursive-agency substrate:

---

## 1. Benchmark Suites

| # | Suite | Directory | Description & Purpose |
|---|---|---|---|
| **1** | **SWE / Bug-Fixing** | [`swe_bench/`](swe_bench/) | **Hermetic multi-tier bug repair.** Tests repository navigation, AST patching, running pytest in Bubblewrap sandbox (UID `10001`), and verifying regression tests. Fast, deterministic, and runnable offline with cassettes. |
| **2** | **Greenfield Project Synthesis** | [`greenfield/`](greenfield/) | **Fullstack and API construction from scratch.** Tests high-level decomposition, multi-turn file creation, setting up endpoints/schemas, and passing Exterior Evaluator test suites (UID `10002`). |
| **3** | **Frontier Algorithmic Engine** | [`datalog_engine/`](datalog_engine/) | **Deep logic & interpreter construction.** Tests complex state/parser construction (e.g., Datalog inference engine), multi-turn reasoning, and subagent delegation (`agent.spawn`) under typed budget bounds. |

---

## 2. Runners & Drivers

- [`run.py`](run.py) — Lightweight launcher delegating to the canonical runtime lab driver (`vanguard.packages.runtime.lab_driver`).
- [`bench.py`](bench.py) — Statistical evaluation and McNemar comparison across harness compositions.
- [`diff.py`](diff.py) — Trajectory and workspace diff inspector.
- [`build.py`](build.py) — Fixture and environment builder.

---

## 3. Usage Commands

```bash
# Run a specific benchmark task against a harness pack
python3 benchmarks/run.py --pack vg-code-default --task-dir benchmarks/greenfield/greenfield-api-html

# Compare statistical outcomes between two harness configurations
python3 benchmarks/bench.py --pack-a vg-code-default --pack-b vg-code-claude-shaped --db traces.sqlite
```

---

## 4. Benchmarking as Code (BaaC) Framework

The [`baac/`](baac/) framework provides declarative challenges with strict zero-state isolation, external non-leaked oracles, fail-closed budget guards ($0.10 cap, 300 requests cap), and root-cause attribution (Harness vs. LLM cognitive error).

```bash
# Verify zero-state manifests across all challenges
python3 -m benchmarks.baac.cli verify

# Run BaaC cycle (verify -> run -> oracle -> reset -> verify) in LAM mode ($0 cost)
python3 -m benchmarks.baac.cli cycle --mode lam --preset vg-1-forge

# Run BaaC benchmark against live OpenRouter models
python3 -m benchmarks.baac.cli run --mode live --preset vg-1-forge --tier easy
```

