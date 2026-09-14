---
id: adr-0047-disposable-prototypes
adr: "0047"
class: decision
authority: binding-decision
canonical_for:
  - decision-0047-disposable-prototypes
status: living
owner: engineering-director
version: "1.0"
last_verified: 2026-09-13
decision_status: accepted
---

# ADR-0047 — Disposable prototype consumers

This is a bounded restoration of the original accepted ADR-0047, whose source is Git `4dad29058d5f608a3ca95d0befedd9c68800830d:docs/05_adr/0047-spike-and-slice-are-disposable-consumers-only-may.md`, originally accepted on 2026-08-14.
`spike/` and `slice/` were disposable consumers, never production import dependencies, and their deletion was required at the historical S4 gate.
Useful behavior graduates through a separately reviewed production adapter behind a port; the disposable implementation itself does not acquire production authority.
The original cited `TEST-ARCH-002` and `REQ-ARCH-002`, not a unified model-provider factory contract, so the latter attribution in [the current factory test](../../../test/contracts/test_evo09_model_factory.py) does not redefine this ADR.
Historical paths and gate timing are provenance, not an instruction to recreate or re-delete absent prototypes, and a successor architectural decision is required to reverse the consumer boundary.
