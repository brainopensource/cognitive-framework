# Developer Prompt — Lane SA: Lead Architect / Tech Lead

**Role:** Lead Software Architect, Tech Lead, Senior Developer A  
**Branch:** `sprint5-6/integration`  
**Base:** `main` (Sprint 0–4 merged at `v0.4.0-sprint4`)  
**Assigned Packet:** [`docs/sprint5/sa-packet.md`](../../sprint5/sa-packet.md)  
**Contract Row:** [`REQ-CTX-001`](../../sprint0/active-mvp-contract.json)  
**Your Target Code:** `vanguard/packages/agency/context/`

---

## 1. Goal
Implement the **L1–L5 Prefix-Stable Context Compiler** (`vanguard/packages/agency/context/compiler.py`) and pre-action competence prior logging $P(\text{success} \mid \text{task})$.

---

## 2. Mandatory Reading Before Writing Code
Read these exact files in order:
1. [`docs/v4/03_vanguard_architecture_planes_and_execution_model_v040.md`](../../v4/03_vanguard_architecture_planes_and_execution_model_v040.md) — §10 Context Assembly & Compaction.
2. [`docs/v4/01_vanguard_engineering_handbook_v040.md`](../../v4/01_vanguard_engineering_handbook_v040.md) — Mental Models M1, M2, M10, M11.
3. [`docs/sprint5/sa-packet.md`](../../sprint5/sa-packet.md) — Exact requirements, layer ordering, and token budget rules.
4. [`docs/sprint0/active-mvp-contract.json`](../../sprint0/active-mvp-contract.json) — `REQ-CTX-001`.
5. [`vanguard/packages/agency/episode/engine.py`](../../../vanguard/packages/agency/episode/engine.py) — The consuming episode loop.

---

## 3. Strict Invariants (DO NOT DRIFT)
* **Prefix Stability:** Layers $L1$ (System Core), $L2$ (Tool Schemas), and $L3$ (Repo Map) MUST be byte-for-byte identical across turns to preserve provider KV prompt caching. Dynamic content belongs in $L4$ (Task) and $L5$ (Dialogue).
* **Zero Cognitive Identifiers:** Do NOT use `plan`, `reflect`, `debug`, or `architect` as function or class names in `agency/context/`.
* **Single Dispatch Authority:** All persistence flows through the event ledger via `Kernel.dispatch`.
* **First Failing Test:** Write `test/agency/test_context_compiler.py` and prove failure before implementing the compiler.

---

## 4. Verification Gate
```bash
python3 -m unittest test.agency.test_context_compiler
python3 tools/check_boundaries.py
python3 tools/check_active_mvp_contract.py
```
Push only to `sprint5-6/integration` with commit message format: `[dev-sa] S5-SA-001: <reason naming REQ-CTX-001>`.
