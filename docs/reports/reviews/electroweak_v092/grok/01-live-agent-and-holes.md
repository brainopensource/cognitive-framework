---
id: report.electroweak-v092.grok.live-agent
canonical_id: report.electroweak-v092.grok.live-agent
class: report
authority: non-canonical
truth_plane: AS_BUILT
status: snapshot
implementation_status: NOT_AUTHORIZING
owner: grok-principal-architect-review
purpose: Forensic picture of the live coding agent at pin HEAD — tools, gate, context, state, holes vs hard SWE.
audience: [architect, release-owner]
last_verified: "2026-09-04"
pin_head: "5243866bc169c7f60cc7d4f74b9a853f60356381"
relationships:
  - report.electroweak-v092.grok.index
  - execution.tasks
  - execution.feature_spec
---

# 01 — Agent as it is

Pinned subject: `5243866bc169` on `feat/strongforce_beta_release_v093`.
Tests were **not** run. Nothing in this file is `PASS`.

## 1. One picture

The product coding agent is not a class hierarchy. It is **pack + profile +
tools + admission** over one loop (FACT: `docs/execution/spec.md` substrate
sentence):

```text
L1–L3 frozen prefix → L4 brief + pinned σ → L5 dialogue
        │
        ▼
 model proposes exactly one effect
        │
        ▼
 Kernel S0–S12 (domain-blind) → GitEnvironment / proc.exec
        │
        ▼
 ingest receipt → distill tool body → refresh epoch/index → fold σ
        │
        ▼
 finish? → completion_admitter → AdmissionGate / pack policy ← VerificationReceipt
```

Composition path (FACT): `ApplicationService → HarnessSession → EpisodeEngine →
Kernel.dispatch`. CLI/TUI is a client. Forge/Chimera exist under
`vanguard/packages/agency/forge/` and `agency/chimera/` and are **not** the
product path (T-23 `[x]`). Do not score them. Do not grow them.

## 2. Tools, arms, patch path

**Product arms.** `vg-code-fast`, `vg-code-balanced`, `vg-code-max` declare the
same four verbs: `fs.read`, `fs.search`, `patch.apply`, `proc.exec` (allowlist
`git,pytest,ruff,python3`). FACT: the three manifests differ only in
`"harness"` name (`vanguard/packages/agency/manifests/vg-code-max/manifest.json`
and siblings). They reuse `vg-code-default` prompt, tools, context/routing/
approval, and **one** skill (`pytest-green`). Arms are **aliases**, not
phenotypes.

Coding semantics live in `packs/code-default/` (fs, AST-patch toolkit, index,
verify, greenfield) **and** in the runtime adapters the kernel actually calls.

**Patch path that actually mutates the tree.** Manifest `patch-tool.json` is
unified-diff **or** whole-file `content`. `GitEnvironment.apply` parses unified
diffs with strict preimage matching (`adapters/.../git.py` ~631–666); multi-file
planned sets go through 2PC (`git.py` ~899–916 → `transaction.py` ~50–70);
**single-file writes are sequential and still succeed with a syntax observation
receipt** (`git.py` ~918–950). Pack `AstPatchToolkit`
(`packs/code-default/toolkits/ast_patch.py`) is a plugin SPI that writes
immediately; it is **not** the kernel product path. Kernel has **no**
`ast.parse` (FACT: `rg ast.parse vanguard/packages/kernel` empty; I-7).

**One effect per turn** is both a kernel law and a prompt law
(`packs/code-default/system-prompt.txt`). A chatbot with `patch.apply` is this
agent when admission is exempt.

## 3. Gate

`AdmissionGate` / `VerificationReceipt.passed` = `exit_code == 0` **and**
`executed_test_count > 0` (`admission_gate.py`). Session parser returns `0` for
unknown runners (`session.py`). `finish` is retried, not auto-completed, when
the admitter rejects (`episode/engine.py`).

**The exemption that kills \(R\) on the default pack** (FACT):

```python
# vanguard/packages/runtime/session.py ~134–148
ADMISSION_GATE_EXEMPT = frozenset({"vg-code-default", "vg-code-lex"})
def admission_required(harness: Any) -> bool:
    ...
    if name in ADMISSION_GATE_EXEMPT:
        return False
    return "patch.apply" in set(getattr(harness, "verbs", ()) or ())
```

`ADMISSION_GATED_HARNESSES` is defined and **unused**. Product arms **are**
gated (they are not exempt). `vg-code-default` can `finish` with zero effects.
T-04 is `[PROPOSAL]` until an RF-25 successor baseline
(`docs/execution/tasks.md`, `milestones.md` MS-TRUTH still `OPEN` on
T-04/T-05/T-07).

## 4. Context and state

**Compiler.** One `ContextCompiler`. L1–L3 frozen at construction. Compaction:
recency / result-eviction; pinned L4 sources `settled-invariant` /
`falsified-hypothesis` / `dead-end`. Distiller caps tool bodies at 2k chars.
Packet epoch + omission ledger refuse `completed` if stale/truncated.

**IndexPort** is observation only — “ranks nothing” (`ports/index.py`). Methods:
`index/files/symbols/dependencies/tests/repo_map`. **No `callers()` on the
port.** Reverse deps must be derived from `dependencies()` in pack policy, not
smuggled in as ranking.

**State.** `SemanticTaskState` + `fold_task_state` (MS-RESUME `CLOSED`).
Session refreshes σ after write/verify. Fold *can* consume `HypothesisOpened`
etc. Whether those events are actually emitted on the product path is a
separate honesty question — do not assume the fold is densely populated.
`technical.md` §21.1 still says resume dumps σ into L3; board says T-12 `[x]`.
Trust `tasks.md` / MS-RESUME CLOSED over the stale handbook sentence.

**Skills.** Skill **names** in L3; bodies on `fs.read` (T-56 shape). Product
skill: `pytest-green` only.

**Phase ladder.** Only if the harness directory has `tool-policy.json` with
`"mode": "phased"`. Product `vg-code-{fast,balanced,max}` directories have
**no** `tool-policy.json` → `preset_mode=None` → ungated loop. `vg-code-max-v3`
is phased. T-23 says product arms ⊆ `{fast,balanced,max}` — so the phased
ladder is **not** the product path. Phased `inspect` also forbids `proc.exec`
until after `patch.apply`, which would **break** fail-to-pass reproduce-first.
Do not turn it on blindly.

## 5. Mechanisms vs wired into admit

| Mechanism | Where | Wired into session admit? |
|---|---|---|
| Epoch + refresh after write | `session.py`, `packet.py` | Yes, **if** admitter runs |
| L4/L5 policy + distiller + omission ledger | compiler / packet T-15/T-36/T-37 | Yes, **if** admitter runs |
| 2PC | `transaction.py` via git multi-file | Multi-file only |
| Tamper module | `tamper_shield.py` | **No.** `rg TestTamperShield` in `session.py` empty. Matches `spec.md`. |
| Vacuous-oracle / greenfield policy | `greenfield.py`, pack `multi_file_completeness.py` | Policy exists; session supplies **incomplete** `greenfield_evidence` (no `oracle_failed_on_stub`) |
| Implicated-set | `implicated_files.py`, completeness | Session does **not** pass `implicated_files` / `callers_by_symbol` |
| Dialect recovery | engine `protocol_decoders` | Yes, as retry |
| Resume σ | T-09–T-13 `[x]` | MS-RESUME CLOSED |
| Meta controller | `meta_controller.py` | Powerless advisor: cannot admit `completed`, cannot enlarge budget. FACT. |
| Memory SPI | `ports/memory.py` | Product wiring gated (T-32) |
| Campaign / outer loop | `runtime/campaign/`, `runtime/outer_loop/` | **Absent** |

MECHANISM ≠ CLOSED. MS-TRUTH, MS-SEE, MS-CHANGE, MS-CONTROL remain `OPEN` on
named leftovers (`milestones.md`).

## 6. Holes vs hard SWE

Hard software engineering this review is scored against:

- **Greenfield:** empty tree, many files, vacuous tests, no callers, no
  failing oracle unless you write one.
- **Brownfield:** multi-file blast radius, signature changes, callers you did
  not open, tests you did not run, tests you mutated.
- **Long context:** 100+ turns without goal amnesia.
- **Long runs:** hours, crash, resume, many episodes — not one 400-turn
  transcript.

### 6.1 Lying `completed`

Default pack exempt. Even gated arms: tamper unwired; implicated callers not
in admit; greenfield evidence mapping is a stub; T-07 typed verification
subject open (`python3 -c 'print("OK")'` still a hole). Session parser
returns `0` for unknown runners — invented-count-adjacent.

**Fixes \(R\)** only if `finish` cannot fire on prose.

### 6.2 Greenfield

Prompt says “write ONE file per turn… Do not read or search first”
(`packs/code-default/system-prompt.txt`) while greenfield policy requires
scaffold baseline + smoke test + **oracle failed on stub**. Those two laws
fight. Vacuous tests that pass on `pass` / `NotImplemented` are rejected
**only if** the policy sees `oracle_failed_on_stub`. Session currently sets
`structural_passed` = `behavioral_passed` = `verification.passed` and never
sets the stub-fail fact.

### 6.3 Brownfield blast radius

Index has import edges; implicated-set builder exists; session never feeds it.
Completeness then treats `surface = changed`. A 40-file signature change can
“complete” after editing one file and running an unrelated pytest. Tamper
unwired ⇒ the agent can edit the assertion instead of the code.

### 6.4 Long context

Compaction is recency + receipt stubs, not Claude-Code-style re-injection of
plan/files from disk. Goal echo is a 240-char tail. σ exists, but if
Hypothesis/DeadEnd events are sparse, L4 pinning has nothing to pin.
Prefix-stable L1–L3 is the right cache law; **no** product telemetry of
`cache_read` / `cache_write` was found. Distiller binds a digest — the model
must `fs.read` to recover; digest ≠ memory.

### 6.5 Long runs

Resume identity is CLOSED. Campaign director does not exist. Crash after hour
6 is “new episode with restored σ”, not a DAG. Operator interrupt UX
(`cancel`, checkpoint) is T-59 `[PROPOSAL]`. Duplicate writes on resume are a
durability problem the board already names; do not paper over it with a
second engine.

### 6.6 Edit brittleness

Strict unified-diff preimage; no T-47 ladder (exact → whitespace → indent →
fuzzy). Conflict is `Result.fail("conflict", ...)`. No typed
`PATCH_PREIMAGE_MISMATCH` recovery in the engine — the model just sees a
failed effect and often retries the same hunk. `AdmissionGate` rejects
`MODIFIED_FILE_NOT_INSPECTED` **at finish** — too late: the workspace is
already dirty.

### 6.7 Stale forensics in lock files

`.draft/todo/SOTA_CODING_HARNESS_ENGINEERING_ROADMAP.md` cites
`episode/compactor.py` and `EpisodeEngine.step()`. Those files/methods are
**not** in this tree. Compaction lives in `agency/context/compaction.py`.
Treat the roadmap as intent, not HEAD.

`docs/research/coding_harness/future_improvements_sota_harness_2808.md` badges
C-01–C-08 as “RATIFIED” with invented KV-cache hit rates. Those badges are
**research fiction** at this pin. AST preflight exists in the **adapter** 2PC
path; prefix-stable compiler exists; SBFL/PageRank/MCTS/SWE-RL are not
product.

## 7. What “Coding Max” actually is

`apps/` is a thin façade. `CodingMaxFacade` selects a composition. The
smallness is load-bearing: if a new agent type required a large app layer,
the substrate would have failed to generalise. Dual mission
(`milestones.md`): (1) Coding Max on one `EpisodeEngine` path; (2) same
substrate for other agents.

Today (1) is a **gated four-verb loop with a lying default pack** and (2) is
real as composition (manifests, packs, ports) but not as product
differentiation (three identical arms).

That is the agent as it is.
