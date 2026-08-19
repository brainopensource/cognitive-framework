---
adr: 0008
title: "JSON Schema 2020-12 is normative; a TypeScript validator is an implementation"
status: accepted
source_section: "3. Adjudications between the two lineages"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0008: JSON Schema 2020-12 is normative; a TypeScript validator is an implementation

**Reasoning.** A TypeScript-first validator expresses refinements and branded types with no schema representation, handing other languages a lossy derivative that drifts silently

**Reversal condition.** Only one language ever consumes the contracts — which would falsify the multi-language premise itself

**Owner · status.** Tech Lead · accepted
