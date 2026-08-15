# domain

Pure types and reducers. No project imports and no I/O.

`contracts.ts` contains the Sprint 1 wire-domain types, constructors, strict parsers,
and serialization helpers. The normative repository schemas remain under
`schemas/v4/`; candidate Receipt and Artifact schemas live in `schemas/` here until
their schema-owner review.

Run `npm test` in this directory to exercise round trips, semantic validation, and
independent Python JSON Schema conformance.
