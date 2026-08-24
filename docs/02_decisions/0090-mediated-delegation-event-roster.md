---
id: adr-0090-mediated-delegation-event-roster
adr: 0090
class: decision
authority: binding-decision
canonical_for:
  - mediated-delegation-event-roster
status: accepted
owner: principal-architect-specialist
version: "0.6.3"
last_verified: 2026-08-24
accepted_date: 2026-08-24
extends:
  - ADR-0088
  - ADR-0080
supersedes: []
superseded_by: null
---

# ADR-0090 — `ChildSpawned` / `ChildReturned` event allocation for mediated delegation

**Status:** ACCEPTED — ratified by the CEO on 2026-08-24.
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

---

## Ratification record (2026-08-24)

Ratified by the CEO. Applied to `feat_W4-W6_Higgs_core` as
`M6_CLOSE_ADR0090.patch` (one commit, five files, kernel untouched) plus one
corrective commit. Rollback is `git revert` of that series.

### What this ADR closes, and what it does not

This ADR closes the **event roster** question for mediated delegation: the two
kinds are allocated, folded, single-writer bound, and schema-described. It does
**not** close milestone M-6.

`agent.spawn` remains inert at three independent points —
`domain/artifacts/manifest.py` refuses any manifest declaring the verb,
`runtime/delegation.py` refuses every spawn (`M6_SPAWN_ACTIVE = False`), and the
verb sits on the inert-verb list. No child episode can be created, so no
`ChildSpawned` can be emitted by the product. The falsifiers below (RF-55–RF-59)
are **named but unallocated**: no such test exists in the repository, and
[`INDEX.md`](INDEX.md) does not register the range. M-6's exit gate is therefore
unmet, and M-6 stays LOCKED behind M-4 and M-5. See
[`milestones.md`](../03_execution/milestones.md).

### Payload key spelling (corrective)

The decision table above is camelCase; the bundle's `child_events.schema.json`
is snake_case; the reducer as first landed read snake_case only. Since every
other payload in the ledger is camelCase, a repo-convention `ChildSpawned` fell
through the fold silently — folding nothing and raising nothing, which left the
duplicate/orphan/double-return/intent-mismatch guards unreachable.

The reducer now accepts **either** spelling, camelCase preferred, and **denies**
a child event carrying no identifiable child id rather than skipping it. Both
spellings are accepted rather than one being chosen because `SpawnAdapter` does
not exist yet; when it lands and the schema is ratified into `schemas/mhf/`, the
losing spelling is dropped. Pinned by
`test/contracts/test_adr0090_child_fold.py`.

### Known gap, deliberately not closed here

`LedgerState.to_canonical_dict()` omits `children`, so the state digest is blind
to delegation: a state with a spawned child and one without digest identically.
Closing it changes the digest of every existing run — a change to the
canonicalisation surface, which is Director-only under
[`sprint_active.md`](../03_execution/sprint_active.md) §7. It must be closed
before M-4 row 7 (cold reconstruction folds to the *same state*) can be claimed
for any run containing delegation. Current behaviour is pinned by
`TheStateDigestDoesNotSeeChildren` so it is changed deliberately, not
discovered.
