# Part III — SOTA Agent Engineering, Applied to Vanguard

This part is the technical core of the review. It states what actually determines coding-agent
capability at the frontier, in priority order, and maps each item onto Vanguard's existing seams —
naming the file where it plugs in, so nothing here requires re-deriving the architecture.

The organising claim: **there are two loops, and almost all of AETHER's investment has gone into
the third thing — the substrate underneath both of them.**

```
  OUTER LOOP    program-level: many episodes deliver a roadmap
                sequencing · cross-episode memory · supervision · drift · approval
                        │ spawns bounded episodes, reads the ledger
                        ▼
  INNER LOOP    task-level: one episode solves one problem
                tools · retrieval · context · editing · verification · termination
                        │ proposes typed effects
                        ▼
  SUBSTRATE     kernel · ledger · ports · profiles · attenuation      ← 95% of the work so far
```

**Capability lives in the inner loop. Reliability at length lives in the outer loop. Trust lives in
the substrate.** You have built trust to a very high standard, and the peer reviews are correctly
pushing on the outer loop. The gap nobody has yet attacked is the inner loop, and it gates both
others — an outer loop that dispatches an inner loop which cannot patch a file multiplies zero.

---

## 1. What actually determines coding-agent performance

Ranked by effect size, from the accumulated public and internal record of coding-agent evaluation.
Percentages are directional magnitudes, not measurements of your system.

| Rank | Factor | Effect | Vanguard status |
|---|---|---|---|
| 1 | **Model capability** | dominant | Tier-2 flash by policy (see §2) |
| 2 | **Tool surface breadth & ergonomics** | very large | **5 verbs, 1 call/turn** ← D1 |
| 3 | **Edit primitive reliability** | very large | unified diff ← D4, §5 |
| 4 | **Retrieval / localisation quality** | large | regex scan; 77k-edge graph unwired ← D2 |
| 5 | **Verification loop tightness** | large | present; `AdmissionGate` now correct |
| 6 | **Context economy** (distill/compact/cache) | large at length | compiler good; distillation & cache missing |
| 7 | **Termination contract** | large (binary) | fixed by `AdmissionGate`; `derive_phase` regressive |
| 8 | **Working-set / anti-thrash state** | moderate | `chimera/search.py` has the parts, unpinned |
| 9 | **Cross-episode memory** | moderate → large on long runs | ports exist, unpopulated |
| 10 | **Sub-agent context isolation** | moderate | `spawn()` exists, unused for this |
| 11 | **Metacognitive intervention** | small → moderate | mechanism present, `undeterminable` |
| 12 | **Topology / multi-agent structure** | small, often negative | 507 LOC, unproven |

The ordering matters more than the entries. **Factors 2–5 are engineering with known answers.
Factors 11–12 are research with unproven returns.** The `.draft` corpus and the peer reports invest
heavily in 11 and 12; the measurable gap is in 2–5.

### 1.1 The model-policy problem

`models_registry.json` sets the default coding model to `deepseek/deepseek-v4-flash-0731` at
$0.14/$0.28 per MTok, with a free tier below it. Every live artifact in Part 1 was produced on
tier-1/tier-2 models, and `benchmarks/gemini_benchmark_*.json` shows `completion_tokens: 1000` —
a hard 1K output cap.

Two consequences, and they are confounds, not opinions:

1. **You cannot distinguish harness defects from model incapacity.** A cheap model at 1K output on
   a hard task fails for reasons that have nothing to do with your architecture. Twenty-seven
   `NO_PATCH` rows are *consistent with* both a broken harness and a weak model, and the run
   cannot tell you which. The peer audit's F2 hit the same wall.
2. **Harness improvements are invisible below a capability floor.** A better tool surface only
   shows up when the model is strong enough to exploit it. Optimising a harness against a weak
   model optimises for the wrong gradient — it selects for prompt hand-holding (exactly the
   `derive_phase` ladder) instead of for capability.

**Recommendation.** Keep the tiering — cost discipline is real and the registry is good design. But
**every architectural decision must be validated on a frontier model at least once.** Establish a
"capability ceiling" run: the frozen suite, best available model, generous output budget, no
`derive_phase`. That number is your harness's actual quality. The cheap-model number is your
harness's *economy*. Reporting only the second and tuning against it is how you end up with a
harness that is excellent at compensating for a bad model and mediocre at using a good one.

---

## 2. Harness engineering: the discipline

"Harness" is the whole apparatus between a model and a repository. Its quality is measured by one
question: **given a capable model, how much of its capability reaches the code?**

Five principles, each violated somewhere in the current code.

**P1 — The harness must not simulate competence the model already has.** The `derive_phase` ladder,
the "ONE tool call per turn" instruction, and the 4-binary `proc.exec` allowlist are all the harness
doing the model's thinking. Each was added to constrain a weak model; each caps a strong one.

**P2 — Every tool result is a context-economy decision.** A raw pytest traceback is ~1,200 tokens
of which ~180 matter. Ungoverned tool output is the largest source of context waste in any coding
agent. This is §7.1 and it is the highest-ROI context work available.

**P3 — Failure must be legible to the model, not just to the ledger.** A denied dispatch, a
rejected patch, a malformed proposal — each must return a message the model can act on. Vanguard
gets this structurally right (`ProposalMalformed` is an instrument error, denial is an event the
loop reduces over and continues from — `_TERMINAL_FOR_FAILURE` deliberately excludes it). This is
better than most harnesses. Preserve it.

**P4 — The harness owns the postcondition, the model owns the path.** `AdmissionGate` is P4 done
right. `derive_phase` is P4 inverted.

**P5 — Every harness parameter must be A/B-able against a frozen suite, or it is decoration.**
32 manifests exist because P5 was never enforced.

---

## 3. Prompt engineering, and the "soul" layer

### 3.1 The three-document model

Frontier practice separates three concerns that Vanguard currently fuses into
`system-prompt.txt`:

| Layer | Owns | Volatility | Vanguard home |
|---|---|---|---|
| **Soul / identity** | who the agent is, standards, refusal posture, tone, when to stop and ask | ~never | `L1`, per-pack |
| **Operating manual** | tool semantics, protocol, output discipline, phase heuristics | per release | `L1`/`L2` |
| **Project constitution** | *this* repo's conventions, build commands, invariants, gotchas | per repo | `L3`/`L4`, from `AGENTS.md` |

The third is the one that compounds and the one Vanguard lacks. `AGENTS.md` **is** a project
constitution — an excellent one — and the agent never reads it. Loading a repository's own
`AGENTS.md`/`CLAUDE.md` into `L3` is a ~30-line change with outsized effect on brownfield work,
because it converts tacit convention into stated constraint.

### 3.2 What is wrong with the current prompt

`packs/code-default/system-prompt.txt`, annotated:

```
"Exactly ONE tool call per turn."                          ← caps throughput 5×; delete (§4.3)
"Always invoke a tool ... Never reply with text"            ← symptom of no postcondition; delete
"If the workspace has no source files matching src/**"      ← branching on repo shape in the prompt
"There is no directory-listing tool"                        ← apologising for D1
"there is no `bash` or `sh` binary available"               ← apologising for D1
"argv[0] must be exactly one of: git, pytest, ruff, python3" ← apologising for D1
"include ... a complete unified diff with @@ -old,count..."  ← apologising for D4/§5
```

Roughly 60% of the prompt describes what the agent *cannot* do. Every one of those lines is a
capability gap wearing prompt clothing. **Prompt text that describes a missing tool is a bug report
in the wrong file.** Fix the tool, delete the line.

### 3.3 Positive prompt engineering that pays

Ranked, all cheap:

1. **State the postcondition, not the procedure.** "You are done when the failing test passes and
   no previously-passing test broke. Nothing else counts as done." Replaces the phase ladder with
   the actual objective.
2. **Reproduce-before-fix as a stated default**, not an enforced sequence: "Before editing, run the
   failing test to see the real error. Do not trust the task description's account of the failure."
3. **Name the anti-patterns explicitly.** "Do not add a `try/except` to make a test pass. Do not
   weaken an assertion. Do not delete a test." These are the specific reward-hacking behaviours
   that a `tests-pass` oracle invites, and `check_test_hygiene.py` already exists to catch them
   post-hoc. Say them in the prompt too — cheaper than detecting them.
4. **A worked micro-example of the edit format.** One correct `str_replace` call inline. Format
   compliance rises sharply and it costs ~80 tokens in the cached prefix.
5. **Budget awareness.** "You have ~N turns remaining" in the working-set header (§7.3) measurably
   reduces both dithering and premature abandonment.

### 3.4 On "soul"

The identity layer is not decoration; it is where *judgement standards* live, and it is the part
that transfers across every agent you will ever build on the substrate. A pack's `soul` should state
the engineering standards the agent is held to — read before you edit, verify before you claim,
prefer the smallest change that fully fixes the cause, say when you are blocked rather than
inventing. That text is worth more than any planner and it belongs in `L1` where it is cached
forever.

Concretely for Vanguard: `packs/*/soul.txt` as a first-class manifest component alongside
`system_prompt`, so identity is versioned and diffable separately from protocol. Today a preset
fork changes both at once and you cannot tell which mattered — one of the reasons the 32 manifests
are mutually incomparable.

---

## 4. Tools — the taxonomy

### 4.1 The target surface

Twenty verbs. Each is one `SinkRegistry` row, one adapter method, one JSON schema, one must-fail
test. Sink classes shown as Vanguard would classify them.

| Group | Verb | Sink | Notes |
|---|---|---|---|
| **Orient** | `glob(pattern)` | observation | **missing today; highest single win after edit** |
| | `list(path, depth)` | observation | missing; the prompt apologises for it |
| | `read(path, offset, limit)` | observation | exists; add offset/limit for large files |
| | `grep(pattern, path, glob, ctx)` | observation | exists; back it with ripgrep, not Python `re` |
| **Localise** | `symbol(name)` | observation | LDA-backed (§6) |
| | `refs(symbol)` | observation | LDA-backed — *the* brownfield primitive |
| | `defs(symbol)` | observation | LDA-backed |
| | `callers(symbol)` / `imports(path)` | observation | LDA-backed |
| | `covering_tests(path)` | observation | `IndexPort.tests()` already returns this |
| | `repo_map(budget)` | observation | exists; budget-bounded ✓ |
| **Edit** | `str_replace(path, old, new)` | privileged | **missing; replaces unified diff (§5)** |
| | `multi_edit(path, edits[])` | privileged | atomic multi-hunk; all-or-nothing |
| | `write(path, content)` | privileged | greenfield; exists as `patch.apply` w/ content |
| | `ast_patch(path, rule, rewrite)` | privileged | `tools/ast_grep_adapter.py`, unwired |
| **Execute** | `bash(cmd, timeout)` | privileged | **real shell in the sandbox**, replaces argv allowlist |
| | `bash_bg(cmd)` + `poll(id)` / `kill(id)` | privileged | servers, long suites, watchers |
| **Verify** | `test(selector)` | privileged | distilled output (§7.1) |
| | `lint` / `typecheck` | privileged | fast, cheap, high-signal |
| | `diff()` | observation | "what have I actually changed" — the anti-drift primitive |
| **Cognition** | `todo_write(items[])` | pure | externalised plan (§9.2) |
| | `spawn(goal, budget, tools)` | privileged | exists; under-used (§12) |
| | `finish(summary)` | pure | must exist in **every** preset; today it does not |

### 4.2 On the `proc.exec` allowlist

`argv[0] ∈ {git, pytest, ruff, python3}`, no shell. This must go, and the argument is the project's
own doctrine (`README.md` §10):

> "The broker grants; the sandbox contains. … A logical mediator in the host language is not
> containment."

A four-binary allowlist *inside* a rootless bubblewrap namespace with an ephemeral tmpfs workspace
is a logical mediator behind a real perimeter. It buys nothing the perimeter does not already
provide, and it costs: no `ls`, no `find`, no `cat`, no pipes, no `&&`, no `mkdir`, no test-runner
you did not anticipate, no `npm`, no `cargo`, no `go`. Every one of those is a task the agent
cannot even attempt.

The correct control is: `bash` is `privileged`, requires a descriptor-bound grant, the grant's
selector scopes it to the workspace, and the sandbox is the containment boundary. That is precisely
what S0–S12 was built to express.

**Keep the allowlist as an *optional profile*** — a `hermetic` or `paranoid` execution profile may
narrow to an allowlist, and `ExecutionProfile` already resolves into `D_R` fail-closed. That is the
right home for it: a profile, not the default.

### 4.3 Parallel tool calls

"Exactly ONE tool call per turn" is a 3–5× throughput tax. Reading five files costs five full
prompt re-sends instead of one. `openrouter.py` already parses a `tool_calls` array
(lines 451–462, 579–590) — the plural is in the wire format.

Vanguard is *better positioned* for this than most harnesses, because `VISION.md` Ch. 15 already
argues for causal partial order and the kernel already reserves per-effect budgets. The rule is
mechanical: **effects with disjoint resource selectors and observation-class sinks dispatch
concurrently; anything privileged or overlapping serialises.** `resource_selector.decide` already
computes the containment relation needed to test disjointness.

Sequence this *after* the tool surface lands and *before* the outer loop. It is the largest single
latency and cost win available after caching.

### 4.4 What not to add

- **No MCP-shaped tool explosion.** Twenty well-chosen verbs beat two hundred discovered ones. Each
  tool schema is permanent prefix cost and permanent selection ambiguity.
- **No `edit_file`-with-natural-language-instruction tool.** It moves the reliability problem into
  a second model call.
- **No web search in the coding pack yet.** Real value, but it introduces untrusted content into a
  provenance model you have built carefully (`Trust`, `SinkClass.OBSERVATION`, "content informs,
  never authorises"). Do it deliberately, later, as its own pack.

---

## 5. Editing — the single highest-leverage primitive

### 5.1 Why unified diff is the wrong choice

`patch.apply` requires `--- a/path`, `+++ b/path`, and numbered `@@ -old,count +new,count @@`
headers. This demands the model perform **line arithmetic over content it saw earlier in the
context**. Language models are unreliable at exactly this: counting lines, tracking offsets after
its own prior edits, and computing hunk lengths.

The evidence is in your own data: `NO_PATCH` 123 and `malformed` 81 (per
`dev_context_logs/context_summary.md` §3). And `forge/resilient_patcher.py` is 504 LOC of recovery
heuristics — code that exists solely to rescue a primitive the model cannot emit. **Five hundred
lines of workaround is the cost of the wrong primitive.** Change the primitive; delete the file.

### 5.2 The right primitive

```
str_replace(path, old_string, new_string)
  → old_string must appear EXACTLY ONCE in the file
  → 0 matches  : fail, "not found — re-read the file"
  → >1 matches : fail, "ambiguous, N matches — include more surrounding context"
  → 1 match    : apply
```

Every property you want falls out of this:

- **No arithmetic.** The model quotes text it can see. No line numbers.
- **Failure is clean and instructive.** Ambiguity and staleness are *rejections with actionable
  feedback*, never corrupted files. This matches P3 and Vanguard's existing "denial is an event"
  design perfectly.
- **Staleness is self-detecting.** If the file changed under the agent, `old_string` no longer
  matches and the edit is refused. That is a free optimistic-concurrency check — and it composes
  with T-16's post-write index refresh.
- **`multi_edit`** applies a list atomically: all hunks match uniquely, or nothing is written. This
  is the primitive that makes coherent multi-file refactors possible.

Retain unified diff as an accepted *input* format for compatibility. Make `str_replace` the
documented default and the one the prompt exemplifies.

> **Divergence from `docs/research/theory/SOTA_AGENTIC_CODING_HARNESS_ENGINEERING_TREATISE.md` §5.1.**
> The treatise proposes a nine-strategy cascade that progressively relaxes whitespace, indentation,
> and line endings until a match succeeds. Strategies 1–2 (exact, then line-trimmed end-of-line
> whitespace) are safe and worth keeping. Strategies 3+ are not: in Python, YAML, and every
> indentation-sensitive language, **indentation is semantics**, so "whitespace-normalized" and
> "indentation-flexible" matching can apply a syntactically valid edit at the wrong nesting level
> and change behaviour with no error raised. That converts a loud failure into a quiet one, which
> is the worse trade for an autonomous agent.
>
> The treatise's own F1 case study supports this reading: the destructive outcome was the model's
> **fallback to a whole-file overwrite** after rejection — it replaced a 200-line module with a
> 20-line snippet — not the rejection itself. The failure was in the recovery path.
>
> The three fixes that address F1 without relaxing matching semantics:
> 1. **Rejection re-shows the current file region**, so the model corrects against reality rather
>    than against its recollection. A rejection with no fresh observation invites exactly the
>    "the file must have changed" spiral the treatise documents.
> 2. **Parse-preflight before commit** (§5.3) — a broken result is rejected and the file is never
>    written, so no cascade can corrupt a module.
> 3. **Whole-file `write` is not a recovery path for an existing file.** It is a greenfield verb.
>    Removing it as an escape hatch removes the mechanism by which F1 became destructive.
>
> With those three, most of the cascade is unnecessary, because the exact-match failure rate on
> quoted text the model can see is far lower than on line-numbered diff arithmetic.

### 5.3 AST-level editing — where it belongs

`tools/ast_grep_adapter.py` is written and wired to nothing. AST editing is the right primitive for
a *narrower* class than people expect:

**Use AST for:** rename symbol across N files · change a signature and all call sites · add a
parameter with a default everywhere · mechanical API migration · "wrap every call to X in Y". These
are pattern-and-rewrite operations where correctness is structural and the edit count is large.

**Do not use AST for:** the ordinary single-site bug fix. `str_replace` is faster, cheaper, more
predictable, and does not require the model to author an ast-grep rule correctly.

The relevant note from commit `5c9870f0` — *"adapter 2PC; AST preflight; no kernel AST"* — is the
right call and worth restating: **AST semantics belong in the adapter, never in the kernel.** The
kernel classifies `patch.apply` as privileged and checks the selector; it must not know what Python
is. An AST *preflight* in the adapter (parse the result before committing the write) is the correct
place to reject a syntactically broken edit, and it is cheap: a failed parse becomes a rejection
event with a real error message, and the file is never left broken.

That preflight generalises beautifully and should be a standing rule: **`write`/`str_replace`/
`ast_patch` on a file whose language has a parser must parse-check the result before commit.** It
converts an entire class of "agent broke the repo" into an instructive rejection.

---

## 6. Retrieval — index, search, and graph engineering

### 6.1 Do not build embeddings

An explicit recommendation against the obvious move. Vector search over code chunks is
systematically inferior to structural search plus agentic exploration, because code identity is
*exact* (a symbol name either matches or it does not), code relationships are *typed* (call,
import, define, test-covers), and chunk boundaries destroy the syntactic structure that carries the
meaning. Frontier coding agents navigate with grep, glob, and reading — not with cosine similarity.

You are in a stronger position than that: **you have the graph.** 77,610 typed relations is a
better retrieval substrate than any embedding index, and it is already computed. Building a vector
store would be replacing an asset with a downgrade.

*(One narrow exception: retrieval over *natural-language* memory — `doc_sections`, past episode
summaries, skill descriptions — where semantic similarity genuinely helps. Even there, FTS5 over
5,073 doc sections is likely sufficient and it is already indexed.)*

### 6.2 The graph as the localisation engine

The brownfield task is fundamentally a **localisation problem**: find the ≤5 files that matter out
of 3,347. The path a competent engineer takes is:

```
failing test name
  → covering_tests⁻¹ → the source file under test
  → symbol(name) → definition site
  → refs(symbol) → every call site
  → imports(path) → the blast radius of a signature change
  → read those, and only those
```

Every edge on that path exists in `.lda/index.db`. None of it is reachable from an episode. This is
D2, and it is the difference between a 13,668-token grep spray and a 2,000-token targeted read.

**Implementation shape**, respecting the existing lattice:

```
vanguard/packages/adapters/stores/lda_index.py
    class LdaRepoIndex:              # implements ports.index.IndexPort — unchanged port
        def __init__(self, db_path, *, source_revision): ...
        def symbols(self, *, name="", path="") -> Result[Sequence[Symbol]]
        def dependencies(self, *, path="")       -> Result[Sequence[DependencyEdge]]
        def tests(self, *, path="")              -> Result[Sequence[TestAssociation]]
        def repo_map(self, *, token_budget=4000) -> Result[RepositoryMap]
```

Three properties to preserve, all already specified in the port's own docstring:

1. **`RepositoryMap` carries `source_revision`, `tree_hash`, `index_digest`, `truncated`.** A stale
   index must be *detectably* stale, not silently wrong. T-45's honest-fallback rule ("never invent
   a silent map") already governs this and is the right rule.
2. **The index returns values, never handles.** "A caller cannot reach back through a symbol into
   the indexer's state." Keep this.
3. **The index proposes nothing.** The port docstring's warning — *"a retrieval component that
   decided what the agent should look at next would be a second policy wearing the word 'index'"* —
   is a better statement of retrieval design than most published work on the subject. Do not build a
   ranker that pre-selects context. Give the agent the graph and let it walk.

Point 3 is worth dwelling on, because it is where most "agentic RAG" designs fail. The moment
retrieval starts deciding relevance, you have two policies competing, and the agent's own hypothesis
— which is usually better informed than any static ranker — gets overridden. **Agentic retrieval
means the agent issues the queries.** Your port already forbids the alternative.

> **Divergence from `docs/research/theory/SOTA_AGENTIC_CODING_HARNESS_ENGINEERING_TREATISE.md` §8.1.**
> The treatise proposes Personalized PageRank over the LDA graph (`α = 0.85`, BM25-seeded) which
> "automatically boosts `governor.py` … and `test_limiter.py` … into the model's `L2` context
> window." The ranking function is genuinely good. The *injection target* is wrong, on two
> independent grounds:
>
> - **Architecturally**, it is the second policy `ports/index.py` forbids by name. A ranker that
>   decides what enters context has taken over the episode's job, and when its guess is wrong the
>   agent has no way to notice — the alternatives were never surfaced.
> - **Mechanically**, it forfeits the cache. `agency/context/layers.py` documents that `L2` sits
>   *inside* the prefix, and `context/compiler.py` states that anything appended to `L1`–`L4`
>   mid-run destroys every downstream cache hit. Per-turn PPR injection into `L2` mutates the
>   prefix on every turn, discarding the ~90% saving the same treatise advocates in §6.1. The two
>   sections are in direct conflict.
>
> **The reconciliation is small and keeps all the value:** PPR becomes the ranking function *behind*
> an agent-issued query — `refs(symbol)` and `callers(symbol)` return PPR-ordered results — and the
> results land in `L5`, outside the prefix. The agent still decides what to look at; the graph still
> decides what is most relevant *within* what was asked for; the cache survives. This is also the
> only version that is A/B-able, because ranking quality becomes a measurable property of a tool
> rather than an invisible property of context assembly.

### 6.3 Index freshness

T-16 ("refresh index after write so the next compile is not a pre-write map") is correct and
important. Two additions:

- **Incremental, not full rebuild.** 3,347 files re-scanned after every edit is unaffordable at
  turn granularity. Re-index the changed paths and their reverse-dependency closure. The `relations`
  table gives you that closure directly.
- **Epoch-bind the map to the packet.** Commit `587db91a` ("epoch-bind packets; stale packet cannot
  complete") already establishes the mechanism. Extend `WorkspaceEpoch` to cover the index digest so
  a compile cannot silently mix a fresh workspace with a stale map.

### 6.4 Search itself

`fs.search` uses Python `re`. Replace with ripgrep: 10–100× faster on a real tree, gitignore-aware
by default, `--glob` filtering, `-A/-B/-C` context, and multiline support. Then add the two
ergonomics that matter most for context economy:

- **Cap hits per file** (default ~5) and report the elision. One match in twenty files beats twenty
  matches in one file for localisation, and un-capped grep output is a top-three source of context
  flooding.
- **Return `path:line: text` triples**, never raw blobs — so a search result is ~15 tokens per hit
  instead of a paragraph.

---

## 7. Context management — compress, compact, cache, place

This is the area where Vanguard's existing code is strongest and its gaps most surgical. Five
distinct problems that are routinely conflated. The peer report
`../octopus/agents/long-horizon-context-engine.md` separates them correctly and I adopt its
taxonomy, with additions.

| # | Problem | Symptom | Solution | Status |
|---|---|---|---|---|
| P1 | Turn-level bloat | raw tool output floods `L5` | **distillation at the effect boundary** | missing |
| P2 | Attention dilution | 40k present, wrong 3k attended | placement + working-set header | partial |
| P3 | Cache destruction | prefix mutates, cost 10× | layer discipline | **solved, unclaimed** (D3) |
| P4 | Cross-episode amnesia | episode 7 re-derives episode 2 | durable memory | ports only |
| P5 | Repo scale | 3,347 files, budget for 30 | retrieval + skeletonisation | ← D2 |

### 7.1 P1 — Distillation at the effect boundary (build this first)

The single distinction that makes context management tractable:

> **Distillation is lossy-on-write and cheap. Compaction is lossy-on-overflow and expensive.**

Today `proc.exec` output lands in `L5` roughly raw, and `ResultEvictionStrategy` only acts when the
ceiling is already breached. By then the damage — attention dilution, cache churn, cost — is done.
Distilling at the boundary means the ceiling arrives far later or never.

```python
class ResultDistiller(Protocol):
    def distill(self, verb: str, payload: Mapping[str, Any]) -> DistilledResult: ...

@dataclass(frozen=True)
class DistilledResult:
    text: str            # what enters L5
    full_digest: str     # content address of the original — retrievable on demand
    tokens_saved: int
```

**The load-bearing rule: never destroy, always address.** `full_digest` plus an `expand(digest)`
verb means aggressive distillation is *safe* — the agent can retrieve the full traceback if it
genuinely needs it. Without addressability, distillation is data loss and you will be forced to be
timid. With it, you can be ruthless.

Distillers in ROI order:

| Verb | Distillation | Typical |
|---|---|---|
| `test` / pytest | exit code, pass/fail counts, first 3 failing ids, assertion line + message. Drop frames below the assertion, collection noise, warnings, timing tables. | 1,200 → 180 |
| `read` | for large files: skeletonise — imports, class/def signatures, docstring first lines, with line numbers. Full body only on explicit `read(offset, limit)`. | 3,000 → 400 |
| `grep` | dedupe by file, cap hits/file, `path:line: text` | 2,000 → 300 |
| `bash` (git diff) | `--stat` plus hunk headers; bodies on demand | 4,000 → 200 |
| default | head/tail with an explicit elision marker | — |

`forge/engine.py` already contains `parse_test_output`. It is used for admission decisions and not
for shrinking context. Reuse it as the pytest distiller — this is a wiring job, not new code.

Register distillers per-verb in a manifest `distillation-policy.json`, so it is pack-configurable
and A/B-able, with a conservative default for unknown verbs.

### 7.2 P3 — Cache: claim what you already built

Order of operations matters here, and getting it wrong wastes the work:

1. **First, add the prefix-stability regression test.** Assert that the rendered digest of
   `PREFIX_LAYERS` is byte-identical across every turn of a multi-turn run. The invariant is
   currently a docstring, and `_schemas_with_aliases` (D3) is a live drift risk. *A cache
   breakpoint on a drifting prefix is worse than no cache: you pay the write cost and never hit.*
2. **Then extend `ContextBundle`** to carry breakpoint positions across the `ModelPort` boundary.
   The compiler knows them; the adapter needs them; today nothing transports them.
3. **Then emit them** in `openrouter.py`, and record `prefix_tokens` / `volatile_tokens` /
   `cached_tokens` separately in the run receipt.

Point 3's reporting split is not cosmetic. Right now a run reports total tokens, which cannot
distinguish "expensive because the work was hard" from "expensive because the cache missed." After
the split, cache regressions become visible in ordinary benchmark output instead of invisible
forever.

Additional caching layers worth having, in order: **tool-result cache** keyed on
`(verb, args_digest, workspace_epoch)` — a re-read of an unchanged file should never cost a second
provider round trip; and **index cache** keyed on `tree_hash`.

### 7.3 P2 — Placement and the working-set header

Two cheap mechanisms.

**(a) Salience-ordered `L5`.** Attention degrades in the middle of long contexts — your own
`benchmark_20_suite/07_context_lost_in_middle_prune` exists to measure exactly this. So order
within `L5`: *most salient adjacent to the generation point*, stale-but-retained in the middle,
task-critical invariants pinned in `L4` and never in the middle of dialogue. `layers.py` renders in
layer order already; this adds an intra-`L5` sort key.

**(b) The working-set header** — the highest value-per-token construct in this entire review. One
pinned block, regenerated every turn, ~80 tokens:

```
WORKING SET (turn 14/40 · $0.021 of $0.25 · 31k/64k tok)
  goal:      make test_lease_expiry pass without breaking test_clean_expired
  changed:   lru/cache.py (2 hunks), lru/entry.py (1 hunk)
  verified:  FAILING — test_lease_expiry: 80 != 100  @ test_limiter.py:45
  rejected:  [t7]  widening the TTL window        → broke test_clean_expired
             [t11] clearing on read               → same failure signature
  next:      inspect Entry.expires_at initialisation
```

Why it works: **the dominant long-session failure mode is an agent re-attempting a path it already
falsified.** Compaction evicts the evidence of failure while the *impulse* that produced it — the
task description — stays pinned. So the agent loops. A durable, pinned `rejected` list breaks the
cycle for ~30 tokens.

`chimera/search.py` already has `distill_trajectory_summaries` producing dead-end summaries. Promote
its output from "occasionally compiled in" to "always pinned in `L4`". Again: wiring, not new code.

### 7.4 P4 — Compaction that summarises rather than elides

Current `ResultEvictionStrategy` replaces a block with:

```
[{label} from {source}: {bytes} bytes elided after use]
```

This preserves *that a read happened* and discards *what was learned*. The receipt is
epistemically honest — commendably so — and operationally useless.

Replace with summarise-on-compact:

```
[read src/lru/cache.py — LRUCache.evict() at :88 uses OrderedDict.popitem();
 no TTL check on read path; Entry.expires_at set only in __init__ · full: sha256:a3f…]
```

Same token cost, carries the finding, and remains addressable. Then — and this is the part that
serves the Vision — **emit a `ContextCompacted` event with input digest, output digest, compactor
identity, and parameters.** `schemas/mhf/context_compacted.schema.json` already exists.
`VISION.md` Ch. 17 demands exactly this:

> "Se uma compaction alterou o contexto, registre source range, compactor identity, relevant
> parameters, input digest e output digest."

That closes the loop between the context engine and the scientific programme: compaction strategy
becomes an A/B-able variable with a durable record, instead of an invisible behaviour.

### 7.5 The rolling handoff

At ~70% budget, generate a structured handoff and start a fresh window from it:

```
HANDOFF (episode continues · turn 28 → 1)
  goal / acceptance:  <verbatim from brief — never summarised>
  established facts:  <what is known about the code, with file:line>
  changed:            <files + hunks, from the ledger, not from memory>
  verified:           <last receipt: command, exit code, test counts>
  falsified:          <paths proven not to work, with reasons>
  open hypothesis:    <current theory>
  next action:        <one concrete step>
```

Two rules. **The brief is copied verbatim, never summarised** — `VG-03 §10.5` already gets this
right ("work is checked against the brief, never against the last summary of it"), and it is the
most common way long-running agents drift. And **`changed` and `verified` are derived from the
ledger, not from the model's recollection** — the ledger is the authority, and this is precisely
what event sourcing was built to make possible. Most frameworks cannot do this correctly. You can.

This is the mechanism that turns a 40-turn ceiling into an effectively unbounded session, and it is
the natural bridge into the outer loop (§11).

---

## 8. Memory — five tiers, honestly separated

Most "agent memory" designs fail by conflating tiers with different lifetimes, authorities, and
failure modes. The separation that works:

| Tier | Substrate | Lifetime | Authority | Vanguard status |
|---|---|---|---|---|
| **Working** | `L5` dialogue | one turn | volatile | ✓ implemented |
| **Episodic** | ledger + `ContextCompacted` notes | one run, replayable | derived fact | ledger ✓, notes ✗ |
| **Semantic** | LDA graph + FTS | repo lifetime, rebuilt on change | projection | built, **unwired** (D2) |
| **Procedural** | skills, promoted from trajectories | cross-run, versioned | governed | ports ✓, empty |
| **Durable / stated** | `AGENTS.md`-shaped project facts | cross-run, human-editable | human-authored | ✗ not loaded |

Ports exist for all five. Two are populated.

### 8.1 Short-term memory is a *retention* problem, not a storage problem

Within an episode, nothing needs a database. What is needed is a decision about *what survives
compaction*, and that decision is a policy: pin the brief and invariants (`L4`, done), pin the
working set (§7.3), distil results (§7.1), summarise on compact (§7.4). Every one of those is a
retention rule. **If you find yourself adding a store for short-term memory, the retention policy
is wrong.**

### 8.2 Long-term memory: the only two kinds that pay

Long-term memory is where agent frameworks accumulate the most machinery and the least return.
Two kinds earn their cost:

**(a) `falsified` — paths proven not to work.** The peer report calls this "the crown jewels" and
that is correct. It is worth more than a record of what succeeded, because **success is visible in
the code and failure is not.** An episode that knows "widening the TTL window breaks
`test_clean_expired`" does not spend six turns rediscovering it.

It is derivable **for free** from the ledger with no LLM call: every `patch.apply` followed by a
non-zero `proc.exec` receipt, paired with the diff and the failure fingerprint. `forge/engine.py`
already computes `FailureFingerprint`. This is the single best return on the event-sourced design
you have already paid for, and nothing currently reads it back.

**(b) Interface and convention facts.** "`EventStorePort.append` returns `Result`, never raises."
"Tests live in `test/`, mirroring the package path." "`uv run`, never bare `python3`." These are
what `AGENTS.md` contains and what a new episode otherwise spends four turns rediscovering. Load
them into `L3` as stated constraints.

What does *not* pay: general-purpose "remember everything the agent said" stores, conversational
recall across unrelated tasks, and vector memory over trajectories. They cost prefix tokens on
every turn and pollute retrieval with stale, low-precision context.

### 8.3 The `EpisodeMemory` record

Adopting the peer report's shape, with the authority annotations that matter:

```python
@dataclass(frozen=True)
class EpisodeMemory:
    episode_id: str
    package_id: str
    intent: str                          # one sentence
    interfaces_touched: tuple[str, ...]  # from the ledger's write receipts — NOT self-reported
    decisions: tuple[Decision, ...]      # {choice, rationale, alternatives_rejected}
    falsified: tuple[Falsified, ...]     # {approach, evidence_digest, failure_fingerprint}
    artifacts: tuple[ArtifactRef, ...]
    verification: VerificationReceipt | None
    tokens: int                          # target < 400
```

The critical discipline: **fields derivable from the ledger are derived, never asked of the model.**
`interfaces_touched`, `artifacts`, and `verification` come from effect receipts. Only `intent`,
`decisions`, and the prose of `falsified` need a model. A memory record that trusts the model's
self-report of what it changed will drift, and drift in memory is worse than no memory — it is
confidently wrong context, permanently.

---

## 9. Skills, plans, and learning

### 9.1 What a skill is

A skill is a *retrieved procedure*: a named, versioned fragment describing how to do a recurring
task in this codebase, loaded on demand rather than resident in the prefix. `domain/artifacts/
skill_index.py` has exactly the right shape:

```python
class SkillCard:
    skill_id: str; name: str; description: str; body_path: str
    def index_line(self) -> str: return f"- {self.skill_id}: {self.name} — {self.description}"
```

This is the progressive-disclosure pattern and it is correct: the **index line** (~15 tokens) sits
in the prefix; the **body** loads only when selected. Ten skills cost 150 prefix tokens and buy
ten procedures. That economy is what makes skills scale where a monolithic prompt does not.

`packs/code-default/skills/pytest-green.json` exists. One skill. The catalogue that would earn the
machinery does not exist yet, and the natural first entries are the procedures your own contributor
docs already describe: *add a pack or tool*, *add an adapter or provider*, *add an event kind*, *run
the qualification gate*, *investigate a failing falsifier*, *bisect a regression*.

### 9.2 Plans: `todo_write` is a cognitive tool, not bookkeeping

An externalised, rewritable task list does three things no prompt instruction achieves:

1. It **survives compaction** (pinned in `L4`), so long-horizon intent does not decay.
2. It **forces decomposition before action** on multi-file work — the failure mode on greenfield
   tasks is a model trying to hold six files in working memory at once.
3. It is **legible to a supervisor** (§11) without reading a transcript.

This is one small tool with outsized effect on exactly the two workloads named in the mandate:
greenfield multi-file, and long-running brownfield.

### 9.3 Learning without touching weights

`VISION.md` Ch. 18 states the discipline and it is right:

> "o agente pode **propor** uma skill, mas não deve declarar unilateralmente que ela é melhor.
> Promotion precisa utilizar avaliação explícita, provenance e rollback."

The lifecycle: `run → trajectory → pattern → candidate skill → held-out evaluation → promote or
reject → rollback available`. `runtime/skill_evaluation.py` (622 LOC) and
`runtime/governance/learning.py` (664 LOC) implement this. Both have **never had a workload to run
against**.

That is the real state of learning in this project: not unbuilt, but unfed. It is downstream of the
benchmark suite (§14), which is downstream of Sprint 3. **Do not touch the learning engine until the
suite exists** — it cannot function without one, and a promotion decision made on n=1 evidence is
worse than no promotion mechanism at all.

---

## 10. Cognition and metacognition

### 10.1 The correct architectural position

`VISION.md`: **"Metacognition is policy/reducer/plugin, never a kernel primitive."** Correct, and it
resolves the tension the CONDUCTOR peer report raises. The reasoning-about-execution layer is not
homeless — it is a **reducer over the ledger**, which is precisely the structure event sourcing
exists to enable. It needs no new core and no new framework.

### 10.2 Make it cheap or it will not run

The `ProgressVector` from `../octopus/agents/meta-conductor.md` is well-designed, and its decisive
property is that **every component is computable from the ledger with no model call**:

```python
verification_delta   # tests passing now − at checkpoint            [-1..1]
novelty              # 1 − repeated action signatures / actions      [0..1]
scope_fidelity       # |touched ∩ declared| / |touched|              [0..1]
evidence_freshness   # turns since last verification receipt          int
budget_burn          # spent / allocated                             [0..1]
convergence          # 1 − distinct failure fingerprints / attempts  [0..1]
```

An LLM-based supervisor that costs a model call per turn will be disabled for cost and will
hallucinate its diagnoses. A pure fold over events costs microseconds and cannot hallucinate. This
is the right design and it should be built as a reducer in `domain/ledger/`, testable with zero
model calls.

`scope_fidelity` deserves emphasis: **an agent writing outside its declared boundary is out of
scope by definition, readable straight off the write receipts, requiring no judgement.** That is the
one anti-hallucination signal that is free and exact. Everything else is heuristic.

### 10.3 Intervention: start with one

The peer report's closed pathology vocabulary is the right *shape* — an open-ended "the supervisor
decides what's wrong" design is untestable and drifts. But I differ on sequencing. Eight pathologies
× eight interventions is 64 untested interaction pairs shipped simultaneously, and you will not be
able to attribute any resulting change.

**Ship one, measure it, then add the second.** The one to ship first is `THRASHING`, because it is
the most frequent, the cheapest to detect, and the cheapest to treat:

```
detect:     novelty < 0.3 over 3 turns   (repeated action signatures)
intervene:  inject ONE L5 block —
            "You have attempted {k} actions with no new information and no
             workspace change. Falsified so far: {falsified}. State your current
             hypothesis and what observation would disprove it."
measure:    paired A/B on the frozen suite — with-nudge vs without
```

~150 LOC, one variable, a decidable experiment. If it wins, add `BLIND`
(`evidence_freshness > 3`). Then `WON_BUT_UNAWARE`.

`WON_BUT_UNAWARE` warrants specific mention because the peer report identifies it as empirically the
most frequent failure here (18 of 26 oracle passes ending `abandoned`), and it corroborates my own
independent finding from a different direction: `live_27_attempts.json` records PASS 16 while the
report rows record NO_PATCH 27. **The agent solving the problem and then failing to declare victory
is a recurring, expensive, and entirely fixable failure.** The fix is not metacognition — it is
`finish` existing in every preset (it is absent from `vg-code-max`) plus the working-set header
showing `verified: PASSING`. Fix it there, not in the supervisor.

### 10.4 What metacognition is *not* for

Not for choosing tools (the model is better at that), not for planning (`todo_write` externalises
it more cheaply), not for judging code quality (that is the evaluator, and it must stay outside —
"the verifier is outside everything"). Metacognition is for exactly one thing: **noticing that the
current approach is not working, and interrupting it.**

---

## 11. The outer loop and the decoupled supervisor

The peer report `../octopus/consolidation/outer-loop-orchestrator.md` is the strongest document in
the review corpus. Its core moves are right: the kernel does not change; `orch.*` events go in the
**same** ledger; the Director reads compacted evidence and never raw transcripts; the Director gets
no write tools; Strategy A is the control condition; LDA is extended rather than forked. I endorse
all of it.

I have one structural amendment and one sequencing objection.

### 11.1 Amendment — the supervisor is a ledger consumer, not a layer

The proposal places the orchestrator as "layer 3.5" in the precedence ladder, with a `Dispatcher`
that owns `HarnessSession` spawning. That makes the outer loop *in-process* and *above* the
substrate. I would invert it:

> **The supervisor is a separate process that tails the event ledger and appends intents. It is not
> a layer above the runtime; it is a peer that reads facts and writes proposals.**

Why this is materially better, and why your architecture uniquely supports it:

- **It cannot corrupt a run.** Kill the supervisor mid-flight and episodes continue. A supervisor
  that owns dispatch is a new single point of failure over a system whose entire selling point is
  process-independent continuation.
- **It is testable with zero model calls and zero episodes** — a pure function from an event stream
  to a decision, replayable against recorded ledgers you already have.
- **It gets crash recovery for free.** Restart, fold the ledger, resume. This is `RF-25` applied one
  level up, and it requires no new machinery.
- **Multiple supervisors compose.** A drift monitor, a budget kill-switch, and a Director can be
  three independent tailers with no coordination, because the ledger is the only shared state.
- **`LedgerEmitter` single-writer already makes it safe.** The supervisor appends `orch.*` intents;
  a dispatcher process consumes them and spawns. Authority and effect stay split, one level up —
  exactly the property the peer report identifies as the design's virtue, achieved structurally
  rather than by convention.

This is a ~300-LOC process that yields live dashboards, stuck-run detection, budget enforcement,
and multi-run orchestration. **It is the single most under-exploited consequence of the
event-sourced design you have already paid for.** Almost no other agent framework can do this at
all, because almost none has a durable causal record to tail.

### 11.2 Objection — sequencing

The peer corpus proposes M-O1…M-O5 (event contract → SequentialDirector → Compactor → Director →
Evolutionary) on top of the current inner loop. My objection is arithmetic:

**An outer loop that dispatches an inner loop with a 7% pass rate produces a 7% roadmap.**
Sequencing, supervision, and cross-episode memory multiply the inner loop's success probability;
they do not add to it. Every hour spent on M-O1 before Sprint 1 is an hour spent building a
multiplier for a number near zero.

There is also an attribution hazard: build the outer loop first and you will never know whether a
later improvement came from the Director or from the tool surface, because both changed.

**Revised sequencing:** Sprint 1–3 (tools, index, cache, postconditions, benchmark) → then
M-O1/M-O2 (event contract + SequentialDirector) → then M-O3 (LDA-backed Compactor) → then M-O4
(Director). Strategy C (evolutionary) stays where the peer report correctly puts it: last, opt-in,
and only on packages with a numeric evaluator.

### 11.3 Rolling handoff is the bridge

§7.5's handoff and the peer report's `Compactor.compact_episode()` are the *same mechanism* at two
scales. Build it once, in `agency/context/`, and let the outer loop consume it. Building an
episode-level handoff and a package-level compactor separately is the sprawl the anti-sprawl rules
warn about.

### 11.4 Interactive vs autonomous

The peer report's `ApprovalPolicy` as **data, not code branching** (`interactive` /
`autonomous` / `hybrid`, with `hybrid` default and named escalation triggers) is exactly right and
maps cleanly onto `runtime/governance/approvals.py` (618 LOC), which already implements Ed25519
human approval. Nothing new is needed structurally — only the trigger vocabulary.

---

## 12. Sub-agents, topologies, and multi-agent structure

### 12.1 The real reason to spawn

`spawn()` exists (`episode/engine.py`, S8-B-01) with monotonic attenuation and budget conservation,
returning a value-only `SpawnResult`. That is a correct and well-built primitive being used for the
wrong purpose.

The dominant value of a sub-agent is not parallelism and not specialisation. It is **context
isolation**: a child burns 50,000 tokens exploring a question and returns 500 tokens of answer. The
parent's context never sees the search.

That single property is what makes large-repository work tractable:

```
parent (goal: fix the flaky lease test, 8k context)
  ├── spawn("find every call site of Lease.renew and report file:line + call shape")
  │        → child burns 40k tokens across 60 files, returns 300 tokens
  └── spawn("read test/runtime/test_lease.py and report the exact assertion that fails and why")
           → child burns 15k, returns 200 tokens
```

`SpawnResult` being value-only ("never carries a mutable engine handle") is precisely the property
that makes this safe. You built the hard part. Use it for what it is good for.

### 12.2 Topologies: the honest assessment

`runtime/topology.py` is 507 LOC and `M-7` gates on "three real artifact-producing topologies."
Directionally, this is the lowest-return item on the roadmap, and the evidence for that is in your
own tree: `vg-code-critic-reviser` exists as a preset and has never beaten `vg-code-default` on any
measured comparison, because no such comparison exists.

The general finding across the field is that fixed multi-agent topologies (planner→executor,
critic→reviser, debate) **underperform a single strong agent with good tools** on coding tasks. They
add latency, cost, and a lossy hand-off boundary at which context is dropped. The exceptions are
narrow and real: verification by an *independent* process (which you have, correctly, as the
exterior evaluator), and fan-out where sub-results are genuinely independent (which is §12.1).

`VISION.md` Ch. 16's separation of topology (structure) from scheduler (time) is theoretically
clean, and I would keep the concept. But `M-7` should be **demoted below the inner-loop work and
gated on evidence**: build a topology only when a measured failure on the frozen suite is
attributable to the absence of one. `ADR-0092`'s framing — a measurement lane that ends in an
explicit implement/simplify/cancel decision — is the right instrument. Apply it to `M-7` itself.

---

## 13. Modularity, plugins, and what actually compounds

### 13.1 The two-tier model is right

`packs/` (declarative composition) over `adapters/` (concrete capability) over `ports/`
(interfaces), with a JSON-Schema + JCS wire as the narrow waist between languages, and the kernel
domain-blind above all of it. This is a genuinely good extensibility architecture and I would not
change its shape.

### 13.2 What went wrong in practice

The failure is not the model; it is that **the composition unit is too coarse and there is no
inheritance.** A preset must name every component file, so varying one thing means copying twelve
paths (Part 1 §2.6). Composition-by-copy is not composition.

The fix is small and mechanical:

```json
{
  "harness": "vg-code-max-v3luna",
  "extends": "vg-code-default",
  "overrides": {
    "system_prompt": ["vg-code-max-v3luna/system-prompt.txt"],
    "tools": { "add": ["shared/finish-tool.json"] },
    "components": { "remove": ["repo_index"] }
  }
}
```

Now a preset's diff *is* its hypothesis. `diff` between two manifests becomes readable, an
ablation becomes a one-line change, and the 32 forks collapse to a base plus 31 short deltas —
most of which will visibly be duplicates and can be deleted on sight.

Shared component files (`shared/read-tool.json`, `shared/finish-tool.json`) eliminate the
duplication class entirely.

### 13.3 What compounds and what does not

| Compounds | Does not |
|---|---|
| Tools — each one multiplies every future agent | Presets — each one divides attention |
| The index — one graph serves every agent and every task | Topologies — each is a fixed shape for one problem shape |
| Distillers — one per verb, forever | Prompts — per-agent, decay with model generation |
| Skills — accumulate as a catalogue | Engines — each is a fork of the same loop |
| The benchmark suite — every task added makes every future decision sharper | Reports — accumulate as noise |
| The ledger schema — every event kind enriches all analysis | Documentation of unbuilt things |

Read that table against Part 1's inventory: the left column is thin (5 tools, 1 skill, no
distillers, no frozen suite) and the right column is thick (32 presets, 3 engines, 50 reports,
59k lines of docs). **Reversing that ratio is the whole of this review's practical advice.**

---

## 14. Logs, trajectories, and benchmarking

### 14.1 The three-artifact discipline

Right now `benchmarks/` mixes all three of these, which is why Part 1 §1.1 was necessary:

| Artifact | Purpose | Lifetime | Where |
|---|---|---|---|
| **Log** | debugging one run | days; disposable | `.vanguard/`, gitignored |
| **Trajectory** | scientific record of one run | permanent, content-addressed | ledger + blob store |
| **Measurement** | one row of an experiment | permanent, aggregate-able | one append-only `results.jsonl` |

`report_v3a…report_v3j` are **logs committed as measurements**. That single category error produces
the unsearchable evidence directory, the n=1-beside-n=21 hazard, and the impossibility of
comparison.

### 14.2 The benchmark instrument

The missing instrument, in full. This is Sprint 3 and it is the item that makes every other decision
decidable.

**One frozen suite.** 40–60 tasks, content-addressed, committed, with a `suite_digest`. Composition:

| Class | n | Purpose |
|---|---|---|
| Brownfield single-file repair | 15 | the core competency; real oracles |
| Brownfield multi-file / cross-module | 10 | localisation + blast radius (needs D2) |
| Greenfield single-file | 8 | generation from spec |
| Greenfield multi-file project | 6 | decomposition, `todo_write`, long horizon |
| Long-horizon (>25 turns expected) | 5 | context economy, handoff, anti-thrash |
| Adversarial / trap | 6 | tests that pass on a stub; oracles that reward weakening assertions |

`benchmark_20_suite` and `frontier_v090/fixtures` are ~80% of the way to this already. The last
class matters most and is usually skipped: `check_test_hygiene.py` and T-19 ("reject greenfield
oracles that pass on stubs") show you already understand the failure mode.

**One runner. One results file.** Append-only `benchmarks/results.jsonl`, one row per
(config × task × attempt):

```json
{"ts":"…","suite_digest":"sha256:…","suite_size":44,"n":44,
 "config":"vg-code-default@a3f2","config_digest":"sha256:…",
 "task_id":"bf-07","task_digest":"sha256:…",
 "model":"…","model_real":true,"provenance":"live",
 "disposition":"pass","turns":7,
 "tokens_prefix":9100,"tokens_cached":8800,"tokens_volatile":2400,"tokens_out":1850,
 "usd_micros":2677,"cost_provenance":"metered","wall_s":41.2,
 "terminal":"completed","terminal_reason":"verified",
 "changed_files":["…"],"trajectory_ref":"sha256:…"}
```

Every field there is either already computed somewhere in the codebase or trivially derivable. The
`tokens_prefix`/`tokens_cached`/`tokens_volatile` split (§7.2) is what makes cache regressions
visible.

**One comparison command.** `bench compare A B --suite <digest>` → paired McNemar over the tasks
both configurations ran, plus per-task deltas. `benchmarks/statistics.py` and
`runtime/paired_evaluation.py` already implement the mathematics. **The statistics are done and
there is no dataset.** This is the gap.

### 14.3 Rules the writer must enforce

Not conventions — code. This is D7:

1. `pass_rate` is refused when `n < suite_size`.
2. Any aggregate containing a `model_real: false` row is emitted as `undeterminable`, never a rate.
3. `provenance` ∈ {live, cassette, lam, dry_run, preregistered} is mandatory; `dry_run` and
   `preregistered` rows are excluded from every rate by construction.
4. `cost_provenance: "unknown"` on a live row is a warning in the report header, not a silent null.
5. One results file. A new `*_report.json` in `benchmarks/` should fail a lint.

### 14.4 Trajectories as the scientific asset

This is where AETHER can be genuinely ahead. A trajectory here is not a chat transcript — it is a
**causally ordered, digest-linked, replayable event sequence** with model I/O, selected context,
effect intents and receipts, budget draws, and compaction operations. `VISION.md` Ch. 3's
replay/re-execution distinction is exactly right and rarely stated so clearly.

What that unlocks, in ascending order of value:

1. **Deterministic regression testing** via cassettes — you have this.
2. **Ablation by replay-with-substitution:** hold the trajectory fixed to turn 11, then vary one
   thing (model, compaction policy, retrieval depth) and re-execute forward. This isolates a single
   variable in a way live A/B cannot, because the prefix history is *identical* rather than merely
   similarly distributed. This is a genuinely strong research capability and the substrate already
   supports it.
3. **Failure-mode taxonomy** from `terminal_reason` × `FailureFingerprint` across a whole suite.
   `NO_PATCH` 123 is the first row of that table; nobody has computed the rest.
4. **Training data** for the procedural tier (§9.3), once there is a suite to validate against.

None of this requires new architecture. It requires the suite and the results file.

---

## 15. Scripts, developer surface, and the "graph" question

### 15.1 Reduce the entry points

`Makefile`, `justfile`, `install_vanguard.sh`, `install-cli.sh`, `env_workspace.sh`,
`collect_dev_context.sh`, `bin/aether`, `bin/aether-tui`, `bin/aether-desktop`, `ci/release_qualify.sh`,
`ci/rf86_gate.sh`, plus `uv`, `npm`, `pytest`, and `mkdocs`. A contributor — human or agent — cannot
determine the canonical path to "run the thing."

`just` is the right choice (already used, already documents intent). Collapse to five verbs:
`just check` · `just verify` · `just bench` · `just run` · `just docs`. Everything else becomes a
recipe those five call.

### 15.2 On "graph engineering"

Three distinct graphs are worth separating, because conflating them is a design hazard:

| Graph | What it is | Authority | Status |
|---|---|---|---|
| **Code graph** | symbols, refs, imports, test-covers | projection, rebuildable | built (LDA), unwired |
| **Causal graph** | the ledger — events, lineages, provenance DAG | **authoritative** | built, working |
| **Composition graph** | which capabilities/policies exist for a run | declaration | built (`compose.py`) |

`VISION.md` Ch. 7's distinction between *composition* (space of possibilities) and *trajectory*
(what happened) is the important one, and it is correct. What must be resisted is a **fourth**
graph: a workflow DAG declaring the order of work before the work runs. `tool_policy.derive_phase`
is a three-node instance of exactly that, and `spec.md`'s "loop-over-DAG inversion" clause exists
to forbid it.

The practical guidance: **invest in the code graph (D2), protect the causal graph (it is working),
keep the composition graph declarative and inheritable (§13.2), and never build the fourth.**

---

## 16. Consolidated priority

| Tier | Items | Why |
|---|---|---|
| **1 — capability** | tool surface (§4) · `str_replace` (§5) · real `bash` (§4.2) · parallel calls (§4.3) · LDA index (§6) | determines pass rate |
| **2 — economy** | cache breakpoints (§7.2) · distillation (§7.1) · working-set header (§7.3) | determines cost, latency, and length ceiling |
| **3 — instrument** | frozen suite · results.jsonl · `bench compare` · schema honesty (§14) | determines whether anything else is decidable |
| **4 — reliability** | postconditions (§D4) · handoff (§7.5) · summarise-on-compact (§7.4) · `falsified` memory (§8.2) | determines long-session success |
| **5 — leverage** | sub-agent isolation (§12.1) · manifest inheritance (§13.2) · skills catalogue (§9.1) | multiplies tiers 1–4 |
| **6 — supervision** | ledger-tailing supervisor (§11.1) · one pathology (§10.3) · outer loop M-O1/M-O2 | multiplies a working inner loop |
| **7 — research** | topologies (§12.2) · evolutionary strategy · learning promotion (§9.3) | gated on tier 3 existing |

Tiers 1–3 are approximately four weeks and touch no kernel code. Tier 7 should not begin before
tier 3 exists, because until it does, none of its results can be believed.
