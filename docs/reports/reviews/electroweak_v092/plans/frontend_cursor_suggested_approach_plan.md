---
id: frontend-cursor-suggested-approach-plan
class: scratch
authority: non-canonical
status: draft
owner: product-frontend
audience:
  - principal-architect
  - staff-engineer
  - senior-frontend
  - technical-staff
created: 2026-09-03
supersedes: []
notes: >
  Ephemeral planning artifact. Not law. Not an ADR. Do not promote into
  docs/ until a live OpenRouter turn and a coding episode are observed.
---

# Frontend-led product closure: SOTA coding-agent control surface

> **For agentic workers:** implement task-by-task; do not claim PASS without a live LLM round-trip. This file is a Cursor-session synthesis, not repository authority. Canonical constraints remain `docs/SPEC.md`, `docs/decisions.md`, and `AGENTS.md`.

**Goal:** Make `aether` / `vg` behave like a serious coding agent (Claude Code / OpenCode / Hermes class): the operator types in the TUI, a real model runs through the hexagonal harness, tools mutate the workspace under policy, and the transcript shows answers, diffs, failures, and approvals.

**Architecture:** Keep the lattice (`domain ← ports ← kernel ← agency ← runtime → adapters`; `clients/` is a runtime slot). The frontend is a **projection + command surface**, not a second brain. Fix the *product composition seam* so wire fields mean one thing each, then make the transcript a faithful fold of the ledger.

**Tech stack:** Ink/React TUI (`vanguard/clients/tui`), `@aether/client` controller + socket transport, Python `RuntimeService` UDS daemon, `RuntimeBootstrap` + `select_model`, OpenRouter free-band (and opt-in DeepSeek v4 flash), `vg-code-*` agency manifests.

## Global constraints

- Never print `OPENROUTER_API_KEY` or `.env` values. Load at process edge only (`env_loader` / daemon), never from kernel/agency.
- Do not claim the LLM path works until a live completion is observed (free models first; paid DeepSeek only under an explicit spend cap).
- Hexagonal law: adapters must not import kernel/agency; TCB budget on `vanguard/packages/kernel/` stays `<= 1438` LOC.
- `profileId` is an **execution profile** (`product` | `plan` | `local` | `sandboxed` | `hermetic`). It is never a harness id (`vg-code-balanced`) and never a model id (`openrouter/free`).
- `manifestPath` is a real `manifest.json` on disk. Workspace `.` is not a harness.
- `model` on StartRun is a **catalog id**. Runtime must coerce it to a `ModelPort` via `select_model`.
- Secrets: `select_model` must not walk the repo `.env` on its own (hermetic tests). Product entrypoints (standalone daemon) load dotenv deliberately.
- No new Markdown under `docs/` for this work. This file stays in `.drafts/`.
- Tests stay hermetic. Live OpenRouter is a gated, budgeted proof — not CI.

---

## 0. What “SOTA agent” means here (product, not slogans)

Claude Code / OpenCode / Hermes succeed because four loops are **closed and visible**:

1. **Intent loop** — operator prompt becomes a run brief without losing cwd, agent, or model.
2. **Cognition loop** — a real ModelPort proposes finish *or* a single effect; the episode engine dispatches through the kernel.
3. **Effect loop** — read / search / patch / test execute in the workspace; approvals are explicit and unblocking.
4. **Narrative loop** — the UI is a fold of durable events: user text, assistant text, tool cards, diffs, errors. Empty glass is a defect.

Vanguard already has (2) and (3) in the lattice. The product defect is that (1) and (4) are mis-wired, so (2) either never runs a live model or runs invisibly.

A painted TUI is not an agent.

---

## 1. Honest diagnosis (do not treat rumor as root cause)

A four-point “complete diagnostic” circulated in-session. Staff review against source:

| Claim | Status | Notes |
|---|---|---|
| Persistence restored `/test/dir` from `workspaces.json` | **Plausible class, unproven as this incident** | `restoreFromPersistence` prefers `pinnedWorkspace ?? nextRecents[0]`. TUI launch pins `"."`. `/test/dir` is a **test fixture** (`tui-product-closure.test.ts`). Dead path can `Path.resolve` → `[Errno 2]`. Verify from ledger before acting. |
| Daemon lacked `OPENROUTER_API_KEY` | **True as a class** | `select_model` reads `os.environ` only. Spawn copies Node env; repo `.env` was historically not injected. Current `standalone_daemon.py` has begun dotenv ingest — **old PIDs do not**. |
| Broken `.venv` `cryptography` (`Encoding` import) | **Unverified; poor fit** | Daemon imports `OperatorSigner` at start. A living socket that accepts StartRun contradicts “every signing import crashed.” Local wheel ABI issues can exist; they are not the OpenRouter transcript bug. |
| `conversation.ts` discarded `RunFailed` / `RunCancelled` | **False as stated** | Those kinds **are** handled and survive the filter when `payload.kind` matches and text/verdict is set. |

**Highest-likelihood blockers (this codebase, this symptom):**

1. StartRun `model` is the string `"openrouter/free"`. If bootstrap treats it as an already-constructed port, `str.propose` explodes or never runs.
2. Execution profile `local` selected **FakeModel** (`finish` / `"local preview"`) when no adapter was resolved — silent, no LLM.
3. Process env often had no key; `ModelUnavailable: OPENROUTER_API_KEY is not set`.
4. **Narrative gap:** episode emits `ProposalProduced` (descriptor + optional diagnostics, **not** finish `note` in the historical payload). TUI folds **`ObservationProduced`**, which the loop does not emit for a chat finish. A successful answer looks like an empty pane.
5. Worker default / Studio remap historically used `code-default` (harness name) or `local` (FakeModel), not `product`.

**Partial in-tree movement (do not assume complete):** `_resolve_model_adapter` exists on `RuntimeBootstrap`; `executionProfileFor` already returns `"product"`; daemon dotenv stubs exist. **Live OpenRouter proof has not been executed in this program of work.** Until it has, status is *wiring in progress*, not *working*.

---

## 2. Axis model (Principal Architect)

Three identities must never collapse:

```text
harness  = what the agent is allowed to do     (vg-code-balanced / vg-code-fast / vg-code-max)
profile  = how the run is contained & stored   (product | plan | local | sandboxed | hermetic)
model    = which brain proposes                (openrouter/free | *:free | deepseek/deepseek-v4-flash-0731)
```

Wire (`StartRun` payload): `manifestPath`, `repoPath`, `brief`, `profileId`, `model`.

Frontend obligations:

- Resolve agent id → `canonicalHarnessId` → **existing** `manifest.json`.
- `planMode` → `profileId: "plan"` (read-only workspace). Else **`product`**, not `local` (local is the CI/offline FakeModel preset).
- Catalog model id is passed **as the model field only**. Never stuff it into `profileId`.
- `repoPath` is an **absolute, existing directory** (resolve `"."` at the client before send). Recents must not override an explicit launch cwd without operator action.

Runtime obligations:

- `isinstance(model, str)` → `select_model("openrouter", model_name=...)` (or named port if the string is in `MODEL_PORTS`).
- Empty model + `product`/`plan` → OpenRouter free-band default.
- Empty model + `local`/`ci` → FakeModel (tests only).
- Missing key → typed `ModelUnavailable` surfaced as `RunFailed` **and** status line.

---

## 3. Target UX (Senior Frontend)

The operator’s mental model is Cursor-like, not Observatory-like.

**Composer**

- Submit creates an optimistic **user turn** immediately (do not wait for `GoalDeclared`).
- Status: `Starting…` → `Model…` → `tool: fs.read` → `approval` → `done` / `failed` with the error string.
- Busy policy already exists (`queue` / `steer` / `interrupt`). Keep it. Do not start a second run that silently replaces the transcript.

**Transcript**

- User bubble: prompt text.
- Agent bubble: finish `note` / assistant text; streaming later is optional (v2).
- Activity cards: EffectStarted/Completed, patch diffs, pytest, approval.
- Failure bubble: `RunFailed.error`, `EpisodeCompleted.detail` on instrument_error, `ModelUnavailable` reason **without** secrets.
- Empty filter: keep turns with text, cards, **or** failed/cancelled verdict. Do not default `RunCompleted` → `"satisfied"` if that paints a fake success on a silent run.

**Approvals**

- Coding agents will hit `approval_default: "ask"` on `product`. The TUI already has `pendingApproval` + keyboard resolve. That path must be **obvious** (focus steal, diff visible). A frozen pane waiting on approval is the #1 “nothing happens” after the model actually works.
- Optional later: session-level “auto-approve low-risk reads; ask on patch/exec.” Do not silently auto-approve in the default product profile.

**Workspace chrome**

- Header shows **resolved absolute path**, agent id, model id, profile, connection.
- If recents contain a missing path, refuse StartRun in the client with a human sentence, before the daemon throws `Errno 2`.

**Non-goals for v1**

- New desktop chrome, new docs site, new agent languages, parallel multi-runtime, spend dashboard beyond cost fields already on diagnostics.

---

## 4. Frontend architecture (Staff + Senior Frontend)

### 4.1 Layers (keep; do not invent a fifth store)

```text
Ink view (app.ts, keyboard.ts)
  → TuiStore (session chrome, composer, modals)
    → FrontendAppController (persistence, providers, startRun)
      → SocketRuntimeClient (vg.4 frames)
        → RuntimeService UDS
```

Projections (`@aether/projections`) are the **only** place that interprets event kinds for conversation, snapshot, approval, evidence. Views must not switch on ad-hoc `payload.kind` lists.

### 4.2 Conversation fold — make it ledger-true

File: `vanguard/clients/projections/src/conversation.ts`

Today: `GoalDeclared` / `UserPromptSubmitted`, `ObservationProduced` (unused for finish), tools, approval, terminal kinds, **and** `RunFailed`/`RunCancelled`.

**Change set:**

1. Fold `ProposalProduced`:
   - If `note` (or future `summary`) is a non-empty string → append to agent text (cap display; ledger cap ~8k).
   - If `action` is a tool verb and not finish → tool card (in addition to EffectStarted, which may arrive later).
2. Fold `EpisodeCompleted.detail` when outcome is `instrument_error` / `runtime_error` into agent text.
3. Optimistic user turn: controller may inject a local `UserPromptSubmitted`-shaped envelope **or** the store prepends a user turn keyed by commandId until the ledger echoes. Deduplicate by text+timestamp window.
4. Tests in `vanguard/clients/projections/test/projections.test.ts`: fixture with **only** `ProposalProduced.note` + `RunCompleted` must produce a visible agent bubble. Fixture with **only** `RunFailed` already should; add a regression that asserts the error substring is present.

### 4.3 Persistence vs launch cwd

Files: `app-controller.ts` `restoreFromPersistence`, `tui/src/store.ts` `initPersistence`, `persistence-port.ts` `workspaces.json`.

**Policy:**

- Launch argument / `process.cwd()` is **sovereign** for that process.
- Recents are a picker, not a hijack.
- `pinnedWorkspace` already encodes this; close the race: `syncFromController` must not overwrite TUI `workspacePath` with a missing recents path after pin.
- Resolve `"."` → `realpath` once at TUI boot; persist the absolute path so recents are not `"."` vs `/test/dir` soup.
- Client-side `existsSync(repoPath)` before `startRun`.
- Tests that use `/test/dir` must use a temp dir or in-memory persistence — **never** the operator’s XDG `workspaces.json`.

### 4.4 StartRun payload (controller + TUI store)

Files: `tui/src/store.ts` `startRun`, `client/src/application/app-controller.ts` `startRun`, `product/harness.ts`.

Already: real `manifestPath`, `executionProfileFor(planMode)` → `product`|`plan`.

**Still required:**

- `repoPath` absolute and existing.
- Surface `startRun` transport errors in `statusMessage` **and** as a conversation system turn.
- Attach stream **before** or immediately after StartRun so early `RunFailed` is not missed (subscribe race is a classic empty-UI bug).
- Header/status must show `RunFailed` even if fold lags.

### 4.5 Accessibility of failure

Ink UIs die from silent status. Contract:

- `lastFailure` (already) + transcript line.
- Never swallow stream errors in empty `catch`.

---

## 5. Runtime composition (Staff backend, owned by frontend contract)

The frontend cannot “hope” the daemon interprets strings.

### 5.1 Bootstrap coercion

File: `vanguard/packages/runtime/bootstrap.py` `_resolve_model_adapter`

Required behavior (partially present — complete + test):

- Non-string model → use as port.
- String in `MODEL_PORTS` → `select_model(port)`.
- Else → `select_model("openrouter", model_name=id)` (free-band enforcement inside `select_model`).
- `None`/blank + `local`/`ci` → fake.
- `None`/blank + else → openrouter default.

Hermetic test: `model="openrouter/free"` + patched env key → `OpenRouterModel`, **zero network**.

### 5.2 Daemon secret inject

File: `vanguard/packages/runtime/standalone_daemon.py`, `adapters/models/env_loader.py`

- `ensure_openrouter_key_loaded(search_roots)` at process start.
- Log **source only** (`environ` | `dotenv` | `missing`), never the value.
- Roots: `AETHER_HOME`, `VANGUARD_ROOT`, repo root from `__file__`.
- Existing naive line-parser at import must not dump other secrets into logs; prefer the protected loader (mode `0600`, untracked).

### 5.3 Worker defaults

File: `vanguard/packages/runtime/service/service.py` `_run_worker_thread`

- Default `profileId` → `"product"` (not `"code-default"`).
- Blank model string → `None` (then bootstrap).

Studio gateway: unknown profile → `product`, not `local`. `"code-default"` is **not** a PRESET.

### 5.4 Operator-visible finish text on the ledger

File: `vanguard/packages/agency/episode/engine.py` `_emit_proposal`

REQ-TRUST-001: **do not** put effect `args` on events.

**Do** put `note` on non-effect proposals (`finish` / `abstain`), truncated (e.g. 8000 chars). That is the assistant answer, not a secret-bearing tool argument.

Translator already maps OpenRouter `{text, toolCalls}` → `{kind: finish, note: text}` (`invocation.py`). Without emitting `note`, the frontend cannot tell the truth.

Agency test: finish cassette → `ProposalProduced.payload.note` present; effect proposal still has no `args`.

### 5.5 Timeouts

Free OpenRouter routes queue. Default `request_timeout=30s` reads as a hung TUI. Product `select_model` should use ~120s for OpenRouter (already sketched as `DEFAULT_OPENROUTER_TIMEOUT_SECONDS`).

### 5.6 ApplicationService

File: `app_service.py`

CLI/`run()` must use the same string→port helper so `vg` and TUI cannot diverge.

---

## 6. Coding-agent loop (what makes it “like Claude Code”)

Harnesses already declare verbs: `fs.read`, `fs.search`, `patch.apply`, `proc.exec` (`vg-code-balanced` et al.).

Gaps vs SOTA:

| Capability | Current | Need |
|---|---|---|
| Q&A / sqrt-style | Coding harness + `tool_choice=required` forces tools | Finish path must remain reachable (`agency.finish` or text-only when no calls) |
| Greenfield file | Patch tool + completion policy | Short briefs must be allowed to finish after one write+test |
| Bugfix | Same | Transcript must show diff cards |
| Long session | `max_turns` (compose default 8; app_service 40) | Persist runId, resume from ledger (already a runtime theme) |
| Big files | Context policy / repo map | Do not dump whole files; search+span (existing agency policy — verify product path uses it) |
| Plan mode | `plan` profile read-only | TUI toggle already; ensure writes are withheld and the model is still live |

Do **not** build a second planner model in the TUI. Planning is a profile + prompt, not a React feature.

Approvals will dominate perceived latency. Frontend must treat `ApprovalRequested` as the main screen, not a footer footnote.

---

## 7. Live proof gate (non-negotiable)

Budget (operator-imposed): **USD 0.10**, **≤ 200** completions, free-band first, DeepSeek v4 flash only if free fails and `VANGUARD_ALLOW_PAID` is set.

**Gate A — cognition (1–3 calls)**  
Load key via `load_api_key(repo)` into a subprocess env. `select_model("openrouter", model_name="openrouter/free")`. `propose` with brief: square root of 1333. Print **ok/fail, resolved model, note/text excerpt, usd_micros**. Never print the key. Fail the gate if `ok` is false and no alternate `*:free` id succeeds within 3 tries.

**Gate B — product narrative (same process or TUI)**  
StartRun `vg-code-fast` or `vg-code-balanced`, `profileId=product`, `model=openrouter/free`, absolute repo. Assert transcript contains a non-empty agent string **or** a visible `RunFailed` reason.

**Gate C — coding (few turns, auto-approve only in a temp git repo)**  
Brief: write `isqrt.py` with integer square root. `autonomous_approval=True` on ApplicationService **only** in that temp repo. Assert a file exists or a typed failure. Cap `max_turns` (e.g. 6) to protect budget.

Until A is green, do not discuss “SOTA.” Until B is green, do not discuss “the TUI works.” Until C is green, do not discuss “coding agent.”

---

## 8. Implementation sequence (bite-sized, reviewable)

Order is causal. Do not start with visual polish.

1. **Hermetic tests for string model → OpenRouterModel** (`test/runtime/…`). Then finish `_resolve_model_adapter` if any branch still passes a raw string to `execute_profiled`.
2. **Daemon `ensure_openrouter_key_loaded`** + test that missing key logs `missing` without values.
3. **Worker/studio default `product`**; remap `code-default` away from PRESETS.
4. **Emit finish `note` on `ProposalProduced`**; agency falsifier.
5. **Projection fold** for `note` + instrument `detail`; TS tests.
6. **Absolute cwd + existsSync**; persistence pin; stop `/test/dir` from writing real XDG in tests.
7. **StartRun stream attach / statusMessage** for early failure.
8. **Timeout 120s** on OpenRouter select.
9. **Gate A** live (manual / script, not CI).
10. **Gate B** TUI or socket client.
11. **Gate C** temp repo coding.
12. Only then: approval UX tightness, plan-mode copy, header showing absolute path.

Optional later (not this plan’s critical path): token streaming into the bubble; session auto-approve reads; multi-file diff viewer polish; spend chip from `diagnostics.usd_micros`.

---

## 9. File map

| Area | Files |
|---|---|
| TUI session | `vanguard/clients/tui/src/{store,main,app,keyboard}.ts` |
| Controller / harness | `vanguard/clients/client/src/application/app-controller.ts`, `product/harness.ts`, `product/paths.ts` |
| Transport | `vanguard/clients/client/src/transports/socket.ts` |
| Transcript | `vanguard/clients/projections/src/conversation.ts` + tests |
| Bootstrap / model | `vanguard/packages/runtime/{bootstrap,model_selection,app_service}.py` |
| Daemon / worker | `standalone_daemon.py`, `service/service.py`, `service/studio_gateway.py` |
| Secrets | `vanguard/packages/adapters/models/env_loader.py` |
| Finish note | `vanguard/packages/agency/episode/engine.py` |
| Manifests | `vanguard/packages/agency/manifests/vg-code-{fast,balanced,max,default}/` |

---

## 10. SWOT (product vs Claude Code / OpenCode / Hermes)

**Strengths.** Real kernel, capability attenuation, WAL ledger, typed budgets, fail-closed model policy, actual coding harnesses. This is more *OS* than a chat wrapper.

**Weaknesses.** Product axes collapsed for months; FakeModel disguised as success; transcript folded from the wrong kinds; persistence can lie about cwd; approvals can freeze the operator; free-router latency vs 30s timeouts.

**Opportunities.** A thin, honest TUI on a trustworthy runtime could beat “chat with tools” products on auditability (every effect is a receipt). Minimal agent creation = new manifest under `agency/manifests`, not a new app.

**Threats.** Declaring victory at “Ink rendered.” Burning the $0.10 budget on a still-string ModelPort. Auto-approve in the operator’s real repo. Scope sprawl (new agents, new UIs) before Gate A.

---

## 11. Definition of done

- Hermetic unit/contract tests for coercion, note emission, conversation fold, workspace pin.
- Live Gate A evidence (model text for √1333 or equivalent) with **no key in logs**.
- TUI or socket client shows that text (Gate B) or a non-empty error.
- Optional Gate C file write in a temp repo.
- `just check` (or targeted unittest + client tests) green for touched surfaces.
- This draft remains non-canonical; promote to `docs/product/` / `FEATURE_SPEC.md` only after gates.

**Out of scope for done:** matching Claude Code’s entire product surface, multi-agent orchestration UI, paid-tier marketplace, rewriting the kernel.
