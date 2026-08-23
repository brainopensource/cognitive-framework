---
adr: 0077
title: "Named Component Graph Manifest: mhf.manifest/2 with typed bindings"
status: accepted
accepted_date: 2026-08-21
amended_date: 2026-08-21
source_section: "ALFA Tier S+ Director Ratification"
implementation_milestone: "M-3 / v0.6.2"
---

# ADR-0077: Named Component Graph Manifest (`mhf.manifest/2`)

**Context.** The fixed `mhf.harness/1` slots and the packages-path `components` role-to-path map
describe one coding-shaped harness. The packages map has named paths but no typed edges, while
`ManifestLoader.REGISTERED_COMPONENT_CONSUMERS` and `runtime.compose.ROLE_KIND` hard-code the
accepted roles. Debate, critic/reviser loops, tree search, and swarms would therefore require
engine branches or another composition language. Because the resolved composition is the subject
of `D_H`, postponing the correction until after M-4 would make later corpus attribution expensive.

**Decision.**

1. The canonical successor manifest is `mhf.manifest/2`, a **Named Component Graph** containing:
   unique component instances, frozen implementation/config references, one of the five existing
   SPI kinds, declared interfaces, isolation and capability ceilings, explicit typed `bindings`,
   and named entrypoints.
2. Multiple component instances MAY have the same SPI kind. Names are pack-owned identifiers;
   neither `kernel/` nor the universal episode loop may branch on a component name.
3. The graph is a **composition graph**, not a workflow engine. Bindings express addressable
   interfaces, not privileged scheduling semantics. Cycles are permitted when interfaces type
   check; turns, depth, reservations, and verifier gates enforce termination. Self-edges fail.
4. One semantic compiler performs: schema validation; immutable reference resolution; interface
   and connection checks; ceiling intersection; isolation/evidence checks; unread-field rejection;
   then JCS freezing. Unknown refs, endpoints, kinds, required interfaces, or authority-bearing
   unconsumed components fail at compose time.
5. `D_H` covers component names/kinds, resolved digests, behavior-affecting config, ceilings,
   isolation, evidence policy, entrypoints, and the complete binding edge set, in addition to the
   inputs already required by ADR-0074. An edge-only change changes `D_H`.
6. The compiler converges all current composition surfaces: the domain role/path bag,
   `REGISTERED_COMPONENT_CONSUMERS`, and `ROLE_KIND`. Exactly one parser produces the canonical
   manifest value from validated bytes.
7. Component ceilings intersect the harness, publisher, and runtime ceilings through the one
   canonical selector algebra. An empty or uncomparable intersection authorizes nothing.
8. `mhf.harness/1` remains readable through M-4 and normalizes to the v2 domain value. New writes
   use `/2` after M-3; the compatibility reader is reviewed for removal at M-5.
9. This ADR changes no SPI count and authorizes no M-2 graph implementation. Implementation begins
   only when M-2 and RF-25 are green and M-3 is opened on the active board.

**Bound falsifiers.** RF-28: two same-kind named components compile. RF-29: the linear,
generator/critic, debate, bounded-tree, cyclic-critic, and stigmergic fixtures produce stable,
distinct `D_H` values with no kernel or episode-engine change. RF-30: an edge-only change changes
`D_H`. RF-31: ceiling intersection fails closed. RF-32: unknown/dangling/unconsumed authority
fails at compose. RF-33: one canonical parser exists.

**Alternatives rejected.** A `stigmergic_blackboard` boolean; a larger fixed slot list; an open
`relation` string that can smuggle in a workflow engine; a graph database as authority; or a new
runtime per topology.

**Reversal condition.** A real topology that cannot be represented by typed components and
bindings but can be represented by the fixed slots, or measured evidence that compose-time graph
resolution materially damages run latency. Preference or migration inconvenience is insufficient.

**Owner · status.** Principal Systems Architect / Tech Lead · accepted by Engineering Director ·
2026-08-21

---

## Amendment — 2026-08-21: reserve profiles and spawn authorization shape

This same-day, pre-implementation amendment is recorded in place under ADR-0000; it is not a
silent rewrite and authorizes no M-3, M-6, or M-7 implementation.

1. `mhf.manifest/2` reserves `profiles` as versioned composition policy. The complete profile
   declaration enters `D_H` even while execution remains sequential and the M-7 router is absent.
2. Spawn authorization reuses the existing capability declaration and selector algebra. A
   component may declare verb `agent.spawn` with a generic selector of the form
   `agent://spawn/harness/<D_H>`. There is no permissive `spawn_grant: true` field. An absent
   `agent.spawn` declaration means deny.
3. At M-3, each reservation discharges as **parse -> digest -> refuse -> falsify**: the compiler
   parses and includes it in `D_H`, then refuses an `agent.spawn` declaration with the named reason
   `agent.spawn not implemented before M-6`; profile activation beyond sequential execution is
   likewise refused until M-7. The inert-state tests are owned by RF-73 and RF-74.
4. Activating either reservation later changes behavior but not the identity pre-image. This
   prevents M-6/M-7 from retroactively re-attributing trajectories emitted after M-3.

Clauses 3 and 9 remain controlling: the graph is not a workflow engine, and this reservation does
not authorize graph, spawn, router, or concurrency implementation in M-2.

---

## Amendment — 2026-08-23: composition graph is statically exhausted

The compiler resolves and freezes the complete Named Component Graph before a run begins. The
runtime MUST NOT walk graph edges as a dynamic control-flow DAG, schedule graph nodes, or introduce
a second episode engine. Every episode continues through one unary, sequential universal turn loop.
Multi-agent topology requires capability-mediated `agent.spawn` at M-6; composed plugins remain
ordinary callees of that loop. Typed bindings provide addresses and interfaces only.
