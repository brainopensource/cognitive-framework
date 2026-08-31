# Coding Max Backend Handoff — 2026-08-31

Session ending. Everything below is either **verified against source/data directly**
(marked ✅) or **a hypothesis worth checking** (marked 🔍 — never treated as fact).
No official SWE-bench claim is made anywhere in this doc.

## 1. What's recorded, where

- **Findings doc (prior round):** `.draft/CODING_MAX_LIVE_QUALIFICATION_FINDINGS_2026-08-31.md`
- **Raw API proof (12 calls, full request/response):** `.draft/raw_proof_log.json`
- **SQLite events + prompt/model-output blobs** for every traced live run:
  `/tmp/claude-1000/-home-rocha-Coding-Aether-D-System/7c81bfa0-bfd8-439e-829e-02c7e79f2cc7/scratchpad/runs/{easy-deepseek-v4-flash-0731,easy-glm-5.3-flash}/state/{events.sqlite3,blobs/}`
  (session-scoped tmp — copy out before the session is cleaned if you want it kept)
- **Dev B's independent parallel qualification** (11 live paid runs, 3 models,
  found mid-session, not run by me): `benchmarks/frontier_v090/artifacts/wave2_paid_*.json`
  and the aggregate `benchmarks/frontier_v090/artifacts/live_27_clean_report.json`
- **Total live spend this session:** ~$0.007 USD, ~100 real OpenRouter calls
  (deepseek-v4-flash-0731, glm-5.3-flash only), across two budget rounds.

## 2. LDA and LAM — use these before spending live money again

**LDA (`tools/007_LLM_DOCS_ATLAS/`)** is the repo's deterministic doc/code index —
`lda_context`, `lda_symbol`, `lda_callers`, `lda_docs_for_symbol` over MCP/CLI. I
used it at the start of this session to route to `AGENTS.md`, `docs/execution/active.md`,
and the CMX-04/05 seams instead of guessing paths. **Not used mid-session** once I
was in live-debugging mode — should have kept re-querying it (e.g. `lda_callers`
on `_messages` would likely have surfaced `ROLE_FOR_LAYER` in `layers.py` faster
than the manual trace I did).

**LAM (`tools/002_LLM_API_MOCK/`)** is a recording/replay proxy for OpenRouter and
Ollama calls: `record.py` captures live traces into reproducible scenarios,
`cassette.py`/`simulate.py` replay them at $0 and ~0 latency. Its SQLite
(`lam.sqlite`) already holds **256 scenarios, 751 traces, 893 recorded calls**.
**I did not use this at all this session** — every one of my ~100 live calls was
a fresh paid request, none recorded for reuse. That's a real inefficiency: the
`fs.read({"path":"."})` repro, the role-mapping-bug repro, the cold-start test —
all of these are now cheaply replayable smoke tests if recorded once and cassetted.
**Recommendation for the next session:** wrap the diagnostic probes below as LAM
recordings first, iterate against the replay for free, and spend live budget only
on the final confirmation run.

## 3. Confirmed fixes shipped this session (2508 tests green, all still true at HEAD)

| # | File | Bug | Fix |
|---|---|---|---|
| 1 | `vanguard/packages/agency/manifests/vg-code-default/system-prompt.txt` | Told the model to read `TASK.md` for file paths instead of trusting the already-given brief | Rewrote step 1; added explicit "don't `read` a directory" warning |
| 2 | `vanguard/packages/adapters/environment/git.py`, `.../fake.py` | `fs.read` on a directory returned `file not found: .` — an unrecoverable dead end both live models hit | `read` on a directory now returns a bounded listing + "call read again with one specific path" |
| 3 | `vanguard/packages/runtime/app_service.py` | `ApplicationService.run()` had no way to supply an approver, so `proc.exec` was unreachable in any headless run through the public facade | Added `autonomous_approval: bool = False` opt-in — ephemeral per-run `OperatorSigner`, same pattern as `test/integration/test_lam_runtime_vertical.py` |
| 4 | `vanguard/packages/adapters/environment/git.py` (`DEFAULT_ALLOWLIST`) | `ls`/`find` (pure read-only) rejected by the `proc.exec` allowlist, wasting turns | Added both to the allowlist |
| 5 | `vanguard/packages/adapters/models/openrouter.py` (`_messages()`) | **Confirmed against the canonical contract** `agency/context/layers.py:ROLE_FOR_LAYER` (`VG-03 §10.1`): layers L1/L2/L3 should all be `role: system`. `_messages()` only implemented L1 — L2 (tool schemas) and L3 (harness + AGENTS.md instructions) were silently sent as `role: user`. Verified by replaying the real captured bundle through the real function: 4 confused messages → 2 correct ones after the fix. | Changed the merge condition to honor the block's own declared `role`, not just `layer == "L1"` |
| 6 | `vanguard/packages/adapters/models/openrouter.py` (sampling defaults) | `temperature` hardcoded `0.0` (fully greedy) — a documented, classic cause of repetition traps in small/fast models | Default raised to `0.2`; added `frequency_penalty` default `0.4` (was not sent at all before). Both overridable via `sampling={...}` for reproducibility-sensitive callers (cassette recording, frozen canary) |

## 4. Why easy/medium/hard actually failed — separating confirmed fact from hypothesis

### ✅ Confirmed: the model is capable, in isolation
12 raw calls to the real OpenRouter endpoint (bypassing our engine, `temperature=0.2`,
`frequency_penalty=0.4`, `parallel_tool_calls=False`):
- **Cold-start** (system+tools+brief, no history) — deepseek 3/3 and glm 3/3 emitted
  the *correct* `read` call on the *correct* file names. Never `path="."`.
- **Single-shot direct fix** (file content given inline, asked for corrected file) —
  deepseek 3/3 correct (`return a / b`), glm 1/1 complete-and-correct (2/3 got cut
  off by my own `max_tokens=300`, my test's fault not the model's).

Full log: `.draft/raw_proof_log.json`.

### ✅ Confirmed: even with fix #5 (the role-mapping bug) shipped, the real harness still fails easy
Re-ran `DOGFOOD-01` (division-sign bug, one file) through
`ApplicationService.run(..., autonomous_approval=True)` post-fix: still `abandoned`
at 12 turns. Trace changed shape (alternates `fs.read(".")` / `ls` instead of
freezing on one call) but **never reads `src/calculator.py` specifically**. So
fix #5 was real and necessary but **not sufficient** — something else in the full
harness context (which is materially larger than my raw cold-start test: it
includes the repo-map / AGENTS.md / capabilities line / tool-schema JSON dump,
none of which were in my minimal raw repro) still derails convergence.

### 🔍 Needs investigation — the harness's own repetition-detection appears not to fire, and here's a concrete reason why it might not
`vanguard/packages/agency/episode/engine.py` already has a `no_progress_limit=3`
mechanism (`episode.repeats(turn, limit=self._no_progress_limit)`,
`vanguard/packages/agency/episode/state.py:252`) that is supposed to abort a
livelocked episode. It never fired in any of my traces despite 8-12 identical
consecutive `fs.read(".")` calls. Looking at `Turn.signature`
(`state.py:200`): it's `(state_digest, proposal_descriptor, receipt_digest,
progress_signal)`. **Hypothesis, not confirmed:** `state_digest` likely
incorporates the growing conversation/context, which changes every turn purely
because history is longer — so two turns proposing the *identical action* would
still produce *different* signatures, and `repeats()` can never trigger for
this exact class of livelock (same action, growing but otherwise pointless
context). **Ask:** trace `state_digest`'s actual inputs in the code that
constructs `Turn` (search `engine.py` for `Turn(` — I did not have budget left
to finish this trace) and confirm whether it's context-inclusive. If so, the
no-progress detector needs a signature that's blind to context length and
sensitive only to the *proposed action* (verb + args), which is the actual
thing that's repeating.

### 🔍 Needs investigation — is the repo/AGENTS.md content in the real prompt itself confusing?
The real harness's L3 layer includes a line like
`"harness=vg-code-fast environment=workspace kind=git root=/workspace capabilities=fs.read,fs.search,patch.apply,proc.exec\n\n=== Workspace Instructions (AGENTS.md) ===\n..."`
— this is denser and structured differently than my raw test's plain-English
system prompt. **Ask:** A/B the real harness prompt vs. my minimal raw one via
LAM-recorded replay (see §2) to see if the *specific formatting* of L3 (the
`key=value,value` capabilities line especially) is what tips the model toward
exploration-mode instead of direct action, independent of the role-mapping bug
already fixed. This is cheap to test now that fix #5 means L3 is at least
correctly role-tagged.

### ✅ Confirmed, separate issue found by cross-referencing Dev B's parallel data (`benchmarks/frontier_v090/`)
Read (not run by me) `benchmarks/frontier_v090/artifacts/live_27_clean_report.json`:
27 rows = 4 `COMPLETED` (**all four have `non_empirical: true` and `model: null`
— never touched a model**, confirmed by direct field read) + 16 `DATASET_INVALID`
(`terminal_reason: baseline_already_passes`, all Medium/Hard) + 7 `NO_PATCH`.
Also confirmed directly in `vanguard/packages/runtime/session.py:107`:
`ADMISSION_GATED_HARNESSES = frozenset({"vg-code-fast", "vg-code-balanced", "vg-code-max"})`
— the preset those 27 rows ran under, `vg-code-v090-react-control`, is not in
that set, so a bare `finish` with zero effects is admissible there. And
`benchmarks/frontier_v090/runner.py:validate_subset()` does build
`{"non_empirical": True, "rows": [...]}` from a `noop_executor` that never
calls a model — confirmed by reading the function. **This is a different,
already-diagnosed problem from the harness/role-mapping issue above** — it's a
benchmark-*reporting* defect (dry-run rows counted as passes, an unguarded
preset), not a model-behavior or prompt-construction defect. Do not conflate
the two when deciding what to fix first.

## 5. Proposed fixes, ranked, with files and pseudocode

**Fix A — make the no-progress detector blind to context growth (backend, agency)**
`vanguard/packages/agency/episode/state.py:200` (`Turn.signature`) and wherever
`Turn(...)` is constructed in `engine.py`.
```
# current (hypothesized): state_digest incorporates full compiled context
# proposed: separate "action_signature" from "state_digest"
action_signature = digest_of((proposal.action, canonical_json(proposal.args)))
# repeats() compares action_signature across the window, not state_digest
```
Add a falsifier: script a `FakeModel` to repeat the identical `fs.read({"path":"."})`
proposal 5 times: assert the episode aborts with a "no progress" reason at
turn `no_progress_limit`, not at `max_turns`. This directly targets the
livelock class actually observed live.

**Fix B — investigate L3 prompt density** (see §4 above). No code change
proposed yet — needs the A/B first. If confirmed, the fix is in whatever
assembles L3 (`vanguard/packages/runtime/prompt_assembler.py` or
`agency/context/*` — I did not locate the exact L3 builder this session,
another dev should `lda_callers` on `Layer.ENVIRONMENT` to find it).

**Fix C — wire the completion gate for the benchmark preset** (Dev B's finding,
independently confirmed above)
`vanguard/packages/runtime/session.py:107`:
```
ADMISSION_GATED_HARNESSES = frozenset({
    "vg-code-fast", "vg-code-balanced", "vg-code-max",
    "vg-code-v090-react-control",  # and any other harness used for scoring
})
```
Better: gate by capability declaration (does the harness grant `patch.apply`?)
rather than a hardcoded name allowlist, so a new preset can't silently ship
ungated. Add a falsifier asserting every harness with `patch.apply` in its
manifest capabilities is in the gated set.

**Fix D — purge non-empirical rows from live reports**
`benchmarks/frontier_v090/runner.py` — `validate_subset()`'s output must never
be written into the same report file/schema as live rows. Give it a distinct
schema id (e.g. `aether.frontier-benchmark-subset-preflight/1`) and have the
report aggregator refuse to merge rows carrying it into a "live" denominator.

**Fix E — fix Medium/Hard fixture seeding**
Wherever the 16 `baseline_already_passes` fixtures are generated (not located
this session — grep `benchmarks/frontier_v090/` and `benchmarks/swe_bench/`
for the M/H challenge source). Add a falsifier: for every challenge, running
the oracle against the *unmodified* baseline workspace must fail, before any
challenge is admitted into the corpus. This is the same discipline already
used correctly in my own `benchmarks/greenfield/qual-0{1,2,3}-*` fixtures
(each verified red-before, green-after by hand — see prior findings doc).

## 6. What I'd do next, in order (didn't get to it — budget/turn limits)
1. Fix A's falsifier first — cheapest, most directly targets the observed livelock.
2. Trace `Turn(` construction in `engine.py` to confirm/deny the `state_digest` hypothesis before writing the fix.
3. Record the cold-start and role-mapping-bug repros as LAM cassettes so the next session doesn't re-pay for them.
4. Only then re-attempt live easy/medium/hard, gated same as before (don't spend on hard until medium passes).
