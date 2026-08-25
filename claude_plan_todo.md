# AETHER Higgs v0.7.0 — Next Development Wave (W-4E)

## Context

The project is blocked at one gate and has been for weeks: **M-4 / RF-85**, the single
uninterrupted nine-row coding run. Everything downstream (M-5 generality proof, M-6
delegation, M-7 concurrency, M-8 topologies) is formally LOCKED behind it.

The tech lead's report `docs/_archive/reviews/archive/proposals/010_fi_review_higgs_gpt.md`
is **directionally correct and should be followed as the spine** — its execution order
(M-4 → M-5 → M-6 → measured M-7 → M-8) matches the ratified ADR ladder, and its
architectural rules restate existing law rather than inventing new authority. It is a
review input, not law; where it proposes net-new law (telemetry envelope v1,
privacy/retention policy) those become ADR drafts, not this wave's work.

**The central finding of this review is that M-4 is far less blocked than the documents claim.**
Measured on this host today:

| Claim in `sprint_active.md` §9 | Measured reality |
|---|---|
| "clean non-WSL restricted Linux environment" required | **False.** Bubblewrap 0.9.0 is installed and both containment denial probes (`unshare --mount`, UDP egress to 1.1.1.1:53) correctly return non-zero as uid 1000. Row 4 is attestable here. |
| Suite has 5 failures + 2 errors | **Stale.** `python3 -m unittest discover -s test -t .` → **1327 tests, OK, 8 skipped, 0 failures.** |
| TypeScript toolchain absent | **False.** node v22.18.0, tsc 5.9.3, `dist/` outputs fresh. |
| No reachable provider | **True, and the only real blocker** alongside evaluator isolation. |

So the residual gap is **two provisioning tasks, not an architecture pass**: a reachable
provider (row 1) and a separately-isolated evaluator identity at uid 10002 (row 5).
`OPENROUTER_API_KEY` is already present in the git-ignored `.env`.

The other genuinely-missing thing is **M7-01**, which is greenfield: zero occurrences of
`EffectRef`, `cache_hit_rate`, or effect-log capture anywhere in the tree. It is separately
authorized by ADR-0092, is measurement-only, and does not touch the M-4 lane — so it runs
in parallel.

**Outcome intended:** close M-4 with real evidence, produce the M7-01 number, and leave the
documentation set consistent with the code — so M-5 (the research/formal second-domain pack
that turns AETHER from a coding harness into a demonstrated meta-framework) can open cleanly.

---

## Decisions taken (confirmed with the user)

1. **Provider:** qualify **both**. Ollama (local, free, reproducible) closes RF-85; a second
   OpenRouter run afterwards proves route-independence.
2. **Sequencing:** M-4 closure first, **M7-01 in parallel** as a non-blocking lane.
3. **010_fi P0s:** telemetry envelope v1 and privacy/retention are **deferred to ADR drafts**.
   They do not gate M-4.

---

## Lane A — M-4 / RF-85 closure (blocking, owns the gate)

### A1. Provision the provider
- Install Ollama; pull a small coding model (`qwen2.5-coder:7b` suggested).
- Adapter already exists: `vanguard/packages/adapters/models/ollama.py` (endpoint
  `http://127.0.0.1:11434/api/chat`). No code change expected.
- Reference `vanguard/packages/adapters/models/env_loader.py` for how `.env` keys are read;
  reuse it for the OpenRouter route rather than adding a second loader.
- **Verify:** three currently-hermetic Ollama absent-tag tests still pass, and a live
  invocation returns provider/model/fingerprint plus measured usage (not `provider_unreachable`).

### A2. Provision the isolated evaluator
- `vanguard/packages/adapters/evaluators/isolated.py` hard-requires `expected_uid=10002`.
  Create that system user; run the evaluator daemon as it.
- Console script already declared: `vanguard-evaluator = adapters.evaluators.daemon:main`.
- Generate the Ed25519 keypair via `adapters/evaluators/signing.py`; the trust root must be
  fixed **before** the run and must not be self-selected by the subject.
- **Verify:** `_validate_instrument()` passes, and a verdict verifies against the pinned key.

### A3. Add a first-class release-run verb
This is the one real code gap in the lane. `Runtime.run_composed` +
`derive_foundation_bundle` exist, but nothing invokes a *release run* as a named command —
today it is reachable only through `lab_driver.py` or a hand-built request.

- Extend `vanguard/packages/runtime/entrypoint.py` (`execute()`, which already dispatches
  `code | explain | doctor`) with a `release` command that:
  - requires `profile_id="hermetic"` — the only preset with
    `promotion_eligible=True` / `evaluation_mode="exterior"` (`runtime/profiles.py` PRESETS);
  - requires a file-backed SQLite-WAL store (never `:memory:`);
  - takes a preregistration id produced in A4 and threads it through `runtime/run_plan.py::plan_run`.
- Reuse, do not duplicate: `runtime/assurance.py::AssurancePolicy.from_profile`,
  `Runtime._validate_release_inputs`, `runtime/foundation_evidence.py::derive_foundation_bundle`.
- **Prohibited scope:** no new parser, compiler, binding table, emitter, or evaluator bypass.
  `Runtime.run_composed` remains the sole public execution authority (RF-94 guards this).

### A4. Preregister task and oracle
- Use `domain/evidence/preregistration.py::Preregistration` +
  `schemas/mhf/preregistration.schema.json` via `adapters/evaluators/gate.py::preregister`.
- Must be immutable and created **before the first run event**, binding task bytes/digest,
  oracle files/digests, evaluator identity, protocol, and subject.

### A5. Execute one uninterrupted run and audit
- One `run_id`, one `D_R`, one episode lineage, through the `release` verb.
- Audit with `domain/evidence/audit.py::audit_foundation_evidence` — it already rejects
  `fake/mock/cassette/test/playback/synthetic` providers and verifies the signature.
- Row 7 (cold reconstruction) needs a real hard-death: `os._exit` mid-run, then a fresh
  process folds the durable prefix. The fixture pattern exists in
  `test/falsifiers/test_rf25_cold_continuation.py` — reuse its shape.
- **Any probe, WAL, identity, cost, or continuity failure = stop and record the blocker.**
  No mock, cassette, `:memory:`, host fallback, stitching, or manual repair.

### A6. Second route (post-closure)
Rerun with OpenRouter (`OPENROUTER_API_KEY` already in `.env`) to demonstrate the nine rows
are not bound to one provider. This is *strengthening evidence*, not a second M-4 claim.

**Lane A exit:** nine `present_valid` rows from one lineage, independently audited.
Only the Engineering Director may then close M-4.

---

## Lane B — M7-01 effect-log measurement (parallel, non-blocking)

Authorized by ADR-0092. **Measurement only. Do not build a scheduler, lease protocol,
claim TTL, or topology engine. I-11 stays mandatory.**

- Build `EffectRef` capture from ledger `EffectStarted` payloads carrying **concrete resolved
  paths** — never from pack manifests. Source of truth is `runtime/ledger_emitter.py`
  (`PRIVILEGED_KIND_OWNERS`, where `kernel` owns `EffectStarted`).
- Capture per effect: `selector`, `sink`, `idempotency_key`, wall/model/tool timings,
  `cache_hit_rate`.
- Run over a fixed-seed task set, sequentially. Place the capture tool under `tools/telemetry/`
  — measurement apparatus stays outside `vanguard/packages/` per `01_law/RUNTIME.md`.
- `runtime/pareto_measurement.py` already holds `WalContentionMetrics` /
  `ParetoMeasurementReport` — extend that vocabulary rather than inventing a parallel one.
- **Allocate a new falsifier from RF-95+.** RF-46–48 are reserved for M-7 *implementation*
  and MUST NOT be consumed. (RF-49–51, 54, 60–64, 71 are unlisted but risky — take RF-95.)
- **Definition of done:** the log exists, is reproducible from a fixed seed, and yields a
  number. The number is reported to the Director; **it is not acted on.** If the measured
  independent fraction is below ~30%, the correct outcome is to cancel M-7 and keep I-11 —
  that is a success of the process, not a failure.

---

## Lane C — Documentation, law, and hygiene reconciliation (cheap, unblocks nothing, prevents drift)

The docs have measurably drifted from the code. Fix now while it is small.

### C1. Re-stamp the law leaves to v0.7.0
All six `docs/01_law/*.md` carry `version: "0.6.2"` while `SPEC.md` is `0.7.0` (ADR-0093
ratified the baseline but the leaves were never re-stamped).

### C2. Close the sharpest law gap
The `ExecutionProfile → D_R` clause from ADR-0089 exists **only in `SPEC.md`, in no law leaf**.
Land it in `01_law/RUNTIME.md` (identity) and `01_law/EVIDENCE.md` (promotion eligibility).
Also record ADR-0090/0091 (`ChildSpawned`/`ChildReturned`, digest extension) in the event roster
clause of `RUNTIME.md`.

### C3. Fix dead anchors and stale ADR ranges
- `01_law/MEASUREMENT.md` routes to `SPEC.md §5.2` and `SPEC §7` — both dead; the detail body
  moved to `01_law/RUNTIME.md`.
- `RUNTIME.md §8` says "accepted ADRs 0069–0088"; `INDEX.md` says "0069–0090". Both should read 0093.

### C4. Resolve the RF-55–59 contradiction
`docs/02_decisions/INDEX.md` carries RF-55–59 in the allocation register while its own
ADR-0090 section states they are unallocated. Pick one — recommend keeping the register row
(ADR-0080 allocated them) and correcting the prose. `tools/linters/check_falsifier_ids.py`
enforces this register, so the inconsistency is live.

### C5. Correct the M-4 blocker narrative
Update `sprint_active.md` §9 to reflect the measured environment: containment attests on this
host, the suite is green, the TS toolchain is present. Leaving "M-4 is blocked on a clean
non-WSL environment" in the board is actively misleading the next engineer.

### C6. Documentation topology cleanup (per ADR-0087)
- `TODO_W-3D_final.md` — 79 KB at the **repo root**, no frontmatter, every row still marked
  `TODO` while the board declares W-3D complete. Archive it.
- `docs/03_execution/sprint_active_fix.md` — `authority: advisory`, `status: frozen` sitting in
  the execution folder. Move to `docs/_archive/reviews/`.
- `delete.md` (0 bytes) at root — remove.
- Root has both `package-lock.json` and a 114-byte `pnpm-lock.yaml` — drop the stray one.
- `.env` is correctly git-ignored and untracked (verified). Leave as is.

### C7. CI coverage gaps (note now, fix opportunistically)
`.github/workflows/ci.yml` is a single Python job. It runs **no TypeScript job** and skips
`test/lab`, `test/tools`, `test/integration`, `test/governance`, `test/benchmarks`. Client
packages are at `0.4.1-beta` while the runtime is `0.7.0`. Not blocking, but a real hole.

---

## What we are explicitly NOT doing this wave

- **Not opening M-5, M-6, M-7, or M-8.** They stay locked. `agent.spawn` stays inert at all
  three points (`domain/artifacts/manifest.py`, `runtime/delegation.py::M6_SPAWN_ACTIVE`,
  the inert verb list).
- **Not implementing a scheduler or concurrency.** I-11 is mandatory; only the Director may lift it.
- **Not landing the telemetry envelope v1 or privacy/retention policy** — ADR drafts only.
  (Worth noting: the privacy gap is real — `01_law/` has no PII/redaction/retention law, only
  R4 quarantine and receipt redaction fragments — and the M-4 run will begin writing real
  prompts into a durable WAL. Recommend ratifying it immediately *after* M-4 closes.)
- **Not touching the kernel.** TCB stays at 1366/1438 logical LOC. `ci/rf86_gate.sh M-5-BASE`
  must stay green across all five frozen paths.

---

## Verification

Run after each lane, and all of it before any Director decision:

```bash
# full suite — baseline is 1327 passed / 8 skipped / 0 failed
python3 -m unittest discover -s test -t .

# frozen-substrate gate — must report all five paths clean
bash ci/rf86_gate.sh M-5-BASE

# TCB ceiling — must stay <= 1438
python3 tools/linters/check_tcb_budget.py

# the rest of the living gates
python3 tools/linters/check_boundaries.py
python3 tools/linters/check_domain_blindness.py
python3 tools/linters/check_isolation_policy.py
python3 tools/linters/check_event_coverage.py
python3 tools/linters/check_falsifier_ids.py
python3 tools/linters/check_markdown_links.py
python3 tools/linters/check_stale_paths.py
python3 tools/linters/scan_secrets.py

# TypeScript (not in CI today)
npm run typecheck --workspaces --if-present
```

Lane-A-specific:
- `vg doctor` (or `entrypoint.py` `doctor` command) must report the real host facts with a
  reachable provider and a qualified `hermetic` profile.
- The nine-row audit must return `present_valid` for all nine — not `deriving`, which is the
  auditor's four-state algebra and is **not** promotion evidence.

**Note on `M-5-BASE`:** if Lane A or C requires an ADR-authorised change inside a frozen path,
the tag must be re-cut **after** the change lands. RF-86 must never be weakened — not by
narrowing the path list, allowlisting a file, or downgrading to a warning.
