# AETHER FORGE — Full Code Manifest — Wave 4

## Delivery contract

- Branch: `feat/beta-release_electroweak-v091`
- Exact reconciled subject: `f242ced297216109736975376802f1e3dc4e29ce`
- Scope: backend only; no frontend changes.
- Focus: Concrete types and examples, protocol lineage, dependency/repository policy, final verification, rollback, migration, promotion criteria, comparative architecture, and engineering checklist.
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


# 160. Example Reflex Policy

```python
class DefaultForgeReflexPolicy:
    def decide(
        self,
        state: ForgeReflexState,
    ) -> StrategyDirective | None:

        if (
            state.finish_attempted
            and state.workspace_digest
            != state.last_verified_workspace_digest
        ):
            return StrategyDirective(
                kind="change_verification",
                reason="Verification is stale for current workspace.",
            )

        if state.repeated_failure_count >= 2:
            if (
                state.forks_available > 0
                and state.competing_hypotheses > 0
            ):
                return StrategyDirective(
                    kind="fork",
                    reason="Repeated failure with unresolved alternatives.",
                )

            return StrategyDirective(
                kind="redirect",
                reason="Repeated equivalent failure; change approach.",
            )

        if state.turns_since_progress >= 3:
            return StrategyDirective(
                kind="abandon_hypothesis",
                reason="No environment-visible progress.",
            )

        if state.context_pressure >= 0.88:
            return StrategyDirective(
                kind="request_context",
                reason="Compact active trajectory.",
            )

        return None
```

---

# 161. Example Goal Contract Builder

```python
def build_goal_contract(
    task: CodingTask,
    harness: ResolvedHarness,
) -> GoalContract:
    checks = []

    if task.mode == "write":
        checks.append(
            CheckRequirement(
                kind="workspace_changed",
                required=True,
            )
        )

        checks.append(
            CheckRequirement(
                kind="verification_fresh",
                required=True,
            )
        )

    return GoalContract(
        task_digest=task.digest,
        mode=task.mode,
        required_effects=tuple(...),
        required_checks=tuple(checks),
        forbidden_conditions=(
            "unresolved_patch_conflict",
        ),
        completion_evidence=(
            "workspace_digest",
            "verification_receipt",
        ),
    )
```

Keep heuristics conservative.

Do not invent test requirements the task cannot satisfy.

---

# 162. Example Context Summary

```text
FORGE STATE

Goal:
Fix TTL refresh so reads after refresh observe the renewed expiration.

Current hypothesis:
refresh() updates value but does not update expiry index.

Verified facts:
- CacheEntry stores expires_at.
- refresh() is implemented in cache/store.py:118.
- test_refresh_expiry currently fails.
- Failure remains after first patch because secondary heap index is stale.

Rejected:
- serializer bug.
- clock mock issue.

Changed:
- cache/store.py

Verification:
pytest tests/cache/test_refresh.py -q
FAIL 1/7
receipt artifact sha256:...

Branch:
branch-02 confirmed heap index is authoritative for eviction.

Next:
update heap index atomically with expires_at, rerun targeted test.

Raw evidence:
sha256:...
```

This is the target quality for compaction.

---

# 163. Example Branch Summary

```json
{
  "branch_id": "run-child-02",
  "objective": "Determine whether TTL eviction uses CacheEntry.expires_at or the heap index.",
  "disposition": "supported",
  "findings": [
    "Eviction reads the heap index, not CacheEntry.expires_at directly.",
    "refresh() updates CacheEntry.expires_at but leaves the heap node stale."
  ],
  "files_inspected": [
    "cache/store.py",
    "cache/eviction.py",
    "tests/cache/test_refresh.py"
  ],
  "evidence_refs": [
    "sha256:..."
  ],
  "dead_ends": [
    "serializer path is unrelated"
  ],
  "next_action": "Update heap entry during refresh."
}
```

---

# 164. Example Candidate Patch Branch Result

```json
{
  "branch_id": "run-child-07",
  "objective": "Try atomic heap replacement during refresh.",
  "disposition": "candidate_patch",
  "patch_digest": "sha256:...",
  "verification_digest": "sha256:...",
  "findings": [
    "Targeted cache tests pass 7/7.",
    "No API surface change."
  ],
  "confidence": 0.94
}
```

Parent must still apply and verify against its own authoritative workspace.

---

# 165. Example ToolScript Manifest Concept

```json
{
  "name": "toolscript",
  "description": "Execute bounded Python that may invoke authorized AETHER tools through a mediated broker.",
  "input_schema": {
    "type": "object",
    "properties": {
      "source": {
        "type": "string"
      },
      "max_tool_calls": {
        "type": "integer",
        "minimum": 1,
        "maximum": 64
      }
    },
    "required": ["source"]
  }
}
```

Translate to the actual tool schema format.

Do not expose arbitrary runtime options to the model unless necessary.

---

# 166. Example ToolScript System Prompt Fragment

```text
Use ToolScript when several deterministic tool operations can be composed more efficiently than alternating model/tool turns.

Good uses:
- search + filter + rank many repository matches
- parse large test output
- traverse symbol/reference relationships
- compute summaries over structured tool results

Do not use ToolScript merely to hide reasoning.
Do not attempt direct host access.
All privileged operations must use the provided tool RPC functions.
Print only the information you need for the next reasoning step.
```

---

# 167. AETHER Protocol Mapping

FORGE should preserve:

```text
Model intention
→ EffectProposal
→ policy/capability check
→ adapter execution
→ receipt
→ event
→ projection
```

ToolScript nests this pattern but does not replace it:

```text
Model intention
→ ToolScript effect
→ sandbox
→ inner tool intention
→ normal AETHER effect
→ normal authorization
→ normal receipt
```

This nested execution must preserve parent causal references.

---

# 168. Causal Lineage for ToolScript

Recommended lineage:

```text
root run
└── model proposal
    └── ToolScript effect
        ├── fs.search effect
        ├── fs.read effect
        ├── fs.read effect
        └── proc.test effect
```

The final ToolScript receipt references all child effect IDs.

This is important for:

- replay;
- audit;
- cost accounting;
- debugging;
- trajectory analysis.

---

# 169. Causal Lineage for Fork

```text
root run
└── agent.spawn effect
    └── child run
        ├── model/tool events
        ├── artifacts
        └── child result
            └── BranchSummary artifact
```

Parent context receives the summary, but lineage remains linked.

---

# 170. Budget Settlement

FORGE must not invent local accounting.

ToolScript consumes:

```text
outer effect budget
+
inner tool-call budget
+
wall-time/runtime budget
```

Fork consumes:

```text
child conserved budget
```

Candidate branch unused budget returns according to existing settlement semantics.

No negative-consumption/refund reinterpretation.

---

# 171. Security of Model-Generated Procedures

A ToolScript is untrusted input.

Treat it similarly to:

```text
a user-submitted script
```

Therefore:

```text
validate
sandbox
constrain
authorize each privileged effect
record
terminate on violation
```

Do not trust it because it was generated by the same model operating the agent.

---

# 172. Dependency Policy

Avoid adding large dependencies.

Preferred ToolScript MVP:

```text
Python stdlib
existing sandbox/process abstractions
existing IPC/JSON utilities
```

Only add dependencies if they provide a substantial and measured benefit.

FORGE itself should not require:

```text
Ray
Celery
LangGraph
Docker SDK
new graph databases
new orchestration frameworks
```

---

# 173. Repository Compatibility

FORGE should remain repository-language agnostic.

Core tools:

```text
filesystem
search
git
process execution
patch
test command
```

Language-specific behavior should live in:

```text
skills
capsules
LDA providers
ToolScripts
repository manifests
```

This keeps Vanguard universal.

---

# 174. Language-Specific Skills

Examples that may later be reusable:

```text
python-pytest
rust-cargo
typescript-vitest
go-test
java-gradle
```

Each can provide:

```text
test command discovery
failure parser
related file conventions
build command
```

But the core FORGE loop remains unchanged.

---

# 175. Repository Bootstrap

On first contact with an unknown repository, FORGE may run a cheap bootstrap:

```text
git status
top-level tree
detect language/build files
detect test roots
read nearest README/AGENTS instructions
```

Do not create a complete semantic index automatically.

Only deepen exploration if needed.

---

# 176. Repository Instructions Priority

Context order:

```text
system/AETHER law
> explicit task
> repository AGENTS/instructions
> package/module-specific instructions
> README/conventions
> inferred behavior
```

FORGE must inspect repo-local agent instructions where present.

Derived summaries may never override direct instructions.

---

# 177. Diff Review

Before finish:

```text
git diff --stat
git diff relevant files
```

Use either:

```text
model review
or
deterministic checks
```

depending on task.

The Stop Gate may require existence of a patch/diff artifact for write tasks.

---

# 178. Final Verification Policy

A reasonable default:

```text
simple bug
→ targeted tests

medium change
→ targeted + related tests

large change
→ targeted + related + build/typecheck where appropriate
```

Do not always run the entire repository test suite.

The model can request broader verification if uncertainty remains.

---

# 179. Task Completion Record

Final result should include references to:

```text
task digest
final workspace digest
patch digest
verification receipt(s)
important artifact refs
branch summaries used
model identities
```

The user-facing response may remain concise.

The internal run remains fully inspectable.

---

# 180. Rollback Strategy

FORGE is outer-layer and should be easy to disable.

Rollback:

```text
remove/disable vg-code-forge manifest
disable ToolScript capability
disable fork reflex
retain generic runtime behavior
```

No data migration should be required for core AETHER.

Artifacts/events from prior FORGE runs remain readable.

---

# 181. Feature Flags

During development:

```text
forge.stop_gate
forge.reflexes
forge.toolscript
forge.forks
forge.capsules
forge.lda
```

Prefer manifest-level flags.

Avoid global environment-variable spaghetti.

---

# 182. Backward Compatibility

Existing harnesses:

```text
vg-code-default
vg-code-swe-mini
vg-code-opencode-shaped
```

must continue to work unchanged.

FORGE additions should be opt-in.

No semantic changes to shared runtime should occur unless existing tests prove compatibility.

---

# 183. Migration Policy

No migration of existing agents into FORGE.

Instead:

```text
existing harness stays
new FORGE preset added
comparison begins
successful mechanisms later generalized selectively
```

This preserves experimental clarity.

---

# 184. Promotion Criteria to General Vanguard

A FORGE mechanism may be generalized only if:

```text
useful across at least two agent domains
not coding-specific
stable contract
measurable benefit
low overhead
clear semantics
```

Likely candidates:

```text
artifact-backed tool admission
generic bounded ToolScript capability
generic branch distillation
```

Likely FORGE-specific mechanisms:

```text
coding GoalContract rules
coding failure reflexes
coding branch prompts
```

---

# 185. Kernel Promotion Criteria

A FORGE mechanism should enter kernel only if:

```text
it is required for authority,
budget conservation,
causal lineage,
settlement,
or universal effect execution semantics.
```

Almost nothing in FORGE should satisfy this criterion.

---

# 186. First Benchmark Expectation

Do not expect immediate SOTA score.

The first milestone is more fundamental:

```text
strong model actually performs complex coding work
```

Observed evidence should shift from:

```text
NO_PATCH
empty/fictional success
unverified answer
```

toward:

```text
real file localization
real patch
real test
adaptive repair
verified completion
```

Only then optimize score.

---

# 187. Why FORGE Could Beat a Heavier Harness

A heavier harness may force the model through incorrect abstractions.

FORGE instead gives:

```text
small trusted substrate
+
high programmability
+
real feedback
+
optional extra compute
```

As models improve, this can age better because less cognitive policy is frozen into the harness.

The harness provides **capabilities and invariants**, not a mandatory theory of reasoning.

---

# 188. Why FORGE Could Fail

FORGE may underperform if:

```text
models cannot reliably decide when to use ToolScript
models do not branch strategically
reactive loop wanders
minimal prompt lacks useful software-engineering priors
ToolScript sandbox overhead is too high
branch distillation loses crucial details
```

If so, selectively add:

```text
skills
reflexes
small procedural guidance
task-type presets
```

Do not immediately revert to a giant orchestration architecture.

---

# 189. Comparison with External Inspirations

FORGE should copy **principles**, not code.

## From DeepSeek Harness

```text
small execution loop
extensibility outside core
interceptable runtime behavior
```

## From Hermes

```text
programmatic tool calling
procedural/skill-oriented agent behavior
context economy
```

## From Pi

```text
small agent surface
branchable sessions
compaction
extensions
```

## From Grok Build

```text
lifecycle interception
stop rejection
subagent isolation
skills
```

AETHER contributes:

```text
capability authority
causal event ledger
budget conservation
artifacts
recovery
settlement
manifest composition
```

The combination is the differentiator.

---

# 190. Reference Architecture Summary

```text
AETHER KERNEL
  authority / budgets / lineage / effects
              │
              ▼
VANGUARD RUNTIME
  session / episode / projections / artifacts
              │
              ▼
FORGE HARNESS
  ├── minimal reactive prompt
  ├── Stop Gate
  ├── Reflex Controller
  ├── Forge Compaction
  ├── ToolScript
  ├── Adaptive Forks
  ├── Branch Distillation
  ├── Task Capsules
  └── Optional LDA
              │
              ▼
REAL REPOSITORY
  filesystem / git / shell / tests
```

---

# 191. Final Implementation Directive

The implementing developer should proceed as follows:

> **Do not redesign the framework. Reconcile the exact current code once, identify the existing seams, create `vg-code-forge`, and implement the smallest missing outer-layer mechanisms required for a powerful reactive coding agent. Use existing admission, controller, spawn, context, artifacts, event ledger, budgets, and recovery semantics. Add ToolScript through a mediated sandbox, use child runs for optional branching, distill trajectories rather than copying transcripts, and make environment evidence the sole basis for completion.**

The implementation should optimize for:

```text
real coding ability
low harness friction
programmability
evidence
context efficiency
recovery
bounded adaptive compute
architectural reversibility
```

---

# 192. Principal Engineering Checklist

Before declaring FORGE implementation ready:

```text
[ ] Runs through current product entrypoint
[ ] No new parallel runtime
[ ] No new event authority
[ ] No capability bypass
[ ] Stop Gate uses real evidence
[ ] Real patches occur
[ ] Real tests occur
[ ] Stale verification rejected
[ ] Repeated failures change strategy
[ ] ToolScript mediated through dispatch
[ ] ToolScript sandbox falsifiers pass
[ ] Fork uses existing child runtime
[ ] Child authority attenuated
[ ] Child summaries bounded
[ ] Compaction preserves engineering state
[ ] Artifacts preserve raw evidence
[ ] Resume reconstructs state
[ ] LDA optional
[ ] LAM external
[ ] Existing harnesses unaffected
[ ] Simple tasks retain low overhead
[ ] Complex tasks can scale compute
```

---

# 193. Final Thesis

The strongest version of FORGE is not a giant coding workflow.

It is a **programmable, evidence-grounded coding substrate layered over AETHER**:

```text
Model
+
Minimal Reactive Loop
+
Authorized Tools
+
Programs Over Tools
+
Branchable Reasoning
+
Runtime Reflexes
+
Artifact-Backed Context
+
Real Verification
```

The model is allowed to create temporary procedure; AETHER remains responsible for authority, execution, evidence, durability, and recovery.

That separation is the core architectural bet.

If successful, FORGE should allow Vanguard to exploit stronger future models without repeatedly redesigning the orchestration layer, while still supporting sophisticated task-specific behavior when the problem actually requires it.


## Wave acceptance

This wave is accepted only after its focused unit/contract/falsifier tests pass, boundary and domain-blindness linters remain green, no kernel LOC is added, and every claimed completion is backed by a fresh verification receipt. Full-suite execution is intentionally deferred to final integration.
