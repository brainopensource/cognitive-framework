---
status: living
id: engineering-security-tcb
class: how-to
authority: descriptive
canonical_for:
  - security-and-tcb-compliance-guide
source_of_truth:
  - docs/01_law/DISPATCH.md
  - AGENTS.md
derived_from:
  - tools/linters/check_tcb_budget.py
  - tools/linters/check_domain_blindness.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: lead-documentation-engineer
version: "0.6.1"
last_verified: 2026-08-21
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Security & TCB Compliance Guide

> **Status:** `AS_BUILT`.

---

## 1. TCB Budget Limit ($\le 1438$ LOC)

The Trusted Computing Base (`vanguard/packages/kernel/`) must strictly remain at or below **1438 logical lines of code**:

```bash
# Verify kernel budget
python3 tools/linters/check_tcb_budget.py
```

---

## 2. Invariant Linters

```bash
# Boundary lattice verification (no illegal cross-layer imports)
python3 tools/linters/check_boundaries.py

# Domain blindness check (Invariant I-7: no coding/pytest/ast in kernel)
python3 tools/linters/check_domain_blindness.py

# Sandbox isolation policy (Invariant I-6)
python3 tools/linters/check_isolation_policy.py

# Secret and credential leak scan
python3 tools/linters/scan_secrets.py
```
