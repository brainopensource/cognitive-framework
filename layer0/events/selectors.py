"""ResourceSelector algebra — Python reader.

Owning contract: VG-04 §5.2 and §5.3.1 / `CT-24`..`CT-28`, `CT-52`, `D-2`;
`schemas/v4/resource-selector.schema.json`; `REQ-SCHEMA-003`.

`includes(parent, child)` is the "resources are a subset" half of attenuation
(VG-04 §5.3). It is **total**: every pair of values, well-formed or not,
returns a decision, and every pair without a defined relation returns denial
with `undefined_relation` (`CT-52`). Nothing is intersected, narrowed or
repaired — `CT-25` exists because a child repeatedly asking for more than its
parent holds is the strongest intrusion signal this shape of system has, and
silent narrowing throws it away.

The relation is a partial order on canonical selectors:

* reflexive     — `includes(x, x)` for every parseable `x`;
* transitive    — `includes(a, b) and includes(b, c) => includes(a, c)`;
* antisymmetric up to canonical equality — `includes(a, b) and includes(b, a)`
  implies `canonicalise(a) == canonicalise(b)`.

The third property is why `canonicalise` prunes: a selector listing both
`/repo` and `/repo/src` and one listing only `/repo` denote the same
authority, so they must reduce to the same bytes or antisymmetry is false for
a reason that has nothing to do with authority.

Semantic rules not expressible in JSON Schema are recorded in
`vanguard/packages/domain/SEMANTICS.md` as ADR candidates.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .canonical import canonicalise, utf16_sort_key

__all__ = [
    "SelectorError",
    "Decision",
    "SELECTOR_KINDS",
    "parse_selector",
    "canonicalise_selector",
    "decide",
    "includes",
]

SELECTOR_KINDS = ("fs", "network", "secret", "git", "table", "browser", "generic")

#: `04 §5.3.1`: "No globs in a grant — expand at issuance."
_GLOB = re.compile(r"[*?\[\]{}]")
_LABEL = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")
_ORIGIN = re.compile(r"^([a-z][a-z0-9+.-]*)://([^/?#]+)$", re.IGNORECASE)
_RANGE = re.compile(r"^(0|[1-9][0-9]*)\.\.(0|[1-9][0-9]*)$")
_DEFAULT_PORTS = {"http": 80, "https": 443, "ws": 80, "wss": 443}


class SelectorError(ValueError):
    """A selector could not be parsed. The caller must fail closed."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


@dataclass(frozen=True, slots=True)
class Decision:
    """The outcome of one inclusion question. Never "unknown" (`CT-52`)."""

    included: bool
    #: `included` · `not_included` · `cross_kind` · `undefined_relation` ·
    #: `unparsable`. Every denial reason maps to
    #: `AuthorizationDenied{scope_escalation}` at the policy boundary.
    reason: str

    def __bool__(self) -> bool:
        return self.included


# --------------------------------------------------------------------------
# Normalisation
# --------------------------------------------------------------------------


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise SelectorError(code, message)


def _require_str(value: Any, field: str) -> str:
    _require(isinstance(value, str), "type", f"{field} must be a string")
    return value


def _normalise_path(raw: Any, field: str = "path") -> str:
    """`D-2`: forward slashes, relative segments collapsed, no trailing slash."""
    text = _require_str(raw, field)
    _require(text != "", "empty", f"{field} must not be empty")
    _require(not _GLOB.search(text), "glob",
             f"{field} contains glob metacharacters; expand at issuance (§5.3.1)")
    text = text.replace("\\", "/")
    absolute = text.startswith("/")
    segments: list[str] = []
    for segment in text.split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            # Collapsing `..` past the start would silently widen the surface,
            # so an unresolvable ascent is a parse failure, not a clamp.
            _require(bool(segments), "traversal", f"{field} escapes its root")
            segments.pop()
            continue
        segments.append(segment)
    joined = "/".join(segments)
    return "/" + joined if absolute else joined


def _normalise_root(raw: Any) -> str:
    """`fs.root` is a `ResourceUri`, compared for equality after one rule: a
    trailing separator is not part of the identity of a root."""
    text = _normalise_uri(raw, "root")
    text = text.replace("\\", "/")
    if len(text) > 1 and text.endswith("/"):
        text = text.rstrip("/") or "/"
    return text


def _normalise_host(raw: Any) -> str:
    """Lowercase, NFC, IDNA A-labels, no trailing root dot (§5.3.1, network)."""
    text = _require_str(raw, "host")
    _require(text != "", "empty", "host must not be empty")
    wildcard = text.startswith("*.")
    body = text[2:] if wildcard else text
    body = unicodedata.normalize("NFC", body).lower().rstrip(".")
    _require(body != "", "empty", "host must have at least one label")
    _require("*" not in body, "wildcard",
             "a wildcard is only allowed as the leading label")
    labels = []
    for label in body.split("."):
        _require(label != "", "label", "empty DNS label")
        if not label.isascii():
            try:
                label = "xn--" + label.encode("punycode").decode("ascii")
            except UnicodeError as exc:  # pragma: no cover - punycode edge
                raise SelectorError("idna", f"label {label!r} is not IDNA-encodable") from exc
        _require(bool(_LABEL.match(label)), "label", f"{label!r} is not a DNS label")
        labels.append(label)
    normalised = ".".join(labels)
    _require(len(normalised) <= 253, "length", "host exceeds 253 characters")
    return ("*." + normalised) if wildcard else normalised


def _normalise_port(raw: Any) -> int:
    _require(isinstance(raw, int) and not isinstance(raw, bool), "type", "port must be an integer")
    _require(1 <= raw <= 65535, "range", f"port {raw} out of range")
    return raw


def _normalise_uri(raw: Any, field: str) -> str:
    text = _require_str(raw, field)
    _require(text != "", "empty", f"{field} must not be empty")
    return text


def _normalise_origin(raw: Any) -> str:
    """Scheme, host and port only — the browser's own trust unit (§5.3.1)."""
    text = _require_str(raw, "origin")
    match = _ORIGIN.match(text)
    _require(match is not None, "origin", f"{text!r} is not a scheme://host[:port] origin")
    assert match is not None
    scheme = match.group(1).lower()
    authority = match.group(2)
    _require("@" not in authority, "origin", "an origin carries no userinfo")
    if authority.startswith("["):
        # IPv6 literal: the brackets are part of the host.
        close = authority.find("]")
        _require(close > 0, "origin", "unterminated IPv6 literal")
        host = authority[: close + 1].lower()
        rest = authority[close + 1:]
    else:
        host, _, port_text = authority.partition(":")
        host = _normalise_host(host)
        _require(not host.startswith("*."), "origin", "a wildcard origin is not an origin")
        rest = f":{port_text}" if port_text else ""
    if rest:
        _require(rest.startswith(":"), "origin", "trailing junk after host")
        port = _normalise_port(int(rest[1:])) if rest[1:].isdigit() else None
        _require(port is not None, "origin", "port must be decimal digits")
        if _DEFAULT_PORTS.get(scheme) == port:
            rest = ""
        else:
            rest = f":{port}"
    return f"{scheme}://{host}{rest}"


def _expand_ref(raw: Any) -> str:
    """Full-ref expansion (§5.3.1, git). Pattern refs are rejected."""
    text = _require_str(raw, "ref")
    _require(text != "", "empty", "ref must not be empty")
    _require(not _GLOB.search(text), "glob", "pattern refs are not grantable (§5.3.1)")
    if text == "HEAD" or text.startswith("refs/"):
        return text
    return f"refs/heads/{text}"


def _parse_range(raw: Any) -> tuple[int, int]:
    """`lo..hi` half-open interval over normalised integer coordinates.

    VG-04 §5.3.1 requires "interval containment on normalised coordinates" but
    does not fix a coordinate grammar. This reader defines exactly one, and
    denies every other spelling rather than guessing (ADR candidate D1-003).
    """
    text = _require_str(raw, "range")
    if text == "*":
        return (0, -1)  # sentinel: the whole table
    match = _RANGE.match(text)
    _require(match is not None, "range",
             f"{text!r} is not `lo..hi` or `*` (ADR candidate D1-003)")
    assert match is not None
    low, high = int(match.group(1)), int(match.group(2))
    _require(low < high, "range", "range must be non-empty and low < high")
    return (low, high)


def _render_range(interval: tuple[int, int]) -> str:
    return "*" if interval[1] == -1 else f"{interval[0]}..{interval[1]}"


def _range_contains(outer: tuple[int, int], inner: tuple[int, int]) -> bool:
    if outer[1] == -1:
        return True
    if inner[1] == -1:
        return False
    return outer[0] <= inner[0] and inner[1] <= outer[1]


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------


def _require_fields(selector: Mapping[str, Any], required: tuple[str, ...],
                    optional: tuple[str, ...] = ()) -> None:
    for field in required:
        _require(field in selector, "required", f"missing required field {field!r}")
    allowed = set(required) | set(optional) | {"kind"}
    for field in selector:
        _require(field in allowed, "additionalProperties", f"unknown field {field!r}")


def _require_array(value: Any, field: str, min_items: int) -> list[Any]:
    _require(isinstance(value, list), "type", f"{field} must be an array")
    _require(len(value) >= min_items, "minItems", f"{field} needs at least {min_items} item(s)")
    return value


def parse_selector(value: Any) -> dict[str, Any]:
    """Parse and normalise one selector. Raises `SelectorError` on anything else.

    The result is the canonical form: normalised, pruned of members another
    member already covers, and ordered. Two selectors denote the same
    authority exactly when their canonical forms are equal.
    """
    _require(isinstance(value, dict), "type", "selector must be an object")
    kind = value.get("kind")
    _require(kind in SELECTOR_KINDS, "kind", f"unknown selector kind {kind!r}")

    if kind == "fs":
        _require_fields(value, ("kind", "root", "paths"))
        root = _normalise_root(value["root"])
        paths = [_normalise_path(path) for path in _require_array(value["paths"], "paths", 1)]
        return {"kind": "fs", "root": root, "paths": _prune_paths(paths)}

    if kind == "network":
        _require_fields(value, ("kind", "hosts", "ports"))
        hosts = [_normalise_host(host) for host in _require_array(value["hosts"], "hosts", 1)]
        ports = [_normalise_port(port) for port in _require_array(value["ports"], "ports", 0)]
        return {"kind": "network", "hosts": _prune_hosts(hosts), "ports": sorted(set(ports))}

    if kind == "secret":
        _require_fields(value, ("kind", "refs", "discloseToModel"))
        _require(value["discloseToModel"] is False, "const",
                 "discloseToModel is the literal false; there is no path that flips it (§5.2)")
        refs = [_require_str(ref, "ref") for ref in _require_array(value["refs"], "refs", 1)]
        for ref in refs:
            _require(ref != "", "empty", "secret ref must not be empty")
        return {"kind": "secret", "refs": sorted(set(refs), key=utf16_sort_key), "discloseToModel": False}

    if kind == "git":
        _require_fields(value, ("kind", "repo", "refs"))
        repo = _normalise_uri(value["repo"], "repo")
        refs = [_expand_ref(ref) for ref in _require_array(value["refs"], "refs", 1)]
        return {"kind": "git", "repo": repo, "refs": sorted(set(refs), key=utf16_sort_key)}

    if kind == "table":
        _require_fields(value, ("kind", "table"), ("ranges",))
        table = _normalise_uri(value["table"], "table")
        # An absent `ranges` denotes the whole table, so it normalises to the
        # explicit whole-table range. Two spellings of one authority must not
        # produce two canonical forms.
        raw_ranges = value["ranges"] if "ranges" in value else ["*"]
        intervals = [_parse_range(item) for item in _require_array(raw_ranges, "ranges", 0)]
        if not intervals:
            intervals = [(0, -1)]
        ranges = [_render_range(item) for item in _prune_ranges(intervals)]
        return {"kind": "table", "table": table, "ranges": ranges}

    if kind == "browser":
        _require_fields(value, ("kind", "origin"), ("accountRef",))
        parsed = {"kind": "browser", "origin": _normalise_origin(value["origin"])}
        if "accountRef" in value:
            parsed["accountRef"] = _require_str(value["accountRef"], "accountRef")
        return parsed

    _require_fields(value, ("kind", "uriPattern"))
    # `04 §5.3.1`: literal equality only. No normalisation is applied, because
    # any normalisation here is an approximation of pattern containment, and
    # an approximation silently widens authority.
    return {"kind": "generic", "uriPattern": _require_str(value["uriPattern"], "uriPattern")}


# --------------------------------------------------------------------------
# Pruning — required for antisymmetry up to canonical equality.
# --------------------------------------------------------------------------


def _path_under(parent: str, child: str) -> bool:
    if parent == child:
        return True
    if parent in ("", "/"):
        return child.startswith(parent)
    return child.startswith(parent + "/")


def _prune_paths(paths: Iterable[str]) -> list[str]:
    unique = sorted(set(paths), key=utf16_sort_key)
    return [p for p in unique if not any(q != p and _path_under(q, p) for q in unique)]


def _host_covers(parent: str, child: str) -> bool:
    """Wildcard containment (§5.3.1, network).

    A parent wildcard contains a child *label*, never another wildcard. Equal
    hosts always contain one another, wildcards included; without that the
    relation would not be reflexive, and `includes(x, x)` must hold for every
    value a grant can carry.
    """
    if parent == child:
        return True
    if not parent.startswith("*."):
        return False
    if child.startswith("*."):
        return False
    suffix = parent[2:]
    if not child.endswith("." + suffix):
        return False
    label = child[: -(len(suffix) + 1)]
    return label != "" and "." not in label


def _prune_hosts(hosts: Iterable[str]) -> list[str]:
    unique = sorted(set(hosts), key=utf16_sort_key)
    return [h for h in unique if not any(g != h and _host_covers(g, h) for g in unique)]


def _prune_ranges(intervals: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    unique = sorted(set(intervals))
    return [i for i in unique
            if not any(j != i and _range_contains(j, i) for j in unique)]


def canonicalise_selector(value: Any) -> str:
    """Canonical RFC 8785 bytes of a selector, as text (`SC-2`)."""
    return canonicalise(parse_selector(value))


# --------------------------------------------------------------------------
# The relation
# --------------------------------------------------------------------------


def _includes_parsed(parent: Mapping[str, Any], child: Mapping[str, Any]) -> Decision:
    kind = parent["kind"]
    if kind != child["kind"]:
        # `CT-52`: any cross-kind comparison is denied, never intersected.
        return Decision(False, "cross_kind")

    if kind == "fs":
        if parent["root"] != child["root"]:
            return Decision(False, "not_included")
        ok = all(any(_path_under(p, c) for p in parent["paths"]) for c in child["paths"])
        return Decision(ok, "included" if ok else "not_included")

    if kind == "network":
        hosts_ok = all(any(_host_covers(p, c) for p in parent["hosts"]) for c in child["hosts"])
        ports_ok = set(child["ports"]).issubset(set(parent["ports"]))
        ok = hosts_ok and ports_ok
        return Decision(ok, "included" if ok else "not_included")

    if kind == "secret":
        ok = set(child["refs"]).issubset(set(parent["refs"]))
        return Decision(ok, "included" if ok else "not_included")

    if kind == "git":
        ok = parent["repo"] == child["repo"] and set(child["refs"]).issubset(set(parent["refs"]))
        return Decision(ok, "included" if ok else "not_included")

    if kind == "table":
        if parent["table"] != child["table"]:
            return Decision(False, "not_included")
        parents = [_parse_range(r) for r in parent["ranges"]]
        children = [_parse_range(r) for r in child["ranges"]]
        ok = all(any(_range_contains(p, c) for p in parents) for c in children)
        return Decision(ok, "included" if ok else "not_included")

    if kind == "browser":
        if parent["origin"] != child["origin"]:
            # Exact origin equality. No subdomain or path containment: origin
            # is the browser's own trust unit (§5.3.1).
            return Decision(False, "not_included")
        if "accountRef" not in parent:
            return Decision(True, "included")
        ok = child.get("accountRef") == parent["accountRef"]
        return Decision(ok, "included" if ok else "not_included")

    ok = parent["uriPattern"] == child["uriPattern"]
    return Decision(ok, "included" if ok else "not_included")


def decide(parent: Any, child: Any) -> Decision:
    """Total inclusion decision for any two values (`CT-52`).

    Returns `Decision(True, "included")` only when `child` is provably a
    subset of `parent`. Anything unparseable, cross-kind or without a defined
    relation is denied; a caller that sees a denial emits
    `AuthorizationDenied{scope_escalation}` recording both what was requested
    and what was grantable (`CT-24`).
    """
    try:
        parsed_parent = parse_selector(parent)
        parsed_child = parse_selector(child)
    except SelectorError:
        return Decision(False, "unparsable")
    return _includes_parsed(parsed_parent, parsed_child)


def includes(parent: Any, child: Any) -> bool:
    """`child ⊆ parent`. False on every undefined pair (`CT-52`)."""
    return decide(parent, child).included
