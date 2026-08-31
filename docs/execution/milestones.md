---
id: execution.milestones
canonical_id: execution.milestones
class: execution
authority: execution
truth_plane: TARGET
status: living
implementation_status: PARTIAL
owner: repository-governance
canonical_for:
  - milestone outcomes and gates
purpose: Present stable TARGET milestone outcomes, dependencies, and acceptance predicates without claiming current completion.
audience:
  - contributor
  - release-owner
analysis_subject_sha: d639ec4bda5ea7d8836a182393498a31fc43ea1a
version: 0.9.2a2
last_verified: 2026-08-31
normative_authority:
  - docs/03_execution/milestones.md
  - docs/SPEC.md#milestone-compatibility
relationships:
  - execution.active
  - execution.backlog
  - spec.core
reviewer: delegated-tech-lead-block-e
confidence: high
---

# TARGET Milestone Gates

## Scope

This page owns stable outcomes and gate predicates. It does not own current package status and does not infer acceptance from source presence, tests, or implementation. Current work is routed to [execution.active](active.md).

| Milestone | TARGET outcome | Acceptance boundary | Execution Status |
|---|---|---|---|
| M-0–M-3C | Trust foundation and canonical composition | Historical completion anchors remain preserved; successor changes require explicit ADR and falsifier | `DONE` (Verified & Frozen) |
| M-4 | Useful real-model coding proof with durable causal evidence | Exact immutable RF-95 bundle plus valid acceptance; RF-85 remains optional assurance | `DONE` (RF-95 Base Tagged) |
| M-5a | Event-derived `AgentView` and accepted successor baseline | Replay evidence and verified `CONVERGENCE-BASE-v1` predicates | `DONE` (Base Reconciled) |
| M-5b | Independent domain-generality witness | RF-86/RF-98 against the uncontaminated successor baseline | `MECHANISM AS_BUILT` (Awaiting Handoff) |
| M-6 | Mediated recursive delegation | Depth-three cold reconstruction, attenuation, budget conservation, recovery, signed evidence | `MECHANISM AS_BUILT` (59 tests green) |
| M-6.5 | Measured adaptive strategy | Valid paired-study disposition; controller remains off unless profile-specific evidence authorizes it | `MECHANISM AS_BUILT` (Controller Off) |
| M-7 | Declarative multi-role topology through one runtime | Three real-effect topologies, persisted artifact flow, and explicit scheduler disposition | `MECHANISM AS_BUILT` (40 tests, 6 skips) |
| M-8 | Durable memory and governed learning MVP | Authorization, recovery, retention, held-out lift, separated promotion authority, and executed rollback receipts | `BLOCKED` (Awaiting empirical held-out lift >=0.05) |
| M-9 | Installable operational beta `0.9.0b1` | Qualified M-1–M-8 evidence, unified product surfaces, health, two workflows, restart/resume, offline-after-install | `UNAUTHORIZED` (Blocked on M-8) |
| M-10 | Final `0.9.0` release | Migration, backup/restore, fault/security/performance qualification, reproducible artifacts, soak, exact-subject signed envelope | `UNAUTHORIZED` (Blocked on M-9) |

## Gate semantics

- Mechanism presence is not integration, experiment, independent attestation, or accepted closure.
- Unknown, missing, failed, degraded, or `undeterminable` evidence never satisfies a predicate.
- Negative experiments may close only when the preregistered protocol remains valid.
- M-9 cannot be authorized before M-8 has an exact producer-verifiable bundle and independent acceptance over its digest.
- M-10 closes only when `./ci/release_qualify.sh` exits `0` for the exact candidate and emits a subject-matching signed envelope.

## Current-status caveat

This page publishes stable gates only. The exact current disposition is owned by
[execution.active](active.md), which records M-8 and later as unaccepted until
the required producer-verifiable and independent receipts exist.

## v0.9.2 capability-wave overlay

Vanguard v0.9.2 is an implementation and qualification overlay, not a replacement milestone
ladder. Its waves are routed through [execution.active](active.md) and contribute evidence to the
existing M-4–M-10 gates without silently closing them.

| Capability wave | Stable outcome | Required evidence | Status |
|---|---|---|---|
| W-092-0 | Canonical contracts and navigable implementation map | Cross-linked canonical owners; target/as-built labels; fresh navigation/index checks | `DONE` (Merged in Ancestry) |
| W-092-1 | Valid benchmark subjects and lossless trajectory/projection evidence | Untouched-fixture preflight, immutable trajectory links, reducer compatibility vectors | `DONE` (Merged in Ancestry) |
| W-092-2 | Coding completion admitted only by fresh applicable verification | Deterministic failure scenarios, local challenge receipts, exterior evaluator kept independent | `DONE` (AdmissionGate Green) |
| W-092-3 | Bounded provider-neutral repository context and durable coding state | Control/treatment trajectories with task, index, context and prompt identities | `DONE` (L1-L5 Radix Integrated) |
| W-092-4 | Tool, patch, recovery, resume, and provider reliability | Patch corpus, injected-failure study, cold-restart parity and provider contract tests | `DONE` (ProtocolRecoveryPolicy Green) |
| W-092-5 | Evidence-qualified release disposition | Exact-subject checks, controlled real-model evidence and explicit SWE claim boundary | `ACTIVE` (Blocked on Empirical Canary) |

No capability wave may close a milestone merely by passing its own component tests. Evidence MUST
be evaluated under the milestone acceptance boundary to which it is offered.

## Post-M-10 1.0 qualification horizon

M-9 and M-10 keep their existing beta and `0.9.0` meanings. The following
outcomes define a non-authorizing 1.0 horizon; they do not create new active
milestones or permit work that M-8/M-9/M-10 currently block.

| Horizon outcome | Acceptance boundary |
|---|---|
| Stable agent framework | Public manifest, port, application-service, event, artifact, resume, and compatibility contracts are documented and tested; a first-party app does not own a second runtime |
| Useful Coding Max product | Repository-scale bugfix, multi-file, migration, and greenfield tasks produce real patches and fresh verification through mediated effects with exact cost/latency/token evidence |
| Reference-agent proof | Coding Max and at least two non-coding supported agents install and run through the same composition contract with domain-specific policies outside the kernel |
| Operational 1.0 candidate | Upgrade/migration, backup/restore, restart/resume, offline-after-install, fault, security, performance, soak, and reproducible-build gates pass on the exact candidate |
| Honest capability claim | Any SOTA or SWE-bench claim names the official/reproducible protocol, exact model and subject, missingness, cost, evaluator, and harness-vs-model ablation |

Coding Max is delivered using the **thin app, thick declarative composition**
boundary recorded in [active.md](active.md) and [backlog.md](backlog.md). A new
kernel primitive, runtime, store, tool broker, or evaluator is a failed horizon
gate unless independently justified as a general framework contract through the
normal decision and falsifier process.

## SWE-P0–SWE-P5 parallel program

The SWE program is evidence work, not a milestone shortcut. It does not authorize
or close M-9 or M-10.

| Program | Outcome | Required gate |
|---|---|---|
| SWE-P0 | Instrument-valid harness | Isolated materialization, trajectory linkage, evaluator validity, secret boundary |
| SWE-P1 | Honest baseline | Preregistered corpus/model/cost policy and explicit missingness |
| SWE-P2 | Harness experiments | Controlled context/tool/recovery experiments with attributable receipts |
| SWE-P3 | Model/harness optimization | Predeclared optimization and held-out comparison without contamination |
| SWE-P4 | Controlled larger run | Budgeted larger sample, independent audit, reproducible subject identity |
| SWE-P5 | Official evaluation | Official benchmark procedure and receipt; local runs are never official |

Only SWE-P5 may support an official SWE-bench claim, and only for its evaluated
subject and protocol. A local canary or green test suite is never an official
SWE-bench result.
