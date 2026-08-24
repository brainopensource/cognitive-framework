---
id: active-sprint-board
class: execution
authority: execution
canonical_for:
  - active-sprint-tasks
  - current-milestone-gates
status: living
owner: tech-lead
version: "0.7.0"
last_verified: 2026-08-24
supersedes: []
superseded_by: null
---

# Active Sprint Board — AETHER Higgs Release (v0.7.0)

**Start here:** [`README.md`](../../README.md) is navigation; [`SPEC.md`](../SPEC.md) and the six
normative leaves under [`01_law/`](../01_law/) are law. Accepted ADRs record decisions. This file is
the **sole living implementation authority**; [`milestones.md`](milestones.md) sequences unopened work.

## 1. Director Decision and Current Truth

**Current Director decision (2026-08-24):** M-3C is closed at `136436e`. W-3D Product Runtime
Profiles is accepted under ADR-0089 and the corrective wave is complete. RF-85 execution is now open
for clean-environment qualification; M-5+ remains locked.

The retained M-3C diagnosis at repository commit `e3acc5c228f9a61a357d955c86317369f3339841` found that the
M-3 contracts and side-path falsifiers exist, but the production closure claim is not yet supported by
one executable authority:

- `Runtime.compose()` still enters through `ManifestLoader.load_pack()`, the legacy manifest value,
  and global `DEFAULT_BINDINGS`.
- `mhf.manifest/2`, the named-graph compiler, registry lifecycle, and isolation broker are not joined
  to that public path.
- `vg-code-default` and `vg-table-default` remain legacy-shaped; the latter cannot be wired by the
  production default binding table.
- the release path defaults to an in-memory event store; file-backed WAL continuation has been proven
  by a focused fixture, not by the product E2E path.
- the nine-row M-4 auditor validates supplied rows but the release path does not yet derive and bind
  all nine rows from canonical sources.

Those defects were corrected and independently reviewed by G0-G4/RF-78-RF-84. M-4 is no longer
blocked by M-3C; it remains blocked until the real provider, evaluator and rootless Linux environment
qualify and the preregistered run produces all nine source-derived rows. Passing isolated schema,
compiler, lifecycle, auditor, fake or synthetic tests cannot close M-4.

| Wave | Milestone | State | Exit condition |
|---|---|---|---|
| Wave 0 | M-0 | **CLOSED (GREEN)** | CI truth and named falsifiers. |
| Wave 1 | M-1 | **CLOSED (GREEN)** | Fail-closed Trust Spine and signed evidence. |
| Wave 2 / 2C | M-2 | **CLOSED (GREEN)** | Truthful trajectory plus fresh-process recovery. |
| Wave 3 | M-3 | **CONTRACT COMPLETE; OPERATIONAL CLOSURE RESOLVED BY M-3C** | Prior graph, lifecycle, and Layer-0 work is retained as evidence, not discarded. |
| Wave 3C | M-3C / v0.6.2 | **CLOSED (GREEN) — DIRECTOR DECISION 2026-08-24** | G0–G4 and RF-78–RF-84 independently reviewed; canonical authority, durable lineage, and authority retirement proven by `136436e`. |
| Wave 4 | M-4 / v0.6.3 | **OPEN — RF-85 QUALIFICATION** | W-3D implementation and focused gates are complete; execute one real uninterrupted nine-row run with no mock, stitched trace, repair, or synthetic substitution. |
| Waves 5–10 | M-5–M-10 | **LOCKED** | Each preceding objective gate must close; roadmap text alone never authorizes work. |

## 2. Frozen Invariants and Decision Envelope

M-3C MUST preserve:

- the domain-blind S0–S12 kernel, descriptor-bound grants, monotonic attenuation, typed reservation
  and settlement, and the TCB ceiling of `<= 1438` LOC;
- RFC 8785 JCS and distinct `D_H`, `D_R`, and `D_X` subjects;
- append-only events, one legal writer per privileged event kind, SQLite-WAL recovery, and I-9
  recovered trajectory continuity;
- exterior Ed25519-signed evaluation, rootless worker isolation, and fail-closed absent/forged rules;
- the unary sequential episode mechanism (I-11); composition is static addressing, never a runtime
  workflow DAG;
- the five-SPI freeze and the M-4 compatibility ingress for supported legacy manifests.

M-3C MUST NOT add `agent.spawn`, concurrency, swarms, topology engines, retrieval redesign, DPO,
VFE/EFE, automatic promotion, a sixth SPI, a new event kind without allocation and writer proof, a
third runtime tree, or packages created merely to mirror conceptual planes.

The Higgs documents are corrective research inputs, not authority. Their proposals become binding
only through the law/ADR/execution precedence defined by `SPEC.md`.

### Decision rights

| Group | Delegated authority | Mandatory escalation |
|---|---|---|
| **Devs A — Principal / Specialist / PhD lane** | Independently decide reversible internal boundaries, normalized composition representation, interface ownership, activation sequencing, migration mechanics, and cross-module implementation within the frozen law and this charter. Own the hardest architecture and integration work. | Any change to normative invariants, authority semantics, TCB scope/ceiling, hashes/JCS, event taxonomy, SPI roster, evaluator boundary, concurrency gate, or release authorization requires a successor ADR and the named Director approval. |
| **Devs B — Senior Development lane** | Implement frozen contracts through packs, adapters, fixtures, persistence wiring, caller migration, conformance tests, CI, and bounded documentation synchronization. May make local implementation choices that do not alter an interface or authority boundary. | Must stop and return a falsifier when a task requires an unresolved architecture decision, kernel/identity/event redesign, or widening of scope. |

Neither lane may be the sole acceptance authority for its own cross-lane gate. Devs A own shared
architecture hotspots; Devs B integrate only after the relevant contract is frozen.

## 3. Authorized Sprint Sequence

### W-3D — Product Runtime Profiles (active)

W-3D is authorized by ADR-0089. Dev A owns runtime/profile/bootstrap/activation architecture
hotspots; Dev B owns packs, adapters, CLI entrypoint, fixtures, evidence plumbing, and CI. Both may
work in parallel, but B integrates only against A's frozen contracts. The merge order is:

`RF-87–RF-94 RED → A interface freeze → B implementation → A integration → cross-lane gate → full gates`.

W-3D MUST preserve the kernel, S0–S12, sequential I-11 loop, evaluator boundary, WAL truth, and
RF-85 requirements. It MUST NOT implement M-5–M-8 features. W3D-00 through W3D-12 are tracked in
`TODO_W-3D_final.md`; this board is the authorization source.

**Current W-3D gate:** W3D-01 through W3D-12 implementation is complete. RF-87–RF-94 focused
falsifiers, RF-78–RF-84 convergence checks, TypeScript typechecks, boundary, RF-ID, TCB, and
duplication gates are green. The deterministic fake preview reaches the same runtime path and
`vg doctor` reports real host facts. M-4 is now open for clean-environment qualification and RF-85;
no RF-85 evidence is claimed until the preregistered real run and independent audit exist.

### Sprint 3C.0 — Authority reconciliation and RED contract (complete)

The two lanes start in parallel, but production refactoring remains closed until Gate G0.

| Lane | Authorized work | Owned surfaces | Evidence / completion |
|---|---|---|---|
| **A0 — Architecture lock** | Reconcile `mhf.manifest/2` versus `mhf.harness/1`; define one authored shape, normalized internal value, freeze boundary, activation ownership, run-plan boundary, binding-provider contract, lifecycle lineage, persistence rule, evidence derivation rule, and compatibility sunset. Decide whether existing ADR-0077/0081 suffice or prepare the minimal successor ADR and atomic law amendments. Allocate new RF identifiers before creating new falsifiers. | `docs/SPEC.md`, affected `docs/01_law/`, successor ADR/index proposal, schemas and cross-module contract map. | Every open decision is classified frozen, retained compatibility, amended, or deferred; no contradiction remains between co-normative leaves; RF ownership is allocated. |
| **B0 — Baseline and characterization** | Produce a claim-to-code-to-test matrix; enumerate every production caller of legacy and v2 readers, compilers, bindings, registry, release stores, and M-4 audit. Prepare bounded characterization fixtures for code and table packs without changing production behavior. | Existing tests/fixtures, pack inventories, CI and caller maps; no architecture hotspot edits. | Current `main` fails the proposed public-path claims for the diagnosed reason; no environment failure is mistaken for architectural evidence. |

**Gate G0 — decision and RED lock:** ADR-0088 and the law amendments are ratified; RF-78–RF-84 are
allocated. G0 remains open until RF-78/RF-79 target the public runtime and fail
for the intended defect. Only then may Sprints 3C.1–3C.3 change production code.

**A0 RED-lock evidence at baseline `6fb5e9a`:** `test/falsifiers/test_rf78_canonical_composition.py`
and `test_rf79_legacy_normalisation.py` are red at the public `Runtime.compose` boundary; their
authored `/2` fixtures are schema-valid and parse on the side path, so the only cause is that the
legacy reader is the public authority and no `FrozenComposition` exists. A0 does not self-certify G0.

### Sprint 3C.1 — Canonical composition and two-domain ingress (complete)

| Lane | Authorized work | Owned surfaces | Evidence / completion |
|---|---|---|---|
| **A1 — Canonical composition core** | Implement one schema-authoritative reader/normalizer and one immutable composition result; resolve refs, interfaces, ceilings, isolation, profiles, entrypoints, and all behavior-affecting identity inputs once. Make the public `Runtime.compose()` consume this result. Names such as `FrozenComposition`, `ActivationPlan`, or `RunPlan` are adopted only if G0 ratifies their distinct responsibilities. | `schemas/mhf/manifest_v2.schema.json`, `domain/artifacts/manifest.py`, `runtime/compose.py`, `runtime/registry/compiler.py`, narrow wiring interfaces. | Legacy compatibility input and authored `/2` converge to the same normalized facts and `D_H`; unknown/unconsumed authority fails before run; no second parser is production authority. |
| **B1 — Packs and binding providers** | Convert `vg-code-default` and `vg-table-default` to the ratified authored shape; implement domain-provided, namespaced binding adapters against A1's frozen interface; add golden and differential fixtures. | `packs/`, `agency/manifests/`, domain adapters outside `domain/` and `kernel/`, pack/adapter/contract tests. | Both packs compose through the same public API; table verbs require no global coding-specific binding row; zero changes to `kernel/` or `agency/episode/`. |

**Gate G1 — composition identity (RF-78/RF-79):** both domains compose through one public boundary; edge/config/ref
changes alter `D_H`; compatibility preserves declared facts without inventing defaults; the normalized
value contains no legacy-only authority. Non-sequential profiles and `agent.spawn` remain named
pre-authorization refusals until M-7 and M-6 respectively.

### Sprint 3C.2 — Activation, lifecycle, and deterministic cleanup (complete)

| Lane | Authorized work | Owned surfaces | Evidence / completion |
|---|---|---|---|
| **A2 — Public activation** | Join canonical composition to one runtime-owned activation/run boundary and registry-owned lifecycle. Bind every activated component to the same run lineage; define deterministic reverse-order cleanup for compose, verify, activation, call, cancellation, evaluator failure, and crash paths. | `runtime/compose.py`, `runtime/root.py`, `runtime/session.py`, `runtime/registry/`, `runtime/wiring.py`. | Public execution walks discover→resolve→verify→activate→call→quiesce→retire; fault paths end fault→cleanup→retire; no plugin can mint grants, judge, or write privileged history. |
| **B2 — Lifecycle integration** | Migrate callers and pack adapters to A2; extend echo, code, and table integration fixtures; cover UDS permissions, typed in-process parity, timeout, crash, cancellation, evaluator failure, log isolation, and cleanup. | Pack/adapters, caller tests, registry/integration fixtures; A-owned hotspots only through reviewed integration patches. | Code and table probes activate and retire through the same public runtime and lineage; injected failures leave no socket/process/workspace leak. |

**Gate G2 — executable canonical path (RF-80/RF-81):** both domain probes compose, activate, execute, and clean up
through one runtime authority; registry events are reachable, owner-written, and reducible; no graph
edge becomes runtime scheduling.

### Sprint 3C.3 — Release durability and source-derived M-4 evidence (complete)

| Lane | Authorized work | Owned surfaces | Evidence / completion |
|---|---|---|---|
| **A3 — Durable identity/evidence join** | Bind composition, activation, run, event range, trajectory, containment, and verdict identities; replace self-attested M-4 booleans with derivation or verification against canonical artifacts; preserve absent/forged distinctions. | `runtime/session.py`, trajectory/evaluator/evidence seams, event projections, narrowly required schemas. | Evidence rows cross-bind one lineage and recomputable `D_H/D_R/D_X`; cryptographic verdict verification is authoritative; unsupported claims remain absent, never pass. |
| **B3 — Release runner and fault proof** | Make the release/E2E path require an explicit file-backed SQLite-WAL store; add fresh-process continuation, durable-intent, cold reconstruction, and clean-Linux environment probes. Wire the nine-row auditor to derived artifacts without fabricating a real run. | Release/lab runner, store configuration, adapters, integration/falsifier fixtures and CI jobs. | Hard process death reconstructs the same composition/run/trajectory identity and does not repeat a settled effect; `:memory:` remains test/local-only and cannot certify M-4. |

**Gate G3 — durable evidence lineage (RF-82/RF-83):** one synthetic hermetic integration fixture proves the complete
shape and negative cases, while remaining explicitly ineligible for M-4. Altered cross-digests,
text-only signatures, mixed lineages, unverified containment, missing cost status, or asserted defaults
must deny.

### Sprint 3C.4 — Legacy retirement and independent certification (complete)

| Lane | Authorized work | Owned surfaces | Evidence / completion |
|---|---|---|---|
| **A4 — Authority retirement** | Remove or make ingress-only every competing production parser, compiler, binding authority, activation route, and default in-memory release path after differential parity. Audit import/runtime traces and architecture diff. | Production composition/activation/runtime surfaces and enforcement linters. | Exactly one public authority remains; supported legacy bytes terminate at the compatibility boundary and cannot survive as an execution value. |
| **B4 — Migration close** | Migrate remaining callers, tests, packaging, CI, and living navigation; run the complete conformance, recovery, security, and documentation gates from a clean clone/environment. | Callers, tests, fixtures, packaging, workflows, existing canonical docs. | No stale production path, duplicate dialect, hidden binding table, package entry, or navigation claim remains. |

**Gate G4 — M-3C closure (RF-84):** independent review confirms G0–G3, both domains use one public path,
supported legacy ingress is bounded through M-4, no competing production authority remains, full
suites and architecture/security/documentation gates are green, and rollback does not restore dual
authority. Only the Engineering Director may then mark M-3C closed and open M-4.

## 4. Parallel Integration Protocol

1. Devs A publish the smallest frozen interface and red contract for each sprint before dependent
   Devs B production work begins; B0 characterization may proceed immediately.
2. Exclusive A hotspots are `domain/artifacts/manifest.py`, manifest schemas, `runtime/compose.py`,
   `runtime/root.py`, `runtime/session.py`, `runtime/wiring.py`, and `runtime/registry/`. Devs B own
   packs, adapters, fixtures, caller migration, runner configuration, and CI unless a reviewed
   integration patch is explicitly assigned.
3. Merge order per slice is `A contract/RED -> B rebase and implementation -> A integration ->
   cross-lane gate -> independent review`; there is no repository-wide “A finishes before B starts”.
4. Every PR states requirement/ADR, affected modules, dependency, risk, acceptance falsifier,
   evidence artifact, rollback, and prohibited scope.
5. Rollback is per reversible slice. A compatibility reader may be retained through M-4; a second
   production authority may not be retained as fallback.

### Common verification sequence

```text
red falsifier confirmed -> focused suites -> cross-lane integration gate
-> full production suites -> codegen/schema vectors
-> boundaries/TCB/domain/isolation/duplication
-> RF IDs/metadata/links/stale paths/secrets -> independent evidence review
```

## 5. M-4 Active Contract

M-4 remains the retained foundation contract and its release lane is open after W-3D
requalification. Its first authorized slice provisions and qualifies a real provider, evaluator identity, rootless Linux environment, file-backed WAL, and
preregistered coding task/oracle. M-4 then executes one uninterrupted `run_id` through the canonical
release path and must populate all nine
rows defined in [`milestones.md`](milestones.md#m-4-single-run-evidence-contract) under RF-85. Mock, cassette,
stitched trace, manual repair, host fallback, or separately passing runs remain ineligible.

## 6. Completed Evidence Kept in Force

| Milestone | Retained result |
|---|---|
| M-0 | CI subject of record and named falsifiers. |
| M-1 | S0–S12 Trust Spine, signed verdicts, single writer, typed budgets, and bounded TCB. |
| M-2 / 2C | RF-23 truthful `mhf.trajectory/1` and RF-25 fresh-process continuation. |
| M-3 partial | Named-graph schema/compiler contracts, registry lifecycle components, and atomic `layer0/` source/package/CI retirement. Operational canonical-path closure is the sole reopened scope. |

## 7. Director Escalation Boundaries

Only the Engineering Director may authorize changing the TCB threshold, normative authority or security
invariants, canonicalization/hash algorithms, event-kind or SPI rosters, evaluator trust boundary,
concurrency before M-7, M-3C closure, M-4 opening, or release versions after M-4.

## 8. Integration Review — 2026-08-24

**Owner:** Tech Lead (integration); independent G4 reviewer required before Director decision.
**Subject baseline:** `db5d733`; retained M-3C commits `5872608`, `3cf6877`, `c4fa5fc`,
`a26b3bb`, `324b1c9`, and `db5d733`. The final G3/G4 corrective patch is still uncommitted and is
not release evidence.

| Gate | State | Evidence and remaining blocker |
|---|---|---|
| **G2 / RF-80–RF-81** | **TECHNICALLY GREEN; INDEPENDENTLY REVIEWED** | Public execution enters the runtime-owned `run_composed` boundary, emits registry-owned lifecycle events on the episode lineage, and retires in reverse order. Code and table packs resolve through namespaced providers. |
| **G3 / RF-82** | **TECHNICALLY GREEN; INDEPENDENTLY REVIEWED** | Release mode requires effective file-backed SQLite-WAL. A hard-death fixture exits with `os._exit`, reconstructs state in a fresh process, verifies chain continuity, and invokes the recovery continuation boundary to prove the settled physical effect is not repeated. |
| **G3 / RF-83** | **TECHNICALLY GREEN; INDEPENDENTLY REVIEWED** | `D_R` is bound through `EpisodeStarted`, WAL, `RunResult`, `mhf.trajectory/1`, and `FoundationEvidence`. Derived rows carry their canonical source, source digests are recomputed, flat/asserted rows deny, Ed25519 verification is verifier-driven, and WAL/cost/authority observations are recomputed rather than trusted as booleans. Unsupported rows remain explicitly absent. |
| **G4 / RF-84** | **TECHNICALLY GREEN; DIRECTOR DECISION REQUIRED** | Executable AST caller/import audit plus a negative competing-authority fixture prove the production path converges on `Runtime.run_composed`; the lab driver bypass was retired, the legacy compiler is no longer package-exported, and lifecycle cleanup persistence failures propagate. Only the Engineering Director may mark M-3C closed or open M-4. |

Verification on 2026-08-24:

- outside the restricted executor sandbox: `test/falsifiers` 50/50, `test/contracts` 199/199,
  and `test/registry` 27/27 passed;
- `test/runtime` passed 416 tests with 7 skips and 3 environment failures. All three require a
  reachable Ollama daemon to distinguish an absent tag and reported the truthful cause
  `provider_unreachable`; they are not M-3C code regressions;
- inside the restricted executor sandbox, UDS, loopback, and Bubblewrap probes additionally fail
  with `EPERM`; rerunning outside that sandbox removes those failures;
- boundaries, TCB (`1366 <= 1438`), secrets, domain blindness, isolation policy, duplication,
  falsifier IDs, Markdown links, and stale-path linters passed.

Independent review first rejected G4 and identified the missing operational joins. After correction,
the same independent reviewer reran 29 focused tests plus `test_composition_root` and reported no
remaining technical G3/G4 blocker. This is technical closure evidence, not Director authorization.

**Director decision:** M-3C is closed and W-3D is active under ADR-0089. The next authorized action is
W-3D-01 baseline/falsifier work. RF-85 remains unclaimed and paused; no synthetic fixture is M-4 evidence.

## 9. Dev C RF-85 Preparation and Frozen Two-Lane Contract — 2026-08-24

**Preparation baseline:** `5229e720be37d708b24a009f35423691aacb3d49` plus the Dev C contract
commit recorded below. ADR-0088 already decides every architecture-bearing question; no successor ADR
is required. `Runtime.run_composed` is the sole public execution authority. `run_id` is correlation,
while `D_R` is the immutable execution-configuration identity. An eligible run is one whose task and
oracle were immutably preregistered before its first event and whose one `RunPlan` binds one `D_R`,
`project_id`, `run_id`, `episode_id`, `D_H`, activation digest, environment, real model route,
file-backed store and evaluator. Every event, WAL range, trajectory and evidence source MUST join that
same tuple.

**Uninterrupted** means one causal ledger lineage from the preregistered start to terminal outcome.
A hard process death may cross a process boundary without breaking continuity only when a fresh
process verifies and folds the durable prefix, retains the same plan and identifiers, reconciles each
open S8a intent, and appends through the canonical writer. A settled physical effect is never invoked
again. An unresolved intent is `unverifiable`/undeterminable and denies continuation of that effect
until exterior reconciliation; it is never guessed successful or retried. A new plan, copied event,
stitched trace, manual edit, alternate run, fallback or post-hoc preregistration breaks eligibility.

**Eligibility environment:** the provider MUST perform a live non-fake/non-cassette invocation and
return provider/model/fingerprint plus measured usage. The worker MUST be Linux rootless Bubblewrap,
with effective UID/mount/network/syscall probes and no host fallback or evaluator path. The evaluator
MUST be a separately isolated identity and verify a preregistered oracle, returning an Ed25519 verdict
whose JCS body binds the task/oracle, subject, protocol, `D_H`, `D_R`, run/episode and evidence. Failure
to reach or verify any of these is an environmental or trust blocker, never a passing row.

**Evidence state algebra:** `absent` means no canonical source existed and carries a typed reason;
`invalid` means a source or bundle exists but violates schema, lineage, digest, policy or signature;
`unverifiable` means a well-shaped source exists but its required exterior verifier/probe is unavailable
or an open intent cannot be reconciled. Only nine independently verified derived rows produce
`present_valid`. All other states fail closed and are ineligible for promotion. Synthetic fixtures may
exercise all states but cannot change their own eligibility.

### Frozen interfaces and lane ownership

| Contract | Frozen minimum | Owner |
|---|---|---|
| Run plan/identity | `RunPlan.lineage()` keys: `project_id`, `run_id`, `episode_id`, `composition_digest`, `activation_digest`, `run_digest`; `D_R` binds task preregistration, environment, file store, route, oracle, authority, budget and sequential mode | A |
| Runtime/events/WAL | `Runtime.run_composed`; canonical event envelopes and one `LedgerEmitter`; file-backed SQLite with effective `journal_mode=wal`; S8a `EffectStarted` durable before physical effect; terminal receipt/reconciliation | A |
| Provider/sandbox/recovery | live provider telemetry; rootless Bubblewrap attestation; fresh-process reconstruction report with chain/state digests and settled-effect non-repetition | A |
| Evaluator protocol | existing `EvaluatorPort`/JSON-RPC and `SignedVerdict`; RFC-8785 JCS body, Ed25519 key ID/public key and task/oracle/subject/protocol/identity binding | B |
| Preregistration | immutable digest created before first run event, binding task bytes/digest, oracle files/digests, evaluator identity, protocol and subject; referenced by `RunPlan`, verdict and bundle header | B |
| Evidence/auditor | `mhf.foundation-evidence/1`; exact nine numbered rows with canonical source plus recomputed source digest; auditor recomputes joins/verifiers and returns `absent`, `invalid`, `unverifiable`, or `present_valid` | B |

No file overlap is authorized. Dev A owns `vanguard/packages/runtime/{root.py,session.py,run_plan.py,
foundation_evidence.py,trajectory.py,ledger/}`, `vanguard/packages/adapters/models/`,
`vanguard/packages/adapters/sandbox/`, `vanguard/packages/adapters/stores/event_store.py`, and A-lane
tests/fixtures. Dev B owns `vanguard/packages/adapters/evaluators/`, `vanguard/packages/ports/evaluator.py`,
`vanguard/packages/domain/evidence/`, evaluator/preregistration schemas and B-lane tests/fixtures. Shared
exports or schema-generated files require a Dev C integration patch; neither lane edits the other's
surfaces. The kernel, episode engine, event-kind roster, JCS and TCB ceiling are frozen.

### RF-85 row ownership and objective acceptance

| Row | Producer / verifier | Passing observation |
|---:|---|---|
| 1 | A / B auditor | one live provider invocation with non-synthetic identity/fingerprint and measured usage |
| 2 | A / B auditor | matching request, descriptor grant, decision, reservation, S8 verification, durable intent and terminal settlement |
| 3 | A / B auditor | before/after workspace digests differ and bind the canonical patch receipt |
| 4 | A / B auditor | rootless UID plus mount/network/syscall attestations; evaluator absent; no host fallback |
| 5 | B | isolated evaluator verifies preregistered oracle and Ed25519 binding |
| 6 | A / B auditor | effective file WAL, complete event range, terminal digest, chain continuity and durable intent |
| 7 | A / B auditor | fresh process reconstructs identical folded state/lineage and proves no settled effect repeated |
| 8 | A / B auditor | one `mhf.trajectory/1`, ordered invocations/receipts, explicit measurement states and conserved cost |
| 9 | A / B auditor | executable import/runtime trace reaches only canonical compose/activate/session authority |

**Rollback and merge gate:** each lane is one revertable commit series against the frozen SHA. A lane
may merge only when its focused tests, the frozen cross-lane contract, negative security cases and
applicable suites pass, it changes no foreign-owned file, and it introduces no competing parser,
compiler, binding table, emitter, evaluator bypass or host fallback. Integration then runs the full
Python suite, TypeScript typecheck/tests and all mandatory architecture/security linters. Rollback is
the lane commit series; it must not restore legacy execution authority or mutate durable evidence.

**Preparation baseline result:** contracts 199/199, falsifiers 50/50, registry 27/27, security 45/45
and trust 22/22 passed. Runtime ran 419 tests with 7 skips and three environment failures because no
Ollama daemon answered at `127.0.0.1:11434`; the implementation truthfully returned
`provider_unreachable` while the live-tag tests expected `model_tag_absent`. These are environmental
qualification failures, not permission to weaken assertions. The new frozen RF-85 contract is RED
only for the missing preregistration join and evidence-state algebra described above.

### Integration record and Leadership handoff

**Frozen base:** `4a7ed9c`. **Dev A integrated:** `2a96158` (`feat(runtime): enforce RF-85 release
admission`). **Dev B integrated:** `6c82635` (`feat(evidence): bind RF-85 preregistration trust`). Dev C
explicitly reassigned `adapters/environment/sandboxed.py` to A because it is the runtime-owned adapter
that invokes the already frozen Bubblewrap perimeter probe; no evaluator/trust surface moved lanes.
Rollback is commit-local in reverse order and must leave `4a7ed9c`'s non-promotional RED lock intact.

Independent review initially rejected integration for an incompatible preregistration wire, an
unverified self-attested preregistration digest, a row-5 self-selected trust key, permissive provider
defaults, incomplete lineage and recovery that converted `undeterminable` into `OK/OCCURRED`. Dev C
corrected each finding. Final independent re-review found no remaining critical merge blocker and ran
24 focused tests green. Legacy/headerless evidence is now always `unverifiable` and non-promotional;
the canonical envelope requires API/header/bundle digest, the preregistration source, authoritative
row verifiers and complete signed evaluator bindings. An unreconciled cold intent returns F-22 and
cannot execute or claim occurrence.

Integration verification on 2026-08-24:

- focused RF-85 trust/release/recovery contracts: 27/27 green; all contract tests reached 207 green
  on the first integrated run, with a later rerun showing two executor-only UDS bind timeouts;
- registry 27/27, security 45/45 and trust 22/22 green;
- full Python discovery ran 1,291 tests: 1,287 passed, 3 skipped, and one RF-82 release fixture was
  blocked before execution because Bubblewrap probes were unverified under the restricted executor;
- runtime discovery ran 424 tests: 414 passed, 7 skipped, and three live Ollama assertions failed
  because no daemon answered; the truthful result was `provider_unreachable`, not `model_tag_absent`;
- boundaries, TCB (`1366 <= 1438`), secrets, domain blindness, isolation policy, duplication, RF IDs,
  Markdown links, stale paths and diff checks passed;
- TypeScript typecheck/tests did not start because `tsc`/installed npm dependencies are absent;
  this is an environment/setup blocker, not a passing or failing product assertion.

**Gate status:** the RF-85 preparation/interface/merge gate is technically reached. M-4/RF-85 is not
reached and has zero claimed rows. Current blockers are a clean non-WSL restricted Linux environment
that can attest rootless Bubblewrap and evaluator isolation, a reachable selected real provider, an
installed TypeScript toolchain for repository gates, and immutable task/oracle preregistration made
in that qualified environment. **Responsible:** Release Engineering owns environment qualification;
Trust/Evidence owns preregistration and independent audit; Leadership/Engineering Director retains
the milestone decision. **Only next authorized action:** provision and qualify that environment,
install the locked dependencies, rerun all gates, then create the immutable task/oracle preregistration.
Only after every startup probe passes may Release Engineering start the single uninterrupted RF-85
run. Waves 5+ remain locked.


---

## 10. ADR-0090 Application and the M-7 Measurement Gate — 2026-08-24

**Branch:** `feat/m6-adr0090`, cut from `feat_W4-W6_Higgs_core` @ `caa78d7`.
**Authority:** ADR-0090, ratified by the CEO on 2026-08-24. Steps 1–8 of the
Leadership Control Report application sequence only. Steps 9–11 are
**LEADERSHIP HOLD** and were not executed.

**No RF-85 foundation evidence is claimed by this work.** Nothing in this
section advances M-4. The nine-row gate is untouched and still requires one
uninterrupted real run.

### 10.1 M-6 work items — closed and not closed

| Item | State | Evidence |
|---|---|---|
| `ChildSpawned`/`ChildReturned` allocated in the event roster | **CLOSED** | Already present in the 42-kind enum; the defect was their classification as advisory markers in `UNFOLDED_ALLOWLIST`. |
| Both kinds folded into `LedgerState.children` | **CLOSED** | `domain/ledger/reducer.py`; open-until-returned, cold path reconciles, never assumed complete. |
| `SpawnAdapter` bound as sole legal writer of both kinds | **CLOSED** | `runtime/ledger_emitter.py` `PRIVILEGED_KIND_OWNERS`; kernel and orchestrator denied. |
| ADR-0090 ratified and indexed | **CLOSED** | [`02_decisions/0090-mediated-delegation-event-roster.md`](../02_decisions/0090-mediated-delegation-event-roster.md). |
| Child payload schema ratified into `schemas/mhf/` | **OPEN** | Only the review bundle carries it, and its spelling disagrees with the ADR. The reducer accepts both spellings until `SpawnAdapter` fixes the wire. |
| `agent.spawn` capability active | **OPEN** | Inert at three points: `domain/artifacts/manifest.py` refuses the verb, `runtime/delegation.py` refuses every spawn (`M6_SPAWN_ACTIVE = False`), verb on the inert list. |
| RF-55–RF-59 allocated and red | **OPEN** | Named by ADR-0090, unallocated in `INDEX.md`, no test exists. |
| Kill-tree drill | **OPEN** | Needs a live multi-process run; gated with the M-4 rows. |
| `LedgerState` digest covers `children` | **CLOSED** | ADR-0091 commits every non-empty child record while preserving the exact canonical shape and digest of historical non-delegating states. |

M-6 remains **LOCKED**. ADR-0090 closed the roster question; the milestone's
exit gate is unmet and its dependencies (M-4, M-5) are not closed.

### 10.2 Next sprint — the sole authorized M-7 item

**M7-01 — capture the sequential effect log.** Measurement only. **Do not build
a scheduler, a leasing protocol, or a topology engine.**

ADR-0092 authorizes this measurement after the ADR-0091 stabilization patch.
It does not open M-7 or lift I-11.

| Field | Value |
|---|---|
| Outcome | One effect log over a fixed-seed task set, run sequentially, sufficient to compute a measured independent fraction. |
| Source | `EffectRef` constructed from ledger `EffectStarted` payloads carrying **concrete resolved paths** — never from pack manifests. |
| Capture per effect | `selector`, `sink`, `idempotency_key`, wall/model/tool timings, `cache_hit_rate`. |
| Owner | Release Engineering (capture); Devs A (analysis). |
| Prohibited scope | Any concurrency, lease, claim-TTL, scheduler or topology implementation. I-11 stays mandatory. |
| Definition of done | The log exists, is reproducible from a fixed seed, and yields a number. The number is reported to the Engineering Director; it is not acted on. |
| Falsifier | To be allocated at the measurement ADR. RF-46–RF-48 remain reserved for M-7 implementation and MUST NOT be consumed by the measurement. |

**Static manifest scans are not the decision input.** Two `fs.read`
capabilities both declaring `root: /workspace` look overlapping on paper and
read different files at runtime. A 0.0% static reading is not evidence against
M-7; it is evidence the measurement has not been taken.

If the measured fraction is below roughly 30%, the correct outcome is to
**cancel M-7 and keep I-11**. Only the Engineering Director may lift I-11, and
only against an accepted measurement ADR stating the speedup ceiling,
contention cost and leasing protocol. M-8 must not begin before this log exists.

### 10.3 Operational findings

**Finding 1 — CI MUST run as a non-root user.** Running as uid 0 grants
`CAP_SYS_ADMIN` inside the Bubblewrap user namespace, so the nested-`unshare`
probe correctly refuses to attest containment, and containment becomes
unattestable. Five of the eight failures seen under root close simply by
switching user; the product code is not involved. GitHub CI already satisfies
this — `.github/workflows/ci.yml` runs on `ubuntu-latest` with no container, so
steps execute as the unprivileged `runner` user — so **no workflow change is
required**. The finding binds local, WSL2 and self-hosted runners: never run the
suite as root and never interpret a root run's containment failures as product
defects.

**Finding 2 — Bubblewrap is already optional; WSL2 is not blocked.** The
`local` execution profile presets `process_backend: "host"` and
`attestation_required: False` (`runtime/profiles.py`), so a host without
Bubblewrap runs the product through the same canonical path. What such a host
cannot do is produce promotion-eligible evidence: `local` also presets
`evaluation_mode: "none"` and `promotion_eligible: False`, and an unavailable
requested containment mode still fails closed rather than falling back to the
host. So WSL2 is a valid development and product environment and an invalid
RF-85 qualification environment. These are different claims and were previously
conflated into "M-4 is blocked".

### 10.4 Verification

Baseline established before any change, on this host as uid 1000 (non-root):
**1297 passed / 5 failed / 8 skipped / 2 errors**. The five failures decompose
as three environmental (no Ollama daemon; the implementation truthfully reports
`provider_unreachable` where the tests expect `model_tag_absent`) and two
`docs/03_execution/sprint_active_fix.md` doc-metadata failures introduced by
commit `caa78d7`, which committed that report without YAML frontmatter. The two
errors are a pytest artifact: the helper `def tests_pass(repo)` in two files
matches the default `test*` collection glob and errors on a missing fixture. The
repository's canonical runner is `unittest` (see `.github/workflows/ci.yml`),
under which neither error occurs.

Every step held that baseline exactly. The final suite is **1312 passed / 5
failed / 8 skipped / 2 errors** — the same failure and error set, plus 15 new
tests. `ci/rf86_gate.sh M-5-BASE` reports all five frozen paths clean, and the
kernel TCB is unchanged at 1366 logical lines against the 1438 ceiling.

---


# CURRENT M-4 RELEASE WORK PROMPTS

These prompts supersede the pre-integration A/B instructions. The implementation seams are merged;
the remaining work is qualification and execution, not another architecture pass.

## DEV A

```text
Você é o Dev A, Senior Runtime/Systems Engineer, responsável pela qualificação e operação da lane
runtime de M-4 sobre a base integrada `1a1ed6c`. Em um host Linux limpo e não restrito, instale as
dependências bloqueadas, qualifique um provider real alcançável e o worker rootless Bubblewrap, e
prove file-backed SQLite-WAL, durable intent e cold continuation sem repetir efeito liquidado. Execute
todos os gates antes do run. Depois que Dev B publicar o preregistro imutável, execute exatamente um
run pela autoridade `Runtime.run_composed` e entregue somente fontes canônicas das linhas 1, 2, 3, 4,
6, 7, 8 e 9. Se qualquer probe, provider, WAL, identidade, custo ou continuidade falhar, pare e
registre o bloqueio; não use mock, cassette, `:memory:`, fallback host, stitching ou reparo manual.
Reporte ao Dev C ambiente, comandos, SHAs, event range, digests e rollback. Não declare M-4 concluída.
```

## DEV B

```text
Você é o Dev B, Senior Trust/Evidence Engineer, responsável pela qualificação e auditoria da lane de
confiança de M-4 sobre a base integrada `1a1ed6c`. Em um ambiente de evaluator separadamente isolado,
fixe sua identidade e trust root, valide RPC/Ed25519 e publique antes do primeiro evento o preregistro
imutável que liga task, oracle, digests, protocolo, subject e chave do evaluator. Durante o único run,
derive a linha 5 e audite o envelope real completo com os verificadores autoritativos das nove linhas,
recomputando source/bundle/cross-digests, lineage, WAL, containment, trajetória e assinatura. Qualquer
ausência, invalidade ou fonte não verificável nega o gate. Não aceite bundle headerless, autoassinatura,
fixture sintética, boolean autoatestado ou resultado copiado. Reporte ao Dev C preregistro, trust root,
resultado do oracle, razões de auditoria, artefatos e rollback. Não declare M-4 concluída.
```

## DEV C — archived preparation prompt

The Dev C preparation below is retained only as the execution record that produced `4a7ed9c`,
`2a96158`, `6c82635`, and `1a1ed6c`; it MUST NOT be rerun as current work.

```text
Você é o Dev C, Principal Engineer e autoridade técnica de preparação e integração. Execute este prompt
integralmente antes de liberar Dev A e Dev B. Você tem poder total de desenvolvimento dentro da
autorização vigente, mas não pode fabricar evidência, ampliar M-4 por inferência nem abrir Waves 5+.

Primeiro reconcilie README.md, docs/SPEC.md, docs/01_law, ADR-0069–0088, milestones.md e este board com
o código real. Elimine toda ambiguidade remanescente de M-3/M-3C/M-4 e registre nas autoridades
canônicas existentes, sem criar Markdown de planejamento: definições exatas de run elegível e
ininterrupto; autoridade pública única; identidade e joins RunPlan/D_R/eventos/WAL/trajetória/evidence;
semântica de durable intent, hard-death e cold continuation sem repetição de efeitos; provider real;
Linux rootless/Bubblewrap; evaluator isolado e Ed25519; preregistro de task/oracle; nove linhas RF-85;
estados absent/invalid/unverifiable; critérios fail-closed; proibições de mock, cassette, stitching,
fallback e reparo manual; ownership, rollback e gates finais. Se uma nova decisão arquitetural for
realmente necessária, registre um ADR append-only e atualize os índices/links canônicos.

Depois congele interfaces mínimas e tipos de wire entre as duas lanes, incluindo schemas, IDs/digests,
eventos, ports, protocolos do evaluator, preregistro, evidence bundle e auditor. Defina uma matriz sem
overlap de arquivos: Dev A possui runtime/composição/provider/sandbox/WAL/continuação; Dev B possui
evaluator/Ed25519/preregistro/auditoria/fixtures de confiança. Crie ou ajuste os testes contratuais RED
que fixam cada interface, as negativas de segurança e os critérios objetivos das nove linhas, deixando
fakes suficientes para A e B avançarem em paralelo sem commits um do outro. Resolva previamente cada
decisão difícil; não transfira ambiguidade arquitetural aos seniors.

Valide a baseline completa, diferencie regressões de limitações ambientais e publique no próprio
sprint_active.md o contrato congelado, owners, dependências, comandos, resultados e bloqueios reais.
Então libere simultaneamente Dev A e Dev B com SHAs-base e critérios de merge. Durante a integração,
revise ambos independentemente, resolva conflitos preservando a autoridade única, execute todas as
suítes e linters obrigatórios e confirme que nenhuma autoridade concorrente ou bypass reapareceu.
Somente um run real, preregistrado, contínuo e auditável pode preencher RF-85. Ao final, registre commits
e evidências reais no board e entregue à Leadership: próximo passo oficial, gate alcançado, bloqueios,
responsável e única ação seguinte autorizada. A declaração final de conclusão/avanço permanece com a
Leadership/Engineering Director.
```
