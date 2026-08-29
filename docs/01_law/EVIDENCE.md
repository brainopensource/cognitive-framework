---
id: normative-evidence-law
class: law
authority: normative
canonical_for:
  - trajectory-accounting-law
  - evaluator-verdict-law
status: living
owner: principal-systems-architect
version: "0.9.0b1"
last_verified: 2026-08-26
read_when:
  - changing-trajectories-or-costs
  - changing-evaluator-verdicts
do_not_read_when:
  - changing-only-ui-or-documentation
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Evidence, identities, and promotion law

The evidence contract is distributed across the detailed runtime law, measurement constitution, and
the trajectory/verdict contracts. This index prevents agents from loading unrelated law.

> **Authority.** Normative, but subordinate to [`VISION.md`](../../VISION.md) (Law Zero, `ADR-0095`).

## Observability is part of the product, not post-processing

Every execution is potentially an experimental observation. A trajectory MUST therefore preserve more
than final messages: inputs, selected context, model outputs, tool invocations, transformations,
costs, latency, errors, compaction operations, cache behaviour, strategy changes, and terminal
outcome MUST be correlatable.

**The provenance rule.** *Any variable that can materially affect a result MUST have observable
identity and provenance appropriate to the selected observability profile* — even when its full
content is stored outside the ledger or is subject to a retention policy.

This does **not** require every byte to live in the ledger. The truth model stays three-layered:

| Layer | Holds | Retention |
|---|---|---|
| **Ledger** | small, durable causal facts, plus identities and digests | permanent, append-only |
| **Artifact store** | large content: full prompts, model outputs, source snapshots, compressed contexts, patches, reports, datasets | content-addressed, configurable retention |
| **Projections** | indexes, embeddings, caches, semantic memory, repo maps | derived, rebuildable, never canonical |

Concretely: when a compaction alters context, record source range, compactor identity, relevant
parameters, input digest, and output digest. When a cache is hit, record cache identity, key, source
artifact, and validation result. The event stays small; the blob is referenced, not inlined.

Retention is a profile axis with values `digests_only`, `standard`, and `full`. It does not authorize
capture: content-capture, redaction, and sensitivity policy MUST be resolved before bytes are stored,
and the applied policy identity/version enters provenance. Experiment profiles MAY retain nearly all
authorized artifacts; interactive profiles MAY retain only digests and essential blobs.

**Reproducibility is a computed vector that MUST enter `D_R`, not an ordinal or self-declared
class.** State reconstruction and semantic replay separately record capability and verification.
WAL presence or pins establish prerequisites only; `verified` requires an immutable executed receipt
bound to the run, input history/checkpoint digest, reducer/schema pins, and reconstructed output/state
digest. `reproducibility_at_run_close` is immutable historical evidence; a later
`reproducibility_current` is a new assessment and MUST NOT overwrite it.

Evidence-ledger append failure is fatal. Artifact failure is fatal when capture is required. Optional
capture may degrade only after a durable `capture_incomplete` fact; the resulting run is
non-evidentiary and cannot satisfy RF-95 or promotion evidence. The causal record remains
authoritative; traces, spans, and metrics are correlated telemetry, never system truth.

Without this, later claims such as "metacognition improved performance", "this skill is superior", or
"this topology works better" are opinion rather than evidence.

> **Current state.** M-4 capture mechanisms and trajectory `/2` are implemented. Their release claim
> remains open because the repository has no immutable RF-95 bundle or independent acceptance
> receipt. Retrieval and topology provenance remain later integration work.

## Evidence and acceptance states

Causal facts, immutable artifacts, projections, telemetry, and attestations MUST remain separately
typed and correlated. A package progresses through `NOT_STARTED`, `IN_PROGRESS`, `PACKAGE_READY`,
`EVIDENCE_READY`, and `ACCEPTED`; `BLOCKED` always names a dependency. The underlying evidence
obligation progresses `ABSENT -> PRODUCED -> VERIFIED -> INDEPENDENTLY_ACCEPTED`. Only the terminal
state may close a mandatory gate. A waived review, missing artifact, degraded run, or passing unit
test is never an acceptance receipt.

An `aether.evidence/1` envelope MUST bind claim/protocol identity, subjects, materials, run identity,
schema/reducer pins, code/tree/dependency/environment identity, outcome, artifact references,
producer identity, and signature. Independent acceptance is a separate signed envelope from a
reviewer distinct from the producer. Canonical bytes determine the digest. Negative scientific
outcomes are admissible and may satisfy a preregistered experiment; invalid instrumentation remains
`UNDETERMINABLE`. See ADR-0101.

## Trajectory accounting

Legacy runs retain a complete `mhf.trajectory/1`; new M-4 writers MUST emit complete
`mhf.trajectory/2` while readers dual-read both versions. A cold continuation loads the durable
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
