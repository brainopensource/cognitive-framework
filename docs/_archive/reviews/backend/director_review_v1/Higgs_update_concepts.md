# AETHER / Vanguard — Forensic Architecture Review and Corrective Evolution Plan

**Repository:** `brainopensource/cognitive-framework`  
**Branch:** `main`  
**Verified commit:** `183fc9dfef928ccaa2d5a0950d2de99eb552a871` (`feat(M-3): V0.6.1`)  
**Commit timestamp:** 2026-08-23 08:36:23 -0300  
**Audit timestamp:** 2026-08-23 19:18 UTC  
**Review mode:** independent, zero-base, implementation-first; no repository modifications  
**Decision horizon:** corrective v0.6.2, M-4, and operational v1.0.0

---

## 1. Executive verdict

**Decision: Proceed with focused corrections.**

**Confidence: 0.91 (high).**

AETHER is not an empty architecture document and it is not merely a thin wrapper around an LLM. It already contains a technically serious trust spine: a bounded effect reference monitor, monotonic capability attenuation, explicit reservations and settlement, JCS-based identity, an append-only event model, fresh-process recovery machinery, exterior signed evaluation, fail-closed evidence semantics, rootless execution adapters, schema vectors, architectural linters, and an unusually strong falsifier culture. Those mechanisms are the expensive, high-leverage part of a durable agent substrate and should be preserved.

However, the current `main` branch does **not** yet implement the architecture it claims to have completed at M-3. The decisive defect is not the quality of the named-component design; it is its absence from the canonical execution path. `mhf.manifest/2` is parsed and compiled in `domain/artifacts/manifest.py` and `runtime/registry/compiler.py`, and the registry lifecycle has contract tests, but the public runtime still executes through `Runtime.compose()` in `runtime/compose.py`, which calls `ManifestLoader.load_pack()` and produces the legacy `HarnessManifest`. Every executable first-party pack under `vanguard/packages/agency/manifests/` is still legacy-shaped. The nominal M-3 graph is therefore a tested side path, not the composition authority of the product.

The same split exposes a real generality failure. `vg-table-default` can be parsed, but the canonical runtime refuses to compose it because `DEFAULT_BINDINGS` knows only `fs.*`, `patch.apply`, and `proc.exec`. The code pack remains executable; the non-code pack is not. This is direct evidence that AETHER today is a **governed coding-agent runtime with a promising meta-framework contract**, not yet a proven meta-framework.

M-4 is also more than environment-blocked. Credentials and an exterior evaluator are genuinely absent in the audit environment, but the default product path creates `SqliteEventStore(":memory:")`, while M-4 requires durable WAL and cold reconstruction; it also does not execute a `mhf.manifest/2` composition or activate its registry graph. A real provider could make a model call, yet still fail to prove the architecture that M-3 claims. Running M-4 now would validate the legacy coding path and harden the wrong seam.

The correct response is **not a broad rewrite**. The kernel, authority algebra, evidence semantics, reducer, event store, evaluator boundary, and recovery work should survive. The required action is a bounded **M-3C Composition Convergence** correction: make one schema, one parser, one frozen composition, one activation plan, one registry lifecycle, and one public runtime path true in production; convert the executable coding pack and one minimal non-coding probe; delete the legacy composition authority only after differential parity. Then execute M-4.

### Bottom line

| Question | Answer |
|---|---|
| Is the foundation worth preserving? | **Yes.** The trust/evidence core is substantive and well-falsified. |
| Is M-3 complete operationally? | **No.** Its graph and registry are implemented but not canonical in execution. |
| Is M-4 blocked only by environment? | **No.** Environment is a real blocker, but composition and persistence integration are incomplete product capabilities. |
| Is a clean-slate rewrite justified? | **No.** Local convergence can repair the failed boundary at much lower cost. |
| Should development proceed unchanged? | **No.** It would certify the legacy path and deepen dual architecture. |
| Correct release meaning | **v0.6.2 = composition convergence and second-domain executability, not new features.** |
| Correct next proof | **M-3C first, then the unchanged nine-row M-4 real run.** |

---

## 2. Baseline and evidence discipline

### 2.1 Repository baseline

The remote `refs/heads/main` and local `HEAD` both resolved to:

```text
183fc9dfef928ccaa2d5a0950d2de99eb552a871
```

The clone was clean (`main...origin/main`) and no source or documentation file inside the repository was modified. The audited tree contained:

- 1,591 tracked files in total;
- 149 Python production files under `vanguard/packages/`;
- approximately 25,805 production Python lines under `vanguard/packages/`;
- 163 Python test modules and approximately 24,568 Python test lines;
- 390 JSON schema/vector files;
- 100 Markdown documents;
- 1,391 files in the explicitly requested architecture, schema, package, pack, container, test, tool, and workflow surfaces.

### 2.2 Verification results

The following results were directly observed:

| Verification | Result | Interpretation |
|---|---:|---|
| Kernel suite | 93/93 pass | Strong local evidence for the effect TCB. |
| Agency suite | 105/105 pass | Sequential episode semantics are well covered. |
| Contract suite | 169/169 pass | Wire/law contracts have substantial executable coverage. |
| Trust suite | 22/22 pass | Trust-spine contract remains green. |
| Security suite | 45/45 pass | Security tests green in this sandbox. |
| Pack suite | 32/32 pass | Pack parsing and pack-local constraints pass; not equivalent to runtime activation. |
| M-4 evidence auditor | 13/13 pass | The auditor rejects important forged/incomplete evidence classes. |
| Boundary linter | Pass, 244 files | Declared lattice is mechanically enforced. |
| TCB budget | Pass, 1,365 logical LOC / 1,438 ceiling | Kernel remains bounded, but only 73 LOC of headroom remain. |
| Domain blindness | Pass with obsolete-path warning | No coding/pytest/AST tokens in domain/kernel; scanner still mentions missing `layer0/`. |
| Isolation policy | Pass | `proc.exec` plugins declare subprocess/container isolation. |
| Code generation | Pass | `types_gen.py` matches `schemas/mhf`. |
| Event coverage | Pass | Production-emittable kinds are catalogued. |
| RF identifier allocation | Pass | Falsifier identifiers are unique and cited. |
| Duplication, links, stale paths, secrets | Pass | Governance checks are useful and operational. |
| Full Python suite | Environment-inconclusive | AF_UNIX socket creation was denied by the audit sandbox; several evaluator/registry tests could not complete. |
| RF-38…RF-45 lifecycle suite | 36 pass, 2 environment errors | Echo/crash broker tests timed out because child UDS binding was prohibited; not evidence of a product defect, but not a green rerun here. |
| TypeScript suite | Blocked by execution environment | Node dependency execution attempted restricted network behavior; no claim made. |

The socket failures are classified as **blocked by environment**, not silently converted into failures or passes. Existing repository evidence may show them green elsewhere, but this review does not independently certify that portion.

### 2.3 Claim classification

| Claim | Classification | Evidence |
|---|---|---|
| M-0 engineering truth is implemented | Implemented and largely verified | CI, linters, codegen, test suites. |
| M-1 trust spine is implemented | Implemented and verified within audit scope | Kernel/trust/security tests; signed verdict machinery. |
| M-2 truthful trajectory and cold recovery exist | Implemented and strongly tested, full-suite rerun partially environment-blocked | Event/reducer/store/recovery modules and targeted contracts. |
| M-3 parser and component graph exist | Implemented and tested | `domain/artifacts/manifest.py`, `runtime/registry/compiler.py`, graph tests. |
| M-3 is canonical runtime behavior | **Contradicted by code** | Public runtime composes the legacy manifest through `load_pack()`. |
| Plugin registry lifecycle exists | Implemented, but independent rerun environment-blocked | `runtime/registry/*`, RF-38…45. |
| Layer-0 source retirement happened | Implemented and verified | No `layer0/` source/package path; duplication checks pass. |
| Layer-0 conceptual duplication is fully retired | **Contradicted** | Two manifest/composition authorities remain. |
| Coding is merely Pack #1 | Documented intent, only partially implemented | Coding path executes; table pack fails canonical composition. |
| M-4 is environment-blocked | True but incomplete | Provider/evaluator absent, plus canonical composition and durable default path are missing. |
| Nine-row auditor proves an actual M-4 run | Correctly documented as false | Auditor validates supplied rows; it cannot create or cryptographically bind every row itself. |
| v0.6.1/v0.6.2 status is coherent | Contradicted across metadata/docs | `pyproject` 0.4.5b1; commit says M-3/V0.6.1; law says M-3/v0.6.2; README/AGENTS still say M-2 active. |

---

## 3. What AETHER is today

AETHER today is best defined as:

> A Python-first, event-sourced, capability-mediated, sequential agent execution runtime with a bounded effect reference monitor, exterior evidence boundary, coding-oriented production composition path, and a separately implemented but not yet activated named-component meta-framework layer.

That definition is narrower than the project vision but stronger than “prototype scaffolding.” It recognizes three different maturity levels:

1. **Durable trusted substrate — real:** domain values, selector algebra, kernel dispatch, grants, budgets, event emission, persistence, recovery, evaluator verification.
2. **Coding agent runtime — partially real:** episode execution, model adapters, context compiler, tool/effect bridges, repair loops, rootless environment, code pack.
3. **General meta-framework — contractual prototype:** named graphs, typed bindings, profiles, plugin lifecycle, reserved future fields; not yet the public activation path.

The architecture is therefore not a failure. Its primary risk is **premature semantic closure**: treating the contractual prototype in level 3 as operationally complete and building M-4 through M-10 on level 2.

---

## 4. Architecture assessment

### 4.1 Domain, ports, kernel, agency, runtime, adapters

The declared lattice is coherent:

```text
domain <- ports <- kernel <- agency <- runtime -> adapters
                                      |
                                      +-> apps/clients
```

The boundary checker makes this more than a diagram. Domain and kernel are relatively clean, domain-blind, and protected from adapter/runtime imports. This should remain.

The main problem is not dependency direction; it is **ownership duplication inside legal layers**:

- `domain/artifacts/manifest.py` contains both legacy and named manifest values/readers.
- `agency/manifests/loader.py` exposes `load_pack()` for legacy execution and `load_named_manifest()` as a reader-only side path.
- `runtime/compose.py` owns the public legacy composition.
- `runtime/registry/compiler.py` owns named composition but is not called by the public runtime.
- `packs/code-default/harness.yaml` introduces yet another `mhf.harness/1` representation, while executable manifests live under `agency/manifests/`.

This is a convergence defect, not a reason to abolish the lattice.

### 4.2 Kernel and authority

The S0–S12 dispatch pipeline, selector decisions, grants, typed reservation/settlement, sink classification, provenance, and fail-closed behavior are the strongest part of the codebase. The kernel is small enough to audit and has direct falsifiers.

Two cautions apply:

- At 1,365/1,438 logical LOC, the kernel has only ~5% headroom. `agent.spawn`, concurrency, routing, recovery policy, plugin lifecycle, and evaluation must not be added to it merely because they are “important.” New kernel code is justified only for new authority semantics.
- The current TCB budget is an alarm, not a proof of minimality. Complexity, branch count, state-space coverage, and mutation strength should supplement LOC.

### 4.3 Episode engine and universal-loop thesis

The unary sequential turn loop is a sound **reference execution protocol** for M-4 and a useful deterministic baseline. It should not be promoted into an ontological claim that every future algorithm is itself a turn loop.

The correct separation is:

- **Episode protocol:** observe/propose/authorize/effect/receipt/evaluate.
- **Topology/controller:** chooses which logical node or agent receives the next transition.
- **Scheduler:** assigns ready transitions to workers.
- **Worker:** executes one bounded transition.

Critic/reviser and planner/executor/verifier can be lowered into the current sequential protocol. Debate, bounded tree search, evolutionary populations, and asynchronous research workflows require explicit graph state and a scheduler, even if their effects still pass through S0–S12. If M-8 tries to encode these as opaque “planner plugins” inside one episode, composition will be decorative and observability will collapse.

Therefore I-11 should remain for the foundation, but ADR-0082’s “universal loop” must be interpreted as a universal **effect/evidence protocol**, not necessarily a universal control-flow implementation.

### 4.4 Runtime composition

The central defect is demonstrable:

```text
Runtime.execute_harness
  -> Runtime.compose (runtime/compose.py)
  -> ManifestLoader.load_pack
  -> legacy HarnessManifest
  -> HarnessSession
```

The implemented M-3 path is separate:

```text
ManifestLoader.load_named_manifest
  -> parse_named_manifest
  -> runtime.registry.compiler.compose_named
  -> NamedManifest with digest
  -X-> no ActivationPlan
  -X-> no Runtime.compose
  -X-> no HarnessSession
```

This means the graph is “declarative” only up to validation and digesting. Its bindings do not yet determine runtime wiring, lifecycle ownership, invocation dispatch, or failure propagation. Important behavior remains hidden in `Runtime.compose`, `wiring.DEFAULT_BINDINGS`, and `HarnessSession`.

### 4.5 Plugin lifecycle and isolation

`runtime/registry/lifecycle.py`, `broker.py`, `worker.py`, `sandbox.py`, and compiler tests are a credible walking skeleton. Good properties include explicit states, illegal-transition rejection, UDS/JSON-RPC framing, crash containment intent, and absence semantics.

What is missing is activation authority:

- no canonical `ActivationPlan` maps frozen components and typed bindings to instances;
- no runtime-owned scope closes all component cells on every exit path;
- no binding resolver proves interface/version compatibility at activation;
- no public run proves component lifecycle events and episode events share one lineage;
- `in_process`, `subprocess`, `container`, and `wasm` are accepted vocabulary, but not equivalently implemented isolation contracts;
- lifecycle is not yet exercised by the code-default product run.

The plugin system is therefore **implemented but not product-integrated**.

### 4.6 Events, ledger, receipts, recovery

The event-sourced direction is appropriate. The SQLite store enables WAL, ordered transactional append, hash continuity, and reconstruction. The reducer and recovery controller separate durable fact from in-memory state. That matches mature durable-execution practice: systems such as Temporal persist a complete event history and distinguish deterministic workflow replay from side-effecting activities ([Temporal event history](https://docs.temporal.io/encyclopedia/event-history), [Temporal SDK architecture](https://docs.temporal.io/encyclopedia/architecture/temporal-sdks)).

But AETHER must avoid claiming “replay” where it performs only a fold. There are three distinct operations:

1. **Projection rebuild:** fold stored events into state.
2. **Deterministic decision replay:** re-run controller code and compare emitted commands with history.
3. **Continuation:** reconcile open intents/leases and resume after the durable frontier.

M-2 provides strong evidence for (1) and (3). Full polyglot equivalence and workflow-code upgrade safety later require (2), including command-sequence mismatch detection and versioned replay behavior.

### 4.7 Evaluator and evidence boundary

Exterior signed evaluation is strategically correct. It prevents the acting agent from self-authoring the evidence used for promotion. The evaluator binding table’s refusal to substitute `FakeEvaluator` in production is good.

The M-4 nine-row auditor is also valuable, but it currently validates a supplied evidence bundle. Several booleans (`signature_verified`, sandbox probes, point-of-effect verification) are claims unless the auditor derives them from canonical artifacts or trusted attestations. M-4 must bind each row to immutable source records and verify cross-row digests, not merely require truthy fields.

### 4.8 Sandboxing

Rootless Bubblewrap, separated worker/evaluator identities, no host fallback, and capability ceilings are sound Linux-first decisions. Keep Bubblewrap as the Python reference implementation for M-4.

Do not equate a process boundary with a security boundary. `in_process` plugins can corrupt host memory and should be reserved for first-party trusted components. `subprocess` provides crash/process separation, not necessarily filesystem/network/syscall confinement. `container` and future WASM cells require explicit conformance matrices.

### 4.9 Schemas and identity

JCS, golden vectors, generated readers, and distinct `D_H`, `D_R`, `D_X` identities are excellent long-horizon choices. RFC 8785 canonicalization is the right class of primitive for cross-language deterministic hashing.

The manifest schema/parser currently exhibits avoidable dialect complexity:

- the schema models components as an object;
- the domain parser accepts both object and array dialects;
- the array and object paths have different validation rules;
- entrypoints accept list or object forms;
- legacy `HarnessManifest` remains separately parsed and executed;
- the named compiler returns `NamedManifest`, while legacy compiler returns generated `FrozenHarness`.

Convergence should select one canonical external shape and one normalized internal value. Compatibility readers may remain at ingress temporarily, but no compatibility type should cross the freeze boundary.

---

## 5. Keep / change disposition

| Subsystem | Disposition | Rationale |
|---|---|---|
| JCS canonicalization and digest vectors | **Keep frozen** | Cross-language identity anchor; high migration radius. |
| `D_H` / `D_R` / `D_X` separation | **Keep and strengthen** | Necessary for causal attribution and experiment validity. |
| S0–S12 effect reference monitor | **Keep frozen** | Correct minimal authority mediation boundary. |
| Capability attenuation and selector algebra | **Keep; add conformance/fuzzing** | Strong security core; needs cross-language and property tests. |
| Typed reservation/settlement | **Keep** | Essential for bounded autonomy and cost truth. |
| Exterior signed evaluator | **Keep; strengthen evidence derivation** | Prevents self-authored promotion evidence. |
| Append-only ledger and SQLite WAL reference store | **Keep; strengthen replay semantics** | Correct durability foundation. |
| Single `LedgerEmitter` ownership | **Keep frozen** | Prevents competing histories. |
| Rootless Bubblewrap worker | **Keep as reference adapter** | Appropriate M-4 security baseline. |
| Sequential EpisodeEngine | **Keep as reference executor** | Deterministic baseline; do not universalize control topology. |
| `mhf.manifest/2` named component graph | **Strengthen and make canonical** | Right direction, currently side-path only. |
| Legacy `HarnessManifest` execution | **Retire through strangler migration** | Maintains dual composition truth. |
| `runtime/registry/*` | **Strengthen and integrate** | Useful skeleton; activation/lifecycle ownership incomplete. |
| `DEFAULT_BINDINGS` global verb table | **Generalize** | Coding-specific global registry blocks second domain. |
| Component SPIs | **Simplify and version** | Current five coarse labels do not define complete wire behavior. |
| Profiles | **Defer activation; preserve identity** | Correctly reserved; no data yet for routing policy. |
| `agent.spawn` | **Defer to post-generality proof** | Must be an effect, but adding it now hides composition defects. |
| Concurrency/worker pools | **Defer until scheduling measurements** | Sequential baseline first; avoid WAL and lease complexity now. |
| Retrieval/skills/macros | **Experiment outside TCB** | Useful policies, not foundation requirements. |
| VFE/EFE metacognition | **Reject as v1.0 requirement; research track only** | Premature algorithm commitment; evidence/promotion substrate matters first. |
| `packs/code-default/` parallel pack surface | **Consolidate** | Must not compete with executable `agency/manifests` packs. |
| Documentation triad | **Keep, repair status automation** | Good authority model undermined by immediate status drift. |
| Fixed kernel LOC ceiling | **Keep as alarm, supplement metrics** | Useful constraint but not sufficient assurance. |

---

## 6. Zero-base survival assessment

### 6.1 Failed assumption

The failed assumption is:

> Implementing and testing `mhf.manifest/2` plus a registry walking skeleton is sufficient to declare extensibility complete before the public runtime executes through them.

It is false because extensibility is an end-to-end property. A component graph that does not control activation, lifecycle, invocation, failure, and evidence is metadata, not architecture.

### 6.2 Why a broad rewrite is unjustified

A clean-slate rewrite would discard the best-tested and highest-radius mechanisms without evidence that they are wrong. The kernel, identity, event semantics, and evaluator boundary are orthogonal to the composition split. Rebuilding them would increase security and migration risk while not inherently fixing composition.

### 6.3 Why a tiny local patch is insufficient

Simply adding one call from `Runtime.compose()` to `compose_named()` is insufficient because the output types, pack layout, artifact resolution, plugin activation, binding semantics, adapter factories, evaluator policy, lifecycle, and session construction differ. The minimum coherent replacement boundary is the **composition-to-activation seam**.

### 6.4 Minimum replacement boundary

Introduce one internal immutable value:

```text
Canonical manifest
  -> normalized ComponentGraph
  -> FrozenComposition (D_H)
  -> ActivationPlan (resolved instances, ports, ceilings, lifecycle)
  -> RunPlan (D_R + environment/model/evaluator identities)
  -> Episode/Scheduler
```

Preserve domain/kernel/event/evaluator semantics. Replace only the parallel manifest loaders, legacy frozen-harness path, hard-coded global wiring assumptions, and disconnected registry activation.

### 6.5 Migration versus clean-slate cost

| Path | Cost | Principal risk | Expected result |
|---|---:|---|---|
| Focused convergence | 2–4 engineering weeks, depending on pack migration and UDS CI | Temporary compatibility complexity | Preserves trust spine and produces one product path. |
| Broad rewrite | 8–16+ weeks before parity | Security regressions, lost falsifiers, new semantics | Recreates existing strengths with no guaranteed composability gain. |
| Proceed unchanged | Lowest immediate cost | Certifies wrong seam; dual architecture compounds | M-4 evidence becomes architecturally misleading. |

### 6.6 Acceptance gates proving convergence superior

1. The public `Runtime.compose()` accepts only the canonical frozen internal representation.
2. A legacy reader, if retained, normalizes to the same representation and yields the same `D_H` as an equivalent v2 manifest.
3. The code pack executes through named graph, registry activation, and lifecycle events.
4. A non-code table or deterministic formal pack executes through the same runtime with zero changes under `domain/`, `kernel/`, `agency/episode/`, and public runtime orchestration.
5. Removing the legacy parser/compose authority leaves all suites green.
6. Every component is started/closed exactly once, including compose failure, cancellation, plugin crash, evaluator failure, and episode exception.
7. One trajectory binds the frozen composition and all activated component digests.

---

## 7. v0.6.2 recommendation

### 7.1 Meaning

**v0.6.2 should mean: “Canonical Composition Convergence.”**

It should not mean that named-manifest syntax exists. It should mean that the complete product path is governed by one frozen named component graph and that at least two domains can activate through it.

### 7.2 Scope

1. **Canonical ingress and normalization**
   - Select the object-map form of `mhf.manifest/2` as the sole authored format.
   - Keep a temporary legacy reader only as an ingress adapter.
   - Normalize to one domain value; freeze once; forbid legacy values beyond ingress.

2. **Activation plan**
   - Add an immutable runtime-owned `ActivationPlan` derived from the frozen graph.
   - Resolve component implementation, configuration digest, interface/version, isolation, ceiling, dependencies, entrypoints, and cleanup order.
   - Include activation-relevant data in `D_H`; runtime/environment identity belongs in `D_R`.

3. **Registry integration**
   - Make registry discovery/verification/start/ready/stop lifecycle part of the public composition scope.
   - Bind lifecycle events to the same project/run/episode lineage.
   - Guarantee reverse-topological cleanup.

4. **Port-based domain extensibility**
   - Replace the global coding-only binding table with composition-supplied, namespaced adapter providers constrained by trusted port interfaces.
   - Move code verbs to the code pack/adapter bundle.
   - Enable the existing table environment without changing kernel or episode engine.

5. **Pack convergence**
   - Convert `vg-code-default` and one minimal non-code pack to canonical v2.
   - Consolidate or retire the parallel `packs/code-default/harness.yaml` surface.

6. **M-4 runner readiness**
   - Default the release/E2E runner to a file-backed SQLite path, never `:memory:`.
   - Separate hermetic test defaults from release-run defaults.
   - Generate the evidence bundle from canonical source artifacts and attestations.

7. **Status truth**
   - Align package version, README, AGENTS, SPEC, sprint board, milestones, and commit/release semantics.
   - Add a CI status-consistency check for machine-readable milestone/version metadata.

### 7.3 Explicit non-scope

- no `agent.spawn` activation;
- no worker pool or concurrency;
- no Pareto controller;
- no tree search/debate/evolution runtime;
- no retrieval platform rewrite;
- no DPO, VFE, EFE, or automatic promotion;
- no Rust/Go rewrite;
- no new general-purpose workflow language;
- no kernel expansion unless a proven authority gap is found.

---

## 8. Strict M-4 readiness assessment

### 8.1 Current verdict

**M-4 is not ready.** The nine-row contract is conceptually correct, but the runner cannot yet demonstrate the canonical post-M-3 architecture.

### 8.2 Block classification

| Block | Classification | Why |
|---|---|---|
| No provider key / local model | Unavailable environment | A real invocation cannot occur here. |
| No evaluator daemon/socket/key material | Missing operational environment/integration | Exterior verdict cannot be independently produced here. |
| Public runtime consumes legacy manifest | Incomplete product capability / design convergence defect | M-4 would bypass M-3 graph. |
| Registry graph not activated by public runtime | Incomplete product capability | Plugin lifecycle is not proven in the run. |
| Default SQLite store is `:memory:` | Product-path defect | Cannot establish file-backed WAL restart continuity by default. |
| Evidence auditor accepts asserted booleans | Evidence integration weakness | Source attestations must be derived/bound, not self-declared. |
| Code-only default bindings | Generality defect, not direct M-4 blocker | Allows coding run but invalidates broader foundation claim. |

### 8.3 What must happen before M-4

- close M-3C composition convergence;
- run one deterministic non-code activation probe;
- provide a file-backed run store and fresh-process continuation command;
- make the E2E runner emit the nine evidence rows from canonical records;
- provision a real model and exterior evaluator environment;
- rerun all gates in a clean Linux environment where AF_UNIX, user namespaces, Bubblewrap, and container UID separation are available.

### 8.4 What must not change before M-4

- S0–S12 semantics;
- capability attenuation rules;
- reservation/settlement algebra;
- exterior evaluator trust boundary;
- JCS and identity preimages except for a deliberately versioned v2 convergence correction;
- one writer/event lineage;
- sequential reference execution;
- the prohibition on mocks, cassettes, stitched traces, manual repair, and host fallback.

### 8.5 Is M-4 the correct next proof?

**Yes, after M-3C.** Do not replace the real coding E2E; it is the correct foundation stop. But first run a narrow composition stress test because otherwise M-4 proves only the legacy coding runtime.

---

## 9. Composition expressiveness probes

| Algorithm / domain | Current status | Required extension | Universal-loop implication |
|---|---|---|---|
| Coding harness | Expressible and partially executable on legacy path | Move to v2 activation; real M-4 environment | Unary loop adequate for foundation. |
| Table manipulation | Parseable, not canonically composable | Domain adapter provider in composition | Strong immediate non-code probe. |
| Formal mathematical proof | Planned only | Formal environment, checker/evaluator, witness schema | Unary loop adequate for first proof pack. |
| Critic/reviser | Expressible as sequential roles only through custom planner | First-class topology state and role-attributed trajectory | Can lower to sequential scheduler. |
| Planner/executor/verifier | Partly expressible, behavior hidden in planner/session | Typed role ports and graph-owned transitions | Sequential lowering acceptable. |
| Hierarchical decomposition | Not active | `agent.spawn` effect and parent/child lineage | Requires logical-agent abstraction. |
| Bounded tree search | Not honestly expressible as declarative graph today | Search-state/checkpoint contract and scheduler | Not one opaque episode loop. |
| Debate/aggregation | Only as monolithic plugin | Multiple logical trajectories and aggregation evidence | Scheduler/topology must be explicit. |
| Evolutionary search | Research scaffolding only | Population/candidate archive, exterior fitness, budgeted scheduler | Exterior experiment controller. |
| Research workflow | Not product-proven | Retrieval/tool adapters, citation evidence, long-running workflow state | Likely DAG/event-driven topology. |
| Deterministic workflow + LLM policy | Architecturally plausible | Separate deterministic controller from LLM decision activity | Strong fit for event protocol. |
| Multi-agent coordination | Deferred | spawn, claims, leases, cancellation, backpressure | Requires scheduler beyond EpisodeEngine. |
| Hybrid symbolic/LLM | Plausible through ports | Typed symbolic worker and verifiable witness | Good polyglot probe. |

The minimum lesson is that **effects can remain universally mediated while control topology becomes plural**.

---

## 10. Plugin and component boundary map

| Mechanism | Correct home | Trust class | Replaceability |
|---|---|---|---|
| Canonicalization, digest verification | Domain reference implementation | Permanently trusted | Polyglot only after vector parity. |
| Capability/grant/reference monitor | Kernel | Permanently trusted | Replace only by formally equivalent TCB. |
| Event envelope and lineage validation | Domain/runtime boundary | Trusted infrastructure | Wire-compatible implementations allowed. |
| Ledger writer | Runtime | Trusted first-party | Store adapter replaceable; single-writer semantics fixed. |
| Scheduler | Runtime policy | Trusted first-party, selectable policy | Replaceable behind scheduling contract. |
| Planner/context/memory/toolkit | Components/plugins | Untrusted or pack-trusted | Freely replaceable per composition. |
| Model gateway/router | Port + adapter/policy | External service or adapter | Replaceable; identity/cost recorded. |
| Environment | Port + adapter | Untrusted external state | Replaceable with capability ceiling. |
| Sandbox worker | Adapter/process | Trusted containment infrastructure | Replaceable after conformance. |
| Evaluator | Exterior process/service | Independent trusted authority | Oracle-specific, signature-bound. |
| Approval policy | Runtime policy | Trusted first-party or explicit operator service | Selectable, absence recorded. |
| Retrieval/skills/macros | Plugins/exterior lab | Experimental | Replaceable and benchmarked. |
| Promotion controller | Exterior governance service | Trusted, never agent-owned | Replaceable only with audit parity. |

Typed bindings should name **versioned interfaces**, not Python classes. A useful minimum descriptor is:

```text
interface_id + version_range + request_schema + response_schema
+ error taxonomy + cancellation + idempotency + streaming mode
+ capability requirements + lifecycle contract
```

The WebAssembly Component Model is a relevant design reference: WIT interfaces define explicit imports and exports and a canonical ABI, allowing components to interact only through declared contracts ([interfaces](https://component-model.bytecodealliance.org/design/interfaces.html), [worlds](https://component-model.bytecodealliance.org/design/worlds.html)). AETHER need not adopt WASM now, but its SPIs should be precise enough that a WIT/gRPC/JSON-RPC realization is mechanically derivable later.

---

## 11. Trust, authority, evidence, and flexibility map

| Concern | Must remain trusted | May vary per composition | Absence semantics |
|---|---|---|---|
| Authority | Grant verification, attenuation, point-of-effect decision | Requested capabilities and approval policy | No grant = deny. |
| Budget | Reservation/settlement conservation | Ceiling and allocation strategy | Unspecified dimension = no authority, not infinity. |
| Identity | Canonicalization and digest rules | Component/config/model/environment inputs | Missing identity = non-promotable. |
| Evidence | Event lineage, receipt binding, signature verification | Oracle and assurance policy | No evaluator must be declared and non-promotable. |
| Isolation | Enforcement and attestation semantics | Isolation tier per component | No isolation is explicit trust, never implied sandbox. |
| Provenance | Envelope chain and writer identity | Source components and datasets | Missing lineage = unknown. |
| Approval | Grant issuance rules and operator identity | Interactive/noninteractive policy | Benchmark mode never auto-approves. |
| Promotion | Exterior comparison and immutable pointer update | Experiment policy | No controlled comparison = no promotion. |

This preserves strong guardrails without forcing every domain to use coding-specific policies. Guardrail mechanisms remain available as trusted services; the composition chooses assurance level, and absence is represented as data.

---

## 12. Runtime, recovery, performance, and scale

### 12.1 Logical agent versus worker

Do not equate an agent with a process. A logical agent is durable state plus authority, budget, policy, and lineage. A worker is a leased executor. This distinction is mandatory for cold reconstruction, process replacement, concurrency, and polyglot execution.

### 12.2 Scheduler ownership

The scheduler belongs in trusted runtime infrastructure but outside the kernel. It may decide readiness, leasing, retry, cancellation, and backpressure; it may not authorize effects or mint budget. Every scheduling decision that affects reproducibility must be evented.

### 12.3 Current scale risks

- SQLite WAL is appropriate for a single-node reference runtime but will face writer contention under M-7.
- Per-event canonicalization and signing can become significant; batch/segment signatures should be measured, not assumed.
- UDS/JSON-RPC is acceptable for coarse plugin calls but expensive for token streaming or high-frequency context access.
- In-process calls should remain zero-copy for trusted components; forcing every component through serialization would impose unnecessary latency.
- Plugin startup per episode may dominate short tasks; lifecycle scopes should support process reuse only with explicit state reset and identity.
- Cancellation and backpressure are not yet first-class across model, plugin, environment, and evaluator ports.
- The default `:memory:` store hides persistence cost and must never be used for release benchmarks.

### 12.4 Measurements required before concurrency

Record separately:

- model queue, time-to-first-token, generation, and retry latency;
- scheduler queue and coordination latency;
- component IPC calls, bytes, serialization CPU, and cold-start time;
- ledger append batch size, fsync latency, WAL size, and lock wait;
- sandbox setup and command execution latency;
- evaluator queue, execution, and signature verification latency;
- critical path versus aggregate work;
- cancellations, duplicate attempts, leases expired, and recovered work;
- cost per externally signed pass, not cost per model response.

OpenTelemetry semantic conventions provide a useful interoperability model for stable names across traces, metrics, logs, and resources ([OpenTelemetry semantic conventions](https://opentelemetry.io/docs/concepts/semantic-conventions/)). AETHER should define an `mhf.*` convention and export it, while keeping the ledger as truth rather than treating telemetry as authority.

---

## 13. Polyglot migration strategy

Python should remain the semantic reference through v1.0. Polyglot replacement should occur process by process, never by translating the entire repository.

### 13.1 Required portability boundary

For every replaceable process, freeze:

- versioned request/response/event schemas;
- canonical JSON/JCS and digest vectors;
- explicit integer/time/unit rules;
- error codes and retryability;
- cancellation/deadline behavior;
- idempotency and duplicate-delivery semantics;
- capability ceiling representation;
- lifecycle state machine;
- signature algorithm and preimage;
- golden success/failure/recovery transcripts;
- differential replay harness.

### 13.2 Candidate order

| Order | Candidate | Likely language | Reason |
|---:|---|---|---|
| 1 | Sandbox worker | Rust | Security-sensitive process boundary; system-call and resource control. |
| 2 | Plugin worker/sidecar | Rust or Go | Clear RPC/lifecycle boundary and crash containment. |
| 3 | Evaluator service | Rust/Go/Python | Independent deployment and signature contract. |
| 4 | Telemetry collector | Go/Rust | High-throughput exterior service, low semantic authority. |
| 5 | Model gateway | Go/TypeScript/Rust | Streaming/network concurrency behind stable port. |
| 6 | Scheduler/registry broker | Rust/Go | Only after event/lease semantics are proven in Python. |
| 7 | SDK/CLI clients | TypeScript/Rust | Naturally client-side; no authority logic duplicated. |
| Last | Kernel/reference reducer | Python reference retained | Highest semantic and security risk; replace only with differential equivalence. |

### 13.3 Equivalence gate

A replacement is acceptable only if Python and candidate implementations produce identical canonical outputs, digests, decisions, error codes, and reconstructed state for the same vectors, including adversarial malformed input and crash-boundary transcripts.

---

## 14. Data, trajectory, experimentation, and metacognition

The current trajectory work is directionally strong because it captures composition, execution, task, costs, events, and verdicts. But scientifically defensible improvement requires a stricter experiment envelope:

```text
ExperimentSpec
  = task-set digest
  + candidate/control D_H
  + runtime D_R
  + dataset/protocol D_X
  + preregistered metric and stopping rule
  + paired assignment
  + exterior verdict policy
  + resource ceiling
```

### 14.1 Readiness by capability

| Capability | Readiness | Missing proof |
|---|---|---|
| Trajectory analysis | Medium-high | Canonical v2 activation identity in real runs. |
| Cost/routing calibration | Medium | Complete provider usage and queue/latency decomposition. |
| Prompt/component attribution | Medium | Controlled interventions; repeated components and binding attribution. |
| Retrieval evaluation | Low-medium | Rebuildable index identity and held-out retrieval benchmark. |
| Skill extraction | Low | Proven source attribution, contamination controls, rollback. |
| Preference datasets/DPO | Low | Stable tasks, unbiased pair generation, versioned policy and provenance. |
| Candidate harness archive | Medium | Canonical frozen graph and artifact retention policy. |
| Promotion/rollback | Low-medium | Immutable pointer service, preregistration, production rollback drill. |
| Metacognitive agents | Research-only | Reliable calibration, causal credit, non-self-authored evaluation. |

Self-refinement and verbal-memory methods demonstrate that feedback/refinement loops can improve outputs, but they do not establish safe self-improvement. ReAct interleaves reasoning and actions ([paper](https://arxiv.org/abs/2210.03629)); Reflexion converts external feedback into episodic verbal memory ([paper](https://arxiv.org/abs/2303.11366)); Self-Refine iterates model feedback and revision ([paper](https://arxiv.org/abs/2303.17651)). These are candidate policies for experiments, not substrate law. SWE-agent further shows that agent-computer interface design materially affects results ([paper](https://arxiv.org/abs/2405.15793)); therefore tool/context interface versions must enter attribution.

### 14.2 Future self-improvement architecture

1. **Candidate generator** proposes a new composition/artifact set; it has no promotion authority.
2. **Static admission** validates schema, authority ceiling, identity, isolation, and policy constraints.
3. **Experiment service** preregisters paired tasks, metrics, budget, and stopping rules.
4. **Execution service** runs control and candidate under attributable identities.
5. **Exterior evaluator** signs task outcomes independently.
6. **Analysis service** computes paired effects, calibration, cost, safety, and failure strata.
7. **Governance service** decides promotion against explicit thresholds.
8. **Pointer store** atomically promotes an immutable candidate digest and retains rollback target.
9. **Canary monitor** compares online behavior and triggers tested rollback.

No component may occupy generator, evaluator, and promoter roles in the same trust domain.

VFE/EFE is one possible future policy formalism, not a necessary v1.0 foundation. The durable achievement is the controlled experiment and reversible promotion substrate.

---

## 15. Minimum benchmark lattice

The generality claim must vary one dimension at a time.

| Axis | Minimum controlled comparison | Pass criterion |
|---|---|---|
| Domain | Coding vs deterministic table/formal task | Same frozen/activation/runtime machinery; zero domain/kernel/episode diffs. |
| Topology | Direct ReAct vs critic/reviser | Manifest/policy change only; role-attributed events and costs. |
| Model | Two providers/models | Same task/composition except route; complete measured identity. |
| Evaluation | Exterior oracle A vs B or none | Absence is explicit; no false promotability. |
| Recovery | uninterrupted vs kill/restart | Same terminal state, no repeated settled effect, complete trajectory. |
| Delegation | single agent vs one child | Monotonic authority/budget/depth and parent-child lineage. |
| Concurrency | sequential vs bounded parallel | Equivalent results; no duplicate effects; measured speed/cost trade-off. |
| Polyglot | Python vs one Rust/Go worker | Golden-vector and differential replay equivalence. |
| Promotion | control vs candidate + rollback | Preregistered paired test and successful rollback drill. |

### Minimum meta-framework proof

AETHER may call itself a meta-framework when all of the following are true:

1. one public runtime executes canonical v2 graphs;
2. coding and one non-coding formal/deterministic domain run without trusted-core changes;
3. at least three topologies run without kernel or episode-protocol changes;
4. model and evaluator policies are independently substitutable and attributable;
5. recovery preserves complete trajectories and exactly-once settlement;
6. one component has a conformant polyglot implementation;
7. a candidate composition can be compared, promoted, and rolled back without self-authored evidence.

---

## 16. Revised roadmap to v1.0.0

| Milestone | Revised outcome | Mandatory gate |
|---|---|---|
| **M-3C / v0.6.2** | Canonical composition convergence | v2 code + non-code activation through one runtime; legacy authority retired; lifecycle/identity/recovery integrated. |
| **M-4 / v0.6.3** | Honest coding foundation E2E | Existing nine rows, derived from one real uninterrupted lineage with durable store and exterior evaluator. |
| **M-5 / v0.7.0** | Formal second-domain proof | Math/formal pack; zero trusted-core/episode changes; verifiable witness and parity matrix. |
| **M-6 / v0.8.0** | Mediated delegation | `agent.spawn` as effect; attenuated child identity/authority/budget; kill/recovery tests. |
| **M-7 / v0.9.0** | Scheduler and bounded concurrency | Claims/leases/cancellation/backpressure; sequential equivalence and measured Pareto benefit. |
| **M-8 / v0.9.x** | Explicit topology layer | Direct, critic/reviser, debate/aggregation, bounded tree; no kernel change; topology state observable. |
| **M-9 / v1.0 RC** | Retrieval/skills + polyglot conformance + experiment service | Held-out lift, rebuild equality, one polyglot worker, controlled candidate archive. |
| **M-10 / post-1.0 research** | Governed adaptive policy research | Only after v1 operational criteria; reversible, exterior-evaluated experiments. |

This deliberately moves “metacognition” out of the v1.0 definition. A framework can be operationally mature without implementing one speculative cognitive theory. v1.0 should certify substrate contracts, not research ambition.

### Operational definition of v1.0.0

v1.0.0 means:

- stable versioned public schemas and compatibility policy;
- one canonical composition/activation/runtime path;
- two domains and three topologies proven;
- durable replay/recovery and bounded delegation/concurrency;
- exterior evidence and promotion/rollback workflow;
- measured performance envelopes and security threat model;
- one polyglot conformance proof;
- installation, CLI/API, observability, and release operations suitable for independent users;
- no known P0/P1 contradiction between law, code, tests, and release metadata.

It does **not** require autonomous self-modification, VFE/EFE, DPO, evolutionary search, or general intelligence.

---

## 17. Prioritized action plan

| Priority | Action / owner | Affected modules | Dependency | Complexity | Principal risk | Acceptance test / falsifier | Timing |
|---:|---|---|---|---:|---|---|---|
| P0 | Freeze M-4; authorize M-3C / Chief Architect | `SPEC`, sprint board, milestones | Review acceptance | S | Status churn | CI asserts one active milestone/version | Day 0 |
| P0 | Add red canonical-path test / Runtime Lead | `test/runtime`, `test/contracts` | None | S | Weak test fixture | `Runtime.compose(v2_code)` and `Runtime.compose(v2_table)` both activate; current main must fail first | Day 1 |
| P0 | Define normalized `FrozenComposition` + `ActivationPlan` / Domain+Runtime | `domain/artifacts/manifest.py`, `runtime/registry/compiler.py`, new/existing runtime value module | Red test | M | Digest migration | Golden `D_H`; unknown/unconsumed fields fail; activation data complete | Week 1 |
| P0 | Converge public runtime / Runtime Lead | `runtime/compose.py`, `root.py`, `wiring.py`, `registry/*` | ActivationPlan | L | Split cleanup/failure semantics | One lifecycle and one emitter lineage; fault injection at every transition | Weeks 1–2 |
| P0 | Convert code pack to v2 / Pack Owner | `agency/manifests/vg-code-default`, `packs/code-default` | Canonical runtime | M | Behavior drift | Differential legacy/v2 effects and `D_H` mapping; then delete legacy authored form | Week 2 |
| P0 | Activate non-code probe / Adapter Owner | table adapter, pack, binding provider | Canonical runtime | M | Smuggling domain logic into runtime | Zero changes to domain/kernel/episode; end-to-end table task and exterior deterministic verdict | Week 2 |
| P0 | File-backed M-4 runner / Reliability Owner | `runtime/root.py`, E2E tooling, store config | Composition convergence | M | Tests accidentally using product defaults | Fresh interpreter reopens DB, resumes, and produces same complete trajectory | Week 2 |
| P0 | Evidence derivation / Evidence Owner | `domain/evidence/audit.py`, runner/attestation adapters | File-backed run | M-L | Attested booleans remain forgeable | Mutating any source digest or row binding fails audit | Weeks 2–3 |
| P1 | Remove legacy composition authority / Runtime Lead | legacy parser/types/loader paths | Parity gates | M | Hidden test consumers | No production import; duplicate authority linter; all suites green | Week 3 |
| P1 | Clean Linux M-3C gate / Release Engineer | CI/workflows/containers | All P0 | M | Namespace/UID portability | UDS, bwrap, evaluator UID, crash cleanup, full suites green from clean clone | Week 3 |
| P1 | Execute M-4 / Release+Evidence | provider/evaluator environment | M-3C closed | M | Human/trace contamination | Existing nine-row contract from one run; independent audit | Week 4 |
| P1 | Property/mutation tests for selectors and budgets / Security | kernel/domain tests | Stable M-3C | M | State-space gaps | Random attenuation never widens; mutation score threshold | Post-M-4 |
| P2 | Formal Pack #2 / Formal Methods Lead | pack, environment/evaluator adapters | M-4 | L | Checker identity ambiguity | Verifiable witness bound to toolchain/input/policy | M-5 |
| P2 | Scheduler protocol / Runtime Research | ports/runtime/ledger | M-5/6 | L | Exactly-once illusion | At-least-once execution + idempotent settlement; kill/fuzz tests | M-7 |
| P3 | Polyglot worker / Systems Lead | schemas/vectors/worker | Stable protocol | L | Semantic drift | Differential transcript/replay equivalence | M-9 |

### Recommended ownership rule

No developer should simultaneously own the component implementation and its only acceptance oracle. Runtime, security/evidence, pack, and release validation should have distinct reviewers even in a small team.

---

## 18. Decisions to keep frozen

1. Domain-blind trusted kernel.
2. S0–S12 mediation for authority-bearing effects.
3. Monotonic capability and budget attenuation.
4. Single canonical writer and append-only durable event truth.
5. Exterior, signed, independently bound evaluation for promotion.
6. JCS/golden-vector identity and distinct `D_H`/`D_R`/`D_X`.
7. Missing evidence is unknown/absent, never a fabricated pass or zero.
8. No mock/cassette/manual repair for M-4.
9. Sequential execution as the foundation reference baseline.
10. Python reference semantics until cross-language parity is proven.
11. Coding behavior outside domain/kernel.
12. Release gates based on falsifiable evidence, not document status.

---

## 19. Decisions to reopen

1. **M-3 completion status** — syntax/contract completion is not runtime completion.
2. **One composition path claim** — currently false; redefine and enforce.
3. **Universal turn-loop interpretation** — retain effect protocol, reopen topology implementation.
4. **Five fixed SPI kinds** — validate against topology/domain probes; allow versioned interface registry without ontology explosion.
5. **Global `DEFAULT_BINDINGS` ownership** — move domain bindings out of runtime core.
6. **Manifest compatibility duration** — set a short deletion deadline and explicit digest mapping.
7. **M-4 runner defaults** — file-backed durability must be release default.
8. **v1.0 = M-10 metacognition** — replace with operational substrate criteria.
9. **Profile schema semantics** — keep identity reservation, defer executable semantics until measurements.
10. **TCB assurance metric** — supplement LOC with complexity, property, mutation, and differential testing.

---

## 20. Features to reject or defer

### Reject as architectural direction

- a new privileged engine per topology;
- “everything is a plugin,” including canonicalization, authority, ledger truth, and promotion;
- embedding code-domain verbs or artifact semantics in domain/kernel;
- treating a planner plugin as a hidden scheduler for all future algorithms;
- auto-promotion based on self-evaluation;
- mutable “latest” component references in attributable runs;
- opaque scalar rewards that combine safety, cost, and quality;
- claims of exactly-once physical execution across crashes; require idempotent effects and exactly-once settlement instead;
- a whole-platform Rust rewrite before wire conformance exists.

### Defer

- `agent.spawn` until second-domain composition is proven;
- concurrency until sequential recovery and lease measurements are stable;
- tree/debate/evolution until an explicit topology-state contract exists;
- semantic retrieval and macro promotion until held-out evaluation and provenance exist;
- DPO and trajectory learning until selection bias and experiment identity are controlled;
- VFE/EFE as product architecture; keep as an experimental policy candidate;
- automatic irreversible self-modification indefinitely.

---

## 21. Direct answers

### What would prevent AETHER from becoming state of the art?

Dual architectural truth, especially a graph that is audited but not executed; coding-specific wiring in runtime core; treating the universal effect loop as universal control flow; accepting self-asserted evidence fields; and moving into delegation/concurrency/metacognition before composition and causal attribution are real.

### What must change before M-4?

The v2 graph must become the public runtime’s sole frozen/activated composition, code and one non-code probe must run through it, lifecycle must share the run lineage, persistence must be file-backed for E2E, and evidence rows must be derived and digest-bound.

### What must not change before M-4?

Kernel authority semantics, attenuation, reservation/settlement, canonical identities, exterior evaluator isolation, single-writer ledger, sequential execution, and the uncompromised nine-row prohibition on synthetic evidence.

### Is M-4 the correct next proof?

Yes, but only after the short M-3C convergence gate. Running it before convergence proves the wrong composition path.

### What should wait until a second domain proves generality?

Spawn, concurrency, topology builders, retrieval scale, macros, training, and metacognitive policies.

### What is the minimum meta-framework proof?

One canonical runtime, two domains, three composition topologies, substitutable model/evaluator policies, durable recovery, one polyglot component, and reversible exterior-evaluated promotion—without trusted-core changes per case.

### Which claims require new falsifiers?

- “one composition path”;
- “bindings drive runtime wiring”;
- “every component is lifecycle-owned”;
- “non-code packs need no trusted/runtime special case”;
- “M-4 evidence rows derive from canonical sources”;
- “file-backed restart preserves graph and trajectory identity”;
- “topologies require no new privileged engine”;
- “polyglot implementation is semantically equivalent.”

### What should v0.6.2 mean?

Canonical composition convergence: v2 graph, activation plan, registry lifecycle, code and non-code execution, legacy authority retirement, and M-4-capable durable/evidence wiring.

### What should v1.0.0 mean operationally?

A stable, independently usable, versioned meta-framework substrate with proven multi-domain/multi-topology composition, bounded delegation/concurrency, durable recovery, exterior evidence, polyglot conformance, and reversible promotion—not completion of speculative metacognition.

### Should the project proceed, be corrected, or be materially re-founded?

**Proceed with focused corrections.** Re-found the composition-to-activation seam, not the substrate.

---

## 22. Final decision and next authorized action

**Proceed with focused corrections.**

**Exact next authorized engineering action:** open a single M-3C “Canonical Composition Convergence” sprint and begin by adding a red end-to-end falsifier that requires both `vg-code-default` and `vg-table-default` canonical `mhf.manifest/2` graphs to compose and activate through the public `Runtime` with one registry lifecycle and zero changes to `vanguard/packages/domain/`, `vanguard/packages/kernel/`, or `vanguard/packages/agency/episode/`; do not execute M-4 or begin M-5 until that falsifier and its failure-path variants are green.


# BRIEFING

# Plano definitivo resumido — M-3C a M-8

A decisão central é não reescrever o AETHER integralmente. O Kernel e o Trust Spine já contêm mecanismos valiosos: autoridade S0–S12, atenuação de capabilities, budgets, reservation/settlement, identidades JCS, ledger append-only, recuperação, avaliação externa assinada e sandboxing rootless. O problema está na fronteira entre composição, ativação e runtime, onde coexistem uma arquitetura nova, baseada em `mhf.manifest/2` e registry, e um caminho legado que continua sendo o executado pelo produto.

O objetivo imediato é corrigir essa seam sem destruir a fundação. O projeto deve primeiro congelar a expansão, consolidar os conceitos, corrigir a documentação e apenas depois executar um refactor cirúrgico. M-3C, ou v0.6.2, será a milestone de convergência da composição canônica. M-4 só deve começar quando essa convergência estiver provada.

## Modelo arquitetural que deve ser congelado

O AETHER deve ser descrito em cinco planos. O Kernel ou Trust Spine governa autoridade, efeitos, capabilities, orçamento e settlement. O Runtime controla ativação, lifecycle, execução, persistência e recuperação. O Meta-Framework declara componentes, bindings, manifests, packs e políticas. O Meta-Harness executa experimentos, compara candidatos, atribui resultados e controla promoção e rollback. A Meta-Cognição propõe adaptações experimentais, mas não recebe autoridade automática para se promover.

O Coding Harness passa a ser formalmente o primeiro pack e laboratório do framework, não a definição do framework inteiro. A universalidade do sistema deve significar universalidade do protocolo de efeitos e evidências, não obrigatoriamente uma única topologia de controle para todos os algoritmos.

Devem permanecer congelados o Kernel domain-blind, o pipeline S0–S12, a atenuação monotônica, o reservation/settlement, o writer único do ledger, a avaliação externa, a identidade JCS, a separação entre `D_H`, `D_R` e `D_X`, a execução sequencial como baseline e a regra de que ausência de evidência nunca pode ser interpretada como aprovação. Devem ser reabertos o status real de M-3, o significado do universal loop, a propriedade de `DEFAULT_BINDINGS`, a duração da compatibilidade legacy, os defaults de persistência e a definição operacional de v1.0.

## Correção documental

Antes de alterar o código, deve ser criado um Architecture Baseline normativo, curto e inequívoco, contendo a ontologia dos cinco planos, as fronteiras de confiança, os invariantes congelados, os conceitos reabertos e os critérios de conclusão de cada milestone. Esse documento passa a orientar a SPEC, os ADRs, o roadmap e o backlog.

A SPEC deve registrar que M-3 possui contratos e componentes implementados, mas ainda não possui convergência operacional. Também deve descrever a cadeia canônica:

```text
Canonical Manifest
→ ComponentGraph normalizado
→ FrozenComposition
→ ActivationPlan
→ RunPlan
→ Episode ou Scheduler
```

Os ADRs não devem ser apagados quando uma decisão mudar. Cada decisão deve ser marcada como frozen, accepted, reopened, superseded, deprecated ou research-only, e qualquer alteração relevante deve criar um ADR sucessor.

O roadmap deve ser reescrito como uma sequência de resultados falsificáveis, e não como uma lista de features. O backlog deve ser reclassificado em preservação, convergência, generalização, substituição, adiamento, rejeição ou pesquisa. Cada item precisa declarar milestone, dependências, módulos afetados, risco, acceptance test, falsifier, evidência esperada e owner.

Também é necessário alinhar `pyproject`, README, AGENTS, SPEC, milestones, sprint ativo, changelog e tags. Um verificador de CI deve falhar sempre que versão, milestone e documentação normativa divergirem.

Os sprints históricos não precisam ser reescritos. Eles devem permanecer como registro do que ocorreu, enquanto os próximos são replanejados a partir de M-3C. Nenhum milestone futuro deve começar apenas porque seus schemas ou testes unitários foram criados.

# Wave 0 — Governance and Architectural Lock

A primeira wave congela M-4 e as features posteriores, aprova formalmente M-3C, estabelece a nova ontologia, revisa SPEC e ADRs, reorganiza o backlog e implementa a verificação automática de consistência documental. Seu resultado é uma única narrativa arquitetural, com claims ligados a código, testes e evidências.

# M-3C / v0.6.2 — Canonical Composition Convergence

M-3C corrige a fundação. Seu primeiro sprint deve criar falsifiers E2E inicialmente vermelhos exigindo que `vg-code-default` e `vg-table-default`, ambos em `mhf.manifest/2`, sejam compostos e ativados pelo `Runtime` público. Também deve escolher uma única forma autoral de manifest, normalizar ingressos legados e definir `FrozenComposition` e `ActivationPlan` imutáveis. Os golden vectors devem provar a identidade `D_H`, campos não consumidos devem falhar e o prazo de remoção legacy deve ser explícito.

Em seguida, o runtime público deve deixar de chamar diretamente o caminho legado e passar a consumir apenas a representação canônica. O registry deverá controlar descoberta, verificação, inicialização, readiness, encerramento e falhas. Cada componente deverá iniciar e encerrar uma única vez, inclusive em cancelamentos, crashes, falhas de composição e erros do evaluator. Os lifecycle events e os eventos da execução precisam compartilhar a mesma lineage.

O pack de código deve ser migrado para v2 e um pack não-coding determinístico deve ser ativado pelo mesmo mecanismo. Os verbs de código devem sair do runtime global e passar a pertencer ao pack ou aos adapters correspondentes. `DEFAULT_BINDINGS` deve ser substituído por binding providers namespaced, limitados por ports e interfaces confiáveis. As superfícies duplicadas de packs devem ser consolidadas, e o caminho legacy só poderá ser removido depois de differential parity.

A última etapa de M-3C torna o runner de release persistente. O uso de `:memory:` deve permanecer limitado a testes. O E2E precisa usar SQLite file-backed com WAL, permitir reabertura por novo processo e preservar composição, identidade e trajetória. As evidências devem ser derivadas de registros canônicos e possuir cross-digests; campos booleanos autoafirmados não são suficientes. A conclusão exige clean-clone gate em Linux com UDS, namespaces, Bubblewrap e evaluator separado.

M-3C estará concluído somente quando houver um manifest canônico, uma `FrozenComposition`, um `ActivationPlan`, um registry lifecycle integrado, execução coding e non-coding, recuperação persistente, evidência vinculada e nenhum authority path legado em produção.

# M-4 / v0.6.3 — Honest Coding Foundation E2E

M-4 não deve adicionar nova arquitetura. Ele deve provar a existente em uma execução real. O ambiente precisa fornecer modelo ou provider real, evaluator externo e identidades separadas. O Coding Pack v2 deve executar por uma única lineage persistente, produzir as nove evidências exigidas e vinculá-las aos artefatos imutáveis correspondentes.

A execução deve demonstrar assinatura, enforcement no ponto de efeito, isolamento sem host fallback, cold restart, ausência de efeitos duplicados e recuperação consistente. Uma auditoria independente deve validar o bundle. Property tests para selectors e budgets, mutation testing do Trust Spine e uma baseline de latência, custo, tokens, I/O e recovery devem completar a certificação.

M-4 só estará concluído quando o run real provar o caminho canônico inteiro, sem mocks, cassettes, traces montados ou reparos manuais.

# M-5 / v0.7.0 — Second-Domain Generality Proof

M-5 prova que AETHER não é apenas um coding runtime. Deve introduzir um Formal Pack, como matemática, SMT ou verificação formal, com environment adapter próprio e evaluator determinístico externo. O witness deve ser vinculado ao input, à toolchain e à policy.

O novo domínio deve usar a mesma composição, ativação, runtime, recovery e evidence lineage, sem alterações em domain, kernel ou episode protocol. Uma parity matrix entre Coding e Formal deve demonstrar que as diferenças residem nos packs e adapters, não no substrate. Esse milestone também deve consolidar o contrato mínimo do Pack SDK.

# M-6 / v0.8.0 — Mediated Delegation

M-6 introduz `agent.spawn` como efeito governado, não como chamada privilegiada interna. A identidade filha deve ser derivada da identidade pai, com atenuação obrigatória de autoridade, orçamento, profundidade e fan-out. A lineage pai-filho, o `RunPlan`, os custos e os settlements precisam ser persistidos.

O sistema deve recuperar árvores parcialmente executadas, testar crashes antes e depois do settlement, impedir ciclos e spawn storms e aplicar cancellation trees e quotas. Nenhum filho pode contornar S0–S12 ou aumentar as permissões herdadas.

# M-7 / v0.9.0 — Scheduler and Bounded Concurrency

M-7 separa agente lógico, worker e scheduler. Deve definir work items, ready-set, claims, leases, expiry, reclaim, idempotency keys, deadlines, cancelamento, backpressure e fairness. A execução física deve ser tratada como at-least-once, enquanto o settlement precisa ser exatamente uma vez.

O scheduler deve persistir decisões, suportar kill e fuzz testing durante claims e settlement e tornar visíveis queue latency, wait time e contention. A execução concorrente deve ser comparada à baseline sequencial, demonstrando equivalência de resultados, ausência de efeitos duplicados e benefício mensurável em qualidade, custo ou latência. Sem ganho Pareto comprovado, concorrência não deve virar default.

# M-8 / v0.9.x — Explicit Topology Layer

M-8 transforma a composição em meta-framework operacional. Deve definir `TopologySpec`, estado explícito de nós e edges, policies de término e agregação e persistência da topologia. O sistema deve suportar Direct, Critic/Reviser, Planner/Executor/Verifier, Debate/Aggregation e bounded tree search.

Essas topologias devem usar o mesmo protocolo de efeitos, runtime e Trust Spine, sem criar engines privilegiados ou esconder o scheduler dentro de um planner plugin. Custos, papéis, decisões, falhas e recuperação precisam ser observáveis. Pelo menos três topologias devem ser comparadas no mesmo benchmark, usando modelos e evaluators substituíveis e identities atribuíveis.

# Horizonte M-9 e M-10

M-9 permanece como horizonte para retrieval com provenance, skills reproduzíveis, conformance polyglot, experiment service, candidate archive e promoção com rollback. O trabalho atual deve apenas preservar schemas versionados, identidades portáveis e eventos language-neutral.

M-10 fica como pesquisa pós-v1 para adaptação governada, geração de candidatos, causal attribution, policy learning e metacognição. VFE/EFE, DPO, autopromotion, evolutionary search produtivo e self-modification irreversível não devem entrar agora no produto.

# Regra final de execução

O próximo passo único é abrir M-3C e começar pelo falsifier E2E vermelho de composição e ativação para código e tabela. Até ele ficar verde, M-4, M-5, `agent.spawn`, concorrência, topologias e metacognição devem permanecer bloqueados.

A trajetória correta é:

> corrigir conceitos e documentação, convergir composição e ativação, eliminar o caminho legacy, provar M-4, validar generalidade em M-5 e só então adicionar delegação, concorrência e topologias em M-6–M-8.
