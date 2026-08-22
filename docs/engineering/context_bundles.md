---
status: living
id: engineering-context-bundles
class: reference
authority: descriptive
canonical_for:
  - context-bundles-index
source_of_truth:
  - docs/README.md
derived_from:
  - docs/
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: lead-documentation-engineer
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Subsystem Context Bundles & Measured Token Budgets

> **Status:** `AS_BUILT` · Optimized Sub-1k Context Slices for AI Coding Agents.

---

## Targeted Context Slices by Task Class

Rather than ingesting multi-thousand-line monolithic specifications, an AI agent or human contributor loads only the targeted context bundle for their specific task:

| Work Class | Ingested Context Bundle | Approx. Token Size | Direct File Links |
|---|---|---:|---|
| **Kernel / TCB** | `KERNEL.md` + `ports/kernel.py` + `test_dispatch.py` | ~850 tokens | [`KERNEL.md`](../04_annex/KERNEL.md) · [`kernel.md`](../protocols/kernel.md) |
| **Model Adapter** | `protocols/model.md` + `adding_an_adapter.md` | ~550 tokens | [`model.md`](../protocols/model.md) · [`adding_an_adapter.md`](adding_an_adapter.md) |
| **State / Ledger** | `contracts/events.md` + `protocols/stores.md` | ~700 tokens | [`events.md`](../contracts/events.md) · [`stores.md`](../protocols/stores.md) |
| **Trajectory (NOVA-1)** | `contracts/trajectories.md` + `ADR-0078` | ~650 tokens | [`trajectories.md`](../contracts/trajectories.md) · [`0078`](../05_adr/0078-trajectory-un-hollowing-cost-accounting.md) |
| **Continuation (NOVA-2)** | `sequences.md` (§3) + `ADR-0082` | ~600 tokens | [`sequences.md`](../architecture/sequences.md) · [`0082`](../05_adr/0082-universal-turn-loop-m10-compatibility-contract.md) |
| **Domain Pack** | `adding_a_pack.md` + `manifests.md` | ~500 tokens | [`adding_a_pack.md`](adding_a_pack.md) · [`manifests.md`](../contracts/manifests.md) |
| **Evaluator** | `protocols/evaluator.md` + `verdicts.md` | ~600 tokens | [`evaluator.md`](../protocols/evaluator.md) · [`verdicts.md`](../contracts/verdicts.md) |

---

## Token Efficiency Measurement
- **Monolithic Ingestion (`SYSTEM_OVERVIEW.md` + `SPEC.md` + `ADR INDEX`)**: $\approx 28,500$ tokens.
- **Targeted Context Bundle**: $\approx 500 - 850$ tokens.
- **Net Context Reduction**: **$97.5\%$ token savings** with zero loss of normative requirements or code context.
