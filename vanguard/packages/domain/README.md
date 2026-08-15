# domain

Pure types, primitives, selectors, and state reducers. No project imports and no I/O (ICD §2, `domain`).

## Core Submodules & Contracts

| Module / Directory | Contract Specification | Active Requirement |
|---|---|---|
| `canonicalisation/` | RFC 8785 / JCS canonical bytes and `sha256:` digests (VG-04 §0.3, `CT-09`) | `REQ-SCHEMA-001` |
| `primitives/` | Opaque, boundary-parsed identifiers and scalars (VG-04 §1, `CT-03`) | `REQ-SCHEMA-002` |
| `selectors/` | `ResourceSelector` inclusion relation algebra (VG-04 §5.2, §5.3.1, `CT-52`) | `REQ-SCHEMA-003` |
| `contracts.ts` | Wire-domain types: `EffectDescriptor`, `CapabilityGrant`, `Receipt`, `EventEnvelope`, `Artifact`, `EvidenceClaim` | `REQ-SCHEMA-004..009` |
| `schemas/` | Candidate JSON Schema reader/writer profiles (`artifact.schema.json`, `receipt.schema.json`) | `REQ-SCHEMA-005..006` |

---

## Testing & Verification

1. **Python Contract Test Suite**:
   ```bash
   python3 -m unittest test.contracts.test_t1
   ```
   Runs 60 unit, property, and golden vector tests (~2s) verifying reflexivity, transitivity, and fail-closed totality.

2. **Schema Conformance Tests**:
   ```bash
   python3 vanguard/packages/domain/test/schema_conformance.py
   ```

`SEMANTICS.md` records rules that JSON Schema cannot express and the ADR candidates raised during implementation. Golden vectors reside under `schemas/v4/vectors/`.
