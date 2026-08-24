---
id: adr-0088-m3c-m8-concept-lock
adr: 0088
class: decision
authority: binding-decision
canonical_for:
  - m3c-m8-concept-lock
status: append-only
owner: engineering-director
version: "0.6.2"
last_verified: 2026-08-23
accepted_date: 2026-08-23
extends:
  - ADR-0077
  - ADR-0078
  - ADR-0080
  - ADR-0081
  - ADR-0082
  - ADR-0083
  - ADR-0084
  - ADR-0085
supersedes: []
superseded_by: null
---

# ADR-0088 — M-3C to M-8 concept lock

## Status and scope

**Accepted by the Engineering Director.** This decision locks the architecture required to execute
M-3C and certify M-4, plans M-5 and M-6 without authorizing their implementation, reserves only the
stable seams needed by M-7 and M-8, and places M-9+ beyond the v1 foundation as non-authorizing
research.

The decision is based on the code at commit
`e3acc5c228f9a61a357d955c86317369f3339841`, the current law and accepted ADRs, the ALFA/Fi proposal
lineage, and the Higgs forensic review. Proposal and review documents remain evidence, never law.

## Context

M-3 implemented the named-manifest parser/compiler contracts, registry lifecycle pieces, and atomic
`layer0/` retirement, but the public runtime still enters through the legacy pack reader and global
bindings. The v2 compiler and lifecycle are side paths; the table probe does not execute through the
public runtime; release execution defaults to an in-memory store; and the M-4 auditor accepts supplied
claims that are not all derived or cryptographically cross-checked. Calling M-3 operationally complete
would certify two architectural truths.

The correction is a bounded convergence, not a new substrate. Kernel authority, S0–S12, typed
budgets, JCS, identity separation, single-writer WAL state, exterior evaluation, rootless isolation,
and the sequential reference mechanism remain unchanged.

## Decision 1 — Canonical composition and activation (M-3C)

The only production chain is:

```text
mhf.manifest/2 bytes
  -> CanonicalManifest
  -> FrozenComposition [D_H]
  -> ActivationPlan [activation_digest, binds D_H]
  -> RunPlan [D_R, binds project/run/task/environment/model/oracle/store]
  -> sequential EpisodeEngine -> S0-S12 -> receipts/evidence
```

1. `CanonicalManifest` is the sole schema-authoritative normalized manifest value. Supported legacy
   bytes may enter only through a compatibility reader and MUST normalize before semantic validation.
   No legacy value may cross the composition boundary.
2. `FrozenComposition` is an immutable domain value containing the complete resolved logical graph:
   named components, implementation/config digests, interfaces, bindings, entrypoints, profiles,
   isolation, evidence policy, and capability ceilings. Its JCS digest is `D_H`.
3. `ActivationPlan` is an immutable runtime projection of `FrozenComposition`: concrete component
   factories/cells, validated interfaces, effective ceilings, initialization dependencies, readiness,
   and reverse cleanup order. It introduces no authority and does not schedule graph control flow.
   Its digest binds `D_H` and contributes to `D_R`.
4. `RunPlan` immutably binds the frozen composition and activation plan to the declared project,
   task, environment, store, model route, oracle/evaluator, root authority, budget, and execution mode.
   `run_id` is a correlation identifier bound to events; it is not a substitute for `D_R`.
5. `FrozenHarness` may remain temporarily as a public compatibility facade, but it MUST wrap the one
   `FrozenComposition`; it cannot be a second composition identity. Duplicate generated wire values
   are representations of the same schema, not independent domain authorities.
6. The authored form after M-3C is `/2`. Per ADR-0077, supported `mhf.harness/1` input remains readable
   through M-4 and is reviewed at M-5. M-3C retires legacy execution authority, not compatibility
   ingress before its ratified sunset.
7. Domain verbs are supplied by namespaced binding providers implementing trusted ports. A global
   coding-specific `DEFAULT_BINDINGS` table cannot be the extension authority. Unknown provider,
   interface, selector relation, field, ref, endpoint, or unconsumed authority fails before activation.
8. Profiles remain identity-bearing and sequential before M-7. `agent.spawn` remains identity-bearing
   and refused with its named pre-M-6 cause.

## Decision 2 — Honest foundation evidence (M-4)

M-4 adds no architecture. M-3C MUST prepare a derived artifact contract
`mhf.foundation-evidence/1`; M-4 populates it from one real run.

The bundle header binds `project_id`, `run_id`, `episode_id`, `D_H`, `D_R`, optional experiment
`D_X`, ledger range, terminal chain digest, task/oracle preregistration, and every row source digest.
Each of the nine rows is derived from canonical sources:

| Row | Authoritative source |
|---:|---|
| 1 | model-adapter invocation and measured usage record |
| 2 | kernel authorization, grant, reservation, S8 verification, and effect events |
| 3 | workspace artifact digests and effect receipt |
| 4 | signed/attested containment report and startup probes |
| 5 | evaluator gateway verification of the exterior Ed25519 verdict |
| 6 | file-backed SQLite-WAL event range and project hash chain |
| 7 | fresh-process reconstruction report bound to the same chain and state digest |
| 8 | emitted `mhf.trajectory/1` and conserved accounting result |
| 9 | import/runtime trace proving the canonical composition/activation/session authority |

The auditor MUST recompute or invoke the authoritative verifier; it MUST NOT trust booleans such as
`signature_verified`, `cost_conserved`, `sandboxed`, or a default runtime path. A text-shaped
signature, mixed lineage under one `run_id`, missing measurement status, altered cross-digest,
unattested probe, synthetic provider, host fallback, manual repair, or stitched trace denies.

M-4 closes only after an independent reviewer verifies one uninterrupted run. A synthetic fixture is
useful M-3C preparation evidence but is permanently ineligible for the M-4 claim.

## Decision 3 — Second-domain generality and T0 witness (M-5 plan)

M-5 is **Math & Formal Deductive Verification Pack #2**. The exact proof language/solver is R2 and is
selected at M-5 through a preregistered toolchain decision; it is not frozen here. The pack supplies
its manifest, prompts/context policy, toolkit/environment adapter, deterministic exterior checker,
fixtures, and oracle identity using the five existing SPIs and ports.

```text
freeze task + checker + toolchain + policy
  -> compose /2 -> activate -> run S0-S12
  -> exterior formal witness -> WAL/trajectory -> cold reconstruct
  -> compare core tree digest -> issue generality evidence
```

The proof interval permits changes only under pack, adapter, evaluator/container, and test surfaces.
There MUST be no semantic diff under `vanguard/packages/{domain,ports,kernel,agency,runtime}`. If a
missing generic substrate capability is discovered, M-5 fails and returns a bounded correction to
leadership; the proof reruns from a new baseline. Domain logic may not be smuggled into the substrate.

T0 witness memoization binds subject/input, `D_H/D_R`, environment, checker, toolchain, assurance,
policy version, result, signature, and invalidation conditions. A changed field is a miss; evidence is
never rebound to a new subject and never widens authority.

## Decision 4 — Capability-mediated delegation (M-6 plan)

ADR-0080 remains controlling. `agent.spawn` is handled by the generic kernel dispatch protocol, not a
verb-specific kernel branch. Agency may request spawn but cannot directly create a production child.
A runtime spawn effect adapter creates the child only after durable S8a intent and successful S0–S8
authorization.

```text
request agent.spawn(target D_H, brief, requested ceiling, sublease)
  -> S0..S8a durable intent
  -> runtime adapter creates child principal/session/workspace
  -> child runs with intersection(parent, target, plugin, request)
  -> ChildSpawned/ChildReturned + receipt
  -> S10..S12 settle/release -> return untrusted-derived output
```

The child receives no ambient handles, credentials, evaluator endpoint, or parent memory. Additive
budget is a conserved parent-linked sublease; depth increments; turns remain bounded. Recursive
target cycles are not categorically forbidden, because recursion is intentional, but depth, turns,
budget, selector scope, admission policy, and optional pack fan-out MUST make them finite. Recovery
reconstructs parent/child lineage and never repeats a settled spawn; open intent remains
undeterminable until exterior reconciliation.

No new spawn event kind is presumed: `ChildSpawned` and `ChildReturned` carry outcome/lineage unless a
red falsifier proves the existing catalog insufficient. The TCB remains `<= 1438` LOC.

## Decision 5 — Scale compatibility seams (M-7 and M-8 only)

No M-7 or M-8 production implementation is authorized by this ADR.

1. A scheduler claim lease is coordination state (`claim_id`, owner, issued/expiry/heartbeat,
   attempt, idempotency key), not a capability grant and not the budget `millis` dimension. Budget
   remains four conserved additive resources plus `turns`/`depth` structural ceilings.
2. Physical worker attempts are at-least-once under crash/reclaim. Durable command settlement is
   exactly once by idempotency key, S8a intent, single-use grant, terminal receipt, and reconciliation;
   the system does not claim exactly-once physical side effects.
3. Unknown selector overlap means conflict. I-11 remains until sequential measurements establish a
   reproducible Pareto benefit and a successor ADR explicitly lifts it.
4. The Pareto router is exterior runtime/planner policy. Feasibility and authority precede ranking;
   neither price nor belief widens authority.
5. M-8 topologies are declarative components/policies lowered to ordinary scheduler work and mediated
   spawn. Topology state may be durable plugin/pack data, but the Named Component Graph remains static
   composition and the kernel/episode mechanism remains topology-blind.
6. A substrate-level dynamic `TopologySpec` or alternate engine is forbidden absent an RF-66
   counterexample and successor ADR. Debate, critic/reviser, planner/executor/verifier, bounded trees,
   and swarms must first prove representability without such a change.

## Decision 6 — v1 boundary and post-v1 research

M-8 is the last planned product-architecture milestone before a separate v1 release-readiness
decision. M-9 and M-10 are non-authorizing **post-v1 research horizons**. Hybrid retrieval, learned
skills, macro mining/compilation, Active Inference, DPO, evolutionary policy learning, automatic
candidate generation, and governed meta-cognition remain exterior experiments. They may consume
versioned schemas and signed trajectories but cannot enter kernel authority, mint evidence, or move
the human promotion pointer.

T0 exact witness reuse remains part of M-5; it is deterministic evidence reuse, not adaptive
meta-cognition. ADR-0084's T1–T3 semantics remain accepted but their product scheduling is deferred
until a post-v1 Director decision.

## Falsifier allocation

- `RF-78` — code and table `/2` manifests compose to the single public frozen value.
- `RF-79` — supported legacy input normalizes to equivalent facts/`D_H` and no legacy value crosses
  the compatibility boundary.
- `RF-80` — public activation traverses registry lifecycle on the run lineage and cleans up every
  success/fault/cancel/evaluator-failure path.
- `RF-81` — domain binding providers wire both domains without a global coding-specific authority.
- `RF-82` — the release path uses file-backed WAL and fresh-process continuation preserves
  composition/run/trajectory identity.
- `RF-83` — foundation evidence is source-derived, cross-bound, and cryptographically verified;
  forged assertions deny.
- `RF-84` — no competing production parser/compiler/activation/runtime authority remains.
- `RF-85` — one real M-4 run populates all nine rows under one uninterrupted lineage.
- `RF-86` — Formal Pack #2 achieves execution/evidence parity with an unchanged substrate tree.

## Alternatives rejected

- certifying the legacy coding path as M-4;
- deleting the compatibility reader before its M-5 review;
- making class names architectural without distinct responsibilities;
- adding table or future domain verbs to a global runtime binding table;
- trusting self-attested evidence booleans;
- adding `agent.spawn` branches, scheduling, topology, Pareto, or cognition to the kernel;
- treating budget `millis` as a scheduler TTL;
- promising exactly-once physical effects;
- prebuilding M-7/M-8 or implementing M-9+ before their gates.

## Reversal conditions

This lock reopens only if a bound falsifier proves one of its contracts impossible, RF-66 supplies a
real topology that cannot be represented by composition plus mediated delegation, the M-5 domain
requires a genuinely domain-neutral missing primitive, or measured M-7 evidence shows that the locked
seams prevent safe Pareto improvement. Preference, naming, or implementation inconvenience is not
reversal evidence.
