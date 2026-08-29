# Supporting Migration, Reconciliation, Validation and Cutover Process

## Role and subordination

This document supplies engineering and assurance controls for the documentation reconstruction of
`brainopensource/cognitive-framework` on `main`. It is not a competing execution plan.

It is subordinate to:

1. `docs/_archive/reviews/backend/director_review_v6/DOC_prompt_documentation_todo.md` for the primary
   method and phase order;
2. `docs/_archive/reviews/backend/director_review_v6/DOC_ARCHITECTURE_SPEC.md` for final taxonomy and
   canonical ownership;
3. `docs/_archive/reviews/backend/director_review_v6/DOC_process_management_todo.md` for delegation,
   actors, and management gates.

`docs/_archive/reviews/backend/director_review_v6/DOC_oss_tools.md` supplies an optional,
evidence-driven tools catalog.

If an older migration-oriented instruction conflicts with the greenfield/code-first phase order,
`DOC_prompt_documentation_todo.md` wins.

None of these bootstrap documents overrides AETHER product truth; they govern how that truth is
reconstructed and represented.

Canonical terms throughout this package are: documentation reconstruction, AS_BUILT, TARGET,
candidate-docs/, legacy loss audit, canonical owner, canonical ID, implementation evidence,
normative authority, generated machine layer, independent audit, governance ratification, cutover,
and rollback.

## Non-authorizations

This process does not authorize:

- beginning with classification of every legacy document;
- using legacy taxonomy to define the candidate architecture;
- changing production code or behavior to match documentation;
- writing reconstruction output directly into active `docs/`;
- deleting, rewriting, moving, archiving, or consolidating active documentation;
- rewriting or deleting append-only ADR history;
- creating a permanent active `_legacy/` tree;
- enabling blocking CI or performing cutover without explicit governance ratification.

`candidate-docs/` is the only authored staging surface. Helper tools are allowed only under
`tools/docs_alpha/`; generated artifacts are allowed only under `.generated/knowledge/`.

## Truth and status model

Product TARGET authority is:

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

AS_BUILT claims use production code, executable tests, schemas, configuration, CLI/API behavior,
runtime composition, public interfaces, and relevant benchmarks at the exact recorded SHA.

Use `IMPLEMENTED`, `PARTIAL`, `PLANNED`, `EXPERIMENTAL`, `UNRESOLVED`, `OBSOLETE`, and `CONTRADICTED`
for capability status. Preserve TARGET/AS_BUILT disagreement as a gap or conflict; never guess.

## Canonical execution flow

This process may support only the following order:

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

Comprehensive legacy analysis begins only at step 8, after deterministic inventory, AS_BUILT
discovery, blueprint approval, initial candidate AS_BUILT documentation, and separate TARGET
reconciliation.

## Artifact model

### Canonical authored layer

Reviewed Markdown under `candidate-docs/` is the canonical candidate knowledge representation. A
durable fact has one canonical owner and canonical ID. Authored pages are never generated from a
legacy file merely to preserve that file's existence.

### Generated machine layer

All generated outputs live under `.generated/knowledge/` and are reproducible from canonical
Markdown, the recorded repository SHA, and command manifests. Recommended alpha artifacts are:

```text
.generated/knowledge/
├── baseline.json
├── repository-inventory.jsonl
├── catalog.jsonl
├── headings.jsonl
├── relations.jsonl
├── code-map.jsonl
├── reconciliation-ledger.jsonl
├── legacy-audit.jsonl
├── knowledge-loss-register.jsonl
├── conflicts.jsonl
├── validation-results.json
├── retrieval-results.jsonl
└── generation-manifest.json
```

Names may change only through blueprint review. There is no manually maintained `migration-matrix`.
Generated artifacts do not become second sources of truth.

## Baseline and deterministic inventory

Every reconstruction execution records its own current `main` HEAD; no prior SHA is a permanent
baseline. `baseline.json` should include:

- repository `https://github.com/brainopensource/cognitive-framework`;
- branch `main` and full SHA;
- capture timestamp and worktree status;
- platform and relevant runtime/tool versions;
- command manifest digest;
- source and output roots;
- known exclusions and failures.

`repository-inventory.jsonl` should cover production roots, languages, packages, entry points,
runtime composition, public interfaces, CLI/API surfaces, schemas, configuration, tests, tooling, CI,
benchmarks, and documentation paths. Inventory records describe files and machine-extractable
structure; they do not semantically classify the complete legacy corpus.

Each generator records command, version, inputs, input digests where practical, output, duration,
exit status, deterministic ordering, and error handling. Re-running identical inputs must produce
byte-identical output or a documented normalized equivalent.

## Metadata schema

The blueprint approves the final schema. The minimum useful authored-page fields are:

```yaml
id: arch.runtime.example
class: architecture
canonical_owner: candidate-docs/architecture/example.md
truth_plane: AS_BUILT
implementation_status: IMPLEMENTED
summary: One-sentence retrieval summary.
audience:
  - developer
source_sha: <full execution SHA>
implementation_evidence:
  - path: vanguard/packages/runtime/example.py
normative_authority: []
related_ids: []
owner: documentation-specialist
reviewer: <reviewer identity>
confidence: high
```

Rules:

- `id` is globally unique and stable across filename changes.
- `canonical_owner` must equal the page that owns the durable fact.
- `truth_plane` is `AS_BUILT`, `TARGET`, or `BOTH` only when the page explicitly separates them.
- `implementation_status` uses the shared status vocabulary.
- AS_BUILT pages cite implementation evidence; TARGET pages cite normative authority.
- `source_sha` is the exact reconstruction SHA, not a permanent project baseline.
- Metadata fields must have a demonstrated retrieval, governance, traceability, or validation use.
- Generated timestamps must not make otherwise identical outputs nondeterministic.

Validate frontmatter with repository capabilities first (`jsonschema` is already a project
dependency and `tools/linters/check_doc_metadata.py` provides an existing pattern). Candidate-specific
extensions belong under `tools/docs_alpha/` until governance ratifies promotion.

## Canonical IDs, catalog, and headings index

`catalog.jsonl` is generated from canonical Markdown and contains, at minimum, canonical ID, path,
class, summary, truth plane, status, owner, evidence counts, authority counts, and relation counts.

`headings.jsonl` is generated from Markdown structure and contains canonical ID, heading anchor,
heading text, level, and stable section locator. It supports retrieval and validation; it does not own
the prose represented by a heading.

Validation must reject duplicate IDs, two canonical owners for the same durable fact, missing owner
paths, invalid enum values, and generated entries with no canonical source.

## Relations

`relations.jsonl` is derived from explicit metadata and links. Use a bounded relation vocabulary such
as:

```text
describes
implements
tests
conforms_to
depends_on
supersedes
derived_from
links_to
has_gap
contradicts
```

Every edge identifies source canonical ID, relation, target ID or repository path, evidence origin,
and generator version. Generated inference must be labeled and must not silently become a reviewed
architectural statement.

## Code map

`code-map.jsonl` links candidate canonical IDs to stable implementation evidence:

- package, module, schema, configuration, test, command, or public-interface path;
- symbol when deterministically extractable;
- relation type and confidence;
- recorded SHA;
- extraction method;
- evidence for ambiguous matches.

Prefer stable paths and symbols over manually maintained line numbers. `rg`, Python AST, existing
package metadata, test discovery, and schemas form the default extraction stack. ast-grep and SCIP are
bounded experiments only when they measurably improve relationships beyond those existing methods.

## TARGET reconciliation and conflict representation

TARGET reconciliation occurs after candidate AS_BUILT documentation exists. For each material claim,
record:

- claim/canonical ID;
- AS_BUILT observation and implementation evidence;
- TARGET requirement and normative authority;
- shared status value;
- relationship (`aligned`, `gap`, `contradiction`, or `unresolved`);
- confidence and reviewer;
- required follow-up owner.

Do not alter implementation and do not reinterpret authority. A lower authority cannot cancel a
higher TARGET requirement. Current code cannot prove a requirement exists; authority cannot prove the
code implements it.

`conflicts.jsonl` preserves all unresolved conflicts. A critical unresolved conflict blocks cutover.
Non-critical unresolved items require severity, owner, risk, and Tech Lead disposition.

## Legacy loss audit

### Timing and question

Run comprehensive legacy review only after steps 3–7 of the canonical flow.

Wrong question:

> Where should every old document move?

Correct question:

> Does this legacy source contain unique, still-valid knowledge absent from AS_BUILT evidence and
> current TARGET authority?

The audit is claim-oriented and loss-oriented, not destination-oriented. A legacy file may produce
zero retained claims and requires no new active destination.

### Classifications

Use exactly:

- `ALREADY_CAPTURED` — current canonical candidate already owns the valid claim.
- `CURRENT_DECISION` — still-valid decision rationale or provenance requiring linkage under current
  decision governance.
- `CURRENT_REQUIREMENT` — currently binding requirement confirmed by normative authority.
- `FUTURE_REQUIREMENT` — binding or accepted TARGET requirement not yet implemented/currently active.
- `THEORY` — explicitly non-implemented conceptual knowledge worth retaining in theory ownership.
- `OBSOLETE` — no longer valid or useful for current/future understanding.
- `CONTRADICTED_BY_CODE` — implementation evidence contradicts the legacy AS_BUILT assertion.
- `UNRESOLVED` — evidence or authority is insufficient or conflicting.

`CONTRADICTED_BY_CODE` does not cancel a binding TARGET requirement. If legacy prose restates current
normative authority but code differs, classify the requirement through its authority and record the
implementation gap separately.

### Required retained-claim record

Every retained legacy claim identifies:

- legacy source and stable locator;
- normalized claim text or digest;
- current evidence;
- authority class;
- classification;
- canonical destination and canonical ID;
- reconciliation decision and rationale;
- reviewer and review date;
- confidence;
- unresolved risk, if any.

For example:

```json
{"legacy_source":"docs/example.md#recovery","claim":"...","current_evidence":["vanguard/packages/runtime/..."],"authority_class":"implementation_evidence","classification":"ALREADY_CAPTURED","canonical_destination":"candidate-docs/architecture/runtime.md","canonical_id":"arch.runtime","reconciliation_decision":"link-only","reviewer":"reviewer-id","confidence":"high","unresolved_risk":null}
```

The ledger stores audit evidence. It does not become the canonical owner of the retained claim.

### Absorption rules

- Add a claim only to an approved existing owner or return an ownership change to blueprint review.
- Preserve source attribution without copying historical prose unnecessarily.
- Retain rationale only when current authority, decision provenance, or comprehension requires it.
- Do not preserve prose because it is old, extensive, polished, or expensive to create.
- Do not create one replacement page per legacy file.
- Do not create a permanent `_legacy/` active tree when Git history and audit ledgers provide
  sufficient recovery.
- Preserve immutable ADR provenance according to current governance; a compact decisions view links
  to it rather than replacing it.
- Leave `UNRESOLVED` claims unresolved until an authorized reviewer decides them.

## Reconciliation and knowledge-loss registers

`reconciliation-ledger.jsonl` records decisions across AS_BUILT, TARGET, and retained legacy claims.
`legacy-audit.jsonl` records legacy sources and findings. `knowledge-loss-register.jsonl` records
candidate omissions, severity, affected audiences, evidence, owner, disposition, and verification.

These are generated/controlled assurance artifacts, not manually curated alternative documentation.
Their human-readable views must regenerate from the JSONL and canonical Markdown.

## Validation

Run existing repository checks before proposing new dependencies. Candidate-scoped wrappers may call:

```bash
python3 tools/linters/check_doc_metadata.py
python3 tools/linters/check_doc_budgets.py
python3 tools/linters/check_markdown_links.py
python3 tools/linters/check_stale_paths.py
python3 tools/linters/check_falsifier_ids.py
python3 tools/linters/scan_secrets.py
```

Because current tools may intentionally exclude `candidate-docs/`, any candidate-specific extensions
must live under `tools/docs_alpha/` and be invoked explicitly. Do not modify production tooling or
enable blocking CI during reconstruction.

### Mechanical checks

Validation must cover:

- metadata schema and enums;
- canonical-ID and canonical-owner uniqueness;
- internal paths, links, and fragments;
- controlled external-link behavior;
- duplicate durable facts and orphan pages;
- AS_BUILT evidence resolution at the recorded SHA;
- TARGET authority resolution;
- explicit status and gap coverage;
- relation and code-map referential integrity;
- generated-artifact reproducibility;
- terminology consistency;
- absence of unauthorized changes outside staging/tool/generated roots;
- zero unresolved critical conflicts before cutover review.

### Terminology validation

Use consistently: `documentation reconstruction`, `AS_BUILT`, `TARGET`, `candidate-docs/`, `legacy
loss audit`, `canonical owner`, `canonical ID`, `implementation evidence`, `normative authority`,
`generated machine layer`, `independent audit`, `governance ratification`, `cutover`, and `rollback`.

Use “migration” only for this supporting migration-engineering specification or a concrete data/path
transition. Do not use `reset`, `rewrite`, `reorganization`, and `migration` as competing names for
the overall documentation reconstruction.

### Retrieval tests

Preregister representative questions before tuning the candidate. Include:

- system/subsystem responsibility and boundary;
- exact schema/configuration/command behavior;
- contributor procedure;
- current implementation status;
- TARGET requirement and implementation gap;
- decision rationale and provenance.

Record query, expected canonical ID, retrieved IDs/order, answer support, token/time cost, incorrect
sources, tool configuration, and SHA. The architecture specification's retrieval threshold is the
acceptance target. Results must not be tuned against hidden questions after each failure without
recording the iteration.

## Independent audit

The final reviewer must be independent from the principal architecture author. The audit samples
code-to-doc and authority-to-doc claims, checks ownership and retrieval results, reviews the legacy
loss audit, challenges `UNRESOLVED` dispositions, and verifies that the proposed cutover contains no
unauthorized deletion or ADR-history rewrite.

Findings use critical/high/medium/low severity, evidence, affected canonical IDs, required correction,
owner, and disposition. Critical findings must be corrected and mechanical validation rerun before
governance review.

## Cutover controls

Cutover is a separate human-authorized developer operation after independent audit. It is contingent
on all of:

- independent audit completion;
- zero unresolved critical conflicts;
- successful validation;
- explicit governance ratification;
- approved backup and rollback plan;
- clean diff review against the exact candidate and baseline;
- explicit decisions for `AGENTS.md`, `docs/README.md`, root navigation, documentation authority,
  ADR governance, active-file movement/deletion, and blocking CI.

This document cannot authorize deletion from the active tree. The ratification record must enumerate
every active path moved, removed, or replaced and every governance file changed.

### Backup and rollback

Before cutover, record:

- immutable pre-cutover commit/reference;
- exact authorized diff and candidate digest;
- operator and validator identities;
- backup/recovery location;
- rollback triggers;
- rollback commands or forward-recovery procedure;
- post-rollback validation commands.

Rollback triggers include unexpected path loss, broken navigation, metadata/link/authority failures,
missing ADR provenance, generated-layer irreproducibility, or diff outside authorized scope. A
rollback must restore the pre-cutover documentation and governance behavior without destructive
history rewriting.

### Post-cutover verification

Run all ratified documentation checks from a clean checkout, regenerate the machine layer, repeat the
critical retrieval sample, verify active navigation and authority links, confirm historical decision
recovery, and rehearse or mechanically verify rollback. Record the exact post-cutover SHA.

## Atlas experiments

Atlas research is explicitly non-blocking. Experiments may measure whether metadata improves routing,
whether AST/symbol extraction improves code maps, or whether alternative retrieval reduces time and
tokens. Each experiment must declare hypothesis, bounded input, baseline, metric, cost, output,
decision rule, and removal plan.

No Atlas experiment may delay a valid candidate, become normative authority, require a generated
artifact to be maintained manually, or enter blocking CI without later governance ratification.

## Readiness checklist

The supporting process is satisfied when:

- the exact SHA and reproducible inventory are recorded;
- metadata and canonical IDs validate;
- generated catalog, headings, relations, and code map reproduce;
- TARGET/AS_BUILT gaps and conflicts are explicit;
- legacy review occurred only after the initial canonical model and asks the loss-oriented question;
- every retained legacy claim has the required provenance and decision fields;
- no legacy file is assigned a destination merely for completeness;
- link, terminology, traceability, retrieval, and knowledge-loss checks pass;
- the independent audit is complete and critical findings are corrected;
- proposed cutover changes are isolated from candidate production;
- governance ratification, clean diff, backup, rollback, and post-cutover checks gate any cutover.
