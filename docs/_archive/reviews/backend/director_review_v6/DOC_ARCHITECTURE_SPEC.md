# AETHER Canonical Documentation Architecture Specification

## Purpose

Define the proposed information architecture, canonical ownership rules, and measurable quality
requirements for candidate documentation reconstructed from
`brainopensource/cognitive-framework` on `main`.

This specification governs the shape of `candidate-docs/`. It does not authorize creating the
candidate during bootstrap convergence, changing the active `docs/` tree, or promoting this proposed
taxonomy into product authority.

## Scope

This specification defines:

- target top-level documentation categories;
- boundaries between normative, architectural, reference, procedural, decision, execution, and
  conceptual knowledge;
- canonical ownership and canonical-ID rules;
- separation of AS_BUILT and TARGET claims;
- relationships among authored Markdown, generated machine views, diagrams, and publishing layers;
- evidence requirements for selecting leaf pages;
- human, AI, traceability, status, link, and metadata acceptance criteria.

## Non-goals

This document does not:

- define AETHER product architecture or amend product requirements;
- describe the current implementation;
- authorize production-code changes;
- require every blueprint leaf to exist;
- classify every legacy document or prescribe a destination for it;
- authorize deletion, rewriting, movement, archiving, or consolidation of active documentation;
- authorize rewriting or removing append-only ADR history;
- perform cutover or change `AGENTS.md`, documentation authority, navigation, or CI.

## Authority and relationship to the bootstrap package

Bootstrap-process precedence is:

1. `docs/_archive/reviews/backend/director_review_v6/DOC_prompt_documentation_todo.md`
2. `docs/_archive/reviews/backend/director_review_v6/DOC_ARCHITECTURE_SPEC.md`
3. `docs/_archive/reviews/backend/director_review_v6/DOC_process_management_todo.md`
4. `docs/_archive/reviews/backend/director_review_v6/DOC_migration_process.md`
5. `docs/_archive/reviews/backend/director_review_v6/DOC_oss_tools.md`

This document owns information architecture and canonical ownership. The primary prompt owns method
and phase order; the management document owns delegation and gates; the supporting migration document
owns reconciliation, generated indexes, validation, and cutover controls; the tools catalog provides
optional implementation choices.

If an older migration-oriented instruction conflicts with the greenfield/code-first phase order,
`DOC_prompt_documentation_todo.md` wins.

None of these bootstrap documents overrides AETHER product truth; they govern how that truth is
reconstructed and represented.

Canonical terms throughout this package are: documentation reconstruction, AS_BUILT, TARGET,
candidate-docs/, legacy loss audit, canonical owner, canonical ID, implementation evidence,
normative authority, generated machine layer, independent audit, governance ratification, cutover,
and rollback.

Product TARGET authority remains:

```text
VISION.md
↓
docs/SPEC.md + docs/01_law/
↓
accepted/current ADRs
↓
schemas, contracts and protocols
↓
active execution documents
```

AS_BUILT claims remain subordinate to implementation evidence from production code, executable
tests, schemas, configuration, CLI/API behavior, runtime composition, public interfaces, and relevant
benchmarks at the exact recorded SHA.

## Definitions

- **documentation reconstruction** — the entire code-first program that creates, validates, audits,
  and potentially promotes a new documentation surface.
- **AS_BUILT** — a claim about behavior or structure supported by implementation evidence at the
  exact recorded repository SHA.
- **TARGET** — intentional identity, architecture, or requirement derived from current product
  authority, whether or not implemented.
- **canonical owner** — the single human-authored page responsible for maintaining a durable fact.
- **canonical ID** — a stable semantic identifier for a canonical document or claim, independent of
  filenames and generated views.
- **generated view** — reproducible catalog, index, relation, code map, diagram, or portal page derived
  from canonical Markdown and repository evidence.
- **historical evidence** — legacy prose, superseded material, or decision provenance retained for
  audit and recovery but not automatically current authority.
- **implementation evidence** — code, tests, schemas, configuration, observable public behavior,
  runtime composition, and bounded benchmark results supporting an AS_BUILT claim.
- **normative authority** — the current product TARGET sources ordered above.
- **legacy loss audit** — the late review for unique, still-valid knowledge missing from current
  evidence and authority; it is not a file-movement exercise.
- **cutover** — the separately ratified operation that replaces or restructures the active
  documentation surface.

## Target top-level architecture

The starting blueprint is:

```text
docs/
├── README.md
├── SPEC.md
├── architecture/
├── reference/
├── guides/
├── decisions/
├── execution/
└── theory/
```

During reconstruction, the equivalent structure exists only beneath `candidate-docs/`. The tree is a
classification model, not permission to create empty folders or pages. Every leaf addition, removal,
or rename requires repository evidence, a user/retrieval need, a canonical owner, and blueprint
approval. The approved blueprint may omit unnecessary leaves or add evidence-backed leaves within
these ownership boundaries.

## Ownership boundaries

### `README.md` — navigation

Owns audience-oriented entry points, authority explanation, reading paths, and links to canonical
owners. It does not duplicate architecture, contracts, commands, status, or requirements.

### `SPEC.md` — normative contract

Owns the compact normative contract and navigation to task-sized normative material. It is not a
general architecture encyclopedia, implementation narrative, historical status report, or tutorial.
Any proposed change to current normative ownership requires governance ratification.

### `architecture/` — structure and behavior

Owns subsystem responsibilities, boundaries, dependency direction, lifecycle, trust boundaries,
state transitions, and end-to-end flows. It explains structure and behavior while linking exact
contracts to `reference/` and normative obligations to `SPEC.md` or their ratified owners.

Architecture pages must identify whether each material statement is AS_BUILT or TARGET. If both are
needed, use clearly separated sections and a gap table; never blend them into one tense or diagram.

### `reference/` — exact interfaces

Owns exact contracts, schemas, events, public APIs, commands, configuration keys, protocol shapes,
error codes, and compatibility behavior. Reference pages must point to source schemas/code and state
generation or validation relationships. They are lookup surfaces, not tutorials or rationale essays.

### `guides/` — task-oriented procedures

Owns repeatable procedures organized around a user goal, prerequisites, commands, expected results,
failure handling, and verification. Guides link to reference definitions and architecture context;
they do not redefine them.

### `decisions/` — current decision views and rationale

Owns current decision navigation, active rationale, supersession relationships, and links to immutable
provenance. Existing ADR identifiers and accepted history remain append-only under current governance.
A compact active-decision view may be proposed, but it must retain historical recovery through Git
and any governance-required retained records. No deletion, rewrite, or movement occurs without
explicit ratification of ADR governance.

### `execution/` — current work and gates

Owns current authorized work, stable milestone gates, dependencies, acceptance evidence, and bounded
forward sequencing. It must not contain historical status narratives, general architecture, or
normative rules. Completed execution history is referenced through approved provenance mechanisms.

### `theory/` — non-implemented concepts

Owns explicitly conceptual, research, mathematical, or exploratory material. Every page must carry
`EXPERIMENTAL`, `PLANNED`, `UNRESOLVED`, or another accurate status and must not imply implementation
or authorization. Implemented mechanisms move to an appropriate canonical owner only through review;
their research provenance may remain linked.

## Canonical ownership invariant

> One durable fact → one canonical owner → all other pages link to it.

A durable fact includes normative requirements, subsystem responsibility, interface shape,
configuration semantics, command behavior, current execution status, and decision rationale. A page
may summarize another owner's fact only when the summary is necessary for navigation and is clearly
identified as derived, linked, and non-authoritative.

The blueprint must include an ownership register with:

- canonical ID;
- canonical owner path;
- fact class;
- status plane (`AS_BUILT`, `TARGET`, or explicitly separated `BOTH`);
- implementation evidence or normative authority;
- known derived views;
- reviewer and confidence.

Duplicate ownership is a validation failure, not an invitation to synchronize copies manually.

## Page selection and size rules

Create a page only when all are true:

1. repository evidence or an approved task establishes the subject;
2. the subject has a distinct ownership boundary and retrieval intent;
3. the page has sufficient verified content at creation time;
4. no existing candidate canonical owner can absorb it coherently;
5. its canonical ID, audience, status plane, and evidence bundle are known.

Do not create empty placeholders. Do not create a folder merely because a subsystem exists in code.
Do not create huge multi-purpose Markdown documents spanning multiple ownership classes. Split a page
when independent audiences retrieve different sections, when different owners maintain them, or when
its size prevents bounded reading; do not split solely to satisfy an arbitrary file count.

## Authored, generated, diagram, and publishing layers

### Canonical human-authored Markdown

Markdown with validated frontmatter is the authored knowledge representation. It owns prose,
normative wording, reviewed explanations, decisions, procedures, and explicit evidence citations.

### Generated machine layer

Catalogs, headings indexes, relations, code maps, ownership reports, and audit ledgers are generated
under `.generated/knowledge/` from canonical Markdown and repository evidence. They must be
deterministic, reproducible, and never manually maintained as a second truth.

### Derived diagrams

Diagrams are used only when they materially improve understanding of relationships, hierarchy,
sequence, or state. Mermaid or other diagram sources are derived from or explicitly linked to their
canonical owners. A diagram cannot introduce an independent component, flow, status, or requirement.

### Portal and publishing layers

Search portals and static sites consume canonical Markdown and generated indexes. They may add
navigation and presentation, never product truth or unique authored facts. Publishing tooling is not
required for reconstruction correctness.

## AS_BUILT and TARGET representation

Use only these status values for material claims:

```text
IMPLEMENTED
PARTIAL
PLANNED
EXPERIMENTAL
UNRESOLVED
OBSOLETE
CONTRADICTED
```

An AS_BUILT section must cite implementation evidence. A TARGET section must cite normative
authority. When both address the same capability, show them separately with an implementation-gap
record. Never infer implementation from an accepted requirement, and never weaken a requirement
because current code differs.

Active architecture pages must describe the current structure and bounded target differences, not a
chronological story of past releases. Historical status narrative belongs in historical evidence or
an approved decision/execution provenance view.

## Anti-sprawl and contamination rules

The candidate must prevent:

- duplicated canonical facts or manually synchronized catalogs;
- new top-level folders for individual subsystems;
- AS_BUILT statements sourced only from legacy prose;
- TARGET statements sourced only from current code;
- diagrams or generated indexes becoming independent truth;
- history narratives in active architecture pages;
- execution status in architecture or reference pages;
- tutorials embedding full schemas or contract tables;
- empty placeholder pages;
- multi-purpose pages spanning unrelated owners;
- permanent `_legacy/` active documentation trees without a ratified recovery need.

## Metadata minimum

The exact schema is finalized during reconstruction, but every canonical candidate page must support:

- unique canonical ID;
- class and canonical owner;
- status plane and implementation status;
- audience and purpose;
- repository SHA last verified;
- normative authority and/or implementation evidence;
- supersession/relationship links where applicable;
- reviewer and confidence;
- generated-view provenance.

Metadata must be validated mechanically. Fields with no retrieval, governance, or validation use are
excluded.

## Measurable acceptance criteria

### Human navigation

- A newcomer reaches orientation, installation, first verified task, and troubleshooting in at most
  three intentional navigation choices from `README.md`.
- A contributor reaches the applicable requirement, subsystem architecture, exact interface, and
  validation command without searching historical evidence.
- Five representative user tasks are timed against the active baseline and candidate; the candidate
  must not regress median time-to-correct-source without an accepted explanation.

### AI retrieval

- A preregistered query set covers architecture, contract, procedure, status, and TARGET/AS_BUILT gap
  questions.
- Retrieval returns the canonical owner in the top three results for at least 90% of the approved
  alpha query set, with no critical answer sourced only from a derived view.
- Context bundles contain canonical pages and links, not duplicate summaries; token cost and wrong-
  owner retrieval are recorded.

### Canonical ownership

- Every registered durable fact has exactly one canonical owner.
- Canonical IDs are unique and stable across filename changes.
- Duplicate-owner and orphan-owner reports contain zero critical findings.

### Code traceability

- Every AS_BUILT subsystem page cites at least one production path and its relevant executable tests,
  schema/configuration, or public behavior.
- Sampled references resolve at the recorded SHA; volatile line numbers are not manually maintained.
- Unsupported implementation claims are zero.

### Status clarity

- Every material capability claim uses the shared status vocabulary.
- TARGET and AS_BUILT evidence are separately identifiable in all sampled pages.
- Every known divergence has an implementation-gap or unresolved-conflict record.

### Link integrity

- All internal links and fragments resolve.
- External links follow an explicit allow/ignore/network policy and do not make hermetic validation
  nondeterministic.
- Generated views contain no dangling canonical IDs.

### Metadata validity

- All canonical pages validate against the approved metadata schema.
- Canonical IDs and enumerated fields are unique/valid.
- Regeneration produces no unexplained diff from identical inputs.

## Canonical execution flow

This specification is applied only in the shared order:

0. Bootstrap documents corrected and committed.
1. Reconstruction branch created.
2. Repository and exact SHA recorded.
3. Deterministic inventory generated.
4. AS_BUILT reconstructed from code/tests/schemas/runtime.
5. Canonical documentation blueprint approved.
6. Candidate AS_BUILT documentation produced.
7. TARGET authority reconciled separately.
8. Legacy loss audit performed.
9. Unique valid knowledge absorbed.
10. Metadata and generated machine indexes produced.
11. Mechanical validation executed.
12. Independent frontier audit completed.
13. Critical findings corrected.
14. Governance change and cutover reviewed.
15. Explicitly authorized cutover performed.
16. Post-cutover validation and rollback check completed.

The architecture blueprint is approved at step 5. It must not be inferred from legacy file
classification, and it does not authorize step 15.
