# Senior B — process engine

Tickets: `S3-SB-001` · Contract: `REQ-EXEC-002`

Own `vanguard/packages/runtime/governance/`. Load `ProcessDefinition`, advance `ProcessInstance` on ledger events, block on pending approvals, resume after restart from the ledger alone. No `ModelPort`. No episode replay.

Placed in Sprint 3 (not S4b) so S4b can be perimeter + deletion without going XL (`ADR-0055`).

Must not touch: `agency/` loop, adapters, `slice/`. Approval UX/CLI wiring is Sprint 6.
