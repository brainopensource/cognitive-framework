---
id: adr-0104-automated-verifier-identity-separation
adr: 0104
class: decision
authority: binding-decision
canonical_for:
  - automated-evidence-verification
  - two-lane-delivery
  - execution-predicate-separation
status: accepted
owner: repository-governance
version: "1.0.0"
last_verified: 2026-08-27
accepted_date: 2026-08-27
extends:
  - ADR-0097
  - ADR-0101
  - ADR-0102
supersedes:
  - ADR-0097 active development ownership and process-gate clauses
  - ADR-0102 Leadership planning dependency
superseded_by: null
---

# ADR-0104 — Automated verifier identity separation

## Status

Accepted 2026-08-27. This decision governs the active AETHER v0.9 delivery
process and does not rewrite historical ADR bodies, tags, evidence, or ledger facts.

## Context

The former execution material mixed technical evidence requirements with process
roles and approval gates that could not produce a machine-checkable terminal
state. It also used ownership labels that no longer describe the two-lane
delivery model. Evidence still requires separation between the producer and the
verifier, but that separation is a security and reproducibility property, not a
dependency on a human countersignature or a management workflow.

## Decision

1. Lane A is the exclusive implementation owner for runtime, execution,
   persistence, clients, packaging, deployment, operations, and release. Lane B
   is the exclusive producer for domain/ports contracts, schemas, projections,
   evaluation semantics, falsifiers, experiments, and promotion criteria.
2. Each lane has WIP=1 and exactly one current package. Stable package states
   remain `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `PACKAGE_READY`,
   `EVIDENCE_READY`, and `ACCEPTED`. A package advances only when its explicit
   predicate is true.
3. A software verifier MUST use an identity, signing key, and writable state
   distinct from the producer and builder. It MUST resolve the exact subject,
   material digests, pins, commands, and outcome before emitting a signed
   receipt. It MUST return failure or `undeterminable` when required material or
   verification is unavailable; it MUST NOT accept a waiver or mutate producer
   evidence.
4. Active execution MUST NOT depend on a human review, a management role, a
   named third lane, or a manual milestone decision. The canonical board and
   verifier receipts are the machine-evaluable control plane.
5. Product-time operator approval remains a runtime security capability. It is
   checked at use time for privileged effects and is independent of development
   package progression.
6. The release trigger remains exact: `./ci/release_qualify.sh` exits `0` and
   emits a signed envelope whose subject exactly matches the candidate. No prose,
   percentage, or pre-existing report can replace that result.

## Required predicates

The active board validator MUST prove all of the following:

- exactly one current package exists for each of Lane A and Lane B;
- the current package is present in the package ledger and is not `NOT_STARTED`
  or `BLOCKED`;
- every backlog package appears once in the package ledger with the same state;
- all milestone rows expose a named predicate; and
- no active package entry or completion predicate names a retired process role or
  process approval dependency.

The evidence verifier MUST additionally prove producer/verifier identity
inequality and exact-subject equality before a receipt can satisfy a milestone
predicate.

## Consequences

The historical ownership and approval vocabulary remains auditable in frozen
provenance, while active execution is compact, two-lane, and mechanically
testable. Independent software verification continues to protect evidence
integrity. A constitutional change to identity separation or product-time
operator authorization requires a successor ADR, migration rule, and falsifier.

## Falsifiers

- `check_execution_truth.py` fails if either lane is missing, duplicated, or
  assigned a blocked current package.
- `check_execution_truth.py` fails if package state drifts between backlog and
  board or if a required milestone predicate is absent.
- The evidence verifier fails a receipt when producer and verifier identities
  or keys are equal.
- The release qualifier fails when the signed envelope subject differs from the
  exact candidate subject.

