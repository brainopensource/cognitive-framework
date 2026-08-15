# domain

Pure types and reducers. No project imports and no I/O.

Sprint 1 (Dev 1) added the common substrate every other schema task consumes,
as two independent readers per `SC-7` — TypeScript (`*.ts`) and Python
(`*.py`). Neither is the interface definition: `schemas/v4/` is normative and
these are implementations verified against it (`CT-01`).

| Directory | Contract | Requirement |
|---|---|---|
| `canonicalisation/` | RFC 8785 / JCS canonical bytes and `sha256:` digests over them (VG-04 §0.3, `CT-09`) | `REQ-SCHEMA-001` |
| `primitives/` | Opaque, boundary-parsed identifiers and scalars (VG-04 §1, `CT-03`) | `REQ-SCHEMA-002` |
| `selectors/` | The `ResourceSelector` inclusion relation (VG-04 §5.2, §5.3.1, `CT-52`) | `REQ-SCHEMA-003` |

`SEMANTICS.md` records the rules JSON Schema cannot express and the ADR
candidates raised by this work. Golden vectors live in `schemas/v4/vectors/`;
the suites that replay them through both readers live in `test/contracts/`.

Purity note: `canonicalisation/digest.ts` imports `node:crypto` for SHA-256.
It is a pure function of the bytes handed to it — no clock, no randomness, no
environment, no I/O — and it is the only host module this package reaches for.
