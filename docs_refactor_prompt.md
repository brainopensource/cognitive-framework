# AETHER Tier S+ Documentation Product Refactor — Executor Prompt

## Role

Act as AETHER's Principal Systems Architect, Documentation Platform Lead, Developer Experience
Lead, and Documentation Assurance Auditor. Treat documentation as a governed product interface for
humans and machines—not as a collection of Markdown files.

## Mission

Evolve the already-cleaned documentation into a modular, progressively disclosed, traceable, and
machine-verifiable knowledge system. A new contributor or coding agent must be able to discover the
correct concept, governing law, decision rationale, implementation boundary, test obligation, and
current milestone without leadership interpretation or loading unrelated history.

This is an information-architecture refactor only. Preserve AETHER's ratified concepts, theory,
goals, milestone ordering, requirements, security posture, and implementation semantics.

## Success thesis

> One concept has one canonical owner; every other view is a small, typed, traceable projection.

The outcome must optimize four properties together:

1. **Authority clarity:** readers always know whether text is law, a decision, current execution,
   verified description, planned design, research, or frozen history.
2. **Progressive disclosure:** readers can stop after orientation or descend by subsystem, contract,
   protocol, theory, implementation, evidence, and provenance.
3. **Autonomous execution:** an assigned developer can find boundaries, source symbols, schemas,
   failure modes, and red-to-green proof without restated oral decisions.
4. **Machine fitness:** stable IDs, metadata, traceability, bounded topic pages, and validated links
   permit targeted retrieval without treating search results as authority.

## Inputs and precedence

Read current files from disk; never assume the repository still matches an earlier proposal.

Authority remains:

1. `docs/SPEC.md` and `docs/04_annex/` — normative law.
2. Accepted ADRs and `docs/05_adr/INDEX.md` — binding decisions and RF allocation.
3. `docs/03_sprints/sprint_active.md` and `docs/02_roadmap/milestones.md` — current and macro execution.
4. `docs/00_overview/`, diagrams, and engineering guidance — descriptive views.
5. `docs/06_references/` and `docs/07_reviews/` — advisory or frozen provenance.

The following proposals explain the accepted synthesis but cannot authorize implementation:

- `docs/07_reviews/archive/proposals/001_alfa_review_full_decision.md`
- `docs/07_reviews/archive/proposals/006_fi_review_full_gptsol_proposal.md`

Executable schemas, linters, and tests prove contracts but do not silently amend normative law.
When sources conflict, stop, identify the exact conflict, and escalate it rather than reconciling it
through editorial wording.

## Non-negotiable constraints

1. Do not modify `vanguard/packages/**`, runtime behavior, schemas, generated types, or test
   semantics in this refactor.
2. Do not change AETHER concepts, equations, invariants, milestone gates, TCB limits, authority
   boundaries, or security decisions.
3. Do not rewrite accepted ADR bodies. Supersession requires a new, separately approved ADR.
4. Do not rewrite frozen research, proposals, reviews, or historical evidence. Index and link them
   externally.
5. Do not split normative law merely to meet a line-count target. Cohesion, stable identity, and
   auditability outrank cosmetic size.
6. Never duplicate normative requirements in reference or tutorial pages. Quote minimally and link
   to the stable clause owner.
7. Do not describe a ratified future interface as implemented. Every view uses one maturity label:
   `AS_BUILT`, `RATIFIED_NOT_IMPLEMENTED`, `EXPERIMENTAL`, or `RESEARCH`.
8. Do not invent ports, events, schemas, file paths, test names, algorithms, performance numbers,
   or code symbols. Verify them on disk.
9. Do not mix this work with RF-23/RF-25 production implementation. Preserve its tests and file
   ownership lanes.
10. Before any move, split, deletion, or bulk rewrite, provide the operator an exact impact ledger
    and request approval.
11. Preserve unrelated working-tree changes and record a recovery commit or immutable recovery
    reference before restructuring.
12. New pages are allowed only when their unique purpose, canonical owner, audience, inputs, and
    lifecycle are stated and machine-validatable.

## Design model: authority × information type × maturity

Do not encode every dimension into directory depth. Use a shallow stable tree plus metadata and
indexes.

### Authority classes

| Class | Meaning | May authorize implementation? | Lifecycle |
|---|---|---:|---|
| Normative law | Behavior and invariant that must hold | Yes | Surgically versioned |
| Binding decision | Accepted choice and trade-off | Yes | Append-only |
| Execution | Authorized current or future gate | Yes, within scope | Living |
| Descriptive architecture | Verified explanation of the system | No | Rebuilt when sources change |
| Reference/how-to | Verified interface or task procedure | No | Maintained with implementation |
| Research/provenance | Hypothesis, evidence, or history | No | Frozen/advisory |

### Information types

Use Diátaxis deliberately, not dogmatically:

- **Explanation:** concepts, theory, trade-offs, and architecture.
- **Reference:** exact schemas, protocols, state machines, symbols, and commands.
- **How-to:** goal-directed procedures using existing supported extension points.
- **Tutorial:** a bounded end-to-end learning path with hermetic fixtures.

A page should have one primary type. If a page repeatedly switches type, split it or replace the
secondary material with a link.

### Maturity labels

- `AS_BUILT`: verified against current source/schema/test.
- `RATIFIED_NOT_IMPLEMENTED`: accepted in ADR/law but scheduled for a future milestone.
- `EXPERIMENTAL`: implemented outside the stable contract and explicitly non-authoritative.
- `RESEARCH`: hypothesis or retained literature with no implementation authority.

## Recommended target architecture

Keep the current numbered directories unless the Phase 0 evidence shows that a move materially
improves retrieval. The target is conceptual ownership, not renaming for appearance.

```text
README.md                         # Short repository orientation and quick start
AGENTS.md                         # Sole contributor/AI operating contract
docs/
├── README.md                     # Precedence, topic catalog, maturity map, reading paths
├── SPEC.md                       # Normative entry; stable clause IDs
├── 00_overview/
│   ├── SYSTEM_OVERVIEW.md        # Concise system mental model and verified status
│   └── topics/                   # Descriptive architecture modules, if justified
│       ├── planes_and_abcd.md
│       ├── boundary_lattice.md
│       ├── identity_and_provenance.md
│       └── capability_maturity.md
├── 02_roadmap/
│   └── milestones.md             # M-0–M-10 outcome and gate ladder only
├── 03_sprints/
│   ├── sprint_active.md          # Sole active board
│   └── done/                     # Compact immutable execution evidence
├── 04_annex/                     # Normative annexes; split only with clause mapping
│   ├── KERNEL.md
│   └── MEASUREMENT.md
├── 05_adr/                       # Append-only accepted decisions and canonical RF registry
├── 06_references/                # Research corpus; indexed, non-authoritative
├── 07_reviews/                   # Reviews/proposals/forensics; indexed and frozen
├── 08_diagrams/                  # Source-controlled descriptive diagrams
├── architecture/                 # OPTIONAL: create only if it replaces justified topic owners
│   ├── README.md
│   ├── c4/
│   ├── sequences/
│   └── state_machines/
├── contracts/                    # OPTIONAL verified reference projections
│   ├── README.md
│   ├── events.md
│   ├── trajectories.md
│   ├── manifests.md
│   ├── verdicts.md
│   └── selectors_and_budgets.md
├── protocols/                    # OPTIONAL verified port/SPI reference projections
│   ├── README.md
│   ├── kernel.md
│   ├── model.md
│   ├── sandbox.md
│   ├── evaluator.md
│   ├── stores.md
│   └── spi.md
├── theory/                       # Curated synthesis; frozen sources remain in references
│   ├── README.md
│   ├── active_inference.md
│   ├── economic_resources.md
│   ├── trajectory_credit.md
│   ├── retrieval_and_skills.md
│   └── preference_and_promotion.md
└── engineering/                  # Operational guidance, never a second specification
    ├── README.md
    ├── development.md
    ├── testing_and_falsifiers.md
    ├── security_and_tcb.md
    ├── adding_an_adapter.md
    ├── adding_a_pack.md
    └── documentation.md
```

The optional directories are not pre-authorized. First demonstrate that each proposed page removes
material from a monolith or provides a verified developer interface. Prefer five strong modules to
twenty skeletal pages.

## Document contract

Every living page must expose validated metadata appropriate to its class. Extend the current schema
only when the linter will enforce the field:

```yaml
---
id: stable-id
class: architecture | contract-reference | protocol-reference | theory | how-to
authority: descriptive
canonical_for: []
source_of_truth:
  - docs/SPEC.md#stable-clause
derived_from:
  - schemas/mhf/example.schema.json
  - vanguard/packages/ports/example.py#ExamplePort
applies_to: [v0.6.1]
implementation_status: AS_BUILT
owner: role-or-subsystem
review_cycle: dependency-change
last_verified: YYYY-MM-DD
---
```

Rules:

- `id` is stable across path moves.
- `canonical_for` is unique and reserved for true owners; derived pages normally use
  `source_of_truth` instead.
- A descriptive page cannot claim normative ownership.
- `last_verified` is evidence, not decoration: record the command, commit, schema, or symbol used.
- Archived pages use archive metadata only in an external index when bodies are immutable.

## Required execution plan

### Phase 0 — Forensic baseline and content ledger

Do not edit files.

1. Record HEAD, branch, dirty files, staged files, and recovery reference.
2. Run current documentation linters and record RF-23/RF-25 state without changing them.
3. Inventory every living and archived document.
4. Inventory each major section of the monoliths, especially `SYSTEM_OVERVIEW.md`, `SPEC.md`, and
   `KERNEL.md`.
5. For every section record:

   | Section ID | Current path/heading | Authority | Information type | Maturity | Unique content | Canonical owner | Derived views | Proposed action |
   |---|---|---|---|---|---|---|---|---|

6. Generate an incoming-link map and identify source-code/schema/test anchors.
7. Report contradictions, duplicate claims, unverified future statements, and orphaned content.
8. Propose the smallest move/split/delete set and stop for operator approval.

### Phase 1 — Taxonomy, vocabulary, and navigation contract

1. Ratify page classes, maturity labels, metadata fields, and stable ID format.
2. Establish one glossary owner and map aliases without rewriting law.
3. Define subsystem tags and role-based reading paths.
4. Define documentation budgets as review triggers, not absolute truth:
   - navigation pages should normally stay below 150–250 lines;
   - topic/reference/how-to pages should normally contain one cohesive subject;
   - a common developer packet should target a small, measured context slice;
   - exceptions require a stated cohesion reason.
5. Update the metadata linter and its tests before relying on new fields.
6. Make `docs/README.md` enumerate all living owners and maturity states, preferably from validated
   metadata rather than hand-maintained parallel tables.

### Phase 2 — Overview and architecture projections

1. Reduce `SYSTEM_OVERVIEW.md` to mission, A-B-C-D, Three Planes, lattice, trust boundaries,
   universal mechanism, current maturity, and links to deeper modules.
2. Move—not copy—cohesive descriptive sections into topic owners.
3. Produce C4 context, container, and component views using verified paths and processes.
4. Produce sequences for:
   - compose and `D_H` freeze;
   - S0–S12 authorized effect dispatch;
   - exterior signed verdict recording;
   - trajectory construction and `D_R/D_X` binding;
   - cold death/reconciliation/resume;
   - plugin lifecycle.
5. Depict future spawn, concurrency, retrieval, macro compilation, and DPO only as
   `RATIFIED_NOT_IMPLEMENTED`, linked to the governing ADR and milestone.
6. Every diagram links to law, decisions, symbols, and tests; it creates no requirement.

### Phase 3 — Contract and protocol reference

1. Generate or hand-curate bounded reference projections for existing schemas and ports.
2. Each contract page includes:
   - purpose and authority pointer;
   - schema `$id` and version;
   - producer, consumer, and writer authority;
   - required fields and invariants;
   - compatibility behavior;
   - valid minimal example and negative example;
   - code symbols and bound tests.
3. Each protocol page includes:
   - port location and signature;
   - caller/implementer boundary;
   - capability and failure semantics;
   - implementations and test doubles;
   - concurrency/idempotency expectations when specified;
   - bound contract/security tests.
4. Validate examples automatically. Do not manually duplicate full JSON Schemas or Python APIs.
5. Planned `mhf.manifest/2`, spawn, index, and macro interfaces stay design references until their
   milestone implementation exists.

### Phase 4 — Theory and research learning path

1. Preserve research sources unchanged.
2. Build a curated map that separates:
   - adopted mechanism;
   - ratified future mechanism;
   - open hypothesis;
   - rejected/deferred idea;
   - empirical evidence and falsifier.
3. Curate modules for Active Inference (VFE versus EFE), the 6D resource algebra, trajectory credit,
   retrieval/skill dynamics, and verifiable preference promotion.
4. Preserve equations exactly or prove equivalence; include symbols, assumptions, applicability,
   limitations, and links to current law/ADR status.
5. Never promote a research claim such as token reduction or coordination complexity without a
   measurement method and recorded result.

### Phase 5 — Autonomous engineering guides

Create a guide only for a supported workflow. Each guide must state prerequisites, files allowed to
change, forbidden boundaries, governing law/ADR, red test, implementation steps, verification
commands, failure recovery, and escalation conditions.

Prioritize:

1. run and diagnose the test pyramid;
2. add or change a falsifier;
3. add an adapter behind an existing port;
4. add a domain pack without domain/kernel changes;
5. add schema/event compatibility safely;
6. audit a security/TCB-sensitive change;
7. add a plugin only after M-3 lands.

Do not turn current sprint assignments into permanent how-to pages.

### Phase 6 — Traceability and developer context bundles

Define one machine-readable traceability source linking:

```text
concept → law clause → ADR → schema/port → code symbol → RF/test → milestone
```

Generate navigation views from it where practical. Do not hand-maintain multiple matrices.

For each subsystem, provide a context bundle index with:

- purpose and trust boundary;
- current maturity;
- allowed dependencies;
- normative clauses and ADRs;
- schemas/ports and concrete symbols;
- common extension points and forbidden shortcuts;
- tests, linters, and known active gaps.

Measure approximate tokens for representative bundles. Claims of improved context efficiency require
before/after measurements over real tasks.

### Phase 7 — CI documentation assurance

Implement narrow tests, each with fixtures and clear failure messages:

1. metadata schema and stable ID uniqueness;
2. unique canonical ownership;
3. authority/maturity compatibility;
4. source-of-truth and derived-from resolution;
5. RFC-2119 placement with quotation/archive exclusions;
6. Markdown links and stable anchors;
7. Python symbol and schema anchor existence;
8. schema example validation;
9. active ADR and RF allocation coverage;
10. sprint-task traceability;
11. architecture diagram source links;
12. archive immutability;
13. no competing active board/spec/agent contract;
14. dependency-triggered freshness.

Roll out new checks as non-blocking diagnostics, repair the baseline, then promote one rule at a
time. Avoid a documentation framework whose maintenance cost exceeds the defects it prevents.

### Phase 8 — Atomic migration and proof of no loss

After explicit approval:

1. Use `git mv` for moves.
2. Move sections through small, reviewable patches using the content ledger.
3. Repair all references in the same change that moves a path or heading.
4. Preserve stable aliases for normative clause/heading changes.
5. Do not edit immutable bodies to repair incoming links; update external indexes.
6. Run checks after every slice, not only at the end.
7. Maintain a migration matrix with old path, new owner, action, unique-content proof, and recovery
   reference.

### Phase 9 — Retrieval drills and acceptance

Demonstrate these tasks using documentation alone:

| Drill | Reader starts at | Required destination |
|---|---|---|
| Newcomer | Root README | mental model + safe quick start |
| RF implementer | active board | law + ADR + files + failing test + DoD |
| Adapter author | subsystem bundle | port + boundary + examples + tests |
| Security reviewer | docs index | TCB law + flow + threat evidence |
| Architect | overview | current/future topology + decisions + gates |
| Researcher | theory index | equations + assumptions + adoption status + sources |
| Forensic auditor | archive index | frozen evidence + recovery + current disposition |

Acceptance requires:

- no loss in the section ledger;
- no duplicated canonical owner;
- all new reference claims verified on disk;
- no future feature presented as built;
- all documentation and architecture linters green;
- production and test semantics unchanged;
- representative context bundles are materially smaller or easier to retrieve by measured evidence;
- operator approval of the final move/delete report.

### Phase 10 — Handoff and steady-state protocol

1. Record final paths, recovery anchors, test evidence, deferrals, and ownership in an existing
   canonical execution/evidence location.
2. Update contributor instructions only after the migration is green.
3. Define change-impact rules:
   - law change reviews derived architecture/reference/how-to pages;
   - schema/port change reviews reference pages and examples;
   - code-symbol change reviews symbol anchors;
   - ADR acceptance reviews maturity maps and roadmap links;
   - milestone transition reviews active board and capability matrix.
4. Delete temporary root prompts/checklists only after their durable obligations are migrated and
   the operator explicitly approves deletion.

## Required executor reports

Before editing, return:

1. verified repository state;
2. section-level content ledger summary;
3. contradictions and duplicate-owner findings;
4. proposed target pages with justification;
5. exact moves, splits, deletions, and immutable files;
6. CI changes and rollout order;
7. estimated migration slices and collision risks with active development;
8. explicit approval request.

After each approved slice, return:

- changed paths and canonical ownership changes;
- content-ledger rows discharged;
- link/symbol/schema validation results;
- deferred conflicts;
- rollback/recovery reference;
- next smallest safe slice.

## Start instruction

Begin with Phase 0 only. Inspect the current tree and report evidence. Do not edit, move, split,
delete, or create documentation modules until the operator approves the exact Phase 1 migration
slice.
