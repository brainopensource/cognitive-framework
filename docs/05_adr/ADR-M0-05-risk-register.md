---
adr: M0-05
title: "Risk register (pruned)"
status: accepted
---

# ADR-M0-05: Risk register (pruned)

**Decision.** Carry forward only the risks that survive the MHF rewrite: plugin-supply-chain
risk (unsigned/malicious third-party plugin manifests — mitigated by isolation tiers + capability
ceilings, SPEC §2.1), oracle overfitting (a preregistered oracle gamed by a planner that learns the
oracle's shape rather than the task — mitigated by the exterior signed evaluator and McNemar paired
testing), and statistical power (Phase-2 promotion requires the 200-task suite prerequisite before
M5, per the audit's synthesis on `docs/04_annex/MEASUREMENT.md`).

**Context.** `docs/01_specs/backend/02_vanguard_charter_claims_and_non_claims_v040.md` §10 held a
larger risk register; most rows named risks specific to the pre-rewrite architecture (five-process
split, TypeScript control plane) that no longer apply.

**Reversal condition.** Per risk — reopens only on the evidence its own row would name if reached.
