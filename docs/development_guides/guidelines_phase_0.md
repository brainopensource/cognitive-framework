# GTS-13C ADOPTION, ENGINEERING BASELINE AND SPRINT 0 EXECUTION PROMPT

## 1. Mandate

Act as the accountable leadership team for adopting GTS-13C as the final Vanguard MVP program plan and converting it into the authoritative decisions, engineering contracts, verification controls, CI gates and executable backlog.

GTS-13C is the living program plan and rationale. It is not a second Decision Record, architecture contract or merge-gating specification.

This master prompt is for the Project Lead, Tech Lead and designated artifact owners. Do not distribute it to developers. Developers receive only the approved developer packet, their Sprint 0/Sprint 1 backlog and their assigned CI work.

## 2. Authority model

The source-of-truth hierarchy must be explicit:

1. Approved Decision Record — architectural and governance decisions
2. Vanguard v4 contracts — system invariants and formal contracts
3. System Architecture & Interface Control Document — structure, boundaries and interfaces
4. Verification, Threat & Evaluation Plan — assurance requirements
5. Active MVP Contract — active merge-gating requirements
6. GTS-13C — program sequencing and rationale
7. Issue tracker — daily execution
8. Rev1/Rev A and Rev2/Rev B — lead-only historical decision inputs
9. GTS-13 and GTS-13B — superseded historical plans

If two sources disagree, do not silently choose one. Record the conflict, identify the authoritative owner and resolve it through the Decision Record, ADR process or Project Lead decision.

## 3. Ownership and delegation

| Chapter                        | Responsible owner                                                       | Approval/accountability                                        |
| ------------------------------ | ----------------------------------------------------------------------- | -------------------------------------------------------------- |
| 1 · Adopt and register GTS-13C | Tech Lead + Project Lead                                                | Joint approval                                                 |
| 2 · Decision Record            | Tech Lead + Project Lead, jointly                                       | Joint accountability for every decision and reversal condition |
| 3 · Architecture & ICD         | Tech Lead drafts; Sr Dev co-authors ports and testability sections      | Tech Lead approves                                             |
| 4 · Active MVP Contract        | Tech Lead owns schema and scope; requirement owners complete their rows | Tech Lead approves the contract baseline                       |
| 5 · Verification Plan          | Sr Dev drafts                                                           | Tech Lead approves                                             |
| 6 · CI and traceability gates  | Sr Dev + Developers implement                                           | Tech Lead accepts enforcement behavior                         |
| 7 · Sprint backlog             | PM + Scrum prepare                                                      | Tech Lead validates technical dependencies                     |
| 8 · Developer packet           | PM prepares                                                             | Tech Lead verifies technical content                           |
| 9 · Baseline and go/no-go      | Project Lead decides                                                    | Decision based on Tech Lead recommendation                     |

Developers may contribute estimates, testability evidence and implementation constraints, but Chapters 1–5 and 9 must not be delegated wholesale to them.

Developers receive Chapter 7’s approved output; they do not receive responsibility for designing Chapter 7’s governance structure.

## 4. Reading scopes

### 4.1 Project Lead and Tech Lead — full corpus

Read completely before resolving authority, supersession or architectural decisions:

* Vanguard v4 documents `00` through `12`;
* `README.md`;
* `READER_PACKET.md`;
* `ANSWER_KEY.md` or its equivalent;
* General Task Solver Concepts Rev1/Rev A;
* General Task Solver Concepts Rev2/Rev B;
* GTS-13;
* GTS-13B;
* GTS-13C;
* every applicable `AGENTS.md`, `CLAUDE.md`, `GPT.md`, `GUIDELINES.md`;
* architecture, coding, security, build, test, CI and contribution instructions.

Rev1/Rev A and Rev2/Rev B are evidence used by the Project Lead and Tech Lead to reconstruct decisions. They do not independently govern implementation.

### 4.2 Sr Dev, PM and Scrum

Read:

* the approved Decision Record;
* GTS-13C;
* the applicable Vanguard v4 contracts;
* the documents required for their assigned chapters;
* repository engineering and contribution instructions.

Do not provide Rev1/Rev A, Rev2/Rev B, GTS-13 or GTS-13B unless the Project Lead or Tech Lead explicitly authorizes access for a specific leadership task.

### 4.3 Developers

Developers read only:

1. Approved Decision Record
2. GTS-13C
3. System Architecture & Interface Control Document
4. Active MVP Contract
5. Verification, Threat & Evaluation Plan
6. Approved Sprint 0/Sprint 1 backlog
7. Relevant Vanguard v4 contract references
8. Repository build, test, security and contribution instructions

Do not include:

* Rev1/Rev A;
* Rev2/Rev B;
* GTS-13;
* GTS-13B;
* obsolete reader packets;
* superseded instructions;
* this leadership execution prompt.

## 5. Sprint 0 operating model

Sprint 0 begins once the following entry conditions are met:

* GTS-13C is designated as the active program plan;
* chapter ownership is assigned;
* the source-of-truth hierarchy is published;
* the protected-branch merge policy is enabled;
* the Sprint 0 start and end dates are recorded.

Sprint 0 is time-boxed to exactly two weeks or ten working days.

Do not extend Sprint 0 to finish documentation. At its deadline:

* close Sprint 0;
* move unfinished work into explicitly owned Sprint 1 tickets;
* record why it was not completed;
* preserve any applicable blocking status;
* do not weaken a control merely because its implementation rolled into Sprint 1.

Local experiments and disposable spikes may run during Sprint 0. No implementation PR may merge into a protected branch until the minimum engineering baseline is approved.

Documentation and governance changes may be reviewed and merged under the repository’s controlled bootstrap procedure.

# ORGANIZED TASK LIST

## Chapter 1 · Adopt and register GTS-13C

**Owners:** Tech Lead + Project Lead
**Output:** One unambiguous active program plan and precedence chain

* [ ] Verify GTS-13C against every approved architectural decision.
* [ ] Register GTS-13C as the sole active successor to GTS-13 and GTS-13B.
* [ ] Mark GTS-13 and GTS-13B as superseded.
* [ ] Remove superseded plans from the active registry, navigation and developer packet.
* [ ] Preserve superseded plans in Git history or a clearly marked historical archive.
* [ ] State explicitly that GTS-13C owns program sequencing and rationale only.
* [ ] State explicitly that GTS-13C is not a normative contract or Decision Record.
* [ ] Update the Vanguard registry with status, owner, precedence and supersession metadata.
* [ ] Identify every GTS-13C statement that projects a decision owned elsewhere.
* [ ] Replace duplicated normative prose with references to stable Decision Record or contract identifiers where practical.
* [ ] Record unresolved contradictions for Chapter 2 resolution.

### Chapter 1 acceptance criteria

* Exactly one program plan is active.
* Historical plans remain reconstructable.
* GTS-13C cannot override the Decision Record, v4 contracts, ICD, Verification Plan or Active MVP Contract.
* Developers cannot accidentally discover superseded plans through the normal packet or repository index.

## Chapter 2 · Create the authoritative Decision Record

**Owners:** Tech Lead + Project Lead, jointly
**Output:** Approved, append-only Decision Record

* [ ] Give every decision a stable decision ID.
* [ ] Record the decision statement.
* [ ] Record its scope and status.
* [ ] Record rationale and evidence.
* [ ] Record alternatives considered.
* [ ] Record trade-offs and consequences.
* [ ] Record affected documents and components.
* [ ] Record the verification method.
* [ ] Record an explicit reversal condition.
* [ ] Record the accountable owner.
* [ ] Record approval date and approvers.
* [ ] Link related ADRs and Active MVP Contract requirements.
* [ ] Make changes append-only or preserve supersession history.
* [ ] Mark Rev1 and Rev2 as lead-only inputs superseded operationally by this record.

The record must cover, at minimum:

* artifact identity, graph resolution and frozen manifests in S1–S2;
* the disposable provider/API spike;
* the disposable end-to-end real-provider slice;
* mandatory delete-or-replace enforcement by S4;
* prohibition against disposable code becoming load-bearing;
* the independent no-model trust-spine gate;
* typed `read/search/patch/test` as the shipped tool baseline;
* selector-scoped, sandboxed shell fallback;
* permanent shell-only experimental benchmark manifest;
* effects as execution primitives;
* Episodes as coordinators of open-ended agentic work;
* explicit durable state machines for approvals, releases and governance;
* the workflow-graph prohibition limited to open-ended agentic control flow;
* recording and attribution of all effects;
* capability mediation for privileged sinks;
* evaluator and release-authority exteriority;
* activation-pointer promotion and rollback;
* the two-stage Active MVP Contract coverage gate;
* the restriction on merging implementation code before baseline approval.

### Chapter 2 acceptance criteria

* Every active architectural decision has an accountable owner and reversal condition.
* GTS-13C refers to Decision Record IDs rather than becoming a duplicate decision authority.
* No active decision depends on tribal knowledge held only by a reviewer.

## Chapter 3 · Create the System Architecture & Interface Control Document

**Primary author:** Tech Lead
**Co-author:** Sr Dev for ports, testability and conformance sections
**Output:** Authoritative structural and interface specification

* [ ] Define package and module boundaries.
* [ ] Define permitted dependency direction.
* [ ] Define prohibited import, call and authority paths.
* [ ] Define trusted-computing-base boundaries.
* [ ] Define process, principal and OS-identity isolation.
* [ ] Define the separation among kernel, ports, agency, governance, runtime, workload, evidence and adapters.
* [ ] Define effects as typed execution primitives.
* [ ] Define Episodes as open-ended agentic coordinators.
* [ ] Define durable state machines for deterministic governance.
* [ ] State that a tool is not an Episode.
* [ ] Define tools as typed effect-producing adapters invoked under an Episode or authorized runtime.
* [ ] Define effect classification and authorization behavior.
* [ ] Require effect attribution and durable receipts.
* [ ] Define artifact identity, artifact graphs and immutable harness manifests.
* [ ] Define the model, environment, evaluator, event store, blob store, index, clock and random ports.
* [ ] Define fake and real implementations for every active port.
* [ ] Define capability, selector and resource-boundary contracts.
* [ ] Define schema versioning, compatibility and migration rules.
* [ ] Define fast safety-clock and slow governance-clock responsibilities.
* [ ] Define context, latency, resource, security, schema and TCB margins.
* [ ] Define extension mechanisms that do not require invariant-kernel changes.
* [ ] Define architecture conformance tests.
* [ ] Give the Sr Dev explicit authorship credit and responsibility for port testability.

### Chapter 3 acceptance criteria

* Developers can implement a component without inventing a new authority boundary.
* Every active port has a test strategy and fake implementation strategy.
* Architecture drift can be detected mechanically or through an explicit review rule.

## Chapter 4 · Create the Active MVP Contract

**Owner:** Tech Lead
**Contributors:** Named owners for individual requirement rows
**Output:** Machine-readable merge-gating contract

Include only active product and assurance requirements. Management activities, documentation work and exploratory research remain backlog tasks unless they express an independently verifiable product or assurance requirement.

Every row must contain:

* `req_id`;
* authoritative source or decision ID;
* precise requirement;
* rationale;
* implementing component;
* requirement owner;
* test owner;
* dependencies;
* verification family;
* stable `test_id`;
* planned acceptance evidence;
* applicable security or performance margin;
* status: `open`, `covered` or `justified`;
* justification and compensating assurance when applicable.

### Gate A — Sprint 0 baseline assignment coverage

Before the first implementation merge:

* [ ] 100% of active rows have a stable `req_id`.
* [ ] 100% have an implementing component.
* [ ] 100% have a named requirement owner.
* [ ] 100% have a named test owner.
* [ ] 100% have an assigned `test_id`.
* [ ] 100% define expected acceptance evidence.
* [ ] All dependencies are declared.
* [ ] Status `open` is permitted and expected because the implementation may not exist yet.

This gate measures planning and accountability coverage, not passing-test coverage.

### Gate B — Ongoing merged-scope evidence coverage

For every implementation PR and at every sprint close:

* [ ] 100% of rows whose component has merged are `covered` or `justified`.
* [ ] `covered` rows link to passing automated tests and acceptance evidence.
* [ ] `justified` rows contain an approved reason, owner and compensating assurance.
* [ ] Rows for unmerged components may remain `open`.
* [ ] A PR cannot merge if it would leave a merged component with an `open` requirement.
* [ ] Coverage is calculated over merged scope, not the complete future MVP scope.

Use two separate metrics:

* `baseline_assignment_coverage = 100%`
* `merged_scope_evidence_coverage = 100%`

Never collapse these into one ambiguous “100% coverage” number.

## Chapter 5 · Create the Verification, Threat & Evaluation Plan

**Author:** Sr Dev
**Approver:** Tech Lead
**Output:** Executable assurance plan

* [ ] Define threat actors, trusted principals and authority boundaries.
* [ ] Define must-fail cases.
* [ ] Define architecture, property, conformance and fault-injection tests.
* [ ] Define prompt-injection, provenance and descriptor-substitution tests.
* [ ] Define capability forgery, replay, expiry and attenuation tests.
* [ ] Define privileged-effect misclassification tests.
* [ ] Define secret-leakage tests across prompts, events, exports and diagnostics.
* [ ] Define evaluator-isolation and sealed-data tests.
* [ ] Define crash recovery and undeterminable-effect handling.
* [ ] Define disposable-component import and S4 deletion tests.
* [ ] Define A/A noise-floor measurement.
* [ ] Define paired-comparison procedures and statistical tests by endpoint.
* [ ] Define DEV, HOLDOUT, SEALED, LIVE and DEPLOYMENT partitions.
* [ ] Define mutation, metamorphic, differential and sanitizer oracles.
* [ ] Define verifier–deployment gap monitoring.
* [ ] Define canary, promotion-freeze and rollback triggers.
* [ ] Define latency, cost, context and resource budgets.
* [ ] Map each active contract requirement to a verification family.

### Chapter 5 acceptance criteria

* The plan is implementable by developers without inventing acceptance standards.
* Every named `test_id` has a defined verification family and owner.
* The Tech Lead has formally approved the threat and evaluation boundaries.

## Chapter 6 · Implement automated traceability and CI enforcement

**Owners:** Sr Dev + Developers
**Output:** Enforced merge controls and evidence reports

This is developer work and should be assigned through Sprint 0/Sprint 1 backlog tickets.

### Baseline controls

* [ ] Parse and validate the Active MVP Contract.
* [ ] Validate unique requirement and test identifiers.
* [ ] Calculate `baseline_assignment_coverage`.
* [ ] Require it to equal 100% before the first implementation merge.
* [ ] Permit rows to remain `open` when their components have not merged.
* [ ] Require each implementation PR to reference at least one valid `req_id`.
* [ ] Generate a requirement-to-owner-to-test assignment report.

### Ongoing controls

* [ ] Calculate `merged_scope_evidence_coverage`.
* [ ] Require it to equal 100% for every proposed merge.
* [ ] Reject a merged-scope row that remains `open`.
* [ ] Validate links to passing tests or approved justifications.
* [ ] Generate requirement-to-test-to-evidence reports.
* [ ] Enforce package dependency direction.
* [ ] Enforce evaluator, workload and governance isolation.
* [ ] Prevent governance code from acquiring a model dependency.
* [ ] Prevent agentic code from owning approvals or releases.
* [ ] Prevent production imports from disposable spike or slice directories.
* [ ] Enforce delete-or-replace-by-S4 for disposable implementations.
* [ ] Protect the permanent shell-only benchmark manifest.
* [ ] Add architecture-margin, latency and TCB regression alarms.

### Controlled bootstrap

If CI enforcement itself must be merged before full automation exists:

* [ ] Use a documented, one-time bootstrap review approved by the Tech Lead and Project Lead.
* [ ] Limit the bootstrap change to contract, CI, repository or documentation infrastructure.
* [ ] Do not include product behavior in the bootstrap exception.
* [ ] Record the manual evidence that the future CI check would have required.
* [ ] Disable the exception as soon as automated enforcement becomes active.

### Required PR-template controls

Add these checks to the repository PR template:

* [ ] This PR references one or more valid Active MVP Contract `req_id` values.
* [ ] All affected merged-scope requirements will be `covered` or `justified`.
* [ ] Required tests and acceptance evidence are attached.
* [ ] No prohibited dependency or authority boundary is introduced.
* [ ] No production code imports a disposable spike or slice.
* [ ] Any architectural decision change is recorded in the Decision Record or an ADR.
* [ ] GTS-13C has not been used as a substitute Decision Record or contract.
* [ ] Any deliberately omitted work is identified and linked to an owned backlog ticket.

## Chapter 7 · Convert GTS-13C into the issue-tracker backlog

**Owners:** PM + Scrum
**Technical validation:** Tech Lead
**Output:** Executable Sprint 0/Sprint 1 backlog and later milestone map

* [ ] Translate the GTS-13C sprint plan into issue-tracker tickets.
* [ ] Separate product requirements from research, management and documentation tasks.
* [ ] Link implementation tickets to Active MVP Contract `req_id` values.
* [ ] Do not create contract rows merely because a management task exists.
* [ ] Assign one accountable owner per ticket.
* [ ] Record supporting roles.
* [ ] Record dependencies and blocked-by/blocks relationships.
* [ ] Preserve required internal ordering such as S1a/S1b and S2a/S2b.
* [ ] Define acceptance criteria and evidence.
* [ ] Link applicable test identifiers.
* [ ] Record complexity, technical risk and design uncertainty.
* [ ] Define milestone, sprint and definition of done.
* [ ] Make both disposable implementations and the S4 deletion gate visible.
* [ ] Include the independent no-model trust-spine gate.
* [ ] Include Chapter 6 CI work in developer assignments.
* [ ] Identify which tasks may run locally before the merge baseline opens.
* [ ] Have the Tech Lead validate technical dependencies before distribution.

Developers receive the approved output of this chapter—their tickets—not this chapter’s governance assignment.

## Chapter 8 · Prepare and distribute the developer packet

**Owner:** PM
**Technical verification:** Tech Lead
**Output:** Clean, role-appropriate developer packet

Include:

1. Approved Decision Record
2. GTS-13C
3. System Architecture & Interface Control Document
4. Active MVP Contract
5. Verification, Threat & Evaluation Plan
6. Approved Sprint 0/Sprint 1 backlog
7. Assigned Chapter 6 CI tickets
8. Relevant Vanguard v4 contract references
9. Repository build, test, security and contribution instructions

Exclude:

* Rev1/Rev A;

* Rev2/Rev B;

* GTS-13;

* GTS-13B;

* obsolete reader packets;

* superseded guidance;

* lead-only conflict analysis;

* this leadership prompt.

* [ ] Publish a developer reading order matching the packet.

* [ ] Confirm every developer has only the current sources.

* [ ] Confirm assigned tickets link to the governing requirements.

* [ ] Confirm developers know where to report contradictions without reopening settled decisions.

* [ ] Confirm the issue tracker is the source of truth for daily execution.

## Chapter 9 · Baseline review and go/no-go

**Decision owner:** Project Lead
**Recommendation owner:** Tech Lead
**Output:** Formal baseline decision and Sprint 1 authorization

The Project Lead must make the decision. It cannot be delegated to developers or left implicit.

### Minimum baseline review

* [ ] GTS-13C is the only active program plan.
* [ ] The authority and precedence chain is published.
* [ ] The Decision Record is approved for active decisions.
* [ ] The minimum implementation-relevant ICD sections are approved.
* [ ] The Active MVP Contract schema and active scope are approved.
* [ ] `baseline_assignment_coverage` is 100%.
* [ ] Open rows are accepted as planned future work, not misrepresented as tested.
* [ ] The Verification Plan covers every named verification family.
* [ ] Sprint 0/Sprint 1 tickets have owners and valid dependencies.
* [ ] CI enforcement is active or the controlled bootstrap procedure is approved.
* [ ] The no-model trust-spine gate remains independent.
* [ ] Disposable-code deletion obligations are visible in CI and the backlog.
* [ ] The permanent shell-only benchmark remains protected.
* [ ] Rev1, Rev2, GTS-13 and GTS-13B are absent from the developer packet.
* [ ] The PR template contains the GTS-13C non-authority safeguard.
* [ ] Cross-document consistency has been reviewed.

### Sprint 0 closure

At the end of ten working days:

* [ ] Close Sprint 0 without extending it.
* [ ] Identify completed outputs.
* [ ] Move unfinished work into owned Sprint 1 tickets.
* [ ] Preserve blocking status for unfinished control work.
* [ ] Record risks introduced by each rollover.
* [ ] Calculate current merged-scope evidence coverage.
* [ ] Obtain the Tech Lead’s written recommendation.
* [ ] Have the Project Lead issue a formal go, conditional-go or no-go decision for Sprint 1.
* [ ] Tag the approved documentation and contract baseline.

A rollover does not waive a gate. Code whose required control is unfinished remains unmerged until the control is satisfied.

# DAY-ONE DEVELOPER HANDOFF

Developers receive:

* the approved developer packet;
* the Sprint 0/Sprint 1 backlog produced by Chapter 7;
* assigned Chapter 6 CI and traceability tickets;
* named technical owners and escalation paths.

Developers do not receive the nine-chapter leadership task list as their work queue.

Permitted early work includes:

* repository and CI scaffolding;
* architecture-test infrastructure;
* contract parsing and traceability tooling;
* pure domain types and port interfaces;
* schema archaeology;
* disposable local provider experiments;
* no-model trust-spine harness preparation.

Any early work that lacks the minimum merge baseline remains local or on an unmerged branch.

# WORKING CONSTRAINTS

* Do not let GTS-13C become a second Decision Record or contract.
* Enforce that rule in the PR template.
* Do not delegate ownership of the Decision Record, ICD shape or Active MVP Contract to developers.
* Do not distribute lead-only historical reviews to developers.
* Do not silently resolve document contradictions.
* Do not delete historical reasoning.
* Do not allow disposable code to become production architecture.
* Do not merge implementation code before the minimum baseline gate.
* Do not require unimplemented components to have passing tests.
* Do require every active baseline row to have a test ID and named owner.
* Do require every merged-scope row to be covered or justified.
* Do not turn management or research tasks into normative contract requirements.
* Do not extend Sprint 0 beyond ten working days.
* Do not weaken an unfinished gate when its implementation rolls into Sprint 1.
* Do not give agentic components authority over evaluation, approval, release or promotion.
* Do not begin autonomous promotion or self-improvement in the MVP.
* Prefer executable contracts, tests, CI evidence and issue-tracker work over additional prose.

# REQUIRED FINAL REPORT

Report:

1. Files read, grouped by reading scope
2. Conflicts found
3. Resolutions applied
4. Documents created or modified
5. Documents archived or superseded
6. Registry and ADR changes
7. Decision Record status
8. Architecture & ICD status
9. Active MVP Contract row count
10. Baseline assignment coverage
11. Merged-scope evidence coverage
12. Verification Plan status
13. CI and PR-template enforcement status
14. Sprint 0/Sprint 1 backlog readiness
15. Developer packet contents
16. Work completed during Sprint 0
17. Work deliberately not done and why
18. Work unfinished at the deadline, its new owner and Sprint 1 ticket
19. Accepted risks and remaining blockers
20. Tech Lead recommendation
21. Project Lead’s explicit go, conditional-go or no-go decision

The report must make omissions and deferrals as reconstructable as completed work.
