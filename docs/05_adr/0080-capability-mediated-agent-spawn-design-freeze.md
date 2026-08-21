---
adr: 0080
title: "Capability-mediated agent.spawn design freeze"
status: accepted
accepted_date: 2026-08-21
source_section: "ALFA Tier S+ Director Ratification"
implementation_milestone: "M-6 / v0.8.0"
implementation_status: deferred
---

# ADR-0080: Capability-mediated `agent.spawn` design freeze

**Context.** `EpisodeEngine.spawn()` already supplies recursive semantics and attenuation, but
future tree search and hierarchical decomposition require delegation to be an explicitly mediated
effect rather than an engine-only callback. Implementing it before evidence, generality, and the
M-4 stop line would enlarge the reviewed surface too early.

**Decision.**

1. The design is accepted now; implementation is **forbidden before M-6**, after M-4 and the M-5
   generality gate. `EpisodeEngine.spawn()` remains the semantic oracle until then.
2. `agent.spawn` is a privileged typed effect and traverses S0–S12 without a bypass:

   ```text
   verb: agent.spawn
   selector: {kind: generic, uriPattern: "agent://spawn/harness/<D_H>"}
   args: {harness_digest, entrypoint, brief, requested_capabilities, reservation, parent_lease}
   receipt: {request_digest, outcome, child_principal_id, child_episode_id,
             lease_id, grant_digest, settled_cost}
   events: ChildSpawned, ChildReturned
   ```

3. The target harness is a resource. A grant may authorize one `D_H` and deny another.
4. Effective child authority is the fail-closed intersection of parent, target manifest, plugin,
   and request ceilings. Widening is denied as a whole, never silently normalized into acceptance.
5. The child's reservation is a parent-linked sublease. Additive use debits parent remaining
   capacity; depth increments along the path; sibling depths are not summed; turns remain an
   episode ceiling.
6. Durable intent precedes creation of the child principal, workspace, process, or session. Every
   terminal/failure path settles and releases the sublease and records lineage.
7. Child output returns as untrusted-derived context and cannot justify capability widening.
8. Child processes receive no ambient handles, model credentials, evaluator endpoint, or parent
   memory. Reachability must be selector-mediated and monotonically attenuated.
9. `spawn` remains the only delegation primitive. No `MetaAgent`, `SwarmEngine`, or second loop is
   introduced; swarms remain policy over ordinary agents and ledger projections.
10. The implementation MUST keep the total TCB at or below 1438 logical LOC and has a target net
    kernel delta of at most 40 LOC. Exceeding the target requires redesign or a newer ADR; it does
    not authorize raising the ceiling.

**Bound falsifiers.** RF-55: no grant means no delegation. RF-56: spawn has durable intent and a
receipt. RF-57: undeclared target `D_H` is denied. RF-58: child cannot reach the evaluator without
an explicit selector. RF-59: wider child authority is denied. These tests may be authored earlier
but become implementation gates at M-6.

**Alternatives rejected.** A planner callback that creates children directly; copied counters;
ambient inherited connections; a separate recursion engine; or implementing spawn to demonstrate
M-4.

**Reversal condition.** The bound suite cannot be implemented within the TCB ceiling, or measured
S0–S12 mediation cost makes bounded deep delegation impractical. A newer ADR must then choose a
different mechanism while preserving attenuation, durable intent, and evidence.

**Owner · status.** Principal Systems Architect / Kernel Owner · design accepted by Engineering
Director · implementation deferred to M-6 · 2026-08-21
