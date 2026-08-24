# ADR-0090 — `ChildSpawned` / `ChildReturned` event allocation for mediated delegation

**Status:** PROPOSED — requires Engineering Director ratification
**Supersedes:** none. **Successor to:** ADR-0088 (canonical composition), ADR-0089 (profiles)
**Date:** 2026-08-24
**Closes:** M-6 item 3 (the only frozen-surface change in the milestone)

---

## Context

`sprint_active.md` §2 freezes the event roster: a new event kind requires
allocation, a single legal writer, a reducer, a schema, conformance vectors, and
coverage proof. M-6 implements `agent.spawn` as an ordinary capability-mediated
effect. The attenuation algebra, spawn adapter, and cold-reconciliation path add
**zero kernel LOC** (TCB measured unchanged at 1737) and require no new SPI.

But delegation is not observable from the existing roster. `EffectStarted` /
`EffectCompleted` describe the *authorisation* of the spawn descriptor; they
cannot express that a child episode came into existence, carried attenuated
authority, and returned an outcome. Without a distinct event kind, parent-child
lineage would have to be inferred from payload conventions — exactly the "path
bag pretending to be a graph" failure `001_alfa` §3 rejects.

## Decision

Allocate exactly two event kinds. No third.

| kind | writer | payload (required) |
|---|---|---|
| `ChildSpawned` | `runtime.SpawnAdapter` **only** | `parentEpisodeId`, `childEpisodeId`, `authority[]`, `budgetShare`, `depth`, `lineage[]`, `descriptorDigest`, `grantId` |
| `ChildReturned` | `runtime.SpawnAdapter` **only** | `childEpisodeId`, `outcome`, `cost`, `terminal`, `settledIntentKey` |

### Constraints

1. **Single writer.** `SpawnAdapter` is the sole legal writer for both kinds.
   Plugins, workers, and child episodes propose; they never append these
   envelopes. Enforced by the existing single-writer linter.
2. **No kernel change.** Both events are emitted from `runtime/`. The kernel
   authorises a generic descriptor and never learns what spawning is.
3. **`ChildSpawned` is emitted after attenuation succeeds and after the S8a
   durable intent**, never before. An event that precedes the durable intent
   would let a crash produce a child with no reconcilable record.
4. **Reducer contract.** Folding `ChildSpawned` then `ChildReturned` yields a
   closed child record. A `ChildSpawned` with no matching `ChildReturned` folds
   to `open` and is reconciled by the cold path (`OCCURRED` / `DID_NOT_OCCUR` /
   `UNDETERMINABLE`), never assumed complete.
5. **Cost conservation.** Child cost folds into the parent trajectory as a
   nested invocation. A child's spend is the parent's spend; it is never new
   budget. `spawns` is a typed budget dimension, so quota exhaustion recovers
   across restarts through the ordinary reservation machinery.
6. **Authority is recorded, not asserted.** `authority[]` on `ChildSpawned` is
   the *derived* result of `attenuate()`, so an auditor can recompute the
   intersection against the parent grant rather than trust the payload.

## Alternatives rejected

**Reuse `EffectStarted` with a `spawn` discriminator.** Cheaper, and wrong: it
overloads one kind with two reducer semantics, and `001_alfa` §3 (via 005
Epsilon) explicitly forbids folding a material FSM transition into another
lifecycle payload. Every material transition must be catalogued, emitted, and
reduced.

**A `ChildFailed` third kind.** Rejected as redundant. `ChildReturned` already
carries `outcome`; a separate failure kind creates two paths to one state and
doubles the reducer surface.

**Emitting from the kernel.** Rejected. It would put parent/child lifecycle
inside the TCB for no new authority semantics, violating
`Higgs_update_concepts.md` L155.

## Consequences

* Schema additions under `schemas/mhf/` plus conformance vectors (valid,
  missing-required, wrong-type) mirroring the existing receipt vectors.
* One reducer addition; no change to existing reducers.
* Kill-tree drill required: SIGKILL the parent mid-child and assert the cold
  path returns `UNDETERMINABLE`, not a retry.
* Rollback is the commit series; it removes the kinds and the adapter binding
  and cannot restore a legacy execution authority.

## Falsifiers

| id | must fail |
|---|---|
| RF-55 | child authority not a subset of parent |
| RF-56 | budget minted rather than subtracted |
| RF-57 | depth or fan-out exceeded |
| RF-58 | delegation cycle admitted |
| RF-59 | a non-`SpawnAdapter` writer appends either kind |
| RF-26 | a settled spawn is repeated after restart |
