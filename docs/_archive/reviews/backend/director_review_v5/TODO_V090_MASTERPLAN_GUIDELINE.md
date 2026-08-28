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

Historical process must not pollute the active development context.

When execution begins, remove or consolidate obsolete operational material that no longer helps implement Vanguard 0.9.x.

Examples include:

- superseded leadership workflows;
- obsolete development methodologies;
- approval-gate documents;
- duplicated TODO plans;
- stale sprint documents;
- old planning reports that are no longer authoritative;
- redundant execution-status documents.

Git history is the historical archive.

Do not preserve obsolete active documentation merely because it may be useful someday.

If historical information is needed later, retrieve it from Git.

Do not remove current technical contracts, still-valid architectural decisions, schemas, specifications, or compatibility requirements merely for cleanliness.

Technical cleanup must remain evidence-based.

---

## 10. Decision authority

When the Evolution Plan leaves an implementation detail open:

1. Dev A may decide immediately.
2. Dev B may decide independently when the choice is local and does not alter a shared contract or foundational invariant.
3. If evidence later proves the decision wrong, correct it and continue.

No additional governance process is required.

The repository is reversible.

---

## 11. Completion rule

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