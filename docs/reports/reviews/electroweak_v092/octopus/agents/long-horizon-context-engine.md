---
id: arch.context.long-horizon-engine
canonical_id: arch.context.long-horizon-engine
class: architecture
authority: descriptive
truth_plane: PROPOSED
status: proposed
implementation_status: NOT_STARTED
owner: consolidation-agent
canonical_for:
  - long-horizon multi-file context economics
  - memory / cache / compression / retrieval algorithms
purpose: >
  Practical spec for making the coding harness survive big contexts and many files:
  what to store, what to compress, what to cache, which algorithms, and where each
  piece plugs into the existing agency/context and agency/chimera code.
audience: [architect, developer, contributor]
last_verified: "2026-09-02"
relationships:
  - report.draft-synthesis-evidence-audit
  - arch.meta.conductor
  - arch.outer-loop.orchestrator
---

# Long-Horizon Context Engine

Everything here extends code that already exists. Insertion points are named explicitly so
this is implementable without re-reading the drafts.

## 1. The five problems, separated

Conflating these is why "context management" proposals sprawl. They have different
solutions and different plugin seams.

| # | Problem | Symptom | Owner |
|---|---|---|---|
| P1 | **Turn-level bloat** | raw tool output floods `L5` | distillation filter |
| P2 | **Attention dilution** | 40k tokens present, model attends to the wrong 3k | ranking + placement |
| P3 | **Cache destruction** | prefix mutates, cost 10× | layer discipline (already solved) |
| P4 | **Cross-episode amnesia** | episode 7 re-derives what episode 2 learned | durable memory |
| P5 | **Repo scale** | 5,000 files, budget for 30 | retrieval + skeletonization |

## 2. P1 — Distillation at the effect boundary (highest ROI, build first)

Today `proc.exec` results land in `L5` roughly raw. `forge/engine.py` already has
`parse_test_output`; it is used for admission decisions, not for shrinking context.

**Insertion point:** a `ResultDistiller` port applied where the effect receipt becomes a
`Block`, *before* `CompactionStrategy` ever sees it. Distillation is lossy-on-write and
cheap; compaction is lossy-on-overflow and expensive. Doing it at the boundary means the
ceiling is hit far later.

```python
class ResultDistiller(Protocol):
    def distill(self, verb: str, payload: Mapping[str, Any]) -> DistilledResult: ...

@dataclass(frozen=True)
class DistilledResult:
    text: str                 # what enters L5
    full_digest: str          # content-address of the original, retrievable on demand
    tokens_saved: int

class PytestDistiller:
    """~1200 tok -> ~180 tok. Keeps: exit code, first N failing test ids, assertion
    line + message, pass/fail counts. Drops: tracebacks below the assertion frame,
    collection noise, warnings, timing tables."""
    def distill(self, verb, payload):
        if verb != "proc.exec" or not _is_test_run(payload):
            return DistilledResult(_truncate(payload["stdout"]), digest_of(payload), 0)
        parsed = parse_test_output(payload["stdout"])      # reuse forge/engine.py
        text = render_compact(parsed, max_failures=3)
        return DistilledResult(text, digest_of(payload), estimate_tokens(payload["stdout"]) - estimate_tokens(text))
```

**Critical design rule — never destroy, always address.** `full_digest` means the agent can
call `ctx.expand(digest)` to get the original if it genuinely needs the traceback. This is
the difference between compression and data loss, and it is what makes aggressive
distillation safe. Register distillers per-verb in a manifest `distillation-policy.json`, so
`fs.read`, `proc.exec`, `search` each get an appropriate one and new verbs get a
conservative default.

Distillers to ship, in ROI order: pytest/unittest → `fs.read` (skeletonize, §6) → `search`
(dedupe by file, cap hits/file) → git diff (stat + hunk headers, bodies on demand).

## 3. P2 — Placement, not just selection

Two mechanisms, both cheap:

**(a) Recency-inverted salience.** Models attend worst to the middle of a long context
(`benchmark_20_suite/07_context_lost_in_middle_prune` exists precisely for this). So the
assembly order within `L5` should be: *most salient last* (adjacent to the generation
point), *stale-but-retained* in the middle, *task-critical invariants pinned in `L4`* — never
in the middle of dialogue. `layers.py` already renders in layer order; this adds an
intra-`L5` sort key.

**(b) Explicit working-set header.** One pinned, regenerated-each-turn block at the top of
`L5`:

```
WORKING SET (turn 14/40)
  goal:      make test_lease_expiry pass without breaking test_clean_expired
  changed:   lru/cache.py (2 hunks), lru/entry.py (1 hunk)
  verified:  FAILING — test_lease_expiry: 80 != 100 @ test_limiter.py:45
  rejected:  [t7] widening TTL window — broke test_clean_expired
             [t11] clearing on read — same failure signature
  next:      inspect Entry.expires_at initialisation
```

This is the single most effective anti-drift device available and it costs ~80 tokens. It is
also what makes `rejected` durable — the dominant long-session failure is an agent
re-attempting a path it already falsified. `chimera/search.py` already has
`distill_trajectory_summaries` producing dead-end summaries; this promotes that output from
"occasionally compiled in" to "always pinned".

## 4. P3 — Cache discipline (already solved; do not regress it)

`agency/context/layers.py` is correct as written and its docstring states the invariant:
appending to `L1`–`L4` mid-run destroys every downstream cache hit. Two additions:

1. **A regression test, not a comment.** Assert that the rendered `PREFIX_LAYERS` digest is
   byte-identical across all turns of a run. This invariant is currently protected only by a
   docstring, and the `_schemas_with_aliases` double-exposure bug (each verb emitted as both
   `read` and `fs.read`, per the root-cause doc) shows `L2` does drift in practice.
2. **Budget the prefix explicitly.** Report `prefix_tokens` / `volatile_tokens` separately in
   run receipts. Right now a run reports total tokens, which hides whether cost came from a
   cache miss or from genuine work.

## 5. P4 — Cross-episode durable memory

This is where the outer loop (`arch.outer-loop.orchestrator`) and this engine meet. The
`Compactor.compact_episode()` output is a **Distilled Episode Record**:

```python
@dataclass(frozen=True)
class EpisodeMemory:
    episode_id: str
    package_id: str
    intent: str                       # one sentence
    interfaces_touched: tuple[str,...]  # symbols/files, from the ledger's fs.write records
    decisions: tuple[Decision, ...]     # {choice, rationale, alternatives_rejected}
    falsified: tuple[str, ...]          # paths proven not to work — the crown jewels
    artifacts: tuple[ArtifactRef, ...]
    verification: VerificationReceipt | None
    tokens: int                       # target: < 400
```

**`falsified` is the highest-value field and the one everyone forgets.** Knowing "X was
tried and failed for reason R" is worth more to episode 9 than knowing what succeeded,
because success is visible in the code and failure is not. It is derivable for free from the
ledger — every `proc.exec` that returned non-zero after a `patch.apply`, paired with the
patch that preceded it.

Store as: content-addressed rows in the existing SQLite-WAL ledger under `mem.*`, plus an
FTS5 index (already a dependency — `benchmark_20_suite/06_fts5_stale_index_rebuild` exists).
**Do not add a vector DB.** At the scale of one repo's episode history (hundreds to low
thousands of records), BM25 over FTS5 plus the structural filters below outperforms
embeddings on both latency and operational cost, and it has no model dependency.

## 6. P5 — Repo-scale retrieval

### 6a. Skeletonization before selection

Never put a whole file in context when a skeleton answers the question. For each candidate
file produce three levels, choose by budget:

```
L0  path + one-line purpose                              ~15 tok
L1  signatures: classes, defs, args, return types,       ~150 tok
    decorators, docstring first line — bodies elided
L2  full text                                            ~500-5000 tok
```

Build with `tree-sitter` (or Python's `ast` for the Python-only path — zero new
dependency, ships today). `tools/ast_grep_adapter.py` and `tools/scip_adapter.py` already
exist as adapters; wire them here rather than adding a parser.

The default retrieval answer for a 5,000-file repo is *not* "3 files at L2". It is
"40 files at L0, 8 at L1, 2 at L2" — chosen by the packer below.

### 6b. Selection as a budgeted knapsack, not a top-k

Top-k retrieval returns k near-duplicates. What is wanted is *coverage* per token. This is
submodular maximization under a budget — the greedy algorithm gives the standard
`(1 − 1/e)` guarantee and is ~30 lines:

```python
def pack_context(candidates, budget_tokens, alpha=0.7):
    """Greedy submodular packing. candidates: (item, tokens, relevance, covered_symbols)."""
    chosen, covered, spent = [], set(), 0
    while True:
        best, best_gain = None, 0.0
        for item in candidates:
            if item in chosen or spent + item.tokens > budget_tokens:
                continue
            new_syms = item.covered_symbols - covered          # marginal coverage
            gain = (alpha * item.relevance + (1-alpha) * len(new_syms)) / max(item.tokens, 1)
            if gain > best_gain:
                best, best_gain = item, gain
        if best is None or best_gain <= 0:
            break
        chosen.append(best); covered |= best.covered_symbols; spent += best.tokens
    return chosen
```

The `/ item.tokens` is the whole point: it is *value per token*, which is what makes a
40×L0 + 8×L1 + 2×L2 mix beat 3×L2 automatically, with no hand-tuned tier rules.

**Insertion point:** `chimera/retrieval.py` already computes exactly the inputs this needs.
`RetrievalBid.utility` is `0.5·rel + 0.3·conf + 0.2·nov − 5e-5·cost` — a linear score that
already gestures at value-per-token but divides by nothing and models no coverage overlap.
Replacing the bid-aggregation step with the packer above is a contained change to one
function, and it is the correct home for it: the market metaphor stays, the settlement rule
gets a coverage term.

### 6c. Graph expansion for the "which files matter" question

Lexical retrieval finds files that *mention* the query. Multi-file bugs live in files that
mention nothing. Expand the seed set by one or two hops over the import/call graph, weighted
by personalized PageRank from the seeds:

```
seeds     = lexical/FTS5 hits + files named in the task brief + files in `changed` set
graph     = imports ∪ calls ∪ test→subject edges   (from .generated/knowledge/*.jsonl — exists)
scores    = personalised_pagerank(graph, restart=seeds, alpha=0.15, iters=20)
candidates= top-N by score, then skeletonize (6a), then pack (6b)
```

`.generated/knowledge/{code-map,symbols,links}.jsonl` already contains this graph.
`benchmark_20_suite/10_graph_ppr_dangling_node_sink` exists, so PPR is already a known
concern here. Twenty power iterations over a repo-scale sparse graph is milliseconds.

## 7. Putting it together — the per-turn pipeline

```
                      ┌──────────────── budget: ceiling − floor ──────────────┐
task brief ──► seeds ──► PPR expand ──► skeletonize ──► submodular pack ──► L3/L4
                                                                             │
tool result ──► ResultDistiller ──► Block(+full_digest) ──────────────► L5 ──┤
                                                                             │
working-set header (goal/changed/verified/rejected/next) ─── pinned top of L5┤
                                                                             │
prior episodes ──► FTS5 over EpisodeMemory ──► top-3 (falsified first) ──► L3┤
                                                                             ▼
                                                              CompactionStrategy
                                                            (only if still over)
```

`CompactionStrategy` becomes the *emergency* path rather than the primary mechanism. Today
it is the only mechanism, which is why context degrades — eviction is the last thing you
want doing your thinking for you.

## 8. Measurement — what to record so this is falsifiable

Add to every run receipt:

```
prefix_tokens, volatile_tokens          # P3: cache health
tokens_saved_by_distillation            # P1
context_precision = tokens_of_files_edited / tokens_of_files_supplied   # P2/P5
expansion_calls                         # how often ctx.expand() was needed — if high,
                                        # distillation is too aggressive
turns, turn_distribution                # F2 guard from the evidence audit
falsified_paths_reused                  # P4: did memory actually prevent a repeat?
```

`context_precision` is the key metric for P5 and almost nobody measures it. If the agent
edits 2 files and was given 30, precision is 0.07 and the retrieval stack is the bottleneck
regardless of what the pass rate says.

## 9. Build order

| Step | Item | Est. | Depends |
|---|---|---|---|
| 1 | `PytestDistiller` + `ResultDistiller` port + `full_digest`/`expand` | S | — |
| 2 | Working-set header block, pinned in `L5` | S | — |
| 3 | Prefix-stability regression test + prefix/volatile token split | S | — |
| 4 | AST skeletonizer (L0/L1/L2) via stdlib `ast`, Python path only | M | — |
| 5 | Submodular packer replacing bid aggregation in `retrieval.py` | M | 4 |
| 6 | PPR expansion over `.generated/knowledge/*.jsonl` | M | 5 |
| 7 | `EpisodeMemory` + FTS5 index + `falsified` extraction from ledger | M | 1 |
| 8 | `context_precision` + full receipt metrics | S | 1,5 |

Steps 1–3 are days and independently valuable. Steps 4–6 are the repo-scale story. Step 7 is
what the outer loop consumes. Nothing here requires a new dependency, a vector database, or
a kernel change.
