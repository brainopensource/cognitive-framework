# Developer Prompt — Lane DD: Mid Developer D

**Role:** Mid Developer D (Client & Hexagonal CLI Interface)  
**Branch:** `sprint5-6/integration`  
**Base:** `main` (Sprint 0–4 merged at `v0.4.0-sprint4`)  
**Assigned Packet:** [`docs/sprint5/dd-packet.md`](../../sprint5/dd-packet.md)  
**Contract Row:** [`REQ-CLI-001`](../../sprint0/active-mvp-contract.json)  
**Your Target Code:** `vanguard/clients/cli/`

---

## 1. Goal
Realign the `@vanguard/cli` TypeScript client to consume live `RuntimeClient` async event streams and provide clean JSONL replay rendering for `vg run`, `vg trace`, and `vg why`.

---

## 2. Mandatory Reading Before Writing Code
Read these exact files in order:
1. [`docs/development/cli_tui_architecture.md`](../cli_tui_architecture.md) — Normative Hexagonal CLI & `RuntimeClient` specification.
2. [`docs/sprint5/dd-packet.md`](../../sprint5/dd-packet.md) — CLI packet deliverables and headless requirements.
3. [`docs/v4/04_vanguard_core_contracts_and_wire_schema_v040.md`](../../v4/04_vanguard_core_contracts_and_wire_schema_v040.md) — EventEnvelope wire schemas.
4. [`docs/sprint0/active-mvp-contract.json`](../../sprint0/active-mvp-contract.json) — `REQ-CLI-001`.
5. [`vanguard/clients/cli/src/`](../../../vanguard/clients/cli/src/) — Existing client codebase.

---

## 3. Strict Invariants (DO NOT DRIFT)
* **Hexagonal Boundary:** The CLI package is outside `vanguard/packages/`. It must NEVER import internal Python files or backend symbols directly.
* **Deterministic Replay:** `vg trace` and `vg why` must parse and render timelines directly from stored JSONL event lines without invoking any LLM.
* **Headless Mode:** In `vg run --headless`, stdout is strictly clean JSON lines; interactive terminal escape sequences are suppressed.
* **First Failing Test:** Write/update `@vanguard/cli` TypeScript unit tests in `vanguard/clients/cli/test/`.

---

## 4. Verification Gate
```bash
npm --workspace @vanguard/cli test
```
Push only to `sprint5-6/integration` with commit message format: `[dev-dd] S5-DD-001: <reason naming REQ-CLI-001>`.
