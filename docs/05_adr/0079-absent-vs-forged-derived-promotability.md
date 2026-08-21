---
adr: 0079
title: "Absent-vs-forged guardrails and derived promotability"
status: accepted
accepted_date: 2026-08-21
source_section: "ALFA Tier S+ Director Ratification"
implementation_milestone: "M-3 / v0.6.2"
---

# ADR-0079: Absent-vs-forged guardrails and derived promotability

**Context.** Coding, formal, research, and compute-only packs do not all require the same exterior
oracle, but an unsigned or unreachable required evaluator must never be mistaken for a deliberately
lower-assurance composition. Without an explicit model, deadline pressure creates debug bypasses
that turn missing evidence into apparent success.

**Decision.**

1. Evaluation evidence has exactly three states:
   - **present/valid:** required exterior evidence is correctly signed and bound;
   - **absent/declared:** the frozen manifest explicitly declares no evaluator, with a reason and
     assurance class that is ineligible for promotion;
   - **forged/broken:** evidence was required or claimed but is missing, unsigned, self-produced,
     wrongly bound, unreachable, or tampered.
2. Forged/broken maps to instrument error or tamper evidence. It never degrades into declared
   absence and never becomes a passing result.
3. Declared absence is selected before execution, enters the resolved graph and `D_H`, and cannot
   be chosen after observing an outcome.
4. `unattributable_for_promotion` and promotion eligibility are **derived** from the resolved
   graph, evidence state, trajectory completeness, and signature verification. They are absent
   from author-controlled manifest/plugin fields and cannot be changed by a runtime flag.
5. `evaluation: none` means no verdict. It does not mean an easier verdict. A declared-absent run
   may complete operationally but cannot license verdict-gated memory, enter a DPO pair, populate
   a verified memo, or move a production pointer.
6. Evidence policy is independent of effect mediation. Compute-only or formal packs remain subject
   to capabilities, selector ceilings, budgets, sandbox policy, event writer authority, and the
   universal mechanism.
7. The trajectory records the guardrail declaration, evidence state, null/signed verdict, bounded
   absence reason, and derived eligibility.
8. Existing non-negotiables remain: single writer; complete lineage; fail-closed selectors; WAL
   truth; attenuated recursion; signatures on every claimed verdict; and JCS as the sole byte source.

**Bound falsifiers.** RF-34: declared absence compiles and changes `D_H`. RF-35: an unsigned
verdict is rejected even under declared absence. RF-36: promotability is derived and cannot be
written by a manifest/plugin. RF-37: in-process execution still requires explicit policy.

**Alternatives rejected.** Mandatory UID-10002 evaluation for every pure computation; unsigned
test verdicts; environment-variable bypasses; or a manifest field such as `promotable: true`.

**Reversal condition.** Any declared-absent composition producing promotion-eligible output. Until
the derivation defect is repaired, the affected guardrail becomes mandatory and promotion stops.

**Owner · status.** CIO / Principal Systems Architect · accepted by Engineering Director ·
2026-08-21
