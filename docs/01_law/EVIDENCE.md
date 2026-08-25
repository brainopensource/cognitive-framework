---
id: normative-evidence-law
class: law
authority: normative
canonical_for:
  - trajectory-accounting-law
  - evaluator-verdict-law
status: living
owner: principal-systems-architect
version: "0.6.2"
last_verified: 2026-08-25
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
[`../02_decisions/0078-trajectory-un-hollowing-cost-accounting.md`](../02_decisions/0078-trajectory-un-hollowing-cost-accounting.md),
and [`RUNTIME.md §1.3`](RUNTIME.md#13-determinism--replay-contract).

## Evaluator and verdicts

For a promotion-eligible assurance run, the evaluator is exterior to the judged runtime and verdicts
are Ed25519-signed. Product runs MAY declare `evaluation: none`; that choice enters `D_R` and derives
`unattributable_for_promotion = true`, but does not make the product execution invalid. An unsigned
or forged verdict is a hard failure when evaluation was declared, never an absence. See
[`../05_contracts/verdicts.md`](../05_contracts/verdicts.md) and
[`../02_decisions/0079-absent-vs-forged-derived-promotability.md`](../02_decisions/0079-absent-vs-forged-derived-promotability.md).

## Identity tuple

`D_H` identifies the complete harness composition; `D_R` adds runtime, environment, model, and oracle;
`D_X` adds dataset and protocol. These identities MUST remain distinct in evidence and promotion.

## Product proof (M-4 / RF-95)

M-4 requires one live-model coding run through canonical composition and ordinary mediated tools. It
MUST produce a real workspace diff, a passing task-specific verification receipt, a file-backed WAL,
a complete terminal trajectory, and fresh-process reconstruction of the same terminal state. Fake or
cassette providers, alternate execution drivers, stitched traces, and manual event repair deny RF-95.
Exterior evaluation and containment MAY be selected but are not required for this product gate.

## Hermetic foundation evidence bundle (RF-85 optional assurance)

`mhf.foundation-evidence/1` is a derived audit artifact, not a new authority ledger. Its header binds
one `project_id`, `run_id`, `episode_id`, `D_H`, `D_R`, optional `D_X`, ledger range, terminal chain
digest, task/oracle preregistration, and the immutable source digest for each required row.

The nine rows derive respectively from: model invocation/usage; kernel authorization/grant/budget and
effect events; workspace artifact receipts; containment attestation/probes; evaluator-gateway
signature verification; file-backed WAL chain; fresh-process reconstruction; the emitted rich
trajectory; and import/runtime trace of the canonical composition/activation/session authority.

The auditor MUST recompute a claim or invoke its authoritative verifier. It MUST NOT trust submitted
booleans such as `signature_verified`, `cost_conserved`, or `sandboxed`, nor invent a canonical path
when absent. Every row cross-binds the same composition, run/episode lineage, event range, and source
artifacts. A textual signature, altered digest, mixed lineage, missing measurement status, unattested
probe, fake/cassette provider, host fallback, manual repair, or stitched trace denies.

A hermetic synthetic bundle may prove validator and negative cases but is permanently ineligible for
RF-85. RF-85 retains its original nine-row independent-verification contract and MUST NOT be claimed
by an RF-95 product run.
