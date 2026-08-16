# Phase 2 (Sprints 5 & 6) Leadership Guidelines & Architecture Directive

**Status:** ACTIVE PLANNING & EXECUTION on `sprint5-6/integration`  
**Target Delivery:** Phase 2 Lightweight Beta MVP (One Framework, One Coding Harness `vg-code-default`, Real OpenRouter Model, Descriptor-Bound Approvals, Isolated Exterior Evaluator, Hexagonal Ink TUI).  
**Authority:** [ADR-0057](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L165), [ADR-0058](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L177), [ADR-0059](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L178), and [ADR-0060](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L179).  
**Audience:** Project Lead, Tech Lead, and Core Engineers.

---

## 1. The Core Architecture Law: Decoupled, Minimal, Polyglot

Vanguard is designed as a **Universal General Task Solver (GTS)** whose microkernel and state ledger are completely agnostic to task domains:

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE UNIVERSAL GTS STACK                                  │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Microkernel & Ledger (Python 3.12+ / Minimal TCB):                                    │
│    • Invariant single dispatch S0–S12 with pre-execution intent writes.                  │
│    • Resource-scoped URI capability grants (file://, proc://, http://, agent://).        │
│    • Immutable append-only event ledger and crash-recovery scanner.                      │
│    • ZERO domain keywords, ZERO cognitive nouns (no "code", "plan", "reflect").         │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. Hexagonal Port Adapters (Polyglot Extension Boundary):                                │
│    • Core interfaces: ModelPort, EnvironmentPort, SandboxPort, EvaluatorPort.            │
│    • Polyglot Plugins: Heavy indexers, browser drivers, microVM runners, or tool servers│
│      in Rust, Go, Python, or TypeScript communicate strictly via standard wire envelopes│
│      (JSON-RPC / stdio / IPC / WebSockets).                                              │
│    • The TCB never imports an external plugin runtime.                                   │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. Declarative Agency Manifests (The Harness as Data):                                   │
│    • Coding Agent (`vg-code-default`): Typed read, search, patch, test tools + Git.      │
│    • Future Manifests (`vg-research-deep`, `vg-assistant-gateway`, `vg-tutor-math`):    │
│      Swapped purely via JSON/YAML manifest without touching kernel or episode engine.    │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Invariants You Must Never Violate (Anti-Drift Doctrine)

Every engineer, agent, and reviewer must uphold these four non-negotiable laws:

1. **The Generality Invariant ([ADR-0060](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L179)):**  
   Never introduce code-specific syntax, Git assumptions, or cognitive identifiers into `vanguard/packages/kernel/` or `vanguard/packages/agency/episode/engine.py`. Domain logic belongs exclusively in `HarnessManifest` and `PortAdapters`.
2. **The Narrow Waist Wire Law ([ADR-0059](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L178)):**  
   Polyglot plugins (Rust Tree-sitter parsers, Go vector search, Node/Deno runtimes) connect across port adapters using standard JSON envelopes. The microkernel remains minimal, deterministic, and language-neutral.
3. **The Exterior Evaluator Law ([VG-01 M5](file:///home/rocha/Coding/Aether-D-System/docs/v4/01_vanguard_engineering_handbook_v040.md#L46)):**  
   The episode engine can **never** trigger evaluation or judge its own output. Evaluation runs in an isolated OS process (`UID 10002`) triggered solely by observing terminal ledger events.
4. **The Four-Lane Parallel Law ([ADR-0056](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L164)):**  
   Developer lanes start on Day 1 without waiting for peer merges. All PRs cite an active `req_id` from [`docs/sprint0/active-mvp-contract.json`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json) and require 100% passing test receipts.

---

## 3. Four-Lane Developer Packet Allocation

### Sprint 5 (The Judge & Context Substrate)

| Lane | Complexity | Scope | Deliverables | Merge Gate Requirement |
|---|---|---|---|---|
| **SA (Senior A)** | Level 4 / 5 (Gate) | `vanguard/packages/agency/context/` | L1–L5 Prefix-Stable Context Compiler, token budgeter, provenance tags, competence prior $P(S \mid T)$ | `REQ-CTX-001` |
| **SB (Senior B)** | Level 4 / 5 (Gate) | `vanguard/packages/adapters/evaluators/` | OS-Isolated Evaluator daemon (`UID 10002`), Double Probes (immutability + non-pollution), `inconclusive` handling | `REQ-EVAL-001` |
| **DC (Dev C)** | Level 2–3 / 5 (Fast) | `vanguard/packages/adapters/models/` | OpenRouter model port streaming retry backoff, token estimation, live key envelope validation | `REQ-PORT-006` / `REQ-SLICE-001` |
| **DD (Dev D)** | Level 2–3 / 5 (Fast) | `vanguard/clients/cli/src/` | Refactor CLI `RuntimeClient` interface to consume live `EventEnvelope` streams; clean JSONL replay | `REQ-CLI-001` |

### Sprint 6 (Beta Product Assembly & Dogfood Milestone)

| Lane | Complexity | Scope | Deliverables | Merge Gate Requirement |
|---|---|---|---|---|
| **SA (Senior A)** | Level 5 / 5 (Gate) | `vanguard/packages/runtime/root.py` | Runtime Composition Root, end-to-end harness runner, real single-file bug fix dogfood execution | `REQ-DOG-001` |
| **SB (Senior B)** | Level 4 / 5 (Gate) | `vanguard/packages/runtime/governance/` | Descriptor-bound human approval flow: unified diff extraction, `argsDigest` signature verification, `MF-GOV-001` | `REQ-APP-001` |
| **DC (Dev C)** | Level 3 / 5 (Fast) | `tools/telemetry/`, `test/benchmarks/` | Telemetry & latency tracking (p95 first-token, effect overhead), paired benchmark runner | `REQ-BENCH-001` |
| **DD (Dev D)** | Level 3 / 5 (Fast) | `vanguard/clients/cli/src/ui/` | Ink/React TUI diff approval modal, live event tree display, single-key `CorrectionRecord` capture (`[d]efect`, `[s]tyle`, `[t]est`) | `REQ-CLI-002` |

---

## 4. Verification & Merge Gates

Before any Phase 2 PR merges to `main`:
1. `python3 tools/check_boundaries.py` passes (zero package lattice violations).
2. `python3 tools/check_tcb_budget.py` passes (kernel logical LOC remains strictly below 1,438).
3. `python3 tools/run_broken_tests.py` passes (all 21 broken counterparts observed failing).
4. `python3 tools/check_active_mvp_contract.py` reports 100% coverage on assigned requirement rows.
5. `python3 -m unittest discover -s test` passes 100% in subprocess-isolated execution.
