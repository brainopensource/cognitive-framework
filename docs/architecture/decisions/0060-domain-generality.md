---
id: adr-0060-domain-generality
adr: "0060"
class: decision
authority: binding-decision
canonical_for:
  - decision-0060-domain-generality
status: living
owner: engineering-director
version: "1.0"
last_verified: 2026-09-13
decision_status: accepted
---

# ADR-0060 — Domain generality of kernel and episode

This restores the accepted 2026-08-15 decision from Git `4dad29058d5f608a3ca95d0befedd9c68800830d:docs/05_adr/0060-the-domain-generality-invariant-the-microkernel-s0-s12.md`.
The S0–S12 microkernel and recursive episode loop are task-domain agnostic, and adding a domain is composition/manifest work rather than a change to kernel or generic episode execution.
Domain verbs, coding AST knowledge and domain-specific phase policies therefore stay outside those generic mechanisms; injected pack policy is compatible with the decision, while a domain-specific second engine is not.
Current references include [the episode engine](../../../vanguard/packages/agency/episode/engine.py), [composition-root conformance](../../../test/runtime/test_composition_root.py), and [kernel-neutrality checks](../../../tools/linters/check_kernel_neutrality.py), whose own primary historical reference also names ADR-0096.
The original reversal condition requires demonstrating that the needed capability algebra cannot be expressed by resource-scoped grants, followed by a successor decision; restoration alone changes no implementation or gate result.
