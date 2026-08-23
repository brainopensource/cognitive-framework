---
id: normative-evidence-law
class: law
authority: normative
canonical_for:
  - trajectory-accounting-law
  - evaluator-verdict-law
status: living
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-23
read_when:
  - changing-trajectories-or-costs
  - changing-evaluator-verdicts
do_not_read_when:
  - changing-only-ui-or-documentation
supersedes: []
superseded_by: null
---

# Evidence, identities, and promotion law

The evidence contract is distributed across the detailed runtime law, measurement constitution, and
the trajectory/verdict contracts. This index prevents agents from loading unrelated law.

## Trajectory accounting

`EpisodeCompleted` MUST contain a complete `mhf.trajectory/1`. A cold continuation loads the durable
pre-crash prefix, appends current turns, preserves ordered `invocations`, and reconciles pending
Governor leases before emitting `RunRecovered`. Costs are additive across retries and escalations;
each measurement is `measured`, `estimated`, or `unavailable`, never silently invented. See
[`../05_contracts/trajectories.md`](../05_contracts/trajectories.md),
[`../02_decisions/0078-trajectory-content-contract.md`](../02_decisions/0078-trajectory-content-contract.md),
and [`RUNTIME.md §1.3`](RUNTIME.md#13-determinism--replay-contract).

## Evaluator and verdicts

The evaluator is exterior to the judged runtime and verdicts are Ed25519-signed. The authority
predicate binds `D_H`, `D_R`, `D_X`, evidence, and signer identity. A missing evaluator is declared
before execution as `evaluation: none`, deriving `unattributable_for_promotion = true`; an unsigned
or forged verdict is a hard failure, never an absence. See
[`../05_contracts/verdicts.md`](../05_contracts/verdicts.md) and
[`../02_decisions/0079-absent-vs-forged-guardrails.md`](../02_decisions/0079-absent-vs-forged-guardrails.md).

## Identity tuple

`D_H` identifies the complete harness composition; `D_R` adds runtime, environment, model, and oracle;
`D_X` adds dataset and protocol. These identities MUST remain distinct in evidence and promotion.
