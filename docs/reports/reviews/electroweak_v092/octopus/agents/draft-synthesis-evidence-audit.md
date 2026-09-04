---
id: report.draft-synthesis-evidence-audit
canonical_id: report.draft-synthesis-evidence-audit
class: report
authority: descriptive
truth_plane: AS_BUILT
status: living
owner: consolidation-agent
canonical_for:
  - reconciliation of .draft proposals against code and measurement
purpose: >
  Before building HYDRA/swarm/meta-cognition layers, establish which claims in .draft are
  supported by the code and the benchmark artifacts, and which are not. Three load-bearing
  claims are falsified here. Building on them would waste a quarter.
audience: [architect, release-owner, maintainer]
last_verified: "2026-09-02"
analysis_subject_sha: a8775c3f (integration/consolidated-v092)
relationships:
  - arch.outer-loop.orchestrator
  - arch.meta.conductor
  - arch.context.long-horizon-engine
---

# Evidence Audit — `.draft` Proposals vs. Actual Substrate

Every claim below was checked against the merged tree at `integration/consolidated-v092`,
not against prose. Commands used are shown so each finding is independently reproducible.

## 0. Summary

The `.draft` corpus (12,185 lines across 22 documents) is architecturally strong and
substantially *already implemented* — `agency/chimera/` (2,437 lines), `agency/forge/`
(2,482 lines), and `agency/context/` (1,063 lines) exist and are real. The gap is not
design. **The gap is measurement integrity and three specific falsified causal claims.**

| # | Claim in `.draft` | Verdict | Consequence if unchecked |
|---|---|---|---|
| F1 | `vg-1-forge` achieves 100% on the 20-task suite | **Misleading** — n=1 | A 100%-vs-9.5% comparison drives roadmap decisions; it is not a comparison |
| F2 | `vg-code-max` 9.5% reflects harness/model capability | **Falsified** — all 21 runs terminated at turn 1 | Effort spent on planning/context when the loop never ran |
| F3 | `v3luna` fails because it dropped `failure_escalation` from routing-policy | **Falsified** — no code reads that key | HYDRA §6.1 proposes a static linter for a key nothing consumes |

## 1. F1 — the "100% vs 9.5%" comparison is not a comparison

```bash
python3 -c "import json;d=json.load(open('benchmarks/benchmark_20_suite/benchmark_20_results_vg_1_forge.json'));print(d['pass_rate_pct'], len(d['results']))"
# -> 100.0 1
python3 -c "import json;d=json.load(open('benchmarks/benchmark_20_suite/benchmark_20_results.json'));print(d['pass_rate_pct'], len(d['results']))"
# -> 9.5 21
```

`vg-1-forge`'s "100%" is **one task** (`01_rate_limiter_lease_recovery`), which is also the
single easiest brownfield item in the suite. `vg-code-max`'s 9.5% is 2/21. These two numbers
sit adjacent in `benchmarks/benchmark_20_suite/` with identical filenames-modulo-suffix and
identical `pass_rate_pct` schema, which is precisely how a 1-sample result gets read as a
21-sample result six weeks later.

**Action (blocking, cheap):** add `n` and `suite_digest` to the results schema and make
`runner.py` refuse to write `pass_rate_pct` when `len(results) < suite_size`. This is a
~20-line change and it is the highest-ROI item in this entire audit, because every
downstream architecture decision is being ranked on these numbers.

## 2. F2 — the 9.5% run never actually ran

```bash
python3 -c "
import json,collections
d=json.load(open('benchmarks/benchmark_20_suite/benchmark_20_results.json'))
print(collections.Counter(x['turns'] for x in d['results']))"
# -> Counter({1: 21})
```

**All 21 tasks terminated after exactly one turn.** Token counts confirm it (1,240–1,287
tokens/task — roughly a single prompt + single response). By contrast the `vg-1-forge` run
that passed used 6 turns and 15,767 tokens.

A 1-turn agent on a brownfield repair task is not a weak agent; it is a loop that did not
iterate. This is the exact signature of D2/D3/D4 in
`.draft/VG_CODE_MAX_V3_ROOT_CAUSE_FINDINGS.md` (`tool_choice="required"` making `finish`
structurally unreachable; engine rebuilt with empty `Episode` on approval re-entry). Those
defects were reported fixed — the artifact was produced 2026-09-01, i.e. *after* the fix
commits — so either the fix regressed, the artifact predates it, or the benchmark path
bypasses the fixed `session.py` re-entry loop.

**This is the single most important open question in the repo and it is answerable in one
run.** Do not design anything on top of a 9.5% number until a `vg-code-max` run shows a
turn distribution with mass above 1.

**Verified positive note:** the completion-recovery feature I preserved during the merge
*is* correctly plumbed end-to-end — `session.py:1366` sets `_completion_allowed_tools` on
repeated redundant verification, `session.py:1078` passes it, `engine.py:392` enforces it.
This directly targets the "agent won but didn't know it won" failure mode (18 of 26 oracle
passes ended `abandoned`, per `SONNET_SUPER_AGENT.md` §2). **Caveat:** the engine is
constructed inside the `while True:` re-entry loop, so the restriction only takes effect on
the *next* approval round-trip. In a fully autonomous preset with no approval-gated effects,
the loop iterates once and the restriction never applies. Fix: re-check
`_completion_allowed_tools` inside the turn loop rather than binding it at construction.

## 3. F3 — the `failure_escalation` root cause is not real

Both `SONNET_SUPER_AGENT.md` §2 and `HYDRA...md` §2.3 state that `v3luna` regressed to 2/21
because its forked `routing-policy.json` dropped `failure_escalation`, leaving
`instrument_error` with "no governed recovery path". HYDRA gives a detailed mechanism
(line 255). The code disagrees:

```bash
for k in failure_escalation role_bands maximum_band known_pricing_required \
         resolved_model_required escalate_after_attempts primary_model; do
  echo -n "$k: "; grep -rn "$k" --include=*.py vanguard/ | grep -v manifests/ | wc -l
done
# every one -> 0
```

`failure_escalation` appears in exactly three places in the entire repository: two draft
documents and one manifest JSON. **No Python, TypeScript, or schema file reads it.**
`vanguard/packages/adapters/models/routing.py:130` (`resolve_model_router`) reads only
`kind`/`strategy`, `tiers`, `primary`, `fallback`, `model`. Both `vg-code-default` and
`v3luna` therefore resolve to the *same* `SingleModelRouter`.

The pass-rate difference between those manifests is real; the stated mechanism is not. The
actual structural difference is elsewhere — `v3luna` ships `finish-tool.json` and
`aliases.json` which `vg-code-default` lacks, and `vg-code-max-v3` ships `tool-policy.json`
which neither other has. That is a far more plausible locus given D2 (the `finish` tool is
what makes termination reachable at all).

### 3b. A real bug found while checking F3

The routing-policy files across manifests use **mutually incompatible vocabularies**:

| Manifest | Content | Resolver reads | Effect |
|---|---|---|---|
| `vg-code-default` | `kind`, `role_bands`, `failure_escalation`, `maximum_band`… | `kind` only | 4 of 5 keys inert |
| `vg-code-swe-mini` | `strategy: fallback`, `primary_model`, `fallback_model` | `primary`, `fallback` | **models silently ignored**, falls back to env defaults |
| `vg-code-claude-shaped` | `strategy: tier-escalation`, `escalation_model`, `escalate_after_attempts` | `tiers` | **escalation config silently ignored** |
| `vg-code-max-v3luna` | `{"kind": "single-model"}` | `kind` | works as written |

`vg-code-swe-mini` believes it routes DeepSeek-Coder with a Qwen fallback. It does not — it
routes `get_medium_model()` / `get_free_model()`. Any benchmark attributing a score to
"deepseek-coder via swe-mini" is mislabeled.

**Action:** a JSON Schema for `routing-policy.json` with `additionalProperties: false`,
validated at compose time, fail-closed. This is the check HYDRA §6.1 wanted — but aimed at
the actual defect (unknown keys silently ignored) rather than the imagined one (a specific
key being absent).

## 4. What the drafts get *right* and should be kept

- **The 5-layer context model is real and good.** `agency/context/layers.py` orders layers by
  *mutation rate* (`L1 SYSTEM`, `L2 TOOLS`, `L3 ENVIRONMENT` = `PREFIX_LAYERS`, cacheable;
  `L4 TASK`; `L5 DIALOGUE`) with explicit cache-breakpoint placement. This is exactly the
  Tier-1/2/3 architecture the treatise §6.1 describes, already shipped. Build on it; do not
  re-specify it.
- **`CompactionStrategy` is already a swappable Protocol** (`context/compaction.py`) with
  `ResultEvictionStrategy` as default and `ForgeDistillStrategy` as a loss-bounded
  alternative. The plugin seam the mandate asks for exists here already.
- **The retrieval market is real and unusual.** `chimera/retrieval.py` models retrieval
  providers as competing bidders scored by an explicit VOI utility
  (`0.5·rel + 0.3·conf + 0.2·nov − 5e-5·cost`). This is a genuinely good primitive and is
  the natural insertion point for the long-horizon memory work.
- **`MetaCognitiveGovernor` exists** (`chimera/governor.py`) with `GovernorPolicy` thresholds
  and `CognitiveDirective` outputs. The meta-cognitive layer the mandate asks for is not
  greenfield — it is an *extension* target.
- **Semantic test-output distillation** (treatise §6.2, ~1200→180 tokens/turn) is the single
  highest-leverage unimplemented item. `parse_test_output` exists in `forge/engine.py`; a
  distillation filter on `proc.exec` results does not.

## 5. Recommended sequencing correction

The mandate asks for swarms and higher-order orchestration. The evidence says the substrate
cannot yet reliably run **one** agent for six turns and know when it has succeeded. Swarms
multiply that uncertainty by `k`.

```
BLOCKING (days, not weeks) ─────────────────────────────────────────
  A1  Fix results schema: require n == suite_size for pass_rate_pct   [F1]
  A2  Re-run vg-code-max on the 20-suite; publish turn distribution   [F2]
  A3  routing-policy JSON Schema, additionalProperties:false          [F3/3b]
  A4  Move _completion_allowed_tools check inside the turn loop       [§2]
  A5  Semantic distillation filter on proc.exec results               [§4]
        ↓  only once a single agent reliably completes multi-turn
THEN ───────────────────────────────────────────────────────────────
  B   Long-horizon context engine  (arch.context.long-horizon-engine)
  C   Conductor / meta-orchestration (arch.meta.conductor)
  D   Swarm topologies (HYDRA Mode B), gated on B and C
```

A1–A5 are collectively a few hundred lines. They are worth more than any new layer, because
every new layer is currently being evaluated against numbers that do not mean what they
appear to mean.
