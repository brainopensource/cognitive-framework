---
id: FE-06
file: 006_runtime_client.md
title: "Vanguard v4.0 — Runtime Client Implementer Specifications"
version: 4.0.0
status: NORMATIVE
authority_scope: >
  Protocol interfaces, buffer management, error handling, and key storage
  for `@vanguard/client-core`.
supersedes: none
superseded_by: none
budget_words: 2500
owners: [Tech Lead]
last_reviewed: 2026-08-17
---

# Vanguard v4.0 — Runtime Client Implementer Specifications

> **Who this is for.** TypeScript engineers building adapters and client ports for daemon communication.

---

## 1. Port Interface Contracts

`RuntimeClient` methods return `Promise<Result<T>>` except `streamEvents`, which returns `AsyncIterable<Result<StreamItem>>`.

Failures use explicit `ClientFailure` error codes; do not throw unhandled exceptions for expected transport errors.

---

## 2. Event Ring Buffer

The live client adapter retains a ring buffer of at most **10,000** `StreamItem`s (`MAX_BUFFER_SIZE`), dropping the oldest when capacity is exceeded. Reducers must tolerate reconnects with historical sequences (`afterSeq`).

---

## 3. Cryptographic Key Persistence

The operator Ed25519 private key is persisted under `~/.vanguard/keys` with permissions **`0600`**. Keys must never be logged or transmitted in cleartext. Signing input is strictly RFC 8785 canonical JSON.
