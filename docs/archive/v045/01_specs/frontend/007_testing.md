---
id: FE-07
file: 007_testing.md
title: "Vanguard v4.0 — Frontend Testing & Verification Matrix"
version: 4.0.0
status: LIVING
authority_scope: >
  Testing pyramid, golden vector compliance, replay fixtures, and E2E verification
  for all frontend packages.
supersedes: none
superseded_by: none
budget_words: 2000
owners: [Tech Lead]
last_reviewed: 2026-08-17
---

# Vanguard v4.0 — Frontend Testing & Verification Matrix

> **Who this is for.** Anyone writing tests or adding CI gates for frontend components.

---

## 1. Testing Pyramid

1. **Unit Tests**: Reducers, parsing logic, and cryptographic signers under `vanguard/clients/client-core/test/` and `vanguard/clients/cli/test/`.
2. **VG-04 Golden Vectors**: Client parser agrees with canonical schema vectors without modifying test vectors.
3. **Wire Contracts**: Conformance verification against `test/contracts/t1_wire_contracts.py`.
4. **Replay E2E**: Verified against JSONL fixtures under `vanguard/clients/cli/fixtures/`.
5. **Live E2E**: Real daemon UDS integration tests.

---

## 2. Soak & Conformance Harnesses

- Client test harnesses live in `vanguard/clients/cli/test/`.
- Frontend GUI tests render against immutable replay fixtures.
