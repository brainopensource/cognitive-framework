# Dev 1 — two-reader evidence report

Tickets `S1-D1-001..003` · Requirements `REQ-SCHEMA-001..003` ·
Branch `sprint1/dev1-primitives` · Date 2026-08-15

Status: **local evidence only.** The packet index gate is open, so nothing
here is a product merge and no schema moves to `LOCKED` (`SC-12`, plus the T0
human gates recorded in `docs/sprint1/README.md`).

## What was built

Two independent readers under `vanguard/packages/domain/`, per `SC-7` and
`GV-4` — TypeScript and Python. `schemas/v4/` stays normative; both readers
are implementations verified against it (`CT-01`).

| Component | Files | Requirement |
|---|---|---|
| RFC 8785 / JCS canonicalisation and digests | `canonicalisation/jcs.{ts,py}`, `canonicalisation/digest.{ts,py}` | `REQ-SCHEMA-001` |
| Opaque boundary-parsed primitives | `primitives/primitives.{ts,py}` | `REQ-SCHEMA-002` |
| `ResourceSelector` inclusion algebra | `selectors/resource-selector.ts`, `selectors/resource_selector.py` | `REQ-SCHEMA-003` |

The Python reader re-derives the ECMAScript number and string rules rather
than delegating to a serialiser, so cross-reader agreement is evidence rather
than tautology. It was differentially checked against `JSON.stringify` over
99,994 doubles — random bit patterns, denormals, the exponent boundaries and
the `2^53` boundary — with zero mismatches.

## Evidence

Command: `python3 -m unittest test.contracts.test_t1`
(the Active MVP Contract registry command for `TEST-SCHEMA-001..003`).
Result: 60 tests, all passing, ~2 s.

| Requirement | Acceptance evidence asked for | Produced |
|---|---|---|
| `REQ-SCHEMA-001` | 40+ shared golden triples pass in both readers with identical canonical bytes and digests | **48 triples** in `schemas/v4/vectors/canonicalisation/canonical/`, replayed byte-for-byte through both readers, plus 400 generated values and 9 must-reject inputs. Zero cross-reader mismatches |
| `REQ-SCHEMA-002` | Shared valid/invalid vectors prove parse, rejection and round-trip for every primitive | **36 valid and 51 invalid vectors** across 16 primitive rules; every reader kind is covered or is a schema-declared `Identifier` alias, asserted against `primitives.schema.json` itself; round-trip through canonical JSON on every valid vector |
| `REQ-SCHEMA-003` | Property tests cover every selector kind; must-fail vectors cover unknown and cross-kind pairs | **50 inclusion vectors** (18 valid + 18 invalid instances), all seven kinds; seeded property runs over a 120-selector population proving reflexivity, transitivity, antisymmetry up to canonical equality, totality and fail-closed denial; 400 generated pairs cross-checked between readers |

Margins: zero cross-reader mismatches; zero casts at external boundaries
(parsing is the only constructor); zero unknown-as-allow outcomes — every
unparseable, cross-kind or undefined pair returns a denial with its reason.

## Decisions taken, and what needs a Tech Lead ruling

`vanguard/packages/domain/SEMANTICS.md` carries the detail. Three ADR
candidates, all resolved conservatively in-reader and all open:

* `ADR-CAND-D1-001` — timestamp validity is enforced as a semantic rule; the
  schema pattern alone accepts impossible instants.
* `ADR-CAND-D1-002` — a wildcard host includes itself, so `includes` stays
  reflexive. `04 §5.3.1` read literally makes the relation non-reflexive,
  which contradicts `REQ-SCHEMA-003`.
* `ADR-CAND-D1-003` — `table` ranges had no coordinate grammar anywhere in
  v4. One decidable grammar (`*` or `lo..hi`) is defined and everything else
  is denied. This is the candidate most likely to be wrong in substance.

One rule was **not** added despite looking attractive: the canonicaliser does
not reject integers beyond 2⁵³−1. RFC 8785 numbers are IEEE-754 doubles, a
JavaScript reader cannot distinguish such a value from any other double, and a
reader that rejects what another accepts is exactly the failure
`REQ-SCHEMA-001` exists to prevent. Keeping those values exact is `IntString`'s
job at the schema layer (VG-04 §0.4, `CT-06`).

## Blocked on governance

`.github/workflows/ci.yml` is covered by the `APPROVAL-0002` baseline manifest,
so it was not edited here. The `sprint0-gates` job installs Python but not
Node, and the TypeScript reader needs **Node ≥ 22.18** (native type stripping;
`CT-02` keeps types derived from schemas rather than adding a build artifact
that can drift). The suite fails loudly rather than skipping when the second
reader is unavailable, because a green run without it would claim two-reader
agreement that was never tested.

**Requested:** add `actions/setup-node@v4` with `node-version: '24'` to the
`sprint0-gates` job, and re-baseline the manifest under the existing approval
process.
