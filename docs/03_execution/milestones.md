---
id: macro-milestones-ladder
class: execution
authority: execution
canonical_for:
  - macro-milestones-ladder
  - wave-gates
status: living
owner: engineering-director
version: "0.7.0"
last_verified: 2026-08-25
supersedes: []
superseded_by: null
---

# Macro Milestones — AETHER Higgs Release

This file defines sequencing and objective exit gates. Only
[`sprint_active.md`](sprint_active.md) authorizes current implementation. A milestone closes on
evidence from the canonical executable path, never because code, schemas, or isolated tests exist.

## Milestone Ladder

| Milestone | Outcome | Exit gate | Status | Depends on |
|---|---|---|---|---|
| **M-0 Engineering Truth** | CI measures production truth and named falsifiers | Production suites, F-01…F-21, codegen, architecture gates | **COMPLETE** | ADR-0075 |
| **M-1 Trust Spine** | Generic effect authority, budgets, provenance, event truth | S0–S12 falsifiers; single writer; TCB `<=1438` | **COMPLETE** | M-0 |
| **M-2 Runtime Recovery** | Truthful trajectories and restart-safe state | RF-23 rich trajectory and RF-25 fresh-process WAL continuation | **COMPLETE** | M-1 |
| **M-3 Extensibility Contracts** | Named graph, registry lifecycle, Layer-0 retirement | RF-28–RF-45 retained; operational closure resolved by M-3C | **COMPLETE** | M-2 |
| **M-3C Canonical Convergence** | One `compose -> activate -> run` authority | RF-78–RF-84; identity, lifecycle, durability, authority retirement | **COMPLETE** | M-3 |
| **W-3D Product Profiles** | Identity-bearing profiles and one adapter bootstrap | RF-87–RF-94 | **COMPLETE** | M-3C |
| **M-4 Product Coding Proof** | Useful, durable coding agent through the framework | RF-95 | **ACTIVE** | W-3D, ADR-0094 |
| **M-5 Generality Proof** | Deterministic Formal Pack #2 through unchanged substrate | RF-86 plus RF-52/RF-53 witness | **BLOCKED ON RF-95** — RF-86 measures zero diff against a substrate baseline a real run has exercised. Preparation (pack, task, oracle, RED tests) is open now. | RF-95 |
| **M-6 Mediated Delegation** | Capability-bounded `agent.spawn` as an ordinary effect | RF-55–RF-59; attenuation, recovery, kill-tree proof | **BLOCKED ON `SpawnAdapter`** — no spawn adapter or attenuation algebra in the production import path; `agent.spawn` is inert in `runtime/delegation.py` (`M6_SPAWN_ACTIVE = False`), `domain/artifacts/manifest.py`, and the inert-verb list. | `SpawnAdapter` + attenuation algebra |
| **M-7 Measured Concurrency** | Optional scheduler only if measurement justifies it | M7-01 plus successor ADR and RF-46–RF-48 | **BLOCKED ON M7-01 BASELINE** — the sequential effect-log capture does not exist yet; without it a scheduler win is unmeasurable. | M7-01 result |
| **M-8 Declarative Topologies** | Replaceable agent coordination above generic execution | RF-65/RF-66; zero privileged second engine | **BLOCKED ON M7-01 BASELINE** — without a sequential baseline a topology win cannot be told from a scheduler win. | M7-01 result, M-6 |
| **M-9 Retrieval/Skills Lab** | Rebuildable retrieval and governed macro experiments | RF-67/RF-68/RF-77 plus measured lift | **HORIZON** | M-8, v1 review |
| **M-10 Governed Adaptation** | Reversible, attributable promotion experiments | RF-69/RF-70 and human rollback | **HORIZON** | M-9 |

## M-4 — Product Coding Proof (RF-95)

One fixed coding task must complete through the canonical coding pack and `Runtime.run_composed` with:

1. a live, attributable provider and measured usage;
2. repository observation through mediated tools;
3. an authorized real file mutation and non-empty diff;
4. a passing preregistered verification command receipt;
5. the `product` profile bound into `D_R`;
6. file-backed SQLite-WAL and a complete terminal trajectory;
7. fresh-process reconstruction of the same terminal state;
8. no fake/cassette model, alternate driver, stitched trace, or manual event repair.

Host execution is allowed, but it remains an adapter behind the same capability/effect mediation and
ledger. It is not permission for the client or model to mutate the workspace outside the substrate.

### Optional RF-85 assurance

RF-85 retains its original nine-row hermetic contract: real model, authorized effect, workspace
change, rootless containment, exterior signed evaluation, WAL, cold reconstruction, rich trajectory,
and one runtime authority bound to one uninterrupted lineage. ADR-0094 makes this an optional
higher-assurance certification rather than the M-4/M-5 dependency. No RF-85 rows are currently claimed.

## M-5 — Formal Pack #2

M-5 tests whether coding is a client of the framework rather than hidden substrate semantics. The
first workload should produce a structured arithmetic/SMT-style witness checked by a deterministic,
independent adapter.

Allowed during the proof:

- a new pack, prompts, policies, schemas, and fixtures;
- domain adapters behind existing ports/binding-provider contracts;
- witness artifacts, deterministic checker, and client rendering.

Forbidden during the RF-86 proof interval:

- semantic changes under `vanguard/packages/{domain,ports,kernel,runtime,agency/episode}`;
- a formal-specific branch in kernel, agency, session, or runtime;
- weakening RF-86 or moving `M-5-BASE` after Formal Pack implementation begins.

If the formal domain requires a substrate change, M-5 returns an abstraction finding. Make the
generic correction under a successor ADR, re-run M-4 if behavior changed materially, then establish a
new baseline before restarting the proof.

## M7-01 — Authorized Measurement Only

M7-01 may proceed in parallel. It captures actual sequential `EffectStarted`/settlement records,
resolved resources, selectors, sinks, idempotency keys, timing, WAL contention, and cache-hit rates
over a fixed-seed workload. It may not add concurrency, scheduler, workers, claims, leases, or topology.

Below 30% useful independence, the default Director decision is to cancel M-7 and retain I-11. At or
above 30%, a successor ADR must still quantify attainable speedup and contention cost.

## Dependency Rules

- Work is blocked only by a named unfinished interface, schema, invariant, primitive, or runtime
  contract — never because a preceding milestone has not been ceremonially closed. Every lane
  without such a dependency (coding CLI/TUI, coding pack, model/tool adapters, M-5 preparation,
  M7-01, indexing behind `IndexPort`, context management, tooling) runs in parallel now.
- `M-5-BASE` must point to the reviewed post-ADR-0094 substrate before Formal Pack code begins.
- An ADR-authorized substrate correction makes the old RF-86 baseline intentionally red; RF-86 is
  never weakened. Advance the tag only after the correction is committed and verified.
- ADR-0090/0091 prepare M-6 event/digest semantics but do not activate delegation.
- Topology decides what may run; scheduler decides when/where; kernel decides whether an effect is
  authorized. These responsibilities do not merge.
- Security/assurance may vary by execution profile. Layer boundaries, event lineage, and authority
  mediation do not.
- Reviews under `_archive/` are inputs, never execution authority.

## Common Gate Sequence

```text
accepted ADR when architecture changes
-> allocated RED falsifier
-> focused suites
-> full Python and TypeScript gates
-> boundaries / TCB / domain blindness / event coverage / duplication
-> RF IDs / metadata / links / stale paths / secrets
-> real-run evidence
-> independent milestone decision
```
