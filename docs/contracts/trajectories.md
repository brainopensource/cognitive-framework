---
status: living
id: contract-trajectories
class: contract-reference
authority: descriptive
canonical_for:
  - trajectory-contract
source_of_truth:
  - docs/SPEC.md#6-trajectory-schema-and-evidence
  - docs/05_adr/0078-trajectory-un-hollowing-cost-accounting.md
derived_from:
  - schemas/mhf/trajectory.schema.json
  - vanguard/packages/runtime/trajectory.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Trajectory Contract (`mhf.trajectory/1`)

> **Schema:** [`schemas/mhf/trajectory.schema.json`](../../schemas/mhf/trajectory.schema.json)  
> **Status:** `AS_BUILT` · Governed by ADR-0078 (NOVA-1 / RF-23).

---

## Content & Cost Attribution

A completed episode emits a truthful, un-hollowed `mhf.trajectory/1` recording per-turn attribution and conserved totals:

```json
{
  "specversion": "mhf.trajectory/1",
  "trajectory_id": "traj-018f23a4-8b1c-7f89",
  "episode_id": "ep-001-turn-04",
  "project_id": "proj-aether-core",
  "identity": {
    "dh": "sha256:11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff",
    "dr": "sha256:aabbccddeeff11223344556677889900aabbccddeeff11223344556677889900",
    "dx": "sha256:ffeeddccbbaa99887766554433221100ffeeddccbbaa99887766554433221100"
  },
  "accounting": {
    "total_usd_micros": 4200,
    "total_tokens": 1250,
    "total_turns": 3,
    "measurement_status": "measured"
  },
  "turns": [
    {
      "turn_index": 0,
      "model_route": {
        "provider": "openrouter",
        "model": "anthropic/claude-3.5-sonnet",
        "fingerprint": "fp_8b1c7f89"
      },
      "cost": {
        "usd_micros": 1400,
        "input_tokens": 350,
        "output_tokens": 100,
        "status": "measured"
      },
      "intent": "Read project README",
      "action": "fs.read",
      "receipt_digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
  ]
}
```

## Guarantees & Non-Fabrication
1. **Conserved Cost**: Episode totals equal the exact sum of per-turn measurements. Zero fabrication (`_ZERO_COST` prohibited).
2. **Distinct Measurement Status**: States are strictly typed as `measured`, `estimated`, or `unavailable`.
3. **Derived Promotability**: Status is derived post-run from verdicts and cannot be forged by input.
