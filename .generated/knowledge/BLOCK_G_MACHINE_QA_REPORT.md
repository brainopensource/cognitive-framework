# Block G — Generated Machine Layer and Mechanical QA

- Reconstruction HEAD: `8614a03ba1b6c27049e45d2f822771b63be05c40`
- AS_BUILT analysis subject: `9fd444674bf3a97f2673ff36a5f5928ef046c574`
- Canonical pages: **30**

## Generated artifacts

- `catalog.jsonl`, `headings.jsonl`, `relations.jsonl`, `code-map.jsonl`
- `reconciliation-ledger.jsonl`, `conflicts.jsonl`, `legacy-audit.jsonl`, `legacy-obsolete.jsonl`, `legacy-unresolved.jsonl`, `knowledge-loss-register.jsonl`
- `validation-results.json`, `retrieval-results.jsonl`, `generation-manifest.json`

## QA results

- Metadata: `PASS`
- Canonical IDs: `PASS`
- Canonical ownership: `PASS`
- Links/fragments: `FAIL`
- Relations/code map: `PASS` / `PASS`
- AS_BUILT/TARGET traceability: `FAIL`
- Retrieval: **15/16 (93.8%)**, threshold 90%
- Mechanical validation errors: **12**
- Repository linters: metadata, links, stale paths, falsifier IDs, and secret scan passed; the existing doc-budget check reports the known unrelated `docs/SPEC.md` 270/250 exception.

## Tool and scope controls

- Only Git, Python stdlib, `rg`, and existing repository checks were retained; optional tools were not installed.
- Generated records are derived from candidate Markdown and repository evidence; no generated file is a canonical authored owner.
- Frontend candidate work under `docs/candidate-docs/product/frontend/` was excluded.

## Retrieval exception

- The query `exact EffectRequest schema contract` ranked `ref.schemas` sixth because the candidate's exact implementation evidence is distributed across the schema, ports, and kernel pages. This is a recorded non-critical retrieval miss; the 15/16 result still exceeds the approved 90% top-three threshold.

## Block G gate

`BLOCK G EXIT GATE: FAIL`

Non-critical authority conflicts remain in `conflicts.jsonl` for Block H; they do not represent hidden omissions.
