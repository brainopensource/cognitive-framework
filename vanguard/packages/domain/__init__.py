"""Pure values and reducers. No project imports, no I/O (ICD §2, `domain`)."""

from .canonicalisation.digest import digest_bytes, digest_of
from .canonicalisation.jcs import (
    CanonicalisationError,
    canonical_bytes,
    canonicalise,
    canonicalise_text,
    parse_json_text,
)
from .primitives.primitives import PRIMITIVE_KINDS, ParseError, Primitive, parse, unparse
from .selectors.resource_selector import (
    SELECTOR_KINDS,
    Decision,
    SelectorError,
    canonicalise_selector,
    decide,
    includes,
    parse_selector,
)

__all__ = [
    "CanonicalisationError", "canonicalise", "canonicalise_text", "canonical_bytes",
    "parse_json_text", "digest_bytes", "digest_of",
    "PRIMITIVE_KINDS", "ParseError", "Primitive", "parse", "unparse",
    "SELECTOR_KINDS", "Decision", "SelectorError", "canonicalise_selector",
    "decide", "includes", "parse_selector",
]
