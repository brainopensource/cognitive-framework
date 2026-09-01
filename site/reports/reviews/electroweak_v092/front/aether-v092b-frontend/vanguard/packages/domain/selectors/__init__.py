"""ResourceSelector algebra (VG-04 §5.2, §5.3.1)."""

from .resource_selector import (
    SELECTOR_KINDS,
    Decision,
    SelectorError,
    canonicalise_selector,
    ceiling_allows,
    decide,
    includes,
    intersect_ceilings,
    parse_selector,
)
from .independence import (
    are_independent,
    compute_independence_groups,
    disjoint,
)

__all__ = [
    "SELECTOR_KINDS",
    "Decision",
    "SelectorError",
    "canonicalise_selector",
    "ceiling_allows",
    "decide",
    "includes",
    "intersect_ceilings",
    "parse_selector",
    "are_independent",
    "compute_independence_groups",
    "disjoint",
]
