---
id: adr-0094-product-first-m4-and-optional-assurance
adr: 0094
class: decision
authority: binding-decision
canonical_for:
  - product-first-m4-gate
  - optional-assurance-tier
  - m5-opening-condition
status: accepted
owner: engineering-director
version: "0.7.0"
last_verified: 2026-08-25
accepted_date: 2026-08-25
extends:
  - ADR-0088
  - ADR-0089
supersedes:
  - ADR-0088-m4-exit-gate-only
superseded_by: null
---

# ADR-0094 — Product-first M-4 and optional assurance

## Context

AETHER's canonical composition, layer boundaries, effect mediation, durable ledger, and recovery
machinery are implemented, but M-4 was defined as a nine-row adversarial-assurance ceremony requiring
rootless containment and a separately isolated Ed25519 evaluator. That gate tests a valuable assurance
mode, but it blocks product learning on infrastructure that is not required to discover whether the
framework can build a useful coding agent or generalize to a second domain.

The immediate product objective is a CLI in the class of Claude Code or Codex: a real model inspects a
workspace, calls typed tools, edits files, runs verification, persists its session, and can resume.
The enduring architectural priority is separation of `domain <- ports <- kernel <- agency <- runtime
-> adapters`, not mandatory process isolation for every run.

## Decision

1. **M-4 becomes the product coding proof, allocated as RF-95.** One real provider MUST complete a
   non-trivial coding task through the canonical manifest/composition, `Runtime.run_composed`, ordinary
   tool effects, and a file-backed SQLite-WAL ledger. The result MUST include a real workspace diff,
   verification command receipt, complete trajectory, and successful fresh-process session replay or
   continuation. No fake, cassette, stitched trace, alternate driver, or manual ledger repair qualifies.
2. **RF-85 is retained, not weakened.** Its nine-row hermetic foundation audit remains the optional
   high-assurance certification profile. It no longer blocks M-4, M-5, or normal product use and MUST
   not be represented as complete without its original evidence.
3. **Assurance is a profile concern.** `product` is the default interactive profile: host workspace,
   explicit approval policy, durable SQLite-WAL, real model adapter, and optional evaluation. `hermetic`
   retains containment, preregistration, exterior evaluator, signature, and promotion eligibility.
   Absence of assurance remains explicit in `D_R`; a product run may not claim hermetic promotion.
4. **Layer boundaries remain binding.** Coding behavior stays in the coding pack, tools/adapters, and
   client. Runtime owns composition, lifecycle, persistence, and sessions. Agency owns the generic turn
   mechanism. Kernel owns generic effect authority only. No coding, formal, research, evaluator, or
   sandbox semantics may move into the kernel.
5. **M-5 opens after RF-95.** M-5 first implements a small deterministic formal/structured-reasoning
   pack with an independently checkable witness. RF-86 continues to prohibit semantic changes to the
   frozen substrate during that proof. Research is the next product pack, not the sole initial
   generality falsifier.
6. M7-01 remains measurement-only and parallel. M-6 through M-8 remain dependency-ordered; this ADR
   does not authorize delegation, concurrency, or topology implementation.

## RF-95 acceptance

The proof task and expected verifier command are fixed before execution. One run must demonstrate:

- a live provider and attributable model/usage;
- canonical composition and the product execution profile in `D_R`;
- at least one repository observation, one authorized file mutation, and one process verification;
- a non-empty before/after diff and passing task-specific tests or checks;
- file-backed WAL with a complete terminal trajectory;
- a new process reopening the ledger and reconstructing the same terminal state;
- no fake/cassette model, alternate runtime, hand-edited event, or post-hoc stitched evidence.

Independent cryptographic evaluation, uid separation, and Bubblewrap are not RF-95 requirements.
They remain RF-85 requirements.

## Consequences

The project gets a short path to product feedback without deleting its stronger assurance machinery.
M-4 can fail on actual agent usefulness, tool ergonomics, context quality, provider integration,
persistence, or recovery rather than on evaluator provisioning. M-5 can then test the abstraction
scientifically. Security claims remain honest because product and hermetic identities cannot be
confused and RF-85 keeps its original meaning.

The first implementation slice adds the `product` profile, makes declared SQLite-WAL persistence the
bootstrap default, routes the generic CLI to that profile, and adds RF-95 regression coverage. It does
not change the kernel, episode engine, event semantics, or evaluator implementation.
