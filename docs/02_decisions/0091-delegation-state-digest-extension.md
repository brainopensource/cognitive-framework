---
id: adr-0091-delegation-state-digest-extension
adr: 0091
class: decision
authority: binding-decision
canonical_for:
  - delegation-state-digest-extension
status: accepted
owner: engineering-director
version: "0.6.4"
last_verified: 2026-08-24
accepted_date: 2026-08-24
extends:
  - ADR-0090
supersedes: []
superseded_by: null
---

# ADR-0091 — Delegation state digest extension

## Context

ADR-0090 made `ChildSpawned` and `ChildReturned` material reducer transitions,
but `LedgerState.to_canonical_dict()` omitted `children`. A state containing an
open or returned child therefore had the same digest as the otherwise identical
state with no child. That collision invalidates cold-replay equality for a
delegating lineage.

Adding an always-present empty `children` object would also change the digest of
every historical, non-delegating state. Those histories contain no omitted
delegation fact and do not need an identity migration.

## Decision

`LedgerState.children` is part of canonical state identity whenever it is
non-empty. Child records are keyed by sorted child episode id and commit every
reducer-controlled field: child and parent episode ids, attenuated authority,
depth, lineage, settled intent key, status, outcome, terminal status, and cost.

For an empty child map, the `children` key remains absent. This compatibility
boundary preserves the exact canonical bytes and digest of all non-delegating
historical states while ensuring that adding, settling, or otherwise changing a
child changes the state digest. Map insertion order cannot affect the digest.

This is a state-identity extension, not a new hash algorithm or a new event
kind. SHA-256 over JCS remains unchanged. M-4 remains unadvanced; the rule is
required before a future delegating run can claim cold reconstruction parity.

## Consequences

- The known child-state collision is closed without rewriting existing
  non-delegating run digests.
- Delegating states produced by the defective omission had incomplete identity
  and must not be promoted as canonical evidence.
- M-6 remains locked: this decision does not activate `agent.spawn`, allocate
  RF-55–RF-59, provide `SpawnAdapter`, or satisfy the kill-tree drill.

