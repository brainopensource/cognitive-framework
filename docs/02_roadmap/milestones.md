# Milestones — v0.5.0 = MHF v1 = M0–M6

**Rewritten** at the v0.5.0 Foundation Lock (`docs/MASTER_REFACTOR_GUIDELINE_FINAL.md`), replacing the
former v0.5.0→v1.0.0 ladder (v0.6 "Molecular Lattice", v0.7 benchmarking, v0.8 memory graphs, v0.9 meta).
Source: `docs/TECH_LEAD_REVIEW/02_ROADMAP_BACKLOG_AND_REVIEW_TRIAGE.md` §3.

**Renumbering note.** The merged PR `feature_v050_meta-harness` and the sprint board it produced
(`docs/03_sprints/sprint_active.md` at commit `b79093c`, "v0.6.0 Molecular Lattice") used the *old*
numbering scheme. Under this scheme: old "v0.5.0 Empirical Baseline" work is absorbed into this M0's
docs lane plus the ground-truth verification already done in `docs/SPEC.md` §8.2; old "v0.6.0 Molecular
Lattice" (`coding_*` extraction, single router, root.py split) maps onto **M3** below, not a separate
version; former v0.8 `(G_C, G_E)` graphs map onto **M5/Phase-2** (§6.1 in `docs/SPEC.md`); former v0.9
operators/playbooks map onto the honour table (permanent refusal, `docs/SPEC.md` §9). Old PR/commit
messages citing "v0.6.0" refer to what this ladder now calls M3.

**Standing rule** (from the roadmap triage §0): an item enters v0.5.0 only if it lands in **Layer 0**,
the **plugin runtime**, or the **Phase-1 Coding Pack**. Everything else is a Phase-2/3 plugin (named
target below) or dead (`docs/05_adr/DEFERRED_REJECTED.md`).

| Milestone | Duration | Outcome | Exit gate (proof command) |
|---|---|---|---|
| **M0 — Docs & Excise** | 1 sprint (docs lane: this wave, done; code/purge lane: staged, not started) | Docs collapsed per migration matrix (`docs/SPEC.md` landed); code-side excise (artifact/secret purge, frontend removal, repo-size ≤ 3MB) is a separately authorised follow-on — see `docs/03_sprints/plans/m0-code-and-purge.md` | `G-M0-DOCS`: docs gates in `docs/SPEC.md` §8 all green. `G-M0-PURGE` (not this wave): `scan_secrets.py --all-refs` PASS; repo ≤ 3 MB |
| **M1 — Layer 0** | 2 sprints | Kernel + events + JCS ported verbatim; full event taxonomy emitted; one generated `EffectRequest`; scheduler v1 (sequential, I-11); six-dim `Reservation`; trajectory record | `G-M1`: E-COV = 100% · `replay-parity` green (grants, budgets, approvals, lifecycle reconstructed) · mutation score ≥ 80% on kernel+reducers · `pytest test/layer0` green |
| **M2 — Plugin Runtime** | 2 sprints | Registry, lifecycle FSM, isolation broker (`in_process`+`subprocess` w/ rlimits+seccomp), SPI v1, `compose()` v2, walking-skeleton echo plugin, `mhf.model.local-adapter` demo | `G-M2`: echo plugin traverses DISCOVERED→RETIRED with full ledger trail · fault injection → `PluginFaulted` + fallback · hot-swap mid-run with attribution · `compose()` rejects unknown ref/alias · grant-ceiling ∩ enforced |
| **M3 — Coding Pack #1** | 2–3 sprints | `apps/coding/` (already extracted from `domain/`, `docs/SPEC.md` §8.2) + adapters re-extracted into plugins; ast-patch, repo-map, terminal (structured first-failure), fs/index toolkits; single router; container tier | `G-M3` (Phase-1 acceptance): compiled `code-default` ≥ v0.4.5 baseline on lab dogfood + `zero_hint_v1` under paired McNemar · un-mocked `oracle_green` on ≥1 greenfield task, live model, signed verdict · `grep -rE "coding|pytest|ast" layer0/` empty (I-7) |
| **M4 — Harness Parity** | 1 sprint | `code-claude-shaped`, `code-opencode-shaped`, `code-swe-mini`, `code-pi-shaped`, `table-default` recompiled as manifests | `G-M4`: 5 packs compile+run · `git diff --stat layer0/` = 0 across M4 · TableWorld registered (closes D-27) |
| **M5 — Phase-2 Plugins** *(v0.6.x)* | — | meta-reflector, genome mutation + lab selection, calibrated escalation, skill harvest; **prerequisite: 200-task suite** (statistical-power gate) | `G-M5`: one promoted mutation beats baseline, McNemar p<0.05, A/A floor respected, preregistered |
| **M6 — Distillation Loop** *(v0.6.x)* | — | Trajectory→DPO harvest; first fine-tuned tier-1 model behind cassette regression | `G-M6`: fine-tuned local model ≥ free-tier baseline pass rate at lower USD/episode |

## Preserved invariants (all versions)

Dispatch-only effect path, one-effect-per-turn at the kernel, fail-closed evaluation, boundary lattice —
restated in `docs/SPEC.md` (I-1…I-11). TCB LOC tripwire stays the *living* gate until M1's metric triple
(mutation score, control-call-site coverage, E-COV) lands — see `docs/04_annex/KERNEL.md` §1.1's amendment
note.

## Killed as a living claim

The vision-tier mapping (LEVEL 0–9 / cosmology) is deleted, not carried forward — `docs/05_adr/ADR-M0-10-no-metaphysics.md`.
