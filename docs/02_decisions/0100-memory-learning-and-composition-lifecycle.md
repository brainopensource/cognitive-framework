---
id: adr-0100-memory-learning-and-composition-lifecycle
adr: 0100
class: decision
authority: binding-decision
canonical_for:
  - m8-memory-authorization
  - m8-memory-lifecycle
  - m8-composition-promotion
status: accepted
owner: engineering-leadership
version: "1.0.0"
last_verified: 2026-08-26
accepted_date: 2026-08-26
extends:
  - ADR-0096
  - ADR-0097
supersedes: []
superseded_by: null
---

# ADR-0100 — Memory, Learning, and Composition Lifecycle

## Context

M-8 preparation contains useful in-memory contracts and evaluation mechanisms, but it does not yet
provide production memory authority, durable promotion, or measured lift. A non-empty `grant_ref` is
not verified authority, an in-memory dictionary is not durable memory, and moving an in-memory
composition pointer is not an operational rollback.

## Decision

1. The five conceptual categories remain distinct: session state, knowledge, experience, skills,
   and project memory. Session state remains the event ledger plus `AgentView`; four external ports
   represent the other categories. One durable adapter may implement several ports, but category,
   tenant, project, and authorization isolation remain mandatory.
2. Every public memory operation consumes an immutable authorized context derived from a verified
   grant or lease. It binds issuer, subject, actions, canonical `memory://` selector, tenant,
   project, purpose, policy, validity interval, revocation epoch, and verification receipt.
   Construction-time string checks are insufficient. Adapters revalidate action, selector, expiry,
   and revocation at use time and fail closed without leaking record existence.
3. Content remains in the content-addressed blob store. Durable metadata and deterministic lexical
   indexing use a file-backed SQLite-WAL adapter for the single-host MVP. Network-filesystem WAL is
   refused. Writes are blob-first, metadata-transaction-second, causal-fact-third.
4. Records are append, supersede, or invalidate; semantic content is never updated in place.
   Retrieval filters authorization before ranking and emits a durable provenance receipt binding
   query, policy/index/tokenizer versions, candidates, selected/dropped records, source digests,
   redactions, and context selection.
5. Retention and garbage collection are policy operations. Legal hold dominates deletion. GC is a
   reviewed mark-and-sweep over event/evidence/composition/hold roots with a quarantine interval and
   a durable deletion receipt. Knowing a digest never grants read authority.
6. Candidate, evaluation, promotion, and rollback lifecycle evidence uses typed `ClaimRecorded`
   payloads through M-8. The deprecated lifecycle event names remain deprecated.
7. The promotion unit is a complete immutable composition manifest. Generator, evaluator, and
   promoter are distinct identities and key authorities. Held-out material is sealed from the
   generator. Presence, retrieval, invocation, grounding, verification, and outcome remain separate
   attribution axes.
8. The product registry is durable and compare-and-swap based. Promotion and rollback validate the
   expected head generation, signed evidence, candidate/base digests, and previous known-good head.
   Last-writer-wins and in-memory-only product promotion are prohibited.

## Required falsifiers and acceptance

M-8 must reject forged, expired, revoked, cross-tenant, cross-project, and cross-category access;
unauthorized pre-ranking; retrieval without provenance; held-out contamination; role/key collapse;
two concurrent promoters both winning; restart loss; and rollback that changes only a pointer.

M-8 reaches acceptance only after durable authorization and recovery tests, measured held-out lift
under the measurement law, an executed injected-regression rollback restoring prior behavior, and
RF-98/TCB neutrality. The existing `runtime/memory.py` and in-memory composition registry remain
contract fakes until replaced on the product path.

## Consequences

Multi-tenant isolation, retention, GC, and legal hold are M-8 obligations because persistence creates
the disclosure surface; they are not deferred to M-9. Vector/graph retrieval, distributed storage,
model training, and continuous-learning infrastructure remain outside M-8.
