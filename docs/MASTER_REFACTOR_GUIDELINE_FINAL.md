Foundation Lock: Docs/Spec/Roadmap/Sprint Refactor (v0.5.0 Concept Lock)

 What this wave is

 This is the intermediate review: lock the product identity and invariants, then make specs / roadmap / sprints tell one story. Code starts only after that lock is signed. This wave touches documentation and process artifacts only — no layer0/ scaffolding, no kernel port, no history rewrite, no deleting clients.

 Product identity to freeze: Vanguard is a meta-harness compiler — declarative manifests + versioned plugins compile into specialised coding-agent harnesses. The attenuation kernel, exterior judge, and measurement lab are the moat. Self-improvement and meta-cognition are Phase-2 plugins, not Layer-0 features.

 Two things this wave explicitly refuses to do:
 - Execute TECH_LEAD_REVIEW's M0 as literally written (mass delete, git filter-repo, drop GUI/IDE, scaffold layer0/). That couples an irreversible history rewrite to a concept lock that isn't signed yet, and it fights SYSTEM_SPEC_DRIFTS.md §2.5's own conclusion: the lattice and dispatch sequence are not the problem.
 - Continue docs/03_sprints/sprint_active.md's current v0.6.0 extraction sequencing as-is. Its "close remaining G-050 rows, then extract coding_*" plan is exactly what docs/TECH_LEAD_REVIEW/02_ROADMAP_BACKLOG_AND_REVIEW_TRIAGE.md §1 correctly supersedes — but its destination (microkernel + packs) is still right, and — see verification below — part of that extraction has already landed.

 Why two reviews must be merged, not picked

 Both reviews agree on the keep-set: S0–S12 kernel, JCS + golden vectors, exterior signed evaluator, harness-as-data manifests, FrozenHarness, the measurement lab, the CI boundary lattice.

 They disagree on three things this guideline must adjudicate:

 1. Rewrite target. DRIFTS: wire runtime/root.py + emit sites, then patch VG text. MHF: rebuild around the kernel (SPIs, registry, scheduler, packs).
 → Lock: MHF is the destination architecture. Remaining honesty holes (provenance wiring, E-COV, replay) become M1 acceptance gates, not a second implementation on the v0.4.x writer. Already-landed G-050 semantics (spans, child_return, EpisodeStarted, ApprovalResolved, apps/coding/ extraction — see verified status below) port with the kernel; they are not re-litigated as fresh work.

 2. v0.5.0 content. DRIFTS forbids playbooks, competence graph, fan-out, and an updater in this version. MHF's scheduler design has room for independence groups.
 → Lock: Phase-1 scheduler is sequential; independence groups are a named extension point, not an M1 feature (honour DRIFTS D-38). Competence graph / meta-reflector / genome mutation  C §5–6, honour D-39).

 3. Docs regime. MHF wants one SPEC.md + ADR log and deletion of THEORY/ASBUILT. DRIFTS wants VG-02/03/05 edited in place before code.
 → Lock: one living normative spec. The v0.4 corpus is archived, not deleted. DRIFTS.md is frozen as historical evidence, not maintained further as a living diff.

 mermaid
 flowchart TD
     subgraph sources ["Inputs this wave"]
         MHF["NEXT_GEN_META_HARNESS_SPECIFICATION.md"]
         Audit["CRITICAL_GAP_ANALYSIS_AND_AUDIT.md"]
         Matrix["01_SPECS_MIGRATION_MATRIX.md"]
         RoadTriage["02_ROADMAP_BACKLOG_AND_REVIEW_TRIAGE.md"]
         SprintPlan["03_SPRINTS_PARALLEL_EXECUTION_PLAN.md"]
         Drifts["SYSTEM_SPEC_DRIFTS.md"]
         Theory["SYSTEM_SPEC_THEORY.md"]
         Asbuilt["SYSTEM_SPEC_ASBUILT.md"]
     end
     Lock["docs/SPEC.md concept lock + annex/ + adr/"]
     Archive["docs/archive/v045/"]
     Road["docs/02_roadmap/"]
     Sprints["docs/03_sprints/"]
     sources --> Lock
     Theory --> Archive
     Asbuilt --> Archive
     Lock --> Road
     Lock --> Sprints

 Approaches considered

 ┌───────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                     Approach                      │                                                           Verdict                                                           │
 ├───────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ A. Execute M0 as written                          │ Fastest collapse, irreversible (filter-repo, frontend gone). Rejected for this wave.                                        │
 ├───────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ B. Patch the VG corpus in place (DRIFTS' S-spec   │ Honest to as-built, but keeps the triple-truth regime alive (audit's AP-2 anti-pattern). Rejected as the living model going │
 │ wave)                                             │  forward.                                                                                                                   │
 ├───────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ C. Concept lock + archive + one living tree       │ Recommended. Preserves archaeology, leaves history-rewrite / frontend-split / layer0/ port as later, separately-authorised  │
 │                                                   │ steps.                                                                                                                      │
 └───────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

 Target living tree (after this wave)

 docs/
   SPEC.md                 # the ONLY living normative spec (MHF v1 + lock deltas)
   annex/KERNEL.md
   annex/MEASUREMENT.md
   adr/                    # VG-09/10 migrated + ADR-M0-* + frozen DRIFTS
   02_roadmap/milestones.md
   02_roadmap/backlog.md
   03_sprints/sprint_active.md
   03_sprints/plans/...    # execution plan for M1+, staged not active
   archive/v045/           # THEORY, ASBUILT, 01_specs, 00_executive, reviews
   TECH_LEAD_REVIEW/       # kept as the review packet that produced the lock; stamped SUPERSEDED-BY-SPEC
   CONTRIBUTING.md         # 1-page mental models, explicitly non-normative

 Root SYSTEM_SPEC_*.md files move into docs/archive/v045/. CLAUDE.md / AGENTS.md / README.md then point at docs/SPEC.md.

 Correction to the source proposal: docs/scrum/ and docs/main_v4/ do not exist on disk — confirmed by direct listing; they were already renamed to docs/02_roadmap/+docs/03_sprints/ and docs/01_specs/backend/ respectively in a prior "docs: clean" pass. Any archive step referencing these paths is a no-op — don't let a git mv docs/scrum ... silently fail the sprint. docs/01_specs/backend/01_vanguard_engineering_handbook_v040.md is the closest current analog to "development guides"; check it (not a nonexistent docs/scrum/development_guides/) for still-operational content before archiving.

 docs/reference/ (generated schema docs) is not created until M1 codegen exists — do not hand-write a fake reference tree now.

 Authority after lock (read this on conflict)                                                                                                                                           

 1. docs/SPEC.md — living contracts. RFC-2119 language (MUST/SHALL/SHOULD) allowed here and in docs/annex/ only.
 2. docs/adr/ — decisions with reversal conditions; a newer ADR wins by citation, never by silent edit.
 3. docs/02_roadmap/milestones.md — version gates; cannot contradict SPEC.
 4. docs/03_sprints/sprint_active.md — execution board only.
 5. docs/archive/v045/ — evidence, not law. No ticket may cite it as a requirement.

 docs/TECH_LEAD_REVIEW/ stays in place as the design-review packet that produced the lock. Once SPEC.md lands, stamp it SUPERSEDED as living law; retained as review evidence.

 ---

 Step 0 — Inventory freeze and ground-truth verification (half day, no edits)

 1. Write docs/adr/DRIFT_REGISTER_v045.md as a copy of SYSTEM_SPEC_DRIFTS.md, headed "frozen at this commit, D-01…D-48 and X-* IDs remain stable." Do not "fix" drifts in the copy — it's a historical snapshot.
 2. Do not trust the [DONE] ✅ tags in docs/03_sprints/sprint_active.md at face value. The board's own header admits self-reported overclaiming: "DEV ALFA/GAMMA and DEV BETA briefs claimed 100% completion... Code audit... accepted four rows only." Each task in Wave 0/Wave 1 already carries its own verification snippet (e.g. rg "EpisodeStarted" vanguard/packages/agency vanguard/packages/runtime, specific unittest invocations) — run those exact commands rather than reading the checkmarks. This is the concrete method, notjust a caution.
 3. Verified from a direct read of docs/03_sprints/sprint_active.md (2026-08-18) — use this as the actual current-state baseline, not the TECH_LEAD_REVIEW audit's dcab22e snapshot:

 | DRIFTS finding                                             | Ticket                       | Board status                                                                                   | Action                                                                                                                                                                          |
 |------------------------------------------------------------|------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
 | D-05 span accumulation (_admit_turn_result)                | TSK-CORE-001                 | [DONE] (claimed)                                                                                                                                                           | Re-verify via grep; if real, this is a ported fact for M1, not new work                                                                                                         |
 | D-06 spawn() → child_return                                | TSK-CORE-002                 | [DONE] (claimed)                                                                                   | Re-verify; port with kernel if real                                                                                                                                             |
 | D-07/D-08 Trust.OPERATOR span + engine AuthorizationDenied | TSK-CORE-003/004             | [DONE] (claimed)                                                                                   | Re-verify                                                                                                                                                                       |
 | D-10 RegroundPolicy                                        | TSK-CTX-001                  | [DONE] — resolved by deletion, not by wiring                                                                                                                               | Update DRIFTS-derived guidance: this is closed, not an open "wire or delete" choice                                                                                             |
 | D-12 EpisodeStarted never emitted                          | TSK-LED-002                  | [DONE] (claimed)                                                                                   | Re-verify                                                                                                                                                                       |
 | D-13 ApprovalResolved in-process only                      | TSK-LED-003                  | [DONE] (claimed)                                                                                   | Re-verify                                                                                                                                                                       |
 | D-42 coding_session.py in domain/                          | TSK-EPIC-060-001 (S060-A-10) | [DONE] — moved to new apps/coding/ package, domain/ledger/__init__.py no longer exports it, apps registered as a 7th boundary-lattice package in tools/check_boundaries.py | Likely already resolved — verify, then update Step 1/M3 scope: M3's "extract coding pack" is are-extraction from apps/coding/ into packs/, not a first extraction from domain/ |
 | D-11 EVENT_KINDS writer enforcement                        | TSK-LED-001                  | [TODO]                                                                                                                                                                     | Still open — becomes an M1 gate (E-COV), not a v0.4.x patch                                                                                                                     |
 | D-02 dual ingress / EvaluationListener not composed        | TSK-EVAL-001                 | [TODO]                                                                                                                                                                     | Still open — the central "evaluator trigger is runtime-owned" defect is live; becomes an M1/M2 gate                                                                             |
 | D-14 Heartbeat                                             | TSK-LED-004                  | [TODO]                                                                                                                                                                     | Still open — M1 gate                                                                                                                                                            |
 | D-15 grant/budget kinds                                    | TSK-LED-005                  | [TODO]                                                                                                                                                                     | Still open — M1 gate                                                                                                                                                            |
 | D-21 one EffectRequest shape                               | TSK-SPEC-008 / S060-B-10     | [TODO]                                                                                                                                                                     | Still open — M1 gate (codegen'd single type)                                                                                                                                    |
 | D-33 AT-12                                                 | S060-B-11                    | [TODO]                                                                                                                                                                     | Still open — M2/perimeter gate                                                                                                                                                  |
 | D-27 TableWorld orphan                                     | S060-G-10                    | [TODO]                                                                                                                                                                     | Still open — M4 gate                                                                                                                                                            |                                                                                                        

 4. The guideline lists the still-open G-050 holes as M1 gates, not a v0.4.x patch sprint: TSK-LED-001 (unknown-kind writer check), TSK-EVAL-001 (evaluation trigger, D-02), TSK-LED-004/005 (heartbeat / budget kinds), TSK-SPEC-008 (one grant shape).
 5. Also note: git history shows a merged PR literally named feature_v050_meta-harness (62a127c) — some "meta-harness" framing already shipped under v0.5.0 branding before the TECH_LEAD_REVIEW packet existed. This is almost certainly the same Alfa/Beta/Gamma work reflected in sprint_active.md, not a separate untracked branch — there is no unmerged branchto freeze; the relevant work is already on main. (This corrects an earlier draft of this guideline, which assumed a separate feat/v060-microkernel-waist branch needed freezing — that branch name only appears in sprint_active.md's front-matter as the nominal working branch; the actual commits are already merged to main per git log.)

 ---

 Step 1 — Write the concept lock into SPEC (the real design work)

 Start from docs/TECH_LEAD_REVIEW/NEXT_GEN_META_HARNESS_SPECIFICATION.md. Copy to docs/SPEC.md, then apply these mandatory deltas before any merge-from-VG:

 - Preamble: product sentence above; non-claims from VG-02 §3 (matrix 1.5) merged line-by-line into SPEC §9.
 - Invariants I-1…I-10 stay. Add I-11: Phase-1 scheduler is sequential; concurrency is a later scheduler property with a measurement gate (honours D-38).
 - A-1…A-6 stay. Record ADR-M0-03: handbook's "four pluggable things" → five SPIs (IPlanner, IMemoryEngine, IToolkit, IContextManager, IEvaluationGate) plus first-party IModelProvider/ISandbox/stores. A sixth SPI requires a design review, not a PR.
 - As-built OPTIMIZATIONs that win (DRIFTS §2.4 / X-*, cite each): sink-class mediation (ADR-0051/D-04); evaluator outside worker (K-40 inverted/D-32); alarm set {F-21a, F-24} (D-18); inbox/outbox (D-17); schema-driven translator as the model waist (D-28); REQ-* as the PR namespace (D-45); measurement stays outside packages (D-40); MetaLoopEngine stays deleted — outer loop is a plugin at a scheduler slot (D-41 + SPEC §5.1).
 - As-built DETERIORATIONs M1 must close: provenance on the production path (D-05/D-06 — verify against Step 0's table first, don't duplicate work if already landed); E-COV 100%;ApprovalResolved ledgered (claimed [DONE] — re-prove under E-COV, don't just trust the checkmark); one EffectRequest (D-21). Do not list D-42 (coding projection out of domain/) as open — Step 0 found it already resolved via apps/coding/; instead task M3 with re-extracting apps/coding/ into packs/.
 - Honour table (SPEC §9, do not reopen): SA-1…SA-6 updater, competence graph before the memory plugin exists, playbook runtime, MCP-as-authority, metaphysical taxonomies (ADR-M0-10), GUI/TUI as a backend gate.
 - Word target: SPEC ≤ ~9k words. If a section restates a schema, it doesn't belong in SPEC.
 - Boundary-lattice note: the current lattice already has 7 packages, not 6 — apps/ was added alongside domain/ports/kernel/agency/runtime/adapters per S060-A-10. Any SPEC/annex passage describing "the hexagon" should reflect this, not the original 6-package diagram.

 ---

 Step 2 — Mint the ADR log

 Follow docs/TECH_LEAD_REVIEW/01_SPECS_MIGRATION_MATRIX.md §1.12–1.13 mechanically:

 1. Split docs/01_specs/backend/09_vanguard_decision_register_v040.md into docs/adr/00NN-slug.md files, preserving original ADR numbers in front-matter (no renumbering, no collision risk — ADR-M0-* is a separate namespace).
 2. Copy docs/01_specs/backend/10_vanguard_deferred_and_rejected_register_v040.md → docs/adr/DEFERRED_REJECTED.md; annotate moot entries [MOOT — subject archived] rather than deleting them.
 3. Mint ADR-M0-01…ADR-M0-13 exactly as the matrix names them (coverage discipline, identifier namespaces, five SPIs, stack, risk, plane-mapping archaeology, six-dimensionreservation, K-40 invert, F-21a alarm, no metaphysics, sink-class mediation, tool≠episode, walking skeleton).
 4. Six-dimension Reservation: allowed only because the M1 scheduler is the named consumer (turns/depth). Do not add evaluations (DRIFTS D-24 — no dimension without a consumer). Reversal condition: a seventh dimension requires a consumer first (record as ADR-M0-07).                                                                                               

 ---

 Step 3 — Land the annexes (keep verbatim + amendments)

 - docs/annex/KERNEL.md from docs/01_specs/backend/05_vanguard_kernel_capabilities_and_security_v040.md. Apply only: K-40 invert, alarm set {F-21a, F-24}, strike the SA-1…SA-6 self-mod pipeline text. Strike the TCB LOC-number tripwire from annex prose; keep the TCB concept. Replacement metrics (mutation score, control-call-site coverage, E-COV) are M1 CI — do not pretend they exist yet. Until then, tools/check_tcb_budget.py remains the living size gate (matches the still-active TCB ≤ 1438 line in current sprint_active.md law §0). That dual state (annex describes the future metric, the old gate still runs) is recorded as an ADR, not a silent drop.
 - docs/annex/MEASUREMENT.md from VG-07 §5 only (paired designs, McNemar, A/A floor, instrument tuple). Phase-2 loop prose goes to plugin design stubs later, not into the annex.

 ---

 Step 4 — Apply MERGE rows into SPEC

 Use the matrix (§1.4–1.7, 1.9–1.10) as a signed checklist, one PR (or commit series) with a reviewer tick per row:

 - Handbook mental models M1, M3–M6, M8–M11 → SPEC; M2 superseded by ADR-M0-03; M7 → a Phase-3 plugin note.
 - Charter mission + non-claims + falsifiable claims rewritten as M-gates with proof commands.
 - VG-03: keep loop-over-DAG inversion and episode-engine discipline; kill the six-plane vocabulary; LT-* become the future boundary-checker-v2 config (not prose).
 - VG-04: keep canonicalisation / provenance / grants / budgets as decisions; kill schema-duplicating prose.
 - VG-06: live verifier-unreachability content moves into KERNEL.md/SPEC; the dormant competence-graph pipeline stays out of living law.
 - VG-08 / VG-11 / VG-12 / 13C: kill as living docs; the extracts that matter are already captured in ADR-M0-11…13.

 ---

 Step 5 — Archive, do not delete

 Move (git mv), do not rm:

 - docs/01_specs/ (backend + frontend)
 - docs/00_executive/
 - docs/scrum/ — does not exist; skip, it was already renamed to docs/02_roadmap/+docs/03_sprints/ in a prior pass
 - docs/reviews/ — after copying triage verdicts into the new backlog (Step 6). Include docs/reviews/todo/deepseek_v050_review_and_v060_plan.md in the same triage pass — itstemplated/generic content and mismatched terminology (ALFA/BETA lanes phrased differently from the current board, "ArtifactNode/Edge Merkle-DAG", "Semantic Vector Index") make it a low-confidence source; expect REJECTED/CLOSED disposition unless a manual read finds something concretely reusable.
 - Root SYSTEM_SPEC_THEORY.md, SYSTEM_SPEC_ASBUILT.md, SYSTEM_SPEC_DRIFTS.md (DRIFTS already copied under docs/adr/)
 - duplicate docs/main_v4/ — does not exist; already consolidated into docs/01_specs/backend/, nothing to move

 Add docs/archive/v045/README.md: "Not normative. The living spec is docs/SPEC.md. CI must not treat archive RFC-2119 language as law."

 Keep docs/TECH_LEAD_REVIEW/ in place (review evidence). For "development guides": check docs/01_specs/backend/01_vanguard_engineering_handbook_v040.md for still-true operational content (layer boundaries, measurement rules, manifest authoring) and copy that into docs/CONTRIBUTING.md or a short docs/guides/; archive the rest. Do not leave two onboardingstories.

 Frontend specs: archived with the corpus, not killed from git. "Clients live elsewhere" is an ADR for a later repo-split wave, not this one.                                           

 ---

 Step 6 — Rewrite the roadmap

 Replace docs/02_roadmap/milestones.md and docs/02_roadmap/backlog.md using docs/TECH_LEAD_REVIEW/02_ROADMAP_BACKLOG_AND_REVIEW_TRIAGE.md, with these edits:

 - v0.5.0 = MHF M0–M4 (docs lock + Layer 0 + plugin runtime + Coding Pack #1 + harness parity). The former "v0.6.0 Molecular Lattice" / v0.8 graphs / v0.9 meta labels map onto named Phase-2/3 plugin milestones, not a parallel ladder. This is a renumbering — sprint_active.md's current v0.5.0/v0.6.0 split (and the merged feature_v050_meta-harness PR title) predate this scheme; record the mapping explicitly in the roadmap so old PR/commit references aren't confusing later.
 - This wave is M0-docs only. M0-code (skeleton, schemas, pytest migration) and M0-purge (filter-repo, artifact blobs, frontend trees) are explicitly deferred tickets on the new board, not part of this PR.
 - Close every legacy TSK-* with superseded_by: <epic-or-task-id>. Kill TSK-FE-* as backend gates; do not delete the GUI tree.
 - Standing rule from deliverable 02: an item enters v0.5.0 only if it lands in Layer 0, the plugin runtime, or the Phase-1 Coding Pack.
 - Carry the review triage (Aider repo-map, Pi lean pack, AST patch, four-protocol model waist, Pi DAG mechanism as branch_id, etc.) into the new backlog verbatim.

 ---

 Step 7 — Rewrite the active sprint

 Replace docs/03_sprints/sprint_active.md with an M0-docs board (not the full two-engineer M0 from deliverable 03 — that model is sized for parallel code work; this wave is mostly single-owner editorial work). Copy the drop-in template from docs/TECH_LEAD_REVIEW/03_SPRINTS_PARALLEL_EXECUTION_PLAN.md §4, then strike S-M0-A-05 (history rewrite), S-M0-B-01…06 (code skeleton), and frontend deletion. Move those into docs/03_sprints/plans/m0-code-and-purge.md as a staged-not-active plan.                                                        

 File the full M1–M2 two-lane plan under docs/03_sprints/plans/ so it's ready when needed, not active now.

 Preserve the current board's convention of an explicit "Explicitly not this sprint" closing section (it already exists in sprint_active.md §5 and is good practice) — carry it forward into the new board with this wave's own boundaries (see the summary list at the end of this document).

 ---

 Step 8 — Hygiene gates (living tree only)

 - tools/check_markdown_links.py green; living docs do not link into docs/archive/ except the archive README.
 - Grep: RFC-2119 MUST/SHALL only in docs/SPEC.md and docs/annex/.
 - README.md: delete the LEVEL 0–9 biological hierarchy (D-46 / REJ-10 / ADR-M0-10); point at docs/SPEC.md.                                                                             
 - CLAUDE.md: replace "normative corpus is docs/main_v4/" with a pointer to docs/SPEC.md (+ docs/annex/, docs/adr/) — this file governs Claude Code's own behaviour in the repo and must not go stale.
 - Also fix while here (plain bugs, independent of the review decision): tools/repo_paths.py's docs_scrum()/docs_sprint() helpers still point at the dead docs/scrum; test/test_repo_paths.py::test_repo_root_from_this_file still asserts it exists; tools/check_schema_archaeology.py fails through the same dead-path chain. Fix all three so python3 -m unittest test.test_repo_paths and check_schema_archaeology.py are green going into this wave, not just coming out of it.
 - Do not retarget tools/rule_test_map.py or drop TCB/test-count badges in this wave — those are M1 CI. Optionally add a comment in CI docs noting the audit's AP-8-flagged metrics get  replaced when M1 lands its real coverage gates.

 ---                                                                                                                                                                                    

 Step 9 — Spec self-review before calling the foundation done                                                                                                                           

 Check SPEC.md for: TBD/TODO markers, SPEC-vs-annex contradictions, SPEC-vs-honour-table conflicts, and any matrix MERGE row with no landing section. Fix inline. Then stop — do not start layer0/ or kernel ports.
                                                                                                                                                                                        

 Keep living (edit into SPEC/annex/adr/roadmap/sprints): MHF spec + audit + three execution packets (as inputs, then stamped superseded); VG-05 (kernel annex), VG-07 §5 (measurement annex), VG-09, VG-10; DRIFTS as a frozen ADR appendix; handbook models, charter non-claims, loop-over-DAG, the LT lattice idea, JCS/grants/budget decisions; lab + telemetry doctrine (stays outside vanguard/packages/); kernel / JCS / evaluator / manifests / FrozenHarness / boundary checker — described, not moved.

 Archive (git mv, readable, not law): SYSTEM_SPEC_THEORY.md, SYSTEM_SPEC_ASBUILT.md; docs/01_specs/**, docs/00_executive/**, docs/reviews/**; frontend spec tree, vision v3, 13C, VG-08, VG-11, VG-12. Sprint evidence stays where it is until the later purge wave; do not filter-repo now.

 Kill as living claims (stop asserting these): triple-truth regime (THEORY vs. ASBUILT vs. DRIFTS as competing law); cosmology/biological README taxonomy; MF-01…MF-37 as if they matched test/broken/; TableWorld as an H0 witness until registered or cut (D-27); "N tests green" / TCB LOC as a safety property on its own (AP-8); competence graph / vg why as a shipped pipeline (D-39); plugin architecture as if it already exists (AP-9 — SPEC must say it's to be built in M2).

 ---
                                                                                                                                                                                        
 What to use as reference while editing

 ┌────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                          Need                          │                                               Source                                                │
 ├────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤                       
────────────────────────────────────────────────────────────────────────────────────────────┤
 │ Keep/kill register + I-1…I-10                          │ docs/TECH_LEAD_REVIEW/CRITICAL_GAP_ANALYSIS_AND_AUDIT.md                                            │
 ├────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ Per-file spec fate                                     │ docs/TECH_LEAD_REVIEW/01_SPECS_MIGRATION_MATRIX.md                                                  │
 ├────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ Backlog/milestone/review verdicts                      │ docs/TECH_LEAD_REVIEW/02_ROADMAP_BACKLOG_AND_REVIEW_TRIAGE.md                                       │
 ├────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤                        │ Later two-lane M1/M2 plan                              │ docs/TECH_LEAD_REVIEW/03_SPRINTS_PARALLEL_EXECUTION_PLAN.md                                         │                    ├────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤            │ As-built wins vs. restorations                         │ SYSTEM_SPEC_DRIFTS.md §2.4, §4.1–4.5, Appendix A/B (→ docs/adr/DRIFT_REGISTER_v045.md after Step 0) │
 ├────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ Verbatim kernel/measurement text                       │ docs/01_specs/backend/05_*.md, 07_*.md                                                              │
 ├────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ ADR/DEF/REJ corpus                                     │ docs/01_specs/backend/09_*.md, 10_*.md                                                              │                       
 ├────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ What code actually does                                │ SYSTEM_SPEC_ASBUILT.md (archive after copy)                                                         │
 ├────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ Identifier/rule names                                  │ SYSTEM_SPEC_THEORY.md (archive after SPEC absorbs them)                                             │                       
 ├────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ What's actually already landed (verified, not claimed) │ The Step 0 table above, backed by docs/03_sprints/sprint_active.md's embedded verification commands │
 └────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────┘                       
 ---

 Explicitly not this wave

 git filter-repo / secret-history purge (SEC-01) / repo-size ≤ 3MB · deleting vanguard-gui/, vanguard-ide/, the Ink client · scaffolding layer0/, schemas/mhf/, pytest migration · porting or rewriting kernel//ports//runtime · closing remaining G-050 holes in the old writer (they become M1 gates) · word-budget CI for the old VG caps.                             

 Those belong on the rewritten backlog as M0-purge and M0-code, started only after SPEC.md is signed.
                                                                                                                                                                                        
 Verification for this wave

 - find docs -name '*.md' | wc -l trending down (not a hard ≤30 gate this wave — that's M0-full; this wave only excises the spec/executive/reviews trees, not everything).
 - tools/check_markdown_links.py, python3 -m unittest test.test_repo_paths, tools/check_schema_archaeology.py all exit 0.
 - Zero RFC-2119 keywords outside docs/SPEC.md / docs/annex/.
 - tools/check_boundaries.py, tools/check_tcb_budget.py still exit 0 (docs-only wave must not touch the 7-package lattice or TCB budget).                                               
 - Step 0's ground-truth table is fully re-verified (each rg/unittest command actually run, not assumed) before it's cited anywhere in SPEC.md or the new roadmap.