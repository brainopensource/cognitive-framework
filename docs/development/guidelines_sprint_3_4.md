# SPRINT 3–4 STRUCTURE PROMPT
## Tech Lead + Project Lead — executable backlog, packets and merge gates

**Audience:** Project Lead and Tech Lead only. Do not distribute this prompt to developers.  
**Companion:** `docs/development/guidelines_sprint_3_4_briefing.md`  
**Pattern:** same production line as `docs/development/guidelines_phase_0.md` → Sprint 1 packets.  
**Code:** this prompt produces documents. It does not authorise implementation until the Project Lead issues a go.

---

## 1. Mandate

Act as the accountable leadership team. Convert the already-built trust spine (schemas, kernel dispatch, ledger) into **Sprint 3 and Sprint 4 executable structure** that four developers can run in parallel: two seniors and two mid/normal developers, mixed complexity, each lane startable on day one against merged ports — not against each other.

The product target for the *next* programme slice is the **beta MVP**:

> A small framework that composes one frozen `HarnessManifest` and runs it. The first shipped harness is a simple coding agent: typed `read` / `search` / `patch` / `test`, Git worktree, human approval of privileged writes, and a real LLM behind `ModelPort` (OpenRouter, OpenAI-compatible). The S4 gate still runs with **no model at all**.

This prompt exists because GTS-13C Part II is a sequencing map, not a staffable sprint. Sprint 1 had packets, a backlog and activated contract rows. Sprints 3 and 4 do not. Your job is to produce that missing structure, then stop. Developers receive only the approved packets.

---

## 2. Authority model

Do not invent a second hierarchy. Use the Sprint 0 chain:

1. Approved Decision Record — `docs/v4/09_vanguard_decision_register_v040.md`
2. Vanguard v4 contracts — `docs/v4/02` through `07`
3. System Architecture & ICD — `docs/sprint0/system-architecture-icd.md`
4. Verification, Threat & Evaluation Plan — `docs/sprint0/verification-threat-evaluation-plan.md`
5. Active MVP Contract — `docs/sprint0/active-mvp-contract.json` (the only merge gate)
6. GTS-13C — `docs/v4/13_C_gts_mvp_program_and_engineering_plan.md` (plan and rationale only)
7. Issue tracker — daily execution
8. This prompt and its briefing — leadership execution only

VG-08 (`08_vanguard_phase_0_build_plan_v040.md`) is **disposable**. Use its Increment A/B hypotheses and must-fail catalogue as evidence. Do not treat its ticket order as the sprint calendar; ADR-0046 already gave sequencing to GTS-13C.

If two sources disagree, record the conflict and resolve it with an ADR or a Project Lead decision. Do not silently choose.

---

## 3. Facts you must not contradict

Verify against the filesystem and CI, not against stale briefing status strings. As of the Sprint 3–4 planning review:

### Already on disk (do not reschedule as Sprint 3 work)

| Capability | Evidence |
|---|---|
| T1.1–T1.12 wire types, dual TS+Python readers, golden vectors | `schemas/v4/`, `vanguard/packages/domain/` |
| T2.1–T2.10 kernel dispatch S0–S12, attenuation, budgets, sink-class mediation | `vanguard/packages/kernel/dispatch.py`, ADR-0054, `REQ-KRN-001..003` covered |
| T3.1–T3.8 event store fake+SQLite, reducer, recovery scanner, cassettes, JSONL | `adapters/stores/`, `runtime/ledger/recovery.py`, `REQ-LEDGER-001..002` covered |
| Package lattice and broken-counterpart harness | `tools/check_boundaries.py`, `test/broken/` |
| Mock CLI `vg run` / `vg trace` / `vg why` | `vanguard/clients/cli/` + `MockRuntime`; `REQ-CLI-001` still **open** |
| Disposable T0a spike + T0b slice (OpenAI-compatible HTTP, git apply path) | `spike/`, `slice/`; `slice-findings.md` exists; live-provider numbers still pending |
| Artifact graph / `vg-shell-only` JSON | `vanguard/packages/domain/artifacts/`, `vanguard/packages/agency/manifests/` |

### Not implemented (this is the Sprint 3–4 surface)

| Capability | GTS-13C | VG-08 |
|---|---|---|
| Episode engine (observe → propose → authorise → effect → receipt; terminate, do not self-evaluate) | T4.1–T4.7 | TK-10 fake-model half |
| Process engine (finite approvals, restart-resume, no model) | T4.8 | (VG-10 `DEF-12` deferred — **supersede for beta**, see §8) |
| Port activation bundles for Model / Environment / Evaluator / Sandbox | ICD §4 | TK-10/08/09/11 ports |
| Worker perimeter + containment report | T5.1–T5.2 | TK-08 |
| Production `ModelPort` (OpenRouter); never lifted from `slice/` | T6.1 | TK-10 real-provider half |
| Permanent Git `EnvironmentAdapter` | T6.1–T6.2 | TK-11 |
| Exterior evaluator identity | T5.3–T5.6 | TK-09 — **S5, not S3–S4 product gate** |
| Context compiler L1–L5 | T4.9–T4.11 | `03 §10` — **S5** |

GTS-13C still lists T2.6–T2.10 and T3.6–T3.8 as Sprint 3. That row is **stale**. Rebase Sprint 3 onto remaining T4/T7/port work. Do not open tickets that re-implement kernel dispatch or ledger recovery.

---

## 4. Product slice this structure serves

Name the gates in the Decision Record before writing packets.

| Gate | When | Done when this is true | Not required |
|---|---|---|---|
| **S4 trust-spine** (Increment A / ADR-0048) | end of Sprint 4 | A **scripted** trajectory runs with **no model**. Denial, attenuation, budget exhaustion, atomicity, recovery, secret non-disclosure are green. `spike/` and `slice/` are deleted and CI proves absence. | OpenRouter, dogfood, A/A, TableWorld |
| **Beta MVP** (Increment B / GTS-13C Ch.10 Q1+Q2) | end of Sprint 6, *previewed* by this structure | Framework composes one harness (`vg-code-default`). A real OpenRouter model, typed tools, Git worktree and human approval fix a real single-file bug without hand-patching. Operator would reach for it again. | A/A floor, paired comparison, non-coding environment, competitor reconstructions, autonomous promotion |

Sprint 3–4 exist to make the S4 gate real **and** to land the parallel adapters the beta needs, without letting the real LLM become a prerequisite of kernel verification.

**Framework, one harness.** A harness is a frozen `HarnessManifest` (`03` composition, GTS-13C Ch.7), not a codebase. Beta ships exactly one product manifest: `vg-code-default` (typed tools). `vg-shell-only` remains the undeletable experimental baseline (ADR-0049). Do not build Claude-Code / OpenCode reconstructions (T7.5–T7.7, Sprint 7).

---

## 5. Deliverables this prompt must produce

Produce all of the following before any Sprint 3 implementation merge. Mirror Sprint 1.

| # | Artifact | Owner | Path |
|---|---|---|---|
| D1 | Named beta and S4 gates (ADR) | Tech Lead + Project Lead | Decision Record append |
| D2 | Rebased S3–S4 projection (what moved, what is already done) | Tech Lead | short note under `docs/development/` or GTS-13C amendment note — **do not silently edit Part II** without recording the defect |
| D3 | Active MVP Contract amendment | Tech Lead | activate `REQ-TRUST-*`, `REQ-EXEC-*`, `REQ-PORT-*` (model/env/sandbox), `REQ-GOV-PROC-*`, `REQ-SEC-*` (perimeter). Create the missing `REQ-TRUST-001` / `TEST-TRUST-001` cited by ADR-0048 |
| D4 | ICD revision for worker identity, evaluator (forward), Git adapter, ModelPort | Tech Lead + Sr Dev | `docs/sprint0/system-architecture-icd.md` or a dated successor; do not leave ICD as “Sprint 0 baseline” while S3 merges product behaviour |
| D5 | Verification rows 1:1 with new `req_id`s | Sr Dev | no duplicate `MF-KRN-004..010` catalogue entries |
| D6 | `docs/sprint3/` — README, backlog, four developer packets | PM + Tech Lead | clone `docs/sprint1/` shape |
| D7 | `docs/sprint4/` — README, backlog, four developer packets | PM + Tech Lead | same |
| D8 | Tracker tickets with blocked-by | PM / Scrum | B-07 still open; do not leave markdown as the only tracker |
| D9 | Go / conditional-go / no-go | Project Lead | recorded decision |

Stop after D9. Do not write feature code under this prompt.

---

## 6. The four-lane law (non-negotiable)

Staff: **Senior A, Senior B, Developer C, Developer D**.

### 6.1 Start in any order

Every Sprint 3 packet must be startable on day one against **already merged** kernel, ledger, schemas and boundary CI. A developer must not wait for another Sprint 3 lane to merge before writing their first failing test.

The only legal shared surface between in-flight lanes is:

* existing `Kernel.dispatch` and `EventStorePort`;
* new port interfaces whose **fake + contract suite** land in the same PR as the interface (`ports` README: no port without the activation bundle);
* frozen JSON Schema / manifest files.

A lane that imports another lane’s unfinished engine is a defective packet. Rewrite it.

### 6.2 Unequal complexity is the point

| Person | Track | Complexity (0–5, same scale as the Phase 0 briefing) | Typical work |
|---|---|---|---|
| Senior A | GATE | 4–5 | Episode loop, trust-spine integration, no cognitive vocabulary in `agency/` |
| Senior B | GATE | 4 | Process engine (S3), then worker perimeter (S4) |
| Developer C | FAST, then GATE on real provider | 2 then 3 | Port fakes + suites; OpenRouter adapter behind `ModelPort` |
| Developer D | FAST | 1–2 | Manifests, typed tool schemas as artifacts, Git adapter, CLI client wiring to fakes |

Do not give Developer C or D an episode-engine or kernel-algebra ticket. Do not give Senior A the OpenRouter HTTP client. Mix is what makes four people busy without four people blocking.

### 6.3 Integration is a named exit ticket, not a day-one dependency

Each sprint has exactly one **integration ticket**, owned by Senior A, scheduled for the last 2–3 working days:

* Sprint 3 integration: fake-model episode turn + process instance both append to the same ledger through the kernel; architecture tests still forbid `agency` → adapters and `governance` → model.
* Sprint 4 integration: scripted no-model trust-spine trajectory (ADR-0048). OpenRouter and Git **real** adapters may exist but must be switchable off. The gate command uses cassette/fake only.

### 6.4 The real LLM must not capture the trust spine

OpenRouter work is **in** Sprint 4 (Developer C) so beta is not delayed, and **out** of the S4 exit command. If the trust-spine demo cannot run with `OPENROUTER_API_KEY` unset, the packet failed.

Never copy `slice/provider.ts` or `spike/` into `adapters/`. Rebuild behind `ModelPort`. Deletion of `spike/` and `slice/` remains a Sprint 4 checked gate (ADR-0047, `MF-S4-001`).

---

## 7. Required Sprint 3 structure

**Sprint goal (one sentence):** four independent seams exist so a fake-model episode and a model-free approval process can both talk to the already-built kernel and ledger.

Half-sprints only if a dependency would otherwise be unsatisfiable inside two weeks. Prefer four parallel packets over S3a/S3b unless Senior A’s loop cannot be tested without Developer C’s `ModelPort` fake — in which case Developer C’s **fake** (not the real OpenRouter adapter) is Sprint 3 week-1, and Senior A consumes the fake from day one via the published port.

| Packet | Owner | GTS-13C / VG-08 | Complexity | Files they own | Done = |
|---|---|---|---|---|---|
| S3-SA | Senior A | T4.1–T4.5 (loop + terminals; recursion may be depth-1 only if T4.4 is split) | 4 GATE | `vanguard/packages/agency/` (engine, not adapters) | Scripted cassette proposal → kernel grant/deny → receipt → terminal state. Episode does not call an evaluator. Lint forbids `plan`/`debug`/`reflect` identifiers in `agency/`. |
| S3-SB | Senior B | T4.8 | 4 GATE | `vanguard/packages/runtime/governance/` | Interrupted approval process resumes from the ledger without replaying an episode. States readable without opening Python. |
| S3-DC | Developer C | ICD §4 port table; T10.2 | 2 FAST | `vanguard/packages/ports/` + `adapters/` fakes + `test/contracts/` | `ModelPort`, `EnvironmentAdapter`, `EvaluatorPort`, `SandboxRunner` each have interface + fake + shared suite. No live network. |
| S3-DD | Developer D | T7.1–T7.4, ADR-0049 | 2 FAST | manifests, kind registry, CLI client against **fake** runtime | `vg-shell-only` flagged undeletable; `vg-code-default` authored as data with typed tool schemas; freeze-at-composition test. CLI still must not import kernel/agency. |

**Sprint 3 must-not:** worker OS isolation, OpenRouter live calls, deleting `slice/`, context compiler, evaluator identity, TableWorld, A/A.

**Carry into Sprint 3 only if still open and cheap:** `REQ-CLI-001` mock completeness (Developer D), remaining T1 lock/justification (Tech Lead, not a fourth engine).

---

## 8. Required Sprint 4 structure

**Sprint goal (one sentence):** Increment A is proven with no model; disposable code is gone; the real provider and Git adapter exist behind ports for Sprint 5–6 to wire, not to invent.

| Packet | Owner | GTS-13C / VG-08 | Complexity | Files they own | Done = |
|---|---|---|---|---|---|
| S4-SA | Senior A | T4.1–T4.7 trust-spine demo; T4.6 concurrency as far as needed for the scripted trajectory | 5 GATE | `agency/` + runtime composition root + `TEST-TRUST-001` | Scripted trajectory, no model: denial, attenuation, budget exhaustion, atomicity, recovery, secret non-disclosure. Evaluator isolation **probe** may be a fake evaluator identity; full T5.3–T5.6 stays Sprint 5. |
| S4-SB | Senior B | T5.1–T5.2; VG-05 §6; TK-08 | 4 GATE | sandbox adapter + containment report | Mount/egress/syscall probes recorded. Unverified perimeter blocks publication. Red-team of this packet is scoped to worker escape against the **fake controller**, not a full programme red team. |
| S4-DC | Developer C | T6.1 ModelPort real half | 3 GATE | `adapters/` OpenRouter (OpenAI-compatible), cassette recorder | Live call works in a throwaway test with secret **references** only (T2.7). Production tests use cassettes. Trust-spine CI path does not instantiate this adapter. |
| S4-DD | Developer D | T6.1–T6.2 Git env + typed tools as effects | 2 FAST | `adapters/` Git environment; typed `read/search/patch/test` descriptors | Worktree per branch, snapshot-bound observe, preview including **new files**, apply, reconcile. Shell is allowlisted `privileged` fallback, never the default. Not copied from `slice/git-environment.ts`. |

**Sprint 4 exit (joint):** delete `spike/` and `slice/`; `MF-S4-001` green; findings already in `slice-findings.md` / `provider-notes.md` remain as notes. Latency numbers stay `TBD` until a live slice-equivalent run exists — do not invent a p95 gate in Sprint 4 (Verification Plan §6).

**Sprint 4 must-not:** claiming beta dogfood, wiring OpenRouter into the default `vg run` path as the S4 demo, TableWorld, competence lifecycle, autonomous promotion.

---

## 9. Conflicts you must adjudicate before packets

Write the winning choice into the Decision Record. Packets may not contain “or”.

| ID | Conflict | Recommendation (you may reverse, but you must choose) |
|---|---|---|
| C1 | GTS-13C S3 = T2.6/T3.6 vs code already covering them | Rebase S3 onto T4 + ports + manifests |
| C2 | VG-08 Increment C (TableWorld in Phase 0) vs GTS-13C T9 at S8 vs beta = coding agent | **Exclude TableWorld from S3–S6 beta.** H0 is tested later. Record that VG-08’s “TableWorld in Phase 0” is sequencing, not a beta requirement |
| C3 | VG-10 `DEF-12` (approvals deferred) vs GTS-13C T4.8 / T6.6 | **Approvals are in beta** for privileged git apply. `DEF-12` is superseded for this slice. Keep Evolution-plane promotion out of band |
| C4 | VG-03 §6.2 terminal vocabulary vs GTS-13C T4.5 | Pick one set (`completed/abstained/...` vs `resolved/abandoned/...`) in an ADR. Dual vocabularies in packets are a defect |
| C5 | VG-03 §7.4 frozen atoms `read, write, edit, glob, grep, shell` vs ADR-0049 `read, search, patch, test` + shell fallback | **ADR-0049 wins** for the coding harness. Map names once in the ICD |
| C6 | Briefing marks T2/T3 TODO and T6.4 DONE vs contract/code | Briefing is stale. S1 CLI is mock scaffold; S6 (not S4) owns real `vg run` against OpenRouter |
| C7 | Trust-spine tests in GTS-13C S4 list “evaluator isolation” vs T5.3–T5.6 in S5 | S4: fake evaluator principal + architecture test that agency cannot import it. S5: separate OS identity and double probe |
| C8 | Open T1 contract rows vs implemented schemas | Tech Lead either marks `covered` with receipts or keeps them merge-blockers. Do not start S3 product merges while Gate B would fail on `schemas/v4-v0.1` |

---

## 10. Packet rules (clone Sprint 1)

Each developer packet is one to two pages and contains:

1. Ticket IDs and `req_id`s they may cite  
2. Files they may create or modify (and files they must not touch)  
3. Ports they consume (exact names) and values they produce for the integration ticket  
4. First failing test they must write  
5. Must-fail / architecture tests they own  
6. Complexity, track (FAST vs GATE), and who signs the merge  
7. Explicit “out of packet” list  

Developers read only: Decision Record, GTS-13C, ICD, Active MVP Contract, Verification Plan, their packet, their backlog, VG-01/03/04/05 as cited, PR template, package READMEs.

Do not give developers this prompt, Rev A/B, GTS-13/13B, VG-12 vision language, or the Phase 0 leadership mandate.

Lint in every `agency/` packet: no cognitive vocabulary as identifiers (`03 §6`, GTS-13C T4.3). Lint in every `runtime/governance/` packet: no model port (`ICD §2`).

---

## 11. Contract, tests and ICD — minimum rows

Create these (names may vary; IDs must exist):

| req_id (suggested) | Statement | Sprint |
|---|---|---|
| `REQ-TRUST-001` | Scripted trajectory with no model dependency proves denial, attenuation, budget, atomicity, recovery, secret non-disclosure | S4 |
| `REQ-EXEC-001` | Episode loop reduces observe→propose→authorise→effect→receipt; evaluation is not requested by the episode | S3 |
| `REQ-EXEC-002` | Process instance resumes from ledger state without episode replay | S3 |
| `REQ-PORT-002` | ModelPort has fake + real (OpenRouter) + shared suite; instrument errors are not task failures | S3 fake / S4 real |
| `REQ-PORT-003` | EnvironmentAdapter Git fake + real; preview includes new files | S3 fake / S4 real |
| `REQ-SEC-001` | Unverified containment report blocks publication | S4 |
| `REQ-ARCH-006` | After S4 exit, `spike/` and `slice/` are absent | S4 |

Bind `TEST-TRUST-001` to `REQ-TRUST-001`. Deduplicate verification-plan `MF-KRN-*` IDs while you are there.

---

## 12. Operating constraints

* Two-week sprints. Do not extend Sprint 3 to finish Sprint 4 perimeter work.  
* Local spikes allowed; merges cite `req_id`s.  
* Secrets: OpenRouter key is a reference. Grep-export test remains in force (T2.7).  
* YAGNI: no canvas, no MCP, no semantic memory, no subagent framework, no routing policy beyond a single model id in the manifest, no promotion pipeline.  
* `lab/` stays isolated.  
* Staff to the architecture: Senior A = `agency`, Senior B = `governance` then sandbox, C = `adapters` model, D = `adapters` environment + manifests.

---

## 13. Reading list for this prompt

**Required:** Decision Record §7–§9; GTS-13C Part I T4–T7, Part II, Ch.4–7, Ch.10, Ch.15; ICD; Active MVP Contract; Verification Plan; VG-02 §2–§3; VG-03 §1, §6–§8, §10; VG-05 §1–§2 and perimeter; VG-08 §0–§2 and §5; VG-10 (to supersede `DEF-12` explicitly); `docs/sprint1/` as the packet template; `slice/slice-findings.md`; `spike/provider_notes.md`; `vanguard/packages/ports/README.md`.

**Forbidden as implementation authority:** GTS-13, GTS-13B, Rev A/B, VG-12, this prompt’s briefing status if it disagrees with CI.

---

## 14. Go / no-go

Project Lead issues one of:

* **Go** — D1–D8 exist, four packets are startable in parallel, `REQ-TRUST-001` is assigned, S3 does not contain covered T2/T3 work.  
* **Conditional go** — packets exist but T1 lock or hosted branch protection remains; local tests only, same rule as `DECISION-0001`.  
* **No-go** — S4 still XL-unsplit, or OpenRouter is on the trust-spine critical path, or lanes share an unfinished engine.

Do not begin Sprint 3 implementation PRs until that decision is recorded.

---

*This prompt owns the leadership procedure for structuring Sprints 3 and 4. It states no contract, gates no merge, and locks no decision.*
