# Sprint 3–4 Engineering Briefing
## Four-lane parallel execution toward the beta coding harness

**Audience:** Project Lead, Tech Lead, PM, Scrum, Senior Developers  
**Leadership prompt (do not give to developers):** `docs/development/guidelines_sprint_3_4.md`  
**References:** GTS-13C, VG-02/03/05/08/10, ICD, Active MVP Contract, Verification Plan, `docs/sprint1/`

**Purpose:** operational map of what is already built, how four people (2 senior, 2 mid) run Sprint 3 and Sprint 4 in parallel at mixed complexity, and how that feeds a beta MVP that is one framework plus one coding harness on a real OpenRouter model.

---

## 1. Beta in one paragraph

The **framework** is: frozen `HarnessManifest` + episode loop + kernel + ledger.  
The **beta product** is one harness, `vg-code-default`: typed `read` / `search` / `patch` / `test`, Git worktree, human approval of privileged writes, OpenRouter behind `ModelPort`.

Sprint 4 does **not** ship that product. Sprint 4 ships Increment A: a scripted trajectory with **no model**, then deletes `spike/` and `slice/`. OpenRouter and Git adapters are built in parallel in Sprint 4 so Sprint 5–6 can wire them instead of inventing them.

Full MVP (Sprint 9, GTS-13C Ch.10 Q3–Q4: A/A, generality, TableWorld) is out of this briefing.

---

## 2. Pacing (unchanged from Phase 0)

| Track | Levels | Who merges |
|---|---|---|
| FAST | 0–2 | Developer + peer/CI |
| GATE | 3–5 | Sr Dev and/or Tech Lead (+ Project Lead at 5) |

| Level | Profile |
| :---: | :--- |
| 1 | JSON manifests, CLI wiring, boilerplate adapters, unit tests |
| 2 | Port fakes, contract suites, Git adapter, cassette tests |
| 3 | Live provider adapter, must-fail counterparts, containment probes |
| 4 | Episode/process engines, attenuation-adjacent integration, OS perimeter |
| 5 | Trust-spine gate, contract amendment, joint go/no-go |

---

## 3. Current inventory (filesystem, not stale briefing checkboxes)

Phase 0 briefing still marks T2/T3 as TODO. The contract and tree disagree. Prefer this table.

| Area | Status | Implication |
|---|---|---|
| T1 schemas + dual readers | Implemented; several `REQ-SCHEMA-*` still `open` / not `LOCKED` | Tech Lead lock-or-justify before S3 product merges |
| T2 kernel dispatch + TCB alarm | Implemented, `REQ-KRN-001..003` covered, ADR-0054 | **Do not put in Sprint 3** |
| T3 ledger + recovery + cassettes | Implemented, `REQ-LEDGER-001..002` covered | **Do not put in Sprint 3** |
| T0a `spike/` | Present | Delete at S4 exit |
| T0b `slice/` + `slice-findings.md` | Present; live credential run still pending | Rebuild Git/provider; never import; delete at S4 |
| CLI mock `vg run/trace/why` | Present; `REQ-CLI-001` open | Keep as client; replace `MockRuntime` after S4 |
| `agency/` episode engine | Missing (manifest JSON only) | Senior A, Sprint 3 |
| `runtime/governance/` process engine | Missing | Senior B, Sprint 3 |
| Model / Env / Evaluator / Sandbox ports | Not activated (`ports` README forbids landing interface-only) | Developer C, Sprint 3 fakes |
| OpenRouter production adapter | Missing (slice has disposable OpenAI-compatible HTTP) | Developer C, Sprint 4 |
| Git production adapter | Missing (slice has disposable git path) | Developer D, Sprint 4 |
| Worker perimeter / evaluator OS identity | Missing | Perimeter = Senior B Sprint 4; evaluator identity = Sprint 5 |

Carry-overs that are **not** Sprint 3 engines: B-06 margin reporting, B-07 tracker import, B-09 hosted protection + tag, T0 reconstruction gaps, T0.6 human timing.

---

## 4. Milestone map (S3 → beta)

| When | Name | User-visible truth |
|---|---|---|
| End S3 | Seams | Fake-model episode and model-free approval process both record through the kernel |
| End S4 | Trust spine | No-model scripted trajectory green; disposables gone; OpenRouter + Git adapters exist but are off the gate path |
| End S5 | Judge is outside | Evaluator separate identity; context compiler prefix-stable |
| End S6 | **Beta** | `vg run` on `vg-code-default` + OpenRouter fixes a real bug; human approves the exact descriptor |

S7–S9 (reconstructions, A/A, TableWorld, Ch.10 Q3–Q4) stay off the beta backlog.

---

## 5. Four lanes — Sprint 3

All four start day one against merged kernel/ledger. They do not wait for each other. Integration is Senior A in the last 2–3 days.

| Lane | Person | Cx | Track | Packet theme | Own these paths | Must not touch |
|---|---|---|---|---|---|---|
| SA | Senior A | 4 | GATE | Episode loop, fake/cassette model, terminals, no self-evaluation | `vanguard/packages/agency/` (engine) | adapters, OpenRouter, governance approvals |
| SB | Senior B | 4 | GATE | Process engine, restart-resume, readable states | `vanguard/packages/runtime/governance/` | `agency/`, model ports |
| DC | Developer C | 2 | FAST | Port activation bundles: interface + fake + suite | `ports/`, `adapters/` fakes, `test/contracts/` | episode recursion, kernel algebra |
| DD | Developer D | 2 | FAST | `vg-code-default` + undeletable `vg-shell-only`; typed tool schemas as artifacts; CLI still on fake runtime | manifests, kind registry, `clients/cli` (no core imports) | live provider, sandbox OS |

**Sprint 3 exit tests (integration):** one cassette-driven episode turn and one interrupted process resume share a ledger digest recipe; architecture tests still fail `agency`→adapters and `governance`→model.

---

## 6. Four lanes — Sprint 4

Same people. Complexity stays mixed. Real LLM is parallel, not the gate.

| Lane | Person | Cx | Track | Packet theme | Own these paths | Gate interaction |
|---|---|---|---|---|---|---|
| SA | Senior A | 5 | GATE | No-model trust-spine trajectory (`REQ-TRUST-001`) | composition root, `TEST-TRUST-001`, agency integration | **Is** the S4 gate |
| SB | Senior B | 4 | GATE | Rootless worker, containment report, unverified ⇒ no publish | sandbox adapter, probes | Required for Increment A perimeter clause; scoped red team only |
| DC | Developer C | 3 | GATE | OpenRouter `ModelPort` real adapter + cassette record; secret references only | `adapters/` model | Must run with key unset on trust-spine CI |
| DD | Developer D | 2 | FAST | Permanent Git `EnvironmentAdapter`; typed tools as effects; preview includes new files | `adapters/` environment | Used by S4 only through **fakes** in the gate command |

**Sprint 4 exit (joint, Project Lead + Tech Lead):** ADR-0048 trajectory green; `spike/` and `slice/` absent (`MF-S4-001`); OpenRouter adapter present and unused by that command.

---

## 7. Why this parallelises

| Temptation | Defect | Rule |
|---|---|---|
| Everyone waits for the episode engine | Three people idle; S4 stays XL | Engines consume **ports**, not each other’s PRs |
| Put OpenRouter on the S4 demo | Model masks missing enforcement (ADR-0048) | Fake/cassette only on the gate command |
| Lift `slice/` into adapters | Disposable becomes architecture (ADR-0047) | Rebuild; then delete |
| Give both seniors the same T4.1–T4.7 XL blob | Unsplittable sprint | SA = open-ended loop; SB = finite process then OS perimeter |
| Give mid-devs kernel work | GATE queue explodes; FAST track unused | C = ports/provider; D = manifests/git |

“Any order” means **start** order, not “no integration”. Merge order is still: fakes before composition-root wiring; composition-root wiring before the trust-spine command.

---

## 8. Explicitly out of S3–S4

* TableWorld / non-coding environment (GTS-13C T9, VG-08 Increment C)  
* A/A floor, paired stats, verifier–deployment gap (T8)  
* Competitor harness reconstructions (T7.5–T7.7)  
* Context compiler as a scored artifact (T4.9–T4.11 → S5)  
* Evaluator double-probe / separate image (T5.3–T5.6 → S5)  
* Default `vg run` live OpenRouter dogfood (S6)  
* Competence promotion, semantic memory, canvas, MCP, routing search  
* Re-implementing T2 dispatch or T3 recovery  

VG-10 `DEF-12` (defer approvals) is **not** followed for beta. Privileged apply needs a human-readable process. Evolution-plane promotion stays human and out of band.

---

## 9. Slice findings the packets must absorb

From `slice/slice-findings.md` (keep the notes; delete the code at S4):

* Model text is not a patch; extract, contain, `git apply --check` are separate stages.  
* Approval must show the exact patch and file stat, not the model’s story.  
* Test commands are argv, not a shell string.  
* Repo root and cwd are contract fields.  
* Provider / invalid patch / human reject / apply fail / test fail are different outcomes.  
* No p95 number until a live receipt exists.

---

## 10. Immediate leadership checklist

Use the full prompt (`guidelines_sprint_3_4.md`) to produce artifacts. This is the burndown:

1. ADR: name S4 trust-spine gate and S6 beta gate; rebase GTS-13C S3 away from covered T2/T3.  
2. Create `REQ-TRUST-001` (cited by ADR-0048, missing today).  
3. Activate EXEC / PORT / SEC rows; ICD update for ModelPort, Git adapter, worker identity.  
4. Write `docs/sprint3/` and `docs/sprint4/` packets (clone `docs/sprint1/`).  
5. Assign SA/SB/DC/DD; confirm no packet waits on another packet’s engine.  
6. Project Lead: go / conditional-go / no-go.  
7. Only then: four local branches, tests first, merges cite `req_id`.

---

*This briefing is operational. The leadership prompt is the procedure. Neither is a contract.*
