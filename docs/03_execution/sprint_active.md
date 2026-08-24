---
id: active-sprint-board
class: execution
authority: execution
canonical_for:
  - active-sprint-tasks
  - current-milestone-gates
status: living
owner: tech-lead
version: "0.6.3"
last_verified: 2026-08-23
supersedes: []
superseded_by: null
---

# Active Sprint Board — v0.6.3 Foundation E2E (M-4)

**Start here:** [`README.md`](../../README.md) is navigation; [`SPEC.md`](../SPEC.md) and the six
normative leaves under [`01_law/`](../01_law/) are law. Accepted ADRs record decisions. This file is
the **sole living implementation authority**; [`milestones.md`](milestones.md) sequences unopened work.

## 1. Director Decision and Current Truth

**Decision:** reopen the operational closure of M-3 as the bounded corrective wave **M-3C**. Preserve
the Trust Spine and converge only the `Composition -> Activation -> Runtime` seam before attempting
M-4. This is not authorization for a platform rewrite.

Static reconciliation at repository commit `e3acc5c228f9a61a357d955c86317369f3339841` found that the
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

Therefore M-4 is blocked by both M-3C and its real provider/evaluator environment. Passing isolated
schema, compiler, lifecycle, or auditor tests cannot close M-3C or M-4.

| Wave | Milestone | State | Exit condition |
|---|---|---|---|
| Wave 0 | M-0 | **CLOSED (GREEN)** | CI truth and named falsifiers. |
| Wave 1 | M-1 | **CLOSED (GREEN)** | Fail-closed Trust Spine and signed evidence. |
| Wave 2 / 2C | M-2 | **CLOSED (GREEN)** | Truthful trajectory plus fresh-process recovery. |
| Wave 3 | M-3 | **CONTRACT COMPLETE; OPERATIONAL CLOSURE REOPENED** | Prior graph, lifecycle, and Layer-0 work is retained as evidence, not discarded. |
| Wave 3C | M-3C / v0.6.2 | **CLOSED (GREEN) — DIRECTOR DECISION 2026-08-24** | G0–G4 and RF-78–RF-84 independently reviewed; canonical authority, durable lineage, and authority retirement proven by `136436e`. |
| Wave 4 | M-4 / v0.6.3 | **ACTIVE — ENVIRONMENT QUALIFICATION / RF-85** | One real uninterrupted nine-row run; no mock, stitched trace, repair, or synthetic substitution. |
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

M-4 is opened by Director decision dated 2026-08-24. Its first authorized slice provisions and
qualifies a real provider, evaluator identity, rootless Linux environment, file-backed WAL, and
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

**Director decision:** M-3C is closed and M-4 is open. The next authorized action is environment
qualification and task/oracle preregistration, followed by one eligible RF-85 run only after every
startup probe passes. No row is presently claimed, and no synthetic fixture is M-4 evidence.
