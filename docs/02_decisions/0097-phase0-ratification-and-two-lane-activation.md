---
id: adr-0097-phase0-ratification-and-two-lane-activation
adr: 0097
class: decision
authority: binding-decision
canonical_for:
  - phase0-ratification
  - m4-two-lane-delivery
  - post-m5a-baseline-identity
  - m5b-m6-parallel-sequencing
status: accepted
owner: engineering-leadership
version: "0.2.0"
last_verified: 2026-08-25
accepted_date: 2026-08-25
extends:
  - ADR-0095
  - ADR-0096
supersedes:
  - ADR-0090-m6-after-all-of-m5-sequencing-only
  - active-sprint-pre-ratification-m5b-before-m6-restriction
  - post-m5a-reuse-of-historical-m5-base-tag
superseded_by: null
---

# ADR-0097 — Phase-0 Ratification and Two-Lane Activation

## Status

**Accepted by Project Ownership and Engineering Leadership on 2026-08-25.**

This decision converts the external Director review and corrected master handoff into canonical
authority. The external review bundle remains evidence only and MUST NOT coexist as a second active
plan. The repository's Vision, law, accepted ADRs, milestones, and active sprint remain the sources
of implementation truth.

## Decision 1 — Foundation and corrections

The AETHER architectural thesis, dependency lattice, domain-blind S0–S12 Kernel, event/artifact
truth model, projection-based agent model, and single Runtime composition seam are confirmed.
ADR-0096 v0.4.0 is ratified with its §14 corrections. No foundational rewrite, second runtime,
workflow authority, or Kernel semantic expansion is authorized.

The following M-4 contracts are frozen before implementation:

- exact model input/output capture at the Runtime provider-call seam;
- typed required-capture failure and durable optional degradation;
- immutable `/1`, dual-read `/1|/2`, single-write `/2` schema evolution;
- proof-honest RF-100 capability/verification separation;
- additive `{usd_micros,millis,tokens,bytes}` and structural `{depth,turns}`;
- digest/artifact goal representation;
- `digests_only|standard|full` retention;
- capture authorization, redaction, and sensitivity policy distinct from retention;
- automatically discovered transitive Trusted Core closure.

## Decision 2 — Two Senior lanes

Exactly two production lanes are active for M-4:

- **Dev A — Evidence Runtime and Causal Capture:** Runtime model-I/O instrumentation, artifact
  production, provenance sinks, cache capture, wiring, and failure/degradation behavior.
- **Dev B — Scientific Contracts and Verification:** execution-profile `/2`, trajectory `/2`,
  RF-100, readers, golden vectors, append/fold benchmark, and analysis tooling.

Both start from commit `f9d7ceb257e8e2c7d6014bd0a29604ffcd89ee0e`. Each has WIP=1, works
against frozen contracts/fixtures, and MUST NOT consume the other's unfinished branch.
`PACKAGE_READY` is isolated readiness, not milestone acceptance. M-4 integration order is Dev B,
then Dev A rebased on main, then the integrated gate and RF-95.

Shared-file ownership is exclusive:

| Surface | Owner |
|---|---|
| `runtime/profiles.py`, `runtime/reproducibility.py`, `runtime/trajectory.py`, trajectory reader, profile/trajectory schemas | Dev B |
| `runtime/session.py`, `runtime/artifacts.py`, `runtime/provenance.py`, `runtime/wiring.py`, `runtime/root.py`, `runtime/ledger_emitter.py`, Agency provenance/compiler integration | Dev A |
| Canonical documents, gate execution, milestone closure | Leadership |

## Decision 3 — Activation receipt

On Linux with AF_UNIX support at the ratified baseline, the complete
`test.falsifiers.test_rf38_rf45_plugin_lifecycle` module passed 13/13 on 2026-08-25, including
`test_echo_plugin_wire_lifecycle` and `test_child_crash_containment`. This is the Phase-0 local
qualification receipt. CI MUST repeat the same suite before either M-4 package merges; a failure is
a blocking lifecycle defect and does not authorize weakened semantics.

This receipt is sufficient to begin both development lanes. It is not evidence that M-4 is closed.

## Decision 4 — Milestone sequencing

The delivery sequence is:

```text
M-4 -> M-5a -> {M-5b || M-6} -> M-6.5 -> M-7 -> M-8 -> M-9
```

M-5b and M-6 may proceed independently after M-5a because both depend on the same frozen
post-M-5a substrate and neither depends on the other's output. This decision supersedes only the
older sequencing statement that placed all of M-6 behind M-5b; ADR-0090's delegation contracts,
event ownership, and pre-activation refusal remain accepted.

## Decision 5 — Immutable baseline identity

The historical `M-5-BASE` tag already exists at commit
`1a7dcba8e1a453740fca924270322707a735729a` and MUST NOT be moved, deleted, or overwritten.
The reviewed post-M-5a control baseline will be created once as:

```text
M-5A-BASE-v2
```

RF-86 and all post-M-5a comparison tooling MUST name that tag explicitly. ADR-0098 will bind its
commit, reducer version, event-envelope version, schema pins, and creation receipt.

## Decision 6 — Closed owner-decision register

The open decisions identified by the review are resolved as follows.

### OD-1 — M-5a semantic roster

ADR-0098 will allocate exactly `GoalDeclared`, `PlanRevised`, `StrategyChanged`,
`ProgressAssessed`, and `ContextCompacted`, subject to the standard writer/reducer/schema/vector
package. `GoalDeclared` carries `goalDigest` and optional `goalArtifact`, never raw goal text. No
additional kind enters the M-5a window without reopening ADR-0098 before implementation.

### OD-2 — Checkpoint defaults

The initial policy is per-lineage at 500 events or 25 turns, whichever occurs first. It is a Runtime
policy, not law, and may be tuned only from the frozen append/fold benchmark while preserving
checkpoint/cold-fold equivalence and digest/pin verification.

### OD-3 — Formal deterministic oracle

M-5b uses DIMACS CNF satisfiability with assignment witnesses. The independent evaluator parses the
CNF and verifies every clause against the submitted assignment deterministically; invalid,
incomplete, or out-of-domain assignments are negative fixtures. Solver choice remains an adapter
detail and the substrate receives no SAT semantics.

### OD-4 — Confidence and calibration

The M-6.5 protocol uses a vector, never a single truth value: exterior-verifier status, behavioral
progress, repeated-failure/stall signals, budget trajectory, ensemble disagreement when available,
and self-reported confidence as diagnostic-only. Calibration reports Brier score and reliability
bins where binary outcomes exist; unavailable signals are explicit. Promotion requires paired runs,
fixed tasks, the A/A floor, a primary outcome metric, and a declared regression budget.

### OD-5 — Concurrency disposition rule

No advanced scheduler is authorized now because M7-01 evidence does not yet exist. Independent
read-only effects may use the bounded safe-parallel path only after pairwise resource/sink
independence is proved. ADR-0099 MUST choose implement, simplify, or cancel from M7-01; below 30%
useful independence the default is cancel, and any implementation must demonstrate material
wall-time benefit after coordination, contention, recovery, and cache costs.

### OD-6 — M-8 lifecycle representation

M-8 uses typed `ClaimRecorded` payloads for candidate, evaluation, promotion, and rollback evidence,
plus existing composition activation/approval events for authoritative state transitions. The eight
deprecated lifecycle kinds remain deprecated; no event-roster expansion is presumed. ADR-0100 owns
the payload schemas, writer authority, independent promoter, rollback, and held-out gate.

### OD-7 — Multi-tenant isolation ownership

Normative ownership belongs to `SECURITY.md`; Runtime profiles realize tenant isolation and adapters
enforce it. The contract is due before M-9 and does not block M-4 through M-8. No pack or client may
invent independent tenant authority.

### OD-8 — Blob GC and legal hold

Artifact retention and legal hold are separate from execution retention. In M-8, legal hold always
dominates GC; deletion eligibility is derived from retention expiry, reachability, and hold state;
deletion receives a durable auditable receipt. Digests and causal facts remain even when authorized
content bytes expire. Store adapters implement collection behind a lifecycle policy/port; Kernel
semantics remain unchanged.

ADR-0098, ADR-0099, and ADR-0100 remain required implementation decisions at their named gates, but
they inherit these closed outcomes and may not reopen them without explicit counter-evidence.

## Consequences

Dev A and Dev B may start their M-4 packages immediately under the active sprint. RF-95 remains
NO-GO until both packages are merged, the integrated suite is green, capture is complete, and the
live task/verifier are frozen. M-5a and later implementation remain unauthorized until their named
entry decisions and technical gates are satisfied.
