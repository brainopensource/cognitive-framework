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
last_verified: 2026-08-23
supersedes: []
superseded_by: null
---

# Subsystem Context Bundles & Context-Budget Estimates

> **Status:** `AS_BUILT` navigation aid. Token figures below are planning estimates, not benchmark results.

---

## Targeted Context Slices by Task Class

Rather than ingesting multi-thousand-line monolithic specifications, an AI agent or human contributor loads only the targeted context bundle for their specific task:

| Work Class | Minimum starting bundle | Size status | Direct File Links |
|---|---|---:|---|
| **Kernel / TCB** | Active task + dispatch clause + kernel protocol + named test | Measure per task | [`DISPATCH.md`](../01_law/DISPATCH.md) · [`kernel.md`](../06_protocols/kernel.md) |
| **Model Adapter** | Active task + model protocol + adapter guide + contract test | Measure per task | [`model.md`](../06_protocols/model.md) · [`adding_an_adapter.md`](adding_an_adapter.md) |
| **State / Ledger** | Active task + event contract + store protocol + ledger test | Measure per task | [`events.md`](../05_contracts/events.md) · [`stores.md`](../06_protocols/stores.md) |
| **Trajectory (NOVA-1)** | Active RF-23 board row + ADR-0078 + schema + failing test | Measure per task | [`trajectories.md`](../05_contracts/trajectories.md) · [`0078`](../02_decisions/0078-trajectory-un-hollowing-cost-accounting.md) |
| **Continuation (NOVA-2)** | Active RF-25 board row + ADR-0082 + failing test | Measure per task | [`sequences.md`](../04_architecture/sequences.md) · [`0082`](../02_decisions/0082-universal-turn-loop-m10-compatibility-contract.md) |
| **Composition / Plugins** | Open milestone + manifest contract + component graph ADR + compose tests | Measure per task | [`manifests.md`](../05_contracts/manifests.md) · [`0077`](../02_decisions/0077-named-component-graph-manifest.md) |
| **Domain Pack** | Governing milestone + pack guide + current pack tests | Measure per task | [`adding_a_pack.md`](adding_a_pack.md) · [`milestones.md`](../03_execution/milestones.md) |
| **Evaluator** | Evaluator protocol + verdict contract + security test | Measure per task | [`evaluator.md`](../06_protocols/evaluator.md) · [`verdicts.md`](../05_contracts/verdicts.md) |
| **Documentation** | Documentation owner + precedence index + governing linter | Measure per task | [`documentation.md`](documentation.md) · [`docs/README.md`](../README.md) |

---

## Measurement rule

Do not claim a percentage reduction from line counts or estimates. For a representative task,
record the exact files/slices loaded, tokenizer/model, token counts, successful destination, and
whether leadership clarification was required. Only then compare the targeted bundle with the old
reading path.

## Fixed execution pattern

For every code task, load context in this order:

1. active-board task and owner;
2. governing SPEC clause and accepted ADR;
3. one architecture/contract/protocol page for discovery;
4. exact implementation symbols;
5. bound falsifier and the smallest regression suite.

Stop following links when the implementation symbol and proof obligation are unambiguous. Historical
reviews may explain provenance but must not expand the active scope.
