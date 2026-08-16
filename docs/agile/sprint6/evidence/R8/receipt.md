# Gate R8 Evidence Receipt — Telemetry Labelling & Pricing Integrity

**Date:** 2026-08-15  
**Gate:** R8 (Telemetry Labelling & Pricing Integrity)  
**Status:** PASS  
**Authority:** `docs/phases_0-2_review_full_rev2.md` §14, `REQ-BENCH-001`  

---

## 1. Scope & Labelling Discipline
- **Target Components:** `tools.telemetry.collector`, `tools.telemetry.metrics`
- **Unit Suite:** `python3 -m unittest discover -s test/benchmarks` (15 tests passed)
- **Rules Enforced:**
  1. **Data Source Field:** `data_source` must be explicitly declared as `"live"`, `"cassette"`, or `"synthetic"` on every collector and report export.
  2. **Integer Timing & Costs:** Latency metrics exported with integer ms; token costs accounted in integer USD micros (`totalUsdMicros`).
  3. **Strict Live Report Protection:** Ingestion or recording of synthetic timing into a live telemetry collector immediately raises `ValueError` (fail closed).
  4. **Deferred Q3 Scope:** Paired trials, A/A permutations, and confidence intervals are deferred to Phase 3.

## 2. Adversarial Broken Controls
- `MF-TEL-001`: Ingestion of synthetic timing into a live report fails closed with `AssertionError("synthetic timing in a live report")`.

## 3. Verdict
Telemetry labelling and pricing integrity are strictly validated with no mixing of synthetic and live data.
