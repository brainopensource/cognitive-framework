---
id: VG-11
file: 11_vanguard_design_convergence_evidence_v040.md
title: "Vanguard v4.0 — Independent Design Convergence (Attested Summary)"
version: 4.0.0
status: EVIDENCE — secondary
authority_scope: >
  A record of the convergence observed between two independently-produced
  design lineages, and of the divergences that required adjudication.
  States no contract.
supersedes: none
superseded_by: none
budget_words: 1000
owners: [Tech Lead]
last_reviewed: 2026-08-14
---

# Independent Design Convergence — Attested Summary

> **Evidentiary status, stated first because it bounds everything below.**
>
> This is a **secondary** account. The primary artifacts — the two independent design reviews as written — are **not preserved in the v4 set and were not available when this summary was compiled.** What follows is reconstructed from the consolidation analysis that adjudicated between them.
>
> **No claim of verbatim preservation is made.** Where this document and a primary artifact ever disagree, the primary artifact wins, and this one is corrected by a note rather than an edit.

---

## 1. What was observed

Two design lineages were produced independently, from a shared problem statement, without either author seeing the other's work in progress. One approached the system from execution mechanics; the other from competence and evaluation.

They converged on a substantial set of structural conclusions. That convergence is the finding this document records.

---

## 2. Convergent conclusions

Reached independently by both lineages:

| # | Conclusion |
|---|---|
| 1 | A static workflow graph is the wrong runtime substrate for agentic execution; an agent loop that can invoke an agent loop is strictly more expressive |
| 2 | Every effect must pass a single authorisation point, and that point must be structurally incapable of being bypassed |
| 3 | The evaluator must be unreachable from everything it judges, or every downstream number is worthless |
| 4 | Measurement apparatus is not optional infrastructure — without it, improvement claims are unfalsifiable |
| 5 | Instrument failure is not task failure, and collapsing them corrupts every comparison |
| 6 | The trajectory is the substrate, not a debugging side effect |
| 7 | Extensions must resolve at composition and then freeze; runtime discovery is an unaudited capability |
| 8 | A control that has never been observed failing is not known to work |

**Why this is weak evidence and worth recording anyway.** Two designs sharing an author's influences, a problem statement and a literature will converge for reasons other than correctness. Convergence is **not** validation. What it does support is a narrower claim: these eight conclusions are not idiosyncratic to one line of reasoning, which lowers the prior that any of them is an artifact of a single perspective.

---

## 3. Where they diverged

Divergence is the more informative half, because each divergence forced an explicit decision rather than an inherited assumption.

| Divergence | Resolution |
|---|---|
| Interface definition: validator-first versus schema-first | Schema-first (`ADR-0008`) |
| Permission model: verbs versus verbs plus resources | Resources are mandatory (`ADR-0011`) |
| Promotion: scalar objective versus partial order | Partial order over a frontier (`ADR-0015`) |
| Competence store: array versus graph | Graph (`ADR-0017`) |
| Trusted-base scope: policy kernel versus transitive dependencies | Both, declared separately (`ADR-0023`) |
| Storage: append-only files versus a transactional store | Transactional, with export (`ADR-0010`) |
| Memory gating: verdict-gated versus staged pipeline | Staged (`ADR-0030`) |

Each resolution and its reasoning is in `09`. None was decided by seniority or by which document was written first.

---

## 4. What this document does not establish

- **Not** that the converged conclusions are correct. Eight shared conclusions from two related lineages is corroboration, not proof.
- **Not** that the divergences were resolved correctly. Each resolution carries a reversal condition in `09` precisely because it might not have been.
- **Not** a substitute for the primary reviews. If they are recovered, they supersede this document, and this document's status changes to superseded rather than being deleted.

---

## 5. Provenance

Compiled 2026-08-14 by the Tech Lead, from the consolidation analysis produced during the v4 migration. That analysis is itself retired and is mapped at section granularity in `00 §7`.

**Attestation:** the convergent and divergent items above are recorded as the consolidation analysis stated them. No item has been added, strengthened, or reworded to support a conclusion. Items whose original wording could not be recovered with confidence were **omitted rather than paraphrased** — which means this list is incomplete, and incompleteness is preferable to invention in an evidence document.
