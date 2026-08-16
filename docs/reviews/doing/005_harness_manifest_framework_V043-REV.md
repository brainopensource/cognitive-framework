# 005 — The Harness Manifest Framework: making `C-01` testable

**Status:** NON-NORMATIVE. Where this file and a v4 owner disagree, the owner wins (`PR-3`).
**Date:** 2026-08-16 · **Branch/HEAD:** `sprints7-8/integration` @ `0238b1a`
**Owns:** the diagnosis of the manifest layer, the specification of what a manifest must express
before the reconstruction claim means anything, and the S7 remediation.
**Authority cited:** `VG-02 C-01/C-02`, `VG-03 §5 §7.4 §11`, `GTS-13C` Ch. 6, Ch. 7, T7, `L-15`,
`ADR-0049`, `ADR-0060`.

---

## 1. The claim under test

`C-01`: *"Every reference harness is expressible as configuration, with no core change.
Falsified by: any reconstruction requiring a loop modification."*

`C-02`: *"Memory, retrieval, tool protocols, web search and knowledge graphs are registry entries
plus configuration."*

`GTS-13C` Ch. 7: *"A harness is a manifest, not a codebase."*

These are the commercial thesis as well as the scientific one. **Everything the programme sells —
"a framework for building agentic coding harnesses" — reduces to whether they hold.**

---

## 2. Current state: the manifest is a prompt selector

### 2.1 What was delivered

Five manifest packs under `vanguard/packages/agency/manifests/`:
`vg-code-default`, `vg-shell-only`, `vg-code-claude-shaped`, `vg-code-opencode-shaped`,
`vg-code-swe-mini`, plus `loader.py`, `discovery.py`, `kinds.json`, `registry.json`.

Composition (`runtime/root.py:543-629`) is genuinely well built: the manifest resolves,
artifacts are read and content-addressed, an `ArtifactGraph` workspace is built with one
`LogicalEdit` per composition, `compose()` freezes it into a `FrozenHarness` with a closure
digest, sink classes are registered per capability, and **a verb with no bound adapter fails at
composition** (`root.py:583-585`). `VG-03 §5.3` freeze-at-composition is real.

### 2.2 What the manifests actually differ by

Diffing `vg-code-claude-shaped/manifest.json`, `vg-code-swe-mini/manifest.json` and
`vg-code-default/manifest.json`:

> **They are byte-identical except for `system_prompt`.** All three reference the *same four
> tool schema files* (`vg-code-default/read-tool.json`, `search-tool.json`, `patch-tool.json`,
> `test-tool.json`), the same four capabilities with the same selectors and risks, the same
> `context_policy`, the same `routing_policy`, the same `budgetPolicy`, the same evaluator.

The only other difference is `aliases.json` — a tool-name rename (`Read`/`Grep`/`Edit`/`Bash`
for the Claude-shaped pack).

**So the "three competitor-shaped harness reconstructions" of `T7.6` differ by a prompt string
and four tool names.**

### 2.3 What real harnesses actually differ by

| Dimension | Claude-Code-shaped | SWE-agent-minimal | OpenCode-shaped | Expressible today? |
|---|---|---|---|---|
| Tool naming | `Read`/`Edit`/`Bash` | `read`/`patch` | varies | ✅ aliases |
| System prompt | long, procedural | short, terse | medium | ✅ |
| **Compaction strategy** | progressive ladder, auto-compact | none / truncate | window | ❌ **decorative field** |
| **Subagent topology** | isolated-context subagents | none | none | ❌ **no recursion** |
| **Planning discipline** | explicit todo/plan artifact | none | none | ❌ **no playbooks** |
| **Permission model** | per-tool prompt + allowlist | none | none | ❌ **hardcoded `"low"` threshold** |
| **Retry / turn budget** | large, adaptive | small, fixed | medium | ⚠️ only `max_turns` from the task |
| **Model routing** | tiered | single | single | ❌ **decorative field** |
| **Search strategy** | grep + glob + agentic search | grep | grep | ⚠️ one `fs.search` verb |
| **Edit granularity** | string-replace + full write | full write | patch | ⚠️ one `patch.apply` |

**Six of the ten dimensions that actually distinguish harnesses are inexpressible.** And the
2026 evidence says these are precisely the dimensions carrying the variance: harness-only
variation moves SWE-bench Verified **9.5–20 points** on a fixed model
([Harness-Bench](https://arxiv.org/pdf/2605.27922),
[SWE-bench 2026 scaffolding analysis](https://www.digitalapplied.com/blog/swe-bench-verified-june-2026-benchmark-vs-scaffolding-analysis)).

**Conclusion: `C-01` is currently neither confirmed nor falsified — it is untested, and the
programme is recording it as tested.** That is the worst of the three states, because it removes
the pressure to build the thing that would test it.

---

## 3. Decorative fields: the `FT-10` instance that matters most

`vg-code-default/context-policy.json`:
```json
{"kind":"recency-window","maxItems":64}
```
`vg-shell-only/context-policy.json`:
```json
{"kind":"recency-window","maxItems":32}
```
`vg-code-default/routing-policy.json`:
```json
{"kind":"single-model"}
```

Grep for consumption across `vanguard/`:

```
root.py:134   "context_policy": "context_policy",    # a key in a role-name map
graph.py:17   "context_policy", ...                   # a name in BUILTIN_KINDS
```

**No code reads the value of either file.** The `ContextCompiler` is built from `system_core`,
`tool_schemas`, `env_text` and a token ceiling from the budget (`root.py:702-707`), and it
implements `result_eviction` + oldest-first drop — **a different strategy from the declared
`recency-window`**. `adapters/models/routing.py` (107 LOC) exists and is never instantiated.

Two consequences, and the second is the serious one:

1. `FT-10` decorative switch: *"a flag that reads as enabled and changes nothing."*
2. **Both files are hashed into the composition digest** (`root.py:606-609`). Two harnesses
   differing only in context policy therefore produce **different digests and identical
   behaviour**. Any paired experiment keyed on context policy would produce a clean, well-formed,
   pre-registered, statistically analysed measurement of *nothing*, and every artifact in the
   chain would look correct.

That is the exact mechanism by which a measurement programme produces confident false results.
It must be fixed before `T8.2` runs, not after.

---

## 4. Sprint 7 defects to fix immediately

### 4.1 The alias translator is failing and fails open

Three test failures on this branch:

```
test_load_vg_code_swe_mini:  to_canonical("read_file") -> "read_file",  expected "fs.read"
test_load_vg_shell_only:     to_canonical("bash")      -> "bash",       expected "proc.exec"
test_bench.ShellOnlyControl: KeyError: 'aliases'
```

Data: `vg-shell-only/aliases.json` is `{"shell":"proc.exec"}`; the tests expect a `bash` key and
an `{"aliases": {...}}` envelope. `loader.py:41-67` accepts three shapes, and `to_canonical`
(`loader.py:69-71`) is:

```python
return self.to_canonical_map.get(tool_name, tool_name)
```

**The identity fallback is the real defect.** An alias whose target is not a declared verb passes
through untranslated and fails much later as `UNKNOWN_ACTION` inside dispatch — violating `N-17`
and `VG-03 §5.3`: *"Unknown names fail at composition, not at first use. A name that fails at
first use fails in production rather than in CI."*

**Fix (three parts):**
1. One canonical alias file shape. Pick the flat `{"alias": "verb"}` form — it is what four of
   five packs already use — and migrate the tests, not the data.
2. At composition, assert **every alias target is a manifest-declared verb** and **every declared
   verb has exactly one alias or none**. Raise `CompositionError` otherwise.
3. At composition, assert **every tool schema's `name` is either a declared verb or an alias
   key**. Today `read-tool.json` declares `{"name":"read","verb":"fs.read"}` while
   `swe-mini/aliases.json` maps `read → fs.read`; that agrees by luck, not by check.

Add a `test/broken/` counterpart with a deliberately mismatched alias and assert composition
fails (`T10.3`, `A-10`).

### 4.2 Verb/argument/selector binding must move out of the model adapter

`adapters/models/invocation.py` hardcodes the coding verb set, per-verb argument requirements
(`path`, `pattern`, `argv`) and selector construction (`{"kind":"fs","root":...,"path":...}`).
This is the `ADR-0060` capture described in `003 §7`.

The manifest already carries everything needed:
- the tool schema file carries `name`, `verb` and a JSON Schema for `args`;
- the capability row carries `verb`, `sink`, `selector`, `risk`.

So the translator can be **fully generic**: tool call → alias → verb → validate `args` against
the declared JSON Schema → bind the selector by substituting args into the declared selector
template. Zero domain knowledge, and TableWorld becomes a manifest directory.

---

## 5. What a manifest must express — the target schema

Extend `harness-manifest.schema.json`. Each new component is a **registered, versioned,
content-addressed artifact kind** — all sixteen kinds already exist in `BUILTIN_KINDS`
(`domain/artifacts/graph.py:16-20`), so this is population, not invention.

```yaml
harness: vg-code-claude-shaped
components:
  system_prompt:      [claude-shaped/system-prompt.txt]
  tools:              [tools/read@1, tools/search@1, tools/edit@1, tools/bash@1]
  # --- currently decorative, must become load-bearing ---
  context_policy:     [policies/progressive-compaction@1]   # -> CompactionStrategy
  routing_policy:     [policies/tiered-route@1]             # -> ModelRouter
  budget_policy:      [policies/interactive@1]
  # --- currently absent, required for C-01 to be testable ---
  approval_policy:    [policies/prompt-above-medium@1]      # replaces the hardcoded "low"
  subagent_config:    [subagents/explore@1]                 # -> child episode shape (needs recursion)
  playbook:           [playbooks/tdd-guided@1]              # rigidity: advisory|guided|strict
  retrieval_policy:   [policies/grep-first@1]
capabilities: [...]                                          # unchanged — already good
evaluators: [coding-oracle@3]
```

### 5.1 The rule that keeps this honest

> **A component listed in `components` that no registered consumer reads is a composition
> error.**

One rule, ~20 lines in `compose()`, and `FT-10` becomes structurally impossible in the manifest
layer forever. This is the single highest-leverage line of code in the S7 remediation, because
it converts "we forgot to wire it" from a silent measurement corruption into a build failure.

Corollary rule: **a component whose digest changes must change behaviour.** Testable by a
metamorphic test — recompose with a mutated policy file and assert at least one observable
differs (a rendered prompt byte, a routing decision, a compaction outcome). If nothing differs,
the component is decorative and the test fails.

### 5.2 `vg-shell-only` is correctly protected

`registry.json` flags it undeletable; `test/lab/test_bench.py` asserts a single `proc.exec`.
`L-15` and `GTS-13C` Ch. 14 both name its deletion as a standing risk. **This is right and was
done right.** One gap: the guard test currently errors (`KeyError: 'aliases'`), so the
protection is not actually running. Fix with §4.1.

---

## 6. Between-episode discovery (`T7.7`)

`agency/manifests/discovery.py` exists. `L-11`/`ADR-0005`: registries freeze at composition
**per episode**; signed, allow-listed manifests may install **between** runs under operator
policy. Two properties to verify before this ships:

1. Discovery is **never** reachable during an episode. Architecture test: no path from
   `agency/episode/` to `agency/manifests/discovery`.
2. Installation requires a signature verified against an operator-held key — the same asymmetric
   authority as approvals (`ADR-0062`, `GOV-01`). The runtime must not be able to install a
   manifest it could also have authored.

This is where MCP server installation will eventually land (`006 §4`), so getting the trust model
right now is cheap and getting it wrong later is not.

---

## 7. What "framework for building harnesses" must mean to be sellable

`GTS-13C §7.3` names the differentiator: *"a harness that ships with its own evidence ledger —
which components are active, what promoted them, what would demote them, what it costs per
verified change."*

That is a genuinely defensible product claim and **no competitor offers it**. It requires, in
order:

| # | Capability | Status |
|---|---|---|
| 1 | Every component is a content-addressed artifact with a digest | ✅ done |
| 2 | The active set is frozen and recorded per episode | ✅ done (`FrozenHarness`, closure digest) |
| 3 | Every effect is attributed to the frozen set | ✅ on the product path; ❌ on the bypass paths (`002`) |
| 4 | Components actually determine behaviour | ❌ **§3** |
| 5 | Cost per verified change is computable | ⚠️ telemetry exists; `... or 100` fabrication must go (`003 §5.1`) |
| 6 | What promoted a component, and what would demote it | ❌ needs `Claim` (`004 §3`) |
| 7 | `vg why <artifact>` surfaces 6 to an operator | ❌ `T6.5` — *"if the operator cannot interrogate governance, they will bypass it"* |

**Items 4 and 6 are the product.** Items 1–3 are the infrastructure that makes them credible and
they are already built. The gap between "impressive infrastructure" and "sellable framework" is
much smaller than it looks — it is §3 plus `004 §3`, roughly three weeks.

---

## 8. Sprint 7 remediation backlog

| # | Item | Effort | Unblocks |
|---|---|---|---|
| H0 | **Gene digests — already implemented.** `root.py:606-609` computes a per-file SHA-256 map over every manifest component. Remaining work is *emitting* it into `result.json`'s `K_compat` block, not building it (`009 §5`) | 0.5 d | comparability |
| H1 | One canonical alias shape; migrate tests; fix 3 failures | 1 d | green suite |
| H2 | Composition-time validation: alias targets ⊆ declared verbs; tool `name` ∈ aliases ∪ verbs; **fail closed** + broken counterpart | 1 d | `N-17` |
| H3 | **"An unread component is a composition error"** rule | 1 d | kills `FT-10` |
| H4 | Metamorphic test: changing a policy digest must change an observable | 1 d | `002` validity |
| H5 | `CompactionStrategy` protocol + registry; `context_policy` becomes real | 3 d | any context comparison |
| H6 | `ModelRouter` protocol + registry; `routing_policy` becomes real; wire `adapters/models/routing.py` | 3 d | `O-04`, tier escalation |
| H7 | `approval_policy` component; delete hardcoded `"low"` | 2 d | harness differentiation |
| H8 | Generic verb/args/selector binding from the manifest; strip domain from `invocation.py` | 1 wk | `Q4`, TableWorld |
| H9 | Rebuild the three reconstructions so they **actually differ** on ≥3 of the ten dimensions | 1 wk | `C-01` testable |
| H10 | `vg harness build \| run \| diff \| bench` (`T7.5`) over the honest instrument | 1 wk | `T7.6` |
| H11 | `subagent_config` + `playbook` components | after recursion | `C-01` fully |

H1–H4 are **four days** and convert the manifest layer from misleading to merely limited.
H5–H8 are the three weeks that make `C-01` a real experiment rather than a claim.

---

## Sources

- [Harness-Bench: Measuring Harness Effects](https://arxiv.org/pdf/2605.27922)
- [SWE-bench in 2026: Benchmarks vs Scaffolding Reality](https://www.digitalapplied.com/blog/swe-bench-verified-june-2026-benchmark-vs-scaffolding-analysis)
- [Stop Comparing LLM Agents Without Disclosing the Harness](https://arxiv.org/pdf/2605.23950)
- [From Question Answering to Task Completion: A Survey on Agent System and Harness Design](https://arxiv.org/pdf/2606.20683)
- [awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering)
