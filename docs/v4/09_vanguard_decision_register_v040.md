---
id: VG-09
file: 09_vanguard_decision_register_v040.md
title: "Vanguard v4.0 — Decision Register"
version: 4.0.0
status: LIVING
authority_scope: >
  Architecture decision records with reversal conditions; the reasoning behind
  each adjudication between the two pre-v4 lineages; the corrections of claims
  found false or impossible, each bound to the test that now catches it.
supersedes: none (v4 is the first version of this document)
superseded_by: none
budget_words: 3000
owners: [Tech Lead]
last_reviewed: 2026-08-14
---

# Vanguard v4.0 — Decision Register

> **The rule that makes this document worth keeping.** Every entry states a **reversal condition** — what would have to become true for the decision to be wrong. That converts a decision from dogma into a hypothesis with an expiry, and it is the single practice most worth carrying forward.

Append-only. An entry is never edited; it is superseded by a later entry that cites it.

---

## 1. Format

| Field | Content |
|---|---|
| Decision | What was decided, in one sentence |
| Context | What made the decision necessary |
| Alternative | What was rejected, stated fairly enough that its advocate would recognise it |
| Reversal condition | What would make this wrong, or an explicit "never, and here is what that assumes" |
| Status | `accepted` · `superseded by ADR-nnnn` · `reversed on evidence` |

**Stating the losing alternative fairly is not courtesy.** A register recording only winners cannot support a reversal, because the reader has no idea what to reconsider.

---

## 2. Foundational decisions

| ADR | Decision | Reversal condition |
|---|---|---|
| `0000` | ADRs are append-only, numbered, and each states a reversal condition | Never — this is the meta-rule |
| `0001` | TypeScript on a Node-compatible runtime for the control plane | Team composition shifts decisively to another language, **or** the interactive-surface roadmap is abandoned, which would make the choice a coin-flip |
| `0002` | Subprocess with line-delimited JSON as the seam to systems components | A measured hot path exceeds thousands of calls per second, justifying an in-process binding |
| `0003` | Agent-loop primary; no runtime workflow graph | A reference reconstruction proves inexpressible without a graph (`03 §2.2`) |
| `0004` | The verifier is immutable and unreachable from every capability | Never within this programme's assumptions. Reversal invalidates `07` entirely |
| `0005` | No runtime extension discovery; registries freeze at composition | Never without a replacement audit mechanism |
| `0006` | No systems-language components in Phase 0, including the index | A measured number on a real repository crosses a stated threshold |
| `0007` | Parallel independent execution from the first loop commit | Measured latency parity on real tasks, which falsifies `02 [C-04]` |

---

## 3. Adjudications between the two lineages

The pre-v4 corpus held two lineages that each claimed authority over the same contracts. Each row below records **why** one prevailed, because a verdict without reasoning cannot be revisited.

| ADR | Decision | Reasoning | Reversal condition |
|---|---|---|---|
| `0008` | JSON Schema 2020-12 is normative; a TypeScript validator is an implementation | A TypeScript-first validator expresses refinements and branded types with no schema representation, handing other languages a lossy derivative that drifts silently | Only one language ever consumes the contracts — which would falsify the multi-language premise itself |
| `0009` | RFC 8785 canonicalisation, not a house algorithm | A hand-rolled sort-and-number specification is a defect surface with no upside; a divergent digest breaks loop detection **silently** | The standard proves inadequate for a required type, documented with the specific failing case |
| `0010` | A transactional embedded store with write-ahead logging; line-delimited JSON is export only | Append-only files fail on atomic multi-record commit, torn writes, concurrent reads and indices — four problems solved at near-zero cost | Storage volume exceeds what an embedded store handles, at which point the export format is unchanged |
| `0011` | Capabilities carry resources, not only verbs | A verb-only "read-only" child can read the evaluator bundle, the policy configuration and the signing keys. All read-class, all permitted | Never — this is `05 [S1(a)]` |
| `0012` | Attenuation denies out-of-scope requests; it never silently intersects | Repeated over-broad requests are the strongest intrusion signal the system produces, and silent narrowing discards it by design | Denial noise proves unmanageable, which would be a policy-authoring defect, not an argument for silence |
| `0013` | Three processes in Phase 0, not five | Five processes means five supervision surfaces before any feedback signal exists | Phase 1, when the perimeter hardens — this is a **scheduled** reversal, not a hypothetical |
| `0014` | Two languages at the first contract lock, not three | Vectors validated against a single implementation are self-agreement; a third language has no consumer until the perimeter supervisor exists | A third consumer appears |
| `0015` | Promotion is a partial order over a frontier, not a scalar objective | A scalar is self-reinforcing through the corpus: what it rewards becomes what is recorded, trained on, and optimised harder | A domain where every dimension is genuinely commensurable — none is known |
| `0016` | Operators are data in the competence graph, not functions in the loop | A loop hard-coding "planning" can never replace its planner. This is what makes operator-level improvement reachable at all | Never without abandoning self-improvement above the prompt level |
| `0017` | Competence is a graph, not an array | An array cannot express contradiction, partial supersession, per-domain activation or lineage-preserving forgetting | Never |
| `0018` | Invalidation conditions are mandatory and non-empty | A claim that cannot state what would refute it is not knowledge. Empty arrays fail at parse (`04 [INV-1]`) | Never — this is the operational form of falsifiability |
| `0019` | Self-modification is a release pipeline; in-place modification is prohibited | A process that rewrites its running components cannot verify the result with the components it just rewrote, and the failure is undetectable from inside | Never within this programme's assumptions |
| `0020` | `VG-nn` document identity equals the file index | The approved plan offset them by one, which is a permanent filename-to-ID trap for every future reader | Never — the cost was paid once |

---

## 4. Corrections

Claims found false, impossible, or unverifiable. **Each is bound to the test that now catches it**; a correction without a test is not migrated (`00 §8`).

| ADR | Claim as stated | Why it was wrong | Now caught by |
|---|---|---|---|
| `0021` | "Every effect passes a mediating layer" | A logical mediator in the host language is not a containment boundary. Subprocess execution grants execution *inside an already-limited environment*; nothing intercepts syscalls | `05 [K-01]`, `05 [K-22]`, `MF-11` |
| `0022` | Containment reported as a boolean | The runtime cannot verify that property at that granularity. Replaced by a containment report with startup probes | `05 [K-42]`, `MF-13` |
| `0023` | A size ceiling covering the trusted computing base | The ceiling applies to the policy kernel; the TCB includes the operating system, runtimes, stores and build pipeline. Concealing a dependency does not remove it | `05 [K-02]`, `AT-08` |
| `0024` | Concurrency safe because reads precede writes | Commutativity is a property of the resource, not the verb. Reading a queue, a price or a clock is non-commutative with time | `03 [CC-7]`, `MF-19` |
| `0025` | A dying process emits a terminal event | A killed process emits nothing. Satisfiable only against a graceful-shutdown mock, and untestable against the real failure | `03 §9`, `MF-21` |
| `0026` | An external effect always resolves to success or failure | Some cannot be determined. Resolving them anyway manufactures evidence | `05 [F-22]`, `MF-22` |
| `0027` | Capability widening as a constant | A constant standing in for a classifier that did not exist. The predicate appeared to fail closed on all tool use, and the resulting deadlock was documented as a property of the model | `05 [K-32]`, `MF-01` |
| `0028` | Justifying spans reset each turn | The predicate evaluated over a set that could not contain untrusted content by construction. The invariant existed, had a test, and did nothing | `05 [K-33]`, `MF-02` |
| `0029` | Read-only mounts protect the evaluator | Necessary, not sufficient: a candidate can add a **new** file that shadows the grader, invisible to a tracked-file diff | `06 §4.3`, `MF-16` |
| `0030` | A passing verdict licenses a memory write | The verdict gates the *artifact*, never the *generalisation* extracted from it | `06 [MEM-1]`, four-stage pipeline |
| `0031` | Provider errors as task failures | An attacker who can induce rate limits on one arm can manufacture a lift result. An integrity control, not accounting hygiene | `06 [V-05]`, `MF-17` |
| `0032` | Schemas strict for both readers and writers | `additionalProperties: false` on a reader rejects every future field, contradicting `04 [CT-44]`. Split into generated writer and reader profiles | `SC-10`, `MF-27` |
| `0033` | Vector agreement establishes schema equivalence | No finite suite establishes equivalence over an infinite instance space. Disagreement is conclusive; agreement is corroboration | `04 §17` property tests |
| `0034` | An architecture test requiring four process identities in Phase 0 | Phase 0 ships three processes and no updater, so the test could not pass. Now phase-aware | `05 [AT-11]`, `03 §12` |
| `0039` | A grant carrying no descriptor | Prose said a grant binds one call; neither type nor schema carried it, so point-of-effect verification had nothing to compare | `04 [CT-51]`, `MF-31` |
| `0040` | "Resources are a subset" with no decision procedure | Undecidable for pattern selectors. Now a per-kind relation that denies every undefined pair | `04 [CT-52]`, `MF-32` |
| `0041` | A mutable timestamp inside a content-addressed artifact | Every check would change the digest. Moved to a keyed check record | `04 [CT-53]`, `MF-33` |
| `0042` | Invalidation satisfiable with only manual conditions | A wholly manual artifact met `INV-1` and still falsified `02 [C-12]` | `04 [INV-2]`, `MF-34` |
| `0043` | Every event bound to an episode | Evolution and governance events belong to no episode; a synthetic identifier would be fiction in the ledger | `04 §12.1`, `MF-35` |
| `0044` | A single trailing emit point | A crash between dispatch and emit left no record the effect was attempted, making an executed effect invisible rather than undeterminable | `05 [K-47]`, `MF-36` |

---

## 5. Deferred with a scheduled reversal

Distinct from `10`, which holds deferrals without a date. These have one.

| ADR | Deferred | Reversal |
|---|---|---|
| `0035` | Five-process split | Phase 1 perimeter hardening |
| `0036` | Third-language conformance vectors | When the perimeter supervisor exists |
| `0037` | Memory-write gating tests | Phase 2, with the memory ticket |
| `0038` | Schema `LOCKED` status | `TK-01`, when two implementations agree and canonicalisation triples exist |

---

## 6. What belongs here, and what does not

An ADR is written when a decision would otherwise become tribal knowledge. Not for every choice — a register of everything is a register nobody reads.

The test: **would a competent engineer arriving in six months be surprised by this, and unable to reconstruct why?** If yes, write it. If they would reach the same conclusion unaided, do not.

---

## 7. Sprint 0 adoption decisions

These rows adopt the GTS-13C programme without making it a decision authority. For this section, `basis` records context, rationale, the fairly stated losing alternative and the principal consequence; `links` records affected artifacts/components, verification and related contract rows. Approval is joint: Tech Lead + Project Lead. Until both approvers sign the baseline, status remains `proposed` and implementation merges remain closed.

| ADR | Decision | Basis | Links | Owner · approval | Reversal condition |
|---|---|---|---|---|---|
| `0045` | New decisions use the expanded fields required by the Sprint 0 mandate; old entries remain immutable and are supplemented only by later entries | The earlier compact format omits scope, evidence, consequences, affected components and approval metadata. Rewriting history was rejected because it would violate append-only reconstruction. Consequence: later entries are denser | Affects this record and future ADRs; verify with governance review; `REQ-GOV-001` | Tech Lead + Project Lead · `proposed` · 2026-08-14 | A machine-readable ADR store supersedes this table while preserving every historical field and link |
| `0046` | GTS-13C is the sole active programme plan and owns sequencing and rationale only | Competing programme plans recreate dual authority. Treating GTS-13C as a contract was rejected because rules would then have two owners. Consequence: projected decisions in GTS-13C may lag their owners | Affects registry, developer packet and PR review; verify `TEST-GOV-001`; `REQ-GOV-001` | Tech Lead + Project Lead · `proposed` · 2026-08-14 | A jointly approved successor explicitly supersedes GTS-13C and preserves its history |
| `0047` | `spike/` and `slice/` are disposable consumers only, may never be imported, and must be deleted at the S4 gate | Fast provider and end-to-end feedback are valuable only if they cannot become architecture. Keeping prototypes as references was rejected because imports make deletion negotiable. Consequence: surviving knowledge must be written as notes/findings | Affects dependency CI, `spike/`, `slice/`; verify `TEST-ARCH-002` and S4 absence check; `REQ-ARCH-002` | Tech Lead + Project Lead · `proposed` · 2026-08-14 | Replace the experiment with a separately reviewed production adapter behind a port; disposable code is still deleted |
| `0048` | The S4 trust-spine gate runs a scripted trajectory with no model dependency | Safety controls must be independently testable. A model-backed demo was rejected because model behaviour can mask missing enforcement. Consequence: model integration cannot become a prerequisite of kernel verification | Affects kernel/runtime test harness; verify `TEST-TRUST-001`; `REQ-TRUST-001` | Tech Lead + Project Lead · `proposed` · 2026-08-14 | Never within the MVP; reversal would invalidate independent assurance |
| `0049` | Shipped tools begin as typed `read/search/patch/test`; shell is selector-scoped and privileged, while `vg-shell-only` remains the permanent experimental baseline | Typed effects narrow authority and improve attribution. Shell-first production was rejected; deleting shell baseline was also rejected because it destroys the control condition. Consequence: two distinct manifests are maintained | Affects adapters, manifests and kernel policy; verify typed-schema, allowlist and undeletable-manifest tests; `REQ-HAR-*` | Tech Lead + Project Lead · `proposed` · 2026-08-14 | Paired evidence shows typed tools cost more than they return; the control manifest remains for comparison |
| `0050` | Effects are execution primitives; Episodes coordinate open-ended work; declared durable state machines coordinate approvals, releases and governance; tools are not Episodes | One recursive coordinator preserves attribution, while finite governance must be restartable and readable. A universal workflow graph and an Episode-driven compliance path were rejected. Consequence: governance has no model dependency and agency owns no approvals | Affects domain, kernel, agency and runtime/governance; verify architecture and restart-resume tests; `REQ-EXE-*` | Tech Lead + Project Lead · `proposed` · 2026-08-14 | Open-ended work is proved inexpressible without a graph, or a supposedly finite process cannot be enumerated in advance |
| `0051` | Every effect is attributed and recorded; only `privileged` sinks require descriptor-bound capability mediation | Universal recording is required for attribution; universal mediation was rejected because pure operations add TCB and latency without authority gain. Consequence: sink class is schema data and misclassification is adversarially tested | Affects schema, kernel, ledger and adapters; verify descriptor-substitution, misclassification and receipt tests; `REQ-KRN-*` | Tech Lead + Project Lead · `proposed` · 2026-08-14 | Evidence shows non-privileged recording costs exceed attribution value, or observation enables escalation |
| `0052` | The Active MVP Contract has two independent 100% gates: baseline assignment coverage and merged-scope evidence coverage | One coverage number conflates planned accountability with passing implementation. A partial percentage was rejected because it permits a permanent uncovered remainder. Consequence: future unmerged rows may stay open, merged rows may not | Affects contract validator, CI and PR template; verify `TEST-CONTRACT-001`; `REQ-GOV-002` | Tech Lead + Project Lead · `proposed` · 2026-08-14 | Never while contract scope remains bounded to active product and assurance requirements |
| `0053` | No implementation PR merges before the governance baseline is jointly approved; governance/CI bootstrap changes may use the documented one-time exception | A gate installed after product code is not a gate. Allowing ordinary implementation during bootstrap was rejected. Consequence: only documentation, contract, CI and repository scaffolding may precede approval | Affects protected branch and PR template; verify required checks and bootstrap record; `REQ-GOV-003` | Tech Lead + Project Lead · `proposed` · 2026-08-14 | The baseline is jointly approved and tagged; thereafter normal contract gates replace the bootstrap exception |

## 8. Sprint 0 approval events

Approval events supplement; they do not edit the proposed rows above.

| Event | Decision | Evidence | Authority | Date |
|---|---|---|---|---|
| `APPROVAL-0001` | Accept ADR-0045 through ADR-0053 as the Sprint 0 governance baseline | Governance, contract, boundary, broken-counterpart, v4 acceptance and schema gates pass locally; contract tests are executed from their registry | Repository principal `rocha`, explicitly acting as both Tech Lead and Project Lead | 2026-08-15 |
| `APPROVAL-0002` | Approve the ICD, Active MVP Contract v1 and Verification Plan for Sprint 0 scope | 22 assigned requirements: 10 covered S0 rows and 12 open T1 rows; merged-scope evidence remains 100% | Tech Lead + Project Lead | 2026-08-15 |
| `DECISION-0001` | Conditional go for Sprint 1 preparation and local schema work; no schema lock or product merge | Four real traces and field inventory exist, but independent third-engineer reconstruction, prospective human timing, hosted branch protection and a Git tag are unproven | Project Lead | 2026-08-15 |
