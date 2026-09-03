---
id: arch.assurance.evaluation
canonical_id: arch.assurance.evaluation
class: architecture
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: assurance-evaluation
canonical_for:
  - evaluation authority boundary
  - trajectory/evidence flow
  - assurance profile relationship
  - absence/failure semantics
purpose: Explain the external evaluation authority boundary, signed verdict flow, trajectory capture, and fail-closed absence semantics.
audience:
  - developer
  - architect
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-09-03
evidence:
  - E-B-013
  - E-B-031
  - E-B-040
  - E-B-041
  - E-B-051
relationships:
  - arch.system.overview
  - arch.trust.kernel
  - ref.events
  - ref.configuration
reviewer: documentation-specialist
confidence: high
---

# Evaluation, Evidence & Assurance Architecture

## Purpose
This document is the canonical architecture owner for the exterior evaluation authority boundary, trajectory capture (`mhf.trajectory/2`), cryptographic signed verdict flows (`VerdictRecorded`), assurance level classifications, and fail-closed missingness semantics (`INV-B-009`).

## Scope
- The strict architectural separation between episode execution and evaluation authority.
- The `EvaluatorGateway` client and standalone evaluator daemon (`vanguard-evaluator`, UID 10002).
- Trajectory evidence collection and hashing (`trajectory.py`).
- Assurance levels: `recorded` (product default) vs `hermetic` (cryptographically attested).
- Fail-closed handling of evaluator offline states and missing evaluation proofs.

## Non-responsibilities
- Exact JSON Schema fields for verdict and trajectory schemas (owned by [`ref.schemas`](../reference/schemas.md)).
- Profile configuration parameters (owned by [`ref.configuration`](../reference/configuration.md)).
- Kernel lease management (owned by [`arch.trust.kernel`](kernel.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Standalone exterior evaluation RPC daemon, cryptographic verdict signing, and trajectory capture are fully implemented in `vanguard.packages.runtime` and `vanguard.packages.adapters.evaluators`.

---

## 1. The Evaluation Authority Boundary (`INV-B-009`)

In Vanguard, an agent or episode cannot grade its own performance or mint evaluation verdicts.

```text
┌─────────────────────────────────────────────────────────────┐
│                 EPISODE EXECUTION DOMAIN                    │
│   EpisodeEngine executes turns, captures trajectory facts.  │
│   Terminates with EpisodeCompleted. Zero grading authority.│
└──────────────────────────────┬──────────────────────────────┘
                               │
                      Trajectory Digest Handoff
                               │
┌──────────────────────────────▼──────────────────────────────┐
│             EXTERIOR EVALUATION AUTHORITY (UID 10002)       │
│   EvaluatorDaemonClient -> vanguard-evaluator RPC Daemon    │
│   Executes objective test suites / rubrics in clean sandbox.│
│   Signs result using Evaluator Ed25519 Private Key.         │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    RUN LEDGER / EVENT STORE                 │
│   EvaluatorGateway (sole writer of VerdictRecorded) appends │
│   SignedVerdict containing score, rubric, signature.        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Trajectory Capture & Evidence Flow (`mhf.trajectory/2`)

Upon episode conclusion, `EvidenceCaptureService` compiles an immutable `Trajectory` payload:
- **Captured Fields**: Initial brief, ordered list of turn proposals, observations, effect receipts, tool inputs/outputs, and final artifacts.
- **Hash-Binding**: Computes `trajectory_digest = SHA256(JCS(trajectory_dict))`.
- **Storage**: The complete trajectory is stored in the blob store (`ref.artifacts`), and its digest is passed to the evaluation daemon.

---

## 3. Signed Verdict Flow & Cryptographic Proofs

1. `EvaluatorGateway` sends an evaluation request containing the `trajectory_digest` to `vanguard-evaluator`.
2. The evaluator daemon executes objective assertions, linters, and verification suites inside an isolated evaluator sandbox.
3. The daemon constructs a `SignedVerdict` (`schemas/mhf/verdict_v2.schema.json`):
   - `verdict_id`, `trajectory_digest`, `run_id`, `score` ($0.0 \dots 1.0$), `status` (`PASSED` | `FAILED`), `rubric_id`.
   - `evaluator_signature`: Ed25519 signature computed over `JCS(verdict_payload)`.
4. `EvaluatorGateway` receives the verdict and appends a `VerdictRecorded` event to the run ledger (`INV-B-007`).

---

## 4. Assurance Levels & Execution Profiles

| Assurance Level | Evaluation Mode | Attestation Required | Promotion Eligible | Description |
|---|---|---|---|---|
| **`recorded`** | `none` (default) | `false` | `false` | Standard developer and interactive runs. Captures event trajectory without requiring external scoring. |
| **`hermetic`** | `exterior` | `true` | `true` | Formal benchmark or promotion candidate runs. Requires valid signed verdict from qualified evaluator. |

---

## 5. Failure & Missingness Semantics

- **Fail-Closed Evaluator Absence**: If an execution profile specifies `evaluation_mode: "exterior"` and the evaluator daemon is offline or returns an invalid signature, the run fails immediately with `EvaluatorUnavailable`. It never silently degrades to `recorded` (`RF-88`).
- **Explicit Absence Reason**: If `evaluation_mode: "none"` is configured, the execution profile requires an explicit `evaluation_absence_reason` string (e.g. `"local product run: exterior assurance is optional"`).

---

## Implementation Evidence

- **Evidence Capture**: `vanguard/packages/runtime/evidence_capture.py`.
- **Trajectory Representation**: `vanguard/packages/runtime/trajectory.py`.
- **Evaluator Gateway**: `vanguard/packages/runtime/evaluator_gateway.py`.
- **Evaluator Daemon & Client**: `vanguard/packages/adapters/evaluators/daemon.py`, `client.py` (`EvaluatorClient`).
- **Assurance Tests**: `test/contracts/test_trajectory_v2.py`, `test/adapters/test_evaluator_daemon.py`, `test/runtime/test_evaluation_service.py`.
