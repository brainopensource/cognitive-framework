# `schemas/v4/` — Normative wire contracts

**Authority.** The JSON Schema artifacts in this directory are **normative**. Document `04_vanguard_core_contracts_and_wire_schema_v040.md` is normative for their *semantics*; where a schema and a prose semantic rule appear to disagree, that is a defect to be fixed in both, not a precedence question (see `00 §1 [PR-4]`).

TypeScript validators are **implementations** verified against these schemas. They are never the source of truth. A TypeScript-first validator cannot express refinements, transforms or branded types in a way other languages can read, and a lossy derivative of a wire contract drifts silently and outlives the code that caused it.

---

## 1. Conventions

| # | Rule |
|---|---|
| SC-1 | JSON Schema **2020-12**. No other dialect |
| SC-2 | Canonicalisation is **RFC 8785 / JCS**. Every digest is computed over the canonical form |
| SC-3 | Integers that may exceed 2⁵³−1 (cost in micro-units, cumulative token counts, byte offsets) use the `IntString` type — decimal string, never a JSON number |
| SC-4 | Every schema declares `$id` as `https://vanguard.dev/schemas/v4/{name}.schema.json` and a `$comment` naming its owning section in `04` |
| SC-5 | Unknown fields: readers preserve them on round-trip; validators reject them only where the owning section says `additionalProperties: false` |
| SC-6 | Every schema ships with golden vectors under `vectors/{name}/` — at least one valid, one invalid-by-omission and one invalid-by-type case |
| SC-7 | Two independent implementations (TypeScript and Python) must agree on every vector before a schema is considered locked |
| SC-8 | Schema versions are additive. Event kinds are never removed. Every version bump ships a migration and a rehearsal against a synthetic corpus in CI |
| SC-9 | No generated schema dump is inlined into a markdown document. `04` carries typed excerpts with complete prose semantics and links here |
| SC-10 | Each schema is the **writer profile**: `additionalProperties: false`, strict per `04 [CT-11]`. A **reader profile** is generated from it by relaxing `additionalProperties` to `true` at every level, and readers validate against that profile. Validating a reader against the writer profile rejects future fields and breaks `04 [CT-44]` |
| SC-11 | Generation of the reader profile is mechanical and tested. The two profiles are never hand-maintained separately |

---

## 2. Layout

```
schemas/v4/
  README.md              this file
  MANIFEST.md            the planned artifact set, with owning sections and lock status
  *.schema.json          normative schemas (authored with document 04)
  vectors/
    README.md            vector conventions
    {name}/              golden vectors per schema
```

---

## 3. Lock discipline

The corpus format is the single most expensive thing to change: altering it means re-running everything ever recorded. Therefore:

- A schema marked `LOCKED` in `MANIFEST.md` changes only through an ADR in `09` with a migration and a rehearsal.
- A schema marked `DRAFT` may change freely, and **may not be used to record anything intended to survive**.
- Recording production trajectories against a `DRAFT` schema is a defect.
