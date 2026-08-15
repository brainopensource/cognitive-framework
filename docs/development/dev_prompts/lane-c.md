# Developer Prompt — Lane DC: Senior Developer C

**Role:** Senior Systems Developer C (Model Port & Telemetry)  
**Branch:** `sprint5-6/integration`  
**Base:** `main` (Sprint 0–4 merged at `v0.4.0-sprint4`)  
**Assigned Packet:** [`docs/sprint5/dc-packet.md`](../../sprint5/dc-packet.md)  
**Contract Rows:** [`REQ-PORT-006`](../../sprint0/active-mvp-contract.json), [`REQ-SLICE-001`](../../sprint0/active-mvp-contract.json)  
**Your Target Code:** `vanguard/packages/adapters/models/`

---

## 1. Goal
Harden the `OpenRouterModelAdapter` with **exponential retry backoff on 429/503**, fallback token estimation, cost calculation, and live disposable key execution receipt.

---

## 2. Mandatory Reading Before Writing Code
Read these exact files in order:
1. [`docs/sprint1/provider-notes.md`](../../sprint1/provider-notes.md) — OpenRouter wire formats and streaming quirks.
2. [`docs/sprint5/dc-packet.md`](../../sprint5/dc-packet.md) — Rate limit backoff and priced accounting requirements.
3. [`docs/sprint0/active-mvp-contract.json`](../../sprint0/active-mvp-contract.json) — `REQ-PORT-006`, `REQ-SLICE-001`.
4. [`vanguard/packages/ports/model.py`](../../../vanguard/packages/ports/model.py) — `ModelPort` contract.
5. [`vanguard/packages/adapters/models/openrouter.py`](../../../vanguard/packages/adapters/models/openrouter.py) — Existing adapter.

---

## 3. Strict Invariants (DO NOT DRIFT)
* **Never Import in Trust Spine:** `openrouter.py` must NEVER be imported on the `test/trust/test_spine.py` gate path.
* **Secret Cleanliness:** Never write raw `OPENROUTER_API_KEY` values into logs, events, or serialized artifacts.
* **Priced Accounting:** Emit accurate token counts (`prompt_tokens`, `completion_tokens`, `cached_tokens`) and USD costs.
* **First Failing Test:** Write unit tests for exponential backoff on 429 rate limits in `test/adapters/test_openrouter.py`.

---

## 4. Verification Gate
```bash
python3 -m unittest test.adapters.test_openrouter
python3 tools/check_boundaries.py
```
Push only to `sprint5-6/integration` with commit message format: `[dev-dc] S5-DC-001: <reason naming REQ-PORT-006>`.
