The phase is **Concept Lock**, not implementation. Forensic discovery is written; ADRs `0069`–`0073` exist; SPEC v0.6 is **partially** rewritten. Hygiene and the SPEC self-review are **not** done. No runtime, CI, or dual-tree code was changed, and nothing was committed.

---

## 1. What this engagement actually is

You asked me to act as Principal Staff Engineer, treat `TODO_DONT_COMMIT_BEFORE_DOING_IT_v2.md` as the locked procedure, use `principal_engineer_proposal.md` as the architectural north star, and “make all the decisions so we can start the next phase: development after locking concepts.”

There is a real conflict in the prompt stack. I did **not** silently merge it.

| Source | What it authorizes | What it forbids |
|---|---|---|
| `TODO_DONT_COMMIT_BEFORE_DOING_IT_v2.md` | Forensic investigation + two deliverables | Architecture rewrite, SPEC rewrite, roadmap, code, deleting either runtime |
| Concept-lock plan (`001_V060_concept_phase_BETA.md` / `.cursor/plans/v0.6_concept_lock_99714496.plan.md`) | After forensics: ADRs `0069`–`0073` + SPEC v0.6 + hygiene | Roadmap, sprints, production code, CI rewire, commit unless asked |
| Your wrapping “Suggestion” §2–6 | CI truth, runtime convergence, substrate repair, plugins, one real coding-agent E2E | — |

**Ruling I already made and will not reopen without you:** this session’s authorized product is **law**, not **machinery**. Suggestion steps 2–6 are the *next major phase*, recorded as deferred. Implementing them now would violate both the forensic TODO and the concept-lock exit gate (“working tree contains no runtime/CI implementation of the next wave”).

That is the correct Principal call: lock the ontology before touching the two runtimes, otherwise every code change becomes a third implicit architecture.

---

## 2. Full plan (the one I am executing)

### 2.1 Global sequence (not skippable)

```text
FORENSIC DISCOVERY          ← done as investigation, not law
        ↓
ARCHITECTURE / CONCEPT LOCK ← in progress; this is the current phase
        ↓
ADR + SPEC v0.6             ← ADRs written; SPEC half-applied
        ↓
AS-BUILT GAP / MIGRATION CLASSIFICATION   ← next major phase
        ↓
SINGLE OPERATIONAL PLAN (not five competing reviews)
        ↓
CODE, in this order only:
  1. CI subject-of-record + negative behavioral tests
  2. Converge packages ← absorb layer0 (no third tree)
  3. Irreversible substrate (schema, D_H/D_R/D_X, lineage, fail-closed ceilings, signed verdicts, cold replay)
  4. Extensibility (compose freeze, walking-skeleton plugin, then pack extraction)
  5. Stop foundation work only when ONE real coding-agent path is true end-to-end
```

Roadmaps, waves, heterogeneous subagents, Meta-Harness, concurrency, distribution, WASM-default, and Rust stay **behind** that E2E gate.

### 2.2 Authority ranking I locked

1. Forensic TODO = procedure for discovery.
2. Concept-lock plan = procedure for *this* phase’s docs.
3. `principal_engineer_proposal.md` = conceptual target (recursive machine, ledger authority, cheap logical agents).
4. Current SPEC + ADRs = law until a newer ADR cites a reversal.
5. Parecer v4 / Full Refactor v3.1 / Execution Plan / Aether waves = evidence only.

Conflicts already adjudicated (not “compromised”):

- **Rust core** (Full Refactor) → rejected as v0.6 architecture. Python 3.10+, Rust only behind a later measured TCB-hot-path gate.
- **`layer0/` as production destination** (Execution Plan + SPEC v0.5 §1) → reversed. Canonical lattice is `vanguard/packages/`.
- **New top-level `core/`** (parecer v4) → rejected; that would be a third identity.
- **Evaluator as product plugin** (parecer Anel 2) → rejected; ADR-0004 / ADR-M0-08 stand.
- **Mid-run hot-swap** (SPEC v0.5 §2.1) → struck for v0.6; ADR-0005 wins.
- **Aether wave roadmap** → out of this phase.

### 2.3 The twelve P0 locks (now ADR-cited)

These are the ontology. Implementation does not get to renegotiate them in a PR.

| ID | Lock | ADR |
|---|---|---|
| P0-1 | Python-first. Production lattice = `vanguard/packages/`. No `aether-rust/`. | 0069 |
| P0-2 | Converge: keep packages implementations; absorb layer0 SPI/JSON-RPC/UDS/lifecycle; delete duplicates only after parity. | 0069 |
| P0-3 | Decision plane proposes; ledger proves. `Decision → DurableEvent → fold → EffectiveState`. | 0071 |
| P0-4 | `Agent = Principal + HarnessInstance`. Swarm = policy. Graph = event projection. | 0070 |
| P0-5 | `Capabilities(child) ⊆ parent`; 6-D budget conservation; mandatory causal envelope. | 0070 |
| P0-6 | Identity trinity: `D_H` / `D_R` / `D_X`. FrozenHarness is `D_H` only. | 0071 |
| P0-7 | Hybrid ES; SQLite WAL; replay taxonomy; consistency unit `project_id`. | 0071 |
| P0-8 | Wire-first JSON-RPC/UDS; Protocol is a client; `in_process` is a privilege; freeze at compose; five SPIs. | 0072 |
| P0-9 | Exterior signed judge. Fabricated `"pass"` is defect F1, not a strategy. | 0072 |
| P0-10 | Sequential execution. Independence may be *declared*, not *run*. | 0073 |
| P0-11 | Production lattice is the CI subject of record. E-COV lexical grep is not I-2. | 0073 |
| P0-12 | Defer Meta-Harness, distribution, WASM-default, graph DB, pytest-runner, competence-graph, Rust rewrite. | 0073 |

### 2.4 What “done” means for *this* phase (exit gate)

All nine must be true before I will call Concept Lock closed:

1. Forensic report exists, 25 sections, labeled `[FACT]/[INFERENCE]/[PROPOSAL]/[UNKNOWN]`, live commands.
2. Concept-lock prompt exists and was followed.
3. Every P0 has an ADR citation in SPEC.
4. Every P1 is LOCK NOW or DEFER DELIBERATELY (forensic §20).
5. SPEC v0.6 has no TBD and **does not** still say `layer0/` is the M1 destination.
6. ADR INDEX lists `0069`–`0073` **and** `ADR-M0-01`…`13`. `0067` stays a hole.
7. Conflict log lists the rejected supporting-doc items.
8. Working tree has **no** runtime/CI implementation of the next wave.
9. No git commit unless you ask after reviewing the docs.

**Honest status: 1–2, 4, 6–9 are essentially satisfied. 3 and 5 are only partially satisfied because SPEC edits were interrupted.** Hygiene (`CLAUDE.md`, `sprint_active.md`, review banners, KERNEL annex amendment line) is not done.

### 2.5 What I will *not* do in this phase, even if it looks like “help”

- Rewire `.github/workflows/ci.yml`
- Fix F1 in `layer0/scheduler/driver.py`
- Split `root.py`
- Delete `layer0/`
- Green the full 1119-test suite
- Write a roadmap / waves / sprint board with dates
- Commit

Those belong to **as-built gap classification**, then one operational plan, then code.

### 2.6 Next major phase (after you accept the lock)

Not “start coding randomly.” A gap matrix first:

```text
SPEC v0.6 × ADR 0069–0073 × as-built packages × as-built layer0 × tests × CI
```

Then a **single** execution plan whose first code commits are:

1. CI subject-of-record: `test/kernel` (already 95 OK), plus runtime/agency/adapters, plus bwrap where the OS allows.
2. Negative tests: forged verdict, missing grant, capability widening, budget widening, fail-open ceiling, replay divergence, sandbox failure.
3. Kill F1 on the *canonical* path (packages engine must *read* signed verdicts; layer0 driver must stop being the CI-blessed liar).
4. Fail-closed ceilings into `FrozenHarness`; persist intersection, not the harness list.
5. Envelope fields by construction; real `mhf.trajectory/1`; cold SQLite replay ≠ `fold(same list)`.
6. Walking-skeleton plugin on JSON-RPC/UDS, then extract coding behavior into `packs/code-default/`.
7. Stop when one path has: real model, real authorized effect, real filesystem change, real sandbox, real signed eval, real WAL, real replay, attributable trajectory, one runtime authority.

That is the only intellectually honest “foundation green.”

---

## 3. Ground truth I actually measured (so the plan is not literary)

Re-run on this tree (`c7e9ded`), not inherited from parecer commit `99d1e0b`.

| Surface | Result | Engineering meaning |
|---|---|---|
| `test/layer0` | 25 OK, 0.014s | CI’s microkernel is green and **semantically weak** |
| `test/packs` | 27 OK | code-default pack + I-6/I-7 fixtures green |
| `test/kernel` | **95 OK, not in living CI** | production kernel is the real oracle and is currently uncertified by CI |
| `test/runtime` | 400 ran, 3 FAIL (Ollama unreachable vs `model_tag_absent`) | env-sensitive, not a dispatch break |
| Full `test/` | 1119 ran, **7 FAIL / 5 ERROR / 8 skip** | CLAUDE.md “not fully green” is confirmed |
| `check_boundaries` / TCB / I-7 / I-6 / secrets | PASS | structural gates work |
| `check_stale_paths` + `test_repo_paths` | **FAIL** (`docs/sprint6B`) | living CI would be red on this tree for a docs-archive path |
| E-COV | “40 kinds, 100%” | **false confidence**: greps strings; F1 still “covered” |
| `root.py` | 1418 LOC | composition god-object; not in TCB glob `kernel/*.py` |
| F1 | `layer0/scheduler/driver.py:138-139` | `VerdictRecorded {verdict: "pass"}` with no signature |
| layer0 spawn | `:170-192` | `CHILD_SPAWNED` then immediate `CHILD_RETURNED` `spans: []` |
| layer0 ledger | `MemoryLedger` | not WAL |
| packages ledger | `PRAGMA journal_mode = WAL` | this is the real store |
| ceiling | `ceiling.py:21-22` | empty capabilities ⇒ allow (fail-open) |
| compose | `compiler.py` | intersects, then stores harness list, not intersection |
| jsonrpc | packages toolkit already imports `layer0.spi.jsonrpc` | convergence has started *accidentally* |

The load-bearing sentence: **CI currently certifies the walking skeleton’s ability to mention event kind names, not the production runtime’s ability to judge, persist, or attenuate.**

---

## 4. Table — TODOs vs what I did

Status vocabulary matches the locked plan: `TODO / IN_PROGRESS / BLOCKED / DONE / DEFERRED`.

### 4.1 This phase (Concept Lock)

| ID | Work item | Status | What actually happened | Residual |
|---|---|---|---|---|
| A | Live test/CI/dual-runtime re-verify | **DONE** | Commands run via WSL; F1, WAL vs MemoryLedger, CI YAML, selector fork, spawn stub, fail-open ceiling, `root.py` size re-verified on this tree | `check_markdown_links`, CLI `npm test`, mutation score, byte-diff of the two selector files left `[UNKNOWN]` |
| B | `docs/07_reviews/VANGUARD_V060_FORENSIC_DISCOVERY.md` (25 sections) | **DONE** | Full report with labels, matrices, P0/P1/P2/P3, Goodhart audit, conflict log | Investigation, not law — as required |
| C | `PROMPT_ARCHITECTURE_CONCEPT_LOCK_V060.md` then execute it | **DONE** (prompt) / **IN_PROGRESS** (execution) | Prompt written; ADRs + partial SPEC follow it | SPEC self-review + hygiene not finished |
| D-adrs | ADR `0069`–`0073` | **DONE** | Five ADRs with ADR-0045 fields, reversal conditions, evidence anchors | None for authorship; they are law once SPEC cites them uniformly |
| D-index | `docs/05_adr/INDEX.md` | **DONE** | `0069`–`0073` added; `ADR-M0-01`…`13` rows added; `0067` hole documented | Verify no leftover INDEX prose contradiction |
| D-spec | `docs/SPEC.md` → v0.6.0 | **IN_PROGRESS** | Header, preamble, A-5 (`D_H` only), §1 lattice reversal + §1.0 recursive machine/authority/identity, replay taxonomy, hot-swap struck, F1 named, fail-closed compose, §8 direction inverted | See §5 below — several v0.5 sentences still in the file |
| E1 | `CLAUDE.md` version pointer | **TODO** | Not edited | Still says `v0.4.5-beta` |
| E2 | `sprint_active.md` status note | **TODO** | Not edited | Still M0 Docs Lock v0.5.0 |
| E3 | Review corpus banners (non-normative) | **TODO** | Not edited | Five Principal-review files still read as if they were law |
| E4 | `KERNEL.md` amendments line | **TODO** | Not edited | Still says “M1 ports verbatim” into `layer0/` |
| E5 | Exit-gate verification pass | **TODO** | Not run as a closeout checklist | SPEC still contains destination/hot-swap residue in later sections |
| Commit | git commit | **DEFERRED** | Explicitly not done | Only if you ask after review |

### 4.2 Forensic TODO deliverables (the v2 document itself)

| Deliverable | Status |
|---|---|
| Establish as-built vs normative vs proposals | **DONE** |
| Dual-tree equivalence matrix | **DONE** |
| SPEC × ADR × code × tests × proposals matrix | **DONE** |
| Concept inventory | **DONE** |
| P0/P1/P2/P3 registries | **DONE** |
| `VANGUARD_V060_FORENSIC_DISCOVERY.md` | **DONE** |
| `PROMPT_ARCHITECTURE_CONCEPT_LOCK_V060.md` | **DONE** |
| Design a new architecture / rewrite SPEC *inside the forensic phase* | N/A — forensic phase complete; SPEC rewrite belongs to Concept Lock and is in progress |
| Roadmap / waves / sprints / code | **DEFERRED** by the TODO’s own global sequence |

### 4.3 Your original Suggestion §1–6 (development after lock)

| Step | Status | Why |
|---|---|---|
| 1. Lock documentation and concepts | **IN_PROGRESS** | ADRs exist; SPEC not self-consistent yet |
| 2. Restore engineering truth (CI + full suite + negative tests) | **DEFERRED** | Concept-lock hard out-of-scope; first code-phase task |
| 3. Converge two runtimes without a third | **DEFERRED** | Law locked in 0069; no directory migration this phase |
| 4. Repair irreversible substrate (`D_H/D_R/D_X`, lineage, signed verdicts, cold replay) | **DEFERRED** | Requirements locked in 0070–0072; not implemented |
| 5. Extensibility (compose pipeline, walking skeleton, pack extraction) | **DEFERRED** | ADR-M0-13 + 0072; prove on packages path later |
| 6. One real coding-agent E2E | **DEFERRED** | Foundation stop condition for the *code* programme, not this docs wave |

### 4.4 P1 leftovers (already classified, not reopened)

| P1 | Classification |
|---|---|
| Envelope fields on new event kinds | LOCK NOW (semantics; emit in code phase) |
| One generated `EffectRequest` (I-1) | LOCK NOW as invariant; codegen later |
| Walking skeleton on canonical path | LOCK NOW as sequencing; implement later |
| `in_process` still speaks the wire | LOCK NOW as rule |
| INDEX M0 rows + `0067` hole | LOCK NOW — INDEX done |
| Trajectory on every `EpisodeCompleted` | LOCK NOW as requirement; emit later |
| Fail-closed ceilings in `FrozenHarness` | LOCK NOW as requirement; fix later |
| Split `root.py` | DEFER DELIBERATELY (code wave) |
| Plugin TS conformance / pytest-runner | DEFER DELIBERATELY |
| Model/sandbox behind plugin wire | DEFER DELIBERATELY (first-party ports in v0.6) |
| Stale `docs/sprint6B` CI red | DEFER (docs hygiene, not architecture) |
| Ollama `provider_unreachable` vs `model_tag_absent` | DEFER (test isolation) |
| Selector `process` vs `generic` | DEFER (contract bug) |
| Concurrency enablement | DEFER (I-11 measurement gate) |

---

## 5. Incomplete SPEC work (the only reason I will not say “Concept Lock is green”)

I interrupted mid-file. The following v0.5 residue is still likely in `docs/SPEC.md` and would fail the exit gate if left:

- **§8 standing gates** still treat E-COV as an I-2 proof. That must be demoted: lexical coverage is a weak proxy; I-2 requires production call-site behavior, including “forged verdict cannot be accepted.”
- **§8.2** still titled as deteriorations “M1 must close” and talks about “port with the kernel.” That language re-imports the reversed destination.
- **I-2** still reads as if emitter-string CI is sufficient. It is not; F1 is the existence proof.
- **I-4** still implies replay is already a CI property. The job is **named and unwired**; the layer0 test folds the same list twice.
- **I-7** still greps `layer0/` only. That remains valid *as domain-blindness of the fork*, but the production core is `vanguard/packages/{domain,kernel}` and must stay domain-blind there too as packs absorb coding.
- **§9 honour table** does not yet list the v0.6 bans: no third runtime, no swarm engine, no byte-identical concurrent ledger as a general requirement, no Rust rewrite, no WASM-default, no Meta-Harness implementation in this version.
- **§4–§6** still read like an implementation programme rather than a blueprint behind `ADR-0073`. I do **not** want to delete Phase 2/3 text; I want it clearly marked *deferred blueprint*, not v0.6 scope.
- **KERNEL.md** front-matter still says M1 ports the kernel into `layer0/`. One amendment line citing 0069 is enough; S0–S12 body stays.

Until those are cleaned, a careful reader can still quote SPEC against ADR-0069. That is exactly the failure mode this phase exists to kill.

---

## 6. Architectural thesis, stated as law rather than taste

The system is not a coding-agent framework with a kernel attached. It is a **small, fail-closed effect machine** plus a **content-addressed harness compiler** plus an **unreachable judge**. Intelligence, if it ever appears, has to appear as composition of those primitives:

```text
Principal + FrozenHarness(D_H) + spawn(attenuation, 6-D budget)
        → events
        → State = fold(Events)
        → exterior signed verdict
        → trajectory (D_R, D_X)
```

Anything that cannot be expressed that way is either a plugin strategy (planner, memory, context, tools) or a forbidden second engine (workflow, swarm, meta-loop, graph DB).

Two Python trees are not two philosophies. They are a **failed strangler**: contracts leaked into `layer0/`; durability and judgment stayed in packages; CI followed the new folder. The repair is convergence under packages authority, not a third rewrite and not a Rust leap that has no measured TCB gate and no staffing evidence.

---

## 7. What I want from you before I touch another file

When you say proceed, the **next** message from me should only finish Concept Lock hygiene, in this order, still no runtime code:

1. Finish SPEC self-review (the bullets in §5).
2. One-line KERNEL annex amendment.
3. `CLAUDE.md` v0.6.0 concept-lock pointer (package version stays `0.4.5b1`).
4. `sprint_active.md`: one status note that M0 docs lock is superseded; next authorized phase is as-built gap / migration classification — **no new sprint tasks or dates**.
5. Non-normative banners on the five Principal-review files.
6. Exit-gate checklist recited against files, not memory.

I will still not commit unless you explicitly ask.

If instead you want to skip the rest of the lock and start CI/F1/convergence code now, that is a **scope change**: it violates the concept-lock exit gate you already had in the plan. I will not do that by implication. Say it outright if that is the new order.

---

**Bottom line:** the ontology is chosen and mostly written into ADRs. The production lattice is packages. Layer0 is absorb-not-destination. The judge stays exterior. Execution stays sequential. Development does not start until SPEC no longer contradicts those sentences, and development itself starts with CI truth plus one real path — not with a new architecture.