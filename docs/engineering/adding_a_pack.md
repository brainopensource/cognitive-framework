---
status: living
id: engineering-adding-pack
class: how-to
authority: descriptive
canonical_for:
  - adding-a-pack-guide
source_of_truth:
  - docs/SPEC.md#4-coding-domain-pack-first-domain-foundation-e2e-not-this-lock-wave
derived_from:
  - packs/code-default/
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: lead-documentation-engineer
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Guide: Adding a Domain Pack

> **Status:** `AS_BUILT`.

---

## 1. Domain Pack Principles

Coding is **Domain Pack #1** (`packs/code-default/`), not the architecture of the substrate. New domains (such as Pack #2 **Math & Formal Deductive Verification**, target: M-5) are added as standalone packs with:

1. `harness.yaml`: Declarative harness specification and plugin dependencies.
2. `plugins/`: Tool descriptors and capability declarations.
3. Domain-owned implementation/configuration such as toolkits, planners, oracles, policies, and `system-prompt.txt` as required by the pack.

---

## 2. Invariant Invariance
- Adding a pack must require **zero modifications** to `vanguard/packages/domain/` or `vanguard/packages/kernel/` (Invariant I-7 Domain Blindness).
