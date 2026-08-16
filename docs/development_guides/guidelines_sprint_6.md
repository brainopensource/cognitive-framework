# Sprint 6 Leadership Guidelines & Exit Criteria

**Status:** BLOCKED — PENDING SPRINT 5 MERGE  
**Target Delivery:** Beta MVP Assembly & Dogfood Milestone (`REQ-DOG-001`, `REQ-APP-001`, `REQ-CLI-002`)  
**Authority:** [ADR-0057](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L165), [ADR-0058](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L177)  
**Audience:** Project Lead and Tech Lead only.

---

## 1. Sprint 6 Mandate & Goal

Sprint 6 finishes the **Beta MVP**. It takes the components built in Sprints 0–5 (Kernel, Ledger, Context Compiler, Isolated Evaluator, OpenRouter, Git Worktree) and wires them through the **Runtime Composition Root** (`runtime/root.py`).

The sprint exits with a live **Dogfood Milestone**: The system must autonomously diagnose, patch, request approval, and pass verification for a real single-file bug in an external test repository.

---

## 2. Four-Lane Execution Structure

| Lane | Role / Assignee | Deliverables | Target Contract | Merge Gate |
|---|---|---|---|---|
| **Lane SA** | Lead Architect / TL | Runtime Composition Root (`runtime/root.py`) & Dogfood Bug Fix Gate | `REQ-DOG-001` | GATE |
| **Lane SB** | Senior Dev B | Descriptor-Bound Human Approvals (`runtime/governance/`) | `REQ-APP-001` | GATE |
| **Lane DC** | Senior Dev C | Telemetry Suite (p95 latency, overhead, cost tracking) | `REQ-BENCH-001` | FAST |
| **Lane DD** | Mid Dev D | Ink TUI Diff Approval Modal & Single-Key Correction Capture | `REQ-CLI-002` | FAST |

---

## 3. Sprint 6 Exit Checklist (The Phase 2 Delivery Gate)

Before tagging `v0.5.0-beta` and closing Phase 2:
1. `vg run --manifest vg-code-default --task "Fix issue #1"` runs end-to-end against real Git repo with zero human code edits.
2. Descriptor-bound approval modal renders unified diff, computes `argsDigest`, and halts tampered execution (`MF-GOV-001`).
3. Isolated evaluator daemon verifies fix under dedicated `UID 10002` with both double probes passing.
4. `active-mvp-contract.json` reports 100% covered across all 49 requirement rows.
5. All 252+ unit tests and 21/21 broken counterparts pass 100% green.
