# PROMPT — Architecture & Concept Lock v0.6

**Status:** Recorded instruction. This is the prompt the Concept Lock phase followed.
**Input:** `docs/07_reviews/VANGUARD_V060_FORENSIC_DISCOVERY.md` (investigation, not law)
**North star (non-normative until cited by ADR):**
`docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/principal_engineer_proposal.md`
**Procedure origin:** `docs/07_reviews/TODO_DONT_COMMIT_BEFORE_DOING_IT_v2.md` Deliverable 2
**Date:** 2026-08-20

You are the Principal Staff Engineer / Tech Lead. Forensic discovery is complete. You are now
authorized to **lock concepts and update normative documents**. You are **not** authorized to:

- create a roadmap, milestones, waves, backlog, or sprints
- migrate or delete `layer0/` or `vanguard/packages/`
- rewrite CI workflows
- introduce Rust, WASM-default, gRPC, or distributed infrastructure
- implement production code, split `root.py`, or "fix" F1 in this phase

---

## 1. Resolve every P0

Adopt the locks in the forensic report §19 without reopening them:

| ID | Lock |
|---|---|
| P0-1 | Python 3.10+. Production lattice = `vanguard/packages/`. No `aether-rust/`. No third `core/` tree. |
| P0-2 | Converge: keep packages implementations; promote layer0 SPI/JSON-RPC/UDS/lifecycle; delete duplicates only after a later parity gate. |
| P0-3 | Decision plane vs ledger: `Decision → DurableEvent → fold → EffectiveState`. |
| P0-4 | `Agent = Principal + HarnessInstance`. Swarm = policy. Graph = event projection. ADR-0003 stands. |
| P0-5 | Spawn subset invariants + mandatory causal envelope fields. |
| P0-6 | Identity trinity `D_H` / `D_R` / `D_X`. FrozenHarness is `D_H` only. |
| P0-7 | Hybrid event sourcing; SQLite WAL; replay taxonomy; consistency unit `project_id`. |
| P0-8 | Wire-first JSON-RPC/UDS; Protocol is client; `in_process` privilege; ADR-0005 freeze; five SPIs; evaluator not a product plugin. |
| P0-9 | Exterior signed judge; fabricating `"pass"` is defect F1. |
| P0-10 | Sequential execution; independence modeled, not enabled. |
| P0-11 | Production lattice is the CI subject of record (requirement locked; wiring is next code phase). |
| P0-12 | Defer Meta-Harness, distribution, WASM-default, graph DB, pytest-runner, competence-graph, Rust rewrite. |

If a supporting review conflicts, **keep this table**. Record the conflict; do not merge.

Already-known rejects (forensic §5.1):

- Full Refactor v3.1 Rust core
- Execution Plan treating `layer0/` as the v0.6 production target with packages as legacy
- Parecer v4 new top-level `core/`
- Parecer Anel 2 Evaluator as product plugin
- SPEC §1 `layer0/` as M1 destination (reversed by ADR, not by silent edit)
- SPEC §2 mid-run hot-swap vs ADR-0005 (ADR-0005 wins)
- `aether-v1-roadmap-waves.md` (out of scope)

## 2. Mark every P1 LOCK NOW or DEFER DELIBERATELY

Use forensic §20 as the registry. Do not convert deferred P1s into SPEC features.

## 3. Consolidate canonical concepts

Do not add: AgentEngine, SwarmEngine, WorkflowEngine, GraphDB, MetaLoopEngine, third runtime.

Canonical: Event, EffectRequest (one schema), Principal, HarnessInstance, FrozenHarness, Episode,
Plugin, Ledger, CAS, Reservation, Capability, spawn, Trajectory, Evaluator (exterior).

## 4. Eliminate architectural contradictions in law

SPEC may not simultaneously:

- call `layer0/` the M1 destination **and** treat packages as the as-built lattice without ranking them
- describe mid-run hot-swap **and** honour ADR-0005
- treat E-COV lexical pass as I-2 proof

## 5. Canonical runtime / migration strategy (law, not a sprint plan)

Invert SPEC §8 direction: recover mature packages semantics; promote layer0 SPI/broker; do not
rebuild WAL/evaluator/sandbox in `layer0/`. `layer0/` is a fork under convergence, not a destination
rewrite.

## 6–9. Boundaries

- Authority: § P0-3
- Multi-agent semantics required for future evolution: P0-4, P0-5 (primitive only)
- Plugin boundaries: P0-8, P0-9
- State/event: P0-7, I-4 as a **future behavioral** CI job, not the current self-fold test

## 10. ADRs

Append-only next numbers `0069+`. `0067` remains a documented hole.

Follow ADR-0045 fields: context, decision, alternatives rejected, evidence/bound test, reversal
condition, owner/status.

| ADR | Decision |
|---|---|
| 0069 | Runtime convergence (P0-1, P0-2) |
| 0070 | Recursive substrate (P0-4, P0-5) |
| 0071 | Authority + state + identity + replay (P0-3, P0-6, P0-7) |
| 0072 | Plugin boundary + evaluator (P0-8, P0-9) |
| 0073 | v0.6 lock vs defer (P0-10, P0-11, P0-12) |

Update `docs/05_adr/INDEX.md`: add `0069`–`0073` **and** missing `ADR-M0-01`…`13` rows.

## 11. SPEC v0.6

Edit `docs/SPEC.md` in place (sole living normative spec):

- Version anchor: **v0.6.0 Concept Lock**. Note `pyproject.toml` still `0.4.5b1` until a later cut.
- Authority: newer ADR wins by citation; `0069`–`0073` now sit above the M1-destination story.
- Preamble: recursive agency substrate; coding pack is the first *domain*, not the architecture.
- Rewrite §1 dual-lattice paragraph.
- Short section: Agent/spawn/identity trinity and decision vs state planes.
- §2: wire-first; strike mid-run hot-swap; `IEvaluationGate` does not host the judge.
- Honour table: keep I-1…I-11; add explicit bans (no third runtime, no swarm engine, no
  byte-identical concurrent ledger requirement).
- §8: invert migration direction.
- Self-review: no TBD; no contradiction with `0069`–`0073`.

Annexes: amend `KERNEL.md` front-matter only if a v0.6 sentence would otherwise contradict it
(destination of "M1 port"). Do not rewrite KERNEL S0–S12.

## 12. Concept Lock exit gate

All must be true:

1. Forensic report exists (25 sections, labeled evidence, live commands).
2. This prompt exists and Phase D followed it.
3. Every P0 has an ADR citation in SPEC.
4. Every P1 is LOCK NOW or DEFER DELIBERATELY in the forensic P1 registry.
5. SPEC v0.6 has no TBD and does not say `layer0/` is the M1 destination.
6. INDEX lists `0069`–`0073` and `ADR-M0-*`.
7. Conflict log lists rejected supporting-doc items.
8. Working tree contains **no** runtime/CI implementation of the next wave.
9. No git commit unless the user explicitly asks after reviewing the docs.

**Next authorized phase (not this prompt):** as-built gap / migration classification, then a single
operational execution plan, then code starting with CI-subject-of-record and F1 removal — not a
Rust rewrite and not a third runtime.
