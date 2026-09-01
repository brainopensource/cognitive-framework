"""Opaque, boundary-parsed primitives — Python reader.

Owning contract: VG-04 §1 / `CT-03`, `CT-06`..`CT-10`, `CT-14`..`CT-16`;
`schemas/v4/primitives.schema.json`; `REQ-SCHEMA-002`.

A value acquires its type by being parsed (`CT-03`). There is no cast: the
constructors below are the only way to obtain a primitive, and each carries
its kind, so passing a `GrantId` where an `EpisodeId` is expected raises
instead of reaching a policy check.

Two rules are stricter than the JSON Schema pattern can express and are
therefore marked `semantic` in the vector set rather than being folded into
the schema (see `SEMANTICS.md`, ADR candidates D1-001 and D1-002):

* `Timestamp` must denote a real UTC instant, not merely match the shape.
* `Uuidv7` must carry version 7 and an RFC 4122 variant, which the pattern
  does encode, but the check is repeated here so a reader that skipped
  schema validation still fails closed.
"""

from __future__ import annotations

import random
import re
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping

__all__ = [
    "ParseError",
    "Primitive",
    "PRIMITIVE_KINDS",
    "parse",
    "unparse",
    "parse_digest",
    "parse_timestamp",
    "parse_principal_id",
    "parse_episode_id",
    "int_string_to_int",
    "int_string_from_int",
    "parse_mapping",
    "uuidv7",
]


class ParseError(ValueError):
    """A boundary value failed to parse. Never repaired, never coerced."""

    def __init__(self, kind: str, code: str, message: str) -> None:
        super().__init__(f"{kind}: {message}")
        self.kind = kind
        self.code = code


@dataclass(frozen=True, slots=True)
class Primitive:
    """An opaque parsed value. `kind` is carried, so kinds never interchange."""

    kind: str
    value: Any

    def __str__(self) -> str:  # pragma: no cover - debugging aid only
        return f"{self.kind}({self.value!r})"


# --------------------------------------------------------------------------
# Declarative kind table. Both readers are driven by the same table shape so
# that "every primitive" in the vector set is enumerable rather than a list
# someone has to remember to extend.
# --------------------------------------------------------------------------

_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_INT_STRING = re.compile(r"^(0|[1-9][0-9]*)$")
_UUIDV7 = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

_DAYS_IN_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def _is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _check_timestamp(kind: str, text: str) -> None:
    if not _TIMESTAMP.match(text):
        raise ParseError(kind, "pattern", f"not RFC 3339 UTC millisecond form: {text!r}")
    year, month, day = int(text[0:4]), int(text[5:7]), int(text[8:10])
    hour, minute, second = int(text[11:13]), int(text[14:16]), int(text[17:19])
    if not 1 <= month <= 12:
        raise ParseError(kind, "semantic", f"month {month} out of range")
    limit = _DAYS_IN_MONTH[month - 1] + (1 if month == 2 and _is_leap(year) else 0)
    if not 1 <= day <= limit:
        raise ParseError(kind, "semantic", f"day {day} out of range for month {month}")
    if hour > 23 or minute > 59:
        raise ParseError(kind, "semantic", f"time {hour:02d}:{minute:02d} out of range")
    if second > 59:
        # RFC 3339 permits :60 for a leap second; `CT-08` wants one unambiguous
        # ordering across languages, and a value no arithmetic library agrees
        # on is not that. Denied rather than truncated.
        raise ParseError(kind, "semantic", f"second {second} out of range (no leap seconds)")


def _string_checker(
    *, pattern: re.Pattern[str] | None = None,
    min_length: int = 0, max_length: int | None = None,
    enum: tuple[str, ...] | None = None, const: str | None = None,
) -> Callable[[str, Any], str]:
    """Build a checker whose failure codes are the schema keywords themselves.

    The order matters: a closed value set is checked before the type, because
    that is the keyword the normative schema would report for a wrongly typed
    instance of a `const` or `enum` definition.
    """

    def check(kind_name: str, value: Any) -> str:
        if const is not None and value != const:
            raise ParseError(kind_name, "const", f"{value!r} is not {const!r}")
        if enum is not None and value not in enum:
            raise ParseError(kind_name, "enum", f"{value!r} is not one of {enum}")
        if not isinstance(value, str):
            raise ParseError(kind_name, "type", f"expected string, got {type(value).__name__}")
        if len(value) < min_length:
            raise ParseError(kind_name, "minLength", "value is shorter than the minimum")
        if max_length is not None and len(value) > max_length:
            raise ParseError(kind_name, "maxLength", "value is longer than the maximum")
        if pattern is not None and not pattern.match(value):
            raise ParseError(kind_name, "pattern", f"{value!r} does not match {pattern.pattern}")
        return value

    return check


def _integer_checker(minimum: int) -> Callable[[str, Any], int]:
    def check(kind_name: str, value: Any) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ParseError(kind_name, "type", f"expected integer, got {type(value).__name__}")
        if value < minimum:
            raise ParseError(kind_name, "minimum", f"{value} is below {minimum}")
        if abs(value) > 2**53 - 1:
            raise ParseError(kind_name, "range", "beyond 2^53-1; use IntString (VG-04 §0.4)")
        return value

    return check


def _timestamp_checker(kind_name: str, value: Any) -> str:
    if not isinstance(value, str):
        raise ParseError(kind_name, "type", f"expected string, got {type(value).__name__}")
    _check_timestamp(kind_name, value)
    return value


_IDENTIFIER = _string_checker(min_length=1, max_length=128)

_ID_KINDS = (
    "RunId", "EpisodeId", "ProcessId", "TaskId", "ArtifactId", "ClaimId",
    "GrantId", "LeaseId", "ApprovalId", "CandidateId", "PrincipalId",
    "TenantId", "OwnerId", "EvaluatorId", "ToolCallId", "Identifier",
)

_CHECKERS: dict[str, Callable[[str, Any], Any]] = {
    "SchemaVersion": _string_checker(const="vg.4"),
    "Timestamp": _timestamp_checker,
    "Digest": _string_checker(pattern=_DIGEST),
    "IntString": _string_checker(pattern=_INT_STRING),
    "UsdMicros": _string_checker(pattern=_INT_STRING),
    "Millis": _integer_checker(0),
    "BranchId": _integer_checker(0),
    "Uuidv7": _string_checker(pattern=_UUIDV7),
    "ResourceUri": _string_checker(min_length=1),
    "RiskTier": _string_checker(enum=("low", "medium", "high", "critical")),
    "ConfidentialityLabel": _string_checker(
        enum=("public", "internal", "confidential", "restricted")),
    "RetentionClass": _string_checker(
        enum=("ephemeral", "standard", "extended", "legal_hold")),
    "TrainabilityLabel": _string_checker(
        enum=("prohibited", "opt_in_required", "opt_in_granted")),
    "RedactionStatus": _string_checker(
        enum=("none", "partial", "complete", "pending")),
    "EpistemicState": _string_checker(enum=(
        "observed", "derived", "hypothesised", "corroborated", "contradicted", "retracted")),
}
for _id_kind in _ID_KINDS:
    _CHECKERS[_id_kind] = _IDENTIFIER

#: Every primitive kind this reader parses. The vector suite iterates it, so a
#: new kind without vectors fails the coverage assertion rather than passing
#: unnoticed.
PRIMITIVE_KINDS: tuple[str, ...] = tuple(sorted(_CHECKERS))


def parse(kind: str, value: Any) -> Primitive:
    """Parse an external value into an opaque primitive of `kind`."""
    checker = _CHECKERS.get(kind)
    if checker is None:
        raise ParseError(kind, "unknown_kind", "no such primitive kind")
    return Primitive(kind, checker(kind, value))


def unparse(primitive: Primitive) -> Any:
    """Return the wire form. `unparse(parse(k, x)) == x` for every valid `x`."""
    if not isinstance(primitive, Primitive):
        raise ParseError("?", "type", "not a parsed primitive")
    return primitive.value


def parse_digest(value: Any) -> Primitive:
    """`CT-09`."""
    return parse("Digest", value)


def parse_timestamp(value: Any) -> Primitive:
    """`CT-08`."""
    return parse("Timestamp", value)


def parse_principal_id(value: Any) -> Primitive:
    """`CT-16`."""
    return parse("PrincipalId", value)


def parse_episode_id(value: Any) -> Primitive:
    return parse("EpisodeId", value)


def int_string_to_int(primitive: Primitive) -> int:
    """Widen an `IntString` to an exact integer (`CT-06`, VG-04 §0.4)."""
    if primitive.kind not in {"IntString", "UsdMicros"}:
        raise ParseError(primitive.kind, "kind", "not an IntString-shaped primitive")
    return int(primitive.value)


def int_string_from_int(kind: str, value: int) -> Primitive:
    """Narrow an exact non-negative integer to its wire form."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ParseError(kind, "type", "expected integer")
    if value < 0:
        raise ParseError(kind, "minimum", "IntString is non-negative")
    return parse(kind, str(value))


def parse_mapping(kinds: Mapping[str, str], record: Mapping[str, Any]) -> dict[str, Primitive]:
    """Parse a whole record of primitives, failing on the first bad field."""
    return {field: parse(kind, record[field]) for field, kind in kinds.items()}


def uuidv7(timestamp_ms: int | None = None) -> str:
    """Generate an RFC 9562 UUIDv7 string with 48-bit timestamp."""
    millis = timestamp_ms if timestamp_ms is not None else int(time.time() * 1000)
    rand_a = random.getrandbits(12)
    rand_b = random.getrandbits(62)
    val = (millis << 80) | (0x7 << 76) | (rand_a << 64) | (0x2 << 62) | rand_b
    hex_str = f"{val:032x}"
    return f"{hex_str[:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:]}"

