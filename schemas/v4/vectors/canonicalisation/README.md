# `canonicalisation/` — the golden triples (`GV-2`)

`REQ-SCHEMA-001`: canonical bytes use RFC 8785/JCS without local variation, and
at least 40 golden input-to-canonical-to-digest triples agree across readers.

```
canonical/{case}.json     input, deliberately un-canonical: reordered keys,
                          whitespace, escaped code points
canonical/{case}.jcs      the RFC 8785 canonical form, exact bytes, no newline
canonical/{case}.digest   `sha256:` over those bytes (`CT-09`, `SC-2`)
```

The triples are data, not tests. `test/contracts/t1_dev1_canonicalisation.py`
replays every one of them through both readers and compares bytes and digests.

**Coverage.** Key ordering (including the UTF-16 code-unit order that differs
from code-point order for astral characters), string escaping, the full
ECMAScript number grammar including its exponent boundaries, denormals, the
`2^53` boundary, negative zero, empty containers, deep nesting, and the
Vanguard wire shapes that carry digests — effect descriptor, capability grant,
event envelope, evidence claim, resource selector, provenance axes.

**Provenance.** The `.jcs` bytes were produced by the TypeScript reader, whose
scalar rules are the ECMAScript ones RFC 8785 adopts by reference, and every
case was required to match the independently written Python reader before it
was written to disk. `GV-5` still applies: a vector is never edited to make an
implementation pass.
