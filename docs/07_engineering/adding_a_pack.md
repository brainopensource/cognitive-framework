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
  - v0.6.2
implementation_status: PARTIAL
owner: lead-documentation-engineer
version: "0.6.2"
last_verified: 2026-08-23
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Guide: Adding a Domain Pack

> **Status:** `PARTIAL`; the canonical `/2` production ingress is an M-3C gate.

---

## 1. Domain Pack Principles

Coding is **Domain Pack #1** (`packs/code-default/`), not the architecture of the substrate. New domains (such as Pack #2 **Math & Formal Deductive Verification**, target: M-5) are added as standalone packs with:

1. `harness.yaml`: One authored `mhf.manifest/2` component graph and plugin dependencies.
2. `plugins/`: Tool descriptors and capability declarations.
3. Domain-owned implementation/configuration such as toolkits, planners, oracles, policies, and `system-prompt.txt` as required by the pack.

---

## 2. Invariant Invariance

- Adding an ordinary pack must require **zero modifications** to the domain-blind substrate.
- M-5's RF-86 is stricter: during the Pack #2 proof interval it permits no semantic diff under
  `vanguard/packages/{domain,ports,kernel,agency,runtime}`.
- A pack supplies namespaced binding adapters; it must not extend a global coding-centric binding
  table or bypass `FrozenComposition -> ActivationPlan -> RunPlan`.
- If Pack #2 exposes a missing primitive, M-5 fails and returns to governance; changing the substrate
  and calling the same run a generality proof is prohibited.
