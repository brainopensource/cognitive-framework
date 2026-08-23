# AETHER Version 6 — Foundation Roadmap and Gap Register

**Classification:** Engineering Director / Chief Engineer review packet.  
**Status:** Authoritative **operational** register after Concept Lock. Cannot contradict `docs/SPEC.md` or ADRs `0069`–`0074`.  
**Date:** 2026-08-20  
**Author role:** Principal Staff Engineer  
**Companion lock:** [GAMMA](001_V060_concept_phase_GAMMA.md)  
**Director review:** **APPROVED** 2026-08-20 (`ADR-0075`, [003](003_V060_DIRECTOR_REVIEW.md)) — **Wave 0 is authorized** and adds falsifiers F-18…F-21 below.  
**Production coding:** not started; the first authorized code change is Wave 0.

> This file is the one foundation roadmap and the one remaining-work register for AETHER Version 6.
> The forensic TODO is closed as investigation and was removed at Director consolidation
> (`ADR-0075`; git history `4f9f8b1`).
> Historical M0–M6 tables in `docs/02_roadmap/` are superseded as *next* work; they remain evidence.

---

## 0. Decision requested

Approve:

1. **Concept Lock** — `docs/SPEC.md` + ADRs `0069`–`0074` + annexes + GAMMA.
2. **This sequence** — gap register below, then Wave 0 → Wave 4, then stop.
3. **Hold** — no runtime refactor, CI rewire, plugin implementation, concurrency enablement, or third tree until that approval.

Reject if the destination should be a new `core/` / `vanguard/substrate/` / `aether-rust/` tree, `layer0/` as rewrite target, evaluator-as-plugin, or mid-run harness hot-swap.

---

## 1. Locked foundation (do not reopen without a new ADR)

| Concern | Lock |
|---|---|
| Runtime | Python 3.10+. Production lattice `vanguard/packages/` (`domain → ports → kernel → agency → runtime → adapters`; `apps/` is a client). |
| Dual tree | `layer0/` is a copy-fork to **absorb**. No third tree. |
| Machine | `Agent = Principal + HarnessInstance`. SubAgent = same Principal type with `parent_id`. |
| Spawn | Capability subset. Typed budget: additive `{usd_micros, tokens, bytes, charged millis}` vs structural `{depth, turns}`. Sibling depths are not summed. |
| Project | One ledger stream, one ceiling, one root budget. `project_id` is the consistency unit. |
| Identity | `D_H` = full behavior-affecting composition (plugins **and** system prompt, ceiling, approval policy, model routes). `D_R` / `D_X` must not collapse into `D_H`. |
| State | `Decision → DurableEvent → fold → EffectiveState`. Writer authority on privileged kinds. Hash integrity ≠ semantic truth. |
| Plugins | JSON-RPC 2.0 / UDS. Protocol is a client. Freeze at compose. `in_process` still speaks the wire. |
| Judge | Exterior signed evaluator. Fabricated `{verdict: "pass"}` is defect F1. |
| Execution | Sequential (I-11). `K` workers ≪ `N` logical agents. |
| CI | Packages are the subject of record. Lexical E-COV is not I-2. |
| Growth | New capability enters as plugin + manifest + policy + composition, not a core rewrite. |

Package version on disk remains `0.4.5b1` until a later release cut. Concept Lock version is **v0.6.0**.

---

## 2. Foundation vs deferred

### Must exist in the Version 6 foundation (through Wave 4)

- One runtime authority on `vanguard/packages/`.
- Fail-closed capability ceilings and typed spawn attenuation.
- Writer-scoped ledger; envelope lineage by construction.
- Cold replay from disk (I-4).
- Exterior signed, request-bound verdicts (I-5); F1 cannot complete a run.
- Complete `D_H` / `D_R` / `D_X`.
- `mhf.trajectory/1` schema + emission at `EpisodeCompleted` (I-9). Harvest/DPO not required.
- Wire-first plugin lifecycle on the canonical path (walking-skeleton echo plugin).
- Domain-blind kernel (I-7); coding behavior in pack/client.
- One real coding-agent E2E as the **stop condition**, not as a second architecture.

### Deferred (after Wave 4, or never as engines)

| Item | Disposition |
|---|---|
| Extra domain packs | After Wave 4 |
| Concurrency enablement | After selector-soundness + race tests (I-11) |
| Multi-agent / swarm **policy** | After Wave 4; never a swarm engine |
| Heterogeneous subagent graphs | After Wave 4 |
| Meta-Harness, promotion controller, DPO harvest productionization | Deferred (`ADR-0073`) |
| Self-updating release pipeline | Deferred (ADR-0019) |
| Model / sandbox as sixth SPI | Deferred |
| `model.infer` as kernel verb | Deferred |
| WASM-default isolation, remote attestation, multi-host, k8s, NATS | Deferred |
| Graph database, workflow DAG engine, competence graph | Refused as substrate |
| pytest-as-universal-runner | Deferred |
| Rust TCB rewrite | Deferred behind a **named** measured gate |
| Skill / Task / Orchestrator-as-engine / Experiment / Promotion / Cache as primitives | Refused |
| Mid-run FrozenHarness hot-swap | Refused |
| Evaluator as product plugin | Refused |
| Byte-identical concurrent ledger as general law | Refused |

---

## 3. Foundation roadmap (no calendar dates)

```text
Concept Lock (G1–G4) + this register     DONE
        ↓
Director / Chief Engineer approval       PASSED 2026-08-20 (ADR-0075)
        ↓
Wave 0   CI subject-of-record + named falsifiers   ← CURRENT (authorized, not started)
Wave 1   Irreversible substrate on the packages path
Wave 2   Converge in place (absorb; parity; then delete dupes)
Wave 3   Walking skeleton; pack extraction begins
Wave 4   One real coding-agent E2E        ← FOUNDATION STOP
        ↓
Only then: extra packs, controlled concurrency, multi-agent policy, lab, Meta-Harness
```

Do not plan every task. Each wave has an **exit gate**. A wave that is green by lexical grep is not done.

> **Execution decomposition (2026-08-20, post-approval):** milestone/sprint/task planning under
> these waves now lives in `docs/02_roadmap/{milestones,backlog}.md` and `docs/03_sprints/plans/`
> (canonical-artifact decisions: `ADR-0076`). This register remains the authority on outcomes,
> falsifiers, and the deferred/refused lists; the roadmap files may not contradict it.

### Wave 0 — Restore engineering truth

**Goal.** Living CI measures the production lattice and the bound falsifiers, not a self-signing fork.

Exit gate:

- `.github/workflows/ci.yml` runs `test/kernel` plus packages runtime/agency/adapters (quarantine env-sensitive Ollama cases).
- `generate_types.py --check` is a hard gate.
- Named falsifiers in §4 exist as tests (they MAY be red; red is honest).
- `tools/check_duplication.py` exists (threshold later; detector now).
- The stale sprint-6B archive citation no longer fails living CI's first step (F-20).
- A green `test/layer0` suite alone is **not** success.

### Wave 1 — Irreversible substrate (canonical path)

**Goal.** False gates cannot certify the trust spine.

Exit gate:

- Scheduler **reads** a signature-valid, request-bound verdict; F1 cannot complete an episode.
- Compiler stores capability intersection; empty ceiling denies; prompt/policy/routes enter `D_H`.
- Every envelope carries lineage; `LedgerEmitter` cannot drop `episode_id` / causation.
- `mhf.trajectory/1` on disk; emitted at `EpisodeCompleted`.
- One selector algebra; unbounded child under bounded parent is deny.
- Writer-scoped append for privileged kinds.
- Receipt carries `lease_id` and `grant_digest`.

### Wave 2 — Converge without a third tree

**Goal.** One identity. Packages stays. Layer0 contracts move *in*.

Exit gate:

- SPI / JSON-RPC / lifecycle FSM / compose digest shape live on the packages path.
- Behavioral parity gate, **then** delete duplicated layer0 kernel/scheduler/mocks.
- `root.py` split **in place** (compiler / session / ledger bridge / wiring), not a new tree.
- Duplication detector fails a second selector algebra.

### Wave 3 — Extensibility foundation

**Goal.** New capability enters mainly through abstractions, plugins, manifests, policies.

Exit gate:

- Manifest → Resolve → Verify → Freeze → FrozenHarness on packages.
- Echo plugin traverses DISCOVERED → RETIRED over UDS (ADR-M0-13).
- Coding-specific behavior continues extracting into `packs/` / `apps/`; I-7 holds on `layer0/` **and** `vanguard/packages/{domain,kernel}/`.

### Wave 4 — Foundation E2E (stop)

All must be true on **one** path:

| Required | Meaning |
|---|---|
| Real model | Not a stub planner |
| Authorized effect | Kernel grant + lease, not ADVISORY-only |
| Filesystem change | Durable, receipted |
| Sandbox | Untrusted exec contained |
| Exterior signed eval | No unsigned pass |
| WAL ledger | Packages store, not MemoryLedger |
| Cold replay | Reconstruct from disk |
| Trajectory | Schema-valid `mhf.trajectory/1` |
| One runtime authority | No competing scheduler/kernel |

**Do not** start extra packs, swarm policy, concurrency enablement, or Meta-Harness before this gate.

---

## 4. Authoritative gap register

Statuses: `DONE` (this docs wave) · `TODO` (authorized after director approval) · `BLOCKED` (waiting on that approval) · `DEFERRED` · `WONT`.

### 4.1 Concept Lock and hygiene — DONE

| ID | Item | Status |
|---|---|---|
| L-01 | Forensic discovery (25 sections) | DONE |
| L-02 | Concept-lock prompt | DONE |
| L-03 | ADRs `0069`–`0073` | DONE |
| L-04 | ADR-0074 GAMMA amendments | DONE |
| L-05 | ADR INDEX + M0 rows; `0067` hole documented | DONE |
| L-06 | SPEC v0.6 self-review vs `0069`–`0074` | DONE |
| L-07 | KERNEL.md destination amendment; MEASUREMENT deferred note | DONE |
| L-08 | CLAUDE.md / AGENTS.md / sprint_active / review banners / roadmap banners | DONE |
| L-09 | This register | DONE |
| L-10 | Production coding / CI rewire | **NOT STARTED** (correct) |
| L-11 | Git commit | BLOCKED on explicit user/director request |

### 4.2 Bound falsifiers — TODO after approval (most currently fail on main; that is intended)

| ID | Locked concept | Falsifier | Wrong implementation | Wave |
|---|---|---|---|---|
| F-01 | Envelope lineage | `test_every_emitted_envelope_carries_full_lineage` | `LedgerEmitter.emit()` dropping lineage | 1 |
| F-02 | `State = fold(Events)` | `test_cold_reader_reconstructs_live_state_from_disk` | Folding the same in-memory list twice | 0/1 |
| F-03 | Evaluator exteriority | `test_scheduler_cannot_produce_a_verdict_without_a_signature` | `driver.py:138` fabricated pass | 1 |
| F-04 | Verdict binding | `test_replayed_or_unbound_signature_is_rejected` | Bare Ed25519 blob without request/nonce | 1 |
| F-05 | Writer authority | `test_orchestrator_cannot_append_privileged_kinds` | Generic `append(any Event)` | 1 |
| F-06 | Capability ceiling | `test_declared_ceiling_survives_compilation_and_denies` | `_parse` ignoring `capabilities:` | 1 |
| F-07 | Fail-closed authority | `test_empty_ceiling_denies_everything` | `if not capabilities: return True` | 1 |
| F-08 | Grant path | `test_privileged_verb_requires_a_bound_grant` | ADVISORY-only CI fixtures | 0/1 |
| F-09 | Spawn attenuation | `test_child_grant_wider_than_parent_is_denied_whole` | layer0 spawn stub | 1 |
| F-10 | Depth algebra | `test_sibling_depths_are_not_summed` | `Σ depth_child ≤ depth_parent` | 1 |
| F-11 | `D_H` completeness | `test_prompt_or_ceiling_change_changes_digest` | Digest over refs only | 1 |
| F-12 | Trajectory | `test_episode_completed_emits_schema_valid_mhf_trajectory_1` | Digest over `{ids, n}` | 1 |
| F-13 | Generated types | `generate_types.py --check` in CI | Hand-edited `DO NOT EDIT` file | 0 |
| F-14 | Durable intent (K-47) | `test_intent_survives_process_death` | `self.intents.append` only | 1 |
| F-15 | Budget lineage | `test_child_budget_debits_parent_remaining` | Independent child wallets | 1 |
| F-16 | No duplicate kernel | `tools/check_duplication.py` | Second selector algebra | 0/2 |
| F-17 | CI subject | living workflow runs `test/kernel` + packages suites | `test/layer0` as sole behavioural gate | 0 |
| F-18 | I-7 enforcement scope (`ADR-0075`) | `check_domain_blindness.py` scans `layer0/` **and** `vanguard/packages/{domain,kernel}/` | Linter narrower than the invariant it certifies | 0 |
| F-19 | Tests are collected (`ADR-0075`) | discovery collects `test/integration/` + `test/governance/` (add `__init__.py`) or retires them with a recorded reason | Silently uncollected test modules counted as green | 0 |
| F-20 | Oracle registry artifact (`ADR-0075`) | `preregistered_oracles.json` exists at a canonical path and `repo_paths` resolves it | Registry file deleted with the sprint-6B docs; tests error on a ghost path | 0 |
| F-21 | Translator lifting (`ADR-0075`) | `ProposalTranslator` lifts the `parameters` call spelling and fenced payloads per `test_model_invocation`, or the contract is re-scoped with P1-17 | Tool calls silently degrade to prose (`kind: "finish"`) | 0/1 |

#### 4.2.1 Ratified `RF-*` namespace and historical alias

> **Canonical register:** The living master RF falsifier allocation register is maintained in [`docs/05_adr/INDEX.md`](../../05_adr/INDEX.md#canonical-rf-falsifier-allocation-register) (governed by `check_falsifier_ids.py`). The table below is retained as historical ratification record.

`F-*` remains the historical kernel-control namespace. Existing `F-*` identifiers are never
renamed or reassigned, and no new proposal requirement may allocate one. Ratified roadmap
falsifiers use `RF-*`.

| Historical control | Ratified requirement | Relationship |
|---|---|---|
| `F-12` | `RF-23` | `F-12` retains the structural `mhf.trajectory/1` schema/emission check. `RF-23` strengthens it with invoked-turn attribution, explicit measurement status, conserved cost, and identity content. This is an alias/lineage edge, not a rename; both tests remain. |

| RF allocation | Owner | Locked subject / milestone |
|---|---|---|
| `RF-23`, `RF-24`, `RF-27` | ADR-0078 | NOVA-1 trajectory content, writer authority, and identity separation / M-2 |
| `RF-25` | ADR-0082 | NOVA-2 true fresh-process cold continuation / M-2 |
| `RF-26` | ADR-0080 + ADR-0067 | Sealed action membership remains denied when the engine pre-filter is bypassed / current behavior |
| `RF-28`–`RF-33` | ADR-0077 | Named Component Graph compilation and identity / M-3 |
| `RF-34`–`RF-37` | ADR-0079 | Absent-vs-forged and derived promotability / M-3–M-5 |
| `RF-38`–`RF-45` | ADR-0081 | Plugin lifecycle parity and NOVA-4 Layer-0 retirement / M-3 |
| `RF-46`–`RF-48` | ADR-0083 | Pareto profile identity, authority, and reservation / M-3 and M-7 |
| `RF-52`–`RF-53` | ADR-0084 | Attributable witness memo / M-5 |
| `RF-55`–`RF-59` | ADR-0080 | Capability-mediated `agent.spawn` / M-6 |
| `RF-65`–`RF-66` | ADR-0082 | Advanced topology fitness and the universal-loop challenge / M-8 |
| `RF-67`–`RF-70` | ADR-0084 | Macro least privilege, dispatch, and exact promotion / M-9–M-10 |
| `RF-72` | ADR-0082 | Identifier uniqueness linter and this one-time historical alias table / governance |
| `RF-73`–`RF-75` | ADR-0085 | Reservation identity, inert refusal, and ADR reversal-condition lint / staged milestones |
| `RF-76` | ADR-0082 | Compatibility-reader fidelity for supported old WAL rows / M-3 |
| `RF-77` | ADR-0082 | Index deletion and rebuild from immutable artifacts / M-9 |

RF-72 requires `tools/linters/check_falsifier_ids.py` to reject duplicate or semantically
conflicting allocations across accepted ADRs, SPEC, this register, and the active board. The linter
must expand inclusive ranges, permit repeated citations of the same allocation, and validate the
single `F-12` -> `RF-23` lineage row above. Unlisted IDs remain unallocated; adjacency grants no
meaning.

### 4.3 As-built vs law (thin G5 matrix)

| Surface | As-built | Law | Action |
|---|---|---|---|
| Production lattice | `vanguard/packages/` (WAL, evaluator, sandbox, S0–S12, spawn) | Canonical | Keep; CI must follow |
| `layer0/` | Copy-fork; MemoryLedger; F1; fail-open ceiling; spawn stub | Absorb SPI/broker/lifecycle/compose | Wave 2 after Wave 1 repairs |
| Living CI | `test/layer0` + packs + lexical tools | Packages + falsifiers | Wave 0 |
| `test/kernel` | 95 OK, not in living CI | Subject of record | Wave 0 |
| Full `test/` | Not green (env-sensitive + real defects) | Honest red allowed | Quarantine env cases; keep real reds until Wave 1 |
| E-COV “100%” | Lexical | Not I-2 | Demote to weak lint |
| `root.py` ~1418 LOC | God-object | Split in place | Wave 2 |
| Codegen `--check` | Stale / unwired | I-1 / A-4 | Wave 0 |
| `mhf.trajectory/1` | Missing / content-free digest | I-9 | Wave 1 |
| Dual selector algebras | Forked | One algebra | Wave 1–2 |
| Stale sprint-6B path | Living CI first step red | Hygiene (P1-15 / F-20) | Wave 0 |
| Phase 2/3 SPEC §§5–7 | Blueprint text | Deferred | Do not implement |
| Historical M0–M6 roadmap | layer0 destination, hot-swap, E-COV=100% | Superseded | Follow this file |

### 4.4 P1 items (lock vs implement)

| ID | Item | Classification |
|---|---|---|
| P1-1 | Envelope lineage | LOCKED; implement Wave 1 |
| P1-2 | Trajectory schema + emission | LOCKED; implement Wave 1 |
| P1-3 | Complete `D_H` | LOCKED; implement Wave 1 |
| P1-4 | Writer authority | LOCKED; implement Wave 1 |
| P1-5 | Typed budget algebra | LOCKED; implement Wave 1 |
| P1-6 | One generated `EffectRequest` | LOCKED as I-1; codegen Wave 0/1 |
| P1-7 | Walking skeleton on packages | LOCKED as sequencing; Wave 3 |
| P1-8 | `in_process` speaks the wire | LOCKED as rule; Wave 3 |
| P1-9 | Receipt `lease_id` / `grant_digest` | LOCKED as fields; Wave 1 |
| P1-10 | Split `root.py` in place | Wave 2 |
| P1-11 | Model/sandbox behind plugin wire | DEFERRED |
| P1-12 | `model.infer` as kernel verb | DEFERRED |
| P1-13 | Plugin TS conformance / pytest runner | DEFERRED |
| P1-14 | Concurrency enablement | DEFERRED |
| P1-15 | Stale sprint-6B archive citation | Wave 0 hygiene (with F-20) |
| P1-16 | Ollama unreachable vs `model_tag_absent` | DEFERRED (test isolation) |
| P1-17 | Selector `process` vs `generic` | Wave 0/1 contract |

---

## 5. How the foundation scales later

Keep the core small. Grow by composition:

```text
new capability → plugin + manifest + policy + FrozenHarness
                 (existing kernel, ledger, judge, scheduler)
```

Recursive agents reuse `spawn` (same Principal type). Many logical agents share a bounded worker pool (`K ≪ N`). Graphs and swarms are projections/policies over events, not engines. Measurement stays attributable because `D_H`/`D_R`/`D_X` and trajectories exist **before** promotion exists.

If a proposed feature needs a new engine, a new runtime tree, or a kernel rewrite, it is out of foundation scope until an ADR says otherwise.

---

## 6. Explicitly not started (hold list)

Do not begin until director approval **and** Wave 0 is the first code change:

- `.github/workflows/ci.yml` rewire
- F1 code fix
- Ceiling fail-closed implementation
- `layer0/` deletion or destination rewrite
- `root.py` split
- Plugin / echo-plugin implementation
- Concurrency
- Rust, WASM-default, distribution
- Meta-Harness / DPO / promotion controller
- New sprint dates or M1 “port into layer0” work from `docs/02_roadmap/`

---

## 7. Director checklist

- [ ] Law is SPEC + ADRs `0069`–`0074` + annexes.
- [ ] GAMMA P0s stand; advisory reviews are evidence only.
- [ ] This file is the only living foundation roadmap / gap register.
- [ ] Historical M0–M6 / Full Refactor / Aether waves / parecer `core/` are not competing plans.
- [ ] Working tree contains **no** Wave 0–4 implementation from this lock wave.
- [ ] Next authorized code is Wave 0 (CI truth + falsifiers), not a runtime rewrite.

**Approve** → Engineering may start Wave 0.  
**Reject** → name the P0 or wave to reopen; do not average with archived reviews.

> **Outcome (2026-08-20): APPROVED** — `ADR-0075`, [003_V060_DIRECTOR_REVIEW.md](003_V060_DIRECTOR_REVIEW.md).
> All checklist items verified against the live tree; F-18…F-21 added to §4.2; Wave 0 may begin.
