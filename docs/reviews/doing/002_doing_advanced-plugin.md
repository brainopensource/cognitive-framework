---
id: REV-PLUGIN-002
file: docs/reviews/doing/002_doing_advanced-plugin.md
title: "Modular Plug-in Adapter Architecture for Local LLMs & Small-Model Economy Governance"
version: 1.0.0
status: DOING / DESIGN-PROPOSAL
authority_scope: >
  Decoupled local model adapter design (Ollama, Qwen2.5, DeepSeek-R1), local prompt engineering,
  multi-action proposal unpacking, heuristic context pre-search, and economic budget measurement
  within Vanguard's Hexagonal Architecture (v0.6.0+ Molecular Lattice alignment).
owners: [Project Lead, Tech Lead]
last_reviewed: 2026-08-18
---

# 002_doing_advanced-plugin: Modular Plug-in Adapter Architecture for Local LLMs

> *"Vanguard's core kernel (`vanguard/packages/kernel/`) must remain pure, minimal (≤ 1438 LOC), and strictly decoupled from model-specific quirks. Small local models require specialized pre-processing, output parsing, and turn-budget governance. These capabilities belong in decoupled adapters and plug-ins, preserving a DRY, reusable framework."*

---

## 1. Executive Summary & Problem Context

Empirical evaluation of local open-weights models (`qwen2.5:1.5b` and `deepseek-r1:14b` via Ollama) against Vanguard's harness revealed specific failure modes under standard single-turn contracts:

1. **Multi-Action Proposal Collisions (`instrument_error:multi_action_proposal`)**: Small models often emit multiple tool actions (e.g. `fs.read` + `patch.apply`) in a single response turn. Vanguard's strict single-effect law (`I-05`, `A-01`) rejects multi-action proposals at the `ProposalTranslator` level.
2. **Formatting & Chain-of-Thought Interference**: Reasoning models like `deepseek-r1` emit extensive `<think>...</think>` tags or raw JSON blocks without markdown wrappers, confusing strict tool parsers or exhausting turn token windows.
3. **Turn Budget & Latency Drift**: Local models incur significant per-turn latency or get stuck in repetitive loops without heuristic guidance.

### Architectural Solution
Rather than hardcoding workarounds into the TCB or core runtime, Vanguard will employ a **Modular Plug-in Adapter Architecture** (aligned with **v0.6.0 Molecular Lattice** and **ADR-0059/0060**). Small-model support is encapsulated in optional, pluggable middleware layers.

---

## 2. Decoupled Hexagonal Topology

Under Vanguard's Hexagonal Architecture, core domain contracts and kernel attenuation logic remain completely untouched.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          VANGUARD CORE KERNEL                               │
│            (Kernel.dispatch, Attenuation Policies, S1(e) Spans)            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ▲
                                      │  `ModelPort` Interface Contract
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       LOCAL MODEL PLUGIN ADAPTER                            │
│           (`vanguard/packages/adapters/models/local_plugin.py`)           │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────┐  ┌─────────────────────┐  ┌───────────────────┐  │
│  │   Pre-Processor       │  │ Output Unpacker /   │  │ Economy & Budget  │  │
│  │ - Heuristic Search    │  │   Regex Parser      │  │   Governance      │  │
│  │ - AST RepoMap Pruning │  │ - Multi-Action Split│  │ - Token/Time Caps │  │
│  │ - Few-Shot Tooling    │  │ - Think Tag Stripper│  │ - Failure Retry   │  │
│  └───────────────────────┘  └─────────────────────┘  └───────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ▲
                                      │ REST / UDS (JSON API)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       LOCAL OLLAMA DAEMON                                   │
│            (`qwen2.5:1.5b`, `qwen3.6:27b`, `deepseek-r1:14b`)              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Plug-in Components

### 3.1 Proposal Unpacker & Action Queue (`MultiActionUnpacker`)
* **Purpose**: Convert multi-action LLM responses into single-effect kernel turns without failing the episode.
* **Mechanism**: When an LLM returns an array of tool calls `[action_1, action_2]`, the unpacker converts `action_1` into the current turn's proposal and enqueues `action_2` into an ephemeral adapter queue for immediate execution on subsequent turns.
* **Invariant Compliance**: The kernel continues to execute exactly one effect per turn (`I-05`).

### 3.2 Regex & Local Formatting Parser (`LocalFormatSanitizer`)
* **Purpose**: Parse non-standard outputs from small or reasoning LLMs.
* **Capabilities**:
  * Strips `<think>...</think>` XML blocks from reasoning models before tool parsing.
  * Extracts JSON schemas embedded in freeform prose via strict regex fallback matchers.
  * Normalizes parameter key aliases (e.g. `path` -> `filepath`).

### 3.3 Heuristic Pre-Search & AST Context Compiler (`HeuristicPrePass`)
* **Purpose**: Maximize small context window utility (e.g., 4k–8k tokens).
* **Capabilities**:
  * Runs fast deterministic heuristics (`ripgrep`, Python `ast` symbol lookup) prior to model invocation.
  * Pre-prunes workspace file trees into minimal relevant snippets (`AST RepoMap`).
  * Injects precise few-shot examples matching the task's declared domain.

### 3.4 Economy & Governance Controller (`EconomyControl`)
* **Purpose**: Monitor and limit local compute consumption without relying on cloud micro-dollar meters.
* **Parameters**:
  ```python
  @dataclass(frozen=True, slots=True)
  class LocalEconomyRules:
      max_turns: int = 12
      max_attempts: int = 4
      max_seconds_per_turn: float = 180.0
      max_total_seconds: float = 600.0
      allow_action_unpacking: bool = True
      strip_reasoning_tags: bool = True
      heuristic_prepass: bool = True
  ```
* **Ledger Recording**: All economy metrics (unpacked actions count, reasoning time, local token throughput) are emitted into the event ledger \(L\) as labelled telemetry.

---

## 4. Integration Roadmap & Future Evolution

### Phase 1: Local Plugin Prototype (v0.5.0 / S-product)
* Implement `LocalModelAdapter` as an experimental adapter in `vanguard/packages/adapters/models/local_plugin.py`.
* Register `--model local-plugin` CLI choice in `lab_driver.py` / `model_selection.py`.
* Validate on safe local dogfood tasks with `qwen2.5`.

### Phase 2: Modular Hexagonal Decoupling (v0.6.0 Molecular Lattice)
* Move local formatting rules, action unpackers, and heuristics into standalone, composable plugins.
* Ensure zero dependency leaks: `vanguard/packages/kernel/` and `vanguard/packages/domain/` remain completely unaware of local model quirks.

### Phase 3: Cognitive Operator Integration (v0.9.0 Tribal Swarm)
* Promote effective heuristic + local model combinations into formal **Cognitive Operators** (`Operators as Data`, `A-02`).
* Allow System 1 / System 2 dynamic routing where small local models handle habitual/observation turns while cloud models handle complex multi-file architectural turns.

---

## 5. Summary Matrix: Architecture Invariants

| Governance Metric | Standard Harness | Local Plug-in Adapter |
| :--- | :--- | :--- |
| **Kernel Size Impact** | 0 LOC added to `kernel/` | 0 LOC added to `kernel/` |
| **Turn Execution Law** | 1 Effect / Turn (`I-05`) | 1 Effect / Turn (Unpacker queues extra actions) |
| **Provenance Tracking** | Span `UNTRUSTED_EXTERNAL` | Span `UNTRUSTED_EXTERNAL` |
| **Model Selection** | `--model openrouter` | `--model local-plugin --model-name qwen2.5:1.5b` |
| **Resource Control** | USD Microdollars | `LocalEconomyRules` (Turn time, tokens, attempt caps) |

---

*Document created under `docs/reviews/doing/002_doing_advanced-plugin.md`. Aligned with Vanguard System Spec v3.0.0 and Milestone ROAD-MILE-01.*
