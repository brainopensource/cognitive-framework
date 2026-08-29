---
id: quick-wins-framework-improvement-v090
class: research-report
authority: non-authorizing
status: proposed
owner: frontier-product-program
version: "0.1.0"
last_verified: 2026-08-29
implementation_performed: false
---

# Quick Wins for AETHER Framework Improvement

## Contract

This report contains hypotheses and future change proposals.

No framework change was implemented while producing it.

The 27-run frozen-framework program must distinguish these framework-level
findings from ordinary prompt, manifest, provider, and benchmark defects.

No proposal is authorized merely because it appears here.

Each proposal requires benchmark evidence, the repository’s normal ADR and
specification process where applicable, tests, security analysis, and a fresh
framework baseline.

## Executive summary

AETHER already has a credible generic substrate.

The strongest existing properties are event sourcing, capability mediation,
typed budgets, composition, replay, artifacts, evaluator separation, and
failure honesty.

The most important risks are at the seams between generic substrate and
frontier product harnesses.

The current top quick-win candidates are:

1. A canonical pack-selectable external benchmark entrypoint.
2. Strict elimination of synthetic benchmark telemetry and responses.
3. A composable web research tool through an existing port/plugin boundary.
4. A composable code-intelligence/index tool through `IndexPort`.
5. DeepSeek tool-call protocol normalization and explicit malformed-response
   diagnostics.
6. Benchmark-mode approval policy that preserves authority without consuming
   agent turns.
7. First-class task, manifest, model, patch, and oracle identity in one report.
8. Provider-reported cost completeness and explicit unknown-cost semantics.
9. Context-compaction invariants for tool-call conversations.
10. A benchmark-validity preflight for broken or contaminated tasks.

## QW-01: Canonical pack-selectable benchmark entrypoint

### Symptom

One SWE challenge runner hardcodes `vg-code-default`.

The real runtime lab driver already accepts a pack name.

This creates two benchmarking paths with different composition freedom.

### Why it matters

Harness comparison is impossible through a hardcoded preset.

Developers may be tempted to patch runtime code or duplicate runners.

### Frozen-program workaround

Use the existing pack-selectable runtime lab driver through a thin external
benchmark wrapper.

### Proposed future change

Consolidate benchmark invocation behind one stable application-level command:

```text
vg benchmark run --pack PACK --task TASK --model MODEL --report REPORT
```

### Required evidence

- Same pack/task/model produces identity-equivalent trajectory through CLI and
  Python application service.
- No hardcoded pack remains in canonical benchmark drivers.
- Existing hermetic runs remain deterministic.

### Falsifier

If the current lab driver already satisfies every official SWE provisioning,
hidden-evaluator, timeout, and report requirement, no new entrypoint is needed.

## QW-02: Remove synthetic benchmark evidence paths

### Symptom

`benchmarks/agentic_harness_matrix_benchmark.py` contains a synthetic response
generator and fallback metric values.

### Why it matters

Synthetic responses can look like empirical model output.

Fallback token, cost, and event values can convert missing telemetry into
apparently precise measurements.

### Frozen-program rule

Do not use this script as live benchmark evidence.

### Proposed future change

Split simulation and empirical benchmarking into visibly separate commands and
schemas:

```text
aether.simulation-report/1
aether.empirical-benchmark/1
```

Empirical reports must reject synthetic model objects.

Missing telemetry must remain null with an explicit reason.

### Required tests

- Synthetic responder cannot emit empirical schema.
- Empirical reporter rejects fallback metrics.
- Report visibly labels cassette, mock, simulation, and live modes.

### Falsifier

If the script is deleted or already excluded mechanically from all evidence
paths, no framework change is needed; documentation cleanup is enough.

## QW-03: Composable web research capability

### Symptom

`vg-research-minimal` exposes only local file read and search.

It cannot conduct internet research.

### Why it matters

One of the target generic products is a corroborated web researcher.

A prompt cannot create a web capability.

### Classification question

This may be a missing solution plugin rather than a framework defect.

### Preferred solution

Implement or install a web search/fetch adapter behind an existing generic
toolkit or environment port.

Declare it in the research manifest with read-only network selectors and
strict egress policy.

### Required contract

```text
web.search(query, domains?, recency?) -> ranked result metadata
web.fetch(url) -> bounded content + digest + timestamp
```

### Security requirements

- Domain allow/deny selectors.
- Bounded response size.
- Redirect limit.
- SSRF protection.
- Secret redaction.
- Content digest.
- Retrieval timestamp.
- Tool receipt in ledger.

### Required evidence

- Research V2 completes easy and hard tasks through Vanguard mediation.
- Network-disabled profile fails closed.
- Local-only researcher remains network incapable.

### Falsifier

If an existing plugin can already be composed without frozen-layer changes,
this is a product packaging gap only.

## QW-04: IndexPort-backed code intelligence

### Symptom

Tutor and coding manifests currently rely primarily on lexical search and file
reads.

Large-context tasks benefit from symbol definitions, references, outlines, and
compressed repository maps.

### Why it matters

Long repositories can consume the token budget before localization succeeds.

### Preferred solution

Implement a plugin or adapter through the existing `IndexPort` rather than
adding coding semantics to the kernel or agency engine.

### Candidate tools

```text
code.outline(path?)
code.symbol_find(name)
code.references(symbol)
code.callers(symbol)
code.context_pack(query, token_limit)
```

### Polyglot strategy

- Python AST first.
- Tree-sitter where already licensed and deployable.
- LSP as an optional richer adapter.
- Lexical fallback clearly labeled.

### Required evidence

- Retrieval precision on known symbols.
- Token reduction relative to full-file reading.
- Coding localization improvement on paired tasks.
- No unauthorized filesystem scope expansion.

### Falsifier

If lexical search matches symbol localization and token efficiency on the
preregistered hard tasks, defer this feature.

## QW-05: DeepSeek protocol normalization

### Symptom

Previous live calibration observed an invalid proposal with neither usable text
nor a valid tool call.

Another provider path produced a stream-read error.

### Why it matters

Model protocol errors can dominate agent quality before task reasoning is
tested.

### Preferred solution

Add provider-specific normalization in the model adapter boundary only after
reproducing failures with captured, secret-redacted payload digests.

### Required behaviors

- Distinguish empty content from empty tool list.
- Validate tool arguments against declared JSON schema.
- Preserve provider stop reason.
- Preserve raw response digest.
- Support bounded repair only when unambiguous.
- Never invent a tool call from prose unless the policy explicitly authorizes
  a deterministic parser.

### DeepSeek-specific research note

Official DeepSeek documentation supports native tool calls.

Model-card material indicates long-horizon tool conversations may retain
reasoning/context across turns.

Compaction must preserve protocol-critical tool messages.

### Required evidence

- Captured failing response reproduces adapter error hermetically.
- Normalizer turns only valid recoverable cases into proposals.
- Ambiguous cases remain instrument errors.
- Coding pass rate improves without hidden parser hallucination.

### Falsifier

If failures disappear with correct OpenRouter configuration and current adapter
usage, this is deployment configuration rather than framework work.

## QW-06: Approval-loop efficiency

### Symptom

A live Minimax calibration exhausted 20 turns during approval behavior without
producing a patch.

### Why it matters

Approval is an authority decision, not useful model reasoning.

Repeated approval choreography can consume budgets and distort harness scores.

### Preferred solution

Define a benchmark approval profile that pre-authorizes only bounded local
workspace writes and allowlisted test commands using a signed grant.

The model should receive the result, not spend a reasoning turn negotiating
the same policy repeatedly.

### Security constraints

- No network writes.
- No external directories.
- No destructive Git operations.
- No secret reads.
- Exact workspace selector.
- Exact command allowlist.
- Existing kernel checks remain authoritative.

### Required evidence

- Approval challenges decrease.
- Security falsifiers remain green.
- Task success does not depend on interactive operator timing.

### Falsifier

If the abandoned run was caused by model behavior unrelated to approvals,
prompt or tool-schema work may be sufficient.

## QW-07: Unified benchmark identity envelope

### Symptom

Identity data exists across trajectories, manifests, task snapshots, provider
routes, patches, and evaluator output, but benchmark consumers need one bound
record.

### Proposed future envelope

```text
framework digest
manifest digest
task digest
model requested and returned
provider fingerprint
execution profile
budget ceiling and actuals
trajectory digest
patch digest
oracle digest and verdict
```

### Why it matters

Without one bound identity, results can be accidentally compared across changed
subjects.

### Preferred location

Application/evidence layer, not kernel.

### Required evidence

- Cold process independently verifies every digest.
- Modified manifest invalidates comparison.
- Modified hidden evaluator invalidates comparison.

## QW-08: Honest cost telemetry

### Symptom

Previous OpenRouter runs reported token usage but no cost.

### Why it matters

The experiment has a hard USD ceiling.

Unknown cost cannot safely be treated as zero.

### Preferred solution

Cost state should be one of:

```text
provider_reported
registry_estimated
unknown
```

Estimated cost must record pricing-table digest and timestamp.

Unknown cost must reserve pessimistically or stop paid calls.

### Required evidence

- Provider-reported cost reconciles with token counts where available.
- Missing cost cannot bypass the budget.
- Pricing updates do not rewrite historical reports.

## QW-09: Context compaction protocol invariants

### Symptom

Long-horizon tool conversations require compaction, but removing tool-call or
tool-result linkage can make the next provider request invalid.

### Proposed invariant

Compaction may summarize semantic content, but must preserve:

- Tool call identifier.
- Tool name.
- Arguments digest.
- Result digest.
- Terminal success/failure.
- Active constraints.
- Unresolved hypotheses.
- Patch/test state.

### Required evidence

- Long tool conversation survives compaction and continuation.
- Provider accepts reconstructed history.
- Dead ends are not repeated after compaction.
- State digest remains deterministic.

## QW-10: Benchmark validity preflight

### Symptom

SWE-bench and SWE-bench Pro can contain broken, underspecified, outdated, or
contaminated tasks.

### Why it matters

A broken task can make a correct harness appear weak.

### Proposed preflight

```text
resolve base commit
build environment
run PASS_TO_PASS baseline
run FAIL_TO_PASS baseline
check hidden-test isolation
check no-op rejection
check date/network dependencies
record evaluator digest
```

### Required output

```text
VALID
INVALID
UNDETERMINABLE
```

Unknown validity must not become a scored task failure.

## QW-11: Anti-thrashing detector

### Symptom

Small and inexpensive models can repeat the same read, patch, or failed command.

### Preferred first solution

Implement as a preset-visible policy or external controller before considering
agency-engine changes.

Track normalized action signatures:

```text
signature = hash(tool_name, canonical_args, workspace_state_digest)
```

If the same signature fails repeatedly against the same state, inject a bounded
recovery observation or terminate `DOOM_LOOP`.

### Required evidence

- Repeated failures decrease.
- Valid retries after changed state remain allowed.
- No security authority is added.

## QW-12: Official benchmark container bridge

### Symptom

Official SWE-bench and SWE-bench Pro evaluation use containerized environments.

Vanguard also has sandbox and evaluator boundaries.

### Risk

Nested isolation or mismatched filesystem ownership can produce instrument
failures unrelated to agent quality.

### Preferred solution

Keep official evaluator containers exterior to the worker.

The worker edits a mounted subject copy.

The evaluator receives only the resulting patch and immutable task identity.

### Required evidence

- Hidden tests never enter worker namespace.
- Official evaluator output is captured verbatim and digested.
- Timeout kills evaluator descendants.
- Evaluator failure is distinct from task failure.

## Prioritization matrix

| ID | Candidate | Layer | Expected impact | Risk | Implement before 27 runs? |
|---|---|---|---|---|---|
| QW-01 | Pack-selectable benchmark path | Product driver | High | Low | Use existing workaround |
| QW-02 | Synthetic evidence separation | Benchmark tooling | Critical | Low | Yes, by exclusion |
| QW-03 | Web research capability | Plugin/adapter | High | Medium | Only if existing port supports |
| QW-04 | Code intelligence | Plugin/adapter | High | Medium | No framework edit during freeze |
| QW-05 | DeepSeek normalization | Model adapter | High | Medium | Only after reproduced proof |
| QW-06 | Approval efficiency | Policy/product | High | Medium | Manifest/profile first |
| QW-07 | Unified identity envelope | Evidence/product | High | Low | External report first |
| QW-08 | Honest cost telemetry | Model/product | Critical | Low | External pessimistic guard first |
| QW-09 | Compaction invariants | Agency/context | High | High | Test first; no freeze edit |
| QW-10 | Validity preflight | Benchmark tooling | Critical | Low | Yes |
| QW-11 | Anti-thrashing | Preset/controller | Medium | Low | Preset/controller first |
| QW-12 | Container bridge | Benchmark tooling | High | Medium | Yes for official tasks |

## Decision order after the 27-run program

1. Fix measurement integrity before optimizing agent quality.
2. Fix provider protocol failures before prompt tuning.
3. Fix approval loops before increasing turn budgets.
4. Add retrieval only when localization evidence shows token/context pressure.
5. Add search strategies only when single-candidate repair is the measured
   bottleneck.
6. Change framework code only when manifest, plugin, and external-controller
   alternatives are falsified.

## Definition of a justified framework change

A framework change is justified only when all are true:

- The blocker occurs in a valid task.
- The blocker repeats in at least three controlled attempts.
- The blocker is not provider-only.
- The blocker is not a malformed manifest.
- The blocker is not a missing solution plugin that existing ports can host.
- The blocker maps to a specific frozen contract.
- A minimal change is proposed.
- Security impact is understood.
- A falsifier exists.
- Expected benchmark improvement is stated before implementation.

## Final recommendation

Run the frozen 27-case program first.

Use its evidence to classify each limitation as:

```text
MODEL
PRESET
PLUGIN
PROVIDER
DATASET
BENCHMARK_DRIVER
FRAMEWORK
```

Most currently visible gaps are likely preset, plugin, provider, or benchmark
tooling gaps.

The framework should remain unchanged until the experiment proves otherwise.
