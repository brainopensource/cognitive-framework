---
adr: 0062
title: "Implement Unix Domain Socket RuntimeService daemon and Asymmetric Ed25519 Operator Approval Authorit"
status: accepted
source_section: "11. Sprint 3–4 closure and Phase 2 authorization"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0062: Implement Unix Domain Socket RuntimeService daemon and Asymmetric Ed25519 Operator Approval Authority for Sprint 6B Close (Beta v0.4.1). RuntimeService exposes NDJSON wire RPC (StartRun, GetRun, StreamEvents, ResolveApproval, Cancel, Resume) with SQLite WAL transaction inbox/outbox. Approvals use Ed25519 signing outside the runtime process with descriptor-bound RFC 8785 canonical bytes; the runtime retains only public key verification authority

**Context.** Symmetric HMAC approval permitted the runtime to forge authority (`GOV-01`), and lack of a Unix daemon forced the CLI into in-process fixture feeds (`CLI-LIVE`)

**Alternative considered (and rejected).** Retain symmetric HMAC with in-process key, or implement HTTP REST control plane

**Evidence / bound test / links.** `vanguard/packages/runtime/service/`, `vanguard/packages/runtime/governance/approvals.py`, `vanguard/clients/cli/src/adapters/live.ts`; `REQ-APP-001`, `REQ-CLI-002`

**Reversal condition.** A mathematically sound hardware token protocol supersedes Ed25519 while maintaining identical external authority invariants

**Owner · status.** Tech Lead + Project Lead · accepted · 2026-08-16 · accepted
