# Golden vectors

Vectors are **data**, not tests. They are the cross-language contract, and their guarantee is bounded: agreement on every vector is evidence of agreement on the schema, **never proof of it** — a finite suite cannot establish equivalence over an infinite instance space. Disagreement is conclusive; agreement is corroboration. Property tests (`04 §17`) cover the space vectors cannot.

## Layout

```
vectors/{schema-name}/
  valid/{case}.json          must validate
  invalid/{case}.json        must fail, with the expected error keyword in {case}.expect.json
  canonical/{case}.json      input
  canonical/{case}.jcs       the RFC 8785 canonical form
  canonical/{case}.digest    the digest over the canonical form
```

## Rules

| # | Rule |
|---|---|
| GV-1 | Every schema has at least one valid case, one invalid-by-omission case and one invalid-by-type case |
| GV-2 | Every type carrying a digest has a canonicalisation triple (input, canonical form, digest). The shared triple set lives in `canonicalisation/` (`REQ-SCHEMA-001`) and is replayed through both readers by `test/contracts/t1_dev1_canonicalisation.py` |
| GV-3 | Vectors are written **before** the second implementation exists — that is the point of writing them as data |
| GV-4 | Two implementations at the first lock: TypeScript and Python. A third is added when a third consumer exists, not before |
| GV-5 | A vector is never edited to make an implementation pass. It is edited only when the schema's semantics change, under an ADR |
| GV-6 | Every case is **pure instance data**. Schemas set `additionalProperties: false`, so annotations live in a sibling `{case}.note.txt`, never inside the instance |
