# TODO_V090_MASTERPLAN_GUIDELINE

## Purpose

Use `VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md` as the authoritative technical assessment and implementation direction for Vanguard / AETHER 0.9.x.

This guideline does **not** replace, summarize, duplicate, or reinterpret that plan.

Its only purpose is to define the **development operating model** used to execute the plan with maximum engineering velocity and minimum process overhead.

If this guideline and the Evolution Plan appear to conflict:

- the Evolution Plan remains authoritative for technical findings, architecture, defects, refactors, simplifications, product gaps, and implementation direction;
- this guideline is authoritative for team structure, autonomy, workflow, validation cadence, and development process.

---

## 1. Operating principle

The project will be executed by two Senior Developers working in parallel.

The default loop is:

**Understand → Decide → Implement → Test → Fix if needed → Integrate → Continue**

Normal engineering work must not stop for ceremony, approval, or documentary process.

Git history, branches, commits, tests, diffs, and pull requests provide sufficient reversibility for ordinary development.

A reversible engineering decision must not be treated as an irreversible organizational event.

---

## 2. Dev A — Principal Developer

Dev A is the principal technical authority for the implementation.

Dev A has full autonomy to:

- make architecture and implementation decisions;
- resolve ambiguity;
- change sequencing;
- modify contracts when technically justified;
- refactor or simplify code;
- remove obsolete code or documentation;
- change tests and validation strategy;
- perform migrations;
- update implementation documentation;
- resolve conflicts between code and documentation;
- redistribute work between lanes;
- integrate completed work;
- decide when engineering evidence is sufficient to continue.

Dev A does not wait for external leadership approval for normal engineering decisions.

Dev A may use up to approximately **1,000,000 OpenRouter tokens** for focused engineering work, including agent execution tests, model comparisons, benchmarks, workflow validation, context experiments, evaluator experiments, regression diagnosis, and implementation validation.

The budget should be used to resolve concrete engineering uncertainty, not for repetitive analysis.

---

## 3. Dev B — Senior Implementation Developer

Dev B is a Senior Developer responsible for substantial coding work in parallel with Dev A.

Dev B follows:

- `VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md`;
- current code;
- current contracts;
- current specifications;
- assigned implementation objectives.

Dev B has broad autonomy over implementation details and should resolve routine technical decisions independently.

Dev B should primarily spend time on implementation, integration, debugging, tests, fixes, and product-facing backend work.

Dev B must not wait for Dev A when the answer can be determined safely from code, tests, interfaces, specifications, or normal Senior engineering judgment.

Dev B may use OpenRouter only with zero-cost/free models unless explicitly authorized otherwise.

---

## 4. Parallel execution

Work must be divided into two lanes that can progress independently for long periods.

The exact split must be derived from the Evolution Plan and actual code coupling.

General preference:

- Dev A owns foundational, cross-cutting, architecture-sensitive, runtime-critical, and integration-sensitive work.
- Dev B owns substantial parallel implementation and product-facing work behind stable contracts.

This division is intentionally flexible.

Dev A may move tasks between lanes whenever doing so improves throughput.

Shared interfaces, schemas, ports, and contracts should be stabilized early enough to avoid unnecessary blocking between Dev A and Dev B.

Artificial dependencies between lanes must not be created.

---

## 5. What is explicitly NOT a development gate

The following must not block ordinary implementation unless they expose a real technical problem:

- independent reviewer approval;
- leadership approval;
- countersignatures;
- evidence ceremonies;
- milestone acceptance ceremonies;
- repeated architecture ratification;
- mandatory external review;
- formal scientific acceptance;
- documentary status synchronization;
- mandatory full-suite execution after every change;
- requirement to freeze or formally qualify every intermediate phase before continuing;
- approval chains between Dev A and Dev B.

Scientific evidence, formal release evidence, independent review, or stronger qualification may still be produced when useful or when required for a specific external claim.

They are not prerequisites for ordinary coding progress.

---

## 6. Testing rule

Both developers validate their own work.

Use the smallest test set that provides sufficient confidence for the change being made.

Developers may freely run unit, integration, falsifier, regression, replay/recovery, end-to-end, and benchmark tests, including redundant tests when additional confidence is valuable.

During normal implementation, prefer focused tests relevant to the changed subsystem.

Broader suites should be run at meaningful integration points and near release closure.

Tests are engineering tools, not organizational gates.

A failure blocks forward progress only when it demonstrates a real issue such as incorrect runtime behavior, violated invariant, broken shared contract, security failure, causal or event-integrity failure, persistence or recovery failure, incompatible migration, or a genuine dependency between unfinished components.

If a test is obsolete, redundant, or tests superseded behavior, fix, replace, consolidate, or remove it.

---

## 7. Pull requests and integration

Branches and pull requests are integration mechanisms, not permission mechanisms.

Each developer may produce coherent PRs containing substantial completed work.

Prefer PRs that are:

- large enough to represent meaningful progress;
- small enough to understand and debug;
- accompanied by the tests relevant to the change.

Avoid both dozens of tiny process-driven PRs and massive unrelated changes that are difficult to integrate.

Dev A controls final integration sequencing and resolves conflicts between the lanes.

---

## 8. Documentation during implementation

Do not duplicate the Evolution Plan.

Do not create new architecture reports unless implementation exposes a genuinely new architectural issue.

Update documentation only when necessary to keep the active repository aligned with the code.

Execution documents should remain concise.

The main execution files are:

- `docs/03_execution/milestones.md`
- `docs/03_execution/backlog.md`
- `docs/03_execution/sprint_active.md`
- `docs/03_execution/sprint_upcoming.md`

They should contain only:

- remaining work;
- Dev A / Dev B ownership;
- real dependencies;
- concise Definition of Done;
- relevant validation;
- current status.

The Evolution Plan explains **what must change and why**.

The execution documents explain **who is doing what, in what order, what is active, and when it is done**.

Do not copy technical analysis from the Evolution Plan into these files.

---

## 9. Obsolete methodology and documentation

The current documentation tree is considered legacy material unless proven necessary for the current Vanguard 0.9.x product.

Do not preserve historical documentation merely because it exists.

Git is the historical archive.

Before deleting legacy documentation, extract only the information that is still required to understand, implement, operate, extend, or preserve compatibility with the current system.

Then perform a hard reset of the active documentation surface.

### Required process

1. Inspect the current documentation tree.
2. Extract every still-valid:

   * architectural invariant;
   * public contract;
   * protocol;
   * schema rule;
   * security constraint;
   * compatibility requirement;
   * non-obvious design decision;
   * operational requirement.
3. Move or rewrite that information into the new minimal Vanguard 0.9.x documentation.
4. Verify that no required technical rule exists only in a file scheduled for deletion.
5. Delete the obsolete documentation from the active branch.
6. Do not create an `_archive` replacement containing the same historical clutter.
7. Rely on Git history when historical material is needed.

### ADR reset

The existing ADR collection must not automatically survive into Vanguard 0.9.x.

Treat old ADRs as historical inputs, not active authority.

For every old ADR ask:

> Does a developer implementing Vanguard today genuinely need this decision to understand a live invariant, compatibility requirement, security property, or architectural constraint?

If the answer is no, delete it from the active tree.

If the answer is yes, do not preserve a large historical ADR merely for provenance.

Create a new, concise Vanguard 0.9.x ADR expressing only the current decision.

New ADRs should be short.

An ADR should normally contain only:

* Decision
* Context
* Why
* Consequences
* Relevant code/contracts

Do not use ADRs as research papers, project diaries, milestone reports, review archives, implementation tutorials, or duplicated specifications.

The code should explain implementation.

Architecture documentation should explain structure and flows.

Contracts and schemas should explain interfaces.

ADRs should explain only decisions that cannot be understood from those surfaces alone.

The exact structure may differ if a simpler organization is better.

The important rule is:

**Every active document must justify the context it consumes.**

### Delete aggressively

Delete from the active branch when superseded:

* historical reviews;
* old leadership plans;
* old convergence plans;
* obsolete milestone narratives;
* superseded sprint documents;
* duplicated specifications;
* duplicated architecture descriptions;
* obsolete ADRs;
* historical experimental plans;
* old evidence explanations;
* planning diaries;
* governance methodology;
* superseded TODOs;
* documents whose only purpose is explaining how the project reached its current state.

Do not preserve them in another active folder.

They remain available through Git history.

### Final standard

A new Senior Developer or AI coding agent should be able to understand the entire active backend documentation without reading project history.

The active repository should describe only:

* what Vanguard is now;
* how it works now;
* which invariants matter now;
* which contracts exist now;
* how to extend it now;
* what work remains now.

Everything else belongs in Git history.

---
## 10. Documentation Folder Proposed Structure

### Documentation Architecture and Target Folder Structure

The Vanguard 0.9.x documentation reset must not merely delete obsolete Markdown; it must replace the current fragmented documentation taxonomy with a small, explicit, predictable information architecture. The current numbered structure (`01_law/`, `02_decisions/`, `03_execution/`, `04_architecture/`, `05_contracts/`, `06_protocols/`, `07_engineering/`, `08_theory/`, `09_diagrams/`, `09_tools/`, `_archive/`) should be treated as legacy organization. Preserve only information that remains technically necessary, migrate it into the new structure below, and then remove the obsolete directories rather than maintaining two parallel documentation systems.

The preferred active structure is:

```text
docs/
├── README.md
├── SPEC.md
│
├── architecture/
│   ├── overview.md
│   ├── system-context.md
│   ├── components.md
│   │
│   ├── runtime/
│   │   ├── execution-model.md
│   │   ├── kernel.md
│   │   ├── agency.md
│   │   ├── orchestration.md
│   │   ├── events-ledger.md
│   │   ├── artifacts.md
│   │   ├── recovery.md
│   │   └── concurrency.md
│   │
│   ├── extensibility/
│   │   ├── agents.md
│   │   ├── plugins.md
│   │   ├── packs.md
│   │   ├── tools.md
│   │   ├── models.md
│   │   ├── evaluators.md
│   │   └── adapters.md
│   │
│   ├── state/
│   │   ├── identity.md
│   │   ├── memory.md
│   │   ├── persistence.md
│   │   └── configuration.md
│   │
│   └── diagrams/
│       ├── system.md
│       ├── runtime.md
│       ├── agent-lifecycle.md
│       └── recovery.md
│
├── reference/
│   ├── contracts/
│   ├── protocols/
│   ├── events.md
│   ├── configuration.md
│   ├── cli.md
│   ├── service-api.md
│   └── schemas.md
│
├── guides/
│   ├── development.md
│   ├── testing.md
│   ├── debugging.md
│   ├── add-agent.md
│   ├── add-plugin.md
│   ├── add-pack.md
│   ├── add-tool.md
│   ├── add-model.md
│   ├── add-adapter.md
│   ├── create-workflow.md
│   ├── benchmarking.md
│   └── release.md
│
├── decisions/
│   ├── README.md
│   └── only-current-and-important-ADRs.md
│
├── execution/
│   ├── milestones.md
│   ├── backlog.md
│   ├── sprint_active.md
│   └── sprint_upcoming.md
│
└── theory/
    ├── README.md
    ├── causal-computation.md
    ├── resource-model.md
    ├── agent-composition.md
    ├── evaluation-and-learning.md
    └── self-improvement.md
```

Each top-level directory has exactly one purpose.

`architecture/` explains **how AETHER is structured and how its major subsystems interact**. This is where the Kernel, Agency layer, Runtime, orchestration, event ledger, artifacts, recovery, concurrency, memory, plugins, packs, tools, models, evaluators, adapters, identities and configuration should be explained. These pages describe responsibilities, boundaries, data flow, lifecycle, state transitions, causal relationships and important implementation constraints. They must not duplicate every class or function.

`reference/` contains **exact technical facts that developers need to look up**. Contracts, protocols, event vocabulary, schemas, CLI semantics, service commands and configuration fields belong here. Reference documentation should be precise and close to the actual code/schema representation. If information answers “what is the exact shape, field, command, event, interface or protocol?”, it belongs here rather than in architecture.

`guides/` contains **task-oriented development instructions**. A developer asking “how do I add a plugin?”, “how do I create an agent?”, “how do I add a tool?”, “how do I test a new adapter?”, or “how do I create a workflow?” should find one short guide instead of reconstructing the procedure from ADRs, architecture documents and old sprint plans.

`decisions/` contains only **small, currently relevant architectural decisions whose rationale is not obvious from code, architecture documentation or contracts**. ADRs must not become a second specification, a project history, a research paper, a milestone report, a design tutorial, or a development diary. The Vanguard 0.9.x reset should aggressively reduce the existing ADR set. If an old ADR still contains an important current decision, extract that decision into a new concise ADR and delete the historical document from the active tree. Git preserves the original reasoning.

`execution/` contains only **current project execution state**: milestones, backlog, active work and immediately upcoming work. It must never become long-term architectural documentation or historical project management. Completed historical execution material belongs in Git history, not in the active context.

`theory/` exists only for **the mathematical, scientific or conceptual material that genuinely helps explain AETHER's design**: causal computation, resource/budget models, agent composition, evaluation, learning, metacognition or self-improvement. Theory must be clearly separated from implemented architecture. A theoretical idea must not appear to be a production feature merely because it has a Markdown file.

Subsystems must therefore be documented as a hierarchy inside the appropriate information category rather than becoming independent top-level documentation silos. For example, the Kernel should have an architectural page such as `architecture/runtime/kernel.md`, exact kernel-related contracts should live under `reference/contracts/`, and instructions for modifying or testing kernel-sensitive code should live in `guides/`. The same rule applies to plugins, agents, orchestration, memory and events. This prevents a new `kernel/`, `plugins/`, `agents/`, `events/`, `runtime/`, `memory/`, and `orchestration/` documentation tree from each accumulating its own duplicated architecture, reference material and tutorials.

The documentation should explicitly model the major AETHER building blocks:

```text
AETHER
├── Kernel / Authority / Capabilities / Budgets
├── Agency / Turn Semantics / Context
├── Runtime / Composition / Lifecycle
├── Events / Ledger / Reducers / Projections
├── Artifacts / Content-Addressed Storage
├── Persistence / Replay / Recovery / Checkpoints
├── Agents / Scope / Lineage / Spawn
├── Workflow / Topology / Scheduling / Concurrency
├── Memory / Retrieval / Context
├── Plugins / Packs / Tools
├── Models / Routing
├── Evaluation / Measurement / Telemetry
└── Clients / Commands / Transports
```

These are architectural building blocks, not necessarily folders at the root of `docs/`. They should be documented at the level where understanding them is useful without reproducing the source tree.

The final test for the documentation architecture is simple: a new Senior Engineer or AI coding agent should be able to answer four different questions without reading historical documents:

1. **What is AETHER and how is it architected?** → `SPEC.md` + `architecture/`
2. **What is the exact contract or protocol?** → `reference/`
3. **How do I implement or extend something?** → `guides/`
4. **Why was a non-obvious architectural choice made?** → `decisions/`

If information does not clearly belong to one of those purposes, it should be questioned before being retained. The goal of the reset is not to rename the current documentation tree; it is to eliminate duplicated authority, historical context pollution, and subsystem documentation sprawl, leaving one small and coherent documentation system for the current Vanguard/AETHER product.


## 11. Decision authority

When the Evolution Plan leaves an implementation detail open:

1. Dev A may decide immediately.
2. Dev B may decide independently when the choice is local and does not alter a shared contract or foundational invariant.
3. If evidence later proves the decision wrong, correct it and continue.

No additional governance process is required.

The repository is reversible.

---

## 12. Completion rule

Continue implementation until the technical work defined by `VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md` is complete.

Do not stop after planning documents are updated.

Do not treat documentation completion as product completion.

Do not create new gates between implementation blocks unless a real technical dependency exists.

The project is finished when the required backend behavior, simplification, refactoring, integration, product capabilities, packaging, and validation defined by the Evolution Plan are implemented and working.

---

## Final rule

**The Evolution Plan defines the technical work. This guideline defines how Dev A and Dev B execute it.**

Optimize the development process for:

- autonomy;
- parallelism;
- engineering judgment;
- fast feedback;
- reversible decisions;
- sufficient validation;
- minimal coordination overhead;
- completion of the working product.

Do not optimize for ceremony.


## Quick Notes Todos
| Task                                       | Complexidade | Motivo                                               | Perfil ideal                  |
| ------------------------------------------ | -----------: | ---------------------------------------------------- | ----------------------------- |
| Limpar docs, backlog, milestones e versão  |       20/100 | Baixo risco técnico; mostly consistency              | Dev Senior                    |
| Unificar bootstrap, config, CLI e service  |       55/100 | Vários entrypoints e semântica duplicada             | Staff Engineer                |
| Packaging + install limpo + state dir      |       40/100 | Trabalho de integração previsível                    | Dev Senior                    |
| Recovery real: kill, restart, resume       |       70/100 | Persistência, idempotência e causalidade             | Staff Engineer                |
| Coding + Explainer agents úteis            |       60/100 | Integra runtime, tools, context e artifacts          | Senior Agentic Engineer       |
| Plugins + composição multi-agent           |       70/100 | Authority, lifecycle e isolamento                    | Staff / Agentic Systems       |
| Refactor runtime/session/service           |       75/100 | Alto risco de regressão semântica                    | Principal / Architect         |
| Eventos, SQLite, checkpoints, concorrência |       85/100 | Causalidade, ordering, performance e recovery juntos | Principal Distributed Systems |
| Catálogo Research/RAG/Planner-Critic       |       65/100 | Mais composição que ciência nova                     | Senior AI Agentic Engineer    |
| Fechamento 0.9.x completo                  |       60/100 | Integração ampla, mas foundations já existem         | Dev A + Dev B                 |