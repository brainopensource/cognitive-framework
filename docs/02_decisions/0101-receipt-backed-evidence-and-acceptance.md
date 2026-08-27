---
id: adr-0101-receipt-backed-evidence-and-acceptance
adr: 0101
class: decision
authority: binding-decision
canonical_for:
  - evidence-envelope
  - evidence-state-machine
  - milestone-acceptance
status: accepted
owner: engineering-leadership
version: "1.0.0"
last_verified: 2026-08-26
accepted_date: 2026-08-26
extends:
  - ADR-0096
supersedes: []
superseded_by: null
---

# ADR-0101 — Receipt-Backed Evidence and Acceptance (“Graviton”)

## Context

Repository tests establish mechanism behavior, but several milestone claims were promoted without
the corresponding immutable bundle or independent review. Configuration, a green unit test, and an
executed release experiment are different facts and must not share one status.

## Decision

1. Immutable causal facts, content-addressed artifacts, derived projections, operational telemetry,
   and independent attestations are separate evidence classes. None substitutes for another.
2. Every milestone obligation progresses monotonically:

   `ABSENT -> PRODUCED -> VERIFIED -> INDEPENDENTLY_ACCEPTED`.

   Operational package state is separate:

   `NOT_STARTED -> IN_PROGRESS -> PACKAGE_READY -> EVIDENCE_READY -> ACCEPTED`, with `BLOCKED`
   available from any non-terminal state. `PACKAGE_READY` means isolated contract readiness;
   `EVIDENCE_READY` means the required immutable bundle verifies; only `ACCEPTED` closes the gate.
3. An evidence envelope uses canonical JSON and binds: claim and protocol identity; subjects;
   materials; run/project/episode and `D_H/D_R/D_X`; schema/reducer pins; code commit and tree;
   dependency/environment identity; outcome including negative or undeterminable results; artifact
   references; producer identity; and signature. Independent acceptance is a separate signed
   envelope whose reviewer differs from the producer.
4. Unknown, absent, waived, degraded, blocked, or undeterminable evidence is never zero or pass.
   A negative scientific result may close an experiment when its preregistered protocol remains
   valid; invalid instrumentation cannot.
5. The canonical boards may cite only resolvable evidence references. A release claim requires
   subject/material digest verification, signature verification, cold reconstruction where
   promised, and independent acceptance. A CI UI or prose statement is not the receipt.

## Minimal envelope

The first implementation uses `aether.evidence/1` with `subject[]`, `materials[]`, `run`, `pins`,
`environment`, `protocol`, `outcome`, `artifactRefs[]`, `producer`, and `signature`. The signature
covers the canonical bytes excluding only the signature value. Producer and reviewer keys are
distinct. This is an evidence protocol over the existing ledger and artifact substrate, not a
second ledger.

## Consequences

Milestones may regress only in planning state when a prior claim is discovered unsupported; their
evidence history remains append-only. M-4 through M-8 cannot be accepted by source presence or test
counts alone. Experiments may end honestly with negative results without pressure to ship ineffective
mechanisms.
