---
adr: 0084
title: "Compounding macro-tool registry and Active Inference"
status: accepted
accepted_date: 2026-08-21
source_section: "ALFA Tier S+ Director Ratification"
implementation_milestone: "T0 M-5; macro lab M-9; statistical promotion M-10"
implementation_status: deferred
---

# ADR-0084: Compounding macro-tool registry and Active Inference

**Context.** A trustworthy corpus can reduce future cost only if reuse preserves subject identity,
authority, and exterior evidence. Macro compilation, skill retrieval, Active Inference, and DPO are
powerful consumers of that corpus but are unsafe if they self-score, inherit broad capabilities,
or promote from unpaired/hollow runs. Token collapse is a measured outcome, not an architectural
assumption.

**Decision.**

1. Compounding proceeds in order:
   - **T0 / M-5:** deterministic witness memoization;
   - **T1 / M-9:** verified trajectory-to-macro candidate compilation;
   - **T2 / M-9:** evidence-ranked skill/retrieval and routing adaptation;
   - **T3 / M-10:** preference/model/harness candidates and promotion.
2. T0 keys bind the goal/obligation, input digests, `D_H/D_R`-relevant environment, checker,
   toolchain, assurance, and policy version. A cache hit is ledgered with its source evidence. It
   never copies a verdict to a different subject digest or widens authority.
3. A macro candidate is an ordinary versioned plugin: typed interface, deterministic
   implementation where possible, wire contract, lifecycle, S0–S12 dispatch, exterior checker,
   and fallback. It never becomes a kernel shortcut.
4. Macro mining uses causally connected provenance subgraphs, not temporal n-grams alone. Its
   capability ceiling is the narrow selector hull of capabilities actually exercised by accepted
   source traces, intersected with pack and publisher ceilings. If the selector algebra cannot
   express a narrow safe ceiling, compilation is rejected.
5. Candidate acceptance includes adversarial replay and paired held-out comparison against the
   original procedure. Total cost includes discovery, dispatch, sandbox, verification, cache,
   compilation amortization, and fallback. Claims such as `50k -> 500` tokens remain hypotheses
   until measured.
6. VFE and EFE are distinct:
   - variational free energy fits beliefs after attributed observations;
   - expected free energy ranks **already feasible** policies by pragmatic and epistemic value.
   Neither mints authority, truth, or promotion.
7. Predicted distributions are recorded before execution and settled observations afterward.
   Calibration error affects future routing probability only.
8. Skill/Elo state ranks retrieval, never grants or promotion. Indices are rebuildable; eviction
   archives evidence rather than erasing it; embedding model/version enters index identity.
9. DPO/preference pairs require comparable experiment cells, two valid exterior-signed outcomes,
   immutable trajectories, no train/eval overlap, and no derived ineligibility. Candidate versus
   baseline evaluation uses exact paired McNemar, effect size/interval, an A/A floor, and the Pareto
   safety gate.
10. Automated systems may nominate candidates. Only the human-controlled, versioned promotion
    pointer can change the production default, and rollback must be tested.
11. No T1–T3 implementation begins before M-4; T0 begins only after Pack #2 establishes generality.

**Bound falsifiers.** RF-52: memo hits are attributable and invalidated by any key change. RF-53:
unsigned/ineligible evidence cannot enter memo. RF-67: over-broad macro ceiling fails at compose.
RF-68: macro dispatches through S0–S12. RF-69: exact McNemar matches enumerated binomial cases and
the A/A control is stable. RF-70: any assurance regression prevents promotion regardless of cost.

**Alternatives rejected.** Self-reported reward; chronology as causality; automatic hot-swap;
macro execution outside the plugin/effect path; weighted promotion that trades safety for quality;
or deleting low-ranked evidence.

**Reversal condition.** Real workloads show negligible T0 reuse or macro candidates reliably harm
held-out solve rate after fallback-inclusive accounting. The affected tier is demoted without
weakening the remaining evidence and authority invariants.

**Owner · status.** PhD AI Specialist / Lab and Release Owners · design accepted by Engineering
Director · phased M-5/M-9/M-10 · 2026-08-21
