# Sprint 6B Lane A — Senior Control Plane, Client and Release Packet

**Assignee:** Senior Developer A — Principal Runtime Architect  
**Delegated authority:** Tech Lead and Project Lead for control-plane implementation and day-to-day integration decisions  
**Accountable outcome:** one durable, authenticated and recoverable operator path from installed `vg` to trusted adapters  
**Primary review partner:** Lane B Senior  
**Complexity:** Level 5/5 — release critical

## 1. Mission

Build the generic framework control plane and make it the only production entry path. Lane A owns the RuntimeService, durable lifecycle, external approval verification, ledger-only recovery, live CLI transport, governance evidence machinery and final candidate assembly. Coding-specific behavior remains in harness/adapters owned by Lane B.

The lane is complete only when `vg` controls a durable runtime through a versioned public protocol, every privileged transition is externally authorized and reconstructable, and no scenario, in-memory, direct-host, runtime-signer or direct-evaluator fallback exists in production composition.

## 2. Read before editing

Read completely, in order:

1. [Sprint 6 SA packet](../sprint6/sa-packet.md) — preserve its composition-root objective, but replace its direct adapter wiring and old dogfood assumptions with this packet.
2. [Sprint 6B closure review](sprint_6B_review_overview_and_next_tasks.md).
3. [Sprint 6B backlog](backlog.md), especially §§2–7, §§9–10 and §§13–17.
4. [Sprint 6B close guidelines](../../development_guides/guidelines_sprint_6B_close.md).
5. [System architecture ICD](../sprint0/system-architecture-icd.md).
6. [Architecture and execution model](../../main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md).
7. [Core contracts and wire schema](../../main_v4/04_vanguard_core_contracts_and_wire_schema_v040.md).
8. [Kernel and security](../../main_v4/05_vanguard_kernel_capabilities_and_security_v040.md).
9. [Decision register](../../main_v4/09_vanguard_decision_register_v040.md), especially ADR-0057/0058.
10. [Active MVP Contract](../sprint0/active-mvp-contract.json).

Inspect runtime, governance, ledger, CLI, schemas, contract tools and their tests before changing them. Do not assume current prose receipts prove behavior.

## 3. Owned backlog

Lane A is the delivery owner for:

- `ADR-FREEZE` and shared protocol coordination with Lane B;
- `GOV-CANDIDATE`, `S6B-GOV-003`, `S6B-EVID-001`, `S6B-GOV-005`;
- `S6B-SA-001` through `S6B-SA-009`;
- former Lane C work `S6B-JR-001` through `S6B-JR-007`;
- approval-side and service-side portions of `SECURITY-R0` and `S6B-SEC-002`;
- `S6B-REL-001`, CLI packaging, deployment orchestration and candidate assembly;
- `S6B-QA-002/003/004/006/007` for control/client/release surfaces;
- integration ownership for R1, R2, R5, R6 and R10;
- coordination of Sprint 1 human/schema/hosted residuals with the repository owner.

Lane A does not implement provider transports, worker internals, containment policy, evaluator internals or image contents. Those belong to Lane B behind frozen ports.

## 4. Normal write scope

- `schemas/v4/**` for jointly accepted Sprint 6B public schemas/vectors;
- `vanguard/packages/runtime/**`;
- runtime/governance/recovery/event-store integration tests;
- `vanguard/clients/cli/**`;
- contract/receipt/release tools and narrowly relevant CI workflows;
- Python/TypeScript protocol generation or conformance tooling;
- distribution metadata and supervisor/orchestration files not owned by Lane B images;
- Sprint 6B evidence for gates Lane A did not author, or unsigned candidate material awaiting review.

Do not edit Lane B adapter implementations to resolve an integration problem. Report the failing frozen contract and agree the change first.

## 5. Decision rights

Lane A may decide without escalation when the choice:

- stays inside an accepted ADR and frozen scope;
- changes only control-plane internals, not public/durable schemas;
- preserves failure semantics, trust boundaries and compatibility;
- is covered by reference and broken-counterpart tests.

Lane A must obtain Lane B approval before changing any shared schema, port, event meaning, model/worker/evaluator request, artifact compatibility or trust boundary. Record the decision, migration impact and new must-fail test.

Lane A must stop and obtain separate repository-owner authorization before credential rotation, history rewriting, remote ref changes, branch-protection changes, tag creation, registry publication or external deployment.

## 6. Implementation sequence

### A0 — Freeze public contracts

Define versioned schemas and valid/invalid golden vectors for:

- RuntimeService commands, receipts, errors and event stream frames;
- command IDs, idempotency keys, run IDs, cursors and causal/sequence fields;
- approval challenge/decision/revocation records;
- worker and evaluator references imported from Lane B's proposed ports;
- compatibility/version negotiation and extension policy.

Python and TypeScript must consume the same vectors. Reject unsupported versions and invalid fields before domain construction.

### A1 — Durable RuntimeService

Implement a bounded authenticated Unix service with:

- `StartRun`, `GetRun`, `StreamEvents`, `ResolveApproval`, `RecordCorrection`, `Cancel`, `Checkpoint`, `Resume`, `ExplainArtifact`;
- durable SQLite command inbox, event outbox, projections and service metadata;
- idempotent command handling and stable error codes;
- per-stream durable sequence allocation and causal parent links;
- cursor reconnect, deduplication, gap detection, bounded buffering and backpressure;
- readiness, graceful shutdown, state permissions and restart behavior.

Transport handlers validate and enqueue commands; they do not own business state.

### A2 — One event-sourced lifecycle

Unify process, approval and run transitions into one reducer/state machine. Enforce:

```text
command accepted
  → proposal persisted
  → authorization/grant persisted
  → approval challenge persisted before suspension
  → external decision persisted before re-dispatch
  → effect intent persisted before execution
  → receipt/reconciliation persisted after execution
  → one terminal event
  → evaluator request triggered from terminal evidence
```

Illegal transitions fail. Recovery reads only durable events and never depends on an in-memory callback, previous model object or replacement reservation.

### A3 — External asymmetric approval

Replace shared HMAC authority with signer/verifier separation. The CLI or external key agent holds the Ed25519 private key. Runtime stores public keys/key IDs and revocation state only. Canonical signed bytes bind schema, key, challenge/approval, actor/reviewer, run/process, action/resource, exact normalized diff/args/descriptor, policy, reservation, challenge event, decision, nonce and expiry.

The CLI renders the exact normalized bytes, signs outside runtime and submits the decision. Non-TTY execution never auto-approves.

### A4 — Live CLI and stable operator semantics

Production `vg` always uses RuntimeService. Remove implicit non-TTY feed mode, fabricated IDs/status, implicit scenario selection and success without a terminal event. Replay/demo require explicit flags, are visibly labelled and cannot mutate live state.

Every command sets `process.exitCode` or exits with the documented result:

- `0`: confirmed successful terminal result;
- `1`: confirmed task rejection/cancellation/unsatisfied result;
- `2`: usage, protocol, instrument, unavailable peer, early EOF or uncertain result.

Keep stdout JSONL-only in headless mode and diagnostics on stderr.

### A5 — Composition and adapter registries

Compose Lane B's adapters only through frozen ports and registries. Runtime framework code must not encode coding verbs; `vg-code-default` provides tool/policy/evaluator references. Unknown capability, missing sandbox/evaluator, invalid manifest, missing durable store or incompatible protocol fails at composition. No direct concrete evaluator import or direct Git/subprocess effect is allowed in the product root.

### A6 — Candidate governance and release assembly

Make candidate tests execute applicable open/covered requirements. Zero commands cannot print PASS. Validate structured receipts against candidate SHA, output/artifact digests, signer and countersigner. Build clean-candidate automation, compatibility manifest, release dry run, upgrade/rollback orchestration and documentation verification.

Do not mark rows covered or reseal the baseline until R0–R9 are valid at the frozen candidate.

## 7. Required acceptance and adversarial tests

Lane A must prove:

- Python/TypeScript golden round trips and unsupported-version rejection;
- malformed/oversized frames rejected before domain construction;
- duplicate command idempotency and concurrent writer sequence uniqueness;
- cursor reconnect, deduplication, gap rejection and bounded buffers;
- one terminal transition and no illegal lifecycle transition;
- signature mutation, transplant, replay, expiry, wrong actor/run/resource and revoked key rejection;
- kill before/after challenge, decision, grant, intent, effect and receipt;
- exactly-once continuation with no repeated committed effect/model call;
- cancel/revoke while active and suspended;
- unavailable daemon, early EOF and missing terminal event return exit 2;
- replay/scenario cannot execute mutable live commands;
- composition contains no fake, host-effect, default/in-memory signer/store or direct evaluator fallback;
- candidate mode cannot pass with zero commands, stale receipts or self-signoff.

## 8. Lane handoff contract

Before Lane B integrates, Lane A supplies:

- frozen schemas and golden vectors;
- generated/conformant Python and TypeScript boundary types;
- service fake/server harness that implements the public contract without production shortcuts;
- explicit adapter registry interfaces for ModelPort, worker and evaluator clients;
- lifecycle event requirements Lane B receipts/verdicts must satisfy;
- compatibility version and integration test commands.

For every handoff, report ticket IDs, exact files, decision record, compatibility impact, commands/results, broken counterpart, migration/rollback impact and unresolved risks.

## 9. Verification commands

Run narrow tests continuously, then at lane gates:

```bash
python3 -m unittest discover -s test/contracts
python3 -m unittest discover -s test/runtime
python3 -m unittest discover -s test/kernel
python3 -m unittest discover -s test/trust
npm --workspace @vanguard/cli run typecheck
npm --workspace @vanguard/cli test
python3 tools/check_boundaries.py
python3 tools/check_tcb_budget.py
python3 tools/run_broken_tests.py
```

At candidate integration, run the complete command sequence in the Sprint 6B close guidelines. Report skips and pre-existing failures honestly.

## 10. Stop rules

Stop if implementation would introduce a second product lifecycle, runtime signing secret, direct host effect, in-memory production authority, CLI business state, direct evaluator implementation or fake fallback. Stop integration on an unreviewed shared-interface change. Stop release if any mandatory candidate command executes zero tests, any receipt is stale/self-signed, or any required adapter is unavailable.

