# Gate R1 Evidence Receipt — TCB Budget Enforcement

**Date:** 2026-08-15  
**Gate:** R1 (TCB Budget Enforcement)  
**Status:** PASS  
**Authority:** `docs/phases_0-2_review_full_rev2.md` §14  

---

## 1. Metric Breakdown
- **Threshold:** 1438 logical lines of code
- **Measured Current Logical LOC:** 1307
- **Alarm Margin (Delta):** +131 lines below alarm ceiling

```json
{
  "alarm_delta_lines": 131,
  "baseline_logical_loc": 1307,
  "current_logical_loc": 1307,
  "files": {
    "vanguard/packages/kernel/__init__.py": 41,
    "vanguard/packages/kernel/attenuation.py": 153,
    "vanguard/packages/kernel/budget.py": 133,
    "vanguard/packages/kernel/classifier.py": 96,
    "vanguard/packages/kernel/dispatch.py": 349,
    "vanguard/packages/kernel/grants.py": 191,
    "vanguard/packages/kernel/model.py": 137,
    "vanguard/packages/kernel/policy.py": 97,
    "vanguard/packages/kernel/provenance.py": 110
  },
  "threshold": 1438
}
```

## 2. Verdict
`tools/check_tcb_budget.py` exits 0. The kernel size remains strictly bounded within the authorized architectural budget.
