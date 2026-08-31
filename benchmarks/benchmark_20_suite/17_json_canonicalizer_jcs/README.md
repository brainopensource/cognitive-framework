# Greenfield PRD: Deterministic RFC-8785 JSON Canonicalizer (JCS)

## Objective
Implement `canonicalize(data: Any) -> bytes` and `canonical_digest(data: Any) -> str` in `src/jcs.py`.

## Requirements
- Sort dictionary keys deterministically by UTF-16 code units (Unicode code point order).
- Serialize without extraneous whitespace (e.g. `{"a":1,"b":2}`).
- Floats without fractional parts formatted with standard representation (e.g. `1.0` -> `1.0` or integer rules).
- Return exact deterministic UTF-8 encoded bytes.
- `canonical_digest` returns SHA-256 hexadecimal string of canonical bytes.
