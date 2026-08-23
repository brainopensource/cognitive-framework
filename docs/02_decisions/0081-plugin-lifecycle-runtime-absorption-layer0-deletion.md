---
adr: 0081
title: "Plugin lifecycle parity, runtime absorption, and terminal Layer-0 deletion"
status: accepted
accepted_date: 2026-08-21
source_section: "ALFA Tier S+ Director Ratification"
implementation_milestone: "M-3 / v0.6.2"
---

# ADR-0081: Plugin lifecycle parity, runtime absorption, and Layer-0 deletion

**Context.** The remaining `layer0/registry`, `layer0/compose`, and support events are the only
unabsorbed plugin-lifecycle implementation. Its seven-state FSM emits only five events:
`DISCOVERED` and `VERIFIED` are silent. The old compiler also discards a ceiling intersection,
and `pyproject.toml` still packages `layer0*`. Deleting the directory without packages-path
parity would remove the only walking skeleton; copying it unchanged would preserve its defects.

**Decision.**

1. Absorb the registry/lifecycle/broker behavior into `vanguard/packages/runtime/registry/` and
   converge compose behavior into the single packages composition root. Do not absorb a second
   event taxonomy, writer, store, selector algebra, or canonicalizer.
2. The canonical lifecycle is:

   ```text
   DISCOVERED -> RESOLVED -> VERIFIED -> ACTIVATED -> QUIESCING -> RETIRED
         \           \          \           \             \
          +-----------> FAULTED <-------------+-------------+
                            |
                            +----------------------------> RETIRED
   ```

3. Every state entry emits one owner-scoped event. Add `PluginDiscovered` and `PluginVerified` to
   the schema-generated event kind source, canonical catalog, registry-only writer table, reducer,
   plugin projection, conformance vectors, and coverage tests. Neither kind may be allowlisted as
   intentionally unfolded.
4. Verification is a state transition, not a boolean payload on `PluginResolved`. It records the
   resolved manifest/component digest, ceiling result, isolation result, and graph identity without
   secrets.
5. The ADR-M0-13 echo plugin must walk the full lifecycle over the canonical UDS/wire path, then
   fault under injection, before `code-default` plugins migrate.
6. Freeze-at-compose is mandatory: unknown refs/ranges/endpoints, missing interfaces, unread
   authority fields, empty ceilings, illegal isolation, or a frozen-graph mutation fail before a
   run starts.
7. NOVA-4 is the required negative suite. Falsifiers are never removed to fit the sprint; optional
   plugin breadth is removed first.
8. Final deletion is atomic with proof: delete all `layer0/` files and Layer-0 tests, remove the CI
   step and live documentation authority, remove `layer0*` from `pyproject.toml`, and leave the
   duplication/boundary suites green in the same change.
9. M-3 cannot close while any live import, packaging inclusion, CI authority, alternate parser, or
   lifecycle writer remains under `layer0/`.

**Bound falsifiers.** RF-38–RF-45 form NOVA-4. RF-43 proves every legal lifecycle transition is
catalogued, registry-owned, emitted, and reduced; illegal transitions and non-registry writes are
denied. RF-45 proves `layer0/` is absent from source, packages, tests, CI, and living navigation.

**Alternatives rejected.** Repairing the fork in place; deleting before parity; retaining
`layer0.events`; folding `VERIFIED` into another event; or leaving packaging inclusion after source
deletion.

**Reversal condition.** NOVA-4 proves that the absorbed registry semantics are irreparable. In
that case the fork is still deleted, but a fresh packages-path lifecycle is written behind the same
wire and falsifiers under a newer ADR.

**Owner · status.** Runtime Lead / Plugin Boundary Owner · accepted by Engineering Director ·
2026-08-21
