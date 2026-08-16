# LAM Benchmark Corpus and Live Model Ladder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn `tools/002_LLM_API_MOCK` from five hand-written cassettes into a frozen coding-agent benchmark plus a record/replay ladder that scores named OpenRouter models on tiers 1–5 without pretending the mock is a model.

**Architecture:** LAM stays a **stateless OpenAI-compatible trajectory player**. Intelligence never lives in LAM. Live models hit OpenRouter through the existing `OpenRouterModel` adapter (or a thin `/v1/chat/completions` client that already matches LAM’s wire). A **recorder** writes successful (and failed) live traces into the scenario bank. A **ladder runner** executes the same workspace+tools loop against `lam/<id>` or `openrouter/<id>`, emitting tokens, calls, USD, and a pass/fail per tier. Expansion of the task gama is a **corpus problem** (more gold traces), not a bigger fake brain.

**Tech Stack:** Python 3.11 stdlib HTTP + unittest, existing `vanguard.packages.adapters.models.openrouter.OpenRouterModel`, JSON scenario banks under `tools/002_LLM_API_MOCK/scenarios/`, metrics JSON under `tools/002_LLM_API_MOCK/runs/` (gitignored if they contain live previews).

## Global Constraints

- LAM must remain **stateless**: next turn = f(messages), never process memory.
- LAM **must not** call OpenRouter. Live I/O is a separate runner.
- Never print `OPENROUTER_API_KEY` or `.env` values. Use `api_key_ref` / `load_api_key`.
- Paid live runs require an explicit remaining budget in `delete_me_later_dont_commit.md`. If remaining is 0, stop and use Ollama/LAM only.
- Do not flip MVP contract rows to `covered` in this work.
- Do not invent the three unspecified **top** OpenRouter model ids. `TOP` is an empty list until Project Lead writes three ids into `tools/002_LLM_API_MOCK/models.json`.
- TDD: failing unittest before production code for every task below.
- Atoms for this corpus are only `view_file`, `edit_file`, `run_command` (and later `grep_file`, `list_dir` as additive tools). No neuroscience/psychology modules in this plan.

---

## Strategic fence (read before coding)

LAM is **not** SOTA like OpenRouter for solving coding problems. OpenRouter is a live inference marketplace. LAM is a **deterministic cassette of an agentic conversation**: the same class of object as VCR cassettes, SWE-bench gold patches, and Vanguard’s own `CassettePlayer`. It is SOTA-shaped as a **harness CI accelerator** (full multi-turn tool cascade in <20ms, $0). It is not a cognitive system.

A bigger gama of options **should** be built, but as:

| Layer | What it is | What it is not |
|-------|------------|----------------|
| Atom | `view_file` / `edit_file` / `run_command` / later `grep` / `list_dir` | A personality |
| Molecule | One scenario: workspace + gold tool trace + tests | A model |
| Polymer | Tier 1–5 bank + live ladder scores | AGI |
| Protein (later) | Vanguard kernel+CLI running the same scenarios | This plan |

Prompt engineering, self-improvement, and AETHER (outer loops, multiple AIs, real-time) **consume** this corpus. They do not belong inside `engine.py`. If a developer “improves LAM” by making it sample random clever answers, they have destroyed the benchmark.

---

## File map

| Path | Responsibility |
|------|----------------|
| `tools/002_LLM_API_MOCK/models.json` | Named bands: free / medium / high / top (top empty until named) |
| `tools/002_LLM_API_MOCK/schema.py` | Scenario JSON validation (tier, tools, workspace, turns, atoms) |
| `tools/002_LLM_API_MOCK/engine.py` | Existing player; extend only for new tools / match rules |
| `tools/002_LLM_API_MOCK/simulate.py` | Existing local harness; add `grep_file` / `list_dir` |
| `tools/002_LLM_API_MOCK/ladder.py` | Live or LAM loop; metrics row per (model, scenario) |
| `tools/002_LLM_API_MOCK/record.py` | Write a live trace into `scenarios/*.json` when `--record` |
| `tools/002_LLM_API_MOCK/live_probe.py` | Keep one-liner pings; ladder supersedes it for tier fit |
| `tools/002_LLM_API_MOCK/scenarios/*.json` | Corpus (grow here) |
| `test/tools/test_llm_api_mock.py` | Player tests |
| `test/tools/test_lam_schema.py` | Schema tests |
| `test/tools/test_lam_ladder.py` | Ladder tests with Fake transport (no network) |
| `tools/002_LLM_API_MOCK/runs/` | Metrics artefacts; do not commit secrets |

---

### Task 1: Freeze the model ladder file (top ids fail-closed)

**Files:**
- Create: `tools/002_LLM_API_MOCK/models.json`
- Create: `tools/002_LLM_API_MOCK/models.py`
- Test: `test/tools/test_lam_models.py`

**Interfaces:**
- Consumes: nothing
- Produces: `load_models() -> dict` with keys `free`, `medium`, `high`, `top`; `assert_live_allowed(band: str) -> list[str]` raises `RuntimeError` if `top` is empty and band is `top`

- [ ] **Step 1: Write the failing test**

```python
def test_top_band_is_empty_and_refuses_to_run(self) -> None:
    from tools import load  # use sys.path to 002_LLM_API_MOCK
    models = load_models()
    self.assertEqual(models["top"], [])
    with self.assertRaises(RuntimeError):
        models_for_band("top")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest test.tools.test_lam_models -v`  
Expected: FAIL `ModuleNotFoundError` or missing `models.py`

- [ ] **Step 3: Write `models.json` and loader**

```json
{
  "free": [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "cohere/north-mini-code:free"
  ],
  "medium": [
    "openai/gpt-5.6-luna",
    "deepseek/deepseek-v4-flash-0731",
    "xiaomi/mimo-v2.5"
  ],
  "high": [
    "google/gemini-3.7-flash",
    "deepseek/deepseek-v4-pro-0813",
    "z-ai/glm-5.2"
  ],
  "top": []
}
```

`models_for_band("top")` must raise: `"Project Lead must name three top OpenRouter model ids in models.json before band=top"`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest test.tools.test_lam_models -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/002_LLM_API_MOCK/models.json tools/002_LLM_API_MOCK/models.py test/tools/test_lam_models.py
git commit -m "[dev-lam] S7-LAM-001: freeze OpenRouter bands; top ids fail-closed until named"
```

---

### Task 2: Scenario schema (atoms, gold tests, metrics hooks)

**Files:**
- Create: `tools/002_LLM_API_MOCK/schema.py`
- Modify: existing scenario JSON files only if validation fails (add `"atoms"` and `"success"`)
- Test: `test/tools/test_lam_schema.py`

**Interfaces:**
- Consumes: scenario dict from JSON
- Produces: `validate_scenario(raw: Mapping) -> None` raises `ValueError`; allowed atoms default `("view_file", "edit_file", "run_command")`

- [ ] **Step 1: Write the failing test**

```python
def test_rejects_unknown_atom(self) -> None:
    raw = json.loads(Path("tools/002_LLM_API_MOCK/scenarios/t1-calculator.json").read_text())
    raw["turns"][0]["tool_calls"][0]["function"]["name"] = "rm_rf"
    with self.assertRaises(ValueError):
        validate_scenario(raw)

def test_existing_five_scenarios_validate(self) -> None:
    for path in Path("tools/002_LLM_API_MOCK/scenarios").glob("t*.json"):
        validate_scenario(json.loads(path.read_text()))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest test.tools.test_lam_schema -v`  
Expected: FAIL missing `validate_scenario`

- [ ] **Step 3: Implement validator**

Require: `id` matching `^t[1-5]-`, `tier` in 1..5, `workspace` map of relative paths (no `..`), every `tool_calls[].function.name` in `atoms`, at least one `finish_reason=stop` turn, `tool_messages` monotonically nondecreasing.

- [ ] **Step 4: Run tests**

Expected: PASS on all five current scenarios (extend JSON if a field is missing rather than loosening the schema).

- [ ] **Step 5: Commit**

```bash
git commit -m "[dev-lam] S7-LAM-002: validate scenario atoms and gold traces"
```

---

### Task 3: Fake-transport ladder (no network)

**Files:**
- Create: `tools/002_LLM_API_MOCK/ladder.py`
- Test: `test/tools/test_lam_ladder.py`

**Interfaces:**
- Consumes: `LamEngine.complete`, `simulate._execute`
- Produces: `run_ladder(model: str, scenario_id: str, complete: Callable) -> dict` with keys  
  `model, scenario, tier, passed, llm_calls, prompt_tokens, completion_tokens, total_tokens, avg_tokens_per_call, estimated_usd, wall_s, error`

`passed` is true iff the workspace tests (`run_command` that looks like pytest) exit 0 **or**, for LAM, the gold stop turn is reached and `simulate` already applied gold edits.

- [ ] **Step 1: Write the failing test**

```python
def test_ladder_on_lam_tier1_passes_without_network(self) -> None:
    row = run_ladder("lam/t1-calculator", "t1-calculator")
    self.assertTrue(row["passed"])
    self.assertGreaterEqual(row["llm_calls"], 3)
    self.assertEqual(row["estimated_usd"], 0.0)

def test_ladder_does_not_open_sockets(self) -> None:
    # complete= lambda that raises if called with openrouter model
    with self.assertRaises(ValueError):
        run_ladder("nvidia/nemotron-3-super-120b-a12b:free", "t1-calculator", transport="forbidden")
```

For the second test: `run_ladder` live path requires `transport=` injectable; default live transport must not be used in this test.

- [ ] **Step 2: Run to verify fail**

Run: `python3 -m unittest test.tools.test_lam_ladder -v`  
Expected: FAIL missing `run_ladder`

- [ ] **Step 3: Implement `run_ladder`**

- If `model.startswith("lam/")`: reuse `simulate_scenario` and set `passed` from last `run_command` observation containing `passed` or returncode 0.
- If live: `complete` must be injected (OpenRouter client). No default network in unit tests.

- [ ] **Step 4: Tests pass**

- [ ] **Step 5: Commit**

```bash
git commit -m "[dev-lam] S7-LAM-003: ladder metrics loop over LAM without network"
```

---

### Task 4: Record live traces into the bank

**Files:**
- Create: `tools/002_LLM_API_MOCK/record.py`
- Test: `test/tools/test_lam_record.py`

**Interfaces:**
- Consumes: list of `{messages, completion}` captured by ladder
- Produces: `trace_to_scenario(scenario_id, tier, workspace, captures) -> dict` suitable for `validate_scenario`

- [ ] **Step 1: Failing test** — given the three-turn calculator transcript from `docs` (view → edit → stop), `trace_to_scenario` emits `tool_messages` 0,1,2+stop and validates.

- [ ] **Step 2: Run fail**

- [ ] **Step 3: Implement** — copy assistant `tool_calls` verbatim; do not rewrite arguments. Strip secrets from tool observations (redact env, keys).

- [ ] **Step 4: Pass + commit**

```bash
git commit -m "[dev-lam] S7-LAM-004: record live OpenRouter traces into LAM scenarios"
```

This is how the gama grows: **live model succeeds → freeze as LAM gold**. Never hand-author T5 novels if a top model can produce a real trace.

---

### Task 5: OpenRouter complete() adapter for the ladder

**Files:**
- Modify: `tools/002_LLM_API_MOCK/ladder.py` (live branch)
- Modify: `vanguard/packages/adapters/models/openrouter.py` only if endpoint/model are already injectable (they are: `endpoint=`, `model=`). Prefer **not** editing the adapter; call it.
- Test: `test/tools/test_lam_ladder.py` with a fake `transport` returning one canned chat.completion JSON.

**Interfaces:**
- Consumes: `OpenRouterModel(endpoint=..., model=..., transport=fake, stream=False)`
- Produces: `openrouter_complete(model: str, messages, tools) -> dict` in OpenAI shape

- [ ] **Step 1: Failing test** — fake transport records the POST body contains `"tools"` and `"messages"`; ladder on T1 with fake that always returns the gold view_file call, then edit, then stop (scripted by tool count, like LAM). Assert no real URL is opened.

- [ ] **Step 2–4:** implement `openrouter_complete` wrapping `OpenRouterModel.propose` **or** a stdlib POST to `https://openrouter.ai/api/v1/chat/completions` using `load_api_key`. Prefer wrapping propose if the return shape can be mapped; otherwise stdlib POST to stay on the public chat schema (LAM already uses that schema).

Mapping note: `OpenRouterModel.propose` returns a Vanguard `Proposal`, not chat.completion. For the ladder, **stdlib POST to chat/completions** is the correct shared wire with LAM. Do not distort the kernel ModelPort for a benchmark tool.

- [ ] **Step 5: Commit**

```bash
git commit -m "[dev-lam] S7-LAM-005: live ladder uses chat/completions wire shared with LAM"
```

---

### Task 6: Budget gate for live runs

**Files:**
- Create: `tools/002_LLM_API_MOCK/budget.py`
- Modify: `delete_me_later_dont_commit.md` is **not** committed; `budget.py` reads it if present else env `LAM_BUDGET_REMAINING`
- Test: `test/tools/test_lam_budget.py`

**Interfaces:**
- Produces: `allow_live_call(remaining_usd: float, band: str) -> None`  
  - `free` always allowed  
  - `medium`/`high`/`top` require `remaining_usd > 0`  
  - after 10 live calls, caller appends a `0.05 USD` line to the ledger file if it exists

- [ ] **Step 1–4:** TDD the allow/deny matrix. Do not auto-debit 0.05 for free `:free` model ids (provider price is 0). Still **count** them toward the 10-call wave so the human ledger stays honest.

- [ ] **Step 5: Commit** (budget.py + tests only)

```bash
git commit -m "[dev-lam] S7-LAM-006: live ladder budget gate"
```

---

### Task 7: Run free band on all five tiers (real API)

**Files:**
- Modify: `tools/002_LLM_API_MOCK/live_probe.py` or CLI in `ladder.py` `if __name__`
- Create: `tools/002_LLM_API_MOCK/runs/ladder_free.json` (local artefact)

**Interfaces:**
- Consumes: `models_for_band("free")`, `run_ladder(live)`
- Produces: table `model × tier → {passed, llm_calls, total_tokens, wall_s, estimated_usd}`

Pass rule for **live** (stricter than LAM gold):

- T1: workspace tests green, no hand patch, ≤ 8 calls
- T2: tests green, ≥ 2 files touched, ≤ 12 calls
- T3: tests green, must not put task brief into L3 if that is the scenario invariant
- T4: tests green + README/docs edit present
- T5: tests green + new module file exists

- [ ] **Step 1:** Script `python3 tools/002_LLM_API_MOCK/ladder.py --band free --max-tokens 512`  
  Expected: 3 models × 5 scenarios = 15 live trajectories. This **will** spend free quota / rate limits, not the $0.50 paid cap.

- [ ] **Step 2:** Write `runs/ladder_free.json` and a human table in the PR body (not in `BETA-MVP-AUDIT-REPORT.md` unless asked).

- [ ] **Step 3:** Fit heuristic (document in `tools/002_LLM_API_MOCK/FIT.md`):

  - Highest tier with `passed=true` on ≥ 1 scenario of that tier is the model’s **ceiling**.
  - Wave-1 one-liner already showed: Super + North Mini = T1 hygiene; Lightning think-trace = T1 fail on concision. Re-score against full tool loops; do not keep the one-liner as the official fit.

- [ ] **Step 4:** Commit only code + FIT.md, not run JSON if it contains model dumps.

```bash
git commit -m "[dev-lam] S7-LAM-007: free-band T1–T5 ladder runner and fit rules"
```

---

### Task 8: Medium then high bands (paid, budget-capped)

**Files:**
- Same runner, `--band medium` then `--band high`
- Ledger: `delete_me_later_dont_commit.md`

**Protocol:**

1. Print remaining budget; refuse if 0.
2. Run **T1 only** for all three medium ids first. Stop a model after two consecutive HTTP 4xx/timeouts.
3. Escalate a model to T2 only if T1 `passed`. Same for T3–T5. This is the Claude Code / Aider **escalation principle**, now measured.
4. Repeat for `high`.
5. Never start `top` until Task 1’s list is non-empty.

- [ ] **Step 1:** Implement `--escalate` flag: next tier iff previous passed.

- [ ] **Step 2:** Failing test with fake complete: T1 fail ⇒ T2 not called.

- [ ] **Step 3:** Pass + commit

```bash
git commit -m "[dev-lam] S7-LAM-008: escalate paid models only after lower tier passes"
```

- [ ] **Step 4 (human/paid):** Operator runs medium then high with a fresh $0.50 wave. Developer does not start this unprompted.

---

### Task 9: Grow the corpus (gama) without random cleverness

**Files:**
- Create at least:  
  `scenarios/t1-string-dedupe.json`  
  `scenarios/t2-import-cycle.json`  
  `scenarios/t3-ledger-digest.json`  
  `scenarios/t4-approval-todo.json`  
  `scenarios/t5-extract-context-compiler.json` (may record from live later)
- Test: `test_existing_five` becomes `test_all_scenarios_validate` (already in Task 2)

Each new scenario must:

1. Include a failing test in `workspace`.
2. Include gold tool trace that makes the test pass under `simulate_scenario`.
3. Use only allowed atoms.
4. Take < 500ms in `simulate.py`.

Do **not** add 50 scenarios in one PR. Add **one per tier** this sprint (5 new + 5 old = 10). That is enough for a first public coding-agent benchmark slice.

- [ ] **Step 1:** TDD simulate pass for `t1-string-dedupe` (easy unique-list function).
- [ ] **Step 2–N:** same for t2–t5, one scenario each, separate commits.

```bash
git commit -m "[dev-lam] S7-LAM-009: add one gold scenario per tier to the coding corpus"
```

---

### Task 10: Optional atoms `list_dir` and `grep_file`

**Files:**
- Modify: `simulate.py` `_execute`, `schema.py` allowed atoms
- Test: `test/tools/test_llm_api_mock.py`

These are the next **atoms** toward AETHER. They are still filesystem, not “psychology.”

- [ ] **Step 1:** Failing test: gold turn 0 on a new tiny scenario calls `list_dir` then `grep_file`.
- [ ] **Step 2:** Implement in `_execute` only (ripgrep not required: Python `Path.rglob` + substring search; cap 64 hits).
- [ ] **Step 3:** Pass + commit

```bash
git commit -m "[dev-lam] S7-LAM-010: list_dir and grep_file atoms"
```

---

### Task 11: Wire LAM as a drop-in endpoint for Vanguard dogfood (optional, same PR series)

**Files:**
- Modify: `test/runtime/test_composition_root.py` is **not** required to hit LAM.
- Create: `tools/002_LLM_API_MOCK/vanguard_bridge.py` with `lam_propose(context, tools, sampling)` mapping `context["messages"]` → `LamEngine.complete`.

This lets `Runtime.execute_harness(..., model=LamOperator("t1-calculator"))` run cassette-free **if** the operator speaks LAM tool names. Vanguard verbs are `fs.read` / `patch.apply` / `proc.exec`, **not** `view_file`. Do **not** alias them in the kernel. The bridge may translate:

- `view_file` ↔ observe `fs.read`
- `edit_file` ↔ `patch.apply` (synthesize a tiny unified diff)
- `run_command` ↔ `proc.exec`

If that translation is lossy, **defer this task** rather than teaching the kernel OpenCode tool names (ARCH-02 / M11).

- [ ] **Step 1:** Spike behind a flag; abort the task if a clean translation needs kernel edits.
- [ ] **Step 2:** Commit only if no kernel/agency edits.

---

## Out of scope (AETHER later)

Do not implement in this plan: neuroscience modules, sociology/economics simulators, multi-agent markets, real-time robotics, self-modifying prompts as a default, training on trajectory dumps, claiming GTS/AGI, naming top models, spending past the ledger, flipping REQ-DOG-001 to covered on LAM evidence.

Those consume a **stable coding corpus + live ladder**. This plan only builds that substrate.

---

## Definition of done

1. `python3 -m unittest test.tools.test_llm_api_mock test.tools.test_lam_models test.tools.test_lam_schema test.tools.test_lam_ladder test.tools.test_lam_record test.tools.test_lam_budget`
2. `python3 tools/002_LLM_API_MOCK/simulate.py` still < 100ms per scenario
3. `models.json` top = `[]` unless PL named three ids
4. Free-band ladder JSON exists locally with a ceiling tier per model
5. Paid bands documented as operator-run; fake-transport tests prove escalation
6. No secrets in git

---

## Spec coverage

| Ask | Task |
|-----|------|
| Is LAM SOTA like OpenRouter? | Fence section (no code) |
| Bigger gama for benchmarking agents, LLMs, both, prompts | Tasks 4, 9 (corpus + record) |
| Meta-harness / AETHER atoms→proteins | Fence + Task 10 atoms only |
| Cheaper simulations after first release | LAM player kept $0 (existing + Task 3) |
| Free × 3 models × tiers 1–5 | Task 7 |
| Medium × 3 | Task 8 |
| High (gemini/deepseek-pro/glm) × 3 | Task 8 |
| Top × 3 | Task 1 fail-closed until named |
| Tokens, calls, price, avg $/call | Task 3 metrics dict |
| More LLM data | Task 4 record + Task 7/8 live |
| Improve existing LAM | Tasks 2, 10, schema; not random answers |
