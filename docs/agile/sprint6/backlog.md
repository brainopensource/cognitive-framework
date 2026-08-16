# Sprint 6 Executable Backlog — Beta MVP Assembly & Dogfood Gate

**Sprint Goal:** Assemble the Runtime Composition Root (`runtime/root.py`), wire descriptor-bound human approvals, implement the interactive Ink TUI screens, and achieve the Beta Dogfood Gate by solving a real single-file bug end-to-end.

---

## Ticket Table

| Ticket | Assignee | Scope | Contract Row | Depends | Target Evidence | Merge Gate |
|---|---|---|---|---|---|---|
| `S6-SA-001` | Lead Arch (SA) | Runtime Composition Root (`vanguard/packages/runtime/root.py`) assembling all ports, kernel, and episode engine | `REQ-DOG-001` | S5-SA-*, S5-SB-* | Programmatic entrypoint `Runtime.execute_harness()` verified | GATE |
| `S6-SB-001` | Senior Dev (SB) | Descriptor-bound approval flow in `vanguard/packages/runtime/governance/` (unified diff extraction & `argsDigest` check) | `REQ-APP-001` | none | Tampered diff fails closed (`MF-GOV-001`); signed diff resumes | GATE |
| `S6-DC-001` | Senior Dev (DC) | Runtime telemetry suite (p95 first-token latency, sandbox effect overhead, token cost tracker) | `REQ-BENCH-001` | none | Telemetry metrics emitted to event store & JSON summary | FAST |
| `S6-DD-001` | Mid Dev (DD) | React Ink TUI Screens: Diff Approval Modal, Live Event Tree, Timeline Inspector | `REQ-CLI-002` | S6-SB-001 | TUI interactive test suite passes; diff modal renders correctly | FAST |
| `S6-DD-002` | Mid Dev (DD) | Single-keystroke human correction capture (`[d]efect`, `[s]tyle`, `[t]est`, `[s]ecurity`, `[a]rchitecture`) | `REQ-CLI-002` | S6-DD-001 | `CorrectionRecord` persisted to ledger | FAST |
| `S6-SA-002` | Lead Arch (SA) | Beta Dogfood Milestone Gate: Execute `vg-code-default` against real repo bug with zero human code edits | `REQ-DOG-001` | S6-SA-001, S6-SB-001, S6-DD-001 | Real single-file bug diagnosed, patched, approved, and verified green | GATE |

---

## Exit Criteria for Sprint 6 (Phase 2 Closure)
1. End-to-end execution of `vg run --manifest vg-code-default --task "Fix issue"` passes against real repository fixture.
2. Human approval modal displays accurate diff and verifies signature against `argsDigest`.
3. Evaluator daemon verifies fix in isolated OS process with double probes green.
4. Contract test suite reports 100% covered across all 49 requirement rows.
