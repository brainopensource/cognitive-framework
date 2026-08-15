# `schemas/v4/` — Artifact manifest

Status: `PLANNED` (no file yet) · `DRAFT` (present, unstable) · `LOCKED` (ADR required to change).

Authored alongside `04_vanguard_core_contracts_and_wire_schema_v040.md`.

**Each writer schema has a generated reader profile** (`*.reader.schema.json`, `SC-10`). Reader profiles are build artifacts, are not listed below, and are never edited by hand.

**`SC-7` for every `DRAFT` row.** `primitives`, `resource-selector` and canonicalisation now have two readers (`vanguard/packages/domain/`, TypeScript and Python) and a shared triple set (`vectors/canonicalisation/`, `REQ-SCHEMA-001`). The remaining `DRAFT` rows still have no second reader, so `TK-01` stays open for them. No row moves to `LOCKED` regardless: `SC-12` and the T0 human gates are unchanged by this work.

**`SC-12` — no schema locks while any type in `04` lacks an artifact.** The premature freeze of `04` happened while `effect-descriptor` was still `PLANNED`, and that absence is exactly what concealed the missing grant binding (`ADR-0039`). Cross-language agreement on the schemas that happen to exist is not coverage. Until they close, no row may move to `LOCKED`, and no production trajectory may be recorded against these schemas.

| Artifact | Owning section | Status | Notes |
|---|---|---|---|
| `primitives.schema.json` | `04 §1` | DRAFT | Branded identifiers, timestamps, digests, `IntString`, tenancy and principal ids |
| `blob-ref.schema.json` | `04 §2` | PLANNED | Content addressing; encryption-key reference by classification |
| `provenance.schema.json` | `04 §3` | PLANNED | Orthogonal axes: origin, instruction authority, integrity, confidentiality, epistemic, influence |
| `context-block.schema.json` | `04 §4` | PLANNED | The only type admissible into context assembly; raw strings are unrepresentable |
| `capability-grant.schema.json` | `04 §5` | DRAFT | Principal, actions, resource selectors, constraints, purpose digest, parent grant, approval reference |
| `resource-selector.schema.json` | `04 §5` | DRAFT | The type that makes "read only this repository" expressible |
| `effect-descriptor.schema.json` | `04 §5.5` | DRAFT | Normalisation rules `D-1`…`D-6` are normative in prose; the schema encodes the shape only |
| `invalidation-check-record.schema.json` | `04 §10.3` | DRAFT | Mutable check state, held outside the artifact (`CT-53`) |
| `budget.schema.json` | `04 §6` | PLANNED | Reservation, lease, ledger; includes the evaluation budget as a sibling dimension |
| `tool.schema.json` | `04 §7` | PLANNED | Tool spec, call, result; read/write sets and independence groups; no commutativity flag |
| `model-message.schema.json` | `04 §8` | PLANNED | Wire message shape, including tool-call correlation identifiers |
| `task-and-proposal.schema.json` | `04 §9` | PLANNED | Task spec, plan artifact, proposal, effect request — four distinct types, deliberately |
| `competence-artifact.schema.json` | `04 §10` | PLANNED | Immutable content-addressed node in the competence graph |
| `evidence-claim.schema.json` | `04 §10` | DRAFT | Scoped claim; **mandatory non-empty invalidation conditions** (`INV-1`) |
| `competence-edge.schema.json` | `04 §10` | PLANNED | Typed edges: derives-from, requires, supersedes, contradicts, evaluated-by, valid-under |
| `verdict.schema.json` | `06 §4` | PLANNED | Evaluator classes; inconclusive as a first-class outcome |
| `event-envelope.schema.json` | `04 §12` | DRAFT | Includes tenancy, ownership, confidentiality, retention class, trainability, redaction status |
| `event-union.schema.json` | `04 §12` | PLANNED | Minimum event set, including recovery, reconciliation and authorisation-denied events |
| `containment-report.schema.json` | `05 §6` semantics, `04 §13` shape | PLANNED | Replaces any boolean containment claim |
| `substrate-profile.schema.json` | `06 §5` | PLANNED | Union with the measurement instrument tuple |
| `instrument-tuple.schema.json` | `07 §5` | PLANNED | Experiment family, arms, splits, contamination ledger references |
| `config.schema.json` | `04 §14` | PLANNED | Configuration file schemas |
| `port-interfaces.md` | `04 §13` | DRAFT | Activation inventory and language boundary; interfaces land only with fake, real adapter and shared suite |
