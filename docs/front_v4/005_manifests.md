# 005 — Manifests in the client (Proposed)

Status: `Proposed`  
Date: 2026-08-16  
Schema owner: `vanguard/packages/domain/artifacts/manifest.py` (`parse_manifest`). FE must not fork the schema.

## Real shape

Required keys:

```text
{ harness, components, capabilities[{verb, sink, selector, risk}], evaluators, budgetPolicy }
```

`sink` ∈ `{pure, observation, privileged}`.

The client may **display** a user-supplied manifest file (path on `StartRun.manifestPath`). The client must **not** walk `vanguard/packages/agency/manifests/` as a discovery API.

## Discovery

A `ListManifests` daemon verb does **not** exist. That is Joint **J3**. Until then:

- operator passes `--manifest` / IDE setting with a filesystem path;
- missing path → `invalid_request` / `not_found`;
- no silent default that reads the core tree.

## Subagents

Multi-agent / subagent UX is **Phase-2 deferred (DEF-03)**. Do not ship subagent panels as product.

## Capabilities UI

Show declared `verb` / `sink` / `risk` from the file the user pointed at. Do not invent extra capability rows.
