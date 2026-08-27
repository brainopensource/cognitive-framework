# M-5 — Second-Domain Generality Proof (Formal Pack #2)

**Class:** engineering report (non-normative)
**Governing sources:** `001_alfa_review_full_decision.md` §4, `Higgs_update_concepts.md` §16 (L903–913)
**Exit gate:** RF-86 — zero semantic diff under `domain/`, `ports/`, `kernel/`, `agency/episode/`, `runtime/`

---

## 1. What M-5 is actually claiming

M-5 is not "add a math feature." It is a **falsification attempt against the
substrate's own generality claim.** The thesis under test:

> The difference between a coding agent and a formal-methods agent is entirely
> expressible as packs and adapters. The trusted core does not know which domain
> it is running.

The gate is therefore a *diff assertion*, not a feature checklist. `001_alfa` §4
states the consequence plainly: a Pack #2 that requires changes to `domain/` or
`kernel/` **fails the generality thesis**. It does not get a waiver — it returns
an architectural finding.

This is an unusually honest milestone design and it should be preserved as
written. The temptation during implementation is always to add "one small hook"
to the kernel. The gate exists specifically to make that visible.

---

## 2. Evidence that the substrate is already domain-blind

The existing `code-explain` pack is **30 lines of JSON and one text file** with no
Python whatsoever. Authority is expressed as `verb + sink + selector + risk`.
Nothing in that tuple is coding-specific. Pack #2 was authored the same way.

Verb disjointness was verified mechanically:

```
verb overlap with coding pack: set()   (fully disjoint domain)
privileged verbs:              ['proof.emit']
```

The formal pack shares **zero verbs** with the coding pack, yet reuses its
`context-policy`, `routing-policy`, and `approval-policy` by reference. That
combination — disjoint domain vocabulary, shared control policy — is precisely
what the generality claim predicts.

### 2.1 Sink assignment is the security-bearing decision

```json
{ "verb": "formal.check", "sink": "observation", "risk": "low"  }
{ "verb": "proof.emit",   "sink": "privileged",  "risk": "high" }
```

`proof.emit` is `privileged` because it mutates the workspace. This forces it
through the same grant/approval/reservation path that `patch.apply` takes in the
coding pack — **same kernel, different noun.** Had it been marked `observation`
for convenience, a formal agent could have written witnesses without a grant,
and the generality proof would have been bought by weakening authority. The
sink taxonomy is where domain-blindness is either real or fake.

---

## 3. T0 witness memoisation

`001_alfa` §4 fixes the memo key exactly. The implementation enforces all seven
fields and refuses to default any of them.

```python
MEMO_FIELDS = ("obligation","input_digests","environment_digest",
               "checker_identity","toolchain_version",
               "assurance_level","policy_version")

def memo_key(**kw):
    if missing := [f for f in MEMO_FIELDS if f not in kw]:
        raise ValueError(f"memo key missing required field(s): {missing}")
    return digest_of({f: kw[f] for f in MEMO_FIELDS})
```

### 3.1 Why each field is load-bearing

Omitting any one produces a specific unsoundness:

| omitted | attack it enables |
|---|---|
| `assurance_level` | a witness computed under `recorded` satisfies a `hermetic` obligation |
| `checker_identity` | a weaker checker's result is reused under a stronger checker |
| `toolchain_version` | a solver bug fixed upstream is silently reintroduced from cache |
| `environment_digest` | a proof about workspace A satisfies a goal about workspace B |
| `policy_version` | a superseded policy's verdict outlives its own retirement |
| `input_digests` | a proof about different premises is replayed |
| `obligation` | trivially unsound |

Verified: mutating **any** of the seven changes the key; a missing field raises
rather than silently defaulting.

### 3.2 The memoisation law

A memo hit narrows **work**, never **authority**. It returns through the same
receipt path and is still checked exteriorly:

```
solve            : unsat memo_hit=False solver_calls=1 tokens=None
memo             : unsat memo_hit=True  solver_calls=1  (stayed 1)
assurance change : memo_hit=False       solver_calls=2  (correctly missed)
```

That third line is the soundness property under test: raising assurance
**must** invalidate the cache. This is `001_alfa` law #2 — cached success may
narrow behaviour but may never widen authority.

---

## 4. Cost honesty: no fabricated zeros

`001_alfa` law #5: absent measurement is *unavailable plus reason*, never zero.
A solver call consumes no model tokens, and the naive encoding is `tokens: 0`,
which is a lie that corrupts every downstream cost aggregation.

```python
Cost(millis=r.millis, tokens=None, tokens_reason="not_a_model_call")
```

Verified: `r.cost.tokens is None` and `r.cost.tokens_reason` is non-empty.

---

## 5. The exterior oracle replays; it does not re-solve

The single most important line in this milestone:

```python
# CRITICAL: the oracle REPLAYS the proof term. It does not re-solve.
# If it re-ran the solver it would be the prover again, and the verdict
# would be self-issued -- failing the exterior-truth law (001_alfa L4).
ok = self._checker.check(protocol.theorem, run_ref.proof_bytes)
```

An oracle that re-invokes the solver is not an independent checker — it is a
second instance of the thing being evaluated. It would agree with the prover by
construction, including on shared bugs. Proof-term replay is cheap, independent,
and is what makes the Ed25519 verdict meaningful.

The signed body binds the full lineage so the auditor can recompute every join:

```python
body = {"api":"mhf.verdict/1", "outcome":…, "subject": D_X, "harness": D_H,
        "run": D_R, "runId":…, "episodeId":…, "taskDigest":…,
        "oracleDigest":…, "preregistrationDigest":…, "protocol":…, "keyId":…}
```

Negative cases, all verified:

| case | result |
|---|---|
| valid proof, correct key | `pass`, signature verifies |
| body tampered post-signature | verification **fails** |
| verified against a foreign key | verification **fails** |
| preregistration digest mismatch (post-hoc) | `invalid / preregistration_mismatch` |
| bogus proof term | `fail / proof_did_not_replay` |

Post-hoc preregistration is rejected *before* the proof is even checked. An
oracle that would sign a verdict for a task registered after the run started
cannot produce eligible evidence, regardless of proof validity.

---

## 6. The RF-86 gate

```python
FROZEN = ["domain","kernel","ports","runtime","agency/episode"]

def test_formal_pack_requires_zero_substrate_diff(self):
    for path in FROZEN:
        d = git_diff("--stat","M-5-BASE","--",f"vanguard/packages/{path}")
        self.assertEqual(d, "", f"M-5 mutated frozen substrate {path}")
```

Current measured baseline:

```
frozen substrate diff : 0 files
kernel TCB            : 1737 LOC (unchanged)
```

**Recommendation: tag `M-5-BASE` immediately and wire this into CI on day one**,
before any further M-5 work lands. Its value is entirely in catching the
incremental hook, and a gate added at the end of a milestone catches nothing.

---

## 7. Verification

```
tests/test_m5_formal.py ............ 12 passed
  memo soundness           4
  formal environment       3
  exterior oracle          5
```

## 8. Residual risk

The bundled checker is a stub replayer. A production M-5 needs a real proof-term
checker (LFSC, Alethe, or Lean kernel export). **The oracle's isolation boundary
matters more than the solver's power**: a weak checker that is genuinely
independent is worth more than a strong one that shares a process with the prover.
