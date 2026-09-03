"""RFC 8785 (JCS) canonical JSON — Python reader.

Owning contract: VG-04 §0.3 / `CT-04`, `SC-2`, `REQ-SCHEMA-001`.

Pure values only: no I/O, no clock, no randomness, no environment access
(`system-architecture-icd.md` §2, `domain` row).

The implementation is deliberately independent of the TypeScript reader: it
re-derives ECMAScript `Number::toString` and the JSON string escape table
rather than delegating to a host serialiser, so that agreement between the two
readers on the golden triples is evidence rather than tautology.
"""

from __future__ import annotations

import json
import math
import re
from typing import Any

__all__ = [
    "CanonicalisationError",
    "canonicalise",
    "canonical_bytes",
    "canonicalise_text",
    "parse_json_text",
    "serialise_number",
    "serialise_string",
    "utf16_sort_key",
]


class CanonicalisationError(ValueError):
    """Input cannot be represented in canonical form. Always fail closed."""


# --------------------------------------------------------------------------
# Strings — RFC 8785 §3.2.2.2 (the ECMAScript `JSON.stringify` escape table).
# --------------------------------------------------------------------------

_SHORT_ESCAPES = {
    0x08: "\\b",
    0x09: "\\t",
    0x0A: "\\n",
    0x0C: "\\f",
    0x0D: "\\r",
    0x22: '\\"',
    0x5C: "\\\\",
}


def serialise_string(value: str) -> str:
    """Escape `value` per RFC 8785 §3.2.2.2.

    Only the two mandatory escapes and the five short control escapes are
    used; every other C0 control becomes a lowercase `\\u00xx` sequence and
    every other code point is emitted literally as UTF-8 (`CT-13`).
    """
    out = ['"']
    for char in value:
        code = ord(char)
        short = _SHORT_ESCAPES.get(code)
        if short is not None:
            out.append(short)
        elif code < 0x20:
            out.append(f"\\u{code:04x}")
        elif 0xD800 <= code <= 0xDFFF:
            # A lone surrogate cannot be encoded as UTF-8. `CT-13` forbids it
            # on the wire, so there is no canonical form to produce.
            raise CanonicalisationError(
                f"lone surrogate U+{code:04X} is not valid UTF-8 (CT-13)"
            )
        else:
            out.append(char)
    out.append('"')
    return "".join(out)


# --------------------------------------------------------------------------
# Numbers — RFC 8785 §3.2.2.3, i.e. ECMAScript `Number::toString` (ECMA-262
# §6.1.6.1.20) restricted to the values JSON can carry.
# --------------------------------------------------------------------------

_REPR_EXPONENT = re.compile(r"^(-?)(\d)(?:\.(\d+))?e([+-]\d+)$")


def _shortest_digits(value: float) -> tuple[str, int]:
    """Return `(digits, n)` such that `value == 0.digits * 10**n`.

    `repr` on a Python float already yields the shortest decimal string that
    round-trips, which is the same digit string ECMAScript produces; only the
    *formatting* rules differ, and those are applied below.
    """
    text = repr(abs(value))
    match = _REPR_EXPONENT.match(text)
    if match is not None:
        _, lead, rest, exponent = match.groups()
        digits = lead + (rest or "")
        n = int(exponent) + 1
    else:
        if "." in text:
            whole, frac = text.split(".")
        else:
            whole, frac = text, ""
        digits = (whole + frac).lstrip("0")
        if digits == "":
            return "0", 1
        n = len(whole) - (len(whole + frac) - len((whole + frac).lstrip("0")))
    digits = digits.rstrip("0") or "0"
    return digits, n


def serialise_number(value: float | int) -> str:
    """Serialise a JSON number per RFC 8785 §3.2.2.3."""
    if isinstance(value, bool):  # bool is an int subclass in Python
        raise CanonicalisationError("boolean is not a number")
    if isinstance(value, int):
        # RFC 8785 numbers are IEEE-754 doubles, so an integer is widened
        # exactly as a JavaScript reader's parser would widen it. Rejecting
        # integers past 2^53-1 here would be a local variation on RFC 8785
        # (VG-04 §0.3) that no other reader shares; keeping such a field
        # inside the safe range is the schema layer's job, via `IntString`
        # (VG-04 §0.4, `CT-06`).
        try:
            value = float(value)
        except OverflowError as exc:
            raise CanonicalisationError(f"integer {value} is not a double") from exc
    if math.isnan(value) or math.isinf(value):
        raise CanonicalisationError("NaN and Infinity have no JSON form")
    if value == 0.0:
        return "0"  # covers -0.0: ECMAScript renders negative zero as "0"

    sign = "-" if value < 0 else ""
    digits, n = _shortest_digits(value)
    k = len(digits)

    # ECMA-262 §6.1.6.1.20, steps 6-10, with `s` folded into `sign`.
    if k <= n <= 21:
        body = digits + "0" * (n - k)
    elif 0 < n <= 21:
        body = digits[:n] + "." + digits[n:]
    elif -6 < n <= 0:
        body = "0." + "0" * (-n) + digits
    else:
        exponent = n - 1
        mantissa = digits if k == 1 else digits[0] + "." + digits[1:]
        body = f"{mantissa}e{'+' if exponent >= 0 else '-'}{abs(exponent)}"
    return sign + body


# --------------------------------------------------------------------------
# Structure — RFC 8785 §3.2.3.
# --------------------------------------------------------------------------


def utf16_sort_key(key: str) -> tuple[int, ...]:
    """Sort key giving UTF-16 code-unit order (RFC 8785 §3.2.3).

    Exported because every canonical ordering in the domain — object keys
    here, selector members in `selectors/` — must be the same order in both
    readers, and JavaScript's default string sort is UTF-16 code units.
    """
    units = key.encode("utf-16-be", "surrogatepass")
    return tuple(int.from_bytes(units[i:i + 2], "big") for i in range(0, len(units), 2))


def _serialise(value: Any, depth: int) -> str:
    if depth > 128:
        raise CanonicalisationError("nesting deeper than 128 levels")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return serialise_string(value)
    if isinstance(value, (int, float)):
        return serialise_number(value)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_serialise(item, depth + 1) for item in value) + "]"
    if isinstance(value, dict):
        members = []
        for key in sorted(value, key=utf16_sort_key):
            if not isinstance(key, str):
                raise CanonicalisationError("object keys must be strings (CT-12)")
            members.append(serialise_string(key) + ":" + _serialise(value[key], depth + 1))
        return "{" + ",".join(members) + "}"
    raise CanonicalisationError(f"{type(value).__name__} has no JSON form")


def canonicalise(value: Any) -> str:
    """Canonical JSON text for an already-parsed JSON value."""
    return _serialise(value, 0)


def canonical_bytes(value: Any) -> bytes:
    """Canonical UTF-8 bytes — the input to every digest (`SC-2`)."""
    return canonicalise(value).encode("utf-8")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    seen: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise CanonicalisationError(f"duplicate object key {key!r}")
        seen[key] = value
    return seen


def parse_json_text(text: str) -> Any:
    """Parse JSON text, rejecting the forms RFC 8785 cannot canonicalise."""
    try:
        return json.loads(text, object_pairs_hook=_reject_duplicate_keys,
                          parse_constant=_reject_constant)
    except json.JSONDecodeError as exc:
        raise CanonicalisationError(f"invalid JSON: {exc}") from exc


def _reject_constant(name: str) -> Any:
    raise CanonicalisationError(f"{name} is not valid JSON")


def canonicalise_text(text: str) -> str:
    """Parse then canonicalise JSON text in one step."""
    return canonicalise(parse_json_text(text))
