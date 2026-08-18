# Vanguard / GTS — System Specification Drifts

Phase 3 diagnostic of `prompt_TL_review.md`: theoretical baseline versus production backend, for the
v0.5.0 rewrite decision.

**Sources (backend only):**
- Theory: `SYSTEM_SPEC_THEORY.md` (synthesis of `docs/main_v4/` / `docs/01_specs/backend/` VG-00…VG-12 + GTS-13C)
- As-built: `SYSTEM_SPEC_ASBUILT.md` (forensic map of `vanguard/packages/` at `feat/harness-cli-v045` / `6f2f8b2`)
- Living board: `docs/scrum/roadmap_backend.md` (v0.4.5-beta, 2026-08-17)

**Out of scope:** `vanguard/clients/cli/`, `vanguard-gui/`, TUI/CLI presentation. `lab/` and
`tools/telemetry/` appear only where VG-07 names them.

**Method:** every row is a THEORY contract versus an ASBUILT fact. Categories:

| Tag | Meaning |
|---|---|
| `[DETERIORATION]` | The code is weaker than the spec, or claims a control it does not run in production |
| `[OPTIMIZATION]` | The code is a pragmatic or superior adaptation; keep it and amend the spec |
| `[NEUTRAL]` | Rename, layout, or honoured deferral/rejection — not a v0.5.0 fight |

**Headline:** the attenuation kernel, episode loop, hexagonal lattice, and freeze-at-composition harness are
real and should be the v0.5.0 core. The largest lies are *controls that exist as libraries and tests but are
not wired*, *a ledger that declares 34 kinds and emits 11*, and *a must-fail ID family the spec still
believes in*. Do not rewrite the kernel. Do wire provenance, emit the missing lifecycle events, and stop
citing `MF-01`…`MF-37` as if they were `test/broken/`.

---

## 1. Architectural & Structural Divergences

IDs `D-nn` are stable for the v0.5.0 plan. THEORY § / ASBUILT § cite the mirrored headings.

### 1.1 Control flow — the turn and the kernel

| ID | Drift | Tag | THEORY | ASBUILT |
|---|---|---|---|---|
| D-01 | Single effect path `Kernel.dispatch` S0–S12 exists and is ordered | `[OPTIMIZATION]` | VG-05 §2; `AT-01` | `dispatch.py` implements S1–S12; S0 is constructed in `EpisodeEngine._to_effect_request`. Keep |
| D-02 | Dual ingress `Principal::EvidencePlane` never calls `Kernel.dispatch` | `[DETERIORATION]` | VG-05 §2.1; `ADR-0061` | Evaluator is a daemon over UDS. Evaluation is *triggered* by `HarnessSession._evaluate` after the loop. No `EvaluationRequested` event |
| D-03 | `evaluate` is not in the episode loop | `[OPTIMIZATION]` | VG-03 six-step protocol includes evaluate | Exteriority is held (`A-12`, `test_spine`). Trigger ownership is the remaining defect (D-02) |
| D-04 | Sink-class mediation: grants only for `PRIVILEGED` | `[OPTIMIZATION]` | Tension `A-03` / `X-01` vs `ADR-0051` | All three sink classes still traverse dispatch and are recorded; only privileged take S6. Amend VG-02 `A-03` rather than revert |
| D-05 | Production justifying spans do not accumulate | `[DETERIORATION]` | `K-33`, `S1(e)`, `MF-02` | `provenance.py` is correct. `_admit_turn_result` returns `None`. Tool results never enter F-09. `MF-KRN-002` tests a fixture, not production |
| D-06 | `spawn()` does not call `Accumulation.child_return` | `[DETERIORATION]` | `K-33` child return is untrusted-derived | Child `run()` receives no spans. Spawn is live (`DEF-03` partially superseded) but provenance-blind |
| D-07 | `_operator_span` is a literal `Trust.OPERATOR` brief span | `[DETERIORATION]` | `K-31` labels per source class, never at a call site | `root.py:1210-1213` hard-codes `Span("brief-1", …)` |
| D-08 | Second refusal site in the episode engine | `[OPTIMIZATION]` | All denials through broker | Attenuated children refused in `engine.py:336-355` without `AuthorizationDenied`. Complements sealed scopes (`ADR-0067`); should emit an event |
| D-09 | Turn ceiling independent of `Reservation` | `[NEUTRAL]` | Budget vector includes turns | `EpisodeEngine._max_turns` → `ABANDONED`. Survives approval boundary. Document as a constraint, do not fold into kernel budget without a measurement |
| D-10 | `RegroundPolicy` exists and is never called | `[DETERIORATION]` | VG-03 §6.4 re-grounding | Only `test/agency/test_regrounding.py` references it. Hard-coded `STATUS.md` |

### 1.2 Ledger, events, recovery

| ID | Drift | Tag | THEORY | ASBUILT |
|---|---|---|---|---|
| D-11 | 34 kinds declared, 11 emitted, plus 2 extras | `[DETERIORATION]` | VG-04 §12.2 minimum set | Emitted: `EpisodeCompleted`, `ProposalProduced`, `AuthorizationDenied`, `BudgetReleased`, `EffectStarted`, `EffectCompleted`, `EffectReconciled`, `CompetencePriorRecorded`, `ApprovalRequested`, `RunRecovered`, `RunAborted`. Extras: `EffectRejected`, `KernelAlarm`. `EVENT_KINDS` is not enforced in production |
| D-12 | `EpisodeStarted` never written by the backend | `[DETERIORATION]` | First lifecycle event | Reducer/projection ready; CLI fixtures invent it. A run has no durable beginning |
| D-13 | `ApprovalResolved` is an in-process queue, not a ledger event | `[DETERIORATION]` | Human plane; `ProcessEngine` consumes the kind | `_cmd_ResolveApproval` → queue. Governance cannot replay an approval from the store |
| D-14 | `Heartbeat` never produced; T-08 HMAC absent | `[DETERIORATION]` | Authenticated heartbeats; recovery from outside | Scanner consumes Heartbeat; only `RunRecovered`/`RunAborted` are written. Grant HMAC is unrelated |
| D-15 | `CapabilityGranted` / `CapabilityRevoked` / `BudgetReserved` / `BudgetCommitted` not emitted | `[DETERIORATION]` | Authorisation and budget groups | Grants and leases happen; the ledger cannot reconstruct them. `GrantIssuer.revoke` has no caller (`K-49`) |
| D-16 | SQLite WAL event store + JSONL export | `[OPTIMIZATION]` | `CT-40`/`CT-42`, `ADR-0010` | `SqliteEventStore` WAL + `FULL` sync; JSONL is export. Keep |
| D-17 | Inbox/outbox as a second sequence store | `[OPTIMIZATION]` | No VG-03 counterpart; `ADR-0062` | `ServiceInboxStore` idempotent commands. Keep; specify in VG-03/04 |
| D-18 | `KernelAlarm` on `F-21a` as well as `F-24` | `[OPTIMIZATION]` | “F-24 is the only kernel alarm” | Intent-append failure must page. Amend VG-05; do not drop the F-21a alarm |
| D-19 | No blob+event atomic commit (`CT-18`); no blob encryption (`CT-19`) | `[DETERIORATION]` | Classification-keyed encryption hook | Two independent ports. Acceptable for Phase 0; must be an explicit ADR if v0.5.0 keeps it |

### 1.3 Types, ports, composition

| ID | Drift | Tag | THEORY | ASBUILT |
|---|---|---|---|---|
| D-20 | Port roster is GTS-leaning plus `ports/kernel.py` | `[OPTIMIZATION]` | `X-09` two rosters | `ModelPort`, `IndexPort`, `ClockPort`, `RandomPort`, `SandboxRunner`, plus kernel `Clock`/`EffectAdapter`/`EventSink`/`Ledger`. No `OperatorRunner`, `ObservationSource`, `PolicyEngine` port (`Governor` is a concrete class) |
| D-21 | Three types named `EffectRequest` | `[DETERIORATION]` | One request at S0 | `kernel.model`, `ports.environment`, wire `EffectDescriptor`. Translator exists (`invocation.py`) because of this |
| D-22 | Wire `Artifact` is T1.8, not VG-04 `CompetenceArtifact` | `[NEUTRAL]` | VG-04 vs GTS `T1.8` | `class`/`compensatesFor`/`hypothesis`/`riskDelta`. Competence graph still absent — shape choice is not the blocker |
| D-23 | `Claim` has graph fields; nothing walks them | `[NEUTRAL]` | VG-06 pipeline | Domain fields present; wire optional. Honoured `DEF-02` as long as v0.5.0 does not pretend `vg why` is a competence store |
| D-24 | `Reservation` has four dimensions, not six | `[NEUTRAL]` | `X-14` | `{usd_micros, millis, tokens, bytes_}`. Turns/depth enforced outside. Document; do not silently add `evaluations` without a consumer |
| D-25 | Closed package set + governance area + evaluator import ban | `[OPTIMIZATION]` | `LT-1`…`LT-8` never close the roster | `check_boundaries.py` is stricter than VG-03. Keep. Promote governance into VG-03’s lattice |
| D-26 | `compose()` freeze + kinds registry | `[OPTIMIZATION]` | `A-11`, `ADR-0005` | `FrozenHarness`; unknown names fail at composition. Keep |
| D-27 | `vg-table-default` on disk, not in `registry.json` | `[DETERIORATION]` | Increment C / `H0` | Pack is an orphan. TableWorld is not an `EnvironmentAdapter` |
| D-28 | Schema-driven `ProposalTranslator` + `aliases.json` | `[OPTIMIZATION]` | No VG-04 counterpart | Replaces a verb table (`S10-A-01`). Keep; specify as the model-to-kernel waist |
| D-29 | Python `parse_wire` is hand-written, not generated (`CT-02`) | `[NEUTRAL]` | Generated reader profile | Reader *JSON* is generated; Python types are not. Accept or generate in v0.5.0 — do not do both |

### 1.4 Perimeter, identity, self-modification

| ID | Drift | Tag | THEORY | ASBUILT |
|---|---|---|---|---|
| D-30 | Namespaces + startup probes + `publication_decision` | `[OPTIMIZATION]` | `K-42`–`K-44`, `K-46` | Real probes; fake runner is marked unverified. Keep |
| D-31 | No seccomp (`K-39`); stock `/usr/bin/bwrap` (`K-41`) | `[DETERIORATION]` | Syscall filter; statically linked supervisor | Probe of `unshare --mount` is not a filter. Limits reported, not applied (`K-37`) |
| D-32 | Evaluator **outside** the worker perimeter (`K-40` inverted) | `[OPTIMIZATION]` | Same perimeter, network denied | Separate UID 10002 daemon + unreadability probe is the *stronger* isolation for CL-1. Amend `K-40`; do not put the judge inside the candidate |
| D-33 | `AT-10`, `AT-11`, `AT-12` unimplemented | `[DETERIORATION]` | Cast lint; UID topology; capability↛verifier paths | Import lattice is not AT-12. v0.5.0 must add AT-12 or officially defer with a compensating control |
| D-34 | `SA-1`…`SA-6` absent | `[NEUTRAL]` | Self-mod is a release pipeline | Honoured: no updater. Do not build one in v0.5.0 |

### 1.5 Cognition, competence, measurement (mostly absence)

| ID | Drift | Tag | THEORY | ASBUILT |
|---|---|---|---|---|
| D-35 | No `CognitiveOperator` / operator registry | `[NEUTRAL]` | `A-02`, four extension forms | `_LayeredOperator` is a private model wrapper. Honoured Phase 0; do not fake operators as “layers” |
| D-36 | No playbooks | `[NEUTRAL]` | VG-03 §8; `DEF` still listed | Kind reserved. Roadmap: still deferred. Keep deferred |
| D-37 | Compaction: 3 of 5 strategies; default is recency-window | `[OPTIMIZATION]` | `structured_consolidate` recommended; `DEF-11` recency-only in Phase 0 | Ahead of DEF-11. Change the default only after a consolidation-loss experiment |
| D-38 | No parallelism / independence groups (`C-04`, `CC-*`) | `[NEUTRAL]` | `ADR-0007` wanted parallel from first commit | Sequential engine. `ADR-0065` D-02 is the operative constraint. Do not add fan-out in v0.5.0 until CC-6 can emit |
| D-39 | Competence graph / claim pipeline / activation / promotion | `[NEUTRAL]` | VG-06, VG-07 L4 | Types and `CompetencePriorRecorded` only. Roadmap: “do not start competence graph”. Keep out of v0.5.0 core |
| D-40 | Measurement apparatus in `tools/telemetry/` + `lab/` | `[OPTIMIZATION]` | VG-07 `S8-J-07`; `Y-08` | `M-18` tuple refusal, A/A refuse, split burn. Keep **outside** `vanguard/packages/` |
| D-41 | `runtime/loops/` / `MetaLoopEngine` deleted | `[OPTIMIZATION]` | Would have inverted `A-05` | Salvage is `tier_escalation.py` around `drive_until_green`. Keep this shape |
| D-42 | `runtime/coding_*` ~2,088 LOC + `domain/ledger/coding_session.py` | `[DETERIORATION]` | `M11` / `ADR-0060` / 80/20 generality | Engine/kernel stay domain-agnostic; domain acquired a coding projection. Move `coding_session` up or generalise it |
| D-43 | Second budget controller `runtime/coding_budget.py` | `[OPTIMIZATION]` | One governor | Pre-call worst-case USD reservation above the kernel. Keep as an adapter-side policy, not a second kernel |

### 1.6 Identifiers, tests, docs

| ID | Drift | Tag | THEORY | ASBUILT |
|---|---|---|---|---|
| D-44 | Live must-fail IDs are `MF-KRN-*` / `MF-S0-*` / … not `MF-01`…`MF-37` | `[DETERIORATION]` | VG-08 §5; `Y-10` | 38 cases pass. `rule_test_map.py` `tested=28` is a spec cross-reference, not coverage. `CI-9` exits 0 with `gaps=133` |
| D-45 | `REQ-*` is the code-visible requirement namespace | `[OPTIMIZATION]` | Example `REQ-KRN-014`; `TK-*` unused in packages | `check_pr_requirements.py` keys on `REQ-*`. Keep; stop minting `TK-*` in code |
| D-46 | README biological hierarchy vs `REJ-10` | `[DETERIORATION]` | Analogies quarantined in VG-12 | README §2 is LEVEL 0…9. No code implements it. Delete from README in v0.5.0 docs pass |
| D-47 | Stale README paths (`coordination.py`, `sqlite_event.py`, `fs_blob.py`) | `[DETERIORATION]` | — | Files were renamed/deleted. Docs, not runtime |
| D-48 | `cryptography` inside governance | `[NEUTRAL]` | “stdlib-only Python core” | Single third-party in the approval path. Declare it in the TCB list (`K-02`) |

### 1.7 How the code resolved corpus contradictions (`X-*`)

These are not new defects; they are decisions v0.5.0 must freeze.

| X | Code took | Tag for v0.5.0 |
|---|---|---|
| X-01 | Sink-class mediation, still one dispatch path | `[OPTIMIZATION]` — amend `A-03` |
| X-02 | `observe(..., grant=None)` | `[OPTIMIZATION]` — match `ADR-0051` |
| X-03 | Episode loop + `ProcessEngine` | `[OPTIMIZATION]` — put `governance/` in VG-03 `LT-*` |
| X-04 | VG-03 two axes (`ADR-0057`) | `[OPTIMIZATION]` — keep |
| X-05 | One `Trust` enum + envelope confidentiality | `[NEUTRAL]` — freeze this fifth shape in VG-04 |
| X-06 | VG-04 selector kinds; commands as `generic` URIs | `[NEUTRAL]` — either add `command` kind or specify the URI convention |
| X-07 | Kernel grant = actions + resources + purposeDigest; wire = actions + singular selector | `[DETERIORATION]` — one grant shape in v0.5.0 |
| X-08 | VG-04 envelope + `principalRole`; no `processId` on envelope | `[OPTIMIZATION]` — keep; processId stays in payload |
| X-09 | See D-20 | `[OPTIMIZATION]` |
| X-14 | Four-dimension `Reservation` | `[NEUTRAL]` |
| X-15 | Privileged approval shipped; ledger `ApprovalResolved` did not | `[DETERIORATION]` — D-13 |

---

## 2. Qualitative Trade-off & Engineering Evaluation

### 2.1 Why the tree diverged

Four forces, not one accident:

1. **The coding cell was the dogfood path.** Waves 11–22 bought a working `vg-code-default` loop, a schema-driven translator, spawn, sealed scopes, and an approval flow. That pulled ~2k LOC of coding-named runtime and left TableWorld / operators / playbooks / competence as reserved kinds. THEORY’s 80/20 generality constraint was mechanised (`check_core_changes.py`) and then locally violated (`coding_session.py`).

2. **Library-first kernel, composition-later wiring.** `provenance.py`, `RegroundPolicy`, `GrantIssuer.revoke`, `EVENT_KINDS`, and `ArtifactRegistryProjection` are complete enough to test in isolation. `runtime/root.py` never connected them. This is the characteristic v0.4.x failure mode: the control exists, the must-fail fixture exists, production does not call it. `K-33` is the exhibit.

3. **ADR stream outran VG-02/VG-03/VG-05 text.** `ADR-0051` (sink classes), `ADR-0057` (approvals), `ADR-0060` (generality), `ADR-0062` (inbox), `ADR-0067` (sealed scopes), `ADR-0063` (Python) are in the code. `A-03`, `K-40`, `DEF-12`, and the “F-24 only alarm” sentence were not patched. THEORY still contains the unresolved `X-*` table; the code already picked sides.

4. **Identity families forked.** Spec `MF-01`…`MF-37` / `TK-*` never landed as test IDs. Sprint packets minted `MF-KRN-*`, `MF-S0-*`, `REQ-*`. `CI-9` still scores the old map and does not fail. Anyone citing “28 tested rules” is citing a documentation grep.

### 2.2 What is actually strong (keep through a rewrite)

The hexagonal lattice with a closed package set is not theatre: `check_boundaries.py` plus 38 must-fail counterparts is the project’s real immune system. The dispatch sequence is small, ordered, and tested (`K-04`…`K-08`, `K-47`, `AT-09`). Attenuation denies rather than intersects. Integer microdollars and RFC 8785 canonicalisation are real. The evaluator cannot be imported from agency. Containment is probed, not asserted. `FrozenHarness` fails at composition. Spawn is fail-closed on missing child scope. `IsolatedEvaluator` runs both probes and will not construct a pass without them.

That cluster is the v0.5.0 kernel. A ground-up rewrite that discards it will re-introduce the defects `ADR-0021`…`0044` already paid for.

### 2.3 What looks like a control and is not

| Apparent control | Why it does not bind in production |
|---|---|
| Authority predicate `S1(e)` | Spans never include tool results; F-09 is almost unreachable |
| Child provenance | `spawn` does not call `child_return` |
| Evidence-plane trigger | Runtime calls `evaluate` directly; `EvaluationRequested` is dead |
| Ledger as the one memory | No `EpisodeStarted`, no grant/budget events, no `ApprovalResolved`, no Heartbeat |
| `EVENT_KINDS` closed set | Production accepts any `payload.kind` string |
| `CI-9` / “28 tested rules” | Wrong ID family; gate exits 0 |
| `K-40` same-perimeter evaluator | Opposite of what shipped; the opposite is better |
| TableWorld as generality witness | Not an `EnvironmentAdapter`; pack unregistered |
| `vg why` / Claim store | Explains absence; does not run a pipeline |

Reverting these to THEORY *as written* is not always right (see `K-40`). Reverting the **wiring** of provenance and lifecycle events is right.

### 2.4 Keep as-built vs restore THEORY — systemic implications

**Keep as-built (and amend spec):** sink-class mediation; sealed scopes; governance as a lattice area; inbox/outbox; schema-driven translator; evaluator as a separate identity not sharing the worker mount; three compaction strategies; `MetaLoopEngine` gone; `principalRole` on the envelope; `publication_decision`; F-21a as an alarm; `REQ-*` as the PR gate.

Implication: VG-02/VG-03/VG-05 must be edited in v0.5.0 *before* code, or the next cycle will re-drift. The `X-*` table is the edit list.

**Restore THEORY (and change code):** monotone span accumulation in the production composition; `child_return` on spawn; emit `EpisodeStarted`, `ApprovalResolved`, grant/budget events; make `EVENT_KINDS` a writer check; wire or delete `RegroundPolicy`; one grant shape; `coding_session` out of `domain/`; AT-12 or an explicit deferral; `CI-9` fails the build or the map is rewritten to live IDs.

Implication: these are not large modules. They are composition-root and emit-site patches, plus a must-fail ID migration. They are the cheapest way to make the existing kernel tell the truth.

**Do not restore in v0.5.0:** operators, playbooks, competence graph, promotion/canary, parallel independence groups, systems-language index, autonomous updater, browser/web search, five-process split. THEORY already deferred or rejected most of these. Building them now would recreate the v0.4 failure: more surface, same unwired predicates.

**Do not keep:** README biological hierarchy; stale README paths; the fiction that TableWorld witnesses `H0`; any claim that `MF-01` is `MF-KRN-001` without a published bijection.

### 2.5 The v0.5.0 rewrite fallacy

A ground-up rewrite is justified only if the lattice or the dispatch sequence is the problem. They are not. The problem is (a) composition that bypasses kernel libraries, (b) an event vocabulary the writer does not use, (c) a spec corpus that disagrees with itself and with the ADRs the code followed.

Rewrite target: **`runtime/root.py` wiring, episode emit sites, and the VG-00…05 text**. Not `kernel/`, not `ports/`, not `domain/canonicalisation/`, not `check_boundaries.py`.

---

## 3. Roadmap & Feature Completion Matrix

Rubric (applied to *production wiring*, not library presence):

| Score | Meaning |
|---|---|
| 100 | Types + production path + tests/must-fail + matching events |
| 70–90 | Path exists; named holes |
| 40–69 | Partial: types and some path; load-bearing invariant unwired or unemitted |
| 10–39 | Types/reserved kinds only, or apparatus outside packages |
| 0 | Absent, including honoured deferrals |

Percentages are judgement from ASBUILT, not CI. They are for sequencing, not for marketing.

### 3.1 Subsystems (backend)

| Subsystem | THEORY owner | Score | What “done” still lacks |
|---|---|---|---|
| Dispatch S0–S12 / tool execution | VG-05, VG-03 §1 | **78** | F-06 unused; EvidencePlane ingress; grant events |
| Capability attenuation + sealed scopes | VG-05 §4, `ADR-0067` | **82** | Child event on engine-level refuse (D-08) |
| Grants / HMAC / single-use | VG-05 `K-18`–`K-20` | **76** | No revoke caller; no renew (`K-21`); no `CapabilityGranted` event |
| Authority predicate in **production** | `S1(e)`, `K-33` | **25** | Library ~90; composition ~0 |
| Context layers L1–L5 + cache breakpoints | VG-03 §6 | **80** | — |
| Compaction | VG-03 §6.3 | **62** | Default not recommended; no loss experiment; two strategies missing |
| Re-grounding | VG-03 §6.4 | **15** | Module exists, unwired |
| Episode engine / terminals | VG-03 §6 | **72** | No `EpisodeStarted`; no operators |
| Spawn / child attenuation | `DEF-03`, `ADR-0060` | **70** | No `child_return`; no playbooks |
| Operators | `A-02` | **5** | Reserved kind only |
| Playbooks | VG-03 §8 | **5** | Reserved kind only |
| Parallelism / CC-* | VG-03 §8, `C-04` | **5** | Sequential; `ConflictDetected` never emitted |
| Git `EnvironmentAdapter` (8 methods) | VG-03 §7 | **85** | `readSet`/`writeSet` unconsumed |
| TableWorld / `H0` | VG-08 Increment C | **18** | Not an adapter; pack unregistered |
| Sandbox probes + publication | `K-42`–`K-44` | **75** | — |
| Sandbox as specified perimeter | `K-34`–`K-41` | **48** | No seccomp; no rlimits; stock bwrap; K-40 inverted (keep inverted) |
| Evaluator daemon + probes + signing | VG-06 §4, `CL-1` | **70** | Trigger is runtime-owned; no `EvaluationRequested` |
| Event store WAL + export | `CT-40`–`CT-43` | **88** | No migrations (`CT-46`) |
| Event *set* as a closed protocol | VG-04 §12.2 | **32** | 11/34 emitted; extras unenforced |
| Recovery scanner | VG-03 §9, `C-11` | **70** | No Heartbeat producer; T-08 unmet |
| Wire schemas + readers | VG-04, T1 | **72** | Hand-written Python; DRAFT schemas used live; two grant shapes |
| Harness manifests / freeze | T7, `A-11` | **78** | `vg-table-default` orphan |
| Model adapters + `Result` errors | `CT-33` | **80** | — |
| Governance processes | `ADR-0050` | **55** | Replay depends on events nobody writes (D-13) |
| Privileged approvals | `ADR-0057` | **60** | Challenge/verify exist; not ledgered |
| Competence / memory pipeline | VG-06 | **12** | `Claim` type + prior event |
| Promotion / evolution plane | VG-07 `M-21`–`M-24` | **0** | Honoured absence |
| Measurement doctrine (incl. `tools/telemetry/`) | VG-07 | **45** | Outside packages; no published A/A floor; Q3 why-not filed |
| Boundary / TCB / broken CI | VG-01, VG-08 | **85** | `CI-9` non-gating; ID family split |
| Self-modification / updater | `SA-*` | **0** | Honoured |
| Generality lint `ADR-0060` | `M11` | **70** | `coding_session` in domain |

**Backend core suitable for a coding harness (dispatch + episode + manifests + git + evaluator + lattice): ~70%.**
**Backend as VG-06/07 competence runtime: ~15%.**
**Phase 0 VG-08 “in” list: ~65%, with Increment C (`H0`) failed.**

### 3.2 Phase 0 tickets (`TK-00`…`TK-12`) vs code

`TK-*` never appear in `vanguard/packages/`. Substance:

| Ticket | Score | Note |
|---|---|---|
| TK-00 repo/CI/boundaries | **90** | Closed package set extra |
| TK-01 schemas/JCS/vectors | **75** | DRAFT used live; Python not generated |
| TK-02 grants/selectors | **80** | Two grant shapes |
| TK-03 budget/leases | **80** | Second USD controller at runtime |
| TK-04 store/reducer | **85** | Kinds under-emitted |
| TK-05 recovery | **70** | D-14 |
| TK-06 broker/dispatch | **80** | Provenance unwired |
| TK-07 secrets/redaction | **55** | Export redaction exists; AT-12 absent |
| TK-08 perimeter | **55** | D-31, D-32 |
| TK-09 evaluator identity | **75** | D-02 |
| TK-10 e2e fake+provider | **70** | Live tool-call still TODO on the board |
| TK-11 git/coding | **75** | Coding win not claimed |
| TK-12 TableWorld | **20** | Fails `H0` |

### 3.3 Living board (v0.4.5-beta) — honesty filter

From `docs/scrum/roadmap_backend.md`, backend-relevant:

| Claim | Board | Diagnostic |
|---|---|---|
| S10-A-01…04, ADR-0067, spawn, packs, IndexPort | `[DONE]` | **Match** ASBUILT |
| Waves 11–13 MOCK loop / DNA / prove | `[DONE]` | **Match** as MOCK; not a live coding win |
| PO acceptance | `[DONE]` (honest) | Live tool-call, Q2, spend still TODO — **do not treat as product-complete** |
| Playbooks | deferred | **Match** D-36 |
| Competence graph | “do not start” | **Match** D-39 |
| Q2 live dogfood | `[TODO]` | **Match** |
| Merge/ship | `[TODO]` | Multi-action proposal still a builder, not a win |

v0.5.0 is not “finish VG-06”. It is “make v0.4.5’s kernel tell the truth, then freeze the spec to the ADRs the code already implemented.”

---

## 4. v0.5.0 Refactor Action Plan & Directives

### 4.1 PRESERVE (do not rewrite)

Lift these into v0.5.0 as the trusted core. Change only by ADR.

| Unit | Path | Why |
|---|---|---|
| Package lattice + closed set + evaluator ban + subprocess allowlist | `tools/check_boundaries.py` | Real `LT-*` + extras that should become spec |
| TCB tripwire | `tools/check_tcb_budget.py`, `kernel/` nine files | 1,333 / 1,438 is the only honest size gate |
| Must-fail runner | `tools/run_broken_tests.py`, `test/broken/` | Keep the 38 cases; migrate IDs (4.3) |
| Dispatch sequence | `kernel/dispatch.py` | S1–S12, K-04…K-08, K-47 |
| Attenuation + sealed scopes | `kernel/attenuation.py`, `kernel/policy.py` | `K-26`, `ADR-0067` |
| Grants HMAC / descriptor binding | `kernel/grants.py` | `K-18`–`K-20` |
| Classifier as a call | `kernel/classifier.py` | `K-08`/`K-32` |
| Provenance **library** | `kernel/provenance.py` | Wire it; do not rewrite it |
| Selector inclusion | `domain/selectors/resource_selector.py` | `K-48`/`CT-52` |
| JCS + digest | `domain/canonicalisation/` | `CT-09`, `D-1` |
| Envelope parse + scope discriminator | `domain/wire/contracts.py` | `MF-35` property |
| Context L1–L5 compiler | `agency/context/` | Breakpoint ceiling, brief in L4 |
| Episode engine loop + terminals | `agency/episode/` | Two axes, `ADR-0057` |
| Spawn fail-closed | `engine.py` spawn | Keep; add `child_return` |
| FrozenHarness | `domain/artifacts/manifest.py` | `A-11` |
| Git environment eight methods | `adapters/environment/git.py` | — |
| Rootless probes + fake visibility | `adapters/sandbox/` | `K-42`–`K-44`, `K-46` |
| Isolated evaluator double probe | `adapters/evaluators/isolated.py` | `V-09` |
| WAL store + JSONL export | `adapters/stores/` | `CT-40`/`CT-42` |
| Inbox/outbox | `runtime/service/inbox.py` | `ADR-0062` |
| Schema-driven translator | `adapters/models/invocation.py` | `S10-A-01` |
| Tier escalation *around* repair | `runtime/tier_escalation.py` | Not a second loop |
| Integer telemetry | `runtime/telemetry.py` | `CT-06`/`CT-07` |
| `publication_decision` | `ports/sandbox.py` | `K-44` |
| Measurement **outside** packages | `tools/telemetry/`, `lab/` | `CL-1`/`LT-8` |
| `REQ-*` PR gate | `tools/check_pr_requirements.py` | D-45 |

### 4.2 DISCARD or stop pretending

| Unit | Action |
|---|---|
| Production story that `S1(e)` holds | Stop claiming it until D-05/D-06 are fixed |
| `EVENT_KINDS` as an enforced protocol | Either enforce on write or delete the “minimum set” claim |
| `MF-01`…`MF-37` as live test IDs | Replace in VG-08 with the `test/broken/` roster, or add aliases |
| `CI-9` as a green gate | Make it fail, or retarget it at live IDs |
| TableWorld as `H0` witness | Either implement `EnvironmentAdapter` + register the pack, or drop Increment C from Phase 0 exit |
| `RegroundPolicy` as a shipped control | Wire it or delete the module |
| `GrantIssuer.revoke` as `K-49` | Call it and emit, or remove the API |
| README LEVEL 0–9 hierarchy | Delete (`REJ-10`) |
| README paths `coordination.py` / `sqlite_event.py` / `fs_blob.py` | Fix |
| `MetaLoopEngine` / `runtime/loops/` | Stay deleted |
| MCP as an authority path | Stay rejected (`ADR-0066`) |
| Operators, playbooks, competence graph, promotion, parallelism, updater | Stay out of v0.5.0 core (honour DEF/REJ) |
| Dual `CompetenceArtifact` VG-04 shape | Do not resurrect; freeze T1.8 or a new ADR |
| Universal grants for `pure`/`observation` | Do not revert `ADR-0051` |
| Evaluator inside the worker mount (`K-40` as written) | Do not restore |

### 4.3 RESTORE from `docs/01_specs/backend` / `docs/main_v4` (code + spec)

**Code (composition and emit — small, mandatory):**

1. Wire `receipt_labeller` so tool results become `UNTRUSTED_EXTERNAL` spans and `advance_turn` runs (`K-33`).
2. Call `Accumulation.child_return` from `spawn()`.
3. Emit `EpisodeStarted` at run start from `vanguard/packages/` (not CLI fixtures).
4. Persist `ApprovalResolved` on the ledger when `_cmd_ResolveApproval` succeeds; let `ProcessEngine` replay it.
5. Emit `CapabilityGranted` at S6, `BudgetReserved`/`BudgetCommitted` around S7/S10, or cut those kinds from the minimum set by ADR.
6. Reject unknown `payload.kind` **or** add `EffectRejected`/`KernelAlarm` to `EVENT_KINDS`.
7. Move `domain/ledger/coding_session.py` out of `domain/` (or generalise the projection) so `M11` is literally true.
8. Register `vg-table-default` or delete the pack; do not leave orphans.
9. Publish a bijection `MF-01`↔`MF-KRN-001` etc., then make `rule_test_map.py` fail CI on gaps **or** change `CI-9` to the live roster.

**Spec text (edit VG, do not re-implement the old sentences):**

1. Amend `A-03` / VG-05 §2.1 to `ADR-0051` sink-class mediation (X-01).
2. Put `runtime/governance/` into VG-03 `LT-*` (X-03).
3. Rewrite `K-40`: evaluator is a **separate** identity; worker must not read it.
4. Alarm set includes `F-21a` and `F-24`.
5. Freeze port names to the as-built roster (D-20).
6. Freeze `Trust` five-value enum as the instruction-authority axis (Y-01, X-05).
7. Specify `ProposalTranslator` + `aliases.json` as the model waist.
8. Specify inbox/outbox (`ADR-0062`).
9. Replace VG-08 §5 IDs with `test/broken/manifest.json` (Y-10).
10. Record `DEF-03`/`DEF-11`/`DEF-12` as partially superseded.

**Must not be restored as written:** `K-40` same-perimeter evaluator; `ADR-0007` parallel-from-first-commit; `MF-01`…`MF-37` as the only must-fail namespace; TypeScript control plane (`ADR-0001`, reversed by `0063`).

### 4.4 Suggested v0.5.0 sequencing

| Wave | Outcome | Closes |
|---|---|---|
| **S-truth** | Provenance wired; lifecycle events emitted; `EVENT_KINDS` enforced or updated | D-05, D-06, D-11…D-15, D-18 |
| **S-spec** | VG-02/03/04/05 patched to ADRs the code already follows; MF ID bijection; `CI-9` honest | D-04, D-25, D-32, D-44, X-* |
| **S-waist** | One grant shape; coding projection out of domain; TableWorld decided (adapter or cut) | D-21, D-27, D-42, H0 |
| **S-perimeter** | AT-12 or documented deferral; rlimits from lease if cheap; seccomp only if a profile is reviewable | D-31, D-33 |
| **S-product** | Live tool-call / Q2 from the existing harness — **no new ontology** | Board TODOs |

Do not open a competence-graph or operator-registry wave until S-truth is green. A graph on top of an unwired predicate is how v0.4.x got a `Claim` type and no pipeline.

### 4.5 Explicit non-goals for v0.5.0

- Ground-up kernel rewrite
- Playbooks, operators-as-data, promotion/canary, independence groups
- Moving `lab/` or `tools/telemetry/` into `vanguard/packages/`
- GUI/TUI as a backend gate
- Restoring `K-40` as “evaluator in the same bubblewrap”

---

## Appendix A — Event emit scoreboard (copy from ASBUILT §3.13.2)

Production emitters in `vanguard/packages/` only:

**Written (11):** `EpisodeCompleted`, `ProposalProduced`, `AuthorizationDenied`, `BudgetReleased`, `EffectStarted`, `EffectCompleted`, `EffectReconciled`, `CompetencePriorRecorded`, `ApprovalRequested`, `RunRecovered`, `RunAborted`

**Declared only (23):** `EpisodeStarted`, `EpisodeStateChanged`, `ObservationRequested`, `ObservationProduced`, `OperatorSelected`, `OperatorInvoked`, `AuthorizationRequested`, `CapabilityGranted`, `CapabilityRevoked`, `BudgetReserved`, `BudgetCommitted`, `EffectPreviewed`, `ConflictDetected`, `EvaluationRequested`, `EvidenceClaimProduced`, `ArtifactCreated`, `ActivationChanged`, `ApprovalResolved`, `Heartbeat`, `CandidateBuilt`, `CandidateAttested`, `CanaryPromoted`, `RollbackTriggered`

**Written, not in `EVENT_KINDS` (2):** `EffectRejected`, `KernelAlarm`

## Appendix B — Honour table (deferrals and rejections)

Do not file these as v0.5.0 “gaps” unless the board reverses them.

Honoured DEF: `DEF-01` canvas, `DEF-02` semantic memory, `DEF-05` systems index, `DEF-06` engines, `DEF-07` updater, `DEF-08` public benches, `DEF-09` training, `DEF-10` discovery doc.

Partially superseded DEF: `DEF-03` spawn, `DEF-04` IndexPort only, `DEF-11` extra compaction strategies, `DEF-12` privileged approval.

Honoured REJ: `REJ-01`…`REJ-09`, `REJ-11`, `REJ-12`, MetaLoopEngine, MCP-as-authority.

Violated REJ: `REJ-10` (README only).

---

*End of Phase 3. THEORY and ASBUILT remain the section-mirrored pair; this file is the decision record for what v0.5.0 keeps, wires, amends, and refuses to rebuild.*
