---
id: VG-10
file: 10_vanguard_deferred_and_rejected_register_v040.md
title: "Vanguard v4.0 — Deferred & Rejected Register"
version: 4.0.0
status: LIVING
authority_scope: >
  Capabilities deliberately not built, and ideas deliberately not adopted, each
  with its reasoning and its reversal condition.
supersedes: none (v4 is the first version of this document)
superseded_by: none
budget_words: 2000
owners: [Tech Lead]
last_reviewed: 2026-08-14
---

# Vanguard v4.0 — Deferred & Rejected Register

> **Why this exists.** A deferral that is not written down becomes an omission, and an omission becomes a surprise. Every entry states what would bring it back — or states plainly that nothing would, and what that assumes.

A **deferral** is a capability worth building later. A **rejection** is an idea examined and declined. The distinction matters: deferrals are scheduled work, rejections are closed questions that may reopen only on new evidence.

---

## 1. Deferred

| # | Deferred | Why now | Reversal condition |
|---|---|---|---|
| `DEF-01` | Graphical authoring canvas | A graph is an excellent authoring and visualisation surface and a poor runtime substrate. The surface is worth building; it is not worth building first | A recorded trajectory renderer exists and users ask to *edit* rather than only inspect |
| `DEF-02` | Semantic memory in Phase 0 | The claim pipeline (`06 §3`) needs an evaluator and a corpus, neither of which exists yet | Phase 2, with the memory ticket and dedicated memory-write gating tests in a clean `MF-` namespace allocation |
| `DEF-03` | General subagents | Operator invocation covers the Phase 0 cases; general composition adds budget-tree and cancellation surface before the loop is proven | Phase 2, when a real task needs depth beyond operator invocation |
| `DEF-04` | Protocol integrations, browser, web search, retrieval index | Each is a registry entry plus configuration by construction (`02 [C-02]`). Building them early proves nothing and costs perimeter surface | Phase 2+, or earlier if a dogfood opt-out reason names one |
| `DEF-05` | Systems-language index | The orchestration path is under five milliseconds against seconds of inference. Optimising it is optimising the row that does not matter | A measured number on a real repository crosses a stated threshold — and the experiment that would produce it is already named in `07 §5.8` |
| `DEF-06` | Search over trajectories, process rewards, reflection | Not built in Phase 0; **their contracts are** (`07 §10`). Deferring the capability is correct; deferring the contracts would make the retrofit a corpus migration |
| `DEF-07` | Autonomous updater as a runtime component | `R0` and `R1` promotion is a human action (`05 [SA-5]`). Phase 0 has no Evolution-plane process at all | Phase 1, as a distinct identity — never as autonomous promotion for those classes |
| `DEF-08` | Public benchmark participation | A number produced before the A/A floor exists is the premature-measurement error this programme exists to avoid | Phase 3, once `07 §5` apparatus runs |
| `DEF-09` | Training on the corpus | Requires corpus opt-in, contamination tracking per instance, and licensing (`04 [CT-16]`, `07 [M-20]`) | Phase 3, and never before the adversarial verifier audit |
| `DEF-10` | A dedicated discovery or competence-expansion document | Premature: the machinery it would specify does not exist, and specifying it now would formalise guesses | When `06 §5` promotion has run on real artifacts and produced a pattern worth naming |
| `DEF-11` | Compaction beyond a recency window in Phase 0 | Strategy comparison is a `07 §5.8` experiment, and there is no instrument yet | Phase 2, once consolidation loss is measurable |
| `DEF-12` | Approvals, suspension and session resume | Phase 0 runs in benchmark-free interactive mode with a human present throughout | **Superseded by ADR-0057 for privileged effects in beta.** Descriptor-bound human approval for `fs.patch` (Sink Class: `privileged`) lands in Phase 2 (Sprint 6). General multi-turn session suspension outside privileged effects remains deferred |

---

## 2. Rejected

| # | Rejected | Why | Would reopen if |
|---|---|---|---|
| `REJ-01` | Runtime workflow graph or topology language | Strictly less expressive than a loop that can invoke a loop, at roughly ten times the machinery. Proof by construction in `03 §2.2` | A reference reconstruction proves inexpressible without one |
| `REJ-02` | Levels as a roadmap (`L6`, `L7`, …) | A level taxonomy invites treating movement up the ladder as progress. Movement is progress only when an instrument says so (`07 [M-01]`) | Never. The vocabulary stays; the backlog does not |
| `REJ-03` | Novelty as an optimisation objective | Any operational novelty metric is trivially gamed by generating unusual junk. Observable, never optimised (`06 §5.2`) | A metric provably resistant to adversarial generation — none is known |
| `REJ-04` | Self-generated evaluation criteria as a promotion gate | An evaluation regress: a system that authors the criteria it is judged against has no exteriority, which is `CL-1` violated at the definition rather than the implementation | Never within this programme's assumptions |
| `REJ-05` | Commutativity as a tool property | Commutativity belongs to the resource, not the verb. A static boolean is false the moment the resource is a queue, a clock or a remote service | Never |
| `REJ-06` | A single ordered provenance lattice | Conflates five independent questions and forces one number to answer all of them. Replaced by orthogonal axes (`04 §3.1`) | Never |
| `REJ-07` | Shell classification as a security boundary | It is a parser, and parsers can be parsed around. A security argument resting on parsing shell correctly is a weak argument | Never — the perimeter is the boundary |
| `REJ-08` | Governance as TCB enforcement | A policy is routed around by a motivated optimiser and forgotten by a tired human, and cannot be checked at runtime by the thing it constrains | Never. Enforcement is at the dispatcher |
| `REJ-09` | "Cognitive operating system" as architectural language | Promises scheduling, isolation, resource ownership and lifecycle the system does not provide. It lives in `12`, never in a specification | When the system provides them |
| `REJ-10` | Biological, cosmological and particle-physics analogies as specification content | They leaked into specifications and produced the two-lineage divergence. Quarantined as non-normative in `12` | Never in a normative document |
| `REJ-11` | Scalar reward for promotion | Self-reinforcing through the corpus (`ADR-0015`) | A domain where all dimensions are genuinely commensurable |
| `REJ-12` | An always-on full-content training capture | Content may be secret, personal or unlicensed. Capture is by policy; the corpus is separately opt-in (`06 [MEM-7]`) | Never |

---

## 3. How an entry moves

A deferral becomes work when its reversal condition is met — at which point it is deleted from §1 and appears as a ticket, with the ADR recording the transition. A rejection reopens **only** on evidence named in its final column; a rejection reopened on preference is how a closed question becomes an argument that recurs every quarter.

**Nothing is removed from this register silently.** An entry that disappears without a corresponding ADR is a defect in the process, not a tidy-up.
