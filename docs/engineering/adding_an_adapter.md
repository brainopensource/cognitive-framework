---
status: living
id: engineering-adding-adapter
class: how-to
authority: descriptive
canonical_for:
  - adding-an-adapter-guide
source_of_truth:
  - docs/SPEC.md#3-hexagonal-production-lattice
derived_from:
  - vanguard/packages/ports/
  - vanguard/packages/adapters/
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: lead-documentation-engineer
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Guide: Adding a Subsystem Adapter

> **Status:** `AS_BUILT`.

---

## Step-by-Step Procedure

1. **Identify the Port Interface**:
   - Inspect [`vanguard/packages/ports/`](../../vanguard/packages/ports/) for the appropriate abstract protocol (e.g. `ModelPort`, `EventStorePort`, `SandboxPort`).
2. **Implement in `adapters/`**:
   - Create your module under `vanguard/packages/adapters/` (e.g. `vanguard/packages/adapters/models/custom_provider.py`).
   - **Crucial Boundary Rule**: Adapters **must not** import from `kernel/` or `agency/`.
3. **Register in Wiring**:
   - Wire the adapter instance inside [`vanguard/packages/runtime/wiring.py`](../../vanguard/packages/runtime/wiring.py).
4. **Add Hermetic Unit & Contract Tests**:
   - Write contract compliance tests under `test/adapters/`.
5. **Verify Boundaries**:
   ```bash
   python3 tools/linters/check_boundaries.py
   ```
