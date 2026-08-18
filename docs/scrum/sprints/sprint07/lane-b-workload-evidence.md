# Sprint 7 · Lane B — Workload & Evidence

**Owner:** Senior Developer B · **Backlog:** `011 §4.2`
**Write scope:** `vanguard/packages/agency/manifests/**` · `vanguard/packages/adapters/**` ·
`test/agency/**` · `test/lab/**`
**Do not touch:** `kernel/**` · `agency/episode/**` · `runtime/**` (Lane A owns `root.py`;
raise a PR comment instead) · `benchmarkings/**`

---

## The lane in one sentence

> **Make the manifest actually determine behaviour — starting by making it impossible for a
> manifest component to be declared and ignored.**

Three tests are red on this branch. All three are in the Sprint 7 alias layer, and the underlying
defect is worse than the failures: **`to_canonical` falls back to identity on an unknown name**, so
a misconfigured alias fails silently at turn 3 as `UNKNOWN_ACTION` rather than at composition.
`N-17` and `VG-03 §5.3` require the opposite: *"unknown names fail at composition, not at first
use. A name that fails at first use fails in production rather than in CI."*

---

## S7-B-01 — Canonical alias shape + fail-closed validation · **START DAY 1**

**Currently red:**
```
test_load_vg_code_swe_mini:  to_canonical("read_file") → "read_file",  expected "fs.read"
test_load_vg_shell_only:     to_canonical("bash")      → "bash",       expected "proc.exec"
```

**Root cause:** `vg-shell-only/aliases.json` is `{"shell":"proc.exec"}`; the tests expect a `bash`
key and an `{"aliases": {...}}` envelope. `loader.py:41-67` accepts **three** shapes.

- [ ] **Step 1** — decide and record: the **flat `{"alias": "verb"}` form wins** (4 of 5 packs
      already use it). **Migrate the tests, not the data** — the data is what ships
- [ ] **Step 2** — failing test first:
      `test_alias_target_not_a_declared_verb_fails_composition` — a pack whose `aliases.json` maps
      `Foo → fs.nonexistent` must raise `CompositionError`. Currently it composes fine
- [ ] **Step 3** — failing test: `test_tool_schema_name_must_resolve` — a tool schema whose `name`
      is neither a declared verb nor an alias key must raise at composition
- [ ] **Step 4** — implement in `compose()`:
      - every alias **target** ∈ manifest-declared verbs
      - every tool schema `name` ∈ aliases ∪ verbs
      - **remove the identity fallback** in `to_canonical` — an unknown name is an error, not a
        pass-through
- [ ] **Step 5** — collapse `AliasTranslator.from_dict` from three accepted shapes to one
- [ ] **Step 6** — update the two red tests to the canonical shape; both green
- [ ] **Step 7** — broken counterpart under `test/broken/`: a pack with a mismatched alias must
      **fail** composition
- [ ] **Step 8** — commit `[lane-b] S7-B-01: one alias shape, fail-closed at composition (N-17)`

> **Note the subtlety.** `vg-code-claude-shaped/aliases.json` maps `Read → fs.read`. That is
> correct and must keep working — the model sees `Read`, the kernel sees `fs.read`. What must fail
> is an alias pointing at a verb the manifest does not declare.

---

## S7-B-02 — "An unread component is a composition error"

**This is the highest-leverage rule in the sprint.** ~20 lines, and it makes `FT-10` structurally
impossible in the manifest layer forever.

Today `vg-code-default/context-policy.json` says `{"kind":"recency-window","maxItems":64}`. It is
read into `contents`, hashed into the composition digest, and **interpreted by nothing.** The
compiler runs `result_eviction`. Two harnesses can therefore differ in digest and be **byte-identical
in behaviour** — which would let a clean, pre-registered, statistically analysed experiment
measure nothing while every artifact in the chain looked correct.

- [ ] **Step 1** — failing test: `test_unconsumed_component_fails_composition` — add
      `"decorative_policy": ["…/x.json"]` to a test manifest → currently composes fine
- [ ] **Step 2** — implement: `compose()` maintains a registry of component roles with a
      registered consumer. A role in `components` with no consumer raises `CompositionError`
      naming the role
- [ ] **Step 3** — **run it against the real packs.** `context_policy` and `routing_policy` will
      **fail** — that is correct and expected. Register them as `consumer: pending(S8-B-02/03)`
      with an explicit, dated marker so the failure is visible but does not block the sprint
- [ ] **Step 4** — broken counterpart
- [ ] **Step 5** — commit

> **Do not** silently exempt `context_policy`. The whole point is that the gap is now *visible*.
> A dated `pending` marker is honest; a wildcard exemption reintroduces the defect.

---

## S7-B-03 — Metamorphic policy-digest test (expected RED)

- [ ] **Step 1** — write `test/agency/test_manifest_metamorphic.py`: recompose a pack with a
      mutated `context-policy.json`, assert **at least one observable differs** (a rendered prompt
      byte, a compaction outcome, a routing decision)
- [ ] **Step 2** — run it. **It fails.** That is the deliverable this sprint — a test that
      documents the decorative-field defect
- [ ] **Step 3** — mark it `@unittest.expectedFailure` with a comment citing `S8-B-02` as the row
      that turns it green
- [ ] **Step 4** — commit

> An expected-failure test is the honest form of "we know, and here is the proof". It converts to a
> real gate the moment Sprint 8 lands, with no extra work.

---

## S7-B-04 — Emit `gene_digests` into results

**Already implemented.** `root.py:606-609` computes a per-file SHA-256 map over every manifest
component. The remaining work is emission, not construction.

- [ ] **Step 1** — failing test: two composes of `vg-code-default` produce identical
      `gene_digests`; changing one byte of `system-prompt.txt` moves **exactly one** entry
- [ ] **Step 2** — surface `gene_digests` on `RunResult`
- [ ] **Step 3** — coordinate with Lane C: emit into `result.json`'s `K_compat` block
- [ ] **Step 4** — commit

> This is what makes `D_treatment = manifest` a checkable claim rather than an assertion.

---

## S7-B-05 — Fix the `vg-shell-only` undeletability guard

`test/lab/test_bench.py::test_vg_shell_only_is_undeletable_single_proc_exec` currently **errors**
with `KeyError: 'aliases'`. So the `L-15` protection — the one flagged as a standing risk in
`GTS-13C` Ch. 14 — **is not actually running.**

- [ ] **Step 1** — fix the fixture to the canonical alias shape from `S7-B-01`
- [ ] **Step 2** — assert both properties: the registry refuses removal, **and** the pack declares
      exactly one `proc.exec` capability
- [ ] **Step 3** — commit

---

## Stop conditions

| Signal | Action |
|---|---|
| Alias repair appears to need an `agency/episode/engine.py` edit | **Stop.** `ADR-0060` violation. Write a finding |
| A reconstruction pack cannot compose without a new kernel verb | **Stop.** `D-04`: new verbs are registry rows, never engine branches |
| `S7-B-02` makes more than the two known policies fail | Not a stop — but each additional failure is a **finding**; list them in the PR |
| You are tempted to add `if harness == "claude"` anywhere | **Stop.** `T10.9`; it always arrives disguised as pragmatism |

## Definition of done for the lane

```bash
python3 -m unittest test.agency.test_manifest_loader -v   # green
python3 -m unittest test.lab.test_bench -v                # green
python3 -m unittest test.agency.test_manifest_metamorphic # expected failure, documented
python3 tools/check_baseline_manifest.py                  # PASS
python3 tools/check_boundaries.py                         # PASS
```
Plus: a planted mismatched alias fails composition; a planted unread component fails composition.
