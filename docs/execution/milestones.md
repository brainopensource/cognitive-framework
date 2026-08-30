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
analysis_subject_sha: c14be3c9d3b2ba9b7bacefec235eddab1bf1e304
version: 0.9.2a1
last_verified: 2026-08-30
normative_authority:
  - docs/03_execution/milestones.md
  - docs/SPEC.md#milestone-compatibility
relationships:
  - execution.active
  - spec.core
reviewer: delegated-tech-lead-block-e
confidence: high
---

# TARGET Milestone Gates

## Scope

This page owns stable outcomes and gate predicates. It does not own current package status and does not infer acceptance from source presence, tests, or implementation. Current work is routed to [execution.active](active.md).

| Milestone | TARGET outcome | Acceptance boundary |
|---|---|---|
| M-0–M-3C | Trust foundation and canonical composition | Historical completion anchors remain preserved; successor changes require explicit ADR and falsifier |
| M-4 | Useful real-model coding proof with durable causal evidence | Exact immutable RF-95 bundle plus valid acceptance; RF-85 remains optional assurance |
| M-5a | Event-derived `AgentView` and accepted successor baseline | Replay evidence and verified `CONVERGENCE-BASE-v1` predicates |
| M-5b | Independent domain-generality witness | RF-86/RF-98 against the uncontaminated successor baseline |
| M-6 | Mediated recursive delegation | Depth-three cold reconstruction, attenuation, budget conservation, recovery, signed evidence |
| M-6.5 | Measured adaptive strategy | Valid paired-study disposition; controller remains off unless profile-specific evidence authorizes it |
| M-7 | Declarative multi-role topology through one runtime | Three real-effect topologies, persisted artifact flow, and explicit scheduler disposition |
| M-8 | Durable memory and governed learning MVP | Authorization, recovery, retention, held-out lift, separated promotion authority, and executed rollback receipts |
| M-9 | Installable operational beta `0.9.0b1` | Qualified M-1–M-8 evidence, unified product surfaces, health, two workflows, restart/resume, offline-after-install |
| M-10 | Final `0.9.0` release | Migration, backup/restore, fault/security/performance qualification, reproducible artifacts, soak, exact-subject signed envelope |

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

| Capability wave | Stable outcome | Required evidence |
|---|---|---|
| W-092-0 | Canonical context, completion, verification, recovery, patch, and trajectory contracts | Cross-linked canonical owners; target/as-built labels; fresh navigation/index checks |
| W-092-1 | Valid benchmark subjects and lossless trajectory/projection evidence | Untouched-fixture preflight, immutable trajectory links, reducer compatibility vectors |
| W-092-2 | Coding completion admitted only by fresh applicable verification | Deterministic failure scenarios, local challenge receipts, exterior evaluator kept independent |
| W-092-3 | Bounded provider-neutral repository context and durable coding state | Control/treatment trajectories with task, index, context and prompt identities |
| W-092-4 | Reliable observation, patching, typed recovery and semantic resume | Patch corpus, injected-failure study, cold-restart parity and provider contract tests |
| W-092-5 | Evidence-qualified release disposition | Exact-subject checks, controlled real-model evidence and explicit SWE claim boundary |

No capability wave may close a milestone merely by passing its own component tests. Evidence MUST
be evaluated under the milestone acceptance boundary to which it is offered.

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
