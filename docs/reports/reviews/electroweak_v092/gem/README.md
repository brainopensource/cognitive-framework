# AETHER / Vanguard — Gem Technical Evaluation & SOTA Harness Masterplan

**Subject:** `github.com/brainopensource/cognitive-framework`, branch `feat/beta-release_electroweak-v091`, observed HEAD `7d46c7f5`  
**Reviewer:** Gemini 3.8 Flash (Autonomous Agent Systems & Principal AI Systems Architect)  
**Date:** 2026-09-04  
**Primary Masterplan:** [`gem_sota_harness_evolution_report.md`](gem_sota_harness_evolution_report.md) (~10 pages, 5,833 words, 65KB)

---

## Executive Summary & Findings

This review provides a comprehensive, mathematically grounded forensic evaluation of the Vanguard / AETHER substrate and delivers the definitive architecture for a state-of-the-art autonomous coding agent harness CLI (`Coding Max`).

### 1. Substrate Evaluation
AETHER possesses one of the most rigorous architectures in the agent ecosystem:
- **Pristine Hexagonal Lattice:** 827 files verified with zero illegal dependencies across `domain ← ports ← kernel ← agency ← runtime → adapters`.
- **Domain-Blind Microkernel:** 1,386 logical LOC (below the 1,438 threshold), implementing an immutable 13-stage dispatch pipeline (S0–S12) with monotonic capability attenuation and typed budgets.
- **In-Process SQLite-WAL Repository Intelligence:** The LDA engine provides an 80,496-relation code graph with sub-25ms incremental delta AST indexing and zero idle daemon overhead.
- **Hermetic Isolation:** Rootless Bubblewrap sandboxing (UID 10001) and deterministic cassette replay ($0 spend via the LAM Engine).

### 2. Diagnosis of Benchmark Failures
Despite this substrate, live runs exhibited severe failure clusters (`129 NO_PATCH`, `89 max_turns`, `81 malformed`, `45 abandoned`). Forensic analysis isolated the root causes:
1. **Patcher Fragility:** `AstPatchToolkit._apply` uses exact substring matching; a single whitespace or indentation difference causes `"search text not found"`, triggering destructive full-file overwrites.
2. **Lack of Multi-File Atomicity (2PC):** Edits to multiple files are written sequentially; an AST or patch failure on file 3 leaves files 1 and 2 dirty on disk without rollback.
3. **KV-Cache Busting:** Dynamic repository orientation packets are appended to Layer 3 (`environment`) in `ContextCompiler`, invalidating prompt cache breakpoints across turns.
4. **Leaky Verification Gate:** `AdmissionGate` checks `exit_code == 0` without binding the verification receipt to the post-edit SHA-256 tree digest, permitting premature exits.
5. **Disconnected Capabilities:** Four-tier memory contracts and skill lifecycles exist in isolation and are not yet composed into the active `CodingMaxFacade` runtime loop.

---

## The 8 Pillars of the SOTA Coding Harness

The masterplan ([`gem_sota_harness_evolution_report.md`](gem_sota_harness_evolution_report.md)) formalizes the solution:

1. **Resilient 2PC Patch Engine:** 9-strategy fallback hierarchy (exact $\to$ whitespace-norm $\to$ indent-shift $\to$ fuzzy Levenshtein) + in-process AST preflight validation ($<0.2\text{ ms}$) + atomic multi-file rollback.
2. **Context Economics & Compaction:** Byte-identical L1–L3 prefix caching (>75% KV-cache hit rate); CTRF test log distillation; tool body eviction in L5; trailing goal echo.
3. **Repository Intelligence (LDA):** Tree-sitter PageRank repo map + blast radius analysis (`callers`, `callees`, `references`, `tests`) bound to immutable `WorkspaceEpoch`.
4. **Four-Tier Governed Memory:** Working ($\sigma$ scratchpad) • Episodic (durable SQLite ledger) • Semantic (capability-gated) • Procedural (skills catalog in L3, body in L5 on demand).
5. **Small Orthogonal Toolkit:** Exactly 10 non-overlapping verbs (`read`, `search`, `list`, `patch.apply`, `patch.transaction`, `write`, `proc.exec`, `index.query`, `skill`, `finish`).
6. **Closed-Loop Control:** Stuck-loop circuit breakers ($d_t = d_{t-2}$ triggers strategy pivot); Cryptographic `AdmissionGate` bound to fresh test execution and tree digest.
7. **Deliberative Search (System 2):** Test-time compute scaling via ephemeral git worktrees; SWE-Search MCTS; Recursive Tournament Voting (RTV); powerless advisory monitor.
8. **Greenfield & Brownfield Workflows:** Spec $\to$ Type Scaffolding $\to$ Vacuity-Rejection Oracle $\to$ Topological Build; SBFL Ochiai Localization $\to$ Minimal Reproducer $\to$ 2PC Patch $\to$ Dual-Loop Verification.

---

## Document Index

- **Master Technical Report:** [`gem_sota_harness_evolution_report.md`](gem_sota_harness_evolution_report.md)
