---
id: VG-00
file: 00_vanguard_registry_v040.md
title: "Vanguard v4.0 — Document Registry & Authority Map"
version: 4.0.0
status: SKELETON — finalised last, after 02–12 are frozen
authority_scope: >
  Document precedence, status lifecycle, word budget and its measurement,
  identifier namespaces, supersession of the pre-v4 corpus, retirement protocol,
  and the CI rules that enforce all of the above.
supersedes: pre-v4 REG-D §§1, 2, 5, 10, 11
superseded_by: none
budget_words: 4500
owners: [Tech Lead]
last_reviewed: 2026-08-14
---

# Vanguard v4.0 — Document Registry & Authority Map

> **One sentence.** The only place that answers *"which document binds, and how do I know?"* — machine-checked, so the answer cannot drift.

**Skeleton notice.** Chapters 1–5 and 7–11 are authoritative. Chapter 6 fills as documents land; Chapter 12 closes at sign-off.

---

## Table of contents

1. [Purpose and the precedence mechanism](#1-purpose-and-the-precedence-mechanism)
2. [The v4.0 document set](#2-the-v40-document-set)
3. [Status lifecycle](#3-status-lifecycle)
4. [Budget ledger and the word-count method](#4-budget-ledger-and-the-word-count-method)
5. [Identifier namespaces](#5-identifier-namespaces)
6. [Normative rules index — pointers only](#6-normative-rules-index--pointers-only)
7. [Supersession map — the pre-v4 corpus](#7-supersession-map--the-pre-v4-corpus)
8. [REG-D content migration ledger](#8-reg-d-content-migration-ledger)
9. [CI rules](#9-ci-rules)
10. [Acceptance verification](#10-acceptance-verification)
11. [Archive and retirement protocol](#11-archive-and-retirement-protocol)
12. [Change log](#12-change-log)

---

## 1. Purpose and the precedence mechanism

The pre-v4 corpus held two lineages that each declared themselves normative over the same contracts, so an engineer opening the repository could not determine which one bound. That is a governance defect of exactly the class this architecture exists to prevent: no choke point, no provenance, no freeze at composition. The fix is mechanical, not editorial.

> **PR-1 — One owner per contract.** Each contract has exactly one owning document. Others reference it by anchor and may not restate it.
>
> **PR-2 — The registry is the authority.** Precedence is resolved by Chapter 2, never by a document's claim about itself. No v4 document asserts precedence over another.
>
> **PR-3 — Registration is a gate.** A document not listed in Chapter 2 is not normative, regardless of content, location, or status header.
>
> **PR-4 — Conflict is a defect, not a ranking.** Disagreement between v4 documents is a bug in owner assignment, fixed by removing the duplicate, not by deciding a winner.
>
> **PR-5 — Independence.** No v4 document may cite as authority or require reading any pre-v4 document. Chapter 7 is forensic only.

`PR-1` is DRY applied to specifications; `PR-4` is what makes it enforceable, since one owner per contract leaves no arbitration surface to litigate.

---

## 2. The v4.0 document set

| # | File (`_v040.md`) | Title | Status | Authority scope |
|---|---|---|---|---|
| **00** | `00_vanguard_registry` | Document Registry & Authority Map | AUTHORITY MAP | Precedence, status, budget, supersession, retirement |
| **01** | `01_vanguard_engineering_handbook` | Engineering Handbook | LIVING | Mental models, SOLID/DRY practice, testing taxonomy, ADR format, repo layout, glossary |
| **02** | `02_vanguard_charter_claims_and_non_claims` | Charter, Claims & Non-Claims | NORMATIVE | Mission, scope, non-claims, falsifiable claims, axioms, cross-cutting norms, locks, risk, honest limits |
| **03** | `03_vanguard_architecture_planes_and_execution_model` | Architecture — Planes & Execution Model | NORMATIVE | Planes, episode engine, concurrency, context engineering, environments, playbooks, failure taxonomy |
| **04** | `04_vanguard_core_contracts_and_wire_schema` | Core Contracts & Wire Schema | NORMATIVE | Schemas, wire format, canonicalisation, capability/competence/event types, ports, versioning |
| **05** | `05_vanguard_kernel_capabilities_and_security` | Kernel, Capabilities & Security | NORMATIVE | Policy kernel, dispatch, grants, attenuation, sandbox, self-modification, threat model |
| **06** | `06_vanguard_competence_memory_and_evidence` | Competence, Memory & Evidence | NORMATIVE | Competence graph lifecycle, claim pipeline, verification, substrate invariance |
| **07** | `07_vanguard_loop_engineering_and_measurement` | Loop Engineering, Measurement & Self-Improvement | NORMATIVE | Closure conditions, measurement doctrine, promotion, release pipeline, experiment registry |
| **08** | `08_vanguard_phase_0_build_plan` | Phase 0 Build Plan | DISPOSABLE | Increments, tickets, must-fail suite, CI gates, exit criterion |
| **09** | `09_vanguard_decision_register` | Decision Register | LIVING | ADRs with reversal conditions; adjudication and correction rationale |
| **10** | `10_vanguard_deferred_and_rejected_register` | Deferred & Rejected Register | LIVING | Deferrals and rejections with reversal conditions |
| **11** | `11_vanguard_design_convergence_evidence` | Independent Design Convergence | EVIDENCE (secondary) | Attested summary of the independent-review convergence finding |
| **12** | `12_vanguard_vision_annex` | Vision Annex | **NON-NORMATIVE** | Analogies, long-horizon framing, product language |

**Ambiguity resolution order.** Owning document → this registry → Tech Lead. No fourth step; prose in a non-owning document never breaks a tie.

**Document 12 header, mandatory:** `NON-NORMATIVE. Not a specification. No ticket may cite this document.`

---

## 3. Status lifecycle

| Status | Meaning | Change rule |
|---|---|---|
| `NORMATIVE` | Binding contract | ADR in `09` required |
| `LIVING` | Binding practice, expected to evolve | Pull request; ADR only if a norm changes |
| `DISPOSABLE` | Binding until phase end | Retired at phase exit |
| `AUTHORITY MAP` | Precedence only | Tech Lead sign-off |
| `EVIDENCE` | Records observations | Append-only |
| `NON-NORMATIVE` | Communicative | Unconstrained |
| `SKELETON` | Structure fixed, content incomplete | Not authority for an unwritten chapter |

---

## 4. Budget ledger and the word-count method

**Envelope: ≤32,000 normative + ≤15,000 supporting = ≤47,000 total.** Normative target is ~29,000 to hold contingency for review-driven additions.

| # | Doc | Class | Cap | Target |
|---|---|---|---:|---:|
| 02 | Charter | Normative | 3,000 | 2,700 |
| 03 | Architecture | Normative | 6,000 | 5,400 |
| 04 | Contracts | Normative | 6,000 | 5,400 |
| 05 | Kernel & Security | Normative | 5,000 | 4,500 |
| 06 | Competence & Memory | Normative | 4,000 | 3,600 |
| 07 | Loop & Measurement | Normative | 5,000 | 4,500 |
| 08 | Phase 0 | Normative | 3,000 | 2,700 |
| | **Normative subtotal** | | **32,000** | **28,800** |
| 00 | Registry | Supporting | 4,500 | — |
| 01 | Handbook | Supporting | 4,000 | — |
| 09 | Decision Register | Supporting | 3,000 | — |
| 10 | Deferred & Rejected | Supporting | 2,000 | — |
| 11 | Convergence Evidence | Supporting | 1,000 | — |
| 12 | Vision Annex | Supporting | 1,000 | — |
| | **Supporting subtotal** | | **15,000** | — |
| | **Total** | | **47,000** | — |

> **Reallocation note.** The registry's cap is 4,500, not the 2,000 originally planned, because Chapters 6 and 7 carry the rules index and the supersession map — both of which must be complete to be useful. `11` and `12` gave up 1,000 each. Supporting actuals total 10,533 against a 15,000 envelope, so the increase consumes headroom rather than creating debt.

### 4.1 The word-count method (CI-authoritative)

One method, deterministic, no dependencies beyond POSIX tools. Any other count is advisory.

```sh
#!/bin/sh
# tools/wordcount_v4.sh — the authoritative v4 word count.
# Rules, in order:
#   1. Strip the leading YAML front-matter block (first --- to next ---).
#   2. Strip fenced code blocks (``` ... ```), including the fences.
#   3. A word is a whitespace-separated token containing >= 1 alphanumeric char.
#   Markdown tables, headings, links and blockquotes DO count. Code does not.
for f in "$@"; do
  n=$(awk '
    NR==1 && $0=="---" { fm=1; next }
    fm==1 && $0=="---" { fm=0; next }
    fm==1 { next }
    /^[ \t]*```/ { code = !code; next }
    code { next }
    { print }
  ' "$f" | tr -s '[:space:]' '\n' | grep -c '[[:alnum:]]')
  printf '%7d  %s\n' "$n" "$f"
done
```

**BR-1.** CI fails on any cap breach. A breach is resolved by deleting duplication or moving content to its owner, never by raising the cap without a sign-off recorded in Chapter 12.

---

## 5. Identifier namespaces

Identifiers are global and permanent. A retired ID is never reassigned.

| Prefix | Meaning | Owner |
|---|---|---|
| `VG-nn` | Document identity, **equal to the file index** | 00 |
| `SC-n` · `GV-n` | Schema and vector conventions | `schemas/v4/` |
| `C-nn` | Falsifiable claim about the system | 02 |
| `NC-nn` | Non-claim | 02 |
| `A-nn` | Design axiom | 02 |
| `N-nn` | Cross-cutting normative rule | 02 |
| `L-n` | Irreversible lock | 02 |
| `RSK-nn` | Risk register entry | 02 |
| `LT-n` | Layer dependency contract | 03 |
| `CC-n` | Concurrency rule | 03 |
| `FT-nn` | Failure taxonomy class | 03 |
| `CT-nn` | Contract rule (wire, schema, versioning) | 04 |
| `D-n` | Descriptor normalisation rule | 04 |
| `INV-n` | Invalidation-condition rule | 04 |
| `K-nn` | Kernel normative rule | 05 |
| `F-nn` | Kernel failure path | 05 |
| `SA-n` | Self-modification rule | 05 |
| `R0`–`R4` | Mutability class | 05 |
| `T-nn` | Threat-model entry | 05 |
| `AT-nn` | Architecture test | 05 |
| `MEM-n` | Memory rule | 06 |
| `V-nn` | Verification invariant | 06 |
| `CL-n` | Closure condition | 07 |
| `M-nn` | Measurement rule | 07 |
| `TK-nn` | Phase 0 ticket | 08 |
| `MF-nn` | Must-fail test | 08 |
| `ADR-nnnn` | Architecture decision record | 09 |
| `DEF-nn` | Deferred item | 10 |
| `REJ-nn` | Rejected item | 10 |
| `PR-n`, `BR-n`, `AR-n`, `CV-n`, `H-nn` | Registry rules | 00 |

**Anchoring.** A reference to a *rule* carries its ID: `05 §3 [K-07]`. A reference to a *topic* may cite the section alone. Section numbers are stable once frozen; renumbering a frozen document requires an ADR, because references resolve positionally.

---

## 6. Normative rules index — pointers only

Rule *text* lives once, in the owning document. This chapter indexes anchors only.

| Rule family | Count | Owner | Anchor |
|---|---:|---|---|
| Claims `C-*` | 12 | 02 | `02 §4` |
| Axioms `A-*` | 12 | 02 | `02 §5` |
| Non-claims `NC-*` | 12 | 02 | `02 §3` |
| Norms `N-*` | 21 | 02 | `02 §6` |
| Locks `L-*` | 6 | 02 | `02 §7` |
| Risks `RSK-*` | 15 | 02 | `02 §10` |
| Layer contracts `LT-*` | 8 | 03 | `03 §4` |
| Concurrency `CC-*` | 7 | 03 | `03 §8.2` |
| Failure taxonomy `FT-*` | 17 | 03 | `03 §14` |
| Contracts `CT-*` | 53 | 04 | `04 §0`, `§5`, `§16` |
| Descriptor `D-*` | 6 | 04 | `04 §5.5` |
| Invalidation `INV-1…INV-2` | 2 | 04 | `04 §10.3` |
| Kernel `K-*` | 49 | 05 | `05 §§0–6` |
| Failure paths `F-*` | 26 | 05 | `05 §2.3` |
| Self-modification `SA-*` | 6 | 05 | `05 §7` |
| Architecture tests `AT-*` | 12 | 05 | `05 §8` |
| Threats `T-*` | 8 | 05 | `05 §9` |
| Memory `MEM-*` | 7 | 06 | `06 §3` |
| Verification `V-*` | 13 | 06 | `06 §4` |
| Closure `CL-*` | 3 | 07 | `07 §1` |
| Measurement `M-*` | 28 | 07 | `07 §§2–9` |
| Must-fail `MF-*` | 37 | 08 | `08 §5` |
| Tickets `TK-*` | 13 | 08 | `08 §3` |
| Decisions `ADR-*` | 45 | 09 | `09 §§2–5` |
| Deferred `DEF-*` · rejected `REJ-*` | 24 | 10 | `10 §§1–2` |
| Schema `SC-*` · vectors `GV-*` | 18 | — | `schemas/v4/` |

**Coverage is generated, not asserted**: `tools/rule_test_map.py` enforces `CI-9`. Phase 0 baseline: 203 rules, 28 tested, 42 untestable, 133 uncovered.

**H-02 applied.** The pre-v4 rule appendices resolve here as pointers; their text sits with the owning sections above.

---

## 7. Supersession map — the pre-v4 corpus

Forensic record. **Nothing in the operating set requires this chapter** (`PR-5`); it lets a future reader trace any v4 statement to its origin and see what was dropped.

Destinations are v4 files per Chapter 2. Status: `MIGRATED` (carried) · `MERGED` (combined) · `AMENDED` (substantively changed) · `SUPERSEDED` (wrong or impossible, replaced) · `REJECTED` (not carried) · `VISION` (non-normative).

### 7.0 Source inventory

| ID | Pre-v4 file | Words |
|---|---|---:|
| S1 | `Vanguard_ACHF_Guia_Navegacao_Sintese_md.txt` | 1,466 |
| S2 | `vanguard_architecture_and_core_specification_v2.md` | 9,414 |
| S3 | `vanguard_02_loop_engineering_and_self_improvement_v2.md` | 7,951 |
| S4 | `vanguard_03_core_contracts_and_trajectory_schema.md` | 7,690 |
| S5 | `vanguard_04_kernel_and_security_specification.md` | 6,129 |
| S6 | `vanguard_05_phase_0_build_plan.md` | 2,598 |
| S7 | `vanguard_00_engineering_handbook.md` | 4,158 |
| S8 | `vanguard_achf_substrate_adequacy_review.md` | 4,907 |
| S9 | `01_Vanguard_ACHF_Parecer_Arquitetural_v3.md` | 4,418 |
| S10 | `02_Vanguard_ACHF_Especificacao_Base_e_Piloto_Fase_0_v3.md` | 5,224 |
| — | `REG-D_Consolidation_and_Migration_Plan.md` | 11,097 |

### 7.1 S2 — Architecture & Core Specification

| § | Content | Status | Dest. |
|---|---|---|---|
| 1 | Thesis, gap, claims C1–C7 | AMENDED | 02 §4 (→ C-01…C-12; LOC ceiling re-scoped to the policy kernel) |
| 2 | The inversion: agent loop ⊃ DAG, proof by construction | MIGRATED | 03 §2 |
| 3 | Design axioms A1–A12 | AMENDED | 02 §5 (A3, A6 corrected) |
| 4 | Layer topology, dependency lattice | MERGED | 03 §4 (intra-process discipline only) |
| 5 | Agent as data; budget vector; model routing | MERGED | 04 §9 |
| 6 | Execution loop | SUPERSEDED | 03 §6 (episode engine) |
| 7.1 | Dispatch sequence | AMENDED | 05 §2 (mediated-effect path only) |
| 7.2 | Ordering rules | MIGRATED | 05 §2 |
| 7.3 | `Decision` types incl. `ASK_*` as suspension | MIGRATED | 05 §2 |
| 7.4 | Attenuation algebra | AMENDED | 05 §4 (no silent intersection) |
| 7.5 | Mutable/immutable boundary | AMENDED | 05 §1 (→ R0–R4) |
| 8.1 | Provenance lattice | SUPERSEDED | 04 §3 (orthogonal axes) |
| 8.2 | Structural enforcement — no raw strings in context | MIGRATED | 04 §3 |
| 8.3 | Authority predicate; capability-widening classifier | AMENDED | 05 §5 (intent binding) |
| 9.1 | Why concurrency is not an optimisation detail | MIGRATED | 03 §8 |
| 9.2 | Read/write partition | SUPERSEDED | 03 §8 |
| 9.3 | Structured concurrency requirements | MIGRATED | 03 §8 |
| 9.4 | Parallel exploration | AMENDED | 03 §8 |
| 10 | Context engineering (layers, caching, compaction, dead ends, re-grounding, immutable brief) | MIGRATED | 03 §10 |
| 11.1 | Frozen atom set | AMENDED | 03 §7 (per environment) |
| 11.2 | Tool rules; diff-as-patch | MERGED | 03 §7 |
| 11.3 | Wire protocol; mock/cassette/live | MIGRATED | 04 §8, 01 §4 |
| 11.4 | Sandboxing; symmetric perimeter | AMENDED | 05 §6 |
| 12 | Subagents and composition | MERGED | 03 §5 |
| 13 | Playbooks; the rigidity dial | MIGRATED | 03 §11 |
| 14 | Verification invariants | MERGED | 06 §4 |
| 15 | Trajectory event schema | MERGED | 04 §12 |
| 16 | Registries; composition; freeze | MERGED | 03 §5, 04 §14 |
| 17 | Technology stack and seams | AMENDED | 02 §9, 03 §12 |
| 18 | Transparency surface | MIGRATED | 03 §13 |
| 19 | The canvas | REJECTED | 10 |
| 20 | Reference reconstructions; integrity constraints | MIGRATED | 07 §8 |
| 21 | Performance engineering | MIGRATED | 03 §12 |
| 22 | Failure taxonomy | MIGRATED | 03 §14 |
| 23 | Inheritance from the prototype | MIGRATED | 09, 08 §5 |
| 24 | Phasing and budget | SUPERSEDED | 08 |
| App. A | Normative rules N1–N20 | AMENDED | 02 §6 |

### 7.2 S3 — Loop Engineering, Memory & Self-Improvement

| § | Content | Status | Dest. |
|---|---|---|---|
| 1 | Governing constraint; mutable/immutable partition | AMENDED | 07 §1 |
| 1.1 | Closure conditions CL1–CL3 | MIGRATED | 07 §1 |
| 2 | Levels of loop engineering L0–L5 | MIGRATED | 07 §2 (vocabulary, never a backlog) |
| 3 | Inner-loop invariants | MERGED | 03 §6 |
| 4.1 | Memory is four problems | MIGRATED | 06 §3 |
| 4.2 | Write asymmetry | MERGED | 06 §3 (framing kept, gate replaced) |
| 4.3 | Retrieval quality is measurable | MIGRATED | 06 §3 |
| 4.4 | Long-horizon coherence | MIGRATED | 03 §10 |
| 4.5 | Consolidation as a verified process | MIGRATED | 03 §10 |
| 5.1–5.8 | Measurement doctrine | MIGRATED | 07 §5 |
| 6.1 | Outer-loop cycle | MIGRATED | 06 §6 |
| 6.2 | Distillation | MIGRATED | 06 §6 |
| 6.3 | Promotion rule | SUPERSEDED | 06 §5 (three-stage) |
| 6.4 | Demotion — anti-ossification | MIGRATED | 06 §5 |
| 6.5 | Selection as a contextual bandit | MIGRATED | 06 §6 |
| 6.6 | Why this compounds and prompt-tuning does not | MIGRATED | 07 §6 |
| 7.1–7.7 | Flywheel; corpus; credit assignment; training regimes | AMENDED | 07 §7 (+ data policy, licensing) |
| 8.1–8.4 | Optimisation versus leaps; exploitation trap | MIGRATED | 07 §6 |
| 9.1–9.6 | Verification without ground truth; calibration; transfer | MIGRATED | 06 §4, 07 §6 |
| 10.1–10.4 | Recursive self-improvement | AMENDED | 07 §7 (mechanism → release pipeline) |
| 11 | Risk register | MIGRATED | 02 §10 |
| 12 | Honest limits | MIGRATED | 02 §11 |
| App. A | Normative measurement rules | MIGRATED | 07 §5 |

### 7.3 S4 — Core Contracts & Trajectory Schema

| § | Content | Status | Dest. |
|---|---|---|---|
| 0.1 | Zod as source of truth | SUPERSEDED | 04 §0 (JSON Schema 2020-12 normative) |
| 0.2–0.4 | Wire rules, canonical JSON, naming | AMENDED | 04 §0 (RFC 8785/JCS) |
| 1 | Primitives, branded identifiers | AMENDED | 04 §1 (+ `IntString`, tenancy ids) |
| 2 | Content addressing, blob store | MIGRATED | 04 §2 (+ encryption hook) |
| 3 | Provenance, taint spans, authority request | MERGED | 04 §3 |
| 4 | Context blocks and conversation | MIGRATED | 04 §4 (+ epistemic state) |
| 5.1 | Effect classes; attenuation | SUPERSEDED | 04 §5 (capability model) |
| 5.2 | Descriptor; normalisation rules D1–D6 | MIGRATED | 04 §5 |
| 6 | Budget, reservation, lease | AMENDED | 04 §6 (+ evaluation budget) |
| 7 | Tool types; frozen atoms | AMENDED | 04 §7 (− `commutative`; + read/write sets) |
| 8 | Model interface; wire message shape | MIGRATED | 04 §8 |
| 9 | Task, Agent, Playbook | MERGED | 04 §9 (+ spec/plan/proposal/request separation) |
| 10 | Verdict and evidence | MERGED | 06 §4 (+ evaluator classes, invalidation conditions) |
| 11 | Instrument tuple | MERGED | 07 §5 (∪ substrate profile) |
| 12.1–12.5 | Trajectory envelope, event union, stream invariants, storage | MERGED | 04 §12 (+ recovery events; SQLite/WAL) |
| 12.6 | Corpus projection; admission filter; contamination ledger | AMENDED | 07 §7 (+ data policy, licensing) |
| 13 | Port interfaces | AMENDED | 04 §13 (+ environment adapter; containment report) |
| 14 | Configuration file schemas | MIGRATED | 04 §14 |
| 15 | Cross-language contract | AMENDED | 04 §15 (two languages at first lock) |
| 16 | Versioning and compatibility | AMENDED | 04 §16 (+ migration rehearsal) |
| 17 | Conformance suite | MIGRATED | 04 §17 |
| **18** | **Module layout** | **MERGED** | **01 §9** *(H-01)* |
| **App. A** | **Normative rules index** | **SUPERSEDED** | **00 §6** *(H-02, pointer-only)* |

### 7.4 S5 — Kernel & Security Specification

| § | Content | Status | Dest. |
|---|---|---|---|
| 0.1 | TCB contents; LOC ceiling | SUPERSEDED | 05 §0 (policy kernel + declared transitive TCB) |
| 0.2 | What is explicitly not claimed | MIGRATED | 02 §3 |
| 0.3 | Assurance method | MIGRATED | 05 §0 (+ fault injection, recovery) |
| 1.1–1.2 | TCB partition; mechanism not policy | AMENDED | 05 §1 (→ R0–R4) |
| 1.3 | Security claim S1(a)–(f) | AMENDED | 05 §1 (+ resource scoping; + clause on runtime/key/updater reachability) |
| 2.1 | Dispatch sequence | AMENDED | 05 §2 (mediated effects) |
| 2.2 | Ordering rules | MIGRATED | 05 §2 |
| 2.3 | Failure path enumeration | MIGRATED | 05 §2 (+ recovery paths) |
| 2.4 | Idempotence and replay | MERGED | 05 §2 (+ effect receipts) |
| 2.5 | Suspension and approvals | MERGED | 05 §2 (+ risk tiers) |
| 3 | Grants: structure, binding, expiry, single use | AMENDED | 05 §3 (+ resource selectors; cross-process integrity) |
| 4 | Attenuation algebra | AMENDED | 05 §4 (+ resource/constraint attenuation; explicit denial) |
| 5.1–5.2 | Provenance lattice; predicate | SUPERSEDED | 05 §5 (axes) |
| 5.3 | The two operands that failed silently | MIGRATED | 05 §5 |
| 5.4 | What provenance does not do | MIGRATED | 05 §5 (+ causal-attribution limit) |
| 6 | Sandbox perimeter; containment honesty | AMENDED | 05 §6 (containment report + risk ladder) |
| 7.1–7.4 | Verifier immutability; double probe; `NONE`; confidence classes | MERGED | 06 §4 |
| 8 | Boundary as mechanism; architecture tests | MIGRATED | 05 §8 (+ cross-process identity tests) |
| 9.1–9.4 | Threat model: assets, attack trees, coverage | MIGRATED | 05 §9 (+ release-pipeline and recovery-forgery threats) |
| 9.4 | Self-flagged gap: a control without a must-fail test | MIGRATED | 08 §5 |
| 10 | Audit checklist | MIGRATED | 05 §10 |
| **App. A** | **Normative rules index** | **SUPERSEDED** | **00 §6** *(H-02, pointer-only)* |

### 7.5 S6 — Phase 0 Build Plan

| § | Content | Status | Dest. |
|---|---|---|---|
| 0 | Scope; parallel-in-first-commit rationale | AMENDED | 08 §0 (→ increments A/B/C) |
| 1–3 | Repo layout, tooling, CI gates | AMENDED | 08 §1–§3 (+ fault injection, schema drift, recovery, supply chain) |
| 4 | Tickets | SUPERSEDED | 08 §4 (compressed set) |
| 4.1 | Notes on specific tickets | MIGRATED | 08 §4 |
| 5 | Must-fail suite | AMENDED | 08 §5 (impossible test replaced; suite extended) |
| 6 | Exit criterion | AMENDED | 08 §6 (+ measurable routing threshold) |
| 7 | ADR seed entries | MERGED | 09 |
| 8 | Working agreements | MIGRATED | 01 §5 |
| 9 | What to watch for | MIGRATED | 08 §7 |

### 7.6 S7 — Engineering Handbook

| § | Content | Status | Dest. |
|---|---|---|---|
| M1 | The loop is the program | AMENDED | 01 §1 (→ the episode is the program) |
| M2 | Everything is a Tool or a Context Source | SUPERSEDED | 01 §1 (→ four extension forms) |
| M3 | One choke point, no exceptions | AMENDED | 01 §1 (→ the broker grants; the sandbox contains) |
| M4 | Provenance constrains authority | AMENDED | 01 §1 (+ axes) |
| M5 | The verifier is outside everything | MIGRATED | 01 §1 |
| M6 | A gate that cannot fail is not a gate | MIGRATED | 01 §1 (+ satisfiability check) |
| — | M7/M8/M9 (new) | ADDED | 01 §1 |
| 2 | SOLID, concretely | MIGRATED | 01 §2 |
| 2.1 | DRY, and where it becomes a trap | MIGRATED | 01 §2 |
| 3 | The shape of a change | MIGRATED | 01 §3 |
| 4, 4.1, 4.2 | Testing taxonomy; mock/cassette/live; what not to test | MIGRATED | 01 §4 (+ fault injection, recovery, conformance vectors) |
| 5 | Practices; when you are stuck | MIGRATED | 01 §5 |
| 6 | Review checklist | AMENDED | 01 §6 (+ no-special-cases constraint) |
| 7, 7.1–7.4 | ADR format; the reversal condition | MIGRATED | 01 §7, 09 |
| 8 | The Deferred Register | MIGRATED | 10 |
| 9 | Repository manifest | AMENDED | 01 §9 (merged with S4 §18, S10 §17) |
| 10 | Glossary | AMENDED | 01 §10 |
| App. | The ten rules | AMENDED | 01 §10 |

### 7.7 S8 — Substrate Adequacy Review

| § | Content | Status | Dest. |
|---|---|---|---|
| 0 | Verdict: do not rethink; change six things | MIGRATED | 02 §8 |
| 1 | What transfers unchanged | MIGRATED | 02 §8 |
| 2 | The reframe: promotion machinery already implements the improvement relation | MIGRATED | 02 §8, 06 §6 |
| 3.1–3.5 | Five structural gaps with severity | MIGRATED | 02 §8 |
| 4.1 | Competence space as a first-class artifact | AMENDED | 04 §10 (array → graph) |
| 4.2 | Operators as data | MIGRATED | 03 §5, 04 §9 |
| 4.3 | Substrate invariance as protocol and test | MERGED | 06 §5 (+ refresh cadence) |
| 4.4 | Promotion as a partial order | SUPERSEDED | 06 §5 (three-stage) |
| 4.5 | Epistemic state as a second lattice | MERGED | 04 §4 (+ invalidation conditions) |
| 4.6 | One non-coding reference environment | MIGRATED | 08 §4 |
| 5.1 | Novelty is not operationalisable | MIGRATED | 10, 06 §5 (observable, never an objective) |
| 5.2 | Evaluation regress in the self-generated-criterion requirement | MIGRATED | 10 |
| 5.3 | Level taxonomies produce complexity without capability | MIGRATED | 10, 07 §2 |
| 5.4 | Where the external program is right | MIGRATED | 02 §8 |
| 6 | Lock now versus open | MIGRATED | 02 §7 |
| 7 | Dual-track weighting and the hard constraint | MIGRATED | 02 §8 |
| **8** | **Revised document plan** | **SUPERSEDED** | **00 §2** *(H-04; the deferred discovery document → 10)* |
| **9** | **Revised phasing; funding-phase exit criterion** | **MIGRATED** | **02 §8, 08 §6** *(H-04)* |
| 10 | Impoverished-ontology transfer experiment; controls A–D | MIGRATED | 07 §8 |
| 11 | Honest limits of the review | MIGRATED | 02 §11 |
| **12** | **Summary** | **SUPERSEDED** | **02 §1** *(H-04; restatement of §§0–7, no unique content)* |

### 7.8 S9 — Architectural Review

| § | Content | Status | Dest. |
|---|---|---|---|
| 0 | Executive verdict; five over-stated guarantees | MIGRATED | 02 §3, 09 |
| 1 | Approve / adjust / reject table | MIGRATED | 09 |
| 1.1 | Disposition of annexes | SUPERSEDED | 00 §7 |
| 2.1 | Self-modification answer | MIGRATED | 05 §7 |
| 2.2 | Deterministic oracles insufficient; layered memory gate | MIGRATED | 06 §3 |
| 2.3 | Deferring autonomy is right; deferring its contracts is wrong | MIGRATED | 04 §9 |
| 2.4 | What to anticipate for search, process rewards, reflection | MIGRATED | 07 §9 |
| 3 (P0.1–P0.5) | Capabilities, choke point, planes, concurrency, persistence | MIGRATED | 05, 03, 04 |
| 3 (P1.1–P1.4) | Competence graph, provenance axes, trajectory privacy, secure update | MIGRATED | 04, 05, 06 |
| 3 (P2.1–P2.3) | Evaluator naming, experimental breadth, frontier as archive | MIGRATED | 06, 07 |
| 4 | Where the architecture breaks outside coding | MIGRATED | 03 §7 |
| 5 | Stack validation | MIGRATED | 09 |
| 6 | New system thesis | MIGRATED | 02 §1 |
| 7 | Revised roadmap | AMENDED | 08 §0 (compressed) |
| 8 | GO criteria for the first functional commit | MIGRATED | 08 §6 |
| 9 | Primary sources | MIGRATED | 09 |
| 10 | Conclusion; the one-line correction | MIGRATED | 02 §1 |

### 7.9 S10 — Consolidated Base Specification

**H-03 applied — every row carries an explicit status.**

| § | Content | Status | Dest. |
|---|---|---|---|
| 0 | Precedence rule | AMENDED | 00 §1 (generalised to the registry) |
| 1 | Mission; non-claims; episode as unit of execution | MERGED | 02 §1–§3 |
| 2 | Normative vocabulary | MIGRATED | 01 §10 |
| 3 | Plane architecture | MIGRATED | 03 §3 |
| 4 | Root of trust; policy kernel vs transitive TCB; SA-1…SA-6; R0–R4 | MIGRATED | 05 §0–§1, §7 |
| 5 | Capability model; resource selectors; attenuation; grants across processes; shell | MIGRATED | 04 §5, 05 §3–§4 |
| 6 | Episode engine; terminal states; retry; no-progress; concurrency | AMENDED | 03 §6, §8 (+ independence groups) |
| 7 | Environment adapter; Git; TableWorld; irreversible effects | MIGRATED | 03 §7 |
| 8 | Competence and evidence graph; quadrants; lifecycle; operators as data | AMENDED | 04 §10, 06 §2 (+ mandatory invalidation conditions) |
| 9 | Memory without degradation; claim pipeline; MEM rules; contradictions | MERGED | 06 §3 |
| 10 | Evaluation and promotion; evaluator classes; hard constraints; frontier | MERGED | 06 §4–§5, 07 §4 |
| 11 | Substrate invariance; substrate profile; migration | AMENDED | 06 §5, 07 §5 (+ refresh cadence, substrate debt) |
| 12 | Event envelope; minimum events; storage; crash semantics; data policy | AMENDED | 04 §12 (+ tenancy and data-policy fields, recovery events) |
| 13 | Contracts and wire format; canonicalisation; integers; unknown fields | AMENDED | 04 §0, §13, §16 (+ migration rehearsal) |
| 14 | Search, process rewards, reflection preparation | MIGRATED | 07 §9 |
| 15 | Approved stack; containment report | MIGRATED | 02 §9, 05 §6 |
| 16 | Phase 0 pilot; hypotheses; increments; tickets; must-fail; exit criteria | AMENDED | 08 (compressed: three processes, two-language vectors) |
| 17 | Initial repository layout; dependency direction | MERGED | 01 §9 |
| 18 | Initial ADRs | MIGRATED | 09 |
| 19 | Summarised norms | MERGED | 02 §6 |
| 20 | Implementation decision; walking skeleton | AMENDED | 08 §0 (gate sequencing retained, scope compressed) |

### 7.10 S1 — Navigation & Synthesis Guide

| § | Content | Status | Dest. |
|---|---|---|---|
| 1 | Per-document analysis | SUPERSEDED | 00 §7 |
| 2 | The project in one sentence | AMENDED | 02 §1 |
| 3 | Layered biological architecture | VISION | 12 |
| 4 | How the system learns and evolves | MIGRATED | 07 §6 |
| 5 | Unified analogies | VISION | 12 |
| 6 | Evolution vision | MIGRATED | 02 §8 |
| 7 | Concept navigation | SUPERSEDED | 00 §2 |
| 8 | The six priority amendments | MIGRATED | 02 §8 |
| 9 | Cosmological principle | VISION | 12 |

### 7.11 Harvest corrections

| ID | Correction | Resolution |
|---|---|---|
| **H-01** | S4 §18 (Module layout) had no disposition | → `01 §9`, merged with S7 §9 and S10 §17 |
| **H-02** | S4 App. A and S5 App. A (rule indexes) had no disposition | → `00 §6`, pointer-only; rule text lives with its owning section |
| **H-03** | S10 rows carried destinations but no statuses | All 21 rows now carry an explicit status (§7.9) |
| **H-04** | S8 §§8, 9, 12 had no dispositions | §8 SUPERSEDED by `00 §2`; §9 MIGRATED to `02 §8` and `08 §6`; §12 SUPERSEDED by `02 §1` |

---

## 8. REG-D content migration ledger

REG-D was scaffolding with a stated end state. It retires once every row below is `DONE`.

| REG-D content | Destination | Rule |
|---|---|---|
| Twelve adjudications, **with reasoning** | `09` | Each becomes an ADR carrying the losing alternative and its reversal condition |
| Fourteen corrections of false/impossible claims | `09` (rationale) + `08 §5` (must-fail tests) | A correction without a test is not migrated |
| Removals and deferrals | `10` | Each carries a reversal condition, or states that it has none |
| New requirements and cross-lineage gaps | Owning normative document per Chapter 7 | Each requires a named owner section and a ticket before REG-D retires |
| The recurring failure mode (premature formalisation) and its standing exception | `01 §1` | Becomes a mental model, not a footnote |
| Deletion contract, coverage checks, archive protocol | `00 §§10–11` | This document |
| Independent-review convergence finding | `11` | Secondary evidence; not verbatim |
| Source inventory and harvest matrix | `00 §7` | Done |

---

## 9. CI rules

| ID | Rule | Method |
|---|---|---|
| CI-1 | Chapter 2 and `docs/v4/` are in exact bijection | Script |
| CI-2 | No v4 file names a pre-v4 source, except `00 §7` | `tools/audit_v4.py` |
| CI-3 | Every cross-reference resolves | `tools/audit_v4.py` |
| CI-4 | No identifier is defined in two documents | `tools/audit_v4.py` |
| CI-5 | Per-document and subtotal caps hold | `tools/wordcount_v4.sh` |
| CI-6 | Every schema validates against JSON Schema 2020-12 and has golden vectors | Schema job |
| CI-7 | Every rule ID prefix is declared in Chapter 5 | `tools/audit_v4.py` |
| CI-8 | Document 12 carries its header; no other document references it | Grep |
| CI-9 | Every rule maps to a test, or is marked untestable with justification | `rule_test_map.py` |

---

## 10. Acceptance verification

The pre-v4 sources may be removed from the working set only when all of the following hold.

| # | Check | Method |
|---|---|---|
| CV-1 | Every Chapter 7 row has a status and destination; no `TBD` | Manual |
| CV-2 | Every destination resolves in the v4 set | `audit_v4.py` |
| CV-3 | Every `REJECTED` row appears in `10` with reasoning and reversal condition | Script |
| CV-4 | Every `VISION` row appears in `12` under its header | Script |
| CV-5 | Every `SUPERSEDED` row has a replacement and, where behavioural, a test ID | Manual |
| CV-6 | Every adjudication in `09` **with reasoning** | Manual |
| CV-7 | Every corrected false claim has a must-fail test in `08 §5` | Script |
| CV-8 | Every migrated new requirement and gap has an owning section and a ticket | Script |
| CV-9 | Every ADR has a reversal condition, or states it has none and what would invalidate it | Script |
| CV-10 | Chapter 2 complete; Chapter 8 fully `DONE` | Manual |
| CV-11 | CI-1…CI-9 pass | CI |
| CV-12 | Normative subtotal within budget | CI |
| CV-13 | **Comprehension gate** | External reader |

> **CV-13.** An engineer who did not author v4, reading **only** the v4 set, must state unaided: which document is normative for a given contract and how they know; the three closure conditions and why each matters; the self-modification contract and why in-place modification is prohibited; why a verb-only permission set cannot authorise; and why a passing suite does not establish semantic truth. If they cannot, v4 is not done. **Not waivable.**

---

## 11. Archive and retirement protocol

| ID | Rule |
|---|---|
| AR-1 | **Nothing is deleted before acceptance.** Pre-v4 files stay untouched until acceptance |
| AR-2 | Before removal, an annotated git tag (`pre-v4-corpus`) preserves the pre-v4 state as the permanent evidentiary record |
| AR-4 | Archived material is never edited; a correction to history is a note here, not a change to the artifact |
| AR-5 | Normative text is English-only; translations sit outside the v4 set, clearly marked |
| AR-6 | The prototype repository is frozen; its only role is forensic source for the must-fail suite |
| AR-7 | A `DISPOSABLE` document retires at phase exit, its surviving contracts having first moved to a `NORMATIVE` owner |

---

## 11.1 Acceptance state

| Item | State |
|---|---|
| Documents | 13 of 13 authored; `02`–`08` frozen |
| `CI-1`…`CI-8` | **PASS** — `.github/workflows/ci.yml`, hard-failing |
| `CI-9` | **RED by construction** — Phase 0 exit gate; regression-blocking at 133 |
| `CV-1`…`CV-12` | **PASS** — `tools/cv_checks.py`, 12/12 |
| `CV-13` | **OPEN** — packet at `cv13/`, requires a named non-author reader. **Not self-certifiable** |
| Schemas | 7 writer + 7 reader, valid 2020-12; all `DRAFT` |
| `SC-7`, `SC-12` | **OPEN** — assigned to `TK-01` |
| Retirement | Pre-v4 sources **untouched**; tag `pre-v4-corpus` not yet created; removal awaits PL acceptance |

**Verdict: DEVELOPMENT READY pending `CV-13` and PL acceptance.** Every mechanical gate passes. The two remaining gates require a human by design.

---

## 12. Change log

| Date | Change | By |
|---|---|---|
| 2026-08-14 | Skeleton created; Ch. 1–5, 7–11 populated; H-01…H-04 applied; `AR-3` retired (ID not reused); `LT`/`CC`/`NC` namespaces registered |
| 2026-08-14 | `02`, `03` frozen | Tech Lead |
| 2026-08-14 | `04` frozen for prose; `04 §8`/`§10` anchor collision corrected; five schemas authored and validated, held at `DRAFT` pending `SC-7` | Tech Lead |
| 2026-08-14 | `05` (full rigor), `06`, `07` authored | Tech Lead |
| 2026-08-14 | **Review fixes.** `VG-nn` remapped to the file index; anchoring rule corrected; `INV-1` pointer repaired; `CI-9` added; writer/reader schema profiles split (`SC-10`) | Tech Lead |
| 2026-08-14 | `08`, `09`, `10`, `01`, `11`, `12` authored. **All 13 documents exist; audit resolves every reference.** Chapter 6 populated from the authored set | Tech Lead |
| 2026-08-14 | **`BR-1` sign-off.** Registry cap raised 4,000 → 4,500 for the completed Chapter 6 index. Supporting envelope unchanged | Tech Lead |
| 2026-08-14 | Closure: `CI-1`…`CI-9` wired; `CV-1`…`CV-12` implemented and passing; `CV-13` packet prepared; backlog generated. Two checker defects fixed — blockquote-defined rules were invisible to every extractor (203 rules, not 183) and one harvest destination pointed at a section of `01` that does not exist | Tech Lead |
| 2026-08-14 | **`04` unfrozen and corrected.** Two lock-class defects (`ADR-0039` grant binding, `ADR-0040` selector algebra) plus `ADR-0041`…`0044`. `02`, `03`, `05` amended in consequence; `06`, `07` unaffected. `SC-12` added: no schema locks while any `04` type lacks an artifact | Tech Lead |
