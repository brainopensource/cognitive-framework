# Vanguard / AETHER v0.90 Frontier Benchmark Quick-Run Guide

**Primary Driver:** `tools/benchmark-drivers/frontier_v090.py`  
**Workspace Root:** `.vanguard/workspace` (configurable via `AETHER_WORKSPACE_ROOT`)  
**Target Model:** `deepseek/deepseek-v4-flash-0731` via OpenRouter  

---

## 1. Prerequisites & Environment Setup

The workspace root is auto-detected from `.vanguard/workspace.toml` and `OPENROUTER_API_KEY` is loaded automatically from the repo's `.env` — no manual setup required:

```bash
python3 tools/benchmark-drivers/frontier_v090.py --dry-run
```

`AETHER_WORKSPACE_ROOT` and `OPENROUTER_API_KEY` can still be set manually in the shell to override `.env` / config file.

---

## 2. Fast Diagnostic & Calibration Commands

### A. The 3 Failed Hard Benchmarks
Run the 3 Hard coding challenges that previously failed due to baseline or tool-call formatting:
```bash
python3 tools/benchmark-drivers/frontier_v090.py --row v090-03 v090-06 v090-09
```

### B. The 3 Failed Medium Benchmarks
Run the 3 Medium coding challenges (`tier2_event_bus`) to verify the calibrated wildcard/unsub logic:
```bash
python3 tools/benchmark-drivers/frontier_v090.py --row v090-02 v090-05 v090-08
```

### C. Regression Check on 2 Passing Easy Benchmarks
Re-run 2 Easy challenges (`tier1_lru_ttl_cache`) that previously passed, ensuring zero regressions:
```bash
python3 tools/benchmark-drivers/frontier_v090.py --row v090-01 v090-04
```

### D. Run One of Each Difficulty (Easy, Medium, Hard)
```bash
python3 tools/benchmark-drivers/frontier_v090.py --row v090-01 v090-02 v090-03
```

---

## 3. Filtered Batch Commands

### By Difficulty
```bash
# Run ALL 11 Easy benchmarks
python3 tools/benchmark-drivers/frontier_v090.py --difficulty Easy

# Run ALL 5 Medium benchmarks
python3 tools/benchmark-drivers/frontier_v090.py --difficulty Medium

# Run ALL 11 Hard benchmarks
python3 tools/benchmark-drivers/frontier_v090.py --difficulty Hard
```

### By Agent Class / Family
```bash
# Coding Family (15 rows: 5 Easy, 5 Medium, 5 Hard)
python3 tools/benchmark-drivers/frontier_v090.py --class-name Coding

# Tutor Family (4 rows: 2 Easy, 2 Hard)
python3 tools/benchmark-drivers/frontier_v090.py --class-name Tutor

# Research Family (4 rows: 2 Easy, 2 Hard)
python3 tools/benchmark-drivers/frontier_v090.py --class-name Research

# Bugfix Family (4 rows: 2 Easy, 2 Hard)
python3 tools/benchmark-drivers/frontier_v090.py --class-name Bugfix
```

### Full Matrix & Safety Runs
```bash
# Preregister / Freeze digests
python3 tools/benchmark-drivers/frontier_v090.py --preregister

# 27-row Deterministic Dry-Run (unpaid fake/cassette)
python3 tools/benchmark-drivers/frontier_v090.py --dry-run

# 2-row Live Sample
python3 tools/benchmark-drivers/frontier_v090.py --live-sample

# 3-row Live Canary
python3 tools/benchmark-drivers/frontier_v090.py --live-canary

# Full 27-row Live Benchmark Run
python3 tools/benchmark-drivers/frontier_v090.py --live-27
```

---

## 4. Master Table of All 27 Individual Rows

Run any single benchmark row on demand using `--row <id>`:

| Row ID | Class | Difficulty | Challenge Slot | Challenge ID | Preset Name | Individual Command |
|---|---|---|---|---|---|---|
| `v090-01` | Coding | Easy | `CODE-E` | `tier1_lru_ttl_cache` | `vg-code-v090-react-control` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-01` |
| `v090-02` | Coding | Medium | `CODE-M` | `tier2_event_bus` | `vg-code-v090-react-control` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-02` |
| `v090-03` | Coding | Hard | `CODE-H` | `tier3_token_bucket` | `vg-code-v090-react-control` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-03` |
| `v090-04` | Coding | Easy | `CODE-E` | `tier1_lru_ttl_cache` | `vg-code-v090-claude-shaped` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-04` |
| `v090-05` | Coding | Medium | `CODE-M` | `tier2_event_bus` | `vg-code-v090-claude-shaped` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-05` |
| `v090-06` | Coding | Hard | `CODE-H` | `tier3_token_bucket` | `vg-code-v090-claude-shaped` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-06` |
| `v090-07` | Coding | Easy | `CODE-E` | `tier1_lru_ttl_cache` | `vg-code-v090-opencode-shaped` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-07` |
| `v090-08` | Coding | Medium | `CODE-M` | `tier2_event_bus` | `vg-code-v090-opencode-shaped` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-08` |
| `v090-09` | Coding | Hard | `CODE-H` | `tier3_token_bucket` | `vg-code-v090-opencode-shaped` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-09` |
| `v090-10` | Coding | Easy | `CODE-E` | `tier1_lru_ttl_cache` | `vg-code-v090-lex-surgical` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-10` |
| `v090-11` | Coding | Medium | `CODE-M` | `tier2_event_bus` | `vg-code-v090-lex-surgical` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-11` |
| `v090-12` | Coding | Hard | `CODE-H` | `tier3_token_bucket` | `vg-code-v090-lex-surgical` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-12` |
| `v090-13` | Coding | Easy | `CODE-E` | `tier1_lru_ttl_cache` | `vg-code-v090-lim-falsifier` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-13` |
| `v090-14` | Coding | Medium | `CODE-M` | `tier2_event_bus` | `vg-code-v090-lim-falsifier` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-14` |
| `v090-15` | Coding | Hard | `CODE-H` | `tier3_token_bucket` | `vg-code-v090-lim-falsifier` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-15` |
| `v090-16` | Tutor | Easy | `TUTOR-E` | `tier1_lru_ttl_cache` | `vg-tutor-v090-v1-read-search` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-16` |
| `v090-17` | Tutor | Hard | `TUTOR-H` | `tier2_event_bus` | `vg-tutor-v090-v1-read-search` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-17` |
| `v090-18` | Tutor | Easy | `TUTOR-E` | `tier1_lru_ttl_cache` | `vg-tutor-v090-v2-evidence-graph` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-18` |
| `v090-19` | Tutor | Hard | `TUTOR-H` | `tier2_event_bus` | `vg-tutor-v090-v2-evidence-graph` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-19` |
| `v090-20` | Research | Easy | `RESEARCH-E` | `tier1_lru_ttl_cache` | `vg-research-v090-v1-local` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-20` |
| `v090-21` | Research | Hard | `RESEARCH-H` | `tier2_event_bus` | `vg-research-v090-v1-local` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-21` |
| `v090-22` | Research | Easy | `RESEARCH-E` | `tier1_lru_ttl_cache` | `vg-research-v090-v2-web-corroborated` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-22` |
| `v090-23` | Research | Hard | `RESEARCH-H` | `tier2_event_bus` | `vg-research-v090-v2-web-corroborated` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-23` |
| `v090-24` | Bugfix | Easy | `BUG-E` | `tier1_lru_ttl_cache` | `vg-bugfix-v090-v1-direct` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-24` |
| `v090-25` | Bugfix | Hard | `BUG-H` | `tier2_event_bus` | `vg-bugfix-v090-v1-direct` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-25` |
| `v090-26` | Bugfix | Easy | `BUG-E` | `tier1_lru_ttl_cache` | `vg-bugfix-v090-v2-reproduce-verify` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-26` |
| `v090-27` | Bugfix | Hard | `BUG-H` | `tier2_event_bus` | `vg-bugfix-v090-v2-reproduce-verify` | `python3 tools/benchmark-drivers/frontier_v090.py --row v090-27` |

---

## 5. Direct Custom Challenge Execution

Run any arbitrary SWE challenge against any preset directly:

```bash
# Run DAG Resolver (Tier 4) with react-control preset
python3 tools/benchmark-drivers/frontier_v090.py --challenge tier4_dag_resolver --preset vg-code-v090-react-control

# Run Token Bucket (Tier 3) with claude-shaped preset
python3 tools/benchmark-drivers/frontier_v090.py --challenge tier3_token_bucket --preset vg-code-v090-claude-shaped
```

---

## 6. Deterministic Mock Benchmarks (LAM: LLM API Mock)

To decouple **agent & harness execution time** from **external LLM network round-trips**, use the LAM simulation testbed (`tools/002_LLM_API_MOCK`):

```bash
# Run isolated fast simulation of a single scenario (e.g. calculator formula bug)
python3 -c "import sys; sys.path.insert(0, 'tools/002_LLM_API_MOCK'); from simulate import simulate_scenario; print(simulate_scenario('t1-calculator'))"

# Run LAM IQ cross-validation suite (Tiers 0 to 5)
python3 tools/002_LLM_API_MOCK/cross_validate_iq.py

# Run full cross-tier simulation benchmark
python3 tools/002_LLM_API_MOCK/benchmark_tiers_0_to_10.py
```