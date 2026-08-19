# 01 — SPECS MIGRATION MATRIX: Audit & Disposal of `docs/01_specs/backend/`

**Authority:** `CRITICAL_GAP_ANALYSIS_AND_AUDIT.md` (AP-1, AP-2, §5 Kill/Keep register, Invariants I-1…I-10) and `NEXT_GEN_META_HARNESS_SPECIFICATION.md` (MHF v1, hereafter **SPEC**).
**Executes:** Milestone **M0 (Excise)** — "collapse specs to one normative doc + ADR log; single normative spec" and Invariant **I-8**: *specs are generated or normative — never both; drift is a CI failure, not a register.*
**Scope:** 16 files, 4,745 lines, ~55k words. Frontend spec tree (`docs/01_specs/frontend/`, 12 files) is **KILLED wholesale** per the backend-only mandate and is not itemised here.

---

## 0. Target end-state (what `docs/` looks like after M0)

```text
docs/
├── SPEC.md                      # NEXT_GEN_META_HARNESS_SPECIFICATION.md — the ONLY normative document
├── annex/
│   ├── KERNEL.md                # from VG-05 (kept nearly verbatim, K-40/F-21a amended)
│   └── MEASUREMENT.md           # from VG-07 §5 (paired designs, McNemar, A/A floor, instrument tuple)
├── adr/                         # append-only, reversal-condition format (from VG-09/VG-10 + extracts)
│   ├── 0001-…                   # renumbered ADR-*/DEF-*/REJ-* corpus
│   └── DRIFT_REGISTER_v045.md   # SYSTEM_SPEC_DRIFTS.md, frozen as historical evidence
├── reference/                   # GENERATED ONLY — schema reference from schemas/mhf/*.json; CI-rebuilt
├── 02_roadmap/                  # rewritten (see 02_ROADMAP_BACKLOG_AND_REVIEW_TRIAGE.md)
└── 03_sprints/                  # rewritten (see 03_SPRINTS_PARALLEL_EXECUTION_PLAN.md)
```

**Deleted trees:** `01_specs/backend/`, `01_specs/frontend/`, `00_executive/` (vision v3 cosmology, pitch), `scrum/` (sprint evidence → blob store per AP-7), `reviews/` (after triage in deliverable 02). Root-level `SYSTEM_SPEC_THEORY.md` and `SYSTEM_SPEC_ASBUILT.md` are deleted; `SYSTEM_SPEC_DRIFTS.md` is frozen under `adr/`. Word budget: ~55k spec words → target ≤ 9k normative + annexes.

**Verdict legend:** **KILL** = delete, no successor · **KEEP VERBATIM** = survives as annex/ADR with minimal amendment · **REFACTOR & MERGE** = named sections absorbed into SPEC, remainder deleted · **EXTRACT TO ADR/PLUGIN** = normative content moves to ADR log or a plugin design doc, file deleted.

---

## 1. The matrix

### 1.1 `00_phase0-rule-backlog.md` (143 ln, generated) — **KILL**
Generated artifact (`tools/rule_test_map.py`, header says "Do not edit"), tracking **133 of 203 rules open** against a rule corpus (N-*, CC-*, CT-*, K-*, MF-*) that M0 deletes with its owning documents. A backlog of obligations against dead specs is dead weight.
**Disposition:** delete file; delete `tools/rule_test_map.py` output targets. The *mechanism* — machine-generated rule→obligation tracking — is superseded by two stronger CI gates from SPEC §8: **E-COV** (declared event kind ⇒ reachable production emitter) and the **control-call-site proof** (AP-5 rule: a control merges only with its production call site). Nothing merges anywhere.

### 1.2 `00_rule-test-map.md` (211 ln, generated) — **KILL** (method extracted)
Same generator. Its self-report is the audit's AP-5 evidence in miniature: *203 rules · 28 tested · 42 "untestable" · 133 gaps*. The one idea worth keeping is the **bijection discipline with justified UNTESTABLE entries** (e.g., LT-* proven by static analysis rather than runtime test — a legitimate justification class).
**Disposition:** delete file. Extract the bijection principle into **ADR-M0-01 "Control coverage discipline"**: every SPEC invariant maps to exactly one of {CI job, contract test, static-analysis proof}, enumerated in CI config, with the mapping itself CI-checked. `tools/rule_test_map.py` is retargeted in M1 to enumerate SPEC invariants I-1…I-10 instead of the VG rule corpus (task S-M1-A-08 in deliverable 03).

### 1.3 `00_vanguard_registry_v040.md` (617 ln) — **KILL** (two extracts)
The document-precedence machine: status lifecycle, word budgets with a CI-authoritative counting script, precedence rules (PR-*), supersession maps over the pre-v4 corpus, identifier namespaces. It exists to adjudicate between multiple normative documents — a problem M0 dissolves by construction (**one** normative document ⇒ precedence is the identity function). Maintaining 617 lines of meta-governance for a corpus of one is the purest expression of AP-2.
**Extract 1 → ADR-M0-02:** §5 identifier namespaces — the convention that every rule/decision/task ID lives in a declared namespace with a single owner. MHF keeps three namespaces only: `I-*` (invariants, owned by SPEC), `ADR-*` (decisions), `S-M*-{A,B}-*` (sprint tasks).
**Extract 2 → CI:** §9's idea of CI-enforced doc integrity survives as a single check: `check_markdown_links.py` (already in `tools/`) + a grep gate that no file outside `docs/SPEC.md` uses RFC-2119 normative language ("MUST", "SHALL") — drift prevention by construction rather than by register.
Word-budget apparatus, supersession maps, REG-D migration ledger: deleted.

### 1.4 `01_vanguard_engineering_handbook_v040.md` (305 ln) — **REFACTOR & MERGE**
The strongest prose in the corpus. The eleven mental models are load-bearing and map 1:1 onto SPEC axioms:

| Handbook model | Fate | SPEC/ADR anchor |
|---|---|---|
| M1 "The episode is the program" (no workflow engine) | MERGE | SPEC §1.1; reinforced by REJ on playbook *runtimes* (see 1.14 note on VG-10 REJ entries) |
| M2 "Exactly four pluggable things" | **SUPERSEDED** — MHF has exactly **five** SPIs; the taxonomy change is recorded, not silent | ADR-M0-03: four extension forms → five SPIs (`IPlanner`, `IMemoryEngine`, `IToolkit`, `IContextManager`, `IEvaluationGate`); reversal condition: a capability that fits none of the five forces a design review, not a sixth SPI by PR |
| M3 "The broker grants; the sandbox contains" | MERGE | SPEC §A-2 (two authority systems) — M3 is its ancestor; cite it |
| M4 "Content informs, never authorises" | MERGE | SPEC §1.2 provenance events + kernel S1(e); the handbook's "it has happened twice" warning is preserved verbatim in `annex/KERNEL.md` |
| M5 "The verifier is outside everything" | MERGE | SPEC §2.1 (evaluator is not a plugin) |
| M6 "A gate that cannot fail is not a gate" | MERGE | SPEC §8 CI gates; also the rationale for killing the 488-test badge (AP-8) |
| M7 "Competence is the persistent object" | EXTRACT → Phase-3 plugin doc | `mhf.memory.graph` design (SPEC §6.1) |
| M8 "One document is normative per contract" | MERGE — becomes global | Invariant I-8; M0 is its enforcement |
| M9 "Minimise what must be simultaneously correct" | MERGE | SPEC §A-1 (Layer-0 ≤ 4.5k LOC) |
| M10 "Polyglot plugins outside the TCB / narrow waist" | MERGE | SPEC §2.1 isolation tiers; the wire *is* the waist |
| M11 "Generality Falsification Invariant" | MERGE | SPEC §6.4 (Pack #N with zero Layer-0 diffs) + Invariant I-7 |

Also merged: §4 testing taxonomy (mock / cassette / live — kept intact; cassettes are already a Layer-0 determinism primitive) and §4.2 "satisfiability check". Killed: §2 SOLID/DRY essays (generic), §3 shape-of-a-change (superseded by the M0–M6 sprint discipline), glossary (regenerate from SPEC terms).
**Residual:** a 1-page `CONTRIBUTING.md` carrying the merged mental models as onboarding, explicitly non-normative.

### 1.5 `02_vanguard_charter_claims_and_non_claims_v040.md` (245 ln) — **REFACTOR & MERGE**
The charter owns the separability thesis and the discipline of *non-claims* — both essential, both already partially restated in SPEC.

| Section | Fate |
|---|---|
| §1 Mission/thesis ("what solved it?" + judge exteriority) | MERGE → SPEC preamble; this is VG-02 and it stays the project's one-sentence identity |
| §1 formalism \(S_t = (G_C, G_E, L, A_t)\) | EXTRACT → Phase-3 `mhf.memory.graph` design doc; premature as core spec (audit D-39: "types only"; SPEC §9 refuses the competence-graph pretence) |
| §3 Non-claims | MERGE → SPEC §9 "What this specification refuses to build" — merge line-by-line; non-claims are the cheapest drift prevention that exists |
| §4 Falsifiable claims | MERGE → each surviving claim is rewritten as an M-gate with a proof command (deliverable 02 §3); a claim without a gate is deleted |
| §5 Design axioms | MERGE → SPEC §0 (A-1…A-6 already subsume most; delta recorded in ADR-M0-03) |
| §9 Approved stack, §10 Risk register | EXTRACT → ADR-M0-04 (stack decisions with reversal conditions) and ADR-M0-05 (risk register, pruned to risks that survive the rewrite: plugin-supply-chain, oracle overfitting, statistical power — per audit synthesis) |
| §6 cross-cutting norms, §7 lock/open, §8 strategic frame, §11 honest limits | KILL (restatements or superseded by M0–M6 sequencing) |

### 1.6 `03_vanguard_architecture_planes_and_execution_model_v040.md` (603 ln) — **REFACTOR & MERGE**
The six-plane model is retired as *vocabulary* (SPEC speaks Layer-0 / SPI / plugin / pack) but several sections are the intellectual source of SPEC mechanisms and merge with attribution:

| Section | Fate |
|---|---|
| §2 The inversion (agent loop over workflow DAG) + §2.2 expressiveness claim | MERGE → SPEC §1.1 rationale block; also anchors the REJ of DAG runtimes (feeds triage of `004_features_meta_dags.md`) |
| §3 Six planes | KILL as taxonomy; the *separations* it encoded survive as: Interaction→generated client contract, Cognition→`IPlanner`/`IContextManager`, Control→kernel, Workload→`IToolkit`+sandbox, Evidence→evaluator daemon, Evolution→Phase-2 plugins. Mapping table preserved once in ADR-M0-06 for archaeology |
| §4 layer topology, LT-1…LT-8 | MERGE → boundary-checker v2 config (Layer-0 lattice, SPEC §1); LT rules become executable config, not prose (I-8) |
| §5 operators-as-data + §5.3 registries freeze at composition | MERGE → SPEC §2.3 `compose()`; "operator" vocabulary retired in favour of plugin refs |
| §6 episode engine (loop, terminal states, two retries, no-progress detection, inner-loop invariants §6.5) | MERGE → SPEC §1.1/§1.4 scheduler; §6.4 re-grounding is now the `IContextManager.reground()` SPI method (closing D-10 by contract rather than by wish) |
| §7 environments & generality (adapter protocol, frozen atom set, irreversible effects) | MERGE → `IToolkit` SPI (§2.2); frozen verb set becomes the pack-declared verb vocabulary; §7.5 irreversibility analysis → SPEC §3 rollback policy taxonomy (`turn`/`checkpoint`/`compensate`) |

### 1.7 `04_vanguard_core_contracts_and_wire_schema_v040.md` (552 ln) — **REFACTOR & MERGE** (into generated reference + one annex section)
The only spec whose truth is partially machine-checked (schemas + golden vectors exist). Under I-8 it must pick a side: the schema-duplicating prose becomes **generated** (`docs/reference/`, rebuilt from `schemas/mhf/*.json` in CI), and only the *rationale* sections survive as normative prose:
- §0.3 canonicalisation rules + §0.4 large integers → MERGE into SPEC §1.2 (JCS envelope) — these are decisions, not schema restatements.
- §3 provenance six axes + §3.2 structural enforcement → MERGE into `annex/KERNEL.md` (they gate S1(e)).
- §5 capabilities & effect descriptors (why a verb set is insufficient; selector inclusion §5.3.1) → MERGE into `annex/KERNEL.md` §Grants.
- §6 budgets/reservations/leases → MERGE, amended to the **six-dimensional** reservation `{usd_micros, millis, tokens, bytes, turns, depth}` (SPEC §1.4; supersedes X-14's four-dimension freeze — recorded as ADR-M0-07 with reversal condition "a seventh dimension requires a consumer first").
- §8 model interface, §9 task/plan/proposal — KILL prose; the shapes are exactly what M1 codegen emits (`spi/types.py`); duplicating them in prose recreates D-29.
Everything else (naming conventions, wire rules): folded into the codegen tool's docstring.

### 1.8 `05_vanguard_kernel_capabilities_and_security_v040.md` (400 ln) — **KEEP VERBATIM** → `docs/annex/KERNEL.md`
The crown jewel. §2 dispatch sequence + §2.2 ordering rules + §2.3 failure-path table + §2.4 idempotence/replay + §3 grants + §4 attenuation + §5 authority predicate (including §5.2's "two operands, both of which have failed silently") + §6 perimeter ("containment is reported, never asserted") + §8 architecture tests + §9 threat model all survive intact — this is the normative twin of `kernel/dispatch.py`, which M1 ports verbatim.
**Three amendments only (each an ADR, per audit findings):**
1. **K-40 inverted** (ADR-M0-08): evaluator at a *separate identity outside* the worker perimeter is the binding text (audit D-32: as-built is stronger than spec; also closes `TSK-SPEC-003`).
2. **Alarm set = {F-21a, F-24}** (ADR-M0-09): intent-append failure pages (audit D-18; closes `TSK-SPEC-004`).
3. §7 self-modification: retained as pure prohibition; SA-1…SA-6 pipeline text struck (audit D-34: honoured non-build; SPEC §9 refuses the updater).
§0 audit stance and §1.2 mutability classes survive; the TCB **LOC-number tripwire** is struck from the annex and replaced by the AP-8 metric triple (mutation score, control-call-site coverage, E-COV) — the TCB *concept* (§1.1 declared transitive TCB) stays.

### 1.9 `06_vanguard_competence_memory_and_evidence_v040.md` (241 ln) — **EXTRACT TO ADR/PLUGIN**
Split along the live/dormant line the audit drew (D-39: types only; SPEC §9 gates the graph on the memory plugin):
- **LIVE, MERGE now:** §4.2 verifier unreachability, §4.3 the double probe, §4.4 inconclusive-as-first-class → `annex/KERNEL.md` §Evaluation + SPEC §2.2 `IEvaluationGate` semantics (`GateDecision` already carries the inconclusive path as `RETRY|ESCALATE`). §4.1 "an evaluator is not a universal judge" → SPEC §4.4 oracle preregistration rationale.
- **DORMANT, EXTRACT:** §2 four stores, §3 claim pipeline + contradiction, §5 promotion/activation/demotion + anti-ossification, §6 outer loop, §7 substrate invariance → `plugins/mhf.memory.graph/DESIGN.md` (Phase 3, SPEC §6.1) and `plugins/mhf.planner.meta-reflector/DESIGN.md` (Phase 2, SPEC §5). These are *design inputs to plugins*, carrying no normative force until the plugin's activation bundle lands (I-3).
- §1 governing asymmetry → one paragraph in SPEC §6.1. File deleted.

### 1.10 `07_vanguard_loop_engineering_and_measurement_v040.md` (284 ln) — **REFACTOR & MERGE** → `docs/annex/MEASUREMENT.md`
§5 measurement doctrine is the lab's constitution and survives nearly whole: paired designs, McNemar's exact test, multiple-comparison policy, the A/A noise floor, arm design, the instrument tuple (§5.6 — which review item M-18 says is still unwired; wiring is task S-M1-A-07), splits & contamination (§5.7). This annex is what makes Phase-2 promotion (SPEC §5.2, gate M5) statistically honest, and it is the direct answer to the audit's antithesis about statistical power — the doctrine already forbids selecting on noise; what's missing is task count, which deliverable 02 schedules.
- §4 distillation & promotion → MERGE into SPEC §7 (DPO harvest) as rationale.
- §1 three closure conditions, §2 loop levels, §10 search/process-rewards prep → EXTRACT to Phase-2 plugin design docs.
- §7 release pipeline, §8 transfer experiment, §9 experiment registry → KILL (§7 is the SA-* pipeline again; §8/§9 regenerate when M5 needs them, against the 200-task suite).

### 1.11 `08_vanguard_phase_0_build_plan_v040.md` (234 ln) — **KILL**
A build plan for a phase that shipped (and partially didn't — see the drift register). Superseded in full by the **M0–M6 progression** (SPEC §8, deliverable 02 §3, deliverable 03). Two ideas are extracted before deletion:
- §5 the must-fail suite → the *concept* (a test that must fail proves the gate can fire — handbook M6) is merged into ADR-M0-01's coverage discipline; the concrete MF-01…MF-37 roster is struck (audit: "stop citing MF-* as if they were `test/broken/`"; `TSK-TEST-001/002`'s bijection demand is satisfied by the new discipline, not by resurrecting the old IDs).
- §7 early warnings → folded into ADR-M0-05 risk register.
`TK-*` ticket namespace retired (also closes `TSK-TEST-003`'s complaint about minting `TK-*` in code).

### 1.12 `09_vanguard_decision_register_v040.md` (203 ln) — **KEEP VERBATIM** → `docs/adr/`
Append-only ADRs with **reversal conditions** — the document's own header calls this "the single practice most worth carrying forward," and the audit agrees. Migration is mechanical: each entry becomes `docs/adr/00NN-slug.md` preserving original ADR-numbers in front-matter; the append-only/supersede-by-citation rule becomes the `adr/` directory contract. Entries adjudicating between the two pre-v4 lineages (§3) are kept as history. New M0 decisions (ADR-M0-01…09 minted by this matrix) append to the same log.

### 1.13 `10_vanguard_deferred_and_rejected_register_v040.md` (67 ln) — **KEEP VERBATIM** → `docs/adr/DEFERRED_REJECTED.md`
The DEF/REJ discipline (every deferral names its reversal condition) is retained wholesale and is load-bearing for triage in deliverable 02: DEF-01 (authoring canvas), DEF-02 (semantic memory), REJ-10 (biological hierarchy in README — already a tracked task, `TSK-DOC-001`) are cited there. One structural change: entries whose subject was killed with the v4 corpus are annotated `[MOOT — subject deleted M0]` rather than removed (append-only holds).

### 1.14 `11_vanguard_design_convergence_evidence_v040.md` (85 ln) — **KILL**
Self-disqualifying by its own header: a **secondary reconstruction** of two primary design reviews that "are not preserved… and were not available when this summary was compiled," stating no contract, marked EVIDENCE-secondary. Evidence documents whose primary sources are lost carry archaeological interest and zero engineering value. One line survives into ADR-M0-06 (the plane-mapping archaeology entry): "two independent lineages converged on kernel-mediated effects and exterior evaluation" — as colour, not proof.

### 1.15 `12_vanguard_vision_annex_v040.md` (64 ln) — **KILL** (with a lesson extracted)
The tragedy document. It correctly diagnoses the failure mode — *"a metaphor in a specification is unfalsifiable"* — and builds a quarantine… which demonstrably failed: the cosmology escaped into `docs/00_executive/vision.md` v3.0.0 (14 tiers, "Turing Foam" → "Solar Systems") and the README's 10-level biological dictionary, both of which M0 deletes (AP-1; `TSK-DOC-001`/REJ-10). Quarantine is not a stable equilibrium for narrative; deletion is.
**Extract → ADR-M0-10 "No metaphysical taxonomies" (REJ class):** metaphors may appear in code comments and talks; no document under `docs/` may define a tier system, hierarchy-of-being, or biological/cosmological mapping. Reversal condition: none — the entry states plainly that nothing reopens it, per VG-10's own format. (Invariant I-10: "metaphors ship as comments, not architecture.")

### 1.16 `13_C_gts_mvp_program_and_engineering_plan.md` (695 ln) — **KILL** (three extracts)
The largest file in the corpus; a program plan (T0–T11 todo spine, sprint tables, a chapter for non-engineers) already superseded twice (13 → 13B → 13C) — a lineage that is itself evidence for AP-2. Superseded in full by M0–M6. Its `corrections_from_13B` front-matter, however, records three adjudications that must not be lost because production code embodies them:
- **ADR-M0-11:** *ALL effects are recorded; only PRIVILEGED sinks are capability-mediated; sink class is a descriptor field* (correction 2 — this is ADR-0051's content, matches as-built D-04, and closes `TSK-SPEC-001`'s demand to amend A-03).
- **ADR-M0-12:** *A tool is not an Episode; tools execute typed effects, episodes coordinate* (correction 3 — protects the `IToolkit`/`IPlanner` boundary).
- **ADR-M0-13:** *End-to-end disposable slice before deep contracts* (correction 1 — carried into the sprint plan as the M2 "walking skeleton" rule: a trivial echo-plugin traverses the full lifecycle before any real plugin is written).
T6's "coding harness is the first, **disposable**, point design" is vindicated by M3 (extraction to Domain Pack #1) and cited in ADR-M0-11's context. Everything else — deleted, not archived, per its own supersession convention.

---

## 2. Migration mechanics & acceptance

**Order of operations (inside sprint M0, Dev-A lane — see deliverable 03):**
1. Mint `docs/adr/` and land ADR-M0-01…13 + migrated VG-09/VG-10 corpus (pure adds — zero conflict surface).
2. Land `docs/annex/KERNEL.md` (VG-05 + three amendments) and `docs/annex/MEASUREMENT.md` (VG-07 §5).
3. Apply the SPEC merges (§§1.4–1.7, 1.9–1.10 rows marked MERGE) as one PR against `docs/SPEC.md`.
4. Delete: `01_specs/` (both trees), `00_executive/`, root THEORY/ASBUILT, `13_C`, generated rule files. Freeze DRIFTS under `adr/`.
5. Run the history rewrite (couples with SEC-01 secret purge and AP-7 artifact purge — one `git filter-repo` pass, one force-push window, one team re-clone).

**Acceptance (gate G-M0-DOCS):**
- `find docs -name '*.md' | wc -l` ≤ 30 (from ~120+).
- Zero RFC-2119 normative keywords outside `docs/SPEC.md` and `docs/annex/*` (grep gate).
- `check_markdown_links.py` green; no link into a deleted tree.
- Every MERGE row above resolves to a named SPEC/annex/ADR section (this matrix is the checklist; reviewer signs each row).
- ADR log is append-only from this commit forward (CI: `git diff` on `docs/adr/` permits additions and `superseded_by` front-matter edits only).
