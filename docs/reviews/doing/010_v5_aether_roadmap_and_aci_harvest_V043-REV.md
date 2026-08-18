# 010 — Active ACI Harvest Requirements (v0.5.0 Rewrite Baseline)

> **Status**: SIMPLIFIED ACTIVE ARCHITECTURAL DIRECTIVES
> **Last Audit**: 2026-08-17

---

## Active ACI Harvest Directives for v0.5.0

### [ACI-1] Paginated `fs.read` Tool & Adapter
- **Severity**: High
- **Subsystem**: `vanguard/packages/adapters/` & `schemas/v4/`
- **Spec Anchor**: `VG-03 §7.4`
- **v0.5.0 Requirement**: Implement 100-line default pagination with offset parameter on `fs.read` tool adapter and schema to prevent context dump-and-drown.

### [ACI-2] Succinct `fs.search` File-First Output
- **Severity**: Medium
- **Subsystem**: `vanguard/packages/adapters/`
- **Spec Anchor**: `VG-03 §7.4`
- **v0.5.0 Requirement**: Cap `fs.search` observation receipts to file matches first with snippet truncations.

### [ACI-3] Empty-Output Acknowledgment on `proc.exec`
- **Severity**: Low
- **Subsystem**: `vanguard/packages/adapters/`
- **Spec Anchor**: `VG-03 §7.4`
- **v0.5.0 Requirement**: Emit explicit `[Command executed with exit code 0 and empty stdout]` receipt text on `proc.exec` to prevent model looping on silent execution.

### [ACI-4] Lint-on-Patch Receipt Observation
- **Severity**: Medium
- **Subsystem**: `vanguard/packages/adapters/`
- **Spec Anchor**: `VG-03 §7.4` / `A-05`
- **v0.5.0 Requirement**: Run fast syntax linter on file patches and return syntax errors as observation receipts to the agent without triggering the evaluator.
