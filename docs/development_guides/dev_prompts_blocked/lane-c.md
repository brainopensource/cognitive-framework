# Developer Prompt — Lane DC: Senior Developer C (Sprint 6)

**Role:** Senior Systems Developer C (Telemetry & Benchmarks)  
**Branch:** `sprint5-6/integration`  
**Base:** Sprint 5 merged cleanly on `sprint5-6/integration`  
**Assigned Packet:** [`docs/sprint6/dc-packet.md`](../../sprint6/dc-packet.md)  
**Contract Row:** [`REQ-BENCH-001`](../../sprint0/active-mvp-contract.json)  
**Your Target Code:** `tools/telemetry/`, `test/benchmarks/`

---

## 1. Goal
Implement the **Runtime Telemetry Suite & Latency Benchmark Runner** tracking $p_{50}, p_{95}, p_{99}$ latency, sandbox overhead, token usage, and USD cost per task run.

---

## 2. Mandatory Reading Before Writing Code
Read these exact files in order:
1. [`docs/v4/07_vanguard_loop_engineering_and_measurement_v040.md`](../../v4/07_vanguard_loop_engineering_and_measurement_v040.md) — §5.6 Instrument tuple, §5.8 Measurable dimensions.
2. [`docs/sprint6/dc-packet.md`](../../sprint6/dc-packet.md) — Telemetry requirements and metric definitions.
3. [`docs/sprint0/active-mvp-contract.json`](../../sprint0/active-mvp-contract.json) — `REQ-BENCH-001`.

---

## 3. Strict Invariants (DO NOT DRIFT)
* **Zero Production Contamination:** Telemetry collectors must NOT add execution latency or alter kernel dispatch semantics.
* **Deterministic Cassettes:** Benchmark unit tests must execute against recorded golden cassettes in CI.

---

## 4. Verification Gate
```bash
python3 -m unittest discover -s test/benchmarks
python3 tools/check_boundaries.py
```
Push with commit message format: `[dev-dc] S6-DC-001: <reason naming REQ-BENCH-001>`.
