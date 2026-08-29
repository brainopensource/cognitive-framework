---
status: living
id: contract-trajectories
class: contract-reference
authority: descriptive
canonical_for:
  - trajectory-contract
source_of_truth:
  - docs/SPEC.md#7-telemetry-self-tuning--model-distillation
  - docs/02_decisions/0078-trajectory-un-hollowing-cost-accounting.md
derived_from:
  - schemas/mhf/trajectory.schema.json
  - vanguard/packages/runtime/trajectory.py
applies_to:
  - v0.6.2
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.9.0b1"
last_verified: 2026-08-26
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Trajectory Contract (`mhf.trajectory/1` and `/2`)

> **Schema:** [`schemas/mhf/trajectory.schema.json`](../../schemas/mhf/trajectory.schema.json)  
> **Status:** Schema and assembler are implemented; RF-23 is green on the canonical packages path.

`mhf.trajectory/1` is frozen. `mhf.trajectory/2` is implemented; readers dual-read `/1|/2` and
new production writers single-write `/2`.
Historical `/1` bytes and identity are never rewritten.

## Frozen M-4 `/2` extension contract

`/2` retains all `/1` obligations and adds these required top-level sections:

- `artifacts`: immutable artifact identity, digest, role, schema, measured size, retention, stored
  status, capture-policy identity/version, and correlation references;
- `provenance.context`, `.compaction`, and `.cache`: policy identity/version, parameters digest,
  input/output or key/source digests, artifact references when authorized, metrics, and turn index;
- `model_io`: finalized provider-input and raw structured provider-output artifact references bound
  to invocation, route, turn, and policy identity;
- `reproducibility_at_run_close`: six-dimensional assessment plus separate capability/verification
  for reconstruction and replay, observable basis, reducer/schema pins, and immutable executed
  receipts for every `verified` value;
- `capture`: `required`, `complete`, optional durable degradation reference, resolved policy identity,
  and non-evidentiary status.

Unknown or unavailable evidence is represented explicitly and never upgraded from configuration
alone. A run with incomplete capture cannot satisfy RF-95 or promotion evidence.

---

## Current schema surface

The Draft 2020-12 schema currently requires `schema`, `project_id`, `run_id`, `episode_id`,
`principal_id`, `harness_digest`, `turns`, `verdict`, and `cost`. It also defines optional
`execution_digest`, `model_routes_used`, manifest genome, attribution, and outcome fields. Read the
schema itself for exact field names and types; this page intentionally does not maintain a second
JSON shape.

## Guarantees & Non-Fabrication

1. **Ordered invocation target:** Each turn preserves every retry, fallback, critic call, and
   escalation as an ordered invocation with route, identity, measurement status, and cost.
2. **Conserved cost target:** Invocation totals reconcile to each turn, and turn totals plus explicit
   non-turn charges reconcile to the episode; fabricated `_ZERO_COST` is prohibited.
3. **Cold-continuity target:** A recovered episode joins the verified durable pre-crash prefix and
   post-recovery turns exactly once before `EpisodeCompleted` emits the row.
4. **Explicit absence target:** Missing measurements and fingerprints carry typed absence reasons
   rather than invented values.
5. **Derived promotability target:** Eligibility is derived from evidence and cannot be supplied by
   a pack; `evaluation: none` is declared before execution and is always ineligible.

These ADR-0078/RF-23 obligations are retained green on the current packages path; M-4 additionally
requires their source-bound occurrence inside the single real foundation run.

## Foundation evidence binding

For M-4, the trajectory is row 8 of `mhf.foundation-evidence/1` and cross-binds the bundle's
`project_id`, `run_id`, `episode_id`, `D_H`, `D_R`, optional `D_X`, ledger range, terminal chain
digest, receipts, outcome, and source digest. It cannot be substituted from another run or treated as
complete merely because its JSON validates. RF-83 proves source derivation; RF-95 proves the real product run. RF-85 remains the separate, optional hermetic assurance certification.
