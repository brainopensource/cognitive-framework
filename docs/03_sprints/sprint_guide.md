# DONE

The director Performed a full independent technical review and refactor plan of the entire project—code, architecture, docs, tests, migration path, and product goals—and, if the current plan is materially flawed, replace it with a cleaner plan from first principles while preserving only what remains justified by the evidence and the project goals.

---

# DONE

Now he is doing waves 1-4 planning


Act as the **Engineering Director / Chief Engineer for AETHER / Vanguard v0.6**, using the full context you now have from the repository, Concept Lock, SPEC, ADRs, GAMMA, Director Review, gap register, tests, and previous forensic work.

Wave 0 is being handled separately by the engineering team. Assume that work will be presented to you when ready.

Your responsibility now is to determine, from the **actual state of the project**, what Director / Principal / Staff-level work will create the most leverage for development of the remaining v0.6 foundation.

The approved destination remains the v0.6 Concept Lock and the foundation stop condition defined in the authoritative documents. Do not reopen settled architectural decisions unless live evidence exposes a material contradiction.

## Objective

Prepare the project so that, after Wave 0, senior developers can execute the remaining foundation work without having to rediscover the architecture, invent missing contracts, duplicate abstractions, or make decisions that should have been settled at Principal/Director level.

Please inspect the **code and documentation together** and decide what should now be:

* clarified;
* designed;
* consolidated;
* scaffolded;
* implemented at leadership level;
* or intentionally left for the Tech Lead and developers.

Use your own judgment about where leadership effort has the highest leverage.

The existing Wave 1–4 descriptions are **outcomes and constraints**, not a prescribed implementation checklist. Refine or reorganize their internal milestones, sprints, dependencies, and backlog where repository evidence suggests a better execution path, provided the locked architecture and Wave 4 foundation objective remain intact.

## Engineering posture

Favor the characteristics already established by the project:

* one authoritative runtime rather than parallel implementations;
* evidence and executable behavior over architectural claims;
* fail-closed authority boundaries;
* event-derived state and explicit ownership;
* small trusted core with capabilities added through composition;
* reuse and convergence rather than rebuilding mature mechanisms;
* one canonical contract where duplication would create semantic drift;
* narrow vertical integration before broad implementation;
* abstractions justified by the real product path rather than hypothetical future systems;
* clear falsification/acceptance criteria for important architectural properties;
* simple, modular and maintainable code that senior developers can extend safely.

Use these principles as guidance, not as a requirement to preserve any particular internal file decomposition proposed by earlier planning drafts.

## Leadership contribution

You have access to multiple strong engineering agents. Use them where the work benefits from **Principal/Staff-level reasoning or cross-system understanding**.

It is acceptable to implement or scaffold difficult foundational code where doing so meaningfully removes architectural uncertainty for the team.

It is equally acceptable to leave implementation to developers when a clear contract, reference flow, ownership boundary, and completion criterion are sufficient.

Avoid using leadership capacity for routine glue, mechanical cleanup, exhaustive unit testing, or implementation details that competent developers can derive safely once the architecture is clear.

## Development readiness

When you finish, a developer should be able to understand:

* which code is production truth;
* which abstractions and implementations must be reused;
* where each major responsibility belongs;
* how authority, state, composition, plugins, execution and evidence connect;
* how the remaining duplicate runtime material converges;
* what the canonical execution path is;
* what dependencies determine implementation order;
* which parts are already scaffolded versus still developer-owned;
* and what objective evidence proves a milestone complete.

Where this knowledge currently exists only implicitly across code, reviews and ADRs, make it accessible without creating another competing specification.

Resolve only ambiguities that could materially produce architectural drift, incompatible implementations, duplicate mechanisms, or wasted development.

## Planning and handoff

Bring the development planning material up to the level needed for execution.

Use your judgment to produce an appropriate hierarchy such as:

**Foundation outcome → milestone → sprint → task**

for the remaining Waves 1–4.

The plan should be detailed enough for assignment and execution, but not so detailed that it designs every local implementation decision in advance.

Update the appropriate roadmap/backlog/milestone material and make:

`docs/03_sprints/sprint_active.md`

a practical handoff board.

Clearly distinguish work that is:

* ready for implementation;
* partially scaffolded and awaiting completion;
* still requiring Tech Lead refinement;
* deliberately left to developer-local design;
* or still requiring Principal/Director judgment.

If previous planning tables or sprint suggestions are suboptimal, replace them with what you believe is the better decomposition based on the live system.

## Foundation integration target

Keep the eventual foundation MVP in view while making these decisions.

The remaining work should converge toward **one real execution path** in which a composed agentic harness can perform a genuine coding task through the production substrate and leave trustworthy state and evidence behind.

Use that real path as an architectural integration test when deciding whether abstractions, migrations, module boundaries, or scaffolds are useful.

The exact implementation route is yours to determine from the repository.

## Scope

Concentrate on the **core v0.6 MVP foundation**.

Do not spend substantial leadership effort on ancillary engineering process, Git conventions, developer prompts, Frontend, UI, speculative scale work, large plugin catalogs, or exhaustive test coverage.

Tests and proofs should be sufficient to protect the important architectural seams; the development team can deepen coverage as implementation progresses.

Focus note: Prioritize Waves 1, 2, and 4, where Principal/Director-level reasoning has the highest leverage: the trust spine, runtime convergence, and the final real coding-agent path. Use these to make the whole system understandable end-to-end—how agents, events, ledger/state, capabilities, plugins, orchestration, reusable components, and autonomous coding execution fit together—so developers inherit not just tasks, but a clear mental model of how and why the framework works, how it stays modular/DRY, and how its parts compose into a reusable agentic substrate.

## Final handoff

At completion, leave the repository and documentation in a state where you can briefly explain:

1. what high-leverage work leadership completed;
2. which important ambiguities were resolved;
3. what architecture/code was intentionally scaffolded;
4. how you decomposed the remaining development;
5. what developers should work on next;
6. what the Tech Lead still owns;
7. the recommended developer reading path;
8. the canonical integration flow they should preserve;
9. any remaining decision that could materially threaten the v0.6 foundation;
10. whether, in your judgment, the team can now execute through the foundation MVP without further architectural intervention.

The standard is not that leadership completes all remaining implementation.

The standard is that **the difficult foundational decisions are settled, the important seams are coherent, and developers can spend their time building rather than interpreting the architecture.**



# DONE 

### Developer A — Evidence / Signing → Wire / Contracts

Act as **Senior Developer A** for AETHER / Vanguard v0.6.

You are working in parallel with **Developer B**.

Read first:

* `docs/03_sprints/plans/000_CANONICAL_EXECUTION_PATH.md`
* `docs/03_sprints/plans/wave1_trust_spine.md`
* `docs/03_sprints/plans/wave2_convergence.md`
* `docs/02_roadmap/backlog.md`
* `docs/03_sprints/sprint_active.md`
* `docs/05_adr/0076-foundation-execution-decisions-canonical-artifacts.md`

Your ownership is:

**Wave 1**

* Primary owner of **Sprint 1.1 — Signed Verdict Loop / Evidence lane**.
* Complete tasks `1.1-A` through `1.1-G` according to the wave plan and their acceptance evidence.
* Coordinate with Developer B because the evaluator gateway and verdict path must eventually use the canonical ledger/emitter path from Sprint 1.2.
* Do not duplicate JCS, selector logic, verdict construction, event writing, or generated types.
* When Sprint 1.1 and Developer B’s Sprint 1.2 are both green, work together on **Sprint 1.3**. Take primary responsibility for the parts closest to composition, identity, verdicts, generated contracts, and trajectory/evidence integration; coordinate ownership with Developer B where surfaces overlap.

**Wave 2**

* Do **not** start Wave 2 until the Wave 1 / M-1 exit gate is green.
* Then take primary ownership of **Sprint 2.1 — Absorb the Wire and Contracts**: JSON-RPC/UDS, generated wire types, SPI Protocols, and removal of `layer0` dependencies from those contract surfaces.
* Work with Developer B during Sprint 2.2 where parity and deletion depend on the contracts you absorbed.
* Never repair `layer0` as a destination; absorb useful contracts into `vanguard/packages/`.

Follow the canonical docs rather than inventing alternate implementation paths. Anything marked `TECH-LEAD` or `DIRECTOR` must be escalated instead of silently decided.

Your result is complete when your assigned Sprint 1.1 work is green, Sprint 1.3 integration is complete with Developer B, and your Wave 2 contract/wire responsibilities satisfy the documented acceptance gates without creating duplicate abstractions.  

---

### Developer B — Ledger / State → Convergence / Runtime

Act as **Senior Developer B** for AETHER / Vanguard v0.6.

You are working in parallel with **Developer A**.

Read first:

* `docs/03_sprints/plans/000_CANONICAL_EXECUTION_PATH.md`
* `docs/03_sprints/plans/wave1_trust_spine.md`
* `docs/03_sprints/plans/wave2_convergence.md`
* `docs/02_roadmap/backlog.md`
* `docs/03_sprints/sprint_active.md`
* `docs/05_adr/0076-foundation-execution-decisions-canonical-artifacts.md`

Your ownership is:

**Wave 1**

* Primary owner of **Sprint 1.2 — Ledger Truth / State lane**.
* Complete tasks `1.2-A` through `1.2-F` according to the wave plan and acceptance evidence.
* Establish the canonical `LedgerEmitter`, lineage, writer authority, cold replay, durable-intent recovery, and removal of hand-built envelope paths.
* Coordinate with Developer A because the signed evaluator/verdict flow must use your canonical emitter/state path.
* Do not create alternate event envelopes, replay stores, append APIs, selectors, or state authority.
* When your Sprint 1.2 and Developer A’s Sprint 1.1 are both green, work together on **Sprint 1.3**. Take primary responsibility for the parts closest to ledger/state, capability ceilings, budget/attenuation, receipt lineage, and trajectory assembly; coordinate exact ownership with Developer A where surfaces overlap.
* Items marked `TECH-LEAD`, especially `1.2-C` and `1.3-C`, require review before implementation/merge.

**Wave 2**

* Do **not** start Wave 2 until the Wave 1 / M-1 exit gate is green.
* Then take primary ownership of **Sprint 2.2 — Parity, Deletion, and Runtime Convergence**, with Tech Lead involvement for parity keep/kill decisions.
* Drive the in-place `root.py` decomposition, convergence cleanup, duplication removal, and eventual deletion of `layer0` authority/runtime pieces only after behavioral parity is proven.
* Coordinate with Developer A because Sprint 2.2 depends on the wire/contracts absorbed during Sprint 2.1.
* Preserve one runtime authority, one event model, one selector algebra, one writer path, and one composition path.

Follow the canonical docs rather than inventing local architecture. Anything marked `TECH-LEAD` or `DIRECTOR` must be escalated.

Your result is complete when your assigned Sprint 1.2 work is green, Sprint 1.3 integration is complete with Developer A, and Wave 2 converges the repository onto one canonical runtime without deleting `layer0` behavior before parity proves it is safe.  


### Developer A — Close Wave 1 / Sprint 1.3

Act as **Senior Developer A** and finish **Wave 1** together with Developer B.

Re-read the latest:

* `docs/03_sprints/plans/000_CANONICAL_EXECUTION_PATH.md`
* `docs/03_sprints/plans/wave1_trust_spine.md`
* `docs/03_sprints/sprint_active.md`
* `docs/02_roadmap/backlog.md`
* `docs/02_roadmap/milestones.md`
* `docs/SPEC.md`
* ADR-0076 and relevant annexes

Sprint 1.1 is your completed foundation; Developer B owns completion of 1.2. Once both lanes are green, **execute your ownership of Sprint 1.3 and close the shared integration seams required by the documented M-1 exit gate**.

Use the live repository and canonical documents to determine the implementation details. Coordinate directly with Developer B on overlapping state/evidence/trajectory surfaces; do not independently implement the same mechanism.

Maintain production-quality Senior/Staff standards: canonical contracts, minimal abstractions, DRY code, strong typing, deterministic behavior, explicit authority, fail-closed semantics, and no compatibility hacks or speculative architecture.

Do not start Wave 2 early and do not weaken acceptance evidence to declare Wave 1 complete. Escalate decisions explicitly assigned to Tech Lead/Director.

**Result:** Wave 1 is not finished when your code is finished; it is finished when **Sprint 1.3 is integrated with Developer B and the complete M-1 exit gate is demonstrably green**. Report remaining blockers if it is not.

---

### Developer B — Close Wave 1 / Sprint 1.2 + 1.3

Act as **Senior Developer B** and drive your remaining work through **Wave 1 closure** together with Developer A.

Re-read the latest:

* `docs/03_sprints/plans/000_CANONICAL_EXECUTION_PATH.md`
* `docs/03_sprints/plans/wave1_trust_spine.md`
* `docs/03_sprints/sprint_active.md`
* `docs/02_roadmap/backlog.md`
* `docs/02_roadmap/milestones.md`
* `docs/SPEC.md`
* ADR-0076 and relevant annexes

First finish and verify any remaining **Sprint 1.2** acceptance evidence. Do not hide or work around honest failures.

Once 1.1 and 1.2 are both green, **execute your ownership of Sprint 1.3 with Developer A and drive the combined implementation through the documented M-1 exit gate**.

Use the plans and current code to determine what remains rather than relying on this prompt as an implementation specification. Coordinate shared surfaces with Developer A and preserve one canonical implementation for every architectural responsibility.

Maintain production-quality Senior/Staff standards: simple modular code, DRY contracts, explicit ownership, deterministic state, strong failure semantics, maintainability, and no unnecessary abstractions or duplicate paths.

Anything assigned to `TECH-LEAD` or `DIRECTOR` remains an escalation/review point rather than a developer-local architectural decision.

**Result:** leave **Wave 1 / M-1 green and ready to authorize Wave 2**, or report the exact remaining blocker and evidence showing why Wave 2 must remain closed.


### Tech Lead — Wave 1 Final Gate / M-1 Authorization

Act as **Senior Tech Lead / Project Lead** for AETHER / Vanguard v0.6.

Perform the **final Wave 1 / M-1 engineering gate review** using the current integrated repository, Developer A/B work, and the authoritative documents:

* `docs/03_sprints/plans/000_CANONICAL_EXECUTION_PATH.md`
* `docs/03_sprints/plans/wave1_trust_spine.md`
* `docs/03_sprints/sprint_active.md`
* `docs/02_roadmap/backlog.md`
* `docs/02_roadmap/milestones.md`
* `docs/SPEC.md`
* ADR-0076 and relevant annexes

Do **not** redo the developers' work or redesign Wave 1. Review the integrated result and resolve only the remaining decisions that require Tech Lead authority.

In particular, independently adjudicate the reported **F-08 ambiguity** from the actual contract, fixture, kernel behavior, and intended falsifier; determine whether it represents a real production defect, an incorrect/stale falsifier, or another contract mismatch. Do not modify evidence merely to obtain green.

Also close the outstanding Tech Lead review points identified by the Wave 1 plan, including `1.2-C` and `1.3-C`, based on the architecture and live implementation.

Verify the complete **M-1 exit gate**, not individual developer completion. Treat the canonical `vanguard/packages/` production path as the subject of record while preserving explicitly deferred `layer0` defects for Wave 2 where the plans require that sequencing.

**Final result:** return exactly one engineering decision:

* **M-1 GREEN — WAVE 2 AUTHORIZED**, with any minor follow-up recorded for its proper later wave; or
* **M-1 BLOCKED**, identifying only the concrete blockers that must be corrected before Wave 2 begins.

If green, update the appropriate planning/sprint status so both developers can immediately proceed into the documented Wave 2 lanes.


# DOING

### Developer A — Continue Canonical Execution Plan

Act as **Senior Developer A** for AETHER / Vanguard v0.6.

Continue from your completed work and treat the repository's current authoritative planning stack as the source of truth. Before proceeding, re-read the latest versions of:

* `docs/03_sprints/plans/000_CANONICAL_EXECUTION_PATH.md`
* the **current wave plan** under `docs/03_sprints/plans/`
* `docs/03_sprints/sprint_active.md`
* `docs/02_roadmap/backlog.md`
* `docs/02_roadmap/milestones.md`
* `docs/SPEC.md`
* relevant ADRs/annexes, especially ADR-0076

Determine your next work from those documents and the **current repository state**, not from this prompt or previous assumptions.

Your objective is to advance your assigned lane through the next documented milestone while preserving the canonical architecture and integrating cleanly with Developer B's work.

Work to **production-quality Senior/Staff engineering standards**: minimal and coherent abstractions, strong typing/contracts, DRY implementation, explicit ownership, fail-closed behavior where required, deterministic behavior, maintainability, clear boundaries, and reuse of canonical mechanisms rather than parallel implementations.

Prefer the smallest correct implementation satisfying the architecture and acceptance evidence. Do not introduce speculative abstractions, compatibility layers, duplicate paths, or unnecessary complexity.

Run the relevant acceptance evidence and tests defined by the plans. Treat failures as engineering evidence rather than weakening gates to obtain green.

If repository reality conflicts materially with the plan, stop that specific decision and document/escalate it rather than silently redesigning the architecture.

**Result:** leave your lane integrated, reviewable, documented where necessary, and demonstrably compliant with the current milestone/exit criteria so the next dependent work can proceed without architectural cleanup.

---

### Developer B — Continue Canonical Execution Plan

Act as **Senior Developer B** for AETHER / Vanguard v0.6.

Continue from your completed work and independently establish the current state before making further changes. Read the latest:

* `docs/03_sprints/plans/000_CANONICAL_EXECUTION_PATH.md`
* the **current wave plan** under `docs/03_sprints/plans/`
* `docs/03_sprints/sprint_active.md`
* `docs/02_roadmap/backlog.md`
* `docs/02_roadmap/milestones.md`
* `docs/SPEC.md`
* relevant ADRs/annexes, especially ADR-0076

Use those documents plus the live implementation to determine exactly what your lane owns next and what dependencies must already be satisfied.

Continue toward the next documented foundation milestone, coordinating with Developer A only at shared architectural seams and integration points.

Maintain **SOTA production engineering quality**: canonical implementations over forks, modular and cohesive components, DRY contracts, explicit state/authority ownership, deterministic behavior, narrow interfaces, strong failure semantics, and code that can be safely extended by subsequent developers.

Do not optimize for merely making tests pass. Optimize for making the **documented architecture true in the production runtime**, with tests and acceptance evidence proving that result.

Avoid speculative refactoring, unnecessary generalization, temporary duplicate architectures, or decisions belonging to the Tech Lead/Principal/Director.

Where the documentation deliberately assigns a decision upward, escalate it. Where it deliberately leaves local implementation to the developer, use sound engineering judgment and keep the solution simple.

**Result:** complete your next assigned lane to its documented acceptance/exit criteria, integrate it cleanly with Developer A's work, and leave the canonical runtime simpler, more coherent, and ready for the next dependent milestone.


Yes. **The logic is now correct, but I would tighten both prompts to explicitly anchor them to the Tech Lead’s newly opened Wave 2 ownership split.** Otherwise the generic “determine your next work” language leaves unnecessary ambiguity.

### Developer A — Wave 2 / Contract & Wire Lane

Act as **Senior Developer A** for AETHER / Vanguard v0.6.

**M-1 is GREEN and Wave 2 is authorized.** Continue from the integrated repository state after the Tech Lead’s final Wave 1 adjudication.

Before implementation, re-read the **latest committed/current versions** of:

* `docs/03_sprints/plans/000_CANONICAL_EXECUTION_PATH.md`
* `docs/03_sprints/plans/wave2_convergence.md`
* `docs/03_sprints/sprint_active.md`
* `docs/02_roadmap/backlog.md`
* `docs/02_roadmap/milestones.md`
* `docs/SPEC.md`
* ADR-0076 and relevant annexes

The Tech Lead has updated the board and opened **your Wave 2 lane around the wire/contracts work**, currently identified as **2.1-A/B/C**. Treat the current documentation and repository as authoritative if task details have evolved.

Execute your assigned Wave 2 work to its documented acceptance criteria. The objective is **convergence toward the canonical `vanguard/packages/` runtime**, not improvement of `layer0/` as a competing destination.

Coordinate with Developer B at shared seams, particularly where their convergence work consumes the contracts/wire surfaces you establish. Do not independently cross into their ownership merely because their work is visible in the shared tree.

Maintain Senior/Staff production quality: canonical abstractions, strong contracts and typing, DRY implementation, narrow interfaces, deterministic behavior, explicit ownership, minimal complexity, and reuse rather than parallel mechanisms.

Do not weaken acceptance evidence to obtain green. If live repository evidence materially contradicts the plan or requires a Tech Lead/Principal decision, escalate that specific issue rather than silently choosing a new architecture.

**Result:** complete your documented Wave 2 lane, leave its canonical contract/wire surfaces integrated and demonstrably correct, and make the dependent convergence work straightforward for Developer B.

---

### Developer B — Wave 2 / Runtime Convergence Lane

Act as **Senior Developer B** for AETHER / Vanguard v0.6.

**M-1 is GREEN and Wave 2 is authorized.** Continue from the integrated repository state after the Tech Lead’s final Wave 1 adjudication.

Before implementation, re-read the latest:

* `docs/03_sprints/plans/000_CANONICAL_EXECUTION_PATH.md`
* `docs/03_sprints/plans/wave2_convergence.md`
* `docs/03_sprints/sprint_active.md`
* `docs/02_roadmap/backlog.md`
* `docs/02_roadmap/milestones.md`
* `docs/SPEC.md`
* ADR-0076 and relevant annexes

The Tech Lead has updated the board and opened **your initial Wave 2 lane**, currently identified around **2.1-D/E**, followed by the convergence work assigned to you by the current Wave 2 plan. Use the live documentation rather than this prompt for the exact implementation details and dependencies.

Execute your lane toward **one canonical production runtime**. Coordinate with Developer A where your work depends on their wire/contracts lane, and respect the documented ordering around parity, migration and removal of duplicate runtime material.

In particular, treat the Tech Lead’s **2.2-A parity triage as a real convergence gate**: do not remove or rewrite duplicate `layer0/` behavior merely to simplify the tree before the documented evidence says it is safe.

Maintain Senior/Staff production quality: cohesive modules, explicit authority/state ownership, canonical mechanisms instead of forks, DRY contracts, deterministic behavior, narrow boundaries, minimal compatibility debt, and straightforward maintainability.

Tests and falsifiers are engineering evidence, not targets to game. Escalate genuine architectural contradictions or decisions reserved for leadership rather than resolving them locally.

**Result:** complete your documented Wave 2 lane and leave the runtime materially closer to the M-2 condition: **one coherent implementation, with duplication removed only when parity and the current plan authorize it.**

---

### Wave 2 Closure & M-2 Re-gate Resolution (2026-08-21)

All requirements from the Round-3 blocker have landed on the canonical `vanguard/packages/` path (Developer A, Round 4):
- **Deterministic Reducer Fold Rules:** Landed in `domain/ledger/reducer.py` for `EffectFailed` (closing in-flight effects with status="failed" and outcome/error), `EffectRejected` (status="rejected"), `BudgetExhausted` (accumulating debits and releasing lease), `CapabilityAttenuated` (recording child grant with `parentGrantId` and attenuated constraints), `TurnStarted` (recording active turn in `state_transitions`), and the 5 `Plugin*` lifecycle events (`PluginResolved`, `PluginActivated`, `PluginQuiesced`, `PluginRetired`, `PluginFaulted` tracked in `LedgerState.plugins`).
- **Fold Property Test Suite:** `test/contracts/test_event_coverage.py::CataloguedKindsAreFoldedOrAllowlisted` proves every kind in `EVENT_KINDS` is folded or explicitly named in `UNFOLDED_ALLOWLIST`, with zero silent fall-through to `unknown_events`.
- **Static Linters & Test Suites Green:** All 14 tests in `test_event_coverage.py`, all 15 tests in `test_ledger_truth.py` (including `ColdReplayParity`), and all static linters (`check_boundaries.py`, `check_tcb_budget.py`, `check_domain_blindness.py`, `check_isolation_policy.py`, `check_duplication.py --enforce`, `check_stale_paths.py`, `check_markdown_links.py`, `scan_secrets.py`) pass cleanly.

**Next Milestone:** Enter **Wave 3 (Extensibility Foundation)** per `docs/03_sprints/plans/wave3_extensibility.md`.