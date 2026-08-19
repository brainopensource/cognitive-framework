---
adr: 0063
title: "**The control plane is Python. `ADR-0001` (TypeScript on a Node-compatible runtime) is reversed on e"
status: accepted
source_section: "12. Phase 3 authorization, language ratification and gate status"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0063: **The control plane is Python. `ADR-0001` (TypeScript on a Node-compatible runtime) is reversed on evidence.** The TypeScript CLI remains the Interaction-plane client and the `ADR-0014` second-language contract reader. The wire contracts stay language-neutral per `ADR-0008`

**Context.** `ADR-0001` remained `accepted` while 15,569 LOC of Python control plane shipped, and `VG-02 §9` still states TypeScript normatively. Its own reversal condition — *"team composition shifts decisively to another language"* — had fired without being recorded. An unrecorded reversal in an append-only register is exactly what `ADR-0000` exists to prevent

**Alternative considered (and rejected).** Rewrite the control plane in TypeScript to honour `ADR-0001`; or leave the contradiction unrecorded

**Evidence / bound test / links.** `vanguard/packages/**` (Python); `vanguard/clients/cli/**` (TypeScript); `test/contracts/readers/` second reader; `docs/reviews/doing/006_…§1`

**Reversal condition.** An interactive-surface latency requirement that Python cannot meet **and** that the daemon boundary (`VG-03 §12`) cannot absorb

**Owner · status.** Tech Lead + Project Lead · accepted · 2026-08-16 · accepted
