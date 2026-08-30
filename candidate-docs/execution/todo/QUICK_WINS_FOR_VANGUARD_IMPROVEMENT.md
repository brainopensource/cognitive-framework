# SOTA Autonomous Coding Agent Harnesses & CLI Product Architecture Blueprint

```text
====================================================================================================
AETHER / VANGUARD FRONTIER AGENTIC CODING HARNESS & SUBSTRATE SPECIFICATION
Document ID: QUICK_WINS_FOR_VANGUARD_IMPROVEMENT.md
Class: Engineering Specification & SOTA Architectural Compendium
Status: Active Working Law (Root Reference)
Authority: Execution & Architectural Synthesis
Version: 1.0.0
Author: Principal Systems Architect & Autonomous Agentic Harness Lead
Scope: Vanguard Framework Evolution, Cordis Microkernel Integration, Claude Code Ergonomics,
       Cross-Substrate Synergies (LEX & LIM), SOTA Verification Algorithms & Frontier CLI Suite
====================================================================================================
```

---

## Table of Contents

1. [Executive Summary & Architectural Synthesis](#1-executive-summary--architectural-synthesis)
2. [Critical Review of Vanguard Benchmarking & Quick Wins](#2-critical-review-of-vanguard-benchmarking--quick-wins)
   - 2.1 [The 27-Measurement Matrix Analysis](#21-the-27-measurement-matrix-analysis)
   - 2.2 [Evaluation of the 12 Quick Wins (QW-01 to QW-12)](#22-evaluation-of-the-12-quick-wins-qw-01-to-qw-12)
3. [The Tri-Substrate Ecosystem: Deep Architectural Audit](#3-the-tri-substrate-ecosystem-deep-architectural-audit)
   - 3.1 [Vanguard (Aether-D-System): The TCB Trust & Governance Kernel](#31-vanguard-aether-d-system-the-tcb-trust--governance-kernel)
   - 3.2 [LEX (LEX_LLM_EXECUTION): The Ultra-Low-Latency Rust Swarm](#32-lex-lex_llm_execution-the-ultra-low-latency-rust-swarm)
   - 3.3 [LIM (LIM_LLM_INT_MACHINE): Formal Verification, SBFL & CEGIS](#33-lim-lim_llm_int_machine-formal-verification-sbfl--cegis)
   - 3.4 [Cross-Substrate Capability Matrix](#34-cross-substrate-capability-matrix)
4. [Frontier Industry & Academic Literature Deep-Dive](#4-frontier-industry--academic-literature-deep-dive)
   - 4.1 [DeepSeek Harness (dsh / Cordis): Microkernel & Event Log as Truth](#41-deepseek-harness-dsh--cordis-microkernel--event-log-as-truth)
   - 4.2 [Claude Code Architecture: Asymmetric Determinism & Prefix Caching](#42-claude-code-architecture-asymmetric-determinism--prefix-caching)
   - 4.3 [SOTA Autonomous Coding Harness Algorithms](#43-sota-autonomous-coding-harness-algorithms)
5. [Comprehensive Framework Improvement Blueprint for Autonomous CLIs](#5-comprehensive-framework-improvement-blueprint-for-autonomous-clis)
   - 5.1 [Pillar 1: Pluggable AgentLoop Microkernel (Cordis Pattern)](#51-pillar-1-pluggable-agentloop-microkernel-cordis-pattern)
   - 5.2 [Pillar 2: Append-Only SessionEvent Store & Pure Context Projections](#52-pillar-2-append-only-sessionevent-store--pure-context-projections)
   - 5.3 [Pillar 3: Stateful Interactive PTY ShellPort](#53-pillar-3-stateful-interactive-pty-shellport)
   - 5.4 [Pillar 4: Instantaneous AST Syntax Pre-Flight Gates (<0.2ms)](#54-pillar-4-instantaneous-ast-syntax-pre-flight-gates-02ms)
   - 5.5 [Pillar 5: SBFL Fault Localization & AST PageRank via IndexPort](#55-pillar-5-sbfl-fault-localization--ast-pagerank-via-indexport)
   - 5.6 [Pillar 6: Speculative Git Checkpoint Engine & Worktree Sandboxing](#56-pillar-6-speculative-git-checkpoint-engine--worktree-sandboxing)
   - 5.7 [Pillar 7: AST Mutation Verification & Anti-Collusion Engine](#57-pillar-7-ast-mutation-verification--anti-collusion-engine)
   - 5.8 [Pillar 8: Deterministic Anti-Thrashing State-Hash FSM](#58-pillar-8-deterministic-anti-thrashing-state-hash-fsm)
   - 5.9 [Pillar 9: Radix L1–L5 Prefix Cache Alignment & Structured Compactor](#59-pillar-9-radix-l1l5-prefix-cache-alignment--structured-compactor)
   - 5.10 [Pillar 10: Cryptographic Identity Envelope & Telemetry Dashboard](#510-pillar-10-cryptographic-identity-envelope--telemetry-dashboard)
6. [Next-Generation Agent Coding CLIs & Product Families](#6-next-generation-agent-coding-clis--product-families)
   - 6.1 [CLI 1: vg-code (Autonomous SWE-Bench Solver)](#61-cli-1-vg-code-autonomous-swe-bench-solver)
   - 6.2 [CLI 2: vg-swarm (Tiered Multi-Model Coding Swarm)](#62-cli-2-vg-swarm-tiered-multi-model-coding-swarm)
   - 6.3 [CLI 3: vg-verifier / vg-fuzz (Formal CEGIS & SMT Synthesis)](#63-cli-3-vg-verifier--vg-fuzz-formal-cegis--smt-synthesis)
   - 6.4 [CLI 4: vg-refactor (Causal Slicing & Large-Scale Modernizer)](#64-cli-4-vg-refactor-causal-slicing--large-scale-modernizer)
   - 6.5 [CLI 5: vg-review / vg-arena (Adversarial Multi-Model PR Adjudicator)](#65-cli-5-vg-review--vg-arena-adversarial-multi-model-pr-adjudicator)
   - 6.6 [CLI 6: vg-tutor (Evidence-Graph Interactive Codebase Guide)](#66-cli-6-vg-tutor-evidence-graph-interactive-codebase-guide)
   - 6.7 [CLI 7: vg-research (Bounded Technical RFC & Web Corroborator)](#67-cli-7-vg-research-bounded-technical-rfc--web-corroborator)
   - 6.8 [CLI 8: vg-rlvr (Verifiable Trajectory & Dataset Generator)](#68-cli-8-vg-rlvr-verifiable-trajectory--dataset-generator)
7. [Implementation Roadmap, Risk Matrix & Skunkworks Validation](#7-implementation-roadmap-risk-matrix--skunkworks-validation)
8. [Conclusion & Strategic Vision](#8-conclusion--strategic-vision)

---

## 1. Executive Summary & Architectural Synthesis

The frontier of agentic software engineering has transitioned from open-ended conversational assistants to **deterministic, compiler-grade execution harnesses**. In these modern architectures, the language model operates as an isolated cognitive reasoning engine inside an unyielding, mathematically formal systems harness.

This document unifies three major independent systems into a coherent blueprint:
1. **AETHER / Vanguard** (Current Repository): A hexagonal, provably sound Trusted Computing Base (TCB) with strict boundary isolation, 13-stage dispatch safety (), typed budget algebra, and Ed25519-signed verdict verification.
2. **LEX (Local Execution X-engine)**: A high-performance, air-gapped Rust coding swarm featuring 3-tier rootless Bubblewrap sandboxing, hardware-aware VRAM drain scheduling, multi-operator mutation testing, and symmetric MCP wire contracts.
3. **LIM (LLM Intelligence Machine)**: A formal verification and algorithmic problem-solving engine featuring Spectrum-Based Fault Localization (SBFL Ochiai), Counterexample-Guided Inductive Synthesis (CEGIS), concolic path fuzzing, and speculative Monte Carlo Tree Search (MCTS).

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE TRI-SUBSTRATE AGENTIC CODING ECOSYSTEM                             │
├───────────────────────────────────┬──────────────────────────────────┬─────────────────────────────────┤
│    AETHER / VANGUARD (Python)     │           LEX (Rust)             │           LIM (Python)          │
├───────────────────────────────────┼──────────────────────────────────┼─────────────────────────────────┤
│ • Pure Hexagonal TCB Microkernel  │ • Zero-Cloud Autonomous Swarm    │ • Formal Verification & CEGIS   │
│ • S0–S12 Monotonic Dispatch Pipe  │ • 3-Tier Rootless Bubblewrap SB  │ • SBFL (Ochiai/Tarantula/DStar) │
│ • L1–L5 Prefix Context Compiler   │ • Multi-Operator Mutation Engine │ • Concolic & Invariant Fuzzers  │
│ • Append-only SQLite WAL Ledger   │ • State-Hash Anti-Thrashing FSM  │ • Speculative MCTS Git Rollback │
│ • Ed25519 Signed Verifiable Oracles│ • Anthropic Cache_Control Marker │ • 18+ Config Ablation Matrix    │
└───────────────────────────────────┴──────────────────────────────────┴─────────────────────────────────┘
                                                    │
                                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                        UNIFIED SOTA CODING HARNESS ARCHITECTURE (TARGET EVOLUTION)                     │
│   Event Sourcing Stream ──► Pluggable AgentLoop ──► L1-L5 Radix Cache ──► Formal Gate ──► Telemetry   │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

By cross-pollinating the **Cordis egalitarian microkernel ("all is a plugin")**, the **append-only event store as single source of truth**, **Claude Code's prefix-caching ergonomics**, and **LIM's SBFL/CEGIS formal verification**, Vanguard can scale into the definitive operating system for autonomous coding CLIs.

---

## 2. Critical Review of Vanguard Benchmarking & Quick Wins

### 2.1 The 27-Measurement Matrix Analysis

The Vanguard v0.9 benchmarking program ([](file:///home/rocha/Coding/Aether-D-System/BENCHMARK_V090_FULL.MD)) formalizes a strict, scientific evaluation across 11 presets and 27 planned measurements.

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                      27-ROW BENCHMARK MATRIX TAXONOMY                                  │
├───────────┬──────────────────────────────────────────┬─────────────────────────────┬───────────────────┤
│ Category  │ Preset / Manifest ID                     │ Difficulties Evaluated      │ Rows Allocation   │
├───────────┼──────────────────────────────────────────┼─────────────────────────────┼───────────────────┤
│ Coding    │ vg-code-v090-react-control               │ Easy, Medium, Hard          │ 3 rows (01–03)    │
│ Coding    │ vg-code-v090-claude-shaped               │ Easy, Medium, Hard          │ 3 rows (04–06)    │
│ Coding    │ vg-code-v090-opencode-shaped             │ Easy, Medium, Hard          │ 3 rows (07–09)    │
│ Coding    │ vg-code-v090-lex-surgical                │ Easy, Medium, Hard          │ 3 rows (10–12)    │
│ Coding    │ vg-code-v090-lim-falsifier               │ Easy, Medium, Hard          │ 3 rows (13–15)    │
│ Tutor     │ vg-tutor-v090-v1-read-search (Direct)    │ Easy, Hard                  │ 2 rows (16–17)    │
│ Tutor     │ vg-tutor-v090-v2-evidence-graph (SOTA)   │ Easy, Hard                  │ 2 rows (18–19)    │
│ Research  │ vg-research-v090-v1-local (Direct)       │ Easy, Hard                  │ 2 rows (20–21)    │
│ Research  │ vg-research-v090-v2-web-corroborated     │ Easy, Hard                  │ 2 rows (22–23)    │
│ Bugfix    │ vg-bugfix-v090-v1-direct (Direct)        │ Easy, Hard                  │ 2 rows (24–25)    │
│ Bugfix    │ vg-bugfix-v090-v2-reproduce-verify       │ Easy, Hard                  │ 2 rows (26–27)    │
└───────────┴──────────────────────────────────────────┴─────────────────────────────┴───────────────────┘
```

#### Core Experimental Constraints:
- **Locked Model**:  via OpenRouter.
- **Budget Envelopes**: Global hard ceiling of 1,000,000 tokens and bash.50 USD.
- **Strict Freezing**: Zero framework mutation permitted during evaluation; frozen paths verified by canonical SHA-256 digests.

### 2.2 Evaluation of the 12 Quick Wins (QW-01 to QW-12)

The findings in [](file:///home/rocha/Coding/Aether-D-System/QUICK_WINS_FOR_FRAMEWORK_IMPROVEMENT.MD) highlight critical practical bottlenecks at the intersection of substrate and frontier products:

| ID | Title & Focus | Technical Diagnostic | Solution Architecture |
|:---|:---|:---|:---|
| **QW-01** | Pack-Selectable Benchmark Entrypoint | Dual execution paths between benchmark runners and runtime lab. | Unify behind . |
| **QW-02** | Synthetic Evidence Elimination | Risk of synthetic mock metrics contaminating empirical records. | Separate  from . |
| **QW-03** | Composable Web Research Capability | Research presets lack outbound search/fetch tools. | Implement  &  adapters under existing ports with SSRF guards. |
| **QW-04** | IndexPort-Backed Code Intelligence | Large contexts exhaust token budget during lexical grep search. | Expose tree-sitter AST symbol maps and call chains through . |
| **QW-05** | DeepSeek Protocol Normalization | Malformed tool-call JSON/XML crashes the execution loop. | Provider-specific stream normalizer in adapter boundary before proposal parsing. |
| **QW-06** | Approval-Loop Efficiency | Agent wastes turns negotiating approvals with the governance engine. | Pre-authorized signed execution grants for workspace-scoped test commands. |
| **QW-07** | Unified Benchmark Identity Envelope | Dispersed metadata across logs, manifests, patches, and digests. | Single  binding all SHA-256 hashes cryptographically. |
| **QW-08** | Honest Cost & Token Telemetry | Missing provider cost data treated as bash.00, breaking budget guards. | Tri-state cost model: , , . |
| **QW-09** | Context Compaction Invariants | Summarization destroys tool-call IDs, breaking subsequent provider turns. | Preserve tool-call linkage, active constraints, and unverified hypotheses during compaction. |
| **QW-10** | Benchmark Validity Preflight | Broken or non-reproducible upstream tasks contaminate harness scores. | Automated  and  validation before scoring. |
| **QW-11** | Anti-Thrashing State Breaker | Small models loop indefinitely executing the same failing diffs. | Deterministic hash FSM (	ext{tool}, 	ext{args}, 	ext{state})$; trigger replan on repeat. |
| **QW-12** | Containerized Benchmark Bridge | Filesystem ownership mismatch between inner agent and external oracle. | Exterior rootless container bridge passing only raw unified patches. |

---

## 3. The Tri-Substrate Ecosystem: Deep Architectural Audit

### 3.1 Vanguard (): The TCB Trust & Governance Kernel

Vanguard implements a mathematically pure hexagonal boundary:
```text
domain ← ports ← kernel ← agency ← runtime → adapters
```

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   VANGUARD KERNEL DISPATCH PIPELINE (S0–S12)                           │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  S0: ENTER       EffectRequest Ingestion                                                               │
│  S1: PARSE       Schema Validation & Type Coercion                                                     │
│  S2: RESOLVE     Action -> EffectAdapter Mapping (Before Any Lease Allocation)                         │
│  S3: DESCRIBE    Descriptor Computation: digest(canonical(name, normalisedArgs))                       │
│  S4: CLASSIFY    Sink Classification & Dynamic Capability Widening Inspection                          │
│  S5: AUTHORIZE   Policy Engine Evaluation: decision := policy.authorize(request, descriptor)          │
│  S6: GRANT       Grant Issuance: grant := issue(descriptor, principal, resources, ttl)                │
│  S7: RESERVE     Typed Budget Reservation: lease := governor.reserve(runId, resources, parentLease)   │
│  ├── TRY ───────────────────────────────────────────────────────────────────────────────────────────┤
│  │ S8: VERIFY    Verify Grant Unexpired & Cryptographically Binds THIS Descriptor                      │
│  │ S8a: INTENT   Durable Append of EffectStarted Event & FSYNC (Crash Consistency)                     │
│  │ S9: DISPATCH  Adapter Execution: adapter.execute(descriptor, payload)                               │
│  │ S10: COMMIT   Governor Commit: governor.commit(lease, actualUsage)                                  │
│  ├── FINALLY ───────────────────────────────────────────────────────────────────────────────────────┤
│  │ S11: RELEASE  Governor Release Lease (Guaranteed on All Exit Paths)                                │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────┘
│  S12: EMIT       Append Outcome Events to Durable Ledger (After Resource Release)                      │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Key Invariants:**
- **TCB Budget**: Kernel LOC $\le 1438$ (enforced by [](file:///home/rocha/Coding/Aether-D-System/tools/linters/check_tcb_budget.py)).
- **Domain Blindness**: Kernel is completely agnostic of domain concepts (no code, git, or web semantics).
- **Prefix-Stable Context**: L1–L5 compiler guarantees that prompt layers L1–L3 are immutable, maximizing provider cache hits.

### 3.2 LEX (): The Ultra-Low-Latency Rust Swarm

LEX models software engineering as a **hardware-aware multi-model compiler pipeline**:
- **Hardware-Aware Swarm Topology**:
  - : Zero-latency request categorization.
  - : High-level reasoning; emits a declarative .
  - : Fast, targeted code generation and test synthesis.
  - : Before loading worker models, Ollama active polling waits until {	ext{Architect}} == 0$.
- **3-Tier Rootless Sandboxing**: Bubblewrap namespaces $	o$ user namespaces $	o$ static AST abort.
- **Surgical Code Patching**: Multi-strategy fallback (exact line index $	o$ fuzzy anchor $	o$ unified diff).
- **Anti-Collusion Mutation Testing**: Synthesizes AST mutants in generated code to verify that test suites actually fail when defects are present.

### 3.3 LIM (): Formal Verification, SBFL & CEGIS

LIM is an algorithmic testbed equipped with 18+ configuration presets:
- **Spectrum-Based Fault Localization (SBFL)**: Traces execution paths across passing and failing tests, computing Ochiai suspiciousness coefficients:
  516164	ext{Ochiai}(s) = rac{	ext{failed}(s)}{\sqrt{	ext{total\_failed} 	imes (	ext{failed}(s) + 	ext{passed}(s))}}516164
- **Counterexample-Guided Inductive Synthesis (CEGIS)**: Formally synthesizes code satisfying SMT constraints by iteratively proposing candidates and checking counterexamples.
- **Concolic & Adversarial Fuzzing**: Combines concrete execution with dynamic symbolic execution to discover branch edge cases.
- **Speculative MCTS Search**: Tree-search over sequence of edits with automatic Git checkpoint rollback upon test regression.

### 3.4 Cross-Substrate Capability Matrix

```text
┌───────────────────────────────────────┬──────────────────────┬──────────────────────┬──────────────────┐
│ Architectural Dimension               │ Vanguard (Aether)    │ LEX (Rust Swarm)     │ LIM (Lab Engine) │
├───────────────────────────────────────┼──────────────────────┼──────────────────────┼──────────────────┤
│ Core Implementation Language          │ Python 3.10+ (Hex)   │ Rust (tokio / async) │ Python 3.10+     │
│ Dispatch Pipeline Formalism           │ S0–S12 13-stage TCB  │ TaskGraph IR         │ Direct Turn Loop │
│ Sandboxing Architecture               │ Bubblewrap UID 10001 │ 3-Tier bwrap/unshare │ Subprocess / AST │
│ Fault Localization Strategy           │ Lexical Search       │ Tree-sitter PageRank │ SBFL Ochiai/DStar│
│ Verification & Falsification          │ Exterior Oracles     │ Mutation Testing     │ CEGIS + Concolic │
│ Speculative Search & Rollback         │ Linear Execution     │ Git Worktree CoW     │ MCTS + Rollback  │
│ Context Cache Discipline              │ L1–L5 Compiler       │ Token-budget Ledger  │ Radix L1–L5 Cache│
│ Wire Contract & Evidence Ledger       │ SQLite WAL + JCS     │ AgentExecutionEnv    │ RunReceipt Ledger│
│ Turn-Level Latency Overhead           │ ~5–15 ms             │ < 2 ms               │ ~10–25 ms        │
└───────────────────────────────────────┴──────────────────────┴──────────────────────┴──────────────────┘
```

---

## 4. Frontier Industry & Academic Literature Deep-Dive

### 4.1 DeepSeek Harness ( / Cordis): Microkernel & Event Log as Truth

The DeepSeek Harness introduces two fundamental design axioms:
1. **Egalitarian Microkernel ("All is a Plugin")**:
   - There is no privileged "core loop". The Agent Loop, Tools, Model Runtimes, Context Managers, and UIs are all egalitarian plugins interacting via the Cordis kernel.
   - Any agent loop (ReAct, Plan-Execute, MCTS, Multi-Model Debate) can be hot-swapped at runtime without altering kernel contracts.
2. **Event Sourcing ("The Event Log is the Center")**:
   - The conventional mutable array of chat messages is deprecated as architectural debt.
   - The single source of truth is an append-only, immutable  stream.
   - The LLM context window is a **pure mathematical projection**:
     516164	ext{ContextWindow} = 	ext{deriveMessages}(	ext{EventStream}[0..n], 	ext{CompactionPolicy})516164
   - Guarantees perfect crash recovery, deterministic time-travel replay, and cryptographic auditability.

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 CORDIS MICROKERNEL & EVENT STREAM TOPOLOGY                             │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│   [ Tool Plugins ]       [ AgentLoop Plugins ]       [ LLM Runtimes ]       [ Context Shapers ]        │
│          │                        │                         │                        │                 │
│          └────────────────────────┼─────────────────────────┼────────────────────────┘                 │
│                                   ▼                                                                    │
│                     ┌───────────────────────────┐                                                      │
│                     │       CORDIS KERNEL       │                                                      │
│                     │  • Monotonic Guardrails   │                                                      │
│                     │  • Typed Capability Leases│                                                      │
│                     └─────────────┬─────────────┘                                                      │
│                                   │                                                                    │
│                                   ▼                                                                    │
│                     ┌───────────────────────────┐                                                      │
│                     │   APPEND-ONLY EVENT LOG   │ ──► [ Pure Projection: deriveMessages() ]            │
│                     │    (SessionEvent Stream)  │ ──► [ Telemetry & Real-Time Dashboard ]              │
│                     └───────────────────────────┘ ──► [ Time-Travel Debugger & Replay ]                │
│                                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Claude Code Architecture: Asymmetric Determinism & Prefix Caching

Analysis of production coding agents (e.g., Claude Code CLI) reveals crucial engineering principles:
- **Asymmetric Determinism Ratio**: 98.4% of the codebase is deterministic systems infrastructure (process supervision, permission lattices, PTY bridges, stream tokenizers, AST parsers), while only 1.6% is LLM inference logic.
- **Prefix-Stable Prompt Caching**: System prompts, tool schemas, and repository maps are locked in an immutable prefix. Explicit cache breakpoints () achieve 0	ext{--}90\%$ cache hit rates across multi-turn sessions.
- **Bash as Universal Adapter**: Avoids tool proliferation by leveraging Unix composability under strict sandbox supervision.
- **Subagent Context Sandboxing**: Complex exploration or long test runs are delegated to isolated subagents that return concise summaries, protecting the parent context from token exhaustion.

### 4.3 SOTA Autonomous Coding Harness Algorithms

1. **Dual-Loop Architecture**:
   - **System 1 (Inner Loop)**: Instantaneous AST pre-flight checks, strict linter gates, and targeted unit test runs (<50ms).
   - **System 2 (Outer Loop)**: POMDP planning, SBFL fault localization, and speculative tree search.
2. **Deterministic Anti-Thrashing FSM**:
   - Tracks action signatures (	ext{tool}, 	ext{args}, 	ext{state})$. If an action repeats against an identical state hash, the harness aborts the doom loop and forces a replan.
3. **Multi-Operator Mutation Falsification**:
   - Verifies patch integrity by injecting syntactic mutants. If tests pass on mutated code, the test suite is flagged as ungrounded.

---

## 5. Comprehensive Framework Improvement Blueprint for Autonomous CLIs

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              VANGUARD FRAMEWORK REFACTORING BLUEPRINT                                  │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│  [ CLI Layer / UI ] ────────►  Pluggable AgentLoop (Cordis Pattern)                                   │
│                                          │                                                             │
│                                          ▼                                                             │
│  [ Agency Layer ]   ────────►  Radix L1–L5 Context Engine + Structured Compactor                       │
│                                          │                                                             │
│                                          ▼                                                             │
│  [ Kernel Layer ]   ────────►  S0–S12 Monotonic Guardrails + Anti-Thrashing FSM                        │
│                                          │                                                             │
│                                          ▼                                                             │
│  [ Ports Layer ]    ────────►  ShellPort (PTY) + IndexPort (Tree-Sitter) + EvaluatorPort               │
│                                          │                                                             │
│                                          ▼                                                             │
│  [ Adapters Layer ] ────────►  Interactive Bash PTY + SBFL Ochiai + Mutation Verifier                  │
│                                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 5.1 Pillar 1: Pluggable  Microkernel (Cordis Pattern)
- **Problem**: Hardcoded  loop in [](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/agency/episode/engine.py) prevents experimenting with alternative cognitive architectures.
- **Solution**: Promote  to an egalitarian protocol:
  ```python
  class AgentLoop(Protocol):
      @property
      def loop_id(self) -> str: ...
      def step(self, ctx: KernelContext, state: LoopState) -> Generator[TurnEvent, None, LoopOutcome]: ...
  ```
- **Result**: Manifests declare their loop engine (, , , ).

### 5.2 Pillar 2: Append-Only  Store & Pure Context Projections
- **Problem**: Mutable message arrays lead to cache fragmentation, state drift, and difficult debugging.
- **Solution**: The SQLite WAL ledger becomes the sole source of truth. The context compiler implements:
  516164	ext{messages} = 	ext{derive\_messages}(	ext{events}, 	ext{budget})516164
- **Result**: Deterministic session replay, instant time-travel debugging, and guaranteed cache integrity.

### 5.3 Pillar 3: Stateful Interactive PTY 
- **Problem**: One-shot  loses shell environment, working directory, and virtualenv between calls.
- **Solution**: Introduce  backed by a persistent pseudo-terminal inside the Bubblewrap container:
  - Supports incremental streaming, sub-200ms  interruption, and head/tail paged output windows (top 25 and bottom 50 lines).

### 5.4 Pillar 4: Instantaneous AST Syntax Pre-Flight Gates (<0.2ms)
- **Problem**: Models waste expensive turns fixing trivial indentation or syntax errors.
- **Solution**: Tool execution pipeline intercepts patches with an in-process AST validator before execution:
  - If invalid, returns exact line syntax error immediately without consuming an LLM turn.

### 5.5 Pillar 5: SBFL Fault Localization & AST PageRank via 
- **Problem**: Lexical grep consumes excessive context on large repositories.
- **Solution**: Implement  and  behind :
  - Computes Ochiai suspiciousness scores on test failure and annotates the prompt with top-5 bug locations.

### 5.6 Pillar 6: Speculative Git Checkpoint Engine & Worktree Sandboxing
- **Problem**: Flawed multi-step edits leave repositories in corrupted intermediate states.
- **Solution**: Before applying changes, runtime creates an in-memory Git checkpoint.
  - If tests regress severely, harness automatically executes a clean rollback and records dead ends.

### 5.7 Pillar 7: AST Mutation Verification & Anti-Collusion Engine
- **Problem**: Agents can write trivial or no-op assertions that pass without verifying the bug fix.
- **Solution**: Port LIM's [](file:///home/rocha/Coding/LIM_LLM_INT_MACHINE/mutation_verifier.py) to generate syntactic mutants and verify that test suites fail on broken code.

### 5.8 Pillar 8: Deterministic Anti-Thrashing State-Hash FSM
- **Problem**: Cheap models enter infinite loops repeating identical invalid actions.
- **Solution**: Track action signatures (	ext{tool}, 	ext{args}, 	ext{state})$. On duplicate detection, trigger  to force replanning.

### 5.9 Pillar 9: Radix L1–L5 Prefix Cache Alignment & Structured Compactor
- **Problem**: Uncoordinated prompt assembly invalidates provider cache prefixes.
- **Solution**: Formalize the 5-layer context hierarchy:
  - **L1**: Static System Core & Tool Schema (Locked)
  - **L2**: Workspace Repo Map & Architecture Outline (Cached)
  - **L3**: Active Issue Brief & Invariant Constraints (Pinned)
  - **L4**: Structured Memory & Verified Hypotheses (Compacted)
  - **L5**: Ephemeral Multi-Turn Observations & Paged Stdio (Evictable)

### 5.10 Pillar 10: Cryptographic Identity Envelope & Telemetry Dashboard
- **Problem**: Dispersed execution metadata prevents independent verification of benchmark claims.
- **Solution**: Emit  containing SHA-256 digests of framework, manifest, task, patch, trajectory, and signed oracle verdicts, accompanied by an interactive HTML/SVG telemetry dashboard.

---

## 6. Next-Generation Agent Coding CLIs & Product Families

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   VANGUARD AGENTIC CODING CLI FAMILY                                  │
├───────────────────┬───────────────────┬───────────────────┬───────────────────┬────────────────────────┤
│  1. vg-code       │  2. vg-swarm      │  3. vg-fuzz       │  4. vg-refactor   │  5. vg-review          │
│  Autonomous SWE   │  Tiered Multi-    │  Formal CEGIS &   │  Causal Slicing & │  Adversarial Debate    │
│  Problem Solver   │  Model Swarm      │  SMT Falsifier    │  Modernizer       │  & PR Adjudicator      │
├───────────────────┴───────────────────┴───────────────────┴───────────────────┴────────────────────────┤
│  6. vg-tutor (Codebase Onboarding)  │  7. vg-research (RFC Web Corroborator) │  8. vg-rlvr (Dataset Gen)│
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 6.1 CLI 1:  (Autonomous SWE-Bench Solver)
- **Role**: Autonomous repository bug fixing, issue resolution, and feature synthesis.
- **Workflow**:
  ```text
  [Issue Ingestion] ──► [SBFL Fault Localization] ──► [Reproducer Synthesis]
                                                              │
  [Signed Patch Delivery] ◄── [Regression Verification] ◄── [Surgical Patch]
  ```

### 6.2 CLI 2:  (Tiered Multi-Model Coding Swarm)
- **Role**: High-throughput, low-cost swarm orchestration using open-weights and frontier models.
- **Workflow**:  categorizes task $	o$  emits  $	o$  and  execute in parallel $	o$ Sandbox merges verified diff.

### 6.3 CLI 3:  /  (Formal CEGIS & SMT Synthesis)
- **Role**: Provable correctness verification for cryptography, parsers, and distributed consensus protocols.
- **Workflow**: SMT Specification $	o$ Counterexample-Guided Synthesis $	o$ Concolic Path Exploration $	o$ Proof Receipt.

### 6.4 CLI 4:  (Causal Slicing & Large-Scale Modernizer)
- **Role**: Dependency isolation, dead-code elimination, and architectural migration.
- **Workflow**: AST Call Graph $	o$ Causal Program Slicing $	o$ Stepwise Migration Plan $	o$ Surgical Patching.

### 6.5 CLI 5:  /  (Adversarial Multi-Model PR Adjudicator)
- **Role**: Zero-trust code review and automated PR risk assessment.
- **Workflow**: Spin up competing reviewer personas (Security, Performance, Clean Code) $	o$ Multi-Agent Debate $	o$ Signed Merge Verdict.

### 6.6 CLI 6:  (Evidence-Graph Interactive Codebase Guide)
- **Role**: Developer onboarding and complex codebase comprehension.
- **Workflow**: Dynamic AST PageRank Traversal $	o$ Call-Chain Visualization $	o$ Socratic Explanations with Clickable Proofs.

### 6.7 CLI 7:  (Bounded Technical RFC & Web Corroborator)
- **Role**: Autonomous technical research and architectural trade-off analysis.
- **Workflow**: Egress-Controlled Search $	o$ SSRF-Safe Markdown Fetching $	o$ Triangulated Verification $	o$ Canonical RFC Generation.

### 6.8 CLI 8:  (Verifiable Trajectory & Dataset Generator)
- **Role**: Mining high-value synthetic reasoning data for reinforcement learning.
- **Workflow**: Autonomous Solve $	o$ Filter by Formal Test Pass & Mutation Score $	o$ Export (State, Action, Reward, Trace) Dataset.

---

## 7. Implementation Roadmap, Risk Matrix & Skunkworks Validation

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 EXECUTION & RATIFICATION MILESTONE LADDER                              │
├───────────────────────────────────┬──────────────────────────────────┬─────────────────────────────────┤
│        PHASE 1: STABILIZE         │        PHASE 2: ENHANCE          │        PHASE 3: FRONTIER        │
│        (Sprint 10 / M-9)          │        (Sprint 11 / M-10)        │        (Sprint 12 / M-11)       │
├───────────────────────────────────┼──────────────────────────────────┼─────────────────────────────────┤
│ • Preregister 27-row dry run      │ • Pluggable AgentLoop microkernel│ • Tiered Swarm Orchestrator     │
│ • Validate 11 manifest presets    │ • PTY ShellPort with streaming   │ • CEGIS / Concolic Fuzzing port │
│ • Execute DeepSeek V4 Flash live  │ • Tree-Sitter & SBFL IndexPort   │ • Multi-Agent Arena Debates     │
│ • Enforce cost & token ceilings   │ • AST Syntax Preflight (<0.2ms)  │ • Verifiable RLVR Exporter      │
│ • Generate honest evidence report │ • Anti-thrashing signature FSM   │ • Full Ink/React TUI CLI (`vg`) │
└───────────────────────────────────┴──────────────────────────────────┴─────────────────────────────────┘
```

### Risk Matrix & Mitigations

| Risk Factor | Probability | Impact | Mitigation Strategy |
|:---|:---|:---|:---|
| **Provider Protocol Drift** | High | High | Strict provider-specific normalizers; captured payload digests for hermetic replay. |
| **Context Window Inflation** | High | High | Head/tail paged output windows, aggressive result eviction, subagent sandboxing. |
| **Infinite Agent Doom Loops** | Medium | Critical | Deterministic state-hash anti-thrashing FSM; hard per-run turn ceilings. |
| **Test-Code Collusion** | Medium | High | Multi-operator AST mutation testing to falsify ungrounded test suites. |
| **Evaluator Container Mismatch** | Low | High | Exterior container bridge receiving only pure unified patches. |

---

## 8. Conclusion & Strategic Vision

The union of **Vanguard's provable TCB kernel**, **LEX's low-latency Rust swarm mechanics**, and **LIM's formal verification and fault localization algorithms** establishes a complete, mathematically grounded substrate for autonomous coding. By incorporating the **Cordis microkernel ("all is a plugin")**, **event-sourced session projections**, and **deterministic multi-layer safety guardrails**, Vanguard is uniquely positioned to power the next generation of resilient, high-autonomy coding agent CLIs.

---

## 9. Algorithmic Specifications & Mathematical Formalisms

### 9.1 Spectrum-Based Fault Localization (SBFL Ochiai & DStar)

The SBFL localizer instrument collects statement execution frequencies during the test suite run. Given:
- {CF}$: Number of failing test cases that execute statement $
- {UF}$: Number of failing test cases that do *not* execute statement $
- {CS}$: Number of passing (successful) test cases that execute statement $
- {US}$: Number of passing test cases that do *not* execute statement $

The suspiciousness coefficients are computed as:

516659\text{Ochiai}(s) = \frac{N_{CF}}{\sqrt{(N_{CF} + N_{UF}) \times (N_{CF} + N_{CS})}}516659

516659\text{DStar}(s, * = 2) = \frac{N_{CF}^2}{N_{CS} + N_{UF}}516659

516659\text{Tarantula}(s) = \frac{\frac{N_{CF}}{N_{CF} + N_{UF}}}{\frac{N_{CF}}{N_{CF} + N_{UF}} + \frac{N_{CS}}{N_{CS} + N_{US}}}516659



### 9.2 SMT-Guided CEGIS Synthesis Loop

Counterexample-Guided Inductive Synthesis (CEGIS) formalizes algorithmic code generation:
1. **Specification**: $\Phi(x, y)$ defines the formal post-condition.
2. **Synthesizer**: Proposes candidate program  \in \mathcal{L}$ satisfying current counterexample set  = \{e_1, e_2, ..., e_k\}$.
3. **Verifier (SMT / Z3)**: Checks $\forall x. \Phi(x, P(x))$.
   - If $\text{UNSAT}$ (no counterexample exists), $ is formally verified.
   - If $\text{SAT}$ with counterexample  = c$,  \leftarrow E \cup \{c\}$, and repeat synthesis.



### 9.3 Anti-Thrashing State Hash FSM Transition Table



---

## 10. Concrete Vanguard Manifest Schema for SOTA Presets



---

## 11. Appendix: Complete Error Taxonomy & Falsification Matrix

| Error Class Code | Formal Definition | Detection Mechanism | Recovery & Mitigation Path |
|:---|:---|:---|:---|
| `ERR_SYNTAX_PREFLIGHT` | Patch violates target language AST syntax | In-process AST parse gate (<0.2ms) | Return exact line error to model without turn penalty. |
| `ERR_MUTATION_COLLUSION`| Test suite passes on intentionally broken AST | AST mutation injector probe | Reject test suite; demand assertion of behavioral change. |
| `ERR_THRASHING_LOOP`   | Repeated identical tool call on unchanging workspace | State-hash FSM H(t, a, s) | Escalate turn to REPLAN with explicit dead-ends history. |
| `ERR_PREFIX_INVALIDATED`| L1-L3 system instructions modified mid-session | Context Compiler digest probe | Force prefix freeze; divert additions strictly to L5. |
| `ERR_BUDGET_OVERRUN`   | Single turn exceeds token or USD reservation | Kernel S7 Typed Budget Governor | Fail closed; release lease; emit partial diagnostic receipt. |
| `ERR_SSRF_NETWORK`     | Outbound web fetch targets private IP range | Web adapter network policy filter | Terminate request with security alert in event ledger. |

### 11.1 Mathematical Proof of Monotonic Budget Attenuation

Let $B_0 = (	au_0, \mu_0, \delta_0)$ represent the root budget tuple where $	au_0 \in \mathbb{N}$ denotes max tokens, $\mu_0 \in \mathbb{R}^+$ denotes USD cost, and $\delta_0 \in \mathbb{N}$ denotes max turns.
For any child subagent spawned at turn $k$ with requested budget $B_{	ext{child}}$, the attenuation function $\mathcal{A}(B_{	ext{parent}}, B_{	ext{child}})$ must strictly satisfy:

$$B_{	ext{child}} \preceq B_{	ext{parent}} \iff 	au_{	ext{child}} \le 	au_{	ext{parent}} \land \mu_{	ext{child}} \le \mu_{	ext{parent}} \land \delta_{	ext{child}} \le \delta_{	ext{parent}}$$

And the parent residual budget immediately transitions to:

$$B_{	ext{parent}}' = B_{	ext{parent}} \ominus B_{	ext{child}}$$

Ensuring the total system budget invariant $\sum B_{	ext{active}} + \sum B_{	ext{consumed}} \le B_0$ is preserved across arbitrary levels of recursive subagent delegation.

### 11.2 Telemetry KPI Digest & Observability Envelope

Every turn emitted by the SOTA harness conforms to the `aether.turn-telemetry/1` schema:

```json
{
  "schema": "aether.turn-telemetry/1",
  "run_id": "vg-run-20260829-01",
  "turn_index": 4,
  "action_descriptor": "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
  "ast_preflight_passed": true,
  "sbfl_top_symbol": "vanguard.packages.kernel.budget.reserve",
  "sbfl_suspiciousness": 0.894,
  "tokens": {
    "prompt": 1420,
    "cached": 1280,
    "completion": 145,
    "total": 1565
  },
  "cost_usd": 0.000124,
  "latency_ms": 420.5,
  "state_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```
