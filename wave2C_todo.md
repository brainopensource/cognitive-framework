# Wave 2C — From ALFA Decision to an Implementable Tier S+ Foundation

## Director-gated work packet for evidence integrity, cold continuation, graph convergence, and the path to VAOH

**Document class:** proposed execution briefing; source for the next board update, not a second board  
**Status:** **PROPOSED — NOT AUTHORIZED UNTIL THE ENGINEERING DIRECTOR ADJUDICATES THE ALFA DECISION**  
**Prepared:** 2026-08-21  
**As-built snapshot:** Git `a9f4747`; clean working tree at inspection  
**Selected decision:** [`001_alfa_review_full_decision.md`](001_alfa_review_full_decision.md)  
**Architectural baseline:** [`006_fi_review_full_gptsol_proposal.md`](006_fi_review_full_gptsol_proposal.md)  
**Controlling law:** [`docs/SPEC.md`](docs/SPEC.md), accepted [`ADRs 0069–0076`](docs/05_adr/INDEX.md), and [`docs/04_annex/`](docs/04_annex/)  
**Current execution authority:** [`docs/03_sprints/sprint_active.md`](docs/03_sprints/sprint_active.md)

> This document tells the Director, Tech Lead, and developers exactly how to turn the selected proposal into law, red tests, implementation, and evidence. It does not itself accept ADRs, reopen M-2, start M-3, or authorize post-M-4 work. When this packet conflicts with accepted law or the active board, law and the board win until they are deliberately amended.

---

## 0. The next action, in plain language

**Do not start by adding more agent features.** First have the Director ratify the ALFA disposition and the six-ADR map; widen the documentation-link gate; put the new requirements onto the one active board; write the trajectory and cold-continuation falsifiers red; then repair the evidence path and prove true fresh-process continuation. Only after that re-gate M-2 and open M-3 for the Named Component Graph, plugin lifecycle, and final `layer0/` deletion.

The shortest safe route is:

```text
Director decision
    -> accepted ADRs + minimal SPEC/board delta
    -> RF-23/RF-24/RF-25/RF-27 RED
    -> NOVA-1 and NOVA-2 GREEN
    -> M-2 re-gate
    -> manifest/2 + lifecycle parity + NOVA-4
    -> M-3 re-gate
    -> one nine-row real M-4 run
    -> Pack #2 generality proof
    -> spawn -> controlled swarms -> builder/CLI -> memory/macros -> learning
```

This order is the product strategy. A sophisticated router over hollow costs, a swarm without cold reconstruction, or a memory flywheel without attributable evidence would compound errors faster rather than create a moat.

---

## 1. What is true on disk now

The following facts were rechecked against the live tree; they define the starting point and must not be replaced by proposal-era assumptions.

| Surface | Verified current state | Consequence |
|---|---|---|
| Wave authority | Wave 2 is submitted for Tech Lead re-gate round 4; Wave 3 remains queued. | Do not silently reopen or close M-2. Add Wave 2C only through a Director/board decision. |
| Kernel | `check_tcb_budget.py` reports **1365/1438** logical LOC. Boundary check covers 248 source files. | There are 73 LOC of budget headroom, not a development allowance. NOVA-1/2 and the graph belong outside `kernel/`. |
| Event coverage | The current 56-kind catalog, privileged-owner subset, reducer folds, and allowlist tests are green. | Keep the M-2 fold repairs. Do not rewrite the taxonomy merely to make a new count. |
| Trajectory schema | [`schemas/mhf/trajectory.schema.json`](schemas/mhf/trajectory.schema.json) is `mhf.trajectory/1`; most identity fields remain optional and costs are required integer fields. | Strengthen `/1` content and missingness rules without a breaking `/2` identifier before M-4. |
| Trajectory writer | [`runtime/trajectory.py`](vanguard/packages/runtime/trajectory.py) assigns `_ZERO_COST` to every turn and episode and emits no `execution_digest` or model route. | F-12 is structurally green but economically hollow. NOVA-1 is the first critical repair. |
| Existing trajectory tests | F-12 and `TrajectoryEmission` validate required-key presence, including a zero-turn aborted row; both pass. | Preserve the aborted-row requirement, but add separate invoked-turn content falsifiers. Do not mutate a useful aborted-case test into an unrelated test. |
| Telemetry | [`RunTelemetry`](vanguard/packages/runtime/telemetry.py) correctly preserves `None` for absent token/cost values, while provider usage is carried in proposal/context-adjacent data. | Join existing measurements into the trajectory; do not invent a second accounting subsystem or turn `None` into zero. |
| Replay | Cold WAL reduction and state-digest parity exist. [`test_resume_from_ledger.py`](test/runtime/test_resume_from_ledger.py) proves reconstruction semantics, mostly with an in-memory store. | NOVA-2 must add a real SQLite file, a new interpreter, and continued execution without duplicate effects. Reduction parity alone is not continuation. |
| Manifest domain type | [`domain/artifacts/manifest.py`](vanguard/packages/domain/artifacts/manifest.py) stores `components` as role-to-path tuples and resolves file digests. | This is a named path bag, not a component graph; it has nodes but no typed bindings or edges. |
| Manifest consumers | [`agency/manifests/loader.py`](vanguard/packages/agency/manifests/loader.py) has `REGISTERED_COMPONENT_CONSUMERS`; [`runtime/compose.py`](vanguard/packages/runtime/compose.py) has `ROLE_KIND`. | `mhf.manifest/2` must converge all three composition surfaces, not just change YAML keys. |
| Plugin lifecycle | The retained [`layer0/registry/lifecycle.py`](layer0/registry/lifecycle.py) has seven states but emits only five destination events. `DISCOVERED` and `VERIFIED` are silent. | M-3 cannot claim “every transition ledgered” until `PluginDiscovered` and `PluginVerified` are catalogued, owner-scoped, emitted, reduced, and tested. |
| Layer-0 | `layer0/registry/`, `layer0/compose/`, and supporting `layer0/events/` remain intentionally for M-3. [`pyproject.toml`](pyproject.toml) still packages `layer0*`; CI still runs the residual Layer-0 suite. | Delete these only after their packages-path twin passes. Deletion, packaging removal, CI removal, and NOVA-4 must be atomic. |
| Documentation gate | [`check_markdown_links.py`](tools/linters/check_markdown_links.py) defaults to only three narrow globs. The active board still links to the old `plans/` location while plans now live under `done/` and `doing/`. | Widen the linter before relying on “LINK PASS”; fix living links without rewriting historical ADR evidence. |

### Verification executed for this packet

The following passed at the snapshot above:

- 16 focused tests covering F-12, trajectory emission, event catalog/fold parity, and plugin reducer state;
- TCB budget: 1365 logical LOC of 1438;
- hexagonal boundary checker;
- event-coverage checker;
- duplication checker.

These green results do **not** falsify the hollow-trajectory or true-continuation gaps because no current test asks those questions.

---

## 2. Authority and documentation sequence

### 2.1 One authority chain—no new documentation tier

The selected source order is:

1. accepted SPEC, annexes, and ADRs;
2. the active sprint board and milestone ladder;
3. the Director-ratified ALFA decision;
4. the 006 Tier S+ baseline;
5. other proposal reports as provenance and suggestion material only.

[`001_alfa_review_full_decision.md`](001_alfa_review_full_decision.md) chooses the architecture but is explicitly not law. [`006_fi_review_full_gptsol_proposal.md`](006_fi_review_full_gptsol_proposal.md) supplies the full mechanisms, equations, schemas, and falsifier ideas but is also not law. Developers must not cite either as implementation authority after ADRs are filed; tickets cite an accepted ADR, SPEC requirement, schema, and named falsifier.

Do **not** create a new SPEC, contracts manual, kernel manual, second backlog, or parallel roadmap. If the Director requests a publication-grade ALFA master, create it after ADR adjudication as a navigational synthesis linking accepted decisions—not as a fourth authority layer.

### 2.2 Director checkpoint D-ALFA-1

Before any Wave 2C production change, the Engineering Director must record one disposition for each item below. The final accepted numbering must be unique. This packet follows the six-ADR map selected in `001`; do not file eight conflicting ADRs unless the Director explicitly chooses to split subjects and publishes the replacement map first.

| Draft | Decision | Immediate implementation horizon | Required bound falsifier |
|---|---|---|---|
| **ADR-0077** | Named Component Graph and `mhf.manifest/2`. | Contract at M-3, never in Wave 2C production. | Six graph fixtures compile with stable `D_H`; unknown/unconsumed binding is rejected. |
| **ADR-0078** | Required / declared-absent / forged guardrail trichotomy. | Content rules may land with NOVA-1; pack enforcement at M-3/M-5. | Required-without-valid-exterior-evidence fails; declared absence is frozen before execution; forged never degrades to absence. |
| **ADR-0079** | Plugin lifecycle parity, composition absorption, and Layer-0 retirement. | M-3. | Seven-state lifecycle is fully evented/reduced; NOVA-4 proves no Layer-0 surface remains. |
| **ADR-0080** | Universal turn mechanism; typed obligations; deferred capability-mediated delegation. | Mechanism claim now; spawn only M-6; obligation claims only M-7. | A topology may change without an engine branch; ungranted spawn is denied through S0–S12. |
| **ADR-0081** | Evidence-complete trajectory and true cold continuation. | **Wave 2C / M-2 correction.** | Rich `/1` trajectory survives a fresh-process resume with no repeated effect and exact lineage. |
| **ADR-0082** | Pareto policy, T0–T3 compounding, and promotion protocol. | Design now; T0 M-5; routing M-7; statistical promotion M-10. | No candidate promotes unless safety-feasible, exterior-signed, paired, exact-test green, and human-approved. |

Each accepted ADR must be concise and contain: context, decision, scope/milestone, invariants narrowed or extended, owner boundary, one primary falsifier, negative cases, reversal condition, and links to the selected baseline. The proposal's long-form explanations remain in 006; do not copy 2,000 lines into the ADR register.

### 2.3 Documentation cascade—exact order

Perform this cascade as its own governance PR before production implementation:

1. **W2C-H1 — Widen link truth first.** Update [`tools/linters/check_markdown_links.py`](tools/linters/check_markdown_links.py) so default CI checks living root briefings, `docs/**/*.md`, schema/package READMEs, and sprint documents. Preserve explicit archive exclusions. Add a planted broken-link fixture test. Run `--all` once and adjudicate existing failures rather than hiding them with new exclusions.
2. **W2C-A1 — File accepted ADRs.** Add only the Director-approved 0077–0082 mapping under [`docs/05_adr/`](docs/05_adr/) and update [`INDEX.md`](docs/05_adr/INDEX.md). If any item is rejected or deferred, record that disposition; do not silently edit the proposal into apparent consensus.
3. **W2C-A2 — Apply the minimal immediate SPEC delta.** Update only the sections required for authorized Wave 2C behavior:
   - §1.3: true cold continuation is reconstruction **and legal continuation** from durable SQLite WAL in a fresh process;
   - §7: `mhf.trajectory/1` populated content, explicit missingness, `D_H/D_R/D_X`, per-turn identity/cost, conservation, and derived legacy exclusion;
   - §8.2/§8.3: NOVA-1/NOVA-2 as M-2 corrections and the exact M-4 row-8 wording;
   - I-9: a schema-valid but hollow row fails the invariant;
   - I-11: sequential execution remains until the M-7 measurement decision.
4. **W2C-A3 — Defer non-existent behavior in SPEC.** Do not norm the full Named Component Graph into §2.3 until ADR-0077 is accepted and M-3 opens. Do not norm VFE/EFE routing, macros, DPO, or swarm claims as shipped behavior; keep them explicitly phased in §5–§7. Law must distinguish current MUSTs from future blueprint.
5. **W2C-A4 — Normalize the falsifier register.** In [`002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md), reserve one `RF-*` sequence or an explicit F→RF alias map. Preserve historical `F-*` meanings. Add a linter under `tools/linters/` and a planted duplicate-ID test under `test/tools/`.
6. **W2C-A5 — Update the one board.** Add Wave 2C tickets, owners, entry/exit gates, and Director dependencies to [`sprint_active.md`](docs/03_sprints/sprint_active.md). Correct plan links to [`done/wave2_convergence.md`](docs/03_sprints/done/wave2_convergence.md), [`doing/wave3_extensibility.md`](docs/03_sprints/doing/wave3_extensibility.md), and [`doing/wave4_foundation_e2e.md`](docs/03_sprints/doing/wave4_foundation_e2e.md). Do not create a second live backlog.
7. **W2C-A6 — Update the milestone ladder only at outcome level.** In [`milestones.md`](docs/02_roadmap/milestones.md), name NOVA-1/NOVA-2 as M-2 evidence gates, strengthen M-4 row 8, name Pack #2 precisely, and retain M-5–M-10 as outcomes—not detailed speculative tickets.
8. **W2C-A7 — Update README/AGENTS last.** Change navigation/status only after the board and files actually move. Do not announce `layer0/` deletion, manifest/2, or a green milestone before the matching falsifier passes.

No production implementation starts until steps 1–6 are merged or the Director explicitly authorizes an inseparable red-test PR with them.

---

## 3. Wave 2C sprint plan

Wave 2C is a narrow correction lane between the current M-2 re-gate submission and M-3 entry. It does not reimplement completed convergence work.

### 3.1 Entry and exit

**Entry:**

- Director checkpoint D-ALFA-1 recorded;
- ADR-0081 accepted with the non-breaking `mhf.trajectory/1` amendment;
- RF identifiers reserved;
- active board explicitly authorizes Wave 2C;
- current M-2 fold, writer, boundary, TCB, and duplication gates remain green.

**Exit:**

- invoked turns have attributable model identity and non-forged measurements;
- episode accounting conserves each available additive dimension;
- `D_R` and `D_X` are computed under accepted ADR-0071 semantics and never substituted for `D_H`;
- historical/hollow rows are derived as ineligible without rewriting WAL history;
- a real SQLite WAL run suspends, loses all process memory, resumes in a fresh interpreter, and completes without repeating or skipping a settled effect;
- RF-23, RF-24, RF-25, RF-27 and all existing M-2 gates are green;
- Tech Lead signs the M-2 re-gate; only then may M-3 start.

### 3.2 Sprint 2C.0 — Decisions, hygiene, and red tests (2–3 working days)

| ID | Owner | Work | Files | Exit |
|---|---|---|---|---|
| **W2C-H1** | Tooling owner | Widen Markdown link coverage and add the broken-link fixture. | `tools/linters/check_markdown_links.py`, `test/tools/` | Default link check detects a broken link in a living sprint doc. |
| **W2C-A1** | Director + Architect | File accepted ADRs and INDEX rows; apply the minimal SPEC delta. | `docs/05_adr/`, `docs/SPEC.md` | Every immediate requirement cites one accepted ADR and one future falsifier. |
| **W2C-A2** | Tech Lead | Add the Wave 2C lane and correct live plan links. | `docs/03_sprints/sprint_active.md`, `docs/02_roadmap/milestones.md` | One board names owners, dependencies, and stop lines. |
| **W2C-A3** | Tooling owner | Reserve/lint RF identifiers; preserve existing F aliases. | gap register, new `tools/linters/check_falsifier_ids.py`, `test/tools/` | Duplicate or reused RF identifier fails CI. |
| **W2C-R23** | Developer A | Write invoked-turn population falsifier. | new `test/falsifiers/test_rf23_trajectory_content.py` | Red specifically because `_ZERO_COST`, route identity, and per-turn usage are missing. |
| **W2C-R24** | Developer A | Write accounting/missingness falsifier. | new `test/falsifiers/test_rf24_trajectory_accounting.py` | Red because totals do not derive from turns/non-turn charges and unknown is not represented. |
| **W2C-R27** | Developer A | Write execution/experiment digest falsifier. | new `test/falsifiers/test_rf27_execution_identity.py` | Red because the emitted row lacks `D_R`/`D_X`. |
| **W2C-R25** | Developer B | Write true cold-continuation falsifier. | new `test/runtime/test_cold_continuation.py`, subprocess helper fixture | Red because no new process can legally continue the episode from WAL alone. |

Production files are untouched in this sprint. A test that accidentally passes must be strengthened until it exercises the stated defect; do not weaken the requirement to manufacture red.

### 3.3 Exact red-test contracts

The names below are the handoff API between governance and code. The Director may renumber IDs but must not weaken the behavior.

```text
test.falsifiers.test_rf23_trajectory_content
  .TrajectoryContentIsPopulated
  .test_completed_invoked_turn_is_attributable_and_measured

test.falsifiers.test_rf24_trajectory_accounting
  .TrajectoryAccountingConserves
  .test_episode_cost_equals_turns_plus_declared_non_turn_charges

test.falsifiers.test_rf24_trajectory_accounting
  .TrajectoryAccountingConserves
  .test_unknown_dimension_is_unavailable_with_reason_not_zero

test.falsifiers.test_rf27_execution_identity
  .ExecutionIdentityIsSeparated
  .test_dh_dr_dx_are_computed_for_their_distinct_subjects

test.runtime.test_cold_continuation
  .ColdContinuationFromWal
  .test_fresh_interpreter_resumes_without_repeating_settled_effect
```

RF-23 drives a completed scripted episode with at least one real model invocation and proposal. It asserts:

- `len(turns)` equals the counted model/proposal turns and is greater than zero;
- each turn carries `provider`, `model`, and fingerprint or a typed unavailability reason;
- each turn carries prompt, completion, and cache-token status; charged milliseconds; bytes; and USD-micro status;
- at least one measured additive dimension is positive for an invoked turn;
- context digest, proposal, receipt/effect lineage, and terminal outcome are populated;
- a completed, invoked row cannot be `legacy_incomplete`.

RF-24 asserts per dimension:

```text
episode_total[d] = sum(turn[d]) + sum(non_turn_charge[d])
```

only when all operands for `d` are measured. If any operand is unavailable, the episode dimension is unavailable with a reason; it is not silently summed as zero. Estimated values are labelled estimated and never promoted as measured. Aborted zero-turn episodes remain legal but explicitly say `model_not_invoked` and are ineligible for learning/promotion.

RF-27 uses the already accepted identity trinity:

```text
D_H = complete frozen harness composition
D_R = H(D_H || runtime || environment || model identity || oracle identity)
D_X = H(D_R || dataset || protocol)
```

It changes one subject at a time and requires the appropriate digest to change while unrelated identities remain stable. Do not adopt a different `D_X` formula from a proposal without an ADR amendment.

RF-25 must use a file-backed SQLite store and a spawned Python interpreter. Process A runs to a deterministic suspension/checkpoint after a known settled effect and exits. Process B receives only stable identifiers and the SQLite path, reconstructs the same harness/run/lease/turn/effect state, reconciles any open intent, continues legally, and finishes. The test fails on duplicate effect, skipped effect, re-query of an already-approved action, broken hash lineage, changed state digest for the same prefix, reset turn budget, or transfer of any live Python object.

### 3.4 Sprint 2C.1 — NOVA-1 trajectory integrity (Developer A, 3–4 working days)

**Primary files:**

- [`schemas/mhf/trajectory.schema.json`](schemas/mhf/trajectory.schema.json)
- [`vanguard/packages/runtime/trajectory.py`](vanguard/packages/runtime/trajectory.py)
- [`vanguard/packages/runtime/session.py`](vanguard/packages/runtime/session.py)
- [`vanguard/packages/runtime/telemetry.py`](vanguard/packages/runtime/telemetry.py)
- model adapter/provider metadata only where the measurement is actually born
- generated types/vectors if the schema generator owns the changed shape

**Implementation contract:**

1. Keep `schema: "mhf.trajectory/1"`.
2. Replace `_ZERO_COST` assembly with a join over per-turn provider measurements, context metrics, receipts, sandbox durations/bytes, and settled budget events.
3. Extend `/1` additively so each cost dimension carries a value or explicit status/reason. Historical rows lacking the content are accepted by compatibility readers but derived as `legacy_incomplete` and never promotion-eligible.
4. Put model route identity on the turn that used it; top-level `model_routes_used` is a derived summary, not the sole attribution source.
5. Represent provider-reported, locally estimated, and unavailable measurements distinctly. Estimates may support routing experiments but cannot impersonate billed facts.
6. Compute `D_R` and `D_X` from canonical, versioned input objects. Persist the objects or their content-addressed refs so the digest can be recomputed.
7. Keep `D_H` unchanged: do not inject runtime/model/dataset facts into the frozen harness digest.
8. Bind the trajectory to its WAL event range and final state digest. The row is a view of ledgered truth, not a parallel source of authority.
9. Derive `legacy_incomplete`, `unattributable_for_promotion`, and promotion eligibility in trusted readers/composition code. Never accept those booleans from a manifest, plugin, model, or trajectory author.
10. Preserve null signed-verdict semantics for aborted or unevaluated episodes. A null verdict is not a passing verdict and not forged evidence.

**Do not:** widen `ModelPort` casually, leak provider-specific DTOs into `domain/`, backfill historical zeros, or count wall time as additive charged time under concurrency. If a port change is unavoidable, treat it as an explicit ADR-0072 contract amendment with fake/cassette/live conformance tests.

**Exit:** RF-23, RF-24, RF-27, existing F-12, schema vectors, cassette/fake adapters, and full trajectory emission tests are green.

### 3.5 Sprint 2C.2 — NOVA-2 true continuation (Developer B, parallel, 2–3 working days)

**Primary files:**

- new `test/runtime/test_cold_continuation.py`
- [`vanguard/packages/runtime/ledger/recovery.py`](vanguard/packages/runtime/ledger/recovery.py)
- runtime session/service entrypoint only if a narrow resume command is required
- existing SQLite event-store adapter and reducer; no second checkpoint database

**Implementation contract:**

1. Define a serializable `ContinuationRequest` containing stable IDs and policy inputs, never Python object references.
2. Reconstruct from the WAL plus immutable blob/artifact refs. Reuse canonical reducers; do not create a second replay state machine.
3. Classify the next legal transition: complete, suspended awaiting exterior approval, safe to resume, or undeterminable because an external effect intent lacks a terminal receipt.
4. Never automatically repeat an uncertain external effect. Reconcile to `EffectReconciled`/undeterminable or require an idempotency proof.
5. Reattach turn/depth/lease limits from durable state. A new process does not receive a fresh budget.
6. Continue through the same `HarnessSession`/universal turn mechanism. Recovery is not a privileged alternate executor.
7. Preserve event IDs, causation/parent lineage, hash chain, `D_H`, `D_R`, project/run/episode IDs, and single-writer rules.
8. Make the test hermetic: subprocess, temporary SQLite path, fake/cassette model, fixed clock/randomness, and no network/API key.

**File-conflict rule:** Developer B owns recovery and the new subprocess test. Developer A owns trajectory/session accounting. If continuation requires a `session.py` entrypoint change, Developer B proposes the interface in a small preparatory PR; Developer A lands or approves the shared seam before either branch continues.

**Exit:** RF-25 is green and existing cold-replay, approval-resume, durable-intent, reducer, event-store, and session tests remain green.

### 3.6 Sprint 2C.3 — integration and M-2 re-gate (1–2 working days)

| ID | Owner | Work | Gate |
|---|---|---|---|
| **W2C-I1** | Both developers | Run NOVA-1 and NOVA-2 together: measured turn → suspension → process exit → resume → signed/null terminal evidence. | One continuous event/trajectory lineage; no cost double count or repeated effect. |
| **W2C-I2** | Tech Lead | Review every compatibility/default branch and every changed writer owner. | Unknown fails closed; legacy data is visible but ineligible; no second writer. |
| **W2C-I3** | Tech Lead | Re-run all M-2 exit gates and adjudicate environmental failures. | No unexplained red, no skipped falsifier, no “mostly green.” |
| **W2C-I4** | Director | Sign M-2 or return a bounded blocker. | M-3 remains closed until signature. |

Minimum re-gate commands:

```bash
python3 -m unittest discover -s test/kernel -t .
python3 -m unittest discover -s test/contracts -t .
python3 -m unittest discover -s test/agency -t .
python3 -m unittest discover -s test/runtime -t .
python3 -m unittest discover -s test/adapters -t .
python3 -m unittest discover -s test/security -t .
python3 -m unittest discover -s test/trust -t .
python3 -m unittest discover -s test/falsifiers -t .
python3 -m unittest discover -s test/registry -t .
python3 tools/linters/check_boundaries.py
python3 tools/linters/check_tcb_budget.py
python3 tools/linters/check_domain_blindness.py
python3 tools/linters/check_isolation_policy.py
python3 tools/linters/check_event_coverage.py
python3 tools/linters/check_duplication.py --enforce
python3 tools/linters/check_markdown_links.py --all
python3 tools/linters/check_stale_paths.py
python3 tools/linters/scan_secrets.py
```

Record exact counts, environment-sensitive exclusions, Git commit, Python version, and the SQLite evidence artifact. Never summarize six unrelated reds as “offline noise” without one bounded reason per test.

---

## 4. M-3 immediately after Wave 2C: make composition generic

M-3 starts only after the M-2 signature. This is where the graph schema, plugin lifecycle, and Layer-0 deletion belong.

### 4.1 Sprint 3.0 — Contract and failing graph tests

Land the accepted ADR-0077/0079 SPEC deltas and [`schemas/mhf/manifest_v2.schema.json`](schemas/mhf/) in the same change as red contract tests—not weeks earlier as an unused speculative schema.

Required tests:

```text
test.contracts.test_manifest_v2_graph
  .ManifestV2GraphFalsifier
  .test_six_topologies_compile_without_kernel_or_engine_change

test.contracts.test_manifest_v2_digest
  .ManifestV2DigestTests
  .test_order_and_yaml_json_do_not_change_digest

test.contracts.test_manifest_v2_digest
  .ManifestV2DigestTests
  .test_authority_config_or_edge_change_changes_digest

test.contracts.test_plugin_lifecycle_v2
  .PluginLifecycleEventParity
  .test_every_state_transition_is_catalogued_emitted_owned_and_reduced

test.registry.test_layer0_retirement
  .Layer0Retirement
  .test_no_layer0_import_package_ci_or_test_surface_remains
```

The six topology fixtures are: linear planner, generator→critic→reviser, debate/fan-in, bounded tree search, cyclic critic loop bounded by budget, and obligation/Pareto controller. These are compile fixtures, not six new engines.

### 4.2 Sprint 3.1 — One Named Component Graph compiler

The graph contract must include:

- unique named component instances;
- component kind and implementation/plugin reference;
- typed provided and required interfaces;
- explicit connections with source endpoint, target endpoint, and optional policy/config ref;
- entrypoints;
- isolation class, capability request/ceiling, evidence mode, and lifecycle policy;
- content-addressed resolved refs;
- cycles allowed where interfaces type-check; runtime termination remains budget/turn governed;
- a JCS-frozen resolved graph defining `D_H`.

Implement semantic passes in order:

```text
P0 schema and identifier validation
P1 resolve all component/plugin/config references to immutable digests
P2 validate kinds and interface compatibility
P3 validate connectivity, entrypoints, required inputs, and explicit fan-in/out
P4 intersect pack, component, publisher, and runtime capability ceilings
P5 validate isolation and exterior evidence requirements
P6 reject unread config, unknown roles, ambiguous consumers, and dangling edges
P7 JCS-freeze the fully resolved graph and derive D_H
```

Converge the three current surfaces:

1. `HarnessManifest.components` in [`domain/artifacts/manifest.py`](vanguard/packages/domain/artifacts/manifest.py);
2. `REGISTERED_COMPONENT_CONSUMERS` in [`agency/manifests/loader.py`](vanguard/packages/agency/manifests/loader.py);
3. `ROLE_KIND` and downstream assembly in [`runtime/compose.py`](vanguard/packages/runtime/compose.py).

Target ownership stays hexagonal: pure graph values/parsing in `domain/`; plugin/SPI protocols in `ports/`; loop mechanics in `agency/`; resolution, registry, lifecycle, and composition in `runtime/`; process/model/sandbox/evaluator implementations in `adapters/`. The kernel receives typed effects, never graph topology.

### 4.3 Sprint 3.2 — Lifecycle parity and walking skeleton

Absorb the retained Layer-0 registry into a packages-path `runtime/registry/`. The complete FSM is:

```text
DISCOVERED -> RESOLVED -> VERIFIED -> ACTIVATED -> QUIESCING -> RETIRED
      \            \          \           \             \
       +-----------> FAULTED <--------------+-------------+
                         |
                         +-----------------------------> RETIRED
```

Every state entry is a distinct event, including `PluginDiscovered` and `PluginVerified`. Add both to the generated wire schema/source, owner table (`registry` only), canonical event catalog derivation, reducer, state projection, golden vectors, and event-coverage tests. Do not encode verification as a boolean inside `PluginResolved`.

Run the echo-plugin walking skeleton over UDS through discover→resolve→verify→activate→quiesce→retire plus fault injection. Only after that migrate `code-default` toolkits through the same path. Pull `_PROC_PATTERN` from the compiled canonical ceiling; do not keep the adapter literal as a second authority.

### 4.4 Sprint 3.3 — NOVA-4 and atomic Layer-0 retirement

Delete only after packages-path parity is green:

- `layer0/registry/`;
- `layer0/compose/`;
- residual `layer0/events/`;
- `layer0/__init__.py`, `py.typed`, and README;
- `layer0*` from [`pyproject.toml`](pyproject.toml);
- residual Layer-0 CI job/comments and tests;
- living documentation links that describe it as present.

NOVA-4 must reject at least: unknown plugin ref, semver mismatch, missing required interface, incompatible edge, empty/unparseable ceiling, unauthorized in-process isolation, unread manifest field, and lifecycle transition by a non-registry writer. After deletion:

```text
find layer0 -type f                  -> no directory / no files
rg -n '(^|\.)layer0|layer0\*' vanguard packs test tools pyproject.toml .github
                                      -> no live import/package/CI authority
python3 tools/linters/check_duplication.py --enforce
                                      -> green
```

M-3 exits only when `code-default` and the echo fixture compile through the same immutable graph and lifecycle, with no engine or kernel topology branch.

---

## 5. M-4 Foundation Stop Line

Wave 4 performs one real coding-agent task against a small failing repository and produces one evidence bundle. All nine rows must refer to the same uninterrupted `run_id`:

| # | Required evidence | Pass condition |
|---:|---|---|
| 1 | Real model | Resolved provider/model/fingerprint or explicit provider fingerprint unavailability; actual tokens/latency captured. |
| 2 | Authorized effect | Descriptor-bound grant digest and lease ID; advisory-only execution is rejected. |
| 3 | Filesystem outcome | Preregistered failing test becomes green; changed artifact digest is recorded. |
| 4 | Sandbox | Actual bwrap containment report and negative probes; dependency presence is not proof. |
| 5 | Exterior evaluation | UID-10002-bound signed verdict recorded only by the evaluator gateway. |
| 6 | WAL truth | File-backed SQLite WAL, single writer, continuous hash/causation lineage. |
| 7 | Cold continuation | Fresh-process reconstruction/continuation proof from the same WAL. |
| 8 | Rich trajectory | `mhf.trajectory/1` is schema-valid **and populated**, with costs, identities, `D_H/D_R/D_X`, receipts, event range, outcome, and evidence semantics. |
| 9 | One runtime | `layer0/` absent; one compiler, selector algebra, writer, scheduler/loop authority, and runtime path. |

No stitched rows, copied verdict, alternate demo, cassette substituted for the live row, manual intervention, or scope widening is allowed. Per-PR CI may replay a cassette recorded from the accepted live run, but the milestone decision uses the original real evidence bundle.

After M-4, stop and obtain the Director's release/generalization decision. Do not let enthusiasm for the first success silently start M-5.

---

## 6. How the foundation grows into the Tier S+ general solver

The requested capabilities are valid goals, but their value and safety depend on the foundation gates. Assign them as follows.

| Capability family | Earliest milestone | Architectural home | Proof before promotion |
|---|---|---|---|
| **Pack #2: Math & Formal Deductive Verification** | M-5 | New pack, formal checker adapter/plugin, existing runtime | Zero diff under `domain/` and `kernel/`; exact exterior witness; graph/trajectory parity with coding pack. |
| **Deterministic witness cache** | M-5 T0 | Runtime cache/index client over content-addressed artifacts | Key binds obligation/task, inputs, environment, checker, toolchain, assurance, and policy version; verdict never copied to a different subject digest. |
| **Recursive `agent.spawn`** | M-6 | One new mediated effect through S0–S12; semantics remain in agency/runtime | No grant→deny; child ceiling is subset; budget/depth/lineage durable; target kernel total remains within 1438 LOC. |
| **Stigmergic swarms / “swards”** | M-7 | WAL-derived obligation/claim projection and lease-bound workers | Bounded state protocol, cold continuation, no peer authority channel, no duplicate external effect, measured contention/bytes/retries/critical path. |
| **Pareto model/tool/topology routing** | M-7 | Exterior runtime policy; current `tier_escalation.py` is the seed | Safety and reservation feasibility precede optimization; predicted vs settled cost calibration retained; escalation gets a new lease. |
| **Harness/agentic CLI builder** | M-8 | `apps/`/TypeScript CLI as client of runtime graph compiler | CLI cannot mint grants/verdicts or bypass composition; generated graph round-trips and produces stable `D_H`. |
| **Debate, critic loops, tree search, MCTS, ensembles** | M-8 | Planner/controller components expressed in the Named Component Graph | No engine/kernel changes per topology; cycles budget-bound; exterior witness decides output. |
| **Skills and procedural cards** | M-9 T2 | Pack/runtime skill index and context compiler | Hybrid retrieval lift on held-out paired tasks; provenance, expiry, protection, and negative transfer measured. |
| **Memory, RAG, indexing, search** | M-9 | `IndexPort` plus exterior adapters; immutable sources and rebuildable indices | Index is disposable/rebuildable; citations bind source digests; retrieval cannot widen authority or overwrite evidence. |
| **Context compression and compaction** | M-9 | Existing `agency/context/` L1–L5 compiler, policy in graph | Token reduction measured with invariant/answer retention; omissions and compaction lineage disclosed; no hidden failed evidence. |
| **AST heuristics and domain algorithms** | M-8/M-9 | Coding-pack plugins/macros, never domain/kernel ontology | Cross-language fixtures, deterministic tests, least-privilege selector ceiling, fallback path. |
| **Local LLM + API-provider mixtures** | M-7/M-9 | `ModelPort` adapters and exterior Pareto router | Provider-neutral contract; model fingerprint/pricing status; failover does not change authority; paired cost-per-signed-pass measurement. |
| **Macro-tool compilation** | M-9 T1 | Offline compiler producing an ordinary versioned plugin candidate | Causal subgraph, inferred narrow interface, adversarial replay, S0–S12, exterior checker, held-out pair, total cost including fallback. |
| **Active-Inference policy** | M-10 | Exterior controller | VFE fits beliefs; EFE ranks feasible actions; prediction recorded before observation; calibration improves without authority growth. |
| **DPO/RL and trajectory-graph credit** | M-10 T3 | Offline lab/training pipeline | Eligible corpus only; signed winner/loser evidence; graph causality rather than timestamp guess; no self-reported reward. |
| **Self-improving harness/model/skill selection** | M-10 | Experiment and release pipeline | Pareto-safe, paired exact McNemar, effect size/interval, A/A floor, immutable baseline, human pointer, tested rollback. |

### Memory and retrieval rules

Future memory is a view over attributable artifacts and evidence, never a second truth store. Separate:

- **working context:** episode-local and budgeted;
- **semantic/lexical index:** rebuildable from immutable sources;
- **witness cache:** exact deterministic reuse only;
- **skill cards:** evidence-ranked suggestions, not grants;
- **training corpus:** opt-in, provenance-complete, promotion-eligible rows only.

Use dense 384-dimensional embeddings only as one retrieval signal combined with lexical/structural evidence. Record embedding model/version in index identity. Elo decay affects retrieval ranking and eviction, never authority. AST and graph heuristics remain pack-specific plugins until at least two domains justify a substrate abstraction.

### Model-routing rules

Local and API models remain replaceable routes. The router optimizes expected cost per signed pass among feasible choices, not raw benchmark score. It records route, resolved model, fingerprint/version, token/cache usage, latency, pricing provenance, fallback, and verifier outcome. Unknown price is not free. A provider failure is an instrument error, not a task failure and not a reason to widen capability.

### Macro and compounding rules

The flywheel order is mandatory:

```text
T0 exact witness memo
 -> T1 verified macro candidate
 -> T2 skill/router adaptation
 -> T3 DPO/model/harness candidate
 -> paired exterior evaluation
 -> human promotion or rejection
```

The frequently cited `50k tokens -> 500 tokens` is a target for a benchmark report, not an assumption in ROI calculations. Measure discovery, compilation, sandbox startup, verification, cache lookup, fallback, and amortization break-even. A macro that is fast but widens its selector, weakens evidence, or fails held-out tasks is rejected.

---

## 7. Sprint-planning operating system

### 7.1 Plan at two resolutions

- Keep M-0–M-10 as outcome-level gates in [`milestones.md`](docs/02_roadmap/milestones.md).
- Keep only the current authorized sprint as file-level tickets in [`sprint_active.md`](docs/03_sprints/sprint_active.md).
- Draft the next sprint when the current gate is approximately review-ready, but mark it queued and do not assign production work before entry is signed.
- Do not prewrite detailed M-7–M-10 task boards; new evidence from M-4/M-5 must shape those designs.

### 7.2 Every ticket must contain

1. one accepted requirement/ADR;
2. one named falsifier or measurable gate;
3. exact owning files and forbidden files;
4. one owner and one reviewer;
5. entry dependency and exit evidence;
6. security/boundary impact;
7. compatibility and rollback rule;
8. expected PR size or explicit split point.

If a developer needs behavior that is not in an accepted ADR/schema/falsifier, stop and escalate. Do not improvise a new architecture inside a code review.

### 7.3 PR sequence

For each feature packet:

```text
PR 1: decision/schema + RED falsifier (no production behavior)
PR 2: smallest implementation that makes the primary falsifier green
PR 3: negative/security/conformance cases and compatibility cleanup
PR 4: deletion/sunset only after parity; update board/status to observed truth
```

Combining PRs is acceptable only when the schema and implementation cannot compile separately; retain separate commits and show the red result in the PR evidence.

### 7.4 Daily and weekly control

- Daily: owner posts falsifier state, changed file surface, blockers, and whether a stop line was touched.
- Twice weekly: Tech Lead checks boundary drift, TCB count, writer ownership, schema/codegen parity, and duplicate surfaces.
- End of sprint: run the full proportional gate set, attach outputs, classify every red, and update the board once.
- Milestone review: Director reviews one evidence bundle and either signs green or returns a bounded blocker with owner and falsifier.

Avoid ceremonial status prose. A state change is backed by a test, artifact digest, signed decision, or measured run.

---

## 8. Repository cleanup plan

### Clean now, before production work

- fix broken living links and widen link scanning;
- normalize RF/F identifier references without changing historical ADR text;
- correct stale `spawn()` documentation if it contradicts accepted behavior, pinned by a test;
- remove duplicated live-board text only when the board retains the decision and links to archived evidence;
- classify current environmental test failures with one bounded reason each.

### Clean atomically at M-3

- all remaining `layer0/` code, packaging, CI, tests, and live navigation;
- hard-coded component-consumer tables after the graph registry becomes their typed replacement;
- the duplicated `_PROC_PATTERN` literal after the compiled ceiling supplies it;
- compatibility readers only when their sunset gate and fixtures say no supported artifact needs them.

### Collapse documentation at M-5, not now

After M-4 is signed, reduce living governance to the Clean Triad:

```text
SPEC + annexes          -> what
accepted ADRs           -> why
sprint_active + plans   -> how/now
```

Keep proposal/research/review files as advisory provenance or archive them through an explicit move with link rewrites. Do not delete duplicate-looking research until hashes, citations, and authority class are verified. Never execute a stale review's delete instruction without rechecking the target at current HEAD.

---

## 9. Hard stop lines and forbidden shortcuts

Stop and escalate if any change proposes to:

- add routing, graph search, memory learning, obligations, or macro compilation to `kernel/`;
- exceed the 1438-LOC TCB ceiling or spend headroom without removing equivalent risk;
- create a sixth SPI before the scheduled measured review;
- introduce a second runtime, selector algebra, event writer, replay reducer, manifest parser, or truth store;
- treat a path map as a graph without typed connections;
- record missing cost as zero or estimated cost as measured;
- copy a verdict or cache hit onto a different subject digest;
- allow a model, macro, agent, or plugin to grade or promote itself;
- let direct agent messages carry grants, claims, approvals, verdicts, or default-pointer changes;
- automatically retry an uncertain external effect after crash;
- claim `O(N)` swarm coordination without the bounded-operation premise and measurements;
- hardcode profile latency/token promises or claim token collapse before a benchmark;
- begin spawn, concurrency, Pack #2, learning, or document collapse before its entry gate;
- widen scope to make the M-4 demo pass.

`AUTHORIZATION_DENIED` never licenses an automatic mutation. State, price, belief, confidence, rating, retrieval rank, cached success, or learned policy may influence selection but may never widen a capability.

---

## 10. Final assignment sheet

### Start immediately after Director authorization

| Order | Assignment | Owner | Expected result |
|---:|---|---|---|
| 1 | D-ALFA-1: approve/narrow/reject six ADR decisions and the `/1` trajectory amendment. | Engineering Director | One signed decision map. |
| 2 | Widen link and RF-ID linters; fix living plan links. | Tooling owner | Documentation gates measure the documents developers will cite. |
| 3 | File accepted ADRs, minimal SPEC delta, and Wave 2C board tickets. | Architect + Tech Lead | One legal, executable work queue. |
| 4 | Write RF-23/RF-24/RF-27 red. | Developer A | Evidence defects reproduced without production edits. |
| 5 | Write RF-25 red with file-backed SQLite and fresh interpreter. | Developer B | Continuation gap reproduced without production edits. |
| 6 | Implement NOVA-1 and NOVA-2 in parallel under the file-conflict rule. | Developers A/B | Rich trajectory and true cold continuation green. |
| 7 | Integrate, run the full M-2 gate, and adjudicate every red. | Tech Lead | Director-ready M-2 evidence bundle. |
| 8 | Sign M-2 or return one bounded blocker. | Engineering Director | M-3 opens or remains closed unambiguously. |

### Then, and only then

1. file the just-in-time manifest/2 and lifecycle contract delta with red graph/FSM tests;
2. implement the one graph compiler and seven-state event parity;
3. prove the echo walking skeleton;
4. migrate `code-default` through the same lifecycle;
5. run NOVA-4 and delete Layer-0 atomically;
6. sign M-3;
7. produce the one nine-row M-4 evidence bundle;
8. prove Pack #2 with zero domain/kernel changes;
9. grow capabilities in the gated M-6–M-10 order.

The desired SOTA system is not one giant feature sprint. It is a compounding sequence in which every new power—recursive delegation, swarms, CLI composition, memory, RAG, search, compression, AST intelligence, heterogeneous models, macro-tools, and learning—enters as an exterior, least-privilege component over a foundation whose authority, state, evidence, identity, and economics are already reconstructible. That is how AETHER becomes a general task-solving recursive meta-framework without sacrificing the properties that make its results trustworthy.
