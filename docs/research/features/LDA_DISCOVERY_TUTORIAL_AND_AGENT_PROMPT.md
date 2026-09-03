# LDA Discovery Tutorial + Agent Prompt

**Verified against index rebuilt 2026-08-31 at HEAD `ca47eef`.**
Index: 3,717 files / 10,505 symbols / 12,442 relations / 323 documents. Status `HEALTHY`.

---

## 1. What actually works (verified, not from the skill file)

`.agents/skills/lda-navigator/SKILL.md` advertises tools that silently return empty.
Do not trust it. This table is measured.

| Command | Status | Use it for |
|---|---|---|
| `lda query "<terms>"` | **WORKS** | BM25/FTS across symbols + doc sections. Best first move. |
| `lda symbol <Name>` | **WORKS** (see caveat) | Exact signature, file, line range, docstring |
| `lda context "<task>" --budget N` | **WORKS** | Token-bounded packet: docs + code + authority |
| `lda brief "<task>"` | WORKS, noisy | Markdown task briefing. Keyword-matches badly — verify every hit. |
| `lda repomap --budget N` | **WORKS** | PageRank structural skeleton of the repo |
| `lda map` | **WORKS** | Entity/kind counts, architecture topology |
| `lda metrics --json` | **WORKS** | Fan-in/out hubs, import cycles, hub files |
| `lda identity` | **WORKS** | Branch, HEAD, dirty state, index-vs-HEAD freshness |
| `lda diff --since <sha>` | WORKS | Fact-level diff workspace vs index |
| `lda standardize <file>` | WORKS | Language + canonical symbol kinds + imports for one file |
| `lda doctor --json` / `lda check` | **WORKS** | Health gate. Run first. |
| `lda drift` / `lda consolidate` | WORKS | Doc drift, duplicate docs |
| `lda callers <sym>` | **BROKEN — always `[]`** | use `rg` instead |
| `lda references <sym>` | **BROKEN — always `[]`** | use `rg` instead |
| `lda tests <file>` | **BROKEN — always empty** | use `rg` instead |

**Why the three are broken:** the DB has only `defines`, `imports`, `inherits`, and `tests`
relation kinds. There are **no `calls` edges at all**, so caller/callee/reference traversal has
nothing to walk. The `tests` edges point test-symbol → bare function name, not at production
symbols, so file-based test lookup can't match either.

**This is dangerous, not just useless.** An empty `lda callers` reads as "nothing calls this,
safe to change." It is not. Always confirm with `rg`.

**`lda symbol` caveat:** results are not ranked by exactness. `lda symbol AdmissionGate`
returns `TestForgeAdmissionGate` and `ForgeAdmissionGate` *above* the exact match. Scan the
list for the name and path you actually want — never take `result[0]`.

---

## 2. Index hygiene (already applied, keep it this way)

Two exclusions were added to `tools/007_LLM_DOCS_ATLAS/profiles/aether.toml`:

- `front`, `back`, `aether-v092b-frontend` — `docs/reports/reviews/electroweak_v092/` contains
  a **full shadow copy of the whole repo** (3,343 files). Indexed, it outranked production
  symbols and routed agents to edit dormant duplicates.
- `.vanguard` — gitignored agent scratch workspaces that contributed **16,263 symbols (61% of
  the index)** and dominated `repomap` with throwaway benchmark runs.

Effect: low-signal symbols dropped 300/300 → 30/300; `repomap` now surfaces real code.

Rebuild after any large branch change:

```bash
uv run lda index --rebuild --json     # ~15s, full purge
uv run lda index --incremental        # warm path
uv run lda doctor --json              # confirm HEALTHY + HEAD match
```

Known residual warnings (tool defects, not your fault, safe to ignore):
`orphan_fts ~5.5k` (the "fix" it recommends is the rebuild you just ran),
`20 duplicate document pairs`, `141 undocumented symbols`.

---

## 3. The discovery workflow

Replaces "open files and read until you understand." Target: locate the true owner of a
change in under 60 seconds without reading a single full file.

### Step 0 — Health gate (once per session)
```bash
uv run lda identity        # index-vs-HEAD freshness
uv run lda doctor --json | head -5
```
If HEAD ≠ index HEAD, rebuild. If `index_healthy: false`, fall back to `rg` +
`python3 tools/docs_rag_v0.py "<query>"` and say so.

### Step 1 — Orient (only when the area is unfamiliar)
```bash
uv run lda repomap --budget 2000
uv run lda metrics --json | head -30      # hub files = blast radius
```

### Step 2 — Locate
```bash
uv run lda query "admission gate verification binding"
uv run lda context "<the actual task sentence>" --budget 4000
```
`query` gives ranked hits with `locator` as `path#Lstart-Lend`. `context` gives a budgeted
packet with canonical docs attached.

### Step 3 — Pin the contract
```bash
uv run lda symbol AdmissionGate       # scan for exact name + production path
uv run lda standardize vanguard/packages/agency/episode/admission_gate.py
```
Read only the line range you were given, e.g. `sed -n '120,140p' <file>`.

### Step 4 — Blast radius (LDA can't do this — use rg)
```bash
rg -n "AdmissionGate" --type py -g '!docs/reports' -g '!.vanguard'
rg -ln "admission_gate|AdmissionGate" test/
```
Always exclude `docs/reports` and `.vanguard` or you'll get shadow-copy hits.

### Step 5 — Falsify
```bash
python3 -m unittest test.agency.test_protocol_recovery -v
python3 tools/linters/check_boundaries.py
python3 tools/linters/check_tcb_budget.py
```

---

## 4. Recipes

**Bug fix:** `query <error text>` → `symbol <suspect>` → `sed -n` the range → patch →
`rg` for callers → run the focused test.

**New feature:** `repomap` → `symbol <the port/protocol>` → `standardize` the adapter →
check `metrics` hub files before touching anything with high fan-in.

**"Who owns this?"** `query "<concept>"` and read the `docs/` hits first — canonical docs
outrank source for *intent*; source outranks docs for *behavior*.

**Never:** trust `lda callers`; take `lda symbol` result[0]; edit a path under
`docs/reports/` (report-tree paths are never production owners).

---

## 5. Agent prompt (copy-paste)

```text
You have LDA, a repository intelligence index over this codebase (SQLite + FTS5 +
AST symbol graph). Use it to locate code instead of reading files exhaustively.

VERIFIED COMMAND SURFACE — this overrides .agents/skills/lda-navigator/SKILL.md,
which documents three tools that silently return empty results:

WORKS:
  uv run lda doctor --json                     health gate; run once at start
  uv run lda identity                          branch/HEAD/index freshness
  uv run lda query "<terms>"                   BM25 over symbols + doc sections
  uv run lda context "<task>" --budget 4000    token-bounded context packet
  uv run lda symbol <Name>                     signature, file, line range
  uv run lda standardize <file>                symbols + imports for one file
  uv run lda repomap --budget 2000             PageRank structural map
  uv run lda map                               architecture topology
  uv run lda metrics --json                    fan-in/out hubs, import cycles
  uv run lda diff --since <sha>                fact-level diff

BROKEN — never rely on these, they return empty for every input:
  uv run lda callers <sym>      -> always []
  uv run lda references <sym>   -> always []
  uv run lda tests <file>       -> always empty
The index has no `calls` relations, so caller/reference traversal has nothing to
walk. An empty result means "the tool is broken", NOT "nothing calls this". For
blast radius always use ripgrep instead:
  rg -n "<Symbol>" --type py -g '!docs/reports' -g '!.vanguard'

CAVEAT: `lda symbol` is not ranked by exactness — the exact match is often NOT
first. Scan the whole result list for the name and path you want. Never take
result[0] blindly.

HARD RULES:
- Never edit anything under docs/reports/ — that tree contains a full dormant
  shadow copy of the repository. Report-tree paths are never production owners.
- Never edit anything under .vanguard/ — gitignored agent scratch.
- Always pass -g '!docs/reports' -g '!.vanguard' to ripgrep.
- Read line ranges (sed -n 'A,Bp'), not whole files, once LDA gives you a locator.

WORKFLOW for any coding, debugging, or refactoring task:
1. `lda identity` — if index HEAD != workspace HEAD, run `lda index --rebuild`.
2. `lda query` or `lda context` with the task description to find candidates.
3. `lda symbol` / `lda standardize` to pin the exact contract and line range.
4. `rg` to find every caller and test — LDA cannot do this.
5. Apply a surgical diff to the production path only.
6. Run the focused tests, then the boundary and TCB linters.

Report which LDA commands you used and what they returned. If the index is
unhealthy, say so explicitly and fall back to rg +
`python3 tools/docs_rag_v0.py "<query>"`.
```
