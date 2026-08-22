# AETHER Documentation Refactor Prompt

Act as the Documentation Architect, Principal Systems Architect, Tech Lead, and Repository Governance Auditor for AETHER.

## Objective

Refactor and reorganize the repository documentation into a progressive-disclosure, anti-sprawl architecture without losing, weakening, silently changing, or duplicating any requirement, decision, falsifier, historical evidence, milestone gate, or development instruction.

The final documentation must let humans and AI agents navigate:

```text
README → system overview → relevant law/ADR → current milestone/task → named falsifier → code
```

A contributor must be able to stop at the appropriate depth or continue into full architectural, theoretical, forensic, and historical detail.

## Authoritative architectural inputs

- `docs/07_reviews/archive/proposals/001_alfa_review_full_decision.md`
- `docs/07_reviews/archive/proposals/006_fi_review_full_gptsol_proposal.md`

These are ratification/design provenance only. They do not override:

- normative SPEC and annexes;
- accepted ADRs;
- schemas and executable falsifiers;
- the active sprint board.

## Core thesis

> One fact, one canonical owner, multiple reading depths, executable proof at every binding boundary.

## Hard safety rules

1. Do not modify production code.
2. Do not change runtime behavior, schemas, or test semantics during this documentation refactor.
3. Accepted ADRs are append-only:
   - Do not silently rewrite their decisions.
   - Correct or supersede decisions only through a new ADR.
4. Archived research, reviews, and proposals are immutable:
   - Move them if authorized, repair links, and add a standard non-normative banner where this does not alter their substantive text.
   - Never rewrite their arguments or conclusions.
5. Do not rewrite SPEC from scratch:
   - Refactor surgically.
   - Preserve every normative clause and falsifier binding.
   - Any semantic change requires explicit identification and Director approval.
6. Before deleting or moving anything:
   - inventory the exact path;
   - identify unique content and incoming references;
   - map its canonical destination;
   - record a recovery commit;
   - ask the operator for approval of the exact destructive move set.
7. Preserve unrelated working-tree changes.
8. Use `git mv` for approved moves and perform path changes atomically.
9. Do not mix this documentation restructure with RF-23/RF-25 production implementation.
10. Do not declare completion until before/after verification proves no requirements or links were lost.

## Target information architecture

```text
README.md
  L0 — short human entry point, current status, quick start, reading paths

AGENTS.md
  L0/L5 — single tool-neutral operating contract for humans and AI agents

CONTRIBUTING.md
  L5 — contribution workflow, PR requirements, coding and review standards

docs/
├── README.md
│   L0 — sole documentation precedence ladder and tier directory
│
├── 01_law/
│   ├── SPEC.md
│   ├── KERNEL.md
│   └── MEASUREMENT.md
│   L1 — normative RFC-2119 law, mechanisms, formal contracts and invariants
│
├── 02_architecture/
│   ├── OVERVIEW.md
│   ├── c4_context.md
│   ├── c4_container.md
│   ├── boundaries.md
│   ├── sequences.md
│   ├── invariants.md
│   └── verification_map.md
│   L2 — descriptive system topology and verified architecture views
│
├── 03_decisions/
│   ├── INDEX.md
│   └── ADR files
│   L3 — append-only architectural decisions
│
├── 04_execution/
│   ├── milestones.md
│   ├── sprint_active.md
│   ├── falsifiers.md
│   └── done/
│   L4 — macro gates, current work, RF allocation and compressed evidence
│
├── 05_engineering/
│   ├── development.md
│   ├── security.md
│   ├── testing.md
│   ├── documentation.md
│   └── pr_checklist.md
│   L5 — development standards and operational procedures
│
└── _archive/
    ├── README.md
    ├── reviews/
    ├── proposals/
    ├── research/
    └── sprints/
    L6 — frozen, non-authoritative provenance
```

Treat this tree as a target to validate, not an unquestionable mandate. If an existing canonical path is better preserved to avoid needless churn, explain the trade-off and retain it. Prefer conceptual consolidation over cosmetic path movement.

## Required methodology

### PHASE 0 — Establish the migration ledger

Create an inventory covering every current Markdown document with:

| Old path | Current role | Authority | Unique content | Incoming references | Proposed destination | Action | Recovery source |
|---|---|---|---|---|---|---|---|

Allowed actions:

- KEEP
- REFACTOR
- SPLIT
- MOVE
- ARCHIVE
- DELETE_AFTER_MIGRATION

Record:

- current commit containing the complete pre-refactor corpus;
- dirty working-tree state;
- active RF-23/RF-25 test status;
- current link, stale-path, and RF-ID linter results.

Do not mutate files during this phase.

### PHASE 1 — Define authority and metadata

Establish this precedence:

1. Normative law: SPEC and normative annexes
2. Accepted decisions: ADR catalog
3. Current execution: active sprint board
4. Macro sequencing: milestone ladder
5. Descriptive architecture and engineering standards
6. Research, reviews, proposals, and historical execution evidence

Use a standard header on living documentation:

```yaml
---
id: stable-document-id
class: navigation | law | architecture | decision | execution | standard | archive
authority: normative | binding-decision | execution | descriptive | advisory
canonical_for:
  - unique-topic-name
status: living | append-only | frozen | superseded
owner: role-or-team
version: applicable-version
last_verified: YYYY-MM-DD
supersedes: []
superseded_by: null
---
```

Requirements:

- `canonical_for` values must be globally unique.
- Archived documents must not claim canonical ownership.
- Only normative law may use RFC-2119 language normatively.
- Descriptive documents must link to law instead of restating requirements.

### PHASE 2 — Refactor navigation

#### README.md

- Target approximately 150 lines.
- Include mission, universal mechanism, current milestone, production lattice, quick-start commands, and reading paths.
- Do not duplicate detailed contracts, milestone ladders, ADR prose, or historical investigations.

#### AGENTS.md

- Keep as the only agent/contributor instruction file.
- Include authority precedence, architectural boundaries, security rules, testing commands, documentation anti-sprawl rules, and developer workflow.
- Do not maintain `CLAUDE.md`, model-specific instructions, or competing contributor contracts.

#### docs/README.md

- Make it the sole documentation directory and precedence map.
- Provide role-based reading paths:
  - newcomer;
  - feature developer;
  - security reviewer;
  - architect;
  - incident/forensic investigator;
  - AI coding agent.
- State explicitly which tiers may authorize implementation.

### PHASE 3 — Refactor normative law safely

For SPEC and normative annexes:

1. Build a clause inventory before edits:

   | Clause | Canonical topic | Bound ADR | Bound RF/test | New location |
   |---|---|---|---|---|

2. Separate:
   - mechanism and invariant;
   - schema/state-machine contract;
   - historical rationale;
   - milestone timing.
3. Keep mechanism and normative behavior in law.
4. Move rationale to ADRs or architecture references.
5. Move timing, owner and status to execution documents.
6. Preserve clause identifiers or provide a stable alias map.
7. Do not weaken or alter requirements while moving them.
8. Verify RF allocations and bound test references before and after each extraction.

The law must answer “what must always be true,” never “who is working on it this week.”

### PHASE 4 — Build progressive architecture documentation

Create or consolidate descriptive architecture views for:

- C4 context: users, operators, providers, evaluator and sandbox boundaries;
- C4 containers: Python substrate, TypeScript CLI, SQLite WAL, sandbox, evaluator daemon;
- canonical lattice: `domain ← ports ← kernel ← agency ← runtime → adapters`;
- A-B-C-D operating foundation;
- Decision, State and Evidence planes;
- S0–S12 authorized-effect sequence;
- composition and `D_H` freeze sequence;
- trajectory assembly and `D_R/D_X` identity sequence;
- cold death, reconciliation and continuation sequence;
- plugin lifecycle FSM;
- M-3 Named Component Graph compilation;
- exterior signed-evaluation flow;
- future M-6 mediated spawn;
- future M-7 stigmergic/concurrent scheduling;
- future M-9/M-10 retrieval, macros and promotion as exterior mechanisms.

Rules:

- Architecture documentation is descriptive.
- Every invariant links to SPEC/ADR/test.
- Diagrams introduce no new requirements.
- Prefer Mermaid or checked text diagrams over unverified images.
- Label future architecture as `PLANNED` and current architecture as `AS-BUILT`.

### PHASE 5 — Normalize ADRs

Do not rewrite accepted ADR substance.

For every active ADR, verify it has:

- status and date;
- context;
- decision;
- scope and milestone;
- affected invariants;
- consequences and trade-offs;
- one primary bound falsifier;
- negative cases;
- reversal criteria;
- links to relevant SPEC clauses.

Update the ADR index, not old ADR bodies, when adding navigation metadata or historical recovery references. If a substantive correction is required, draft a superseding ADR and stop for Director approval.

### PHASE 6 — Make execution documentation lean

#### milestones.md

- Keep only M-0 through M-10 outcomes, dependencies, version mapping, entry gates and exit gates.
- No file-level task assignments.
- No completed investigation narratives.

#### sprint_active.md

- Target approximately 100–150 lines.
- Keep only:
  - current milestone and goal;
  - active gates;
  - owners;
  - exact files or ownership zones;
  - dependencies and shared hotspots;
  - named red tests;
  - merge order;
  - definition of done;
  - immediate next milestone entry condition.
- Compress completed waves into:

  | Milestone | Result | Evidence pointer | Closed date |
  |---|---|---|---|

- Remove old blocker essays, superseded arguments, and completed task-by-task narration after preserving evidence pointers.

#### falsifiers.md

- Extract the RF allocation register from advisory review `002`.
- Store:

  | RF ID | Requirement | ADR/SPEC owner | Test function | Milestone | Status |
  |---|---|---|---|---|---|

- Keep detailed test behavior in the executable test, not duplicated prose.
- Make this the canonical RF registry.
- Archive the remaining advisory portions of `002`.

#### done/

- Store compact completed sprint evidence.
- Include outcome, relevant commits, commands/results and unresolved carry-outs.
- Do not retain conversational review transcripts in the active board.

### PHASE 7 — Consolidate engineering standards

Organize development guidance around:

- dependency boundaries;
- coding style;
- TCB budget;
- capability/security review;
- schema and code generation;
- testing pyramid;
- hermetic provider testing;
- PR requirements;
- documentation rules;
- release evidence.

Avoid copying normative rules. Engineering documents link to their governing SPEC/annex clause and explain how to comply operationally.

### PHASE 8 — Archive without losing provenance

Archive:

- retained research;
- proposals 001–008;
- forensic and staff reviews;
- completed sprint narratives;
- superseded non-normative plans.

Every archive subtree receives this warning:

```text
NON-NORMATIVE / FROZEN PROVENANCE

This material preserves research and decision history. It cannot authorize implementation.
Implementation work must cite current SPEC/annex law, an accepted ADR, the active execution
board, and a named executable falsifier.
```

Requirements:

- Preserve original contents and filenames where practical.
- Maintain an archive index with topic tags and current canonical destinations.
- Record the recovery commit.
- Repair incoming links.
- Never use the archive as a second backlog.

### PHASE 9 — Add automated governance

Implement or extend CI checks for:

1. all living docs have valid metadata;
2. every `canonical_for` topic has exactly one living owner;
3. archives claim no canonical topics;
4. RFC-2119 normative terms do not appear outside law, except quotations or clearly descriptive text;
5. every active sprint task cites:
   - an accepted ADR or SPEC clause;
   - one allocated RF;
   - one owner;
   - one exit condition;
6. every cited RF is uniquely allocated;
7. every active ADR is indexed;
8. Markdown links resolve;
9. no stale paths remain;
10. schema examples validate;
11. generated types match schemas;
12. architecture diagrams link to governing contracts;
13. no second active board, backlog, specification, or agent instruction file exists;
14. archived files remain unchanged after their archive digest is recorded.

Keep these checks narrow and falsifiable. Do not build a large documentation framework or introduce unnecessary dependencies.

### PHASE 10 — Verification and handoff

Run before and after comparisons:

- Markdown link checker;
- stale-path checker;
- RF-ID checker;
- schema validation and generated-type check;
- boundary checker;
- TCB-budget checker;
- domain-blindness checker;
- relevant documentation-linter unit tests;
- `git diff --check`.

Produce a final migration report in an existing canonical execution/evidence document, not a new scratch Markdown file, containing:

- old path → new path mapping;
- deleted files and their recovery source;
- clause and RF preservation evidence;
- linter/test results;
- intentionally deferred improvements;
- exact developer reading path;
- confirmation that no production code or runtime semantics changed.

## Required developer reading paths after completion

### Simple task

```text
README → AGENTS → sprint task → named test
```

### Subsystem feature

```text
README → architecture overview → relevant SPEC clause/ADR → sprint task → named test
```

### Security-sensitive change

```text
README → KERNEL/MEASUREMENT → relevant ADR → architecture sequence → security falsifier
```

### Architectural review

```text
docs/README → overview/C4 views → SPEC → ADR index → milestones → evidence archive
```

### Historical investigation

```text
docs/README → archive index → frozen proposal/review → current superseding ADR
```

## Completion conditions

- One canonical owner exists for every active concept.
- No living document competes with SPEC, ADRs, milestones, or the active board.
- SPEC clauses and RF bindings are preserved.
- ADR and archive history remains immutable.
- Current developers can identify their task, owner boundary, files, test, and exit gate without reading historical narratives.
- M-0 through M-10 remain fully discoverable without placing future implementation details in the current sprint context.
- Documentation linters pass.
- No production code changed.
- The operator receives the exact move/delete list and explicitly approves destructive actions before they occur.

## Start condition

Begin with Phase 0 only. Present the inventory, conflicts, proposed mapping, recovery commit, and exact requested move/delete scope for approval before changing the repository.
