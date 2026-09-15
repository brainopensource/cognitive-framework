# Vanguard Backend Remediation — §4.1–4.5

## Context

An external backend evaluation found the architecture sound but the integration
incomplete: the fallback model produced **correct code for both diagnostic tasks
and independent test execution passed, yet neither session reached successful
completion**. The backend can edit; it cannot reliably convert a correct,
verified edit into a durable, accurately accounted, completed outcome.

Five defects block that conversion. Sequencing is deliberate: defect 4.5
corrupts the evidence for every other fix, so the instruments are repaired
first; identity (4.2) is investigated before it is changed, per direction.

**Standing constraint:** never weaken an execution gate to restore a green test.
Narrow a noisy check, prove it still reds, never delete it. Several stages below
add gates — none removes one.

**Scope decisions taken:** full 4.1–4.5; candidate identity gets a reproduction
falsifier before any change; red tests are repaired at the fixture level with
security predicates untouched.

---

## Stage 0 — Restore measurement integrity (§4.5)

Nothing downstream is believable until the instruments are.

### 0.1 Fix the unittest summary parser

`.agents/skills/test-runner/scripts/run_test.py`

Root cause confirmed at `run_test.py:71`:

```
FAILED\s*\((?:failures=(\d+))?(?:,\s*)?(?:errors=(\d+))?\)
```

This requires `failures=` before `errors=` and tolerates no third key. unittest
emits `FAILED (failures=5, errors=27, skipped=17)` and `FAILED (errors=2,
skipped=1)`. On any such line the match fails **entirely**, and line 72 silently
falls back to `len(failures)` — the count of *block-regex* matches — while
`errors_count` becomes 0. That is exactly the reported 5 failures / 27 errors
resurfacing as 17 / 0. `skipped` is never parsed anywhere in the file, and
`Ran N tests` is never captured, so there is no total.

Replace with order-independent key scraping anchored to the real summary:

- Match `^(OK|FAILED)(?:\s*\((?P<keys>[^)]*)\))?$` with `re.M`, then parse
  `keys` as a comma-separated `name=count` bag — `failures`, `errors`,
  `skipped`, `expected failures`, `unexpected successes`.
- Capture `^Ran (?P<total>\d+) tests? in` for a real total.
- Take the **last** summary block: `combined_output` (line 52) concatenates
  stdout and stderr, so a nested run can emit its own.
- Keep `len(failures)` only as a last-resort fallback, and when it is used set
  `"counts_parsed": false` so a caller can distinguish a parsed count from an
  inferred one. A parse miss must never read as zero.
- Return `skipped_count`, `total_count`, and the parsed bag, and include them in
  the synthesized `summary` string at line 88 — that synthesized string is what
  the evaluation saw disagreeing with raw output.

Fix failure-block association at `run_test.py:58-68` as well:

- Split on the `====`/`----` separator lines into blocks **first**, then parse
  each block header. The single `re.DOTALL` pattern can swallow forward across
  blocks and bind a traceback to the wrong test.
- Handle both header forms: legacy `FAIL: test_x (mod.Class)` and Python 3.11+
  `FAIL: test_x (mod.Class.test_x)`. The current `f"{cls}.{method}"` at line 66
  yields `mod.Class.test_x.test_x` on 3.11+.
- Do not require a `Traceback` header — a bare `AssertionError` block (subTest,
  `assertRaises`) is currently dropped entirely.

Fixtures: errors-only, skipped-only, mixed failures+errors+skipped, `OK
(skipped=n)`, subTest output, expected-failure/unexpected-success, empty
collection, and a capture whose own stdout contains the literal `FAILED (`.

### 0.2 Fix timeout termination

Same file, lines 30–46. `Popen(..., shell=True)` without `start_new_session`
means `proc.pid` is the `/bin/sh` wrapper; `proc.kill()` at line 44 SIGKILLs only
that shell and orphans the real `python3 -m unittest` child. The following
`proc.communicate()` at line 45 then blocks on pipes the surviving grandchild
still holds — so the runner can hang *past* its own timeout, defeating the
"fail-closed timeout protection" claim in its own SKILL.md.

Reuse the pattern the repo already implements correctly:

- `vanguard/packages/adapters/sandbox/rootless.py:122` (`start_new_session=True`)
  and `:138` (`os.killpg(...)`, exit code 124)
- `tools/runners/run_swe_challenge.py:230,275`

Apply `start_new_session=True`, `os.killpg(os.getpgid(proc.pid), SIGTERM)` then
SIGKILL after a short grace, and bound the post-kill `communicate()` with its own
timeout.

This exact defect is a **planted benchmark bug** in this repo
(`benchmarks/benchmark_20_suite/08_evaluator_oracle_timeout/src/sandbox_runner.py:17`)
— the production skill runner currently has the seeded bug's shape. Mirror the
falsifier at
`test/security/test_sandbox_isolation.py:84::test_process_group_cancellation_on_timeout`.

Also fix `.agents/techniques/tdd-falsifier/scripts/run_falsifier.py:24-36`, whose
inline fallback hardcodes `timed_out=False` and passes no timeout to
`subprocess.run` at all.

### 0.3 Repair the red fixtures — predicates untouched

`test/runtime` (5 failures, 4 errors) and `test/falsifiers` (18 failures,
4 errors). Classify each before touching it:

- **Fixture defects** — missing ledger initialization in partial-session
  fixtures, outdated capability counts. Repair the setup.
- **Prerequisite masking** — tamper tests receiving `INDEX_UNBOUND` before
  reaching their intended assertion. That code is raised by
  `session.py:1957+ _epoch_from_environment_snapshot` when the workspace digest
  is missing or empty, and `engine.py:753-758` turns it into an immediate
  `ABANDONED`. Bind the epoch in setup so the test reaches the assertion it was
  written to make. The predicate itself does not change.
- **Environmental** — socket/network-dependent cases that pass unconfined. Make
  them declare the requirement and skip explicitly rather than error.

For every repaired test, prove it still reds against the original defect before
accepting it green.

`just verify` (justfile:83-85) discovers only `test/kernel`, `test/agency`,
`test/contracts`. `test/runtime` and `test/falsifiers` run **only in CI**
(`.github/workflows/ci.yml:71,95`), so a locally green `just verify` leaves those
collections unexercised. Add a `just verify-full` recipe covering the CI set
(`runtime`, `falsifiers`, `registry`, `adapters`, `security`, `trust`) so this
class of rot becomes locally visible.

### 0.4 Unblock `just check` / `just verify`

Both stop at `tools/linters/check_path_hygiene.py` (justfile:12, :77). Clean the
tracked files carrying machine-specific `/home/<user>/` paths or the forbidden
developer-username token. `docs/reports/reviews/**` and `dev_context_logs/` are
already exempt (check_path_hygiene.py:80-86, :20-34); extend the exemption list
only if a file genuinely must carry a local path — never loosen
`FORBIDDEN_PATTERNS`.

---

## Stage 1 — Candidate identity (§4.2): investigate, then fix

Per direction: reproduce before changing.

### 1.1 Reproduction falsifiers first

`git.py:247-278 GitEnvironment.snapshot` digests
`{"head": head_commit, "status": status_out}` at line 270. `git status
--porcelain` emits **status codes and paths, not content** — so two different
edits to the same tracked file both render ` M a.py` and hash identically. This
was confirmed by reading; the falsifiers make it executable.

- **A — collision:** one repo; write content X to `a.py`, snapshot; write
  content Y to the same `a.py`, snapshot; assert digests differ. Should red.
- **B — degradation:** with a present-but-failing git (non-zero `rev-parse`),
  lines 259 and 264 degrade to literal `"unknown"` and `""`, yielding a
  valid-looking *constant* digest instead of an error. Assert `snapshot()`
  returns a failed `Result`. Should red.
- **C — the live observation:** the evaluation reported identical candidate
  digests for different workspaces. Two distinct worktrees at the same HEAD with
  different dirty content must produce distinct digests.

Only once A/B/C red do we change `snapshot`.

### 1.2 Canonical content-addressed identity

One canonical candidate digest over the enumerated tree: normalized relative
path, entry type, mode bits, and content digest per entry, folded in sorted path
order with **unambiguous framing** (length-prefixed fields, so `a/b` + `c`
cannot alias `a` + `b/c`). Explicit, documented treatment of untracked files,
ignore rules, and symlinks (digest the link target; never follow). **Any
enumeration error produces a failed `Result`** — never a degraded-but-plausible
digest.

Reuse `digest_of` / `digest_bytes` from
`vanguard/packages/domain/canonicalisation/digest.py:17-25` (RFC 8785, contract
VG-04 CT-09/SC-2) so framing stays the existing canonical one.

Preserve the separation recorded in the comment at `git.py:266-269`:
`snapshot_id` varies with `_snapshot_seq`, the `digest` does not. Folding seq
into the digest once staled every verification receipt — do not regress it.

Align the siblings, which disagree today: `fake.py:124-136` still folds `seq`
into its digest (so it is *not* idempotent the way git's is) and
`sandboxed.py:111-121` mints its own shape. The invariant in
`runtime/evidence_capture.py:50-80` — both adapters' `snapshot()` are reused so
"a third tree hash is not minted" — must survive.

### 1.3 Bind verification to that identity

Re-verify, don't blindly rewrite: `session.py:1934-1938 _workspace_digest` and
its uses at :2211, :2268, :2399, :2515, :2643, :2653;
`agency/episode/admission_gate.py:54,124` (stale-receipt comparison);
`agency/forge/engine.py:112,160,289,536,572-576`.

Keep the three identities distinct in naming and type so they stop being
interchangeable strings: **repository revision** (HEAD), **filesystem candidate**
(the content digest), **execution-environment identity**. Admission and
publication bind to the filesystem candidate.

Do not conflate this with the *compiled-context* `candidate_digest` in
`agency/context/layers.py:256`, `context/compiler.py:282,457`,
`runtime/prompt_assembler.py:250,262`, `runtime/provenance.py:196,226` — a
different concept that happens to share the name. The workspace one travels as
`workspace_digest` / `candidateDigest`.

---

## Stage 2 — Crash-safe candidate lifecycle (§4.1)

`vanguard/packages/adapters/environment/transaction.py` (194 lines).

`_snapshot` (:102-115) holds pre-images **in memory only**; `_commit`
(:131-164) stages temps, then publishes with sequential `os.replace` (:150).
Abrupt death between two replaces leaves `a.py` new, `b.py` old, and a staged
`.vg-txn-` temp on disk — matching the evaluation's kill experiment. The
existing suite (`test/runtime/test_atomic_multi_file_transaction.py`, T-17)
covers AST preflight and *exception* rollback only; there is no fault injection.

Three further latent defects found while reading, worth fixing in the same pass:

- Rollback is `except OSError` (:159). A non-OSError — e.g. `UnicodeEncodeError`
  from `tmp.write_text` at :144 — escapes `_commit` with **no `_restore`**,
  leaving a partially published set. Catch broadly, restore, then re-raise/fail.
- `_restore` (:166-176) rebuilds `self._root / rel_path` raw instead of reusing
  the already-resolved `dest`, re-running path resolution during recovery.
- The publish loop indexes `staged` by a parallel `stage_index` counter
  (:146-154) whose skip condition must stay byte-identical to the stage loop's.
  Carry the staged path in the tuple instead of re-deriving the index.

### 2.1 Durable transaction journal

Before publishing any commit decision, persist a journal record containing: base
candidate digest (from Stage 1), mutation manifest, pre-image content (or a
reference to durably stored pre-image blobs), staged content digests, and
transaction state. `fsync` the journal file **and its containing directory**
before the first `os.replace`, and again on each state transition.

### 2.2 Deterministic recovery

On environment construction, scan for an incomplete journal and deterministically
complete or undo it. The decision is a function of the persisted state, never of
what happens to be on disk. Remove orphaned `TXN_TMP_MARKER` temps only as part
of that recovery, so `test/adapters/test_str_replace_exact.py:150` (asserts no
leftover markers) keeps holding after a crash, not merely after a clean run.

### 2.3 Indivisible candidate publication

Sequential renames cannot prevent an observer from seeing an intermediate state,
however durable the journal. For readers requiring an indivisible candidate,
publish via immutable candidate directories plus an atomic publication reference
swapped with a single `os.replace`. Readers resolve the reference once and read
a frozen tree.

### 2.4 Fault injection, fencing, stale base

A seam that fails deterministically at every staging, replacement, deletion,
journal-write, and publication boundary. For each injection point: kill, reopen,
run recovery, assert the tree is exactly the pre-state or exactly the post-state
and that no temp survives. Plus **writer fencing** (a second writer against the
same base is rejected, not interleaved) and **stale base** (a transaction whose
base candidate digest no longer matches must refuse).

The only production caller path is `git.py:798-873 _apply_str_replace` →
`:754-768 _apply_multi_file_transaction`, which composes batched edits into an
in-memory shadow before handing over a single transaction. That composition is a
good property — preserve it.

---

## Stage 3 — Completion convergence (§4.3)

The mechanism the evaluation asks for **already exists and is lossy**. This is a
plumbing and policy defect, not a missing feature.

### 3.1 Stop discarding structured rejection detail

`agency/multi_file_completeness.py:131-142 CallerAdmissionVerdict` already
carries `uninspected_callers`, `stale_receipts`, `omissions`, `diagnostics`, and
**`consumes_reasoning_retry`** (False when the *environment*, not the model,
failed). But `session.py:2688-2693` normalises it into `AdmissionVerdict`
(`admission_gate.py:13-20`) carrying only `reason` and `rejection_feedback` —
every structured field is dropped before `engine.py:759-774 _apply_retry` sees
it.

Independently, `packs/code-default/middleware/repository/multi_file_completeness.py`
returns a `rejections` tuple, but `session.py:2667-2678` collapses it to
`rejections[0]`, so only the *first* completeness failure ever reaches the model.
A session fixing failure #1 then discovers #2 — one turn per obligation. Combined
with the caller-admission loop, this is the observed
"alternated completion requests and caller queries until the turn bound".

Widen `AdmissionVerdict` to carry the evaluation's requested shape end to end:

```
reason_code            # existing `reason`
candidate_digest       # from Stage 1 — binds the rejection to a tree
missing_obligations    # the full `rejections` tuple, not [0]
required_evidence      # what would satisfy each obligation
permitted_recovery_actions
```

Thread it through `session.py:2641-2693` into `engine.py:759-774` and out via
`_view()["recoveryFeedback"]` (`engine.py:1003-1019`). Reason vocabulary already
exists and is rich — `admission_gate.py:44-152`,
`packs/code-default/.../multi_file_completeness.py:204-345`, and the
`CALLER_*` constants at `agency/multi_file_completeness.py:67-72`. Preserve the
codes; stop truncating them.

### 3.2 Honour `consumes_reasoning_retry`

An environment-caused refusal must not burn a reasoning retry. `_apply_retry`
currently spends a turn unconditionally and aborts to `ABANDONED` if the retry
repeats (`engine.py:358-395`). Plumb the flag so environment refusals do not
count against the no-progress window (`_no_progress_limit`, default 3) or the
repeated-action ladder (`engine.py:515-600`).

### 3.3 Terminate immediately once satisfied; report unresolvable blockers

Persist each rejection with its dependencies. Once candidate-bound evidence
satisfies the predicate, terminate immediately rather than re-running the
ladder. If an obligation **cannot** be resolved under the active index or
authority — e.g. `CALLER_COVERAGE_UNRESOLVED` with no index bound — report that
precise blocker and abstain, instead of consuming repeated finish attempts. The
`TodoItem` obligation ledger at `domain/task_state.py:186-207` (with its
`receipt_digest`) is the natural place to record resolution.

### 3.4 Reconcile the two admission implementations

There are two independent gates with overlapping-but-unequal vocabularies: the
product path (`AdmissionGate` + `CodeDefaultCompletionPolicy`) and the bench path
(`ForgeAdmissionGate`, `agency/forge/engine.py:102-195`). Forge returns its
rejection text to the model *as a tool result* (`:571-586`) rather than as a
termination — which is closer to the desired behaviour. Extract the shared
reason vocabulary so the two cannot drift, and keep the product path
authoritative.

### 3.5 Controls

Add full **product-route** positive controls through `execute_product`
(`benchmarks/product_path.py:28-71`) for a valid greenfield completion and a
valid multi-file completion — both must reach `COMPLETED`. Add adversarial
stale-evidence controls asserting that a receipt bound to a superseded candidate
digest is still rejected. These are the two diagnostic artifacts from the
evaluation; they are the acceptance criterion for this stage.

---

## Stage 4 — Provider compatibility and accounting (§4.4)

### 4.1 Dialect qualification

DeepSeek v4.1 returned DSML tool-call markup inside ordinary assistant text. The
adapter correctly refused to promote it (correct fail-closed behaviour), but the
session could not recover. Route this through the existing
`agency/episode/protocol_recovery.py` seam (`engine.py:489-506`), which already
supports accept / retry_model / stop, so unsupported serialization triggers
**bounded** protocol recovery and then the authorized fallback rather than a dead
session. Any normalization must still pass declared tool-schema validation — a
recovered call that skips schema checking is worse than no recovery.

Qualify the model/provider/dialect matrix explicitly: native tool calls, streamed
arguments, truncation, malformed responses, and HTTP 429. Capability profiles
live at `domain/models/profile.py:74-105`; route records at
`adapters/models/routing.py:10-96`.

### 4.2 Cost provenance

`adapters/models/openrouter.py:1219-1226` computes money **locally** from the
static table (`models_registry.json:77-84`, `routing.py` `pricing_as_of =
"static"`); no provider-reported cost field is read anywhere. When the provider
omits usage entirely, tokens fall back to estimates (`:1205-1217`), so
`usage_observed` can be true off an estimate.

Retain provider-reported cost as a **separate authoritative observation**
alongside the local estimate rather than replacing it. Record per transport
attempt — including translation failures — with four distinct amounts:
estimated, reserved, provider-observed, unresolved.
`runtime/trajectory.py:117-183` already models `measurement_status` per dimension
(`measured` | `estimated` | `unavailable`); extend that vocabulary rather than
inventing a parallel one, and persist provider-observed cost under its own key
instead of scavenging it as a fallback at `:140-146`.

### 4.3 Reservations across retries and fallback

`InferenceMeter` (`runtime/inference_meter.py`) is already well-behaved in
isolation: `settle` charges the full held reservation when the provider reports
nothing and increments `_unsettled_calls` (`:247-289`), and `observed_usage`
fail-closes to `(None, None)` when `usage_complete is False` (`:114-149`). The
defect is aggregate: one live diagnostic made two successful provider requests
while its terminal report reflected only the first request's usage. Preserve the
aggregate reservation across retries and fallback so a multi-attempt call settles
the sum of its attempts, not the last one. Reserve/settle/release call sites are
`session.py:480-509`.

The older ladder runner's post-response spending check is insufficient for a hard
ceiling — the `Governor` (`kernel/budget.py:83+`) is the ceiling; route through
it. Note `depth` and `turns` are deliberately non-additive (`:48`).

---

## Stage 5 — Purity reconciliation (§5)

`tools/linters/check_boundaries.py` declares `"domain": set()` (imports nothing),
yet `vanguard/packages/domain/workspace.py` imports `os`/`sys`/`pathlib` and does
real I/O — `cfg.read_text` (:34) and `mkdir(parents=True, exist_ok=True)` at :75
and :95. It passes every gate only because the linter resolves stdlib specs to
`target_area = None` and never inspects them.

Separately, `SUBPROCESS_ALLOWLIST` (`check_boundaries.py:84-101`) permits four
paths including `runtime/registry/broker.py`, each with an inline justification,
while the documentation states subprocess is confined to `adapters/sandbox/`.

Reconcile stated contracts with enforced ones. Either the exceptions are
legitimate — document them as part of the contract with the allowlist as single
source of truth — or they are violations to route through ports. Do not keep two
disagreeing statements. Extending `check_domain_blindness.py`-style enforcement
to catch I/O-in-domain would make the `workspace.py` case fail loudly instead of
passing invisibly.

### Claims to correct in canonical documentation

"Mathematically verified microkernel" and "mathematically sound production-ready
systems" exceed what any evidence here establishes. A small TCB improves
auditability; signatures authenticate evidence; passing tests establish behavior
under tested conditions. None alone proves correctness. Restate as what is
demonstrated.

Also correct the retrieval claims: LDA's built-in benchmark reached recall@5 of
1.0 for BM25/PPR on a **six-file fixture** (hybrid 0.875), and the real
repository planning call took ~4.9s. That does not substantiate universal
sub-50ms retrieval or million-line effectiveness; delta-indexing latency is a
different measurement.

---

## Verification

Run in order; each stage gates the next.

**Stage 0**
- `python3 .agents/skills/test-runner/scripts/run_test.py --cmd "..."` against
  the new parser fixtures; assert counts match the raw `FAILED (...)` line for
  every ordering and key combination, and that a parse miss sets
  `counts_parsed: false` rather than 0.
- Timeout: launch a test that spawns a sleeping grandchild; assert the runner
  returns at its deadline, exit code 124, and **no descendant survives**
  (`pgrep -g` on the recorded process group).
- `just check` and `just verify` both green.
- `just verify-full` (new) — runtime and falsifiers green, each repaired test
  shown to still red against its original defect.

**Stage 1**
- Falsifiers A/B/C red before the change, green after.
- Full `test/runtime` + `test/falsifiers` rerun: no new stale-receipt rejections
  from `admission_gate.py:54,124`.
- `runtime/evidence_capture.py` invariant holds — still exactly two tree hashes.

**Stage 2**
- Fault-injection matrix: every boundary killed, recovery run, tree asserted
  pre-state or post-state, no `TXN_TMP_MARKER` survivor.
- Re-run the evaluation's original experiment: SIGKILL immediately after the
  first replacement, reopen, confirm `a.py` and `b.py` agree.
- Concurrent-writer and stale-base tests red without fencing, green with it.
- T-17 (`test/runtime/test_atomic_multi_file_transaction.py`) and
  `test/adapters/test_str_replace_exact.py` still pass unchanged.

**Stage 3 — the acceptance criterion for the whole effort**
- Both diagnostic tasks (two-file refactor; greenfield retry helper) run through
  `execute_product` and reach `COMPLETED`, not `budget_exhausted` or
  `abandoned`.
- Exterior verification in a fresh copy with original tests restored still
  passes, and the oracle files are unchanged.
- Adversarial control: a receipt bound to a superseded candidate digest is
  rejected — no false success.
- Assert turn counts drop materially versus the 14-turn and 6-turn traces;
  that is the convergence evidence.

**Stage 4**
- Replay the DSML-markup response as a fixture; assert bounded protocol recovery
  or authorized fallback, and that any normalized call still passes tool-schema
  validation.
- A two-attempt call settles the sum of both attempts; assert reserved,
  estimated, provider-observed and unresolved amounts are all recorded per
  attempt and that the aggregate conserves
  (`runtime/foundation_evidence.py:127-151` already asserts
  `total == sum(turns)` per dimension).
- Assert a declared USD/token ceiling is enforced by the `Governor` before the
  call, not after the response.

**Stage 5**
- `just check` green with the reconciled boundary rules; the `workspace.py` I/O
  either fails loudly or is documented as a contract exception.

## Out of scope

Evaluation §5 items 4–6 (long-session cognition beyond the existing passing
104-turn restart test, repository-intelligence retrieval benchmarking, delegation
and learning) and the §6 SOTA evidence harness. Note for later: a 30-task Wilson
gate is a reasonable internal milestone but not SOTA evidence — zero false
completions in 30 trials still leaves a one-sided 95% upper failure bound near
9.5%.
