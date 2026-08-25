# SPEC_M5B_M6 — Generality Falsifier (M-5b) & Mediated Delegation (M-6)

Horizon rule: architecture + contracts strong; local algorithms open. Both milestones start from
`M-5-BASE` and are mutually parallel (disjoint module sets).

---

# §1 M-5b — Formal Pack #2 (D-16; RF-86, RF-52/53, RF-98 first run)

**Purpose.** Falsify substrate generality: a materially non-coding domain runs through the
*unchanged* post-M-5a substrate. Success = new pack only; failure = admissible counter-evidence
(0096 §1) triggering Vision review — both outcomes are wins for the process.

**Domain selection (open decision OD-3, owner: Director, due at M-5b entry):** candidates —
(a) SAT/SMT witness problems (oracle: solver check, e.g. DIMACS + verifier binary);
(b) Lean/proof-checking mini-corpus; (c) constraint puzzles with deterministic verifiers.
Selection criterion: strongest deterministic witness (RF-52/53 "T0 witness") with the weakest
possible evaluation ambiguity; zero new kernel/substrate needs by construction of the criterion.

**Structure (mirrors `packs/code-default/` exactly):**

```text
packs/formal-<oracle>/
  plugin.yaml · harness.yaml           # composition entries (mhf.manifest/2)
  system-prompt.txt
  context-policy.json · context_policy.py   # domain context layers/selection
  toolkits/            # solver invocation tool(s): typed EffectRequest verbs e.g. "solver.check"
  oracles/             # deterministic witness verifier → verification receipt
  planners/            # optional domain proposal policy
```

**Contract obligations (all reuse, none new):** tools declare capability + sink class like any
adapter-backed verb; the witness verifier is an exterior evaluator producing a signed verdict
(I-5) — implement as `adapters/evaluators/suites/` entry, not pack-internal self-grading; domain
projections (proof state, candidate/counterexample sets) are pack-owned reducers over generic
kinds (`ProposalProduced`, `ClaimRecorded{claimKind:domain-…}`, `EffectCompleted`, `PlanRevised`,
`ProgressAssessed`) — **no new event kinds permitted** (that is the test).

**Falsifiers/gates.**
- **RF-86 zero-semantic-diff:** CI job diffing `vanguard/packages/{domain,ports,kernel,agency,runtime}`
  between M-5-BASE and M-5b completion — only additive pack/adapter/test paths may change; any
  substrate diff requires either revert or an ADR classifying it as counter-evidence.
- **RF-52/53:** fixed task set where the deterministic witness accepts/rejects candidates;
  end-to-end run produces signed verdicts + complete trajectory + fresh-process reconstruction.
- **RF-98 (first material run):** `kernel semantic diff == 0` report attached to the exit review.
- Trajectory sections (provenance/repro) populate identically to coding — proves M-4 capture is
  domain-blind.

**Acceptance:** one full formal run bundle (trajectory + verdicts + reconstruction) reviewed;
RF-86 diff report empty; Director closes M-5b. Artifacts: pack, evaluator suite, diff report,
generality memo (evidence-first, per 0096 §1.4 — no pre-registration required, assurance profile
may add it).

---

# §2 M-6 — `agent.spawn` as mediated nested lineages (D-17; RF-55…RF-59)

**Design authority already frozen:** ADR-0080 (capability-mediated spawn), ADR-0090 (mediated
delegation event roster: `ChildSpawned/ChildReturned` owned by `spawn_adapter`), ADR-0091
(delegation state digest), SPEC refusal: *"`agent.spawn` is a generic S0–S12 effect whose
post-intent child creation belongs to a runtime adapter; the kernel MUST NOT branch on the verb
or know child topology."* This spec binds those decisions to current symbols.

**As-built seams:** `runtime/delegation.{SpawnRequest, prepare_spawn, SpawnPreparationError}`
(pure preparation: grant/attenuation validation); `agency/episode/engine.EpisodeEngine.spawn`
(in-process child executor with scope narrowing, budget conservation, workspace destroy-in-finally);
kernel `attenuate()` + `Governor` leases; writer role `spawn_adapter` reserved in
`PRIVILEGED_KIND_OWNERS`.

**Target call path:**

```text
policy proposes Proposal(kind=EFFECT, verb="agent.spawn", body=SpawnRequest-shape)
→ EpisodeEngine._to_effect_request (unchanged, generic)
→ Kernel.dispatch S0–S12   # capability "agent.spawn" required on grant; budget reservation
                           # covers the child budget slice as ordinary resources; verb-blind
→ SpawnAdapter.execute(request)          # the EffectAdapter bound to sink class "delegation"
    1. prepare_spawn(request, grant, parent_scope)         # existing pure validation
    2. child ExecutionScope = parent.attenuated_for_child(budget_slice,…)   # M-5a contract
    3. emit ChildSpawned (role=spawn_adapter; payload mhf.child-spawned/1:
         childLineageId(uuid7), parentLineageId, briefDigest, scope{budget,maxDepth,maxTurns},
         capabilityGrant(child, attenuated), authoritySource="capability")
    4. run child: EpisodeEngine.spawn(child_scope=…, brief=…, parent_lease=…)   # in-process M-6;
         a process/remote executor is a later adapter behind the same step
    5. emit ChildReturned (payload mhf.child-returned/1: childLineageId, terminal,
         resultDigest|resultArtifact, evidence[], confidence?, unresolved[], consumed{6D},
         stateDigest per ADR-0091)
    6. return EffectCompleted result = delegation contract:
         result + evidence + confidence + artifacts + unresolved  (never a conversation dump)
```

```python
# runtime/delegation.py — additions
class SpawnAdapter:            # implements ports.kernel.EffectAdapter
    """deps: engine_factory: Callable[[ExecutionScope, str-brief], EpisodeEngine-run-closure],
             emitter: RoleScopedEmitter("spawn_adapter"), clock, governor_view (read-only)."""
    def execute(self, request: EffectRequest) -> EffectResult:
        """Failure semantics:
             SpawnPreparationError → EffectRejected (kernel path), no child events;
             child crash/abandon    → ChildReturned{terminal:aborted|abandoned} + EffectFailed;
             cancellation           → propagate is_cancelled; kill-tree = cancel depth-first,
                                      each child settles ChildReturned before parent EffectFailed;
             restart mid-spawn      → RecoveryScanner: ChildSpawned without ChildReturned ⇒
                                      reconcile as EffectReconciled + ChildReturned{terminal:aborted,
                                      recovered:true} (no budget leak — lease reconciliation
                                      re-uses reconcile_open_intents).
           Idempotency: idempotency_key of the spawn effect keys the whole subtree; re-dispatch
             after settlement returns the settled result (continue_idempotent_effect pattern).
           Must not: widen authority; execute domain child policy; mutate parent AgentView."""
```

**Budget algebra (kernel-unchanged):** parent reserves the child slice via ordinary
`BudgetReserved`; child consumption events carry the child lineage; on `ChildReturned`, unspent
slice is `BudgetReleased` to the parent lease. Structural dims: child `depth = parent.depth+1 ≤
max_depth`; turns are child-local ceilings. Conservation test: Σ(child consumed) + released ==
reserved, per additive dim (RF-57 shape).

**Falsifier matrix (all under `test/falsifiers/`):**
| RF | Asserts |
|---|---|
| RF-55 | spawn without `agent.spawn` capability → EffectRejected; no child events |
| RF-56 | scope/authority attenuation strict (verb withheld from child stays denied at kernel policy, per ADR-0067 path) |
| RF-57 | 6D budget conservation across the tree; depth/turn ceilings enforced |
| RF-58 | join semantics: parent receives typed delegation contract; ChildReturned precedes parent settlement |
| RF-59 | kill-tree + **real restart** recovery: fresh process reconciles orphan ChildSpawned, no lease leak, AgentView shows children with recovered terminals |

**Payload schemas:** `mhf.child-spawned/1`, `mhf.child-returned/1` are M-6 kind-package additions?
No — kinds exist (`ChildSpawned/ChildReturned`, generated enum); only payload schemas + golden
vectors are added (allowed: payload-level, ADR-0090 roster already normative).

**Deprecation:** direct policy-level calls to `EpisodeEngine.spawn` become non-product path
(benchmark/lab only); product profiles route spawn exclusively through kernel dispatch — enforced
by a governance test asserting no production import calls `engine.spawn` outside `SpawnAdapter`.

**Exit gate:** RF-55…59 green; one demonstration run: coding task delegating a subtask
(e.g. test-writing child) end-to-end with trajectory showing nested lineage; fresh-process
reconstruction includes child tree. Unlocks: M-6.5 delegate action; M-7 topology lowering targets.
