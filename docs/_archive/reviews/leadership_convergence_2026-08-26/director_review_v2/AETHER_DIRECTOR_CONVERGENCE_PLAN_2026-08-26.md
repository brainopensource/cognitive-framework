# AETHER — Director Convergence, Concept Lock and MVP Delivery Plan

**Audit date:** 2026-08-26  
**Repository:** `brainopensource/cognitive-framework`  
**Branch:** `feat_higgs_M4_M8`  
**Audited HEAD:** `624d80fb428bee50a6610b18fd7736f6d316eb36`  
**Decision horizon:** convergence now; delivery through M-8; M-9/M-10 remain non-authorizing horizons  
**Authority:** Director assessment and execution recommendation; becomes binding only when its decisions are ratified into the canonical triad

---

## 1. Executive decision

The architectural foundation is strong and must be preserved. There is no justification for a rewrite, a second runtime, a larger Kernel, or a new mandatory “metacognition layer”. The accepted lattice remains:

`domain ← ports ← kernel ← agency ← runtime → adapters`

The branch, however, is **not ready to be treated as a scientifically closed M-4…M-8 program state**. It contains substantial, generally good implementation work, but the evidence chain, baseline provenance, canonical status board, document topology, and milestone acceptance semantics have diverged from the code and from each other.

**Director verdict:**

- **GO** for a short convergence and evidence-restoration phase.
- **NO-GO** for claiming M-5b, M-6.5, M-7, or M-8 closed.
- **M-4 remains provisionally accepted for continued development, not evidence release.**
- **M-5a implementation is strong, but its experimental baseline is not validly available from the remote.**
- **M-6 is package-ready and technically credible, but its milestone evidence/review gate remains open.**
- **M-9/M-10 implementation must not start before M-8 closes.** Their constraints may be preserved in Vision/milestones only.

The shortest honest path to the MVP is not more feature work. It is to restore one chain of authority and proof, then execute four bounded blocks: M-5b revalidation, M-6.5 experiment, M-7 runtime integration/decision, and M-8 durable memory plus measured promotion.

---

## 2. Audit scope and method

The remote branch was cloned and verified at the exact requested commit. The working tree remained clean during review.

Reviewed inputs:

1. Production code under `vanguard/packages/`.
2. Schemas under `schemas/mhf/`.
3. Tests and falsifiers under `test/`.
4. Experimental instruments under `lab/`.
5. Canonical authority: root `VISION.md`, `docs/SPEC.md`, `docs/01_law/`, accepted ADRs, `docs/03_execution/milestones.md`, and `docs/03_execution/sprint_active.md`.
6. Descriptive contracts and architecture under `docs/04_architecture/` and `docs/05_contracts/`.
7. The complete `docs/00_leadership_supersede_all/` package, including `masterplan_todo_rev1.md`.
8. `sprint_doing_v2.md` and the new `sprint_doing_v2B.md`.
9. Git history from the masterplan baseline `f9d7ceb` to `624d80f`, including commit content rather than commit labels.
10. Remote tags and executable gates.

The attached Leadership files are byte-identical to the copies under `docs/00_leadership_supersede_all`, except the attached `VISION.md`, which is older than the repository Vision. The repository root Vision v0.7.1 is therefore the current constitutional source.

---

## 3. Independently executed evidence

### 3.1 Provenance and repository state

| Check | Result |
|---|---|
| Remote branch | `feat_higgs_M4_M8` resolves to `624d80f...` |
| Local checkout | Exact commit, clean working tree |
| Remote `M-5A-BASE-v2` | **Absent** |
| Remote historical `M-5-BASE` | Present |
| Provider keys in audit environment | Unset |
| Secret scan | Pass |

### 3.2 Static and contract gates

| Gate | Result |
|---|---|
| Boundary lattice | PASS, 321 source files |
| Kernel TCB directory budget | PASS, 1,373 / 1,438 logical LOC |
| Domain blindness | PASS |
| Isolation policy | PASS in available checks |
| Duplication | PASS |
| Markdown links | PASS |
| Stale paths linter | PASS, but it does not detect semantic status drift |
| Code generation | PASS |
| Event coverage | PASS |
| RF identifier allocation | PASS |
| Python compileall | PASS; one unrelated SyntaxWarning under desktop tooling |
| RF-86 | **FAIL-CLOSED: `M-5A-BASE-v2` does not resolve** |

### 3.3 Focused test evidence

| Surface | Result |
|---|---|
| Kernel | 94/94 pass |
| Agency | 105/105 pass |
| Packs | 39/39 pass |
| M-5a event/replay/checkpoint/authority/profile/trajectory | 90/90 pass |
| M-6 delegation + M-8 promotion/rollback mechanisms | 65/65 pass |
| M-6.5 statistical/controller contracts | 61/61 pass |
| M-7 analyzer/topology/lowering units | 33/33 pass |
| Contracts discovery | 274 effective passes, 3 errors |

The three contract errors separate into two categories:

- Two UDS lifecycle errors are caused by this audit sandbox refusing `AF_UNIX`; they must be rerun on qualified Linux and are not evidence of a product defect by themselves.
- `test_m5a_schema_vectors` cannot import `jsonschema`. This **is a repository dependency defect**: CI installs `.[dev]`, but `[project.optional-dependencies].dev` declares only `pytest`, while the test imports `jsonschema`. The CI is not hermetically reproducible from declared dependencies.

The full suite was attempted with provider keys unset. It could not produce an admissible final result in this restricted environment because the UDS tests fail at socket creation and several long integration cases did not terminate within the audit window. The branch's stated 1,781/1,786 counts are therefore not independently re-certified by this report. They remain prior evidence, not this audit's evidence.

TypeScript gates were not rerun because the fresh clone has no installed npm dependencies and the available environment could not fetch them. No TypeScript pass claim is made here.

---

## 4. Assessment of `sprint_doing_v2B.md`

The report has good instincts: it correctly refuses closure by prose, distinguishes package readiness from milestone evidence, preserves Kernel neutrality, identifies the missing remote tag, and correctly treats M-6.5 and M-8 as unmeasured. It is a useful handoff input.

It is not an authoritative execution plan and requires correction before use.

| Item | Director disposition | Reason |
|---|---|---|
| D-1 RF-86 red | **Partially accepted** | RF-86 is red because the tag is absent remotely. The claimed post-tag diff cannot be independently reconstructed because the tag object/commit is unavailable. |
| D-2 tag local-only | **Accepted** | Confirmed by `git ls-remote --tags origin`. |
| D-3 exposed provider key | **Unverified environment incident** | Repository secret scan passes and all provider variables are unset here. Rotate only if secret bytes reached logs/artifacts or the developer confirms exposure. Add hermetic preflight regardless. |
| D-4 commit mislabelling | **Accepted and broader than reported** | Numerous `docs(...)` commits contain large production/schema/test changes, not only `a92951d`. |
| D-5 selector/timing gap | **Rejected as written** | `EffectStarted` already carries `resource`, and the analyzer reads it. The canonical workload test expects one independent pair out of three. Timing is available from correlated event timestamps, though monotonic performance telemetry would improve rigor. |
| D-6 M-6.5 instrument absent | **Accepted** | No stochastic attributable provider or deliberately blockable task set exists. |
| Option A: create `M-5A-BASE-v2.1` | **Rejected as immediate remedy** | It would legitimize an unknown/possibly contaminated baseline without first recovering or adjudicating the original tag provenance. |
| M-7 proposal to add settlement data to `EffectStarted` | **Rejected** | An append-only event cannot be completed later. Kernel is already the sole writer. Timing should be a correlated telemetry observation or a separate authorized fact, not a mutation. |
| Stall-provider pseudocode | **Needs redesign** | It calls nonexistent `Result.ok`, references undefined helpers, and keys perturbation to turn index, which becomes incomparable once controller behavior changes the turn path. |

### Correct M-7 decision

No selector schema change is currently justified. `kernel/dispatch.py` has emitted the resolved request resource into `EffectStarted.payload.resource` since commit `e3311ba`, and `lab/m701_independence.py` reads `resource` or `selector`.

For the M7-01 decision:

1. Use the existing causal selector and sink data.
2. Rerun the canonical recorded workload on qualified CI.
3. Treat event envelope timestamps as ordering/approximate wall-time evidence only.
4. If monotonic duration is necessary, emit **correlated non-authoritative telemetry** at start and settlement, keyed by run/episode/idempotency/descriptor. Do not alter an existing event after append and do not add timing policy to Kernel.
5. Produce the M7-01 report and only then ratify ADR-0099.

---

## 5. Critical findings

### P0-01 — The canonical board contradicts itself

`docs/03_execution/sprint_active.md` says, at the same time:

- `M-5A-BASE-v2` does not resolve;
- creation/push of the tag is `DONE`;
- RF-86/RF-98 rerun is `DONE`;
- RF-86 is intentionally red until the tag exists;
- the immediate sequence still says to create the tag and run RF-86.

This destroys the board's function as sole execution authority. Status must be computed from receipts, not edited narratively in several sections.

### P0-02 — The M-5a experimental control is missing and likely contaminated

The remote has no `M-5A-BASE-v2`, and the repository does not record its intended commit digest. Git history also shows M-5b, M-6, M-6.5, M-7, and M-8 code landing in mislabelled `docs(...)` commits before the board later claimed the M-5a tag was created.

Examples before the alleged tag window include:

- formal SAT evaluator and delegation code in `67bbe0f`;
- memory, meta-controller, scheduler, topology, and lifecycle seams in `f99b015`;
- M-6.5/M-7/M-8 evaluators and tests in `3bab575` and `e3311ba`.

Therefore, even recovering a local tag is insufficient unless its target commit is inspected. A tag containing the treatment code is not a valid control for proving that the treatment required zero substrate change.

### P0-03 — M-4 is overclaimed

The branch contains a runner and a board claim that RF-95 passed. It does not contain the immutable evidence bundle or independent G-M4-05 review receipt. The board simultaneously marks the review `WAIVED — development only` and M-4 `CLOSED`.

Director correction: M-4 is **PROVISIONALLY ACCEPTED FOR DEVELOPMENT**. It becomes scientifically closed only when the existing bundle is recovered, digest-verified, and independently reviewed, or a newly preregistered one-candidate run is executed if the original bundle is unavailable.

### P0-04 — Leadership documentation became a second authority tree

The masterplan explicitly says it must stay outside the repository and must not coexist as a second active plan. It was nevertheless committed under `docs/00_leadership_supersede_all/` together with duplicated assessments, duplicated ADR-0097 candidates, obsolete specs, stale boards, and old terminology.

This conflicts with `AGENTS.md`'s anti-sprawl invariant and with the canonical triad. The directory name `supersede_all` is especially unsafe because a review folder cannot supersede Vision/Law/accepted ADRs.

### P0-05 — The new report is stale against its own HEAD

`sprint_doing_v2B.md` says it was verified at `a92951d`, but the file is delivered at `624d80f`. Its D-5 claim contradicts code already present before `a92951d`. It must be archived as a review input after accepted corrections are applied to canonical documents.

### P1-01 — CI dependency declaration is incomplete

`test/contracts/test_m5a_schema_vectors.py` imports `jsonschema`, but `pyproject.toml` does not declare it in the development dependencies. Add and lock the dependency, or replace the test with a declared/internal validator. CI must install only declared dependencies and remain reproducible from a clean runner.

### P1-02 — Descriptive documentation is materially stale

Examples:

- `AGENTS.md` and `README.md` still describe M-4 active and M-5a…M-8 planned.
- `docs/04_architecture/traceability_matrix.md` still says `ACTIVE_M3_CONVERGENCE`.
- `docs/05_contracts/trajectories.md` is titled only `mhf.trajectory/1` despite `/2` production support.
- `docs/05_contracts/README.md` still calls trajectory RF-23 repair active.
- `docs/05_contracts/selectors_and_budgets.md` presents an undifferentiated “6D budget”, while current law and code distinguish four additive dimensions from depth/turn ceilings.
- Leadership specs still use `digests-only`, `charged_millis`, `M-5-BASE` re-tagging, proposed ADR status, and `dev-C` ownership that the masterplan itself says must be removed.

The link/stale-path linter passes because it checks paths, not semantic consistency. Add a status/authority consistency linter.

### P1-03 — M-7 topology is a library mechanism, not a composed runtime capability

`parse_topology`, `lower_topology`, `SequentialScheduler`, and readiness tests are good isolated mechanisms. There is no production use of `RunPlanExtension` in `Runtime.compose`, `plan_run`, `HarnessSession`, or the root execution path. Three fixtures lowering through one function do not prove three topologies execute through one runtime.

### P1-04 — M-8 memory is capability-shaped, not capability-verified

`MemoryAccess.permitted()` accepts any nonempty `grant_ref`, tenant, and project. Tests use the literal string `"grant"`. No grant signature, selector attenuation, revocation registry, expiry, or authority source is verified. `InMemoryMemoryPort` is useful as a contract fake, but it is not production capability mediation.

M-8 needs an immutable `AuthorizedMemoryContext` derived from a verified Kernel grant/lease or an equivalent runtime authorization receipt. Durable adapters must recheck that context at read/write time.

### P1-05 — Evidence bundles are mostly tests, not release artifacts

M-5b signed vectors, M-6 nested lineage, M-6.5 studies, M7-01, and M-8 rollback have strong executable tests, but milestone claims need digest-addressed result bundles with run identity, protocol identity, input manifests, receipts, environment, and reviewer decision. Test success proves mechanism; it does not automatically create release evidence.

### P1-06 — Commit taxonomy and scope discipline are unreliable

The branch is roughly 40,925 additions across 315 files from `f9d7ceb`, mixing backend, frontend, research, generated corpora, SQLite data, docs, experiments, and milestone code. Many production changes are hidden under `docs(...)` subjects. Future review must be based on bounded PRs and mechanically checked commit/diff labels.

---

## 6. Concept lock

The following decisions are locked for implementation through M-8.

### 6.1 Ontology and layer boundaries

1. AETHER is a general event-sourced agentic computation substrate, not a coding-specific workflow engine.
2. The fundamental execution unit is a typed causal operation within an execution lineage.
3. Agent = identity + policy + event-derived projection + bounded execution scope.
4. Runtime is the single concrete composition seam.
5. Agency owns generic turn/context/proposal mechanics and has no upward dependency.
6. Kernel owns admissibility, capability authority, attenuation, and generic resource invariants only.
7. Packs own domain semantics.
8. Topology, scheduling, memory, learning, delegation strategy, and metacognition are derived capability families, never privileged layers.

### 6.2 Truth and evidence

1. Event = immutable causal fact.
2. Artifact = content-addressed immutable content; blob first, event second.
3. Projection = deterministic derived state, never a second truth.
4. Telemetry is correlated operational evidence, not ledger truth.
5. Capability is not verification; configuration is not execution; tests are not release evidence.
6. Evidence status is monotonic and receipt-backed: `ABSENT → PRODUCED → VERIFIED → INDEPENDENTLY_ACCEPTED`.
7. A milestone may close only at `GATE_ACCEPTED`; `PACKAGE_READY` and `MERGED` are not closure.
8. Missing/unknown values remain missing/unknown, never zero or pass.

### 6.3 Compatibility and baselines

1. `/1` schemas remain immutable; new writers use `/2`; readers dual-read.
2. A baseline tag must be annotated, pushed, immutable, and recorded with commit digest, tree digest, schema/reducer pins, gate receipts, creator, and review receipt.
3. A missing tag is not recreated under the same name.
4. A baseline containing the feature under test is scientifically contaminated.
5. A successor baseline requires a successor decision and a new name.

### 6.4 Resources and authority

1. Additive conserved dimensions are exactly `usd_micros`, `millis`, `tokens`, and `bytes`.
2. `depth` and `turns` are structural ceilings, not costs.
3. Raw goal content stays out of ledger truth; use digest plus authorized artifact reference.
4. Memory, retrieval, skill promotion, and topology cannot mint authority.
5. Generator, evaluator, and promoter are distinct identities and trust authorities.

### 6.5 Scientific methodology

Adopt the previously proposed **ADR-0101 “Graviton”** as the program-wide evidence methodology: every hypothesis, decision, experiment, negative result, counterfactual, variable set, seed, artifact, protocol version, code/tree digest, and promotion/rollback decision receives explicit provenance and machine-checkable status. It does not create a second event ledger; it defines evidence envelopes and projections over the existing substrate.

---

## 7. Baseline and evidence recovery decision

Do **not** immediately create `M-5A-BASE-v2.1`.

Execute this decision tree:

```text
Can the original local tag object and its annotated metadata be recovered?
  yes -> inspect exact target commit and receipts
           valid M-5a-only control -> push unchanged; run RF-86/RF-98
           contains M-5b/M-6/M-6.5/M-7/M-8 code -> preserve as contaminated history
  no  -> record M-5A-BASE-v2 as unresolved/lost provenance; never recreate it

If valid control is unavailable:
  converge current substrate -> create CONVERGENCE-BASE-v1 under successor ADR
  -> add a new materially different deterministic domain pack after that tag
  -> prove zero substrate semantic diff from the new baseline
  -> treat existing SAT run as engineering demonstration, not historical generality proof
```

This avoids expensive history surgery and produces a valid forward falsifier. A small deterministic graph-coloring witness pack is a good candidate: the generator proposes a complete coloring; an exterior evaluator checks every edge and color bound; no solver search occurs in the evaluator; the substrate must remain unchanged.

Ratify **ADR-0102 — 2026-08-26 Convergence and Experimental Baseline Succession** to record:

- disposition of the missing/contaminated tag;
- status reset for M-4…M-8;
- creation criteria for `CONVERGENCE-BASE-v1`;
- the new generality falsifier;
- the evidence ladder;
- retirement of noncanonical planning trees;
- prohibition on rewriting historical ADRs or reusing the missing tag name.

---

## 8. Constitutional convergence phase

### C0-1 — Freeze and inventory

- Pause new feature merges.
- Preserve `624d80f` as the audit input, not an accepted milestone baseline.
- Capture branch/commit/tree digests and remote tag inventory.
- Obtain the original `M-5A-BASE-v2` tag object and RF-95/M-5b/M-6 bundles from the developer if they exist.
- Reject screenshots or prose as substitutes for immutable artifacts.

### C0-2 — Ratify decisions

- Ratify ADR-0099 only after M7-01 evidence; do not pre-decide concurrency.
- Ratify ADR-0100 before public M-8 lifecycle or memory APIs.
- Ratify ADR-0101 Graviton evidence methodology.
- Ratify ADR-0102 convergence/baseline succession.

### C0-3 — Collapse documentation to one authority tree

Apply accepted decisions to existing canonical homes:

- `VISION.md` only for constitutional amendments.
- `docs/SPEC.md` and `docs/01_law/` for normative obligations.
- `docs/02_decisions/` for append-only decisions.
- `docs/03_execution/milestones.md` and `sprint_active.md` for status and sequencing.
- `docs/04_architecture/` and `docs/05_contracts/` as generated/verified descriptive projections.

Then archive or remove from the active tree:

- `docs/00_leadership_supersede_all/`;
- root `sprint_doing_v2.md` and `sprint_doing_v2B.md` after accepted findings are absorbed;
- duplicated assessment and ADR-0097 candidate copies;
- the committed masterplan as active authority.

Historical review material may live under `docs/_archive/reviews/` with non-authorizing metadata. No file or directory may claim `supersede_all` authority.

### C0-4 — Make status machine-checkable

Replace duplicated prose status with one table in `sprint_active.md` whose rows carry:

```yaml
milestone: M-6
package_state: PACKAGE_READY
merge_state: MERGED
gate_state: OPEN
evidence_refs: []
blocked_on:
  - independent_review_receipt
last_verified_commit: 624d80f...
```

Add a linter that rejects:

- `DONE` with an empty evidence reference;
- `CLOSED` when any required gate is open/waived;
- a named tag that does not resolve remotely;
- contradictory statuses for the same milestone;
- stale current-state claims outside `docs/03_execution/sprint_active.md`;
- `docs:` or `chore:` commits that touch production/schema surfaces.

### C0-5 — Restore hermetic CI

- Declare and lock every Python test dependency, including JSON Schema validation.
- Add the provider-key hygiene preflight.
- Run qualified Linux UDS lifecycle tests.
- Keep RF-86 fail-closed, but update its baseline only through ADR-0102.
- Run Python, TypeScript, codegen, boundary, TCB, event coverage, RF allocation, links, secrets, and documentation consistency gates from a clean clone.

**C0 exit:** canonical docs have no status contradiction; CI is reproducible from declared dependencies; remote baselines resolve; every accepted claim points to a digest-addressed artifact.

---

## 9. Corrected milestone state at `624d80f`

| Milestone | Mechanism state | Evidence state | Director status |
|---|---|---|---|
| M-4 | Evidence runtime, `/2` trajectory, RF-100 and runner implemented | Live-run claim exists; bundle/reviewer not present | **PROVISIONAL — development continuation only** |
| M-5a | Event `/2`, AgentView, checkpoints, RF-96/97/99/100 strong | Control tag absent; baseline provenance unresolved | **IMPLEMENTED / GATE OPEN** |
| M-5b | SAT pack, exterior evaluator and signed vectors implemented | Historical zero-diff control invalid/unavailable | **PACKAGE_READY / REVALIDATION REQUIRED** |
| M-6 | SpawnAdapter, attenuation, conservation, recovery and E2E tests strong | Independent bundle/review not present | **PACKAGE_READY / GATE OPEN** |
| M-6.5 | Controller seam, guards, projection, statistics implemented | No valid non-degenerate paired study | **PACKAGE_READY / STUDY BLOCKED** |
| M-7 | Parser, lowering, scheduler reference and analyzer implemented | Selector-gap claim false; production integration and accepted M7-01 absent | **PARTIAL / DECISION OPEN** |
| M-8 | Skill evaluation/promotion/rollback mechanisms strong; memory fake exists | ADR-0100, real capability binding, durability and lift absent | **PREPARATION ONLY** |
| M-9/M-10 | Narrative/scaffold ideas only | No authority | **PLANNED; DO NOT START** |

---

## 10. Delivery plan through M-8

Two Senior developers remain sufficient if they receive large, bounded ownership blocks. Both work from the same accepted baseline, never consume each other's unfinished branches, and synchronize only through frozen contracts and integration gates.

### Lane A — Execution / Runtime / Causal Infrastructure

Linear sequence:

1. **A-C1 Evidence and release path:** recover or regenerate the RF-95 evidence bundle; close qualified UDS/CI defects; produce M-6 nested-lineage release bundle.
2. **A-M7 Runtime integration:** bind topology extension and reference scheduler into the one runtime path, disabled by default and sequential under I-11.
3. **A-M8 Durable memory:** implement verified authorization context, durable category stores, retrieval provenance, revocation, and context integration.

### Lane B — Contracts / Experiments / Generality / Learning

Linear sequence:

1. **B-C1 Generality revalidation:** recover/adjudicate the old baseline; if invalid, implement the new deterministic domain pack after `CONVERGENCE-BASE-v1` and produce the clean neutrality bundle.
2. **B-M65 Experimental instrument:** create a preregistered stochastic attributable environment/provider and deliberately blockable tasks; run the paired study.
3. **B-M7 Evidence:** run canonical workloads, produce M7-01, and prepare the ADR-0099 evidence package against A's frozen integration contract.
4. **B-M8 Promotion experiment:** build the real held-out workload, candidate generator input pipeline, signed evaluation bundle, promotion, and executed rollback over A's frozen memory contract.

### Shared-package rule

Each package can reach `PACKAGE_READY` using frozen protocols, fixtures, and fakes. Final `GATE_ACCEPTED` may depend on the producer package already merged. This preserves development independence without pretending architectural consumers have no dependencies.

---

## 11. Sprint sequence

### Sprint C1 — Truth Restoration and M-5/M-6 Closure

**Entry:** C0 documentation/CI convergence accepted.

**Dev A outcome:** one immutable release-evidence package covering M-4 RF-95 provenance and M-6 nested-lineage/conservation/kill-tree behavior. If the old RF-95 bundle exists, verify rather than rerun. If absent, create one new preregistration and execute exactly one candidate.

**Dev B outcome:** one valid M-5b generality package. Prefer recovery of a genuinely clean M-5a control; otherwise use `CONVERGENCE-BASE-v1` plus a new deterministic domain pack. Keep the current SAT pack as smoke/regression coverage.

**Leadership gate:** independently accept M-4, M-5a baseline disposition, M-5b generality evidence, and M-6 separately. Create no closure by aggregation.

**Exit:** M-4, M-5a, M-5b, and M-6 each have an explicit accepted/open state and immutable evidence references; no contradictory board row remains.

### Sprint C2 — M-6.5 Measured Meta-Control

**Dev A:** freezes the current guarded runtime seam and reviews provider/task wiring only. No new privilege and no Kernel diff.

**Dev B:** implements the experiment.

The stochastic design must use common-random-number blocking at stable semantic checkpoints, not raw turn index. A recommended identity is:

```python
perturbation_key = digest(task_manifest_digest, environment_seed,
                          semantic_checkpoint_id, attempt_ordinal)
```

Both treatment and control see the same task/environment perturbation. Controller presence is the only declared treatment axis. A/A uses preregistered replicate seeds from the same configuration to estimate the noise floor. Every seed and perturbation record enters experiment identity and provenance.

Required evidence:

- interior A/A floor;
- arm comparability except controller axis;
- observed directives on deliberately blocked tasks;
- McNemar exact test over discordant pairs;
- Holm correction over the preregistered metric family;
- paired confidence interval;
- regression budget;
- signed report artifact.

**Exit:** M-6.5 closes on either an accepted positive result or an honest negative result with controller disabled by default.

### Sprint C3 — M-7 Topology Integration and Concurrency Decision

**Dev A outcome:** optional, digest-pinned `RunPlanExtension` reaches `Runtime.execute_harness`; the reference scheduler remains sequential; disabled topology is bit-identical; three real topologies execute through the same runtime and ordinary mediated spawn.

**Dev B outcome:** canonical M7-01 report using actual resource selectors/sinks and correlated timing telemetry where required; three-topology neutrality and replay bundle.

**Leadership gate:** ADR-0099 chooses one:

- implement bounded concurrency;
- allow only proven-safe read parallelism;
- keep the reference scheduler sequential.

Default is simplicity unless measured benefit exceeds the preregistered threshold after contention, recovery complexity, cache behavior, and budget/idempotency risk.

**Exit:** M-7 closes with topology execution evidence and an explicit scheduling decision. Concurrency is optional; the decision is mandatory.

### Sprint C4 — M-8 MVP: Durable Memory and Governed Learning

**Entry:** ADR-0100 accepted and five-category contract kit frozen.

**Dev A outcome:**

- session state remains WAL + AgentView, not a new memory port;
- durable Knowledge, Experience, SkillLibrary, and ProjectMemory adapters;
- content-addressed append/index model;
- verified `AuthorizedMemoryContext` bound to grant, selector, tenant/project scope, expiry/revocation, and policy identity;
- provenance for every retrieval entering model context;
- cross-category, cross-project, revoked, expired, and forged-grant falsifiers;
- atomic durability/recovery tests.

Conceptual contract:

```python
@dataclass(frozen=True)
class AuthorizedMemoryContext:
    grant_digest: str
    authority_source: str
    selector: ResourceSelector
    tenant_id: str
    project_id: str
    policy_digest: str
    expires_at: str | None
    verification_receipt: str

class MemoryPort(Protocol):
    def write(self, value: ArtifactRef, auth: AuthorizedMemoryContext) -> RecordRef: ...
    def recall(self, query: Query, auth: AuthorizedMemoryContext) -> RetrievalResult: ...
    def invalidate(self, record: RecordRef, auth: AuthorizedMemoryContext) -> None: ...
```

The adapter verifies the receipt and selector at every operation. Nonempty strings are never sufficient authority.

**Dev B outcome:**

- trajectory-derived candidate generation;
- sealed dev/held-out/adversarial/transfer splits;
- independent evaluator authority;
- signed promoter authority;
- versioned composition as the promotion unit;
- measured held-out lift with attribution to actual invocation/grounding/verification;
- affected-context regression budget;
- real atomic promotion;
- injected regression followed by executed rollback restoring the previous composition behavior.

**Leadership gate:** accept M-8 only if memory authority is real, retrieval provenance reaches context evidence, at least one composition shows measured held-out lift, rollback actually executes, and Kernel/RF-98 neutrality remains green.

**Exit:** M-8 is the MVP. M-9 planning may then become active.

---

## 12. Required PR contract

Every future PR must contain this matrix:

| Obligation | Implementation symbol/path | Test/falsifier | Evidence artifact |
|---|---|---|---|
| Exact spec/ADR requirement | Exact public seam | Exact command and RF identifier | Digest-addressed output |

And must declare:

- starting commit/tag;
- owned files and shared hotspots;
- schema read/write versions;
- Kernel semantic diff: yes/no;
- dependency-lattice diff: yes/no;
- event roster/writer authority diff: yes/no;
- migration and rollback;
- package-local DoD;
- integrated gate;
- deliberately excluded scope.

Commits touching `vanguard/packages/**` or `schemas/**` cannot use `docs:` or `chore:`. SQLite databases, generated experiment corpora, frontend work, research, and milestone backend code must not share one commit or PR.

---

## 13. Definition of Done through M-8

The MVP is delivered only when all conditions hold:

1. Canonical authority contains no parallel plan or contradictory status.
2. Clean-clone CI is reproducible from declared dependencies.
3. Qualified Linux UDS lifecycle gates pass.
4. Every baseline resolves remotely and carries immutable metadata/receipts.
5. M-4 has an independently accepted RF-95 bundle.
6. M-5a has a valid baseline disposition and reconstruction evidence.
7. M-5b has a non-contaminated generality falsifier.
8. M-6 has accepted nested-lineage/conservation/recovery evidence.
9. M-6.5 has an accepted positive or negative paired study.
10. M-7 executes at least three topologies through one runtime and ADR-0099 records the concurrency decision.
11. M-8 has real capability-mediated durable memory, provenance-visible retrieval, measured composition lift, independent promotion, and executed rollback.
12. Kernel remains domain-blind and within the budget; transitive trusted closure remains bounded.
13. No M-9/M-10 semantics enter Kernel, domain substrate, or the generic episode loop.

---

## 14. Immediate Director orders

1. Stop new feature merges on `feat_higgs_M4_M8` until C0 closes.
2. Ask the developer for the exact local `M-5A-BASE-v2` tag object, target commit, annotation, and review receipt; do not ask them to recreate it.
3. Ask for the original RF-95, M-5b, and M-6 evidence bundles with digests and environment/protocol identities.
4. Correct `sprint_active.md` to the state table in §9.
5. Retire the Leadership/masterplan/sprint-report parallel authority tree after extracting accepted decisions.
6. Fix declared test dependencies and add status/tag/commit-label consistency gates.
7. Ratify ADR-0101 and ADR-0102.
8. Create `CONVERGENCE-BASE-v1` only after clean-clone CI and canonical reconciliation pass.
9. Open Sprint C1 with one large package for Dev A and one for Dev B.
10. Do not schedule M-9/M-10 implementation until the M-8 MVP gate is accepted.

---

## 15. Final Director judgment

The project does not have an architecture crisis. It has an **evidence-control and execution-governance crisis produced by rapid, interleaved progress**. The code is materially ahead of the old plans and contains several strong mechanisms; the documents and baseline claims failed to keep up, and some tests/prototypes were promoted rhetorically into milestone completion.

Preserve the architecture. Reset claims to proof. Recover or supersede the contaminated baseline explicitly. Collapse documentation to the canonical triad. Then execute C1→C4 without adding a new framework layer. This is the lowest-risk and fastest credible route to an M-8 MVP.
