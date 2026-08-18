# Sprint 7 · Joint Track — Tech Lead + Project Lead

**Owners:** Tech Lead + Project Lead (joint signature required on every row)
**Backlog:** `011 §4.4`
**Write scope:** `docs/main_v4/**` · `LICENSE` · git history remediation · `VG-00 §11`
**Not delegable.** These rows carry authority decisions or touch repository history.

---

## Completed this sprint

| ID | Item | Evidence |
|---|---|---|
| `S7-J-01` | **`ADR-0063`** — control plane is Python; `ADR-0001` reversed on evidence | `VG-09 §12`; `VG-02 §9` stack table corrected |
| `S7-J-02` | **`ADR-0064`** — MVP gate status recorded: Q1 partial+regressed, Q2/Q3/Q4 not met | `VG-09 §12`, with per-gate reversal conditions |
| `S7-J-03` | **`ADR-0065`** — D-01…D-15 adopted as binding | `VG-09 §12` |

### Why `ADR-0063` mattered

`ADR-0001` said TypeScript, status `accepted`. 15,569 lines of Python control plane shipped.
`VG-02 §9` — a **NORMATIVE** document — still stated TypeScript. `ADR-0059`/`ADR-0060` referred to
"the Python microkernel" as settled fact. No ADR superseded `ADR-0001`.

The Python choice is correct and was ratified, not reversed. But an unrecorded reversal in an
append-only register is precisely what `ADR-0000` exists to prevent, and it left a normative
document asserting something false about the system.

**The lesson for this sprint:** a locked decision living in prose drifts. That is also why
`ADR-0065` moves D-01…D-15 out of a review file and into the register.

### Why `ADR-0064` mattered

Gate status existed only as a table inside a review document. A table is not a governance artifact.
With Sprint 6B receipts on record and two kernel-bypassing paths added afterwards, the programme
was one confident summary away from describing Q1 as closed. `ADR-0064` makes each gate reverse
**individually**, on named evidence, in a named sprint.

---

## S7-J-04 — `SEC-01` remediation · **HIGHEST SEVERITY OPEN ITEM**

```
$ python3 tools/scan_secrets.py            → SECRET SCAN PASS
$ python3 tools/scan_secrets.py --all-refs → SECRET SCAN FAIL: reachable-object: env-named blob .env
$ git for-each-ref | grep -c refs/original → 21
```

A previously committed OpenRouter credential **remains reachable in history**. The prior audit
named this (`mvp_beta_delivery_audit` P0-08) and it was carried as stale. The v0.4.3 review set
asserted the opposite (`007 §6`) on the evidence of `git ls-files` — **which reports HEAD, not
history.** Corrected; recorded as `DECISION-0006`.

**The generalisable defect is worse than the finding: the scanner was only ever run in its passing
mode.** `A-10` — a gate that cannot fail is not a gate — extends to a gate whose failing mode is
never invoked.

### Binding order — do not reorder

- [ ] **Step 1 — rotate at the provider.** Revoke the credential at OpenRouter **first**. Until
      this is done, everything else is cosmetic. A rotated key makes the history a hygiene problem
      instead of an incident
- [ ] **Step 2 — authorisation.** Repository owner authorises a history rewrite in writing. This is
      not an engineering decision; it invalidates every existing clone
- [ ] **Step 3 — enumerate.** Identify every affected ref, including all 21 `refs/original`. If a
      ref's owner cannot be identified, **stop** and escalate
- [ ] **Step 4 — rewrite.** Coordinated across every local and remote ref
- [ ] **Step 5 — remove backup refs.** `refs/original` must be empty
- [ ] **Step 6 — force-update the authorised remote; announce clone invalidation**
- [ ] **Step 7 — verify.** `scan_secrets.py --all-refs` PASSes **and** a fresh clean clone scans
      clean. Both, not either
- [ ] **Step 8 — CI runs `--all-refs`, not the lenient default.** This is the row that prevents
      recurrence and it is the one most likely to be skipped

> **Never place the secret value in a ticket, command line, log, receipt or commit message** —
> including during remediation. A remediation that leaks the secret into a PR description has
> widened the exposure.

---

## S7-J-05 — Add `LICENSE`

`pyproject.toml` declares `license = {text = "Apache-2.0"}`. No `LICENSE` file exists.

- [ ] Add the Apache-2.0 text matching the declared metadata
- [ ] Verify `ls LICENSE` succeeds and the package metadata agrees

Small, but a distribution blocker and a legal one — the package currently claims a licence it does
not ship.

---

## S7-J-06 — Promote the measurement science into `VG-07`

Three bodies of correct, load-bearing work currently live in **non-normative review files**, where
nothing binds them. `ADR-0001`'s drift is the argument for moving them.

- [ ] **C1–C12 cheating taxonomy** — the operational definition of an invalid run
- [ ] **The 9 evidence labels** — `lam-replay` … `paired-holdout`; partly coded in
      `tools/002_LLM_API_MOCK/verdict.py`
- [ ] **Splits** `DEV/HOLDOUT/SEALED/LIVE/DEPLOYMENT`, one-way contamination, touch ledger
      (`M-19`, `M-20`)
- [ ] **Outcome algebra** — `pass`/`public_overfit`/`fail`/`abandoned`/`inconclusive`/`invalid`
- [ ] **12-layer FUAA** and the **three evidence levels** (public contract / architectural
      inference / unverifiable)
- [ ] Update `VG-00 §6` normative rules index
- [ ] Record the promotion as a correction in `VG-09 §4`

> **`T10.7` check:** these are **corrections and promotions of existing practice**, not new
> normative rules, so they do not trip the "no new normative rule while a contract row is
> uncovered" gate. Record them as such, explicitly.

---

## S7-J-07 — Review WIP protocol

- [ ] Cap `docs/reviews/doing/` at **8 documents**. A new review may not be created while the cap
      is met — the WIP limit is what converts reviewing into deciding
- [ ] `docs/reviews/todo/` is **abolished** (done this sprint). A review nobody has scheduled is
      not a todo, it is an opinion
- [ ] Every archived document carries a closure header naming what superseded it (done for all 13)
- [ ] Record the protocol in `VG-00 §11` (retirement protocol)

**The evidence this was needed:** 5,494 lines of review against 4,928 lines of specification, ten
NO-GO verdicts, zero closures — while Sprint 6B had silently closed 8 of 9 blockers. Those
documents were not merely stale; they were **actively misleading**, and they misled this
programme's own review two turns ago.

---

## S7-J-08 — `ADR-0066`: MCP adapter rules, pre-recorded

No MCP code exists. Record the rules now, while they are cheap.

- [ ] An MCP tool is an `EffectAdapter`, **never a second dispatch path**. It resolves at
      composition into `DEFAULT_BINDINGS` and takes `sinkClass` + selector from the manifest
      capability row like any other verb. `AT-01` must still hold
- [ ] An MCP server's declared tool list is **untrusted content**. Discovered *between* episodes
      under signed allow-listing (`T7.7`, `L-11`), frozen at composition, descriptions entering
      context with an untrusted provenance label (`A-04`, `N-09`). **A tool description is a
      prompt-injection vector**
- [ ] Network egress to an MCP server is a `privileged` effect with a `host`-kind selector.
      An MCP server on localhost is still egress

> The 2026 literature is explicit that none of MCP/A2A/ACP can express a capability grant. That
> layer is ours, and it is a genuine differentiator — provided we do not let a protocol adapter
> become a second dispatch path on the way in.

---

## Sprint 7 sign-off checklist

Joint signature required. Every box needs a command and its output.

- [ ] Lane A, B, C definitions of done all green
- [ ] `scan_secrets.py --all-refs` PASSes; `refs/original` empty
- [ ] `LICENSE` present and consistent with `pyproject.toml`
- [ ] `ADR-0063`…`ADR-0066` merged; `VG-02 §9` no longer states a false stack
- [ ] `VG-07` amended; `VG-00 §6` index updated; promotion recorded in `VG-09 §4`
- [ ] Net LOC ≈ **−1,530**; TCB still under budget
- [ ] **Q1 evidence pack assembled** — architecture tests + broken counterparts + the absence of
      any second execution path — and `ADR-0064`'s Q1 row reversed **or explicitly not reversed**

> Q1 is the only gate this sprint can close. If the evidence does not support closing it, **say so
> and leave `ADR-0064` unchanged.** That is the entire point of having written it down.
