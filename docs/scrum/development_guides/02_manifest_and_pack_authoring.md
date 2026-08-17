# 02 — Manifest & Harness Pack Authoring

**Purpose:** how to author a harness pack so it is honest, comparable, and cannot silently do
nothing.
**Owner:** `GTS-13C` Ch. 7, `VG-03 §5`. This is a projection.

---

## 1. The claim a pack is under test for

`C-01`: *"Every reference harness is expressible as configuration, with no core change. Falsified
by: any reconstruction requiring a loop modification."*

If your pack needs a kernel or engine change, **stop and write the finding.** That is the
experiment producing a result — a cheap and valuable one — not a blocker to route around.

---

## 2. Pack directory contract

```
vanguard/packages/agency/manifests/<id>/
  manifest.json          # harness, components, capabilities, evaluators, budgetPolicy, undeletable
  system-prompt.txt
  *-tool.json            # {name, verb, description, schema}
  context-policy.json    # → CompactionStrategy   (load-bearing from S8-B-02)
  routing-policy.json    # → ModelRouter          (load-bearing from S8-B-03)
  budget-policy.json     # tokens, wall, effects, depth, maxTurns
  approval-policy.json   # → approval threshold   (load-bearing from S8-B-04)
  aliases.json           # {"model-visible-name": "canonical.verb"}
  REFERENCE.md           # which PUBLIC docs were read; what was NOT copied
```

Register in `registry.json` with a role: `experimental-control` · `product-default` ·
`reconstruction` · `generality-witness`.

---

## 3. The two rules that keep packs honest

### 3.1 An unread component is a composition error

If `components` names a role that no registered consumer reads, **composition fails**.

This exists because `context_policy` and `routing_policy` were declared in every pack, hashed into
the composition digest, and **read by nothing**. Two harnesses could differ in digest and be
byte-identical in behaviour — which would let a pre-registered, statistically analysed experiment
measure nothing while every artifact in the chain looked correct.

**That is `FT-10`, in the one place where it silently invalidates the experiment the whole system
exists to run.**

### 3.2 A changed digest must change behaviour

Metamorphic test: recompose with a mutated policy file and assert **at least one observable
differs**. If nothing differs, the component is decorative and the test fails.

---

## 4. Aliases

```json
{ "Read": "fs.read", "Grep": "fs.search", "Edit": "patch.apply", "Bash": "proc.exec" }
```

**Rules:**

1. Flat `{"alias": "verb"}` — one shape, no envelopes, no dialects.
2. Every alias **target** must be a manifest-declared verb. Otherwise **composition fails**.
3. Every tool schema `name` must be a declared verb **or** an alias key.
4. **No identity fallback.** An unknown name is an error, not a pass-through. `N-17`: *"unknown
   names fail at composition, not at first use."*
5. Aliases are **pack-local data**. A global Python dict of competitor tool names is a second
   ontology (`D-05`, `D-11`).

**Why aliases exist at all:** models are trained on `Read`/`Bash`/`Edit`. The model sees the alias;
the kernel sees the verb. That is a naming translation, never an authority translation.

---

## 5. Capabilities

```json
{"verb": "fs.read",     "sink": "observation", "selector": {"kind":"fs","root":"/workspace","paths":["/workspace"]}, "risk": "low"}
{"verb": "patch.apply", "sink": "privileged",  "selector": {"kind":"fs","root":"/workspace","paths":["/workspace"]}, "risk": "medium"}
{"verb": "proc.exec",   "sink": "privileged",  "selector": {"kind":"generic","uriPattern":"proc://exec/allow/git,pytest,ruff,python3"}, "risk": "high"}
```

| Field | Rule |
|---|---|
| `sink` | `pure` · `observation` · `privileged`. **Everything is recorded; only `privileged` traverses the kernel** (`L-17`). Misdeclaring a privileged effect as `pure` is adversarially tested |
| `selector` | Must be a kind with a **decidable** inclusion relation. Undefined pairs are **denied** |
| `risk` | Drives the approval threshold. A shell fallback is **never weaker** than the typed tool it substitutes for |

**A wider allowlist is a capability change**, reviewed as security — not as UX.

---

## 6. Authoring a reconstruction pack

A reconstruction differing only in prompt text is **not a reconstruction**. As of Sprint 9, a pack
must differ on **≥3** of:

compaction strategy · model routing · approval policy · turn budget · tool surface ·
search strategy · edit granularity

### Honesty requirements

- `REFERENCE.md` cites the **public** documents read and states what was **not** copied.
- Name it `*-shaped`. It reconstructs **tool surface + prompt + policy**, not a vendor's scheduler.
- **Never** claim "beats X" or "equivalent to X". A comparison against a faithful reimplementation
  is a comparison against **that reimplementation**, and must be labelled so.
- Do not copy proprietary prompts beyond what is public — legal exposure and contamination.

---

## 7. `vg-shell-only` is undeletable

The zero-assumption control arm. One tool, selector-scoped, no middleware, no skills, no
sub-agents. **Every claim that a typed tool, skill or context policy improves outcomes is measured
against this manifest, paired.**

`ManifestRegistry.remove` throws for it, and the guard test asserts both the refusal and the single
`proc.exec` capability. `GTS-13C` Ch. 14 lists "baseline manifest deleted as dead code" as a
standing risk — it is not dead code, it is the instrument's floor.

---

## 8. Checklist before opening a pack PR

- [ ] `Runtime.compose(<pack>)` succeeds; `composition_digest` stable across two composes
- [ ] Every capability verb has a binding; unwired verbs fail **at composition**
- [ ] Every alias target is a declared verb; every tool `name` resolves
- [ ] No component is declared without a consumer
- [ ] `REFERENCE.md` present for a reconstruction
- [ ] **Zero** diff in `kernel/**`, `agency/episode/**`, `domain/wire/**` (`BR-5`)
- [ ] `gene_digests` emitted so the pack is comparable
