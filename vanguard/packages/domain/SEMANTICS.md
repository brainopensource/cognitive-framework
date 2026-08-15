# `domain` — semantic rules and ADR candidates (Sprint 1, Dev 1)

Covers `REQ-SCHEMA-001..003` / `S1-D1-001..003`.

`schemas/v4/*.schema.json` is normative for structure (`CT-01`). This file
records the rules the readers enforce that **JSON Schema cannot express**, and
the places where VG-04's prose left a decision open. Nothing here is a schema
change: every rule below is additive to the schema and is marked
`schemaAccepts` in the vector set, so a schema-only validator is never held to
a constraint the normative artifact does not carry.

Per the Dev 1 packet, ambiguities go to the Tech Lead as ADR candidates rather
than being resolved silently. The three below are **decided in this reader in
the conservative direction and are open for an ADR**.

---

## 1. Rules the readers add on top of the schema

| # | Type | Rule | Why it cannot live in the schema |
|---|---|---|---|
| `S-1` | `Timestamp` | The value must denote a real UTC instant: calendar-valid month and day including Gregorian leap rules, `hour ≤ 23`, `minute ≤ 59`, `second ≤ 59` | A regular expression cannot decide whether February has 29 days in a given year |
| `S-2` | `Timestamp` | Leap seconds (`:60`) are denied, not truncated | `CT-08` asks for one unambiguous cross-language ordering; `:60` is a value no two arithmetic libraries agree on |
| `S-3` | `fs` selector | Paths are normalised per `D-2`, and a path that ascends past its own start fails to parse | Path arithmetic is not a schema keyword. Clamping the ascent instead would silently widen the surface |
| `S-4` | `fs`, `git` selectors | Glob and pattern metacharacters (`* ? [ ] { }`) are rejected | `04 §5.3.1`: "no globs in a grant — expand at issuance" |
| `S-5` | `network` selector | Hosts are NFC-normalised, lowercased, root-dot-stripped and IDNA A-label encoded before comparison | Host equality is a normalisation question, not a shape question |
| `S-6` | `browser` selector | The origin must be exactly scheme, host and optional port; a path, userinfo or wildcard fails to parse, and a default port is dropped | `04 §5.3.1`: origin is the browser's own trust unit |
| `S-7` | all selectors | The canonical form prunes members another member already covers, and orders what remains | Required for antisymmetry: `/repo` and `/repo` + `/repo/src` denote one authority and must reduce to one set of bytes |

Canonicalisation itself adds **nothing** to RFC 8785 (`CT-04`, VG-04 §0.3). In
particular, integers beyond 2⁵³−1 are canonicalised as the IEEE-754 doubles
RFC 8785 says they are; keeping such a value exact is `IntString`'s job at the
schema layer (VG-04 §0.4). Rejecting them inside the canonicaliser would be a
local variation, and a reader that rejects what another reader accepts is the
exact failure `REQ-SCHEMA-001` exists to prevent.

---

## 2. ADR candidates

### `ADR-CAND-D1-001` — timestamp validity is a semantic rule, not a pattern

**Question.** `primitives.schema.json` constrains `Timestamp` by pattern only,
so `2026-02-29T00:00:00.000Z` and `2026-13-45T99:99:99.999Z` are schema-valid.
Should the readers accept them?

**Decision taken here.** Deny. A timestamp that does not name an instant
cannot be ordered, and `CT-08` exists to make ordering unambiguous. The
rejection is recorded with code `semantic` and the affected vectors carry
`schemaAccepts: true`.

**For the Tech Lead.** Either (a) accept this as a documented semantic rule
with `format: date-time` added to the schema as an annotation, or (b) require
the readers to accept schema-valid impossible instants. Option (b) puts an
unorderable value into a permanent corpus, which is why it was not chosen
unilaterally.

### `ADR-CAND-D1-002` — a parent wildcard contains itself

**Question.** `04 §5.3.1` says a parent wildcard "contains a child label but
never another wildcard". Read literally, `*.example.com` does not contain
`*.example.com`, and `includes` is then not reflexive — which contradicts
`REQ-SCHEMA-003`'s requirement of a partial order.

**Decision taken here.** Literal identity always includes: `includes(x, x)`
holds for every parseable selector, wildcards included. The wildcard rule
governs every *non-identical* pair, so `*.example.com` still never contains
`*.a.example.com`, and never contains the apex.

**For the Tech Lead.** Confirm the reading. The alternative — a non-reflexive
relation — makes "a grant includes itself" false and would break attenuation
checks on re-issued grants.

### `ADR-CAND-D1-003` — `table` ranges need a coordinate grammar

**Question.** `04 §5.3.1` requires "interval containment on normalised
coordinates" for `table`, and `resource-selector.schema.json` types `ranges`
as free strings. No coordinate grammar exists anywhere in v4, so containment
is undecidable as specified.

**Decision taken here.** Exactly one grammar is defined and everything else is
denied: `*` for the whole table, or `lo..hi` — a half-open interval over
decimal non-negative integers with `lo < hi`. An absent `ranges` normalises to
`["*"]`. Containment is per parent range: a child range must sit inside a
**single** parent range, never inside the union of several, because union
containment is the kind of approximation `CT-52` and `04 §5.3.1` warn about.

**For the Tech Lead.** This grammar is a placeholder chosen to be decidable
and conservative, and it is the one rule here that is likely wrong in
substance — `TableWorld` (`VG-03 §341`) may want named columns or version
coordinates. An ADR should either adopt this grammar into
`resource-selector.schema.json` as a pattern or replace it. Until then, every
other spelling of a range fails to parse, so nothing is silently widened.

### Open, not decided: UTS-46 versus bare punycode

The two readers reach IDNA through different host facilities (Python's
`punycode` codec after explicit NFC and case folding; the platform URL parser
in Node). They agree on every vector and on the generated population, but full
UTS-46 mapping differences on exotic labels are not proven equal. If IDNA
handling ever becomes load-bearing beyond host equality, this needs a vendored
implementation rather than two host libraries — the same argument `04 §0.3`
makes for canonicalisation.
