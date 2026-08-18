# 004 — Active Cognition & Evidence Requirements (v0.5.0 Rewrite Baseline)

> **Status**: SIMPLIFIED ACTIVE ARCHITECTURAL DIRECTIVES
> **Last Audit**: 2026-08-17

---

## Active Architectural Requirements for v0.5.0

### [GE-01] Implement Minimum Viable Evidence Graph ($G_E$) Dataclasses
- **Severity**: High
- **Subsystem**: `vanguard/packages/domain/evidence/`
- **Spec Anchor**: `VG-02 §1` / `T4.11`
- **Current Defect**: `Claim` exists only as a JSON schema (`schemas/v4/evidence-claim.schema.json`). Pure domain Python types, evaluation protocol references, and invalidation condition data structures do not exist in `domain/`.
- **v0.5.0 Requirement**: Create `domain/evidence/claim.py` declaring immutable `Claim` dataclasses with `subject`, `predicate`, `protocol`, `evaluator`, `uncertainty`, and `invalidation_conditions`.

### [AA-01] Establish A/A Benchmark Floor Runner
- **Severity**: High
- **Subsystem**: `vanguard/packages/runtime/` & `lab/`
- **Spec Anchor**: `VG-02 §8` / `O-01`
- **Current Defect**: The A/A benchmark floor does not exist, blocking the trigger for `O-01` (derived competence lifecycle).
- **v0.5.0 Requirement**: Build a refusing A/A benchmark floor runner that verifies null-lift baseline variance before registering competence claims.
