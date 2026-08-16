# Sprint 5 Executable Backlog

**Sprint Goal:** Land the L1–L5 Prefix-Stable Context Compiler with competence priors (Lane SA), the OS-Isolated Evaluator with Double Probes (Lane SB), enhanced OpenRouter streaming resilience (Lane DC), and the aligned CLI client interface (Lane DD).

---

## Ticket Table

| Ticket | Assignee | Scope | Contract Row | Depends | Target Evidence | Merge Gate |
|---|---|---|---|---|---|---|
| `S5-SA-001` | Lead Arch (SA) | L1–L5 layered context compiler module (`vanguard/packages/agency/context/compiler.py`) | `REQ-CTX-001` | none | Prefix immutability, token truncation, provenance tags | GATE |
| `S5-SA-002` | Lead Arch (SA) | Pre-action competence prior $P(S \mid T)$ logging before Turn 1 | `REQ-CTX-001` | SA-001 | Ledger event `CompetencePriorRecorded` emitted | GATE |
| `S5-SB-001` | Senior Dev (SB) | OS-Isolated Evaluator daemon (`vanguard/packages/adapters/evaluators/isolated.py`) | `REQ-EVAL-001` | none | Dedicated UID/process boundary execution | GATE |
| `S5-SB-002` | Senior Dev (SB) | Double Probes: Immutability Probe (1) + Non-Pollution Probe (2) | `REQ-EVAL-001` | SB-001 | Tampered test oracle and untracked patch rejected | GATE |
| `S5-DC-001` | Senior Dev (DC) | OpenRouter ModelPort streaming backoff, token estimation & rate limit recovery | `REQ-PORT-006` | none | Test cassette retry & rate-limit handling suite | FAST |
| `S5-DC-002` | Senior Dev (DC) | Live disposable key test execution receipt (`REQ-SLICE-001`) | `REQ-SLICE-001` | DC-001 | Real provider latency log captured | FAST |
| `S5-DD-001` | Mid Dev (DD) | Realign `@vanguard/cli` TypeScript client interface to consume `RuntimeClient` async streams | `REQ-CLI-001` | none | `npm --workspace @vanguard/cli test` passes 100% | FAST |
| `S5-INT-001` | Lead Arch (SA) | End-to-end Sprint 5 integration: Context Compiler + Isolated Evaluator + OpenRouter | `REQ-CTX-001`, `REQ-EVAL-001` | SA-*, SB-*, DC-* | Full suite + broken harness green | GATE |

---

## Out of Scope for Sprint 5 (Deferred to Sprint 6)
- Composition Root `runtime/root.py` (`S6-SA`).
- Descriptor-bound interactive approval modal in TUI (`S6-SB` / `S6-DD`).
- Single-key human correction capture (`S6-DD`).
- End-to-end dogfood bug fix milestone run (`S6-SA`).
