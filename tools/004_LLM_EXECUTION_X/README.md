# LEX — Local Execution X-engine (Autonomous Coding Swarm)

> **Tier S+ Autonomous Multi-Model Coding Swarm & Evidentiary Synthesis Engine**  
> *Zero-Cloud Dependency • Sub-25s End-to-End Latency • Mutation-Verified Code • Hardware-Aware VRAM Scheduling*

---

## 1. Overview

**LEX** (*Local Execution X-engine*) is a high-performance, local multi-model agentic coding framework. It coordinates a tiered swarm of specialized open-weights models (**Qwen 2.5 1.5B Router**, **Qwen 3.8 27B / Qwen3-Coder 30B MoE Architect**, and **Qwen 2.5 Coder 14B Workers**) running locally on Ollama/vLLM.

LEX treats code generation not as a conversational prompt, but as a **formal compiler pipeline** with:
- **`TaskGraph IR`** semantic contracts.
- **3-Tier Rootless Sandboxing** (Bubblewrap / User Namespaces).
- **Multi-Operator Mutation Testing** to eliminate test-code collusion.
- **Diagnosis-Driven Self-Healing** with state-hash anti-thrashing circuit breakers.
- **Symmetric Wire Protocols** exposing an **MCP Tool Server** returning cryptographically verifiable `AgentExecutionEnvelope`s.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             LEX SWARM TOPOLOGY                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [User Request] ──► [L0: Context RAG] ──► [L1: 1.5B Router]                │
│                                                  │                          │
│                                            (Needs Plan)                     │
│                                                  ▼                          │
│                                     [L2: 27B/30B Architect]                 │
│                                                  │                          │
│                                       (Emits TaskGraph IR)                  │
│                                                  ▼                          │
│                                     [VRAM Drain Polling Probe]              │
│                                                  ▼                          │
│                          ┌───────────────────────┴───────────────────────┐  │
│                          ▼                                               ▼  │
│               [L3A: Worker Coder (14B)]                       [L3B: Worker Tester (14B)]
│                          │                                               │  │
│                          └───────────────────────┬───────────────────────┘  │
│                                                  ▼                          │
│                                   [L4: 3-Tier Rootless Sandbox]             │
│                                   • AST Syntax & Import Audit               │
│                                   • Ruff Strict Linter                      │
│                                   • Multi-Operator Mutation Probe           │
│                                   • Sandboxed Pytest Suite                  │
│                                                  ▼                          │
│                                     [VerificationPolicy Engine]             │
│                                       /                     \               │
│                                 (PASS)                       (FAIL)         │
│                                   ▼                             ▼           │
│                     [AgentExecutionEnvelope]         [Semantic Diagnostician]│
│                     [Signed ExecutionReceipt]        [Surgical Repair Loop] │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Documentation Architecture

All project documentation lives in [`docs/`](docs/):

| Document | Purpose & Scope |
|:---|:---|
| [`docs/PRD.md`](docs/PRD.md) | **Product Requirements Document:** Vision, personas, user stories, SLOs, market moat, and product governance. |
| [`docs/SPEC.md`](docs/SPEC.md) | **Normative Technical Specification:** RFC-2119 requirements, schemas, mathematical invariants, error taxonomy. |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | **Macro Roadmap & Milestones:** Sprints 0–9, phase gates, complexity points, exit criteria, risk matrix. |
| [`docs/BACKLOG.md`](docs/BACKLOG.md) | **Sprint Task Register:** Epics, granular task IDs, acceptance criteria, and Definition of Done. |
| [`docs/dev_plan.md`](docs/dev_plan.md) | **Execution Plan & Implementation Guide:** Sprint 1 thin vertical slice, architecture lattice, config reference. |
| [`docs/dev_plan_review.md`](docs/dev_plan_review.md) | **Architectural Masterclass & Whitepaper:** Long-term theoretical foundation, math proofs, benchmark catalogs. |

---

## 3. Quickstart & Developer Workflow

### Prerequisites
- **OS:** Linux / WSL2 Ubuntu 24.04 LTS
- **Rust Toolchain:** `rustc` & `cargo` >= 1.75
- **Local Ollama Daemon:** `http://127.0.0.1:11434`
- **GPU:** AMD Radeon (16GB–24GB VRAM) with ROCm / NVIDIA GeForce (16GB–24GB VRAM)

```bash
# 1. Pull verified local model weights
ollama pull qwen2.5:1.5b
ollama pull qwen3.8:27b
ollama pull qwen2.5-coder:14b

# 2. Run hermetic Rust test suite (Zero GPU / Zero Network required)
cargo test

# 3. Build optimized release binary
cargo build --release

# 4. Execute interactive code synthesis via compiled binary
./target/release/lex "Create an async TokenBucket rate limiter with Redis backend"

# 5. Start the native MCP JSON-RPC tool server
./target/release/lex --mcp-stdio
```

---

## 4. Architectural Invariants

1. **Pure Rust Hexagonal Crate:** `domain ← ports ← engine → adapters`. No domain or engine references to adapters.
2. **Separation of Evidence and Verdict:** Validadores produzem dados (`Evidence`); apenas a `VerificationPolicy` emite o veredito.
3. **Fail-Closed Sandbox:** Código não confiável gerado por IA nunca é executado in-process. Se o sandbox isolado não estiver disponível, cai para análise estática.
4. **Active VRAM Drain:** Antes de carregar os workers de 14B, o adaptador de Ollama faz polling ativo até `size_vram == 0` no modelo de 27B.
5. **Universal Wire Contract:** Toda saída emite o `AgentExecutionEnvelope` estruturado com digests SHA-256 e contabilidade real de tokens.
