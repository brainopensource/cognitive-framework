---
adr: 0060
title: "The Domain Generality Invariant: The microkernel (S0–S12) and recursive episode loop must remain 100"
status: accepted
source_section: "11. Sprint 3–4 closure and Phase 2 authorization"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0060: The Domain Generality Invariant: The microkernel (S0–S12) and recursive episode loop must remain 100% agnostic to task domains. Coding is merely a configuration manifest (`vg-code-default`). Adding non-coding domains (research, RAG, medical/legal triage, autonomous assistants) must require zero lines of code modified in `kernel/` or `agency/episode/`

**Context.** Hardcoding coding concepts into the engine guarantees multi-million-dollar rewrites when scaling to general cognitive tasks

**Alternative considered (and rejected).** Build domain-specific engines or hardcode git/AST into the kernel

**Evidence / bound test / links.** `vanguard/packages/agency/episode/engine.py`; `VG-01 M11`

**Reversal condition.** Formal proof that domain-specific capability algebra cannot be expressed through resource-scoped URI grants

**Owner · status.** Tech Lead + Project Lead · accepted · 2026-08-15 · accepted
