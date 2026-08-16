# Lane DC Developer Packet — OpenRouter Enhancements & Live Token Accounting

**Assignee:** Senior Developer C  
**Tickets:** `S5-DC-001`, `S5-DC-002`  
**Complexity:** Level 3 / 5 (Fast Lane)  
**Contract Row:** [`REQ-PORT-006`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json), [`REQ-SLICE-001`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json)  
**Owned Code:** `vanguard/packages/adapters/models/openrouter.py`  
**Target Test:** `test/adapters/test_openrouter.py`

---

## 1. Scope & Objective
Harden the `OpenRouterModelAdapter` with production-grade HTTP streaming resilience, token estimation fallback, exponential retry backoff on 429/503 status codes, and optional disposable live-key execution.

---

## 2. Invariants & Rules
1. **Never Import in Trust Spine:** `openrouter.py` must never be imported by `test/trust/test_spine.py`.
2. **Secret Cleanliness:** Secrets (`OPENROUTER_API_KEY`) are resolved from environment variables only; raw secret values must never be written to event payloads or log files.
3. **Priced Accounting:** Every response must emit token usage (`prompt_tokens`, `completion_tokens`, `cached_tokens`) and computed USD cost based on the model pricing table.

---

## 3. First Failing Test & Verification
```bash
python3 -m unittest test.adapters.test_openrouter
python3 tools/check_boundaries.py
```
Must prove: 429 rate limit triggers backoff; token estimation functions when provider omits usage; cassette replay remains 100% deterministic.
