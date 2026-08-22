---
status: living
id: contract-trajectories
class: contract-reference
authority: descriptive
canonical_for:
  - trajectory-contract
source_of_truth:
  - docs/SPEC.md#7-telemetry-self-tuning--model-distillation
  - docs/05_adr/0078-trajectory-un-hollowing-cost-accounting.md
derived_from:
  - schemas/mhf/trajectory.schema.json
  - vanguard/packages/runtime/trajectory.py
applies_to:
  - v0.6.1
implementation_status: RATIFIED_NOT_IMPLEMENTED
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Trajectory Contract (`mhf.trajectory/1`)

> **Schema:** [`schemas/mhf/trajectory.schema.json`](../../schemas/mhf/trajectory.schema.json)  
> **Status:** Schema and assembler exist, but the ADR-0078 content contract is
> `RATIFIED_NOT_IMPLEMENTED` while RF-23 is red.

---

## Current schema surface

The Draft 2020-12 schema currently requires `schema`, `project_id`, `run_id`, `episode_id`,
`principal_id`, `harness_digest`, `turns`, `verdict`, and `cost`. It also defines optional
`execution_digest`, `model_routes_used`, manifest genome, attribution, and outcome fields. Read the
schema itself for exact field names and types; this page intentionally does not maintain a second
JSON shape.

## Guarantees & Non-Fabrication
1. **Conserved Cost target**: Episode totals equal per-turn measurements; fabricated `_ZERO_COST` is prohibited.
2. **Explicit absence target**: Missing measurements and fingerprints carry typed absence reasons rather than invented values.
3. **Derived promotability target**: Eligibility is derived from evidence and cannot be supplied by a pack.

These are ADR-0078/RF-23 obligations, not claims about the current green state.
