# Part II — Diagnosis

Seven structural findings. Each states the defect, the evidence, the mechanism, and the correction.
They are ordered by expected value of fixing them, highest first.

---

## D1 — The capability inversion

**Defect.** The project's rigor is allocated inversely to where capability is determined.

```
kernel/            1,769 LOC   13-stage dispatch, attenuation algebra, provenance DAG
                               ← months of careful work, a LOC ceiling, must-fail falsifiers
agent tool surface       5 verbs   read-one-file · grep · unified-diff · argv-exec · finish
                               ← an afternoon, no ceiling needed because there is nothing there
```

**Evidence.** Part 1 §2.1, §2.2. The kernel has a governance apparatus (`check_tcb_budget.py`,
`check_domain_blindness.py`, `check_kernel_neutrality.py`). The tool surface has a system prompt
that apologises for itself.

**Mechanism.** `SinkRegistry.register(action, sink_class)` in `kernel/classifier.py` makes adding a
capability *one row*. The docstring says so explicitly:

> "Open/closed: adding a capability is a registry entry plus a configuration line (`01 §2`), and
> the dispatcher never changes to accommodate one."

The design anticipated a large mediated capability set. Nobody wrote the rows. The consequence is a
world-class authority-mediation system mediating almost nothing — the security equivalent of a bank
vault installed around an empty room.

Why this is the top finding: **capability is where coding-agent performance actually lives.** The
gap between a 10% agent and a 60% agent on brownfield repair is not the loop, the planner, the
topology, or the metacognition. It is whether the agent can list a directory, find a symbol's
callers, edit by exact string match, run an arbitrary shell command, and issue five reads in one
turn. Every one of those is a `SinkRegistry` row plus an adapter method.

**Correction.** Part 3 §4 (tool taxonomy), Part 5 Sprint 1. Twenty verbs, each a registry row, each
with a must-fail test. No kernel change.

---

## D2 — The best asset is wired to the wrong consumer

**Defect.** `.lda/index.db` — 3,347 files, 13,882 entities, 10,422 symbols, **77,610 relations**,
5,073 doc sections, 29,959 FTS rows — serves the *human developer*. The *agent* gets a five-regex
file scan.

**Evidence.** Part 1 §2.3. `AGENTS.md` mandates the LDA navigation protocol for "humans and AI
agents", but the protocol is a set of shell commands a developer runs, not tools an episode can
call. `IndexPort` is bound to `FileRepoIndex`. `ast_grep_adapter.py` and `scip_adapter.py` are
referenced by nothing.

**Mechanism.** The index was built as a *development tool* under `tools/`, outside the hexagonal
lattice, and so it never acquired an adapter. `IndexPort` was designed correctly and then bound to
a placeholder whose own docstring calls it "deliberately cheap … tree-sitter can replace the body
later without the port moving, which is the point of having the port now." The port *is* the point,
and the replacement never happened.

**Why this is finding #2.** Retrieval quality is the second-largest determinant of brownfield
performance after tool surface, and this is the one place where AETHER could be *ahead of* the
frontier rather than behind it. Frontier coding agents navigate with `grep` + `glob` + reading,
because they have no code graph. You have a code graph with 77,610 edges and you are not using it.
`symbol → refs → callers → tests-that-cover-it` is a materially better localisation path than
grep-and-hope, and it is already computed.

**Correction.** `LdaRepoIndex(IndexPort)` backed by `.lda/index.db`, with `FileRepoIndex` retained
as the honest fallback that T-45 already specifies. Then expose `symbol`, `refs`, `defs`, `callers`,
`covering_tests` as agent verbs. Part 3 §6, Part 5 Sprint 2.

---

## D3 — Prompt caching: the hard half done, the free half skipped

**Defect.** A provably cache-stable prefix is computed and no cache breakpoint is ever emitted.

**Evidence.** Part 1 §2.4. `BREAKPOINT_LAYERS` exists in `layers.py`; `cache_control` appears
nowhere in `vanguard/`; `cached_tokens` appears only inside `openrouter.py`'s price arithmetic.

**Mechanism.** Split ownership. The compiler (in `agency/`) knows *where* the breakpoints are; the
adapter (in `adapters/`) knows *how* to send them. Nothing carries the positions across the port
boundary, because `ModelPort`'s `propose(context, tools, sampling)` signature has no place for
them — `ContextBundle` transports the rendered text, not the layer structure.

This is the cleanest example in the repository of a **port that under-specifies its payload**. The
fix is to make cache breakpoint positions part of the `ContextBundle` contract, not to bolt them on
in the adapter.

**Impact.** At 13,668 prompt tokens/turn × 4–40 turns × hundreds of runs, uncached prefix re-sends
are the dominant recurring cost and a significant share of latency. Typical prefix share for this
layout is 70–85% of the prompt. This is a two-file change with an immediate, measurable, one-order
effect on both cost and wall time.

**Secondary defect, same area.** `_schemas_with_aliases` (`compose.py:506,524`) expands each verb
into aliased duplicates at composition time. If that expansion is not byte-deterministic across
turns, `L2` mutates and the prefix invariant silently breaks — invalidating the cache the moment it
starts working. The invariant is protected by a docstring and no test. **Add the test before adding
the breakpoints**, or you will ship a cache that appears to work and does not.

---

## D4 — There was no termination contract

**Defect.** `completed_without_source_patch` × 27 is not a model failure. It is the absence of a
postcondition.

**Evidence.** Part 1 §1.3. Identical `before_digest`/`after_digest` on all 27 rows, terminal state
`COMPLETED` at the episode level, `NO_PATCH` only at the report level. The episode believed it
succeeded.

**Mechanism.** `RunTermination` (`agency/episode/state.py`) is deliberately, and correctly, an
*instrument* axis, separated from evaluation:

> "Collapsing this with the evaluation outcome is how instrument failure silently becomes task
> failure, so the evaluation axis is deliberately absent from `agency/`."

That separation is right. But it left a hole: *nothing* between the episode and the exterior
evaluator asserted "work was performed." The agent's self-report of completion was the only gate.

**What is now correct.** `AdmissionGate` (`agency/episode/admission_gate.py`) plus
`VerificationReceipt` is the right answer and it is well-formed:

```python
@property
def passed(self) -> bool:
    return self.exit_code == 0 and self.executed_test_count > 0
```

`executed_test_count > 0` is a particularly good detail — it defeats the "exit 0 because zero tests
collected" failure that commit `25dbe177` was written to fix. Bound to `changed_files` and a
`workspace_digest`, this is a domain-blind, checkable postcondition that eliminates all 27 failures.

**What is now wrong.** `tool_policy.resolve_tool_policy` in the same package hardcodes a workflow:

```python
if phase == "inspect": allowed = ("fs.read", "fs.search")
if phase == "edit":    allowed = ("fs.read", "fs.search", "patch.apply")
if phase == "verify":  allowed = ("proc.exec", "fs.read", "patch.apply")
_VERIFY_TRIGGERS = frozenset({"patch.apply"})
```

Against `README.md` §10:

> "If you find yourself declaring a shape for the work *before* the work runs, you are building the
> thing `spec.md` (loop-over-DAG inversion) rejects."

This is that. It is a fixed three-state DAG, in the domain-blind layer, keyed on the string literal
`patch.apply`, with `_EDIT_TRIGGERS` and `_VERIFY_TRIGGERS` naming coding verbs directly. The
in-file comment — "the phase ladder lives here, not in the engine: `ADR-0060` requires the episode
loop to name no domain verb" — relocates the violation within the same package rather than
resolving it.

**Why it must go, beyond purity.** It forbids running the test suite before editing. Reproducing
the failure first is the single most reliable brownfield strategy known; a capable model does it
unprompted, and this policy denies it. The ladder was added to stop a weak model from monologuing;
it will cost you on every capable model you ever attach. **Prior restraint on the action space is
the wrong control; postconditions on the outcome are the right one.** Keep `AdmissionGate`, delete
`derive_phase`.

---

## D5 — Sprawl by copy, in a project whose thesis is composition

**Defect.** 32 manifests, 3 engines, 3 patchers, ~50 single-row report files. Nothing can be
retired because nothing can be compared.

**Evidence.** Part 1 §1.5, §2.5, §2.6.

**Mechanism — this is the important part.** The sprawl is not carelessness. It is the *rational
response* to a missing instrument.

When you cannot measure whether change X helped, the only way to preserve the possibility that it
helped is to keep X alongside not-X. Every fork is a hypothesis that could not be falsified, so it
was archived instead. Thirty-two manifests, three engines, and fifty `report_v3*` files are all the
same artifact: **the residue of unfalsifiable hypotheses.**

This inverts the usual advice. "Delete the forks" is not the fix; the forks will regrow within a
month. **Build the comparison instrument, and the forks delete themselves** — because once `bench
compare vg-code-max vg-code-max-v3luna` prints a McNemar p-value over 40 tasks, twenty-nine of the
presets become visibly worthless and deleting them costs nothing emotionally.

The tragedy is that the instrument's hardest component already exists: `benchmarks/statistics.py`
and `runtime/paired_evaluation.py` implement paired designs and McNemar. **You have the statistics
and no dataset to run them on.** What is missing is mundane: one frozen suite, one runner, one
append-only results file, one comparison command.

**Correction.** Part 3 §14, Part 5 Sprint 3. Freeze the suite, build the runner, run all 32, delete
by data.

---

## D6 — Documentation has become the second product

**Defect.** 58,910 lines of documentation, a six-tier precedence ladder, a constitutional amendment
procedure, and ADRs through 0102 — governing a coding agent that produced no patch on 27
consecutive tasks.

**Evidence.** Part 1 §2.1, §2.7. Nine commits reworking board structure. `VISION.md` at 487 lines
of frontmatter-versioned constitutional text; `docs/execution/technical.md` at 5,575 lines;
`docs/execution/spec.md` at 1,258.

**Mechanism.** Documentation is *tractable*. When the agent doesn't work and you don't know why,
restructuring the board produces a visible, satisfying, committable result. The `check_doc_budgets.py`
limit of 200 lines per living document is itself evidence that someone recognised the problem and
addressed it with a linter rather than with deletion — and `docs/execution/technical.md` at 5,575
lines shows the linter is being routed around.

**What is genuinely valuable and must survive any cut:**

- `docs/execution/spec.md` as the single normative surface, with RFC-2119 obligations and invariants.
- The falsifier IDs and the `check_*` linter suite. These are executable law and they work.
- The precedence *principle* — one normative document per contract — which prevents the second
  source of truth.
- The epistemic vocabulary: `undeterminable`, "mechanism presence is not milestone acceptance",
  `DATASET_INVALID` preserved. This is the project's intellectual signature.

**What should go:** the constitutional apparatus. A six-tier ladder, a Vision-superseding-ADR
ratification procedure, and "Engineering Leadership" as an authority are governance for a
multi-team organisation. This repository has one primary developer and a 10% pass rate. The ceremony
is a tax paid in the exact currency — attention — that D1 and D2 need.

There is also a concrete accessibility defect: **`VISION.md`'s twenty substantive chapters are in
Portuguese** inside an otherwise English repository whose normative law, code, and peer reviews are
all English. The thinking in those chapters is good — Ch. 4 (agent as projection), Ch. 7
(composition vs. trajectory), Ch. 15 (partial order), Ch. 17 (ledger/artifact/projection), Ch. 18
(skill promotion discipline) are the intellectual core of the project. As written, no contributor
and no coding agent will treat them as authority, because everything that cites them is in another
language. Law Zero that cannot be read is not law.

---

## D7 — Evidence discipline is strong in principle and weak in schema

**Defect.** The project has excellent epistemics and no schema-level enforcement of them, so
honest artifacts and misleading artifacts are indistinguishable by shape.

**Evidence.**

| Hazard | Instance |
|---|---|
| `n=1` presented as a rate | `pass_rate_pct: 100.0`, `len(results) == 1` |
| Mock presented as measurement | `score: 1.0`, `model: cassette/golden-deterministic` |
| Simulation adjacent to live | `baac-*-lam-*` and `baac-*-live-*` in one directory, same `report.json` name |
| Preregistration adjacent to result | `PLANNED` × 115 in the same schema as executed rows |
| Two truths, one run | `live_27_attempts.json` says PASS 16; `live_27_*_report.json` says NO_PATCH 27 |
| Cost unaccounted | `cost_usd: null`, `cost_provenance: "unknown"` on all 27 rows |

**Mechanism.** The discipline lives in prose ("mechanism presence is not milestone acceptance") and
in human review, not in the writer. Any field a writer can emit without justifying, it will
eventually emit wrongly.

**Correction — cheap, blocking, highest ROI per line in this review.** Make the results schema
carry its own epistemic status, and make the writer refuse to lie:

```python
@dataclass(frozen=True)
class RunRow:
    n: int                     # sample count; a rate with n < suite_size is refused
    suite_digest: str          # content address of the frozen task set
    suite_size: int
    provenance: Literal["live", "cassette", "lam", "dry_run", "preregistered"]
    model_real: bool           # False for cassette/lam/fake — poisons every derived rate
    cost_provenance: Literal["metered", "computed", "unknown"]
    disposition: Literal["pass", "fail", "no_patch", "dataset_invalid", "undeterminable"]
```

Then: `runner.py` refuses to write `pass_rate_pct` when `n < suite_size`; any aggregate containing
a `model_real: False` row is emitted as `undeterminable`, never as a number. That is ~40 lines and
it retires the entire class of hazard above, permanently. The peer audit called this out as the
highest-ROI item in its own review; I concur and would sequence it into Sprint 1 rather than later,
because every subsequent decision in Part 5 is ranked on these numbers.

---

## Summary table

| # | Diagnosis | Cost to fix | Expected effect |
|---|---|---|---|
| D1 | Capability inversion — 5 tools | ~2 weeks | Primary determinant of pass rate |
| D2 | LDA index unwired to agent | ~1 week | Primary determinant of brownfield localisation |
| D3 | Cache breakpoints never emitted | ~2 days (+1 day test) | 60–80% prompt cost, large latency cut |
| D4 | Postcondition vs. prior restraint | ~3 days | Eliminates all 27 NO_PATCH failures |
| D5 | Sprawl from missing instrument | ~1 week | Makes every later decision decidable |
| D6 | Documentation as second product | ~3 days deletion | Returns attention to D1/D2 |
| D7 | Evidence schema does not enforce honesty | ~1 day | Prevents recurrence of the whole class |

**Total critical path: approximately four weeks, none of it touching `kernel/`.**
