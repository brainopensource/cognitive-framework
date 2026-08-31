---
id: report.electroweak.solution-a.full-code-forge-wave-3
class: report
authority: non-canonical
canonical_for: []
status: proposal
owner: repository-governance
version: 0.9.2a2
last_verified: 2026-08-31
---

# AETHER FORGE — Full Code Manifest — Wave 3

## Delivery contract

- Branch: `feat/beta-release_electroweak-v091`
- Exact reconciled subject: `f242ced297216109736975376802f1e3dc4e29ce`
- Scope: backend only; no frontend changes.
- Focus: Tests, falsifiers, performance, observability, data model, module boundaries, PR decomposition, P0–P3 backlog, risks, benchmark protocol, and first implementation cut.
- Architectural rule: specialize existing Vanguard seams; do not fork the kernel.
- Status: implementation manifest; code blocks are the exact classes, functions, schemas, and manifests to add or replace.

## Code-first reconciliation

The inspected branch already contains `AdmissionGate`, workspace-bound `VerificationReceipt`, `MetaController`, guarded deterministic consultation, ledger-derived progress, structured compaction, model routing, attenuated child execution, durable events, and artifact capture. FORGE must compose these mechanisms. Any passage below that appears to create a second engine is interpreted as an exterior FORGE policy, adapter, preset, or runtime lowering layer. No new code belongs in `vanguard/packages/kernel/`.

## Authoritative file routing

| Concern | Existing owner | FORGE change surface |
|---|---|---|
| Completion admission | `agency/episode/admission_gate.py` | compose `GoalContract`; preserve base gate |
| Reflex decisions | `ports/meta_controller.py`, `runtime/meta_controller.py` | deterministic rules and state builder |
| Context | `agency/context/` | `forge-distill` strategy; preserve evidence |
| Tools | existing effect dispatch | declarative ToolScript port and lowering |
| Forks | `EpisodeEngine.spawn`, child runtime | budget-attenuated branch policy |
| Verification | receipts/evaluator gateway | current-workspace binding and goal evidence |
| Models | adapter routing policy | bounded escalation policy |
| Memory | artifact/experience seams | evidence-gated strategy capsules |

## Implementation specification and complete changed units


# 131. Edit Guide — Step-by-Step

A senior developer implementing this should follow:

```text
1. Checkout target branch and record exact HEAD.
2. Run focused existing runtime/agency tests.
3. Inspect local signatures before writing FORGE code.
4. Create vg-code-forge manifest using only existing capabilities.
5. Prove baseline execution.
6. Add ForgeAdmissionGate.
7. Add ForgeMetaController.
8. Add fork lowering to existing spawn seam.
9. Add ForgeCompactionStrategy.
10. Re-run focused tests.
11. Add ToolScript ports/runtime/adapter.
12. Add ToolScript falsifiers.
13. Add branch distillation.
14. Add optional LDA adapter.
15. Add StrategyCapsules only after core FORGE works.
16. Run real coding smoke tasks.
17. Compare against baseline harness.
18. Keep only mechanisms that materially improve capability.
```

---

# 132. Before Editing Any Existing Method

For each target:

```text
find all call sites
find tests
find protocol/interface
find manifests depending on behavior
find projection/event assumptions
```

Then write a one-line change reason.

Example:

```text
HarnessSession._lower_controller_directive
Reason:
lower existing `fork` directive into the already-supported `agent.spawn`
without creating a second branching mechanism.
```

This prevents accidental architectural duplication.

---

# 133. Required Code Review Questions

Every FORGE PR should answer:

```text
Did this bypass an existing AETHER abstraction?
Could this be a manifest/plugin/policy instead of runtime code?
Did this add authority?
Did this change budget conservation?
Did this duplicate event state?
Can it be disabled?
Can a simple task avoid paying its cost?
Can the run be reconstructed after crash?
Is success backed by environment evidence?
```

---

# 134. PR Decomposition

Recommended implementation PRs:

```text
PR-FORGE-01
native preset + goal contract + stop gate

PR-FORGE-02
reflex controller + fork lowering

PR-FORGE-03
forge compaction + artifact-backed admission

PR-FORGE-04
ToolScript port/runtime/sandbox

PR-FORGE-05
branch distillation + adaptive fork policy

PR-FORGE-06
candidate patch isolation

PR-FORGE-07
optional LDA adapter

PR-FORGE-08
strategy capsules

PR-FORGE-09
LAM experiment fixtures + comparative report
```

Each PR should remain independently reviewable.

---

# 135. Backlog — P0

## FORGE-P0-001 — Reconcile current seams

**Goal:** confirm exact local implementation.

**Inspect:**

```text
EpisodeEngine
HarnessSession
AdmissionGate
MetaController
SpawnAdapter
ContextCompiler
compaction registry
model routing
manifest schemas
```

**Exit:** one mapping document or commit note.

---

## FORGE-P0-002 — Create `vg-code-forge`

**Goal:** native preset with minimal reactive prompt.

**No new runtime code initially.**

**Exit:** manifest validates and executes through current runtime.

---

## FORGE-P0-003 — Stop Gate

**Goal:** prevent textual/self-reported success.

**Exit:** unverified write task cannot complete.

---

## FORGE-P0-004 — Reflex Controller

**Goal:** detect pathological loops.

**Exit:** repeated failure produces strategy directive.

---

## FORGE-P0-005 — Fork Lowering

**Goal:** use existing `agent.spawn`.

**Exit:** FORGE can create one bounded research child.

---

# 136. Backlog — P1

## FORGE-P1-001 — `forge-distill`

**Goal:** compact long coding trajectories.

**Exit:** objective/patch/test/dead-end state survives compaction.

---

## FORGE-P1-002 — Artifact-backed Tool Results

**Goal:** prevent context flooding.

**Exit:** large test output enters context as summary + artifact ref.

---

## FORGE-P1-003 — ToolScript Port

**Goal:** stable contract for mediated programmatic tool execution.

---

## FORGE-P1-004 — ToolScript Sandbox

**Goal:** execute bounded Python without authority bypass.

---

## FORGE-P1-005 — ToolScript Broker

**Goal:** inner tool calls use standard AETHER dispatch.

---

## FORGE-P1-006 — ToolScript Falsifiers

**Goal:** prove capability and sandbox boundaries.

---

# 137. Backlog — P2

## FORGE-P2-001 — BranchSummary

## FORGE-P2-002 — TrajectoryDistiller

## FORGE-P2-003 — Adaptive ForkPolicy

## FORGE-P2-004 — BranchSelector

## FORGE-P2-005 — Candidate Patch Worktree Isolation

## FORGE-P2-006 — Alternate Model Route for Forks

---

# 138. Backlog — P3

## FORGE-P3-001 — LDA adapter

## FORGE-P3-002 — LDA provenance

## FORGE-P3-003 — ToolScript + LDA integration

## FORGE-P3-004 — StrategyCapsule schema

## FORGE-P3-005 — TaskCapsuleRegistry

## FORGE-P3-006 — Capsule promotion evidence pipeline integration

---

# 139. Risk Register

| Risk | Impact | Mitigation |
|---|---:|---|
| ToolScript bypasses authority | Critical | RPC-only privileged effects |
| Fork explosion | High | hard count/budget limits |
| Context distillation loses key fact | High | artifact refs + dereference |
| Writable branches collide | High | isolated worktrees |
| Capsule becomes arbitrary code injection | Critical | pure/advisory MVP |
| LDA stale index | High | repo/tree digest provenance |
| Stop Gate becomes over-restrictive | Medium | task-specific GoalContract |
| Reflex controller fights model | Medium | sparse deterministic triggers |
| Branches increase cost without gain | Medium | opportunistic fork policy |
| Complex runtime diffuses core | High | strict module boundaries |
| Benchmark overfitting | Medium | varied internal tasks + external checks |

---

# 140. Security Review Checklist

Before enabling ToolScript by default:

```text
[ ] no unrestricted subprocess from script
[ ] no inherited environment secrets
[ ] no unrestricted sockets
[ ] no host filesystem escape
[ ] all privileged calls mediated
[ ] all mediated calls capability checked
[ ] time limit enforced
[ ] memory limit enforced
[ ] tool-call limit enforced
[ ] output limit enforced
[ ] process terminated on session cancellation
[ ] causal parent id recorded
[ ] artifact digests recorded
```

---

# 141. Performance Review Checklist

```text
[ ] ToolScript startup cost measured
[ ] ToolScript saves model turns on representative task
[ ] branch summaries bounded
[ ] no duplicate repository scan
[ ] compaction avoids re-summarizing immutable artifacts
[ ] LDA used only when beneficial
[ ] simple task path remains small
[ ] no mandatory branch
[ ] no mandatory second model
```

---

# 142. Benchmark Philosophy

FORGE development should not block on exhaustive benchmark campaigns.

Use:

```text
Stage A
5–10 targeted tasks exposing current failures

Stage B
small LAM/internal corpus

Stage C
representative external coding tasks

Stage D
larger SWE-style evaluation only after harness is competent
```

The goal of early testing is:

```text
does the mechanism make the agent actually work better?
```

not:

```text
produce a publication-grade confidence interval.
```

---

# 143. Minimal Comparative Report

For every major FORGE mechanism record:

```text
baseline result
FORGE result
task success
turns
tool calls
token usage
verification
observed failure mode
qualitative trajectory difference
```

Example:

```text
Task: complex-cache-17

Baseline:
FAILED
17 turns
wrong file localization
no real patch

FORGE + ToolScript:
PASS
11 turns
24 inner tool operations
1 patch
target tests PASS

Interpretation:
programmatic repository triage materially improved localization.
```

---

# 144. What Constitutes Evidence of Improvement

Strong evidence:

```text
previously failing real task now passes
fewer repeated failures
correct repository localization
real tests move from fail to pass
lower turns for same success
successful recovery after first bad patch
```

Weak evidence:

```text
model says reasoning felt clearer
longer plan
more agents participated
more logs produced
larger context
```

---

# 145. First Real Tasks to Use

Select tasks that exercise distinct mechanics.

```text
Task A
small obvious bug
tests Fast Path

Task B
large output / repository search problem
tests ToolScript

Task C
competing hypotheses
tests fork

Task D
first patch wrong
tests reflex recovery

Task E
long task crossing context pressure
tests compaction

Task F
large indexed repo
tests optional LDA
```

Do not begin with a giant benchmark sweep.

---

# 146. Failure Analysis Protocol

After each failed real task:

```text
1. inspect final verification
2. locate first irreversible wrong assumption
3. inspect context at that point
4. inspect available but unused tools
5. inspect repeated effects
6. inspect whether a fork would have helped
7. inspect whether ToolScript could compress mechanical work
8. inspect whether Stop Gate rejected correctly
9. classify missing harness capability
10. change smallest outer-layer mechanism
```

Do not immediately modify the kernel.

---

# 147. FORGE Engineering Loop

Canonical development loop:

```text
real task
→ trajectory
→ identify first meaningful failure
→ smallest harness change
→ rerun
→ compare
→ keep/revert
```

The purpose is to converge toward a better harness while keeping architecture simple.

---

# 148. Meta-Harness Compatibility

FORGE should expose configuration so future experiment tooling can mutate:

```text
ToolScript enabled
ToolScript budget
fork threshold
fork count
branch model
compaction strategy
LDA mode
reflex thresholds
stop contract strictness
capsule enablement
```

Do not implement automated mutation in FORGE itself.

A meta-harness can operate above it later.

---

# 149. Potential Future Extension — Trajectory Search

If adaptive branching proves valuable, FORGE can later support:

```text
best-first branch expansion
beam search over hypotheses
candidate patch ranking
trajectory reuse
```

But do not implement MCTS/beam infrastructure in v0.x.

First prove:

```text
one useful branch beats one stuck trajectory
```

---

# 150. Potential Future Extension — Trajectory Memory

Successful branch summaries could later form retrieval memory:

```text
task pattern
failure pattern
useful strategy
evidence
```

Example:

```text
"pytest fixture scope regression"
→ inspect conftest hierarchy
→ compare fixture overrides
```

This should remain evidence-backed and provenance-aware.

---

# 151. Potential Future Extension — Learned Reflex Policy

Once enough trajectories exist:

```text
state features
→ learned policy
→ directive probability
```

Potential targets:

```text
fork now?
compact now?
request more context?
switch model?
stop?
```

Not for v0.x.

Start deterministic.

---

# 152. Potential Future Extension — Compiled ToolScript Templates

Repeated successful ToolScripts can become reusable templates:

```text
repo localization
failure clustering
API impact analysis
test selection
dependency traversal
```

They remain tools/skills, not kernel code.

---

# 153. Anti-Patterns

Reject the following implementations.

## Anti-pattern A — FORGE as another workflow engine

```text
ForgeEngine
ForgeScheduler
ForgeRuntime
ForgeLedger
```

No.

Use AETHER.

## Anti-pattern B — unrestricted Python REPL

No direct model-generated host code.

## Anti-pattern C — mandatory swarm

Most tasks should not spawn agents.

## Anti-pattern D — full transcript merging

Child summaries only.

## Anti-pattern E — giant static system prompt

Keep the model-facing contract compact.

## Anti-pattern F — LDA mandatory for every task

Use on demand.

## Anti-pattern G — review agent after every patch

Environment verification first.

## Anti-pattern H — model confidence as stop signal

Evidence first.

---

# 154. Definition of Done — Architecture

Architecture is complete when:

```text
FORGE is expressed as an AETHER composition
kernel remains domain-blind
authority remains conserved
events/artifacts remain authoritative
simple tasks retain low overhead
advanced compute remains optional
```

---

# 155. Definition of Done — Product Capability

FORGE is practically useful when a frontier model can:

```text
open an unfamiliar repo
find relevant code
write/edit real files
run real tests
process large tool outputs efficiently
recover from a wrong attempt
spawn bounded independent investigation when needed
preserve state across long runs
refuse premature completion
finish with evidence
```

That is the actual blocker to solve before optimizing benchmark score.

---

# 156. Recommended First Implementation Cut

If only one implementation wave is allowed, build:

```text
1. vg-code-forge manifest
2. ForgeAdmissionGate
3. ForgeMetaController
4. forge-distill compaction
5. ToolScript MVP
6. one research fork path
```

Do **not** build first:

```text
candidate patch tournament
learned routing
MCTS
capsule promotion automation
large analytics platform
complex LDA preprocessing
```

This first cut already changes the harness qualitatively.

---

# 157. Recommended Initial Directory Shape

After reconciling with the real repository:

```text
vanguard/packages/
├── agency/
│   └── manifests/
│       └── vg-code-forge/
│           ├── manifest.json
│           ├── system-prompt.txt
│           ├── context-policy.json
│           ├── routing-policy.json
│           ├── approval-policy.json
│           ├── budget-policy.json
│           └── toolscript-tool.json
│
├── ports/
│   └── toolscript.py
│
├── runtime/
│   ├── forge_admission.py
│   ├── forge_controller.py
│   ├── forge_branch.py
│   ├── forge_distillation.py
│   ├── forge_capsules.py
│   └── toolscript.py
│
└── adapters/
    └── sandbox/
        └── toolscript.py
```

Do not force this exact shape if the existing repo conventions place these responsibilities elsewhere.

The architectural responsibility matters more than the filename.

---

# 158. Suggested Test Directory Shape

```text
test/
├── agency/
│   └── test_vg_code_forge_manifest.py
├── runtime/
│   ├── test_forge_admission.py
│   ├── test_forge_controller.py
│   ├── test_forge_branch.py
│   ├── test_forge_compaction.py
│   └── test_toolscript_broker.py
├── adapters/
│   └── test_toolscript_sandbox.py
└── falsifiers/
    ├── test_forge_toolscript_authority.py
    ├── test_forge_stale_verification.py
    └── test_forge_child_budget.py
```

Use actual project test conventions.

---

# 159. Example `ForgeReflexState`

```python
@dataclass(frozen=True)
class ForgeReflexState:
    run_id: str

    turns: int
    turns_since_progress: int

    workspace_digest: str
    last_verified_workspace_digest: str | None

    active_hypothesis: str | None
    hypothesis_count: int
    competing_hypotheses: int

    last_failure_fingerprint: str | None
    repeated_failure_count: int

    finish_attempted: bool
    finish_rejection_count: int

    context_pressure: float

    forks_used: int
    forks_available: int

    remaining_turns: int
    remaining_tokens: int | None
```

Keep it projection-derived.

Do not treat it as an independent authoritative mutable store.

---

## Wave acceptance

This wave is accepted only after its focused unit/contract/falsifier tests pass, boundary and domain-blindness linters remain green, no kernel LOC is added, and every claimed completion is backed by a fresh verification receipt. Full-suite execution is intentionally deferred to final integration.
