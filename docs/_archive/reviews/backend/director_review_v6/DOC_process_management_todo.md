# AETHER Documentation Reconstruction — Process Management and Delegation

## Role

This document manages actors, work packets, sequencing, entry gates, exit gates, and handoffs for the
documentation reconstruction of `brainopensource/cognitive-framework` on `main`.

It is subordinate to
`docs/_archive/reviews/backend/director_review_v6/DOC_prompt_documentation_todo.md` for method and
phase semantics. It does not define product truth, information architecture, migration engineering,
or tool adoption independently.

## Bootstrap precedence

1. `docs/_archive/reviews/backend/director_review_v6/DOC_prompt_documentation_todo.md`
2. `docs/_archive/reviews/backend/director_review_v6/DOC_ARCHITECTURE_SPEC.md`
3. `docs/_archive/reviews/backend/director_review_v6/DOC_process_management_todo.md`
4. `docs/_archive/reviews/backend/director_review_v6/DOC_migration_process.md`
5. `docs/_archive/reviews/backend/director_review_v6/DOC_oss_tools.md`

If an older migration-oriented instruction conflicts with the greenfield/code-first phase order,
`DOC_prompt_documentation_todo.md` wins.

None of these bootstrap documents overrides AETHER product truth; they govern how that truth is
reconstructed and represented.

Canonical terms throughout this package are: documentation reconstruction, AS_BUILT, TARGET,
candidate-docs/, legacy loss audit, canonical owner, canonical ID, implementation evidence,
normative authority, generated machine layer, independent audit, governance ratification, cutover,
and rollback.

## Authority boundaries

Product TARGET authority is `VISION.md` → `docs/SPEC.md` + `docs/01_law/` → accepted/current ADRs →
schemas, contracts and protocols → active execution documents.

AS_BUILT claims require implementation evidence from production code, executable tests, schemas,
configuration, CLI/API behavior, runtime composition, public interfaces, and relevant benchmarks at
the recorded SHA. Conflicts are represented with `IMPLEMENTED`, `PARTIAL`, `PLANNED`, `EXPERIMENTAL`,
`UNRESOLVED`, `OBSOLETE`, or `CONTRADICTED`; agents do not resolve them by preference.

## Delegation rule

```text
deterministic/repetitive → scripts, developer or ordinary AI
structured writing from an approved blueprint → ordinary capable model
ambiguity/conflict/architecture/ownership → frontier model
final architecture audit → independent frontier reviewer
destructive cutover → human-authorized developer operation
```

No actor may alter production behavior to make it agree with documentation. No worker may change
active `docs/`, ADR history, `AGENTS.md`, documentation authority, or blocking CI under a candidate
work packet.

## Roles and separation of duties

- **Tech Lead / governance owner** — approves the blueprint, resolves escalated ownership decisions,
  ratifies governance changes, and explicitly authorizes or rejects cutover.
- **Principal architecture author** — constructs the AS_BUILT model and proposed ownership map from
  evidence; cannot serve as the independent final reviewer.
- **Documentation Specialist** — manages canonical writing, consistency, metadata, and reconciliation
  within the approved blueprint.
- **Developer / deterministic tooling owner** — runs extraction and validation and may implement
  bounded helpers only under `tools/docs_alpha/`.
- **Ordinary capable AI** — writes bounded pages from approved evidence and templates; cannot redefine
  architecture or canonical ownership.
- **Frontier conflict reviewer** — resolves or records ambiguity using the authority model; cannot
  silently invent a requirement or implementation fact.
- **Independent frontier reviewer** — audits the full candidate without having authored the principal
  architecture model, ownership map, or majority of canonical content.
- **Human-authorized cutover developer** — performs only the ratified active-tree change and rollback
  procedure.

Multiple agents may investigate different evidence bundles, but they must not independently redefine
the architecture, taxonomy, canonical IDs, or canonical owners. All proposed changes to those items
return to the single blueprint owner and approval gate.

## Mandatory work-packet contract

Every delegated packet contains:

- exact subsystem;
- evidence bundle;
- allowed source paths;
- target document under `candidate-docs/`;
- canonical ID;
- expected sections;
- prohibited duplication and named canonical owners to link;
- status plane (`AS_BUILT`, `TARGET`, or explicitly separated `BOTH`);
- validation command;
- unresolved-output mechanism;
- actor and reviewer;
- entry and exit predicates.

The unresolved-output mechanism writes a structured finding to the reconciliation ledger with claim,
sources, authority class, conflict, confidence, risk, and requested decision. A worker must use it
instead of guessing or broadening scope.

## Block A — Baseline and deterministic extraction

**Maps to flow steps:** 0–3.
**Inputs:** corrected bootstrap package; `origin/main`; repository access; current `AGENTS.md` and
bounded governance/TARGET reading bundle.
**Responsible actors:** developer or ordinary AI for deterministic commands; Documentation
Specialist for evidence custody; Tech Lead for branch authorization where required.
**Outputs:** reconstruction branch; repository URL, `main`, full HEAD SHA, environment record,
deterministic inventory, command manifest, and errors register.
**Entry gate:** bootstrap documents are committed and cross-document validation passes.
**Exit gate:** another executor can reproduce the inventory at the recorded SHA; production, tests,
schemas, configuration, CLI/API, runtime, tooling, CI, benchmarks, and documentation paths are
enumerated without recursively interpreting legacy prose.

Management rules:

- Resolve and record the exact HEAD for this execution; never reuse a SHA embedded in a prior report.
- Helper tools are confined to `tools/docs_alpha/`; generated artifacts are confined to
  `.generated/knowledge/`.
- `candidate-docs/` is not populated until the AS_BUILT model and blueprint gates open.

## Block B — Frontier AS_BUILT architecture discovery

**Maps to flow step:** 4.
**Inputs:** deterministic inventory and bounded implementation evidence at the recorded SHA.
**Responsible actor:** principal frontier architecture author, with subsystem evidence gathering
delegated through bounded packets.
**Outputs:** AS_BUILT subsystem model, dependency and flow model, public-interface map, evidence map,
status/confidence register, and unresolved findings.
**Entry gate:** Block A exit gate is satisfied.
**Exit gate:** every production subsystem has an evidence-backed responsibility and boundary; runtime
composition and public behavior are traced; TARGET observations remain separately labeled; no legacy
taxonomy has preselected the model.

## Block C — Canonical documentation blueprint

**Maps to flow step:** 5.
**Inputs:** approved AS_BUILT model; `DOC_ARCHITECTURE_SPEC.md`; user/retrieval needs; unresolved
ownership findings.
**Responsible actors:** principal architecture author proposes; Documentation Specialist checks
retrieval and maintainability; Tech Lead approves.
**Outputs:** candidate tree blueprint, canonical IDs, canonical owners, page purposes, evidence
bundles, work packets, and validation plan.
**Entry gate:** Block B exit gate is satisfied and critical AS_BUILT ambiguities are resolved or
explicitly registered.
**Exit gate:** one canonical owner exists for each durable fact; every proposed leaf is evidence-
justified and non-empty; no agent has an independent competing taxonomy; Tech Lead approval is
recorded.

## Block D — Bounded document production

**Maps to flow step:** 6.
**Inputs:** approved blueprint and AS_BUILT work packets.
**Responsible actors:** ordinary capable models and Documentation Specialist; frontier reviewer only
for packet-specific ambiguity.
**Outputs:** candidate AS_BUILT Markdown under `candidate-docs/`, code/evidence links, and unresolved
findings.
**Entry gate:** Block C approval and a complete packet for each page.
**Exit gate:** all approved AS_BUILT pages are complete, status-labeled, evidence-backed, and free of
prohibited duplication; no active-tree or production-code changes exist.

## Block E — TARGET reconciliation

**Maps to flow step:** 7.
**Inputs:** candidate AS_BUILT documentation and the current product TARGET authority ladder.
**Responsible actors:** frontier architecture/conflict reviewer; Documentation Specialist records
outcomes; Tech Lead handles product-authority ambiguity.
**Outputs:** separate TARGET architecture, implementation-gap register, authority conflicts, and
candidate TARGET content.
**Entry gate:** Block D exit gate is satisfied.
**Exit gate:** every TARGET statement cites normative authority; every divergence preserves both
observed and required states; no AS_BUILT claim has been rewritten to fit TARGET and no TARGET has
been weakened to fit code.

## Block F — Legacy loss audit

**Maps to flow steps:** 8–9.
**Inputs:** initial candidate AS_BUILT and TARGET documentation, implementation-gap register, and
legacy corpus.
**Responsible actors:** ordinary AI or developer for deterministic extraction; Documentation
Specialist for claim comparison; frontier reviewer for ambiguity and conflict.
**Outputs:** `legacy-audit.jsonl`, `reconciliation-ledger.jsonl`, unique-knowledge records, obsolete
records, absorbed claims, and unresolved risks under `.generated/knowledge/`.
**Entry gate:** Blocks D and E are complete; legacy prose cannot anchor architecture discovery.
**Exit gate:** unique valid knowledge has been reviewed and absorbed into existing approved owners;
critical loss findings are zero; files without unique knowledge require no active destination;
append-only ADR provenance remains intact.

## Block G — Machine layer and validation

**Maps to flow steps:** 10–11.
**Inputs:** reviewed candidate Markdown, approved metadata schema, existing repository checks, and
accepted alpha-tool decisions.
**Responsible actors:** developer or ordinary AI for deterministic generation; Documentation
Specialist for semantic validation design.
**Outputs:** generated catalog, headings, relations, code map, reproducibility manifest, validation
results, retrieval measurements, and exception register.
**Entry gate:** Block F exit gate is satisfied.
**Exit gate:** generated artifacts reproduce from canonical sources; metadata, IDs, ownership, links,
status, traceability, terminology, and representative retrieval tests pass; optional tool value is
measured; no generated view is manually maintained as truth.

Blocking CI remains prohibited at this stage unless the Tech Lead later ratifies it in Block I.

## Block H — Independent final audit

**Maps to flow steps:** 12–13.
**Inputs:** complete candidate, source/evidence manifest, generated machine layer, validation results,
legacy loss audit, and proposed cutover diff.
**Responsible actor:** independent frontier reviewer with no principal authorship role.
**Outputs:** severity-ranked findings, evidence for each finding, correction dispositions, and an
independent readiness verdict.
**Entry gate:** Block G passes with no hidden critical exception.
**Exit gate:** all critical findings are corrected and revalidated; reviewer independence is recorded;
remaining non-critical risks have named owners and Tech Lead disposition.

The principal architecture author may answer questions and correct findings but may not issue the
independent verdict.

## Block I — Governance ratification and cutover

**Maps to flow steps:** 14–16.
**Inputs:** independently audited candidate, clean proposed cutover diff, governance-change proposal,
validation evidence, backup reference, rollback procedure, and post-cutover checklist.
**Responsible actors:** Tech Lead/human governance owner ratifies; a separately authorized developer
performs cutover; independent reviewer or designated validator verifies the result.
**Outputs:** explicit authorization record or rejection; if authorized, active-tree change,
post-cutover validation, and rollback verification.
**Entry gate:** Block H exit gate; zero unresolved critical conflicts; successful validation; clean
diff review; backup and tested rollback instructions.
**Exit gate:** either no cutover occurred, or the exact authorized change is applied, post-cutover
checks pass, rollback remains possible, and governance/navigation/validation are internally aligned.

Human/Tech Lead ratification is mandatory before:

- replacing `docs/`;
- changing `AGENTS.md`;
- changing documentation authority;
- deleting or moving active documents;
- changing ADR governance;
- enabling blocking CI checks.

Cutover authorization must name exact paths, commit/diff subject, operator, maintenance window if
needed, backup reference, rollback trigger, rollback command or procedure, and validators. Failure or
scope drift stops the operation; it does not authorize opportunistic cleanup.

## Canonical execution flow

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

No manager, agent, or block may reorder, collapse, or independently reinterpret these steps.
