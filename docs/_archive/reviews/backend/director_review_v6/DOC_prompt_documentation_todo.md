# AETHER Documentation Reconstruction — Primary Execution Mandate

## Mandate

Reconstruct coherent candidate documentation for
`brainopensource/cognitive-framework` from verified repository evidence while preserving the
distinction between what the product intentionally requires (**TARGET**) and what the exact reviewed
revision implements (**AS_BUILT**).

Repository: `https://github.com/brainopensource/cognitive-framework`
Authoritative branch: `main`

This is a documentation-governance and planning mandate. It does not authorize production-code
changes, canonical documentation reconstruction during bootstrap convergence, or replacement of the
active `docs/` tree.

## Governing bootstrap package

These documents govern documentation reconstruction in this order:

1. `docs/_archive/reviews/backend/director_review_v6/DOC_prompt_documentation_todo.md` — primary
   execution method and phase order.
2. `docs/_archive/reviews/backend/director_review_v6/DOC_ARCHITECTURE_SPEC.md` — target information
   architecture and ownership rules.
3. `docs/_archive/reviews/backend/director_review_v6/DOC_process_management_todo.md` — delegation,
   sequencing, actors, outputs, and management gates.
4. `docs/_archive/reviews/backend/director_review_v6/DOC_migration_process.md` — supporting migration
   engineering, metadata, indexes, reconciliation, loss audit, validation, and cutover controls.
5. `docs/_archive/reviews/backend/director_review_v6/DOC_oss_tools.md` — optional, evidence-driven
   tooling catalog.

If an older migration-oriented instruction conflicts with the greenfield/code-first phase order,
`DOC_prompt_documentation_todo.md` wins.

None of these bootstrap documents overrides AETHER product truth; they govern how that truth is
reconstructed and represented.

Canonical terms throughout this package are: documentation reconstruction, AS_BUILT, TARGET,
candidate-docs/, legacy loss audit, canonical owner, canonical ID, implementation evidence,
normative authority, generated machine layer, independent audit, governance ratification, cutover,
and rollback.

## Authority model

### Product TARGET authority

Use the following precedence for intentional architecture, identity, and normative requirements:

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

The reconstruction must not silently discard, override, weaken, or reinterpret binding product
requirements. Historical ADR provenance remains immutable. A decision changes only through the
repository's authorized successor process.

### AS_BUILT evidence

Claims about current implementation must be derived from the exact recorded revision using:

```text
production code
executable tests
schemas
configuration
CLI/API behavior
runtime composition
public interfaces
benchmarks where relevant
```

Use tests as evidence of exercised behavior, not as a substitute for inspecting implementation and
contracts. Use benchmarks only for the measured subject and conditions they actually cover.

### Status vocabulary

Every material capability or claim must use one of these values:

- `IMPLEMENTED` — implementation evidence supports the claim at the recorded SHA.
- `PARTIAL` — some required behavior exists, but the complete claim is not supported.
- `PLANNED` — TARGET authority requires or schedules it, without sufficient implementation evidence.
- `EXPERIMENTAL` — implemented or described as a bounded experiment, not accepted product behavior.
- `UNRESOLVED` — available evidence or authority does not permit a defensible conclusion.
- `OBSOLETE` — no longer current under product authority or implementation evidence.
- `CONTRADICTED` — an explicit source conflicts with stronger authority or verified implementation.

TARGET and AS_BUILT may differ. Record the difference; never make either impersonate the other.

## Mandatory governance precondition

The current `AGENTS.md` prohibits documentation sprawl and defines the current Clean Triad.
Candidate reconstruction is allowed only in the isolated `candidate-docs/` staging surface.
Promotion into `docs/` requires explicit ratification of the new documentation governance and
corresponding updates to `AGENTS.md`, `docs/README.md`, repository navigation and validation rules.

During reconstruction:

- `candidate-docs/` is the mandatory staging surface.
- No reconstruction output may directly change active `docs/`.
- Existing active documents and ADRs must not be deleted, rewritten, moved, archived, or consolidated.
- Append-only ADR history must not be rewritten. If a compact active decisions surface is proposed,
  it must be an active index or current-decision view while historical provenance remains available
  through Git and any governance-required retained records.
- Cutover is a separate, explicitly authorized, reviewable, and reversible operation.
- Reconstruction findings must not trigger production-behavior changes. Implementation gaps are
  reported for a separately authorized engineering process.

The reconstruction agent may create helper tools only under `tools/docs_alpha/` and generated
artifacts only under `.generated/knowledge/`. Canonical candidate Markdown belongs only under
`candidate-docs/`. Scratch notes remain ephemeral and are not committed.

## Required baseline

At the beginning of every reconstruction branch, the executor must independently resolve and record
the exact `main` HEAD. No SHA written in this bootstrap package is a permanent project baseline.

Minimum baseline procedure:

```bash
git fetch origin main
git switch --create docs/reconstruction-<date> origin/main
git rev-parse HEAD
git status --short --branch
```

If branch creation or network access is controlled by a human, the executor records the equivalent
commands and evidence supplied by that operator. The baseline record must include repository URL,
branch, full SHA, timestamp, dirty/clean status, runtime versions, and inventory command versions.

Before discovery, read the following bounded TARGET/governance bundle:

- `AGENTS.md`
- `README.md`
- `VISION.md`
- `docs/README.md`
- `docs/SPEC.md`
- `docs/02_decisions/INDEX.md`
- `docs/03_execution/milestones.md`
- `docs/03_execution/sprint_active.md`
- `docs/07_engineering/documentation.md`

This early reading protects TARGET and repository governance. It must not anchor, preselect, or
distort the AS_BUILT subsystem model. Do not recursively load the legacy documentation corpus before
the first AS_BUILT model exists.

## Canonical execution flow

Every governing document and work packet must preserve this order:

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

Steps 0–14 prepare and review a candidate. Step 15 is not implied by completion of any earlier step.

## Execution phases

### Phase 0 — Bootstrap convergence

Correct and commit only this five-document bootstrap package. Confirm that all five documents share
the same authority model, terminology, phase order, staging boundary, and cutover controls. Do not
start reconstruction in this phase.

### Phase 1 — Reconstruction branch and exact baseline

Create a branch from current `origin/main`, record its full SHA and environment, and confirm a clean
or fully explained working tree. Preserve the baseline record in the reconstruction evidence, not as
a permanent baseline embedded in these instructions.

### Phase 2 — Deterministic repository inventory

Generate a reproducible inventory before semantic synthesis. At minimum cover:

- production roots, package boundaries, imports, and public entry points;
- Python and TypeScript clients, CLI commands, API/service surfaces, and runtime composition;
- tests grouped by subsystem and evidence claim;
- schemas, vectors, manifests, protocols, configuration, and generated-code relationships;
- tools, linters, runners, CI workflows, release scripts, and benchmark surfaces;
- documentation paths and metadata without recursively interpreting legacy prose.

Prefer checked-in tools and deterministic standard utilities. Record command, version, inputs,
outputs, duration, and errors. Write helper code only under `tools/docs_alpha/` and generated output
only under `.generated/knowledge/`.

Exit only when another executor can reproduce the inventory from the recorded SHA.

### Phase 3 — AS_BUILT architecture discovery

Reconstruct the implementation bottom-up from production code, executable tests, schemas,
configuration, runtime wiring, and public behavior. For each discovered subsystem identify:

- purpose and responsibilities;
- owned code and public interfaces;
- inbound and outbound dependencies;
- data, event, and control flows;
- lifecycle and failure semantics;
- trust and authority boundaries;
- configuration and extension points;
- tests, schemas, and evidence;
- status and confidence;
- unresolved questions.

Produce an AS_BUILT architecture model and evidence map before interpreting the legacy corpus. Keep
TARGET observations in a separate register during this phase.

### Phase 4 — Canonical documentation blueprint

Apply `DOC_ARCHITECTURE_SPEC.md` to the discovered architecture. Propose only pages justified by
repository evidence and user tasks. Assign each durable fact one canonical owner and canonical ID.
For each candidate page record purpose, audience, status plane, evidence bundle, expected sections,
links, and non-responsibilities.

The Tech Lead or designated architecture owner must approve the blueprint before bounded writing
begins. Empty placeholders and speculative leaf pages are prohibited.

### Phase 5 — Candidate AS_BUILT documentation

Write implementation-facing pages under `candidate-docs/` from approved work packets. Cite exact
implementation evidence and use status values consistently. Do not alter production behavior to make
it agree with documentation. Report inconsistencies and gaps instead.

### Phase 6 — Separate TARGET reconciliation

Revisit `VISION.md`, normative law, accepted/current ADRs, schemas/contracts/protocols, and active
execution documents. Produce TARGET pages or clearly separated TARGET sections without modifying the
AS_BUILT findings. For every difference, record required behavior, observed behavior, authority,
implementation evidence, status, and unresolved ownership.

### Phase 7 — Legacy loss audit

Only after the AS_BUILT model, approved blueprint, initial candidate documentation, and TARGET
reconciliation exist may the executor comprehensively inspect legacy documentation.

Ask:

> Does this legacy source contain unique, still-valid knowledge absent from AS_BUILT evidence and
> current TARGET authority?

Do not ask where every old file should move. Classify findings using the ledger and classifications
defined in `DOC_migration_process.md`. A legacy file need not receive a new destination, and prose is
not retained merely because it exists. Preserve unresolved conflicts without guessing.

### Phase 8 — Unique-knowledge absorption

Absorb only reviewed, unique, valid claims into their approved canonical owners. Each retained claim
must carry its legacy source, current evidence, authority class, destination, decision, reviewer,
confidence, and unresolved risk. Record obsolete and contradicted material in the derived audit
ledger; do not copy it into active candidate pages as current truth.

### Phase 9 — Generated machine layer

Add validated frontmatter and reproducibly generate catalogs, heading indexes, relations, code maps,
and reconciliation views under `.generated/knowledge/`. Markdown remains the canonical human-authored
representation. Generated indexes and diagrams are derived views, never independent sources of truth
and never manually maintained.

### Phase 10 — Mechanical validation

Run the existing repository documentation checks first, plus candidate-scoped validation created
under `tools/docs_alpha/` when needed. Validate at least:

- metadata schema and canonical-ID uniqueness;
- local links and controlled external-link policy;
- canonical-owner uniqueness and duplicate durable facts;
- TARGET/AS_BUILT status clarity;
- code, schema, test, and authority references;
- terminology and prohibited path names;
- generated-artifact reproducibility;
- human navigation and representative AI retrieval tasks;
- absence of changes outside authorized reconstruction surfaces.

Optional tools from `DOC_oss_tools.md` are adopted only after measured need and overlap review.

### Phase 11 — Independent audit and correction

An independent frontier reviewer who did not author the principal architecture model evaluates
implementation fidelity, TARGET protection, ownership, retrieval, knowledge loss, governance
compliance, and cutover readiness. Critical findings must be corrected and revalidated. Independence
must be recorded, not merely asserted.

### Phase 12 — Governance review and cutover

Prepare a proposed cutover diff as a distinct output. Before any active-tree change, obtain explicit
human/Tech Lead ratification for the new taxonomy, documentation authority, `AGENTS.md` changes,
`docs/README.md` and root navigation changes, ADR governance treatment, validation rules, deletion or
movement of active files, and any blocking CI checks.

Only a separately authorized developer operation may perform cutover. It must use a clean reviewed
diff, preserve append-only decision provenance, create a recoverable backup/reference, define rollback
criteria and commands, and run post-cutover validation. Failure triggers rollback or a forward fix
under the ratified plan; it never grants permission for improvised cleanup.

## Required reconstruction outputs

Keep these outputs separate and reviewable:

1. discovered AS_BUILT architecture;
2. TARGET architecture;
3. implementation gaps;
4. unresolved conflicts;
5. legacy unique knowledge;
6. obsolete legacy material;
7. proposed cutover changes;
8. generated machine layer and validation evidence;
9. independent audit findings and dispositions;
10. rollback plan.

The first seven must never be collapsed into one ambiguous narrative.

## Completion criteria

The candidate is ready for governance review only when:

- repository identity, branch, and exact execution SHA are recorded;
- deterministic inventory is reproducible;
- AS_BUILT and TARGET are independently traceable;
- every durable fact has one canonical owner and canonical ID;
- all material claims have evidence, authority, status, and confidence;
- the legacy loss audit has no unresolved critical omission;
- generated artifacts reproduce from canonical Markdown and repository evidence;
- mechanical validation passes or explicitly records approved non-critical exceptions;
- an independent audit is complete and critical findings are closed;
- active `docs/`, active ADRs, `AGENTS.md`, and production code remain unchanged during reconstruction;
- the proposed cutover is isolated, reviewable, reversible, and awaiting explicit ratification.

## Core invariant

> Reconstruct current documentation from current implementation; reconstruct future documentation
> from current intentional design; use legacy documentation only to recover unique knowledge that
> neither source contains.
