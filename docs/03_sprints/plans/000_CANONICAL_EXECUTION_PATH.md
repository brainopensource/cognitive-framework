# The Canonical Execution Path — developer mental model

**Status:** Non-normative orientation. Law is `docs/SPEC.md` + ADRs (esp. `0069`–`0076`) +
`docs/04_annex/`. This file exists so a senior developer can hold the whole machine in their head
and knows **which file wins** when two look similar. If this file disagrees with SPEC/ADRs, they win.
**Read order for a new senior dev:** this file → `docs/SPEC.md` §§0–3 → `docs/04_annex/KERNEL.md`
§2 → ADR `0076` → your wave plan in this directory → the code it names.

---

## 1. Production truth (reuse; do not rebuild)

| Concern | Canonical artifact | Status |
|---|---|---|
| Effect authority (S0–S12) | `vanguard/packages/kernel/dispatch.py` (+ `grants`, `budget`, `attenuation`, `classifier`, `policy`, `provenance`) | **Mature.** Semantic oracle. 95 tests. Do not fork, do not "port". |
| Selector algebra | `vanguard/packages/domain/selectors/resource_selector.py` (`parse_selector`, `decide`) | **Mature.** The ONLY inclusion relation (ADR-0076 §2). |
| Canonical bytes | `vanguard/packages/domain/canonicalisation/jcs.py` | **Mature.** The ONLY digest/signing byte source (ADR-0076 §3). |
| Durable ledger store | `vanguard/packages/adapters/stores/event_store.py` (SQLite WAL + FULL sync) | **Mature.** Keep. |
| Turn loop + spawn | `vanguard/packages/agency/episode/engine.py` (`EpisodeEngine`, attenuated `spawn()`) | **Mature.** Canonical recursion primitive (ADR-0070). |
| Exterior judge | `vanguard/packages/adapters/evaluators/daemon.py` + `signing.py` (UID 10002, Ed25519, nonce handshake) | Mature process identity; **verdict binding + ledgering incomplete** → Wave 1. |
| Context compile | `vanguard/packages/agency/context/` (L1–L5, compaction) | Mature. |
| Model adapters + translator | `vanguard/packages/adapters/models/` (`invocation.py` ProposalTranslator, ollama, openrouter, cassette, fake) | Mature; F-21 lifting gaps → Wave 1. |
| Sandbox | `vanguard/packages/adapters/sandbox/` (rootless bwrap, UID 10001) | Mature. |
| Composition root | `vanguard/packages/runtime/root.py` (1418 LOC: `Runtime.compose`, `HarnessSession`, `LedgerBridge`, port bridges) | Works; split **in place** in Wave 2 along exactly those class seams. |
| Wire contracts | `schemas/mhf/*.schema.json` → generated types via `tools/codegen/generate_types.py` | Contracts updated (ADR-0076); generated file stale (F-13, Wave 0/1). |
| Plugin wire + lifecycle | `layer0/spi/jsonrpc.py`, `layer0/registry/` (FSM, broker), `layer0/compose/` digest **shape** | **To absorb into packages** (Wave 2/3). Contracts good; runtime around them is not. |

**Not production truth, never extend:** `layer0/kernel/`, `layer0/scheduler/driver.py` (fabricates
verdicts — defect F1), `layer0/events/MemoryLedger`, `layer0/spi/ceiling.py`'s private subset logic.
These are deleted at the Wave-2 parity gate. Writing new code against them is wasted work.

---

## 2. The one flow (Wave-4 target; every wave hardens a segment of this)

```text
harness.yaml (packs/code-default)                            [composition]
   │  compose(): resolve plugin refs → verify ceilings (INTERSECTION, fail-closed)
   │             freeze L1–L3 → FrozenHarness, D_H = JCS(full composition)   ← Wave 1/3
   ▼
HarnessSession (runtime)                                     [decision plane]
   │  EpisodeEngine turn loop: observe → propose → authorize → effect → receipt → evaluate
   │    model (ollama/openrouter adapter) → ProposalTranslator → EffectRequest
   ▼
Kernel.dispatch S0–S12                                       [authority]
   │  S5 policy → S6 grant (descriptor-bound) → S7 lease → S8 verify → S8a durable intent
   │  S9: OBSERVATION/ADVISORY direct; PRIVILEGED via sandbox cell (bwrap, UID 10001)
   ▼
LedgerEmitter → SQLite WAL event store                       [state plane]
   │  mhf.event/1 envelopes: lineage + prev_digest chain per project_id
   │  State = fold(events); cold replay must reconstruct grants/budgets/approvals/FSM (I-4)
   ▼
EpisodeCompleted ─→ EvaluationRequested ─→ evaluator daemon (UID 10002)   [evidence plane]
   │                                        signs SignedVerdict (bound: request/subject/oracle/nonce)
   │              evaluator gateway appends VerdictRecorded (sole legal writer)
   │              agent-side gate READS the ledgered verdict → PASS/RETRY/ESCALATE/ABANDON
   ▼
mhf.trajectory/1 emitted at EpisodeCompleted                 [dataset]
```

Planes never blur: the **decision plane** (session/engine/kernel) chooses; the **state plane**
(ledger + pure reducers) is the only truth; the **evidence plane** (exterior daemon) is the only
source of verdicts. Subagents are the same machine: `spawn()` = same `Principal` type with
`parent_id`, capability ⊆ parent, typed budget ≼ remaining(parent). Plugins speak JSON-RPC/UDS;
`in_process` is a privilege that still speaks the wire. Sequential scheduling (I-11) until a
measured gate says otherwise.

---

## 3. Decisions already settled — do not redecide locally

1. Envelope: `mhf.event/1` extended with lineage; v4 dataclass is read-path legacy (ADR-0076 §1).
2. Selectors: domain algebra only; `proc://…` is `generic`; no `process` kind (ADR-0076 §2).
3. Bytes: domain JCS everywhere; `signing.py`'s `json.dumps` is a Wave-1 fix (ADR-0076 §3).
4. `D_H`: computed over the full composition at compose; `FrozenHarness.composition_digest`
   (episode-scoped) is not it (ADR-0076 §4).
5. Verdicts: bound `SignedVerdict` schema; gateway-only `VerdictRecorded`; gate reads, never
   writes (ADR-0076 §5).
6. Writers: one `LedgerEmitter`, role-scoped facades; no generic append (ADR-0076 §6).
7. Budget algebra: additive `{usd_micros, tokens, bytes, charged millis}` vs structural
   `{depth, turns}`; `None` bounds fail closed (ADR-0074 §2).
8. Scope: no third tree, no Rust, no hot-swap, no evaluator-as-plugin, no concurrency, no
   Meta-Harness — see SPEC §9 and the `002` register's deferred table before proposing anything.

## 4. Where responsibility lives (target end-state)

- `domain/` owns value semantics: selectors, JCS, envelope/verdict/trajectory generated types, reducers.
- `ports/` owns interfaces only. The SPI Protocols land here when absorbed (Wave 2).
- `kernel/` owns authority. It gains **nothing** in Waves 1–4 except tests (TCB ≤ 1438 LOC stands).
- `agency/` owns the turn machine and spawn. Trajectory assembly hangs off episode completion here.
- `runtime/` owns composition (`compose`), session, `LedgerEmitter`, governance, recovery, listener.
- `adapters/` owns the outside: models, sandbox, evaluator client/daemon, stores. Never imports kernel/agency.
- `packs/` + `apps/` own every coding-specific token (I-7). The kernel stays domain-blind.

Evidence of done, per wave, lives in the wave plans in this directory and in
`docs/02_roadmap/milestones.md`. A milestone is complete when its falsifiers pass, not when its
code exists.
