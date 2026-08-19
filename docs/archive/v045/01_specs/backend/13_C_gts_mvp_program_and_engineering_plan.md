---
id: GTS-13C
supersedes: GTS-13 (original), GTS-13B (interim). Both are deleted, not archived.
title: "General Task Solver — MVP Program, Engineering Plan & Build Spine"
status: LIVING — non-normative program document
date: 2026-08-14
owners: [Project Lead, Tech Lead]
audience: everyone on the programme, including non-engineers (see Chapter 13)

authority: >
  None. This document owns the PLAN and the RATIONALE, nothing else.
  Decisions are owned by the Decision Record. Contracts are owned by the v4 set.
  Merge gating is owned by the Active MVP Contract. Where this document restates
  any of those, it is a non-authoritative projection and the owning artifact wins.

corrections_from_13B: >
  (1) End-to-end disposable slice added at S2 — the S1 item was only an API spike
      and left real integration feedback until S6.
  (2) Contradiction resolved between "mediate privileged sinks only" and "every
      effect is authorised": ALL effects are recorded; only PRIVILEGED sinks are
      capability-mediated. Sink class is now a descriptor field, not a convention.
  (3) "A tool is an Episode" removed. Tools execute typed effects; Episodes
      coordinate open-ended agentic work. Recursion is scoped to coordination.
  (4) Active MVP Contract holds product and assurance requirements only.
      Management and research tasks stay in the issue tracker.
  (5) Chapter 2 is a projection of the Decision Record, not a second source of
      truth. Local spikes may start immediately; no PR merges to main before the
      Active MVP Contract and baseline are approved.
---

# General Task Solver — MVP Program, Engineering Plan & Build Spine

> **One sentence for the whole programme.** We are building the smallest system that can honestly tell us whether machine competence accumulates — and the first thing it will do for a living is write code.

---

## Document map — what owns what

Six artifacts. Each owns exactly one thing. A statement appearing in two of them is a defect in ownership, fixed by deleting the copy, not by ranking them.

| Artifact | Owns | Status |
|---|---|---|
| **Decision Record** | Every locked decision, its trade-off, its reversal condition | Append-only, authoritative |
| **System Architecture & ICD** | Package boundaries, port signatures, isolation topology | Authoritative for structure |
| **Active MVP Contract** | `requirement → component → owner → test → evidence` | **The only merge gate** |
| **Verification, Threat & Evaluation Plan** | Must-fail suite, adversarial suite, A/A protocol, gap monitor | Authoritative for assurance |
| **Issue tracker** | What is being worked on, by whom, when | Source of truth for execution |
| **This document (GTS-13C)** | The plan and the reasoning behind it | **Non-normative.** Owns nothing else |

v4 documents `04`, `05`, `06 §3–§4` and `07 §5` remain the contract library and are cited, never restated.

---

# PART I — THE TODO LIST

Ordered by dependency, not priority. Nothing here is optional for the MVP.

**Contract-relevance tag** on each series, per Ch. 15: **[C]** generates Active MVP Contract rows · **[B]** stays in the backlog only.

## T0 · Schema archaeology — before any contract is cut · **[B]**

- [ ] **T0.1** Select three real bugs in a repository the team knows well. One single-file, one multi-file, one requiring a test to be run and reacted to.
- [ ] **T0.2** Two engineers fix them **by hand**, recording every step as a line in a flat file: observation, proposal, effect, receipt, judgement. No tooling. No schema.
- [ ] **T0.3** Third engineer independently reconstructs the run from that file alone. Every ambiguity is a missing field.
- [ ] **T0.4** Produce `field-inventory.md`: every field *needed*, every v4 `04` field *unfillable*, every field *never referenced*.
- [ ] **T0.5** Repeat for one **non-coding** task (structured-data reconciliation or log triage). Fields present in both are candidate-universal; fields in only one are candidate-domain. **The cheapest generality test that exists.**
- [ ] **T0.6** Time each manual fix. The human baseline for verified-change throughput, and never this cheap again.

> **Exit:** `field-inventory.md` merged. Any v4 `04` field with no evidence of use is marked `speculative` and does not enter v0.1.
>
> **T0 blocks the *locking* of T1 contracts. It blocks nothing else** — T0a, T0b, T10 and T11 start the same day.

## T0a · Provider API spike — S1a, deleted at S4 · **[B]**

- [ ] **T0a.1** Throwaway script calling one real provider directly. No engine, no kernel, no grants, no ledger. Discovers wire format, streaming shape, rate-limit behaviour, error taxonomy, token-accounting quirks — **before** T1 cuts schemas against untested assumptions.
- [ ] **T0a.2** Lives in `spike/`, which T10.1's dependency gate makes unimportable by anything.
- [ ] **T0a.3** Output is `provider-notes.md`, feeding T1.11 (`Recording`) and T0b. **The notes survive; the code does not.**

## T0b · End-to-end disposable slice — S2, deleted at S4 · **[B]**

> **Why this exists and why it is separate from T0a.** T0a answers *"what does the provider actually do?"* — it is an API probe. It does **not** answer *"does a request survive the whole path from a human's intent to a file on disk?"*, and without that answer real integration feedback waits until S6, which is five sprints of building against assumptions. T0b is the walking skeleton: thin, end-to-end, and built to be thrown away.

- [ ] **T0b.1** One vertical path, real provider, real repository, real file write: *prompt → model call → proposed patch → human approval → applied diff → test run → result shown*. Every stage may be the crudest possible implementation.
- [ ] **T0b.2** It **may** use the real T1 schemas and the real event store as a consumer. It **may not** be depended upon by them, nor by `kernel/`, `agency/`, `governance/` or `adapters/`.
- [ ] **T0b.3** Its purpose is a written finding, not a codebase: `slice-findings.md` recording every place the design was wrong, every latency surprise, every field that turned out unfillable in a live path. That document feeds T4, T6 and the latency budget.
- [ ] **T0b.4** **Deleted outright at the S4 exit review**, together with `spike/`. Not superseded, not archived, not "kept as a reference". The S4 trust-spine demo runs with **no model at all**, so nothing can depend on it by then. Deletion is a checked item on the gate and is verified in CI. Real provider integration is rebuilt cleanly behind `ModelPort` at T6.1 and is never lifted from this code.

> **The discipline that makes this safe:** a disposable slice earns its keep only if deleting it is free. The moment anyone argues to keep it, it has already become architecture and the argument itself is the signal to delete it faster.

## T1 · Contracts — the keel · **[C]**

- [ ] **T1.1** Canonicalisation spec: deterministic byte encoding, integer handling, field ordering, digest algorithm. ≥40 golden triples (`input → canonical → digest`).
- [ ] **T1.2** `primitives`: `Digest`, `Timestamp`, `EpisodeId`, `RunId`, `BranchId`, `ProcessId`, `ArtifactId`, `ClaimId`, `GrantId`, `PrincipalId`, `EvaluatorId`. Opaque, validated at parse.
- [ ] **T1.3** `ResourceSelector` with a **decidable inclusion relation per kind**. Kinds at v0.1: `path`, `glob`, `command`, `host`, `record`. `includes(a,b)` total, and **denies** every undefined pair. Property test: reflexive, transitive, antisymmetric-up-to-equality.
- [ ] **T1.4** `EffectDescriptor` — `{verb, sinkClass, selector, args, argsDigest, idempotencyKey, riskTier, provenance}`.
  > **`sinkClass ∈ {pure, observation, privileged}` is the field that resolves the mediation question** (T2.8 / T4.1). It is data on the descriptor, not a convention in the code, so it is testable and cannot drift.
- [ ] **T1.5** `CapabilityGrant` — `{grantId, principal, descriptorDigest, selector, constraints, expiry, parent, maxUses}`. **A grant with no descriptor digest fails at parse.**
- [ ] **T1.6** `Receipt` — `{grantId?, outcome: ok|failed|undeterminable, observedAt, resultDigest, note}`. `grantId` optional because non-privileged effects are recorded without a grant. `undeterminable` is a first-class outcome, not an error.
- [ ] **T1.7** `EventEnvelope` — `{seq, at, kind, episodeId?, processId?, causationId, correlationId, payload, provenance, dataPolicy, tenant}`. Both scope ids optional: an event belongs to an episode, to a governance process, or to neither. A synthetic id would be a lie in the ledger.
- [ ] **T1.8** `Artifact` — `{artifactId, kind, class, compensatesFor?, hypothesis, evidenceRefs, invalidationConditions[], riskDelta}`. `kind` resolves against an **extensible registry**, never an enum. `class ∈ {enforcement, compensation}`; `compensatesFor` required iff `compensation`.
- [ ] **T1.9** `Claim` — v4 `06`'s evidence claim, unchanged. `invalidationConditions` `minItems: 1` enforced in schema. **Keep exactly as v4 wrote it; it is the best single decision in the corpus.**
- [ ] **T1.10** `CorrectionRecord` — `{episodeId, proposedPatchDigest, acceptedPatchDigest, reasonCodes[], magnitude, scope}`. Reason codes: `functional_defect | missing_requirement | security_policy | test_inadequacy | maintainability | architecture_preference | style | product_change | environment_change | reviewer_disagreement`. **Scope matters:** style and preference corrections are user/team/repo-scoped and may never become general competence.
- [ ] **T1.11** `Recording` — `{modelCassetteDigest, imageDigest, envSnapshotDigest, seed, clockPolicy}`. What makes counterfactual re-execution possible. Without it, "replay" means only state reconstruction. Informed by `provider-notes.md`.
- [ ] **T1.12** `ProcessDefinition` + `ProcessInstance` — the durable state machine contract. `{processId, definitionDigest, currentState, allowedTransitions[], pendingApprovals[], boundEffectVerbs[]}`. States and transitions are **declared data**, readable by a non-engineer, resumable from the ledger without replaying any agent reasoning.
- [ ] **T1.13** Writer profile (`additionalProperties: false`) and **generated** reader profile (`additionalProperties: true`). A reader rejecting unknown fields breaks forward compatibility on its first schema bump.
- [ ] **T1.14** Second-language **reader-only** implementation. Conformance = both readers agree on all golden vectors. Disagreement is conclusive; agreement is corroboration, not proof.
- [ ] **T1.15** Migration rehearsal: add a field, bump minor, prove old readers survive and old events still reduce.

## T2 · Kernel — enforcement, permanent · **[C]**

- [ ] **T2.1** Principal model: `user`, `operator`, `episode`, `process`, `evaluator`, `release` are **distinct principals**. A governance process must not borrow an episode's authority.
- [ ] **T2.2** Grant issuance bound to `descriptorDigest`. Point-of-effect verification recomputes and compares.
- [ ] **T2.3** **Attenuation algebra.** A child grant may only narrow: verb ⊆, selector ⊆, constraints ⊆, expiry ≤, uses ≤, budget ≤. Property test: monotone, no widening fixpoint.
- [ ] **T2.4** Explicit denial as an **alertable event**, never a silent no-op. A denial producing no event is an escalation attempt you did not see.
- [ ] **T2.5** Budget as a **lease tree**. Child holds a lease on the parent's remainder. Overrun at commit debits negative and lowers the ceiling. Property test: conservation.
- [ ] **T2.6** Dispatch with **complete failure enumeration**, and an intent record written **before** dispatch — a crash between dispatch and emit must leave evidence the effect was attempted.
- [ ] **T2.7** Secret references only. No secret value in any prompt, event, export or diagnostic stream. Test: grep the full export for every known secret.
- [ ] **T2.8** **Mediation is scoped by `sinkClass`, and this is the rule that resolves the old contradiction:**

  | `sinkClass` | Recorded in ledger | Capability-mediated | Examples |
  |---|---|---|---|
  | `pure` | **Yes** | No | Deterministic transform, digest computation, reduction |
  | `observation` | **Yes** | No — but **selector-checked** and provenance-labelled | File read within an already-granted scope, index query, event query |
  | `privileged` | **Yes** | **Yes — grant required, descriptor-bound** | File write, patch apply, process exec, network egress, model call, secret access, memory write, irreversible external effect |

  **Everything is recorded. Only `privileged` traverses the kernel.** Mediating `pure` inflates the TCB and the latency budget for no security gain; failing to *record* it destroys attribution. The two properties are independent and were previously conflated.
- [ ] **T2.9** Provenance axes (origin, integrity, sensitivity, trust) with **conservative sink-oriented propagation**: a `privileged` effect whose args derive from an untrusted block requires elevation regardless of verb. Do not claim causal isolation once mixed text has entered the model — claim only that the sink narrowed authority.
- [ ] **T2.10** TCB size budget as a tracked metric with an **alarm**, plus an ADR per kernel change.

## T3 · Ledger · **[C]**

- [ ] **T3.1** Transactional append-only store, single writer, monotonic sequence, crash-safe.
- [ ] **T3.2** Pure reducer `(State, Event) → State` in `domain/`, zero I/O. Property test: associative over batches.
- [ ] **T3.3** State reconstruction: replay yields an identical state digest.
- [ ] **T3.4** Projections rebuildable from zero. A projection is a cache, never a source of truth.
- [ ] **T3.5** Line-delimited JSON export with redaction, correlation preserved.
- [ ] **T3.6** Run lease + heartbeat + **recovery scanner outside the dying process**. The terminal record is written by the recovery controller, never by the corpse.
- [ ] **T3.7** Effect reconciliation by idempotency key. Where occurrence cannot be determined, the record says `undeterminable` and **stays** that way.
- [ ] **T3.8** Cassette recorder/player for the model port. Record writes; replay serves. T1.11 made real.

## T4 · Execution — effects, episodes, processes · **[C]**

- [ ] **T4.1** **Effects are the primitive, and every effect is recorded.** Every touch of the world produces an `EffectDescriptor` and a `Receipt` in the ledger — no exceptions, because attribution depends on completeness. **Authorisation is scoped by `sinkClass` per T2.8:** `privileged` effects require a grant; `pure` and `observation` effects are recorded and selector-checked but do not traverse the kernel.
- [ ] **T4.2** **Two coordinators are built on that primitive, and they are not interchangeable.**
  - **Episodes** carry *open-ended agentic work*, where the shape is unknown before it runs. Control flow is the recursive loop. This is where the model reasons.
  - **Durable state machines** carry *approvals, releases, governance*, where the state set is known, finite, must be auditable by a non-engineer, and must survive restart without replaying agent reasoning.
  - **The test:** *if you can enumerate the states in advance and someone outside engineering would want to read them, it is a process.* Otherwise it is an episode. A state machine standing in for episode recursion is forbidden; an episode standing in for a compliance process is a defect.
- [ ] **T4.3** Episode loop: `observe → propose → authorise → effect → receipt → evaluate`. The engine knows no cognitive vocabulary — lint rule forbids `plan`, `debug`, `reflect`, `architect` as identifiers in `agency/`.
- [ ] **T4.4** **Recursion, correctly scoped.** An episode may spawn child episodes with attenuated leases and a cancellation scope. This is what an agent, a team, and a department are — one type, one budget algebra, one attenuation rule, one event stream, at every level of *coordination*. **A tool is not an episode.** A tool executes a typed effect; it coordinates nothing. Conflating the two inflates the coordination unit and destroys the very attribution the recursion exists to provide.
- [ ] **T4.5** Terminal states: `resolved | abandoned | denied | inconclusive | abstained | recovered`. **Abstention is a scored success**, not a failure.
- [ ] **T4.6** Structured concurrency: task groups, automatic cancellation propagation, per-branch workspace destroyed in `finally`, cancellation reaching the subprocess **group**.
- [ ] **T4.7** Ordering: emitted order preserved; mutations are barriers; parallelism requires a declared independence group or provably disjoint read/write sets; conflict raises an explicit event, never last-write-wins.
- [ ] **T4.8** Process engine: load `ProcessDefinition`, advance `ProcessInstance` on events, block on pending approvals, resume after restart from the ledger alone. Property test: an interrupted process resumes to the same state without re-running any episode.
- [ ] **T4.9** **Context compiler as a separately versioned artifact.** Layers `L1 SYSTEM / L2 TOOLS / L3 ENVIRONMENT / L4 TASK / L5 DIALOGUE`, rendered prefix-stable for provider cache economics. Every block tagged with source and provenance label.
- [ ] **T4.10** Operator invocation = child episode with a pinned artifact set. An operator is **data** (prompt + tool subset + context policy + termination rule), never a class.
- [ ] **T4.11** Competence estimate recorded **before** acting, scored after. Nothing consumes it yet; recording it now costs nothing and retrofitting it later costs a corpus migration.

## T5 · Perimeter & evaluator · **[C]**

- [ ] **T5.1** Rootless worker: own OS identity, mount namespace, credential set. Network denied by default; egress through a destination-aware proxy with logs.
- [ ] **T5.2** **Containment report** — mount, egress and syscall probes per run. An unverified perimeter blocks publication of any result from it.
- [ ] **T5.3** Evaluator under a **separate identity and image digest**. A candidate can neither read nor write the evaluator bundle.
- [ ] **T5.4** **Double probe** on every verdict: tracked evaluator inputs unchanged **and** no untracked additions under evaluator input paths. Both required. A verifier that cannot compute them cannot construct a verdict.
- [ ] **T5.5** Evidence plane owns the evaluation trigger — it observes termination in the ledger. **No episode may request its own evaluation.**
- [ ] **T5.6** `inconclusive` fail-closed. Provider errors, socket resets, unbuildable images and perimeter crashes never become task failures. Per-arm instrument-error rate reported; asymmetry is a confound, not a footnote.

## T6 · Coding harness — the first, disposable, point design · **[C]**

- [ ] **T6.1** Git environment adapter: worktree per branch, snapshot-bound observation, diff/patch/apply, preview before effect. Real provider rebuilt cleanly behind `ModelPort` — **never lifted from T0a or T0b.**
- [ ] **T6.2** **Default tool set is typed, not shell.** `read`, `search`, `patch`, `test` ship as the default from first integration — each with a typed schema, an explicit `sinkClass`, a risk tier and a resource selector. `shell` is a **selector-scoped fallback**, reachable only through a `command`-kind allowlist, always `sinkClass: privileged`, at a risk tier no weaker than the typed tool it substitutes for.
  > **Why typed first.** A shell-first default hands every early episode the largest and least-attenuable attack surface available, at exactly the moment the kernel is least exercised. Typed tools are also what make T2.9's provenance meaningful: `patch(file, hunk)` has an inspectable resource scope; `shell("...")` does not.
- [ ] **T6.3** `build` joins the typed set once the first four are stable. Every new typed tool still earns its place against the `vg-shell-only` baseline under T8. Only the starting point moved.
- [ ] **T6.4** CLI: interactive TUI + headless. Streaming, cancel, resume, checkpoint. `vg run`, `vg trace`, `vg why`.
- [ ] **T6.5** `vg why <artifact>` — what evidence activated it, what it predicts, what would demote it. If the operator cannot interrogate governance, they will bypass it.
- [ ] **T6.6** Descriptor-bound approvals: the approval authorises the **normalised descriptor shown to the human**, not a later-altered command. Approval is an effect against the process engine, not a side channel.
- [ ] **T6.7** Correction capture in the merge path. Reason code prompt is one keystroke, not a form.
- [ ] **T6.8** Latency instrumentation: startup, time-to-first-token, time-to-first-effect, approval round trips, event-write overhead, p95 resume. Budgets seeded from `slice-findings.md`.

## T7 · Artifact graph & harness manifests — S2a · **[C]**

> **Moved from S7.** T1.8 introduces the typed artifact at S1b. Leaving the graph and manifest machinery until S7 meant five sprints of harness work built on a component model that did not exist, and every run in that window unattributable. **T7.5–T7.7 (reconstruction and benchmarking) still wait on T6 and remain at S7** — only the graph and manifest *shape* moved early.

- [ ] **T7.1** `kind` registry: `system_prompt`, `tool_schema`, `tool_impl`, `middleware`, `skill`, `context_policy`, `retrieval_policy`, `compaction_policy`, `routing_policy`, `budget_policy`, `subagent_config`, `playbook`, `process_definition`, `runtime_image`, `operator`, `competence_claim`. **Extensible — new kinds require a schema, never a core change.**
- [ ] **T7.2** One logical edit = one commit in the harness workspace. File-level diff and rollback granularity fall out for free.
- [ ] **T7.3** `HarnessManifest`: component graph + capability requirements + evaluator bindings + budget policy. Resolves and **freezes at composition**, per episode.
- [ ] **T7.4** **`vg-shell-only` registered as a permanent baseline manifest.** One tool, selector-scoped, no middleware, no skills, no sub-agents. Not a migration artifact; never deleted. It is the standing zero-assumption control against which every typed tool, skill and context policy proves its gain under T8. Flagged undeletable in the registry.
- [ ] **T7.5** `vg harness build | run | diff | bench`.
- [ ] **T7.6** **Reconstruction suite** — express a Claude-Code-shaped, an OpenCode-shaped and a minimal-SWE-agent-shaped harness as manifests. The direct test of "every reference harness is configuration". Label honestly: a comparison against a faithful reimplementation is a comparison against *that reimplementation*.
- [ ] **T7.7** Between-episode discovery: signed, allow-listed manifests may install between runs under operator policy. Within an episode, the set is frozen.

## T8 · Instrument — concurrent, not later · **[C]**

- [ ] **T8.1** A/A runner: identical configuration against itself, N repeats, per-task-class noise floor. **No delta is interpretable until this number exists.**
- [ ] **T8.2** Paired runner: both arms attempt the same instances; analysis over discordant pairs only.
- [ ] **T8.3** Statistics module: McNemar exact for paired binary; paired bootstrap/permutation for cost and latency; survival methods for timeouts and censoring; hierarchical models for repeated repos/models/task families. **McNemar alone is not a statistics strategy.**
- [ ] **T8.4** Pre-registration artifact: hypotheses, primary metrics, alpha, correction, manifest hash, fixed stopping rule — hashed **before any arm runs**.
- [ ] **T8.5** Split discipline: `DEV / HOLDOUT / SEALED / LIVE / DEPLOYMENT`, with a touch ledger and per-instance corpus membership check.
- [ ] **T8.6** Oracle suite beyond repo tests: property, metamorphic, mutation score delta, differential vs pre-change binary, sanitizers, type/borrow checks.
- [ ] **T8.7** **Meta-evaluator dashboard.** Correlation between promotion score and accepted deployment outcome — the verifier–deployment gap. Widening past threshold **freezes promotions automatically**.
- [ ] **T8.8** Seeded-sabotage suite: plant proxy-exploiting candidates and confirm the pipeline rejects them. A gate never proven able to fail is not a gate.

## T9 · Generality falsifier — from month one · **[C]**

- [ ] **T9.1** One genuinely non-coding environment. Structured-data reconciliation is the cheapest honest choice.
- [ ] **T9.2** Domain-native evaluator under the same evaluator contract.
- [ ] **T9.3** Added through **registries, configuration and adapters only**. If it forces an episode-engine, capability-algebra or event-envelope change, the generality claim is falsified — early, cheaply, and therefore usefully.

## T10 · Engineering discipline — CI, from day one · **[C]**

- [ ] **T10.1** Dependency direction enforced as a **build failure**: `domain ← ports ← kernel ← agency ← runtime → adapters`; `governance → domain, ports, kernel` only; `cli → runtime`; `lab/` imports nothing and is imported by nothing; **`spike/` and `slice/` are imported by nothing** — this is what makes T0a and T0b disposable by construction rather than by intention.
- [ ] **T10.2** Two implementations per port from day one (fake + real). A contract satisfied by one implementation is an implementation wearing an interface.
- [ ] **T10.3** `test/broken/` — deliberately broken implementations. Every must-fail test runs against its broken counterpart and **must fail**.
- [ ] **T10.4** Architecture tests proving paths do **not** exist. Minimum set: nothing imports `spike/` or `slice/`; no route from `agency` to `adapters/evaluators`; `governance/` has no model dependency; `agency/` contains no approval logic.
- [ ] **T10.5** Fault injection over every dispatch failure path.
- [ ] **T10.6** Generated requirement-to-test map from the Active MVP Contract. CI fails on any row with neither a passing test nor an `untestable-with-justification` marker.
- [ ] **T10.7** **Specification gate: 100% test-or-justification coverage of the Active MVP Contract. No partial threshold.** No new normative rule enters any v4 document while a single contract row is uncovered and unjustified. Recorded in `00`.
  > **Why 100%, not a percentage.** A percentage gate tolerates a permanent untested remainder below the line — precisely the mechanism that produced 133 uncovered rules in v4. **The scope, not the threshold, is what makes 100% achievable:** the gate covers the active MVP contract only, which by Ch. 15's rules excludes management tasks, research tasks, and everything deferred in Ch. 3.
- [ ] **T10.8** Margin alarms, not limits: TCB LOC, p95 first-token, p95 first-effect, context tokens, schema extension slack. A margin nobody watches is a margin already spent.
- [ ] **T10.9** No-special-cases review item: a conditional naming one provider, one environment or one task type fails review. It always arrives disguised as pragmatism.

## T11 · The four executable artifacts — S0, before the first merge · **[B]**

> Not documentation. **T10.7 and Ch. 9 gate on artifact 3, so it must exist before any code merges.** A merge gate written after the code it gates is not a gate.

- [ ] **T11.1** **Decision Record.** Every locked decision with its trade-off and **reversal condition**. Append-only, authoritative. Supersedes the Rev A and Rev B analyses, which become lead-only inputs. **Chapter 2 of this document is a projection of it, not a peer.**
- [ ] **T11.2** **System Architecture & Interface Control Document.** Exact package boundaries, dependency lattice, port signatures with fake and real implementations, isolation topology, process/identity table. What an engineer builds against; Ch. 5 here is its summary, not its substitute.
- [ ] **T11.3** **Active MVP Contract.** `requirement → component → owner → test → acceptance evidence → status`. **Every PR cites a row.** Full specification in Ch. 15.
- [ ] **T11.4** **Verification, Threat & Evaluation Plan.** Must-fail suite, adversarial suite (injection, descriptor substitution, escalation, exfiltration, memory poisoning), A/A protocol, verifier–deployment gap monitor with freeze threshold.
- [ ] **T11.5** **Issue-tracker backlog.** Part II as tickets with dependencies, owners, acceptance criteria. The tracker owns *what is being done*; this document owns *why*.
- [ ] **T11.6** Cross-document consistency review, then tag the baseline.

> **The merge rule.** T11.6 **does not block** T0, T0a, T0b, T10.1–T10.3 or any local spike — start them the day the Decision Record is approved. It **does block merging to main**: no PR lands until the Active MVP Contract exists and the baseline is tagged. Spikes run on branches; the gate applies at the merge, not at the keyboard.

---

# PART II — SPRINT & TASK TABLE

Two-week sprints, split into **half-sprint milestones (a/b)** where a stated dependency would otherwise be unsatisfiable within its own sprint.

**Complexity:** S = days · M = ~1 sprint for one dev · L = ~1 sprint for a pair · XL = multi-sprint, decompose first · ⚠ = high design risk, decide with Tech Lead + Project Lead before starting.

| ID | Sprint | Track | Milestone / feature | Goal (done = this is true) | Requires | Tests | Cx | Owner | Support |
|---|---|---|---|---|---|---|---|---|---|
| **T11.1–T11.6** | S0 | Governance | Four executable artifacts | Decision Record, ICD, **Active MVP Contract**, V&T Plan, backlog exist and are tagged | — | Every **[C]** Part I item maps to contract rows; CI can parse the map | L ⚠ | Tech Lead | Project Lead, PM, Scrum |
| **T0.1–T0.6** | S0 | Contracts | Schema archaeology | Hand-written ledger of 3 coding + 1 non-coding task; `field-inventory.md` merged | — | Third engineer rebuilds the run from the file alone | M ⚠ | Tech Lead | Sr Dev, 1 Dev |
| **T10.1–T10.3** | S0 | Discipline | Repo, CI, boundaries | Cyclic import fails the build; `spike/` and `slice/` unreachable | — | Boundary gate; broken-impl harness runs | S | Sr Dev | Dev |
| **T0a.1–T0a.3** | S1a | Spike | Provider API spike | Wire format, rate limits, error shapes known; `provider-notes.md` merged | T10.1 | `spike/` unimportable; **deletion checked at S4** | S | Dev | — |
| **T1.1–T1.6** | S1a | Contracts | Wire schema v0.1 | Canonicalisation deterministic; grants bind descriptors; `sinkClass` present | T0 exit | 40 golden triples; selector-inclusion property tests | L ⚠ | Tech Lead | Sr Dev |
| **T1.7–T1.12** | S1b | Contracts | Envelope, artifact, claim, correction, recording, process | All six parse, digest, round-trip | T1.1–T1.6, `provider-notes.md` | Round-trip property test; empty-invalidation array rejected at parse | L | Sr Dev | Dev |
| **T0b.1–T0b.4** | S2a | Slice | **End-to-end disposable slice** | *Prompt → model → patch → approval → apply → test → result* runs against a real repo | T1.7–T1.12, T0a | `slice/` unimportable; `slice-findings.md` merged; **deletion checked at S4** | M ⚠ | Sr Dev | Dev |
| **T7.1–T7.3** | S2a | Contracts | **Artifact graph + manifest** *(moved from S7)* | Every mutable component is a typed file; one edit = one commit | T1.8 (S1b) | `kind` extension without core change; freeze-at-composition test | L ⚠ | Tech Lead | Sr Dev |
| **T3.1–T3.5** | S2a | Ledger | Event store & reducer | Replay reproduces an identical state digest | T1.7 (S1b) | Reduction associativity; projection rebuild from zero | M | Dev | Sr Dev |
| **T2.1–T2.5** | S2a | Kernel | Capabilities & budgets | Scope escalation denied and emitted as an alertable event | T1.3–T1.5 (S1a) | Attenuation monotonicity; budget conservation; must-fail: verb-only attenuation reads the evaluator bundle | L ⚠ | Sr Dev | Tech Lead |
| **T1.13–T1.15** | S2b | Contracts | Reader profiles + migration | Old readers survive a minor bump | T1.7–T1.12 | Cross-reader conformance; migration rehearsal | M | Dev | Sr Dev |
| **T7.4** | S2b | Harness | `vg-shell-only` permanent baseline | Baseline manifest registered, runnable against the fake environment | T7.1–T7.3, T3.1 | Builds and runs; **flagged undeletable** | S | Dev | — |
| **T2.6–T2.10** | S3 | Kernel | Dispatch & sink-class mediation | No `privileged` effect executes without a grant; all effects recorded | T2.1–T2.5, T3.1 | Fault injection on every dispatch path; must-fail: a `pure` effect skipping the ledger; must-fail: crash between dispatch and emit leaving no intent record | L ⚠ | Sr Dev | Tech Lead |
| **T3.6–T3.8** | S3 | Ledger | Recovery & cassettes | A killed worker gets a terminal record written from outside it | T3.1–T3.5 | `kill -9`; undeterminable stays undeterminable; cassette replay byte-identical | L | Dev | Sr Dev |
| **T4.1–T4.7** | S4 | Execution | Episode engine + recursion — **trust-spine demo** | **A scripted trajectory runs with no model at all** | T2, T3 | Denial, attenuation, budget exhaustion, atomicity, recovery, evaluator isolation, secret non-disclosure — all green | XL ⚠ | Tech Lead | Sr Dev, 2 Dev |
| **T4.8** | S4 | Execution | Process engine | An interrupted approval process resumes from the ledger without replaying an episode | T3.6, T1.12 | Restart-resume property test; states readable by a non-engineer | M ⚠ | Sr Dev | Dev |
| **T5.1–T5.2** | S4 | Kernel | Worker perimeter | Containment report produced; unverified perimeter blocks publication | T2.6 | Mount, egress, syscall probes; red team reaches nothing | L ⚠ | Sr Dev | Dev |
| **DELETE `spike/` + `slice/`** | S4 gate | — | Disposables removed | Both directories gone from the repository | S4 exit review | Checked gate item; absence verified in CI | S | Sr Dev | — |
| **T5.3–T5.6** | S5 | Instrument | Evaluator identity | A candidate can neither read nor write the evaluator bundle | T5.1 | Double probe required on verdict; must-fail: planted untracked file under an input glob scores as passing | L | Dev | Tech Lead |
| **T4.9–T4.11** | S5 | Execution | Context compiler + competence estimate | Prefix-stable rendering; estimate recorded pre-action | T4.3 | Cache-hit ratio measured; provenance label on every block | M | Dev | Sr Dev |
| **T6.1–T6.3** | S6 | Harness | Git env + **typed tools** | First real bug fixed end-to-end with `read/search/patch/test`; shell only via allowlist | T4, T5, `slice-findings.md` | New file appears in preview and patch; export complete and redacted; **S4 deletions still hold** | L | Sr Dev | 2 Dev |
| **T6.4–T6.8** | S6 | Harness | CLI, approvals, corrections, latency | p95 budgets met; corrections captured with reason codes | T6.1, T4.8 | Descriptor-substitution-after-approval must-fail; latency gate blocks release | L ⚠ | Dev | PM (UX), Sr Dev |
| **T7.5–T7.7** | S7 | Harness | `vg harness` + reconstructions | Three competitor-shaped harnesses expressed as manifests | T7.1–T7.4 (S2), T6 | **Any reconstruction requiring a core change falsifies the configurability claim** | XL ⚠ | Sr Dev | 2 Dev |
| **T8.1–T8.2** | S7 | Instrument | A/A floor + paired runner | A per-task-class noise floor number exists | T3, T6, T7.4 | A/A on ≥3 task classes; floor refuses to report when degenerate | M | Dev | Tech Lead |
| **T8.3–T8.6** | S8 | Instrument | Statistics, splits, oracles | Comparative claims become computable | T8.1–T8.2 | Pre-registration hash enforced; touch ledger detects leakage; mutation-score delta computed | L ⚠ | Tech Lead | Dev |
| **T8.7–T8.8** | S8 | Instrument | Meta-evaluator + sabotage | Promotions freeze automatically when the gap widens | T8.3 | Seeded proxy-exploiting candidates rejected; gap dashboard live | L ⚠ | Tech Lead | Sr Dev |
| **T9.1–T9.3** | S8 | Generality | Non-coding environment | Added with **zero** episode-engine changes | T4, T5.3 | Core-change detector in CI; domain evaluator under the same contract | L ⚠ | Sr Dev | Dev |
| **T10.4–T10.9** | S0→S8 | Discipline | Continuous | **100% Active MVP Contract coverage**; margins alarmed | T11.3 | Requirement-to-test map green; every uncovered row carries a justification marker | M | Scrum | All |
| — | S9 | All | **MVP gate review** | Go/no-go on the four gate questions (Ch. 10) | Everything above | The three-real-bugs judgement test | — | Project Lead | Tech Lead, PM |

**PM owns** throughout: dogfood scheduling, opt-out reason logging, the human baseline dataset, user-facing latency acceptance, correction-capture UX. **Scrum owns**: increment exit-test enforcement, the weekly three-question review, the Active MVP Contract coverage burndown. Neither owns architecture.

---

# PART III — THE PROGRAM DOCUMENT

## Chapter 1 · What this document is

Three audiences, one text. Engineers read Ch. 4–9 and Ch. 15. Leads read Ch. 2–3 and 10. Everyone reads Ch. 13. If Ch. 13 does not make sense to a non-engineer on the team, that is a defect in Ch. 13, not in the reader.

This document owns **the plan and the reasoning**. It defines no contract, gates no merge, and locks no decision. See the document map above for what owns what.

## Chapter 2 · Locked decisions — **a projection, not a source**

> **Non-authoritative.** The **Decision Record** is the single source of truth for every row below, including the exact wording of each reversal condition. This chapter exists so a reader of the plan can see the constraints without a second file open. **Where this table and the Decision Record differ, the Decision Record wins and this table is the defect.** Do not amend a decision here; amend it there and regenerate this.

| # | Locked concept | Reversal condition |
|---|---|---|
| L-01 | The evaluator is unreachable from everything it judges | Never within this programme's assumptions. Reversal invalidates the entire measurement chapter |
| L-02 | Authority is **resource-scoped**, never verb-scoped | Never. A verb lattice lets "read-only" read the signing keys |
| L-03 | A guarantee may not exceed the boundary that actually enforces it | Never. This is the audit stance |
| L-04 | Every claim carries non-empty invalidation conditions, enforced at parse | Never. A claim that cannot state its own refutation is not a claim |
| L-05 | Promotion moves an activation pointer; it never overwrites a running component | Never. A process cannot verify a rewrite using the components it just rewrote |
| L-06 | Rollback is tested **before** the promotion it protects | Never |
| L-07 | `inconclusive` is a first-class outcome, excluded from both numerator and denominator | Never. Otherwise induced rate limits can manufacture a lift result |
| L-08 | Comparisons are paired; effects reported with intervals; families pre-registered and hashed | Never. Post-hoc family selection is undetectable after the fact |
| L-09 | No self-authored evaluation criteria; no scalar reward; novelty observed, never optimised | New evidence that a novelty metric resists adversarial generation. None is known |
| L-10 | No runtime workflow graph governs **open-ended agentic control flow** — episode recursion handles that. This does **not** prohibit a durable state machine for approvals, releases and governance, where the state set is finite, known in advance, and auditable by a non-engineer | A reference reconstruction proves *open-ended agentic work* inexpressible without a runtime graph |
| L-11 | Registries freeze at composition **per episode**; signed discovery between episodes is permitted | Never without a replacement audit mechanism |
| L-12 | Every mutable component declares `enforcement` or `compensation` + its expiry hypothesis | Never. This is how the Bitter Lesson becomes maintenance instead of catastrophe |
| L-13 | Coding is the first environment, not the ontology | Never. Any coding concept that cannot express in the shared space is a defect |
| L-14 | Biological, cosmological and physical analogies are non-normative | Never in a specification. See Ch. 12 for their legitimate use |
| L-15 | Default tools are typed; shell is a selector-scoped fallback. `vg-shell-only` is retained permanently as the experimental baseline | Measured evidence that typed tools cost more than they return against that baseline |
| L-16 | The Active MVP Contract gates every merge at 100% test-or-justification | Never while the scope stays "active MVP" — the threshold is achievable precisely because the scope is bounded |
| **L-17** | **All effects are recorded; only `privileged` sinks are capability-mediated** | Evidence that recording non-privileged effects costs more than the attribution it buys, or that an `observation` sink enabled an escalation |
| **L-18** | **Tools execute typed effects; Episodes coordinate open-ended work. A tool is not an Episode** | A tool that genuinely requires child coordination — at which point it was an operator, not a tool |

## Chapter 3 · Open concepts — design later, with a trigger

Writing these now would formalise guesses. Each names what must happen first. **None of these generate Active MVP Contract rows** (Ch. 15.2).

| # | Open concept | Design when |
|---|---|---|
| O-01 | Competence graph lifecycle (promotion/demotion/activation topology) | One distilled artifact clears the A/A floor. **Derive the lifecycle from the survivor, not before it** |
| O-02 | Semantic memory and consolidation schedule | A corpus exists and retrieval value is measurable |
| O-03 | General subagent composition beyond operator invocation | A real task needs depth the operator mechanism cannot reach |
| O-04 | Model routing policy | Two providers are live and a cost/quality frontier is measurable |
| O-05 | Search over trajectories, process rewards, reflection | Deferred as capability; **their contracts land now** so the retrofit is not a corpus migration |
| O-06 | Training on the corpus | Opt-in, licensing, per-instance contamination tracking, adversarial verifier audit all exist |
| O-07 | Autonomous promotion of any class | Measured false-promotion and rollback rates acceptable for that class. Never for kernel or evaluator |
| O-08 | Multi-tenant isolation and enterprise policy | A second tenant exists |
| O-09 | Graphical authoring canvas | Users ask to *edit* a rendered trajectory, not only inspect it |
| O-10 | Cross-domain artifact portability classes | Two environments have produced artifacts worth comparing |
| O-11 | Process-definition authoring surface | More than three governance processes exist and engineers stop being the ones editing them |

## Chapter 4 · The spine — one primitive, two coordinators, five nouns

### 4.1 The reduction

```
Effect     descriptor → [authorisation if privileged] → execution → receipt
             │            ALL effects recorded. Only privileged mediated.
             │
             ├── Tool       executes ONE typed effect. Coordinates nothing.
             │
             ├── Episode    identity + lease + context + operators + terminal state
             │              ⟵ RECURSIVE. Open-ended agentic work.
             │
             └── Process    definition + instance + states + transitions + approvals
                            ⟵ DURABLE. Known, finite, auditable governance.

Artifact   content-addressed, typed by an extensible kind registry
Claim      scoped assertion with non-empty invalidation conditions
Event      immutable record of all of the above
```

### 4.2 Recording and mediation are different properties

The previous drafts conflated these and produced a contradiction that would have been discovered in code. They are independent:

- **Recording is universal.** Every effect, of every sink class, lands in the ledger. Attribution depends on completeness — a `pure` transform omitted from the record is a hole in the causal chain that no later analysis can fill.
- **Mediation is scoped.** Only `privileged` sinks require a grant and traverse the kernel. Routing a digest computation through the capability broker inflates the TCB, blows the latency budget, and buys nothing, because a pure function cannot escalate.

`sinkClass` is a **field on the descriptor** (T1.4), not a convention. That makes the distinction testable — a must-fail test can plant a `privileged` effect declared as `pure` and confirm the kernel rejects it.

### 4.3 Why the recursion matters, and where it stops

An agent is an Episode. A team is an Episode that spawns Episodes. A department is an Episode that spawns Episodes that spawn Episodes. **One type, one budget algebra, one attenuation rule, one event stream — at every level of coordination.**

**A tool is not an Episode.** A tool executes a typed effect and coordinates nothing. Calling it an Episode inflates the coordination unit until the word means nothing, and destroys exactly the attribution the recursion exists to provide: if everything is an Episode, "which Episode caused this?" has no useful answer. If something that looks like a tool genuinely needs child coordination, it was never a tool — it was an operator, and operators are already Episodes (T4.10).

The atom/molecule/polymer/cell/organism vocabulary is therefore **not a class hierarchy**. It is a set of names the trace viewer applies to observed *coordination* depths after a run. Build the classes and you have hand-authored the hierarchy you claimed would emerge; build one recursive coordinator and the hierarchy becomes a finding in the ledger. Nature did not implement `class Cell`; it implemented a replicator under selection and let scale happen.

### 4.4 Why the process is separate, and not a compromise

Episode recursion is the right control flow for work whose shape is unknown before it runs. It is the **wrong** control flow for a release approval:

- **The states are known in advance.** A finite declared state set can be read; a loop's reachable states cannot.
- **A non-engineer must audit it.** A compliance path is read by a regulator, a security reviewer, an operator. Conditionals scattered through a loop are not readable in that sense — a workflow hidden inside conditionals is *harder* to inspect than a small declared graph, not easier.
- **It must survive restart without replaying reasoning.** Resuming an episode means resuming a model. Resuming a process means reading state from the ledger. Different cost, different risk.

> **The test:** *if you can enumerate the states in advance and someone outside engineering would want to read them, it is a process.* Otherwise it is an episode. Both authorise through the same kernel and write to the same ledger — that is what keeps this from becoming two systems with two audit trails.

## Chapter 5 · Core structures

### 5.1 `domain/` — pure, no I/O, no dependencies

```
Digest, Timestamp, EpisodeId, RunId, BranchId, ProcessId,
ArtifactId, ClaimId, GrantId, PrincipalId, EvaluatorId      // opaque, parsed not cast

SinkClass          = pure | observation | privileged
ResourceSelector   { kind, pattern }        + includes(a,b): total, denies unknown pairs
EffectDescriptor   { verb, sinkClass, selector, args, argsDigest, idempotencyKey,
                     riskTier, provenance }
CapabilityGrant    { grantId, principal, descriptorDigest, selector, constraints,
                     expiry, parent, maxUses }
Receipt            { grantId?, outcome: ok|failed|undeterminable, observedAt,
                     resultDigest }          // grantId absent for non-privileged
BudgetVector       { tokens, wallClock, cost, effects, evaluations, depth }
Lease              { leaseId, parent, remaining: BudgetVector, expiry }
EventEnvelope      { seq, at, kind, episodeId?, processId?, causationId, correlationId,
                     payload, provenance, dataPolicy, tenant }
Artifact           { artifactId, kind, class, compensatesFor?, hypothesis,
                     evidenceRefs, invalidationConditions[], riskDelta }
Claim              { subject, predicate, value, protocol, evaluator, environmentProfile,
                     substrateProfile, uncertainty, validity, invalidationConditions[] }
CorrectionRecord   { episodeId, proposedPatchDigest, acceptedPatchDigest,
                     reasonCodes[], magnitude, scope }
Recording          { modelCassetteDigest, imageDigest, envSnapshotDigest, seed, clockPolicy }

ProcessDefinition  { definitionDigest, states[], transitions[], approvalPoints[],
                     boundEffectVerbs[] }     // an Artifact of kind `process_definition`
ProcessInstance    { processId, definitionDigest, currentState, pendingApprovals[],
                     history[] }              // resumable from the ledger alone

EpisodeState
reduce(State, Event) -> State                 // reduces BOTH episodes and processes
```

> `reduce` is shared. Episodes and processes are different control flows over the **same** event stream and the **same** effect primitive — that is what stops them becoming two systems with two audit trails.

### 5.2 `ports/` — interfaces only, two implementations each

```
ModelPort        propose(ContextBundle, ToolSchemas, Sampling) -> Proposal
EnvironmentPort  observe(Selector) -> Observation      // snapshot-bound, never a live handle
                 effect(Grant?, Descriptor) -> Receipt // Grant required iff privileged
EvaluatorPort    evaluate(RunRef, Protocol) -> Verdict | Inconclusive
EventStorePort   append(Event[]) / read(range) / digest()
BlobStorePort    put(bytes) -> Digest / get(Digest)
IndexPort        query(Query) -> RankedRefs
ClockPort        now()          // determinism seam — never call the system clock directly
RandomPort       next()         // determinism seam
```

> No `ProcessPort` and no `ToolPort`. A process advances by reading events and emitting effects; a tool *is* an effect. Neither needs a new port — the strongest available evidence that both belong on the same primitive rather than beside it.
>
> Every port has a **fake** and a **real** implementation from day one: simultaneously the contract test and the entire fast test suite.

### 5.3 `kernel/` — small, boring, auditable

`grants` · `attenuation` · `policy` · `budget` · `dispatch` · `provenance`. Nothing else. Tracked LOC budget with an alarm; an ADR per change. **Only `privileged` effects reach it. Both episodes and processes authorise through it; there is no second dispatch path.**

### 5.4 `agency/` and `governance/`

| Package | Holds | Explicitly does not hold |
|---|---|---|
| `agency/` | `episode` (recursive coordinator) · `context` (layered compiler) · `operators` · `playbooks` | Declared state machines. Approval logic. Release logic |
| `governance/` | `process` (definition loader, instance advancer, approval blocking, restart resume) | Any model call. Any open-ended control flow |

**No cognitive vocabulary as identifiers in `agency/`** — planning, debugging and reflection live in the artifact graph as data. **No model dependency in `governance/`** — a compliance path that calls an LLM is not a compliance path. Both are architecture tests (T10.4), not conventions.

### 5.5 Isolation topology

| Trust domain | MVP | Enforced by | Holds |
|---|---|---|---|
| Interaction · Cognition · Control · Governance | One process | Module boundary + architecture test | Episode state, process state, operator selection, grant issuance |
| **Workload** | **Separate process, identity, namespace** | OS | Sandboxed adapters. Real containment reporting |
| **Evidence** | **Separate process, identity, image digest** | OS | Evaluators. Owns the evaluation trigger |
| Evolution | **No runtime component** | Human action | Promotion is out-of-band |

An unstated gap between a diagram and a deployment is how "we have separation" becomes true in documentation and false in production. Workload and Evidence get real separation from day one because those are the two boundaries an attacker actually stands on.

## Chapter 6 · Where every capability lives

The falsification test for the abstraction: **anything fitting none of these columns means the spine is wrong.**

| Capability | Adapter behind a port | Artifact in the graph | Policy parameter |
|---|---|---|---|
| Tools, scripting, files | Environment adapter | Tool schema + description | Risk tier, sink class |
| Browsing, research, sensors | Environment adapter | Retrieval policy | Egress scope |
| LLMs (primary + auxiliary) | Model port, n providers | Routing policy | Budget vector |
| Short/long-term knowledge | Store adapter (4 stores) | Write + consolidation policy | Retention |
| Indexing, search, cache, compression | Index adapter | Context compiler | Token budget |
| Context | — | Context compiler (versioned, evaluated) | Layer budgets |
| Cognition, planning, decomposition | — | Operators | Activation set |
| Reflection | — | Operator emitting a **candidate Claim** | Rigidity |
| Methodologies, workflows | — | Playbooks (agentic) · **Process definitions (governance)** | Selection policy |
| Approvals, releases, compliance | — | **Process definition** | Approval points |
| Skills | — | Artifact | Scope |
| Harness engineering | — | *Editing the artifact graph* | Tier 1/2/3 |
| Loop engineering | — | *Editing episode-policy artifacts* | — |
| Learning | Offline optimiser reading the ledger | Emits candidate Artifacts | Promotion gate |
| Evaluating, judging | **Evaluator — outside, unreachable** | Emits Claims | Sealed set |
| Integrations, comms (MCP/ACP/HTTP) | Protocol adapter | Tool schemas | Trust level |

Not one requires a new architectural layer. **That is the decoupling answer:** you do not leave room by adding extension points; you leave room by having a reduction general enough that new capability arrives as an adapter, an artifact, or a number.

## Chapter 7 · Harness manifests — how the framework builds CLIs

A harness is a **manifest**, not a codebase.

### 7.1 The default — typed tools

```yaml
harness: vg-code-default
components:
  system_prompt:    sha256:…
  tools:            [read@1, search@1, patch@1, test@1]   # typed, selector-scoped
  fallback_tools:   [shell@1]                              # allowlist only, elevated tier
  context_policy:   layered-l1l5@1
  routing:          single-model@1
  budget:           interactive-default@1
capabilities:
  - verb: fs.read     sink: observation  selector: {kind: glob, pattern: "${repo}/**"}
    risk: low
  - verb: fs.patch    sink: privileged   selector: {kind: glob, pattern: "${repo}/**"}
    risk: medium
  - verb: proc.test   sink: privileged   selector: {kind: command, allow: [pytest, go, cargo]}
    risk: medium
  - verb: proc.exec   sink: privileged   selector: {kind: command, allow: [git]}
    risk: high          # shell fallback — never weaker than what it replaces
evaluators: [coding-oracle@3]
```

### 7.2 The permanent baseline

```yaml
harness: vg-shell-only          # NEVER DELETED. The instrument's floor.
components:
  system_prompt:    sha256:…    # minimal
  tools:            [shell@1]
  context_policy:   recency-window@1
  routing:          single-model@1
capabilities:
  - verb: proc.exec   sink: privileged   selector: {kind: command, allow: [git, pytest, ruff]}
    risk: high
evaluators: [coding-oracle@3]
```

Every claim that a typed tool, skill or context policy improves outcomes is measured **against this manifest**, paired, under T8. Delete it and the instrument has no zero-assumption control condition.

### 7.3 The reconstruction suite

`vg harness build | run | diff | bench`.

Express a Claude-Code-shaped, an OpenCode-shaped and a minimal-SWE-agent-shaped harness as manifests; `vg harness bench` runs them paired on the same tasks under the same evaluator. Two rules keep it honest:

1. If any reconstruction requires a core change, the configurability claim is falsified — **a finding, and a cheap one.**
2. A comparison against a faithful reimplementation is a comparison against *that reimplementation*, and must be labelled as such. This separates the exercise from marketing.

What no competitor offers: **a harness that ships with its own evidence ledger** — which components are active, what promoted them, what would demote them, what it costs per verified change.

## Chapter 8 · Test doctrine

Six families. Coverage is satisfied by any of them, not by must-fail tests alone — demanding must-fail coverage for every rule produces ceremonial tests.

| Family | Proves | Example |
|---|---|---|
| **Must-fail** | The control can fail | Verb-only attenuation reads the evaluator bundle; a `privileged` effect declared `pure` is accepted |
| **Architecture** | A path does **not** exist | Nothing imports `spike/` or `slice/`; no route from `agency` to `adapters/evaluators`; `governance/` has no model dependency; `agency/` has no approval logic |
| **Property** | An algebraic law holds | Attenuation monotone; budget conserved; selector inclusion transitive; process resumes to the same state |
| **Conformance** | Two implementations agree | Golden canonicalisation triples across both readers |
| **Fault injection** | Every failure path recovers | Crash at each dispatch stage |
| **Adversarial** | The threat model is real | Injection, escalation, exfiltration, memory poisoning, descriptor substitution |

Plus two statistical families that are not unit tests: **A/A** (noise floor) and **paired comparison** (effect estimation).

## Chapter 9 · Margins — carried and alarmed, naval-style

| Margin | Alarm at | Why |
|---|---|---|
| TCB size | Budget exceeded | Logic belonging in cognition has leaked into the kernel |
| p95 time-to-first-token | Budget exceeded | The product becomes unpleasant and dogfood collapses |
| p95 time-to-first-effect | Budget exceeded | Governance has reached the interactive path |
| Context tokens per turn | Budget exceeded | The compiler is padding |
| Schema extension slack | Below threshold | The next contract change becomes a migration |
| **Active MVP Contract coverage** | **Below 100% (test or justification)** | **Blocks all new normative rules** — Ch. 15 |
| Substrate debt | Above threshold | The activation set has become a set of assumptions |
| Verifier–deployment gap | Widening | **Freezes automated promotions** |

A margin with a hard limit gets gamed. A margin with an alarm gets discussed. Carry them the way you carry weight, KG and power margin.

## Chapter 10 · The MVP gate — four questions

Done when all four are answered, and no earlier. Tickets merged, CI green, and a demo that worked once do **not** close it.

1. **Is the boundary real?** Red team reaches neither control plane, evaluator, nor secrets. Every must-fail test fails against its broken counterpart. Kill and restart preserve the distinction between known and uncertain. `spike/` and `slice/` are gone.
2. **Is it useful?** Three real bugs in a repository someone knows well, fixed interactively without hand-patching mid-run. Then, honestly: *next time, would you reach for it?* If no, the loop is not done, and no amount of later work fixes that.
3. **Is it measurable?** An A/A floor exists per task class, computed against `vg-shell-only`. A paired comparison runs. The verifier–deployment gap has a number.
4. **Is it general?** The non-coding environment was added with zero episode-engine changes.

## Chapter 11 · How the MVP grows itself

Four stages. Emergence enters at stage 4, not stage 1.

1. **The ledger accumulates.** Episodes, processes, effects of every sink class, receipts, verdicts, correction deltas. No learning. You are building the corpus, and the corpus is the asset. This is why the schema is the keel — everything downstream reads it.
2. **The corpus becomes attributable.** With the artifact graph populated *from S2* and counterfactual re-execution working, *which component caused this* becomes answerable. Attribution turns a log into evidence.
3. **Attribution becomes proposal.** The offline optimiser clusters failure modes and proposes Tier-1 edits (prompts, skills, retrieval, context, routing), each with a **declared prediction**. Predictions verified against next-round outcomes give the progressive-vs-degenerating ratio — a real measure of whether the loop is learning or merely accommodating.
4. **Proposal becomes structure.** Plateau is the observable form of *"my representation is inadequate."* At plateau the system proposes a representation it was not given. That is the only genuinely interesting question in the programme, and everything before it exists to make it askable.

The coordination hierarchy — agents → teams → departments — is **discovered**, not built: whatever depth survives evaluation on task classes that need it. If depth-3 never beats depth-1 on any task class, that is a real and expensive finding about the thesis, learned from the ledger rather than from an argument.

## Chapter 12 · How the other sciences are used

Imported as **mechanism with a falsifiable prediction**, never as module names. The test: *does the import predict something about our system's behaviour that could turn out false?*

| Discipline | Legitimate import | Illegitimate import |
|---|---|---|
| Capability security / OS | Least privilege, attenuation, unforgeable tokens, namespace isolation | "The kernel is a brainstem" |
| Philosophy of science | Falsifiability as a required schema field; Lakatos hard-core/protective-belt as the mutability partition; progressive-vs-degenerating as a measured ratio | "Science is a search process, and so are we" |
| Statistics / replication crisis | Pre-registration, pairing, family correction, MDE, A/A floors | "As rigorous as a clinical trial" |
| Cognitive neuroscience (CLS) | Fast episodic store / slow consolidated store; offline interleaved replay; forgetting as competition | "The event store is a hippocampus" |
| Metacognition | Competence estimate recorded pre-action, scored post; Brier score as an alertable metric | "The system knows itself" |
| Evolutionary computation | Pareto/QD archives; the failure of scalar fitness; diversity as insurance | "Evolution guarantees progress" |
| Control theory | Estimated state, bounded actions, stop rules, rate limits, rollback | "More feedback is always more stable" |
| Economics | EV-gated exploration; cost per verified change; two-clock queueing | "Maximum compute is maximum rationality" |

## Chapter 13 · The simple version — for everyone on the team

Read only this if you are not writing code.

**What we are building.** A machine that does work for you, and — the unusual part — **keeps an honest record of whether it actually helped.** Most AI tools cannot tell you that. Ours is designed so it cannot avoid telling you.

**Three ideas, and that is genuinely all of them.**

1. **The worker and the judge are different people.** The part that does the work is never allowed to touch the part that grades the work. Not "discouraged" — *unable to*, at the operating-system level. Every system that has ever fooled itself did so because it could reach its own scoreboard.

2. **The worker asks permission for anything that changes the real world**, and permission is specific: not "you may write files" but "you may write *this* file, *once*, *until 4pm*." A general permission is how a small mistake becomes a large one. Harmless things — reading something it was already allowed to read, doing arithmetic — don't need a permission slip, but they are still written down, because we want the complete story of what happened, not just the dangerous parts.

3. **Everything that happens is written down, permanently, and cannot be edited afterwards.** That record is the actual product. The code we ship this year will be replaced. The record will not.

**Two kinds of process, kept deliberately apart.** When the machine is *figuring something out*, we let it wander — we cannot predict the steps, so we do not pretend to. When the machine is *asking approval to release something*, we do the opposite: the stages are written down in advance as a list anyone can read, including people who do not write code. If you ever audit what happened before a release, you will read that list, not the code.

**How it gets better.** Not by thinking about itself. By doing thousands of tasks, having them graded by something it cannot influence, noticing patterns in the failures, proposing a small change, and **only keeping the change if it wins a fair test against the current version.** If it cannot prove the change helped, the change is thrown away. Slower than it sounds, and far more honest.

**Why we start with programming.** Code is the only kind of work where grading is fast, cheap and merciless. Tests either pass or they do not. We are not building a coding tool because coding is the goal; we are building it because it is the only place we can afford to be wrong ten thousand times while learning how to grade.

**Why we will throw code away on purpose.** Twice in the first four sprints we will build something quick, learn from it, and delete it — not refactor it, delete it. That is deliberate. Fast throwaway code teaches us where the design is wrong while it is still cheap to change. Code that survives because someone got attached to it is how a prototype quietly becomes the architecture.

**What "done" looks like this year.** Somebody on this team fixes a real bug with it, and then genuinely wants to use it again tomorrow. That is the whole bar. Everything else is in service of it.

**What we are not claiming.** We are not building AGI. We are building the best instrument anyone has for finding out whether machine competence accumulates. If it turns out not to, that is a real answer and we will publish it — a negative result from a good instrument is worth more than a positive result from a bad one.

## Chapter 14 · Standing risks

| Risk | Early signal | Standing mitigation |
|---|---|---|
| Specification capture | New normative rules outpace tests | **100% Active MVP Contract coverage gate** (Ch. 15) |
| Nobody dogfoods | No real bug attempted by mid-S6 | PM owns scheduling; opt-out reasons logged and reviewed |
| Latency collapse | p95 alarms | Two-clock split; governance off the serving path; `slice-findings.md` seeds real budgets |
| TCB growth | LOC alarm | ADR per kernel change; only `privileged` sinks reach the kernel |
| **Disposable becomes architecture** | Anyone argues to keep `spike/` or `slice/` | **Deletion is a checked gate item; both unimportable by CI rule. The argument to keep it is the signal to delete it faster** |
| Reward hacking | Seeded sabotage passes | External evaluator, mutation oracles, sealed gate, canary |
| Statistical noise as signal | Archive fills with sampling artifacts | A/A floor against `vg-shell-only`, MDE, pairing, sequential rules |
| Baseline manifest deleted as "dead code" | `vg-shell-only` proposed for removal | Flagged undeletable; L-15 |
| Ontology rigidity | A new capability needs a new layer | Ch. 6 table is the test — if it fits nowhere, the spine is wrong |
| Process/episode confusion | Approval logic appears in `agency/` | Architecture tests: `governance/` has no model dependency; `agency/` has no approval logic |
| **Mediation drift** | A `privileged` effect declared `pure` | Must-fail test; `sinkClass` is schema data, not convention |
| Contract inflation | Management tasks appearing as contract rows | Ch. 15.2 exclusion rules; 100% becomes unachievable the moment scope leaks |
| Conway drift | Team boundaries diverge from module boundaries | Staff to the architecture; review at each gate |
| A special case appears | A conditional names one provider or environment | Review item T10.9; it always arrives disguised as pragmatism |

## Chapter 15 · The Active MVP Contract

**This is the artifact T10.7 and Ch. 9 gate on.** Not this document, not the ICD, not the backlog. A single machine-readable table that CI parses.

### 15.1 Shape

| Column | Meaning |
|---|---|
| `req_id` | Stable identifier, e.g. `REQ-KRN-014` |
| `statement` | One sentence, testable as written. If you cannot write the test from the sentence, the sentence is wrong |
| `source` | Which Part I task and which v4 rule it derives from |
| `component` | The package that implements it |
| `owner` | A person, not a team |
| `test` | Test identifier, or `untestable-with-justification:<reason>` |
| `test_family` | One of the six in Ch. 8 |
| `acceptance_evidence` | What a reviewer looks at to agree it passed |
| `status` | `open` · `covered` · `justified` |

### 15.2 What enters, and what does not

**This is the rule that makes 100% coverage achievable rather than theatrical.**

| Enters the contract | Stays in the issue tracker |
|---|---|
| **Product requirements** — observable behaviour of the shipped system | **Management tasks** — write a document, run a review, tag a baseline |
| **Assurance requirements** — a boundary, an invariant, a failure mode, a recorded property | **Research tasks** — schema archaeology, spikes, exploratory measurement |
| Anything a PR could regress | Anything with no code artifact to regress |
| Series tagged **[C]** in Part I | Series tagged **[B]** in Part I |

Concretely: *"a grant with no descriptor digest fails at parse"* is a contract row. *"time each manual fix"* is a ticket. *"the Decision Record exists"* is a ticket. **A task with no testable statement is not a contract defect — it is simply not a contract item.** Forcing it in is how a 100% target becomes ceremony, and ceremony is what the gate exists to prevent.

Rows for deferred capability (Ch. 3) never enter. They arrive when their trigger fires.

### 15.3 Rules

1. **Every PR cites at least one `req_id`.** A PR citing none is rejected by CI, not by a reviewer.
2. **A row is `covered` only when its named test exists and passes.** Marking `covered` without a test is the failure this artifact exists to prevent.
3. **`justified` requires a written reason and a compensating assurance**, using the three classes from v4 `08 §5.1`: architectural prohibitions (proved statically), statistical rules (hold over a family, not one run), human-gated rules (proved by showing no autonomous path exists).
4. **Coverage is generated into a report each CI run.** That report is the burndown Scrum tracks.
5. **The merge rule.** Local spikes and branches may start the day the Decision Record is approved. **No PR merges to main until this contract exists and the baseline is tagged.** The gate applies at the merge, not at the keyboard.

### 15.4 Seeding

Seed in S0 from the **[C]** series of Part I. Each becomes one or more rows. A **[C]** item that cannot be phrased as a testable statement is a defect in Part I — fix the task, not the table. A **[B]** item becomes a ticket and nothing else.

---

*This document owns the plan and the reasoning. It states no contract, gates no merge, and locks no decision. It is meant to be argued with, and superseded when it is wrong.*
