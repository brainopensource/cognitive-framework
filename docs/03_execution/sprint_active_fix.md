# Leadership Control Report — AETHER M-4 → M-8 Bundle

**To:** Project CEO / Engineering Leadership
**From:** Principal Staff Engineer review track
**Date:** 2026-08-24
**Baseline:** `cognitive-framework@feat_W4-W6_Higgs_core`, commit `c8fc6dd`
**Bundle root:** `docs/_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/aether-m4-m8/m456/`
**Decision requested:** ratify the application sequence in Chapter 3 and retain
approval authority over the two gates marked **LEADERSHIP HOLD**.

---

## 0. Purpose and control posture

This bundle contains 38 files: new code, tests, schemas, one patch against the
existing tree, and seven reports. **None of it is applied to your repository
yet.** You are on base `c8fc6dd`; the bundle is inert until Chapter 3 is
executed.

Leadership retains full control through three mechanisms, none of which this
bundle bypasses:

1. **One patch, one commit.** All modifications to existing files are isolated
   in `M6_CLOSE_ADR0090.patch`. Everything else is additive new files. Rollback
   is `git revert` of a single commit.
2. **Two explicit holds.** M-7 (concurrency) and M-8 (topologies) are *planned
   and unstarted*. Neither may proceed without a leadership decision, and the
   M-7 decision is gated on a measurement that does not yet exist.
3. **No evidence claims.** This bundle asserts no RF-85 foundation evidence. Every
   run it can produce self-reports `promotion_eligible = False`.

**Verified before writing this report:** `M6_CLOSE_ADR0090.patch` applies
cleanly to base `c8fc6dd` (`git apply --check` passed).

---

## 1. Complete file map

Paths are relative to the repository root.

### 1.1 Reports and decision records

| # | File | Lines | Bytes |
|---|---|---|---|
| 1 | `docs/_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/aether-m4-m8/m456/reports/README.md` | 50 | 2,363 |
| 2 | `docs/_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/aether-m4-m8/m456/reports/M4_FOUNDATION_EVIDENCE.md` | 190 | 7,866 |
| 3 | `docs/_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/aether-m4-m8/m456/reports/M5_GENERALITY_PROOF.md` | 205 | 7,735 |
| 4 | `docs/_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/aether-m4-m8/m456/reports/M6_MEDIATED_DELEGATION.md` | 190 | 8,106 |
| 5 | `docs/_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/aether-m4-m8/m456/reports/M6_CLOSURE_RECORD.md` | 106 | 4,580 |
| 6 | `docs/_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/aether-m4-m8/m456/reports/M7_M8_MEASUREMENT_AND_TOPOLOGY.md` | 253 | 10,914 |
| 7 | `docs/_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/aether-m4-m8/m456/reports/adr/0090-mediated-delegation-event-roster.md` | 91 | 4,523 |

### 1.2 Runtime modules

| # | File | Lines | Bytes |
|---|---|---|---|
| 8 | `…/aether-m4-m8/m456/aether_m456/runtime/attenuate.py` | 54 | 2,073 |
| 9 | `…/aether-m4-m8/m456/aether_m456/runtime/spawn_adapter.py` | 50 | 2,288 |
| 10 | `…/aether-m4-m8/m456/aether_m456/runtime/child_reducer.py` | 87 | 3,321 |
| 11 | `…/aether-m4-m8/m456/aether_m456/runtime/writer_authority.py` | 22 | 899 |
| 12 | `…/aether-m4-m8/m456/aether_m456/runtime/evidence.py` | 95 | 3,800 |
| 13 | `…/aether-m4-m8/m456/aether_m456/runtime/local_verifiers.py` | 93 | 4,709 |
| 14 | `…/aether-m4-m8/m456/aether_m456/runtime/context_store.py` | 79 | 3,027 |
| 15 | `…/aether-m4-m8/m456/aether_m456/runtime/independence.py` | 106 | 4,480 |
| 16 | `…/aether-m4-m8/m456/aether_m456/runtime/memo.py` | 45 | 1,667 |
| 17 | `…/aether-m4-m8/m456/aether_m456/runtime/__init__.py` | 0 | 0 |

### 1.3 Adapters

| # | File | Lines | Bytes |
|---|---|---|---|
| 18 | `…/aether-m4-m8/m456/aether_m456/adapters/formal_env.py` | 62 | 2,769 |
| 19 | `…/aether-m4-m8/m456/aether_m456/adapters/formal_oracle.py` | 57 | 2,489 |
| 20 | `…/aether-m4-m8/m456/aether_m456/adapters/models_init_lazy.py` | 37 | 1,385 |
| 21 | `…/aether-m4-m8/m456/aether_m456/adapters/__init__.py` | 0 | 0 |

### 1.4 Pack #2 and schemas

| # | File | Lines | Bytes |
|---|---|---|---|
| 22 | `…/aether-m4-m8/m456/aether_m456/packs/formal-default/manifest.json` | 24 | 973 |
| 23 | `…/aether-m4-m8/m456/aether_m456/packs/formal-default/system-prompt.txt` | 9 | 573 |
| 24 | `…/aether-m4-m8/m456/aether_m456/packs/formal-default/check-tool.json` | 5 | 300 |
| 25 | `…/aether-m4-m8/m456/aether_m456/packs/formal-default/emit-tool.json` | 5 | 286 |
| 26 | `…/aether-m4-m8/m456/aether_m456/schemas/child_events.schema.json` | 58 | 2,883 |

### 1.5 Tests

| # | File | Lines | Bytes |
|---|---|---|---|
| 27 | `…/aether-m4-m8/m456/tests/test_m4_evidence.py` | 91 | 4,978 |
| 28 | `…/aether-m4-m8/m456/tests/test_m5_formal.py` | 74 | 3,834 |
| 29 | `…/aether-m4-m8/m456/tests/test_m6_delegation.py` | 58 | 2,925 |
| 30 | `…/aether-m4-m8/m456/tests/test_m6_close_adr0090.py` | 89 | 4,346 |
| 31 | `…/aether-m4-m8/m456/tests/test_m7_independence.py` | 64 | 3,728 |
| 32 | `…/aether-m4-m8/m456/tests/test_foundation_perf.py` | 54 | 2,319 |
| 33 | `…/aether-m4-m8/m456/tests/__init__.py` | 0 | 0 |

### 1.6 Tooling, patch, packaging

| # | File | Lines | Bytes |
|---|---|---|---|
| 34 | `…/aether-m4-m8/m456/M6_CLOSE_ADR0090.patch` | 223 | 9,486 |
| 35 | `…/aether-m4-m8/m456/rf86_gate.sh` | 19 | 651 |
| 36 | `…/aether-m4-m8/m456/tools_independence_scan.py` | 21 | 879 |
| 37 | `…/aether-m4-m8/m456/requirements.txt` | 2 | 27 |
| 38 | `…/aether-m4-m8/m456/aether_m456/__init__.py` | 0 | 0 |

**Totals:** 38 files · 2,323 lines of Markdown and Python · 7 reports · 6 test
modules (79 tests) · 1 patch.

---

## 2. What each file is

### 2.1 Reports

**`reports/README.md`** — Bundle index. Milestone status table, the three
performance numbers, run instructions, and the two operational findings
(run CI as non-root; bubblewrap is already optional). Read this first.

**`reports/M4_FOUNDATION_EVIDENCE.md`** — Establishes that M-4 was never
"blocked" in the way the board recorded. Separates the *capability* gap (can the
runtime execute here?) from the *evidence* gap (can it prove the nine rows?).
Only the second is real. Documents the root cause of the WSL2 friction: running
as uid 0 grants `CAP_SYS_ADMIN` inside the bubblewrap user namespace, so the
nested-`unshare` probe correctly refuses to attest containment. Re-running the
suite as a non-root user moved the result from 1294/8 to 1298/3. Contains the
nine-row state algebra and the measured `local`-profile bundle showing five of
nine rows already deriving with no credentials.

**`reports/M5_GENERALITY_PROOF.md`** — Frames M-5 as a falsification attempt
against the substrate's own generality claim, not a feature addition. Explains
why the memo key needs all seven fields, with a table of the specific
unsoundness each omission enables. Documents the single most important design
rule in the milestone: the exterior oracle **replays the proof term and does not
re-solve**, because an oracle that re-invokes the solver is a second instance of
the thing being evaluated and would agree with it by construction. Includes the
RF-86 gate definition.

**`reports/M6_MEDIATED_DELEGATION.md`** — The design rationale for treating
`agent.spawn` as an ordinary effect rather than a kernel primitive, with the
rejected alternative stated and costed. Contains the attenuation algebra and a
frank write-up of a real defect found during implementation (§2.1): the first
guard was dead code, because `authority - parent.authority` is always empty
after an intersection. The extracted principle — *silent narrowing is a failure
mode, not a safety feature* — is the most transferable lesson in the bundle.

**`reports/M6_CLOSURE_RECORD.md`** — Records what was actually missing.
`ChildSpawned`/`ChildReturned` were already allocated in the 42-kind enum; the
defect was their classification in `UNFOLDED_ALLOWLIST` as advisory markers.
Includes verified fold output from the real reducer, and §6 documents an
ordering finding: RF-86 fired when `M-5-BASE` was tagged before the M-6 commit,
because the gate cannot distinguish an ADR-authorised change from an illicit
kernel hook. The gate was right; the tag was misplaced.

**`reports/M7_M8_MEASUREMENT_AND_TOPOLOGY.md`** — The forward plan, and the
longest document. Covers the three performance fixes with before/after numbers,
the M-7 measurement protocol, the M-8 topology schema, and §3, a literature-based
assessment of the SWE-bench strategy. §5.1 states plainly why the independence
numbers the analyser currently produces are **not** the M-7 decision input.

**`reports/adr/0090-mediated-delegation-event-roster.md`** — The architecture
decision record for allocating the two child event kinds. Six numbered
constraints, three rejected alternatives with reasons, consequences, and six
falsifiers. Ratified by CEO on 2026-08-24.

### 2.2 Runtime modules

**`attenuate.py`** — Pure authority algebra. No I/O, no kernel dependency, which
is what makes it exhaustively testable. Enforces six denials: authority
escalation, budget minting, unknown budget dimension, depth ceiling, delegation
cycle, spawn-quota exhaustion. `spawns` is a typed budget dimension rather than a
separate counter, so storm protection recovers across restarts through the
ordinary reservation machinery.

**`spawn_adapter.py`** — Interprets an authorised `agent.spawn` intent as a child
episode. Lives in `runtime/`, never `kernel/`. Carries the idempotency guard (a
settled spawn is never repeated) and `reconcile_cold`, whose third branch returns
`UNDETERMINABLE` rather than guessing — the branch where naive implementations
quietly corrupt themselves.

**`child_reducer.py`** — Standalone reference fold for the two child events.
`ChildSpawned` opens a record; `ChildReturned` closes it; an unmatched spawn
stays `open` and `reconcilable`. Raises on duplicate spawn, orphan return, double
return, and intent-key mismatch. `parent_cost()` implements cost conservation:
a child's spend is the parent's spend, never new budget.

**`writer_authority.py`** — Single-writer registry fragment. `spawn_adapter` owns
both kinds; kernel and orchestrator are denied. Merges into the existing
`PRIVILEGED_KIND_OWNERS`.

**`evidence.py`** — The nine-row auditor and four-state algebra. Three fail-closed
properties: an unbound verifier yields `absent`, a throwing verifier yields
`invalid`, and a row claiming `present_valid` without a source digest is demoted
to `invalid`. Never trusts a self-asserted boolean.

**`local_verifiers.py`** — The nine row derivations for the `local` profile. Each
derives from a canonical source or returns a typed reason. Row 1 is the
instructive one: a fake provider yields `unverifiable`, not `absent`, because the
source record genuinely exists and names its own synthetic nature.

**`context_store.py`** — The foundation performance fix. Interns context layer
bodies by digest *and* memoises the digest computation, addressing both the RAM
and CPU manifestations of one root cause. Append-only within an episode and never
evicts, because replay correctness depends on every referenced digest remaining
resolvable.

**`independence.py`** — M-7 Deliverable B. Derives effect independence from the
manifest selector algebra. Fail-closed: unknown selector kinds and network
wildcards are treated as overlapping, because a false "disjoint" admits a write
race while a false "overlap" only costs speed. Its `verdict()` is explicitly
willing to recommend *not* doing M-7.

**`memo.py`** — JCS canonicalisation, digest helper, and the seven-field T0
witness memo key. Raises on a missing field rather than defaulting.

### 2.3 Adapters

**`formal_env.py`** — The formal environment on the same `EnvironmentAdapter`
port as Git. Verbs `formal.check` (observation) and `proof.emit` (privileged).
Reports `tokens=None` with `tokens_reason="not_a_model_call"` rather than a
fabricated zero.

**`formal_oracle.py`** — Exterior evaluator with real Ed25519 signing. Rejects
post-hoc preregistration *before* checking the proof. The signed body binds the
full lineage so an auditor can recompute every join.

**`models_init_lazy.py`** — Drop-in replacement for
`vanguard/packages/adapters/models/__init__.py`. PEP 562 lazy attribute access,
because `ollama` eagerly pulled `urllib → http.client → email.parser` on every
process start including runs that never use it. Keeps `TYPE_CHECKING` imports so
static analysis and IDEs are unaffected.

### 2.4 Pack #2, schemas, tooling

**`packs/formal-default/*`** — Manifest, system prompt, and two tool schemas.
Shares zero verbs with the coding pack while reusing its context, routing, and
approval policies by reference. `proof.emit` is `privileged`, which forces it
through the same grant path as `patch.apply`.

**`schemas/child_events.schema.json`** — Payload schemas for both child kinds.
`additionalProperties: false`, depth bounded 1–4, and no `ChildFailed` kind —
the rejected alternative stays rejected, and a test asserts its absence.

**`M6_CLOSE_ADR0090.patch`** — The only file that modifies existing code. Five
files, verified to apply cleanly to base `c8fc6dd`.

**`rf86_gate.sh`** — CI gate. Fails if any of the five frozen substrate paths
diverges from the baseline tag. Also prints kernel TCB.

**`tools_independence_scan.py`** — Scans pack manifests and reports the
independent fraction. Currently pointed at manifests; see Chapter 3 Step 9.

**`tests/*`** — 79 tests across six modules. All passing.

---

## 3. Implementation sequence

Execute in order. Steps 1–8 are safe and reversible. Steps 9–11 are
**LEADERSHIP HOLD**.

### Step 1 — Establish the baseline (do not skip)

```bash
git checkout feat_W4-W6_Higgs_core
git rev-parse --short HEAD          # expect c8fc6dd
python3 -m pytest test/ -q --ignore=test/runtime/fixtures 2>&1 | tail -3
```

Record the result. Expect **1294 passed / 8 failed** as root, or **1298 / 3** as
a non-root user. If your numbers differ from both, stop and reconcile before
applying anything — every claim downstream is measured against this.

### Step 2 — Run CI as a non-root user

The single highest-value change in this report, and it touches no product code.
Running as uid 0 makes containment unattestable. Switch the CI runner and five
of the eight failures close.

```bash
useradd -m ci && chown -R ci:ci /path/to/repo   # or configure your runner
```

### Step 3 — Apply the M-6 patch

```bash
git apply --check docs/_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/aether-m4-m8/m456/M6_CLOSE_ADR0090.patch
git am              docs/_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/aether-m4-m8/m456/M6_CLOSE_ADR0090.patch
```

`--check` must pass silently first. This is the only step that modifies existing
files. Rollback: `git revert HEAD`.

### Step 4 — Verify M-6 closure

```bash
python3 -m pytest test/contracts/test_event_coverage.py -q     # expect 14 passed
python3 -m pytest test/ -q --ignore=test/runtime/fixtures 2>&1 | tail -3
```

The full suite must match your Step 1 baseline exactly. **Any new failure means
stop and revert** — the patch is designed to be behaviour-neutral.

### Step 5 — Tag the RF-86 baseline

Order matters. Tag **after** Step 3, never before.

```bash
git tag -f M-5-BASE HEAD
```

Tagging before M-6 causes RF-86 to fire on `ledger_emitter.py`, because the gate
cannot distinguish an ADR-authorised change from an illicit kernel hook. That is
the gate working correctly.

### Step 6 — Wire the RF-86 gate into CI

```bash
cp docs/_archive/reviews/.../m456/rf86_gate.sh ./ci/
bash ci/rf86_gate.sh M-5-BASE       # expect all five paths clean
```

Add it to the pipeline **now**, before further M-5 work. A gate added at the end
of a milestone catches nothing; its entire value is catching the incremental
kernel hook the moment it lands.

### Step 7 — Land the additive modules

Copy `aether_m456/runtime/*`, `aether_m456/adapters/*`, `aether_m456/schemas/*`
and `tests/*` into their corresponding project locations. All new files; no
existing file is touched.

```bash
python3 -m pytest tests/ -q         # expect 79 passed
```

### Step 8 — Apply the two performance fixes

**8a. Lazy model imports.** Replace `vanguard/packages/adapters/models/__init__.py`
with `models_init_lazy.py`. Verify:

```bash
python3 -c "import sys; from vanguard.packages.adapters.models import FakeModel; \
            print('urllib.request' in sys.modules)"     # expect False
```

**8b. Context interning.** Wire `context_store.py` into the live trajectory
build path, replacing inline layer bodies with `LayerRef`s. This is the only
step in Chapter 3 requiring genuine integration work rather than a file copy.
Assert `rehydrate()` byte-equality against a recorded trajectory before merging —
the 11× reduction is worthless if replay fidelity regresses.

### Step 9 — **LEADERSHIP HOLD**: capture the M-7 effect log

Do **not** build a scheduler. Build the measurement.

Construct `EffectRef` from ledger `EffectStarted` payloads carrying concrete
resolved paths — not from manifests. Run the fixed-seed task set sequentially and
capture per effect: `selector`, `sink`, `idempotency_key`, plus wall/model/tool
timings and `cache_hit_rate`.

Then feed that log to `analyse()`.

**The static numbers currently produced by `tools_independence_scan.py` are not
the decision input.** Two `fs.read` capabilities both declaring `root:
/workspace` look overlapping on paper yet read different files at runtime. A 0.0%
static reading is not evidence against M-7; it is evidence the measurement has
not been taken.

### Step 10 — **LEADERSHIP HOLD**: the M-7 decision

If the measured independent fraction is below roughly 30%, **cancel M-7 and keep
I-11**. That outcome saves a scheduler, a leasing protocol, and an entire
concurrency recovery surface, and it is a success of the process rather than a
failure.

If it clears the bar, write the measurement ADR stating the speedup ceiling,
contention cost, and leasing protocol. Only leadership may lift I-11.

### Step 11 — **LEADERSHIP HOLD**: M-8

Do not begin before Step 9 has produced a baseline. Topologies change the cost
profile, and without a sequential baseline a topology win cannot be distinguished
from a scheduler win — you would be building something unfalsifiable.

### Step 12 — Environment qualification (parallel track)

Stand up any reachable model endpoint. Combined with Step 2, this closes M-4
rows 1, 4, and 7; row 5 closes with the M-5 oracle from Step 7. No code change is
required — the profile upgrades the same evidence rows in place.

---

## 4. What leadership is being asked to decide

| # | Decision | Recommendation |
|---|---|---|
| 1 | Approve Steps 1–8 | Proceed. Reversible, behaviour-neutral, verified against base. |
| 2 | Fund Step 9 (measurement only) | Proceed. Small, and it is the sole gate on M-7. |
| 3 | M-7 authorisation | **Defer** until Step 9 reports a number. |
| 4 | M-8 authorisation | **Defer** until Step 9 exists. |
| 5 | Polyglot kernel rewrite (Rust/Go) | **Defer to M-9.** A rewrite now discards the TCB proof and stalls M-7. Prove the SPI with one small non-Python *worker* first. |

## 5. Standing risks

* **No RF-85 evidence is claimed by this bundle.** Every run it can produce
  self-reports `promotion_eligible = False`. Rows 1, 4, 5, 7 remain
  environment-gated until Step 12.
* **The kill-tree drill is outstanding.** It needs a live multi-process run and
  is gated alongside the M-4 rows. The reducer-level property it depends on — an
  open child is never folded to complete — is proven.
* **Kernel TCB reads 1737 raw lines against a 1438 logical ceiling.** The linter
  counts logical lines and passes, so this is not a breach, but the ~300-line gap
  is headroom leadership may be assuming exists and does not.
* **Scaffolding is worth roughly four points on SWE-bench Verified; model
  generation is worth tens.** AETHER will not out-score Codex CLI by harness
  quality alone. The defensible position is attributability — signed exterior
  verdicts bound to preregistered oracles, replayable trajectories, per-row
  evidence states. Compete on "you can verify our number."
