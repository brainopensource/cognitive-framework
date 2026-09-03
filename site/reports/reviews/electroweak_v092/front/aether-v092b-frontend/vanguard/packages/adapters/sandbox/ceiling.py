"""Plugin-cell host ceiling. Delegates inclusion to the domain algebra (2.1-D).

The SPI signature is `(method, params, capabilities)` so toolkit and broker
call sites stay drop-in. Inclusion itself is `domain.selectors.ceiling_allows`
/ `decide` — there is no second subset walk here (F-16).
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ...domain.selectors.resource_selector import ceiling_allows as domain_ceiling_allows

__all__ = ["ceiling_allows"]

_HOST_METHODS = frozenset({"execute", "health", "compensate", "verbs", "quiesce", "init"})


def ceiling_allows(
    method: str,
    params: Mapping[str, Any] | None,
    capabilities: Sequence[Mapping[str, Any]],
) -> bool:
    """Fail-closed host gate. Empty capabilities authorize no `execute`."""
    if method not in _HOST_METHODS:
        return False
    if method != "execute":
        return True
    payload = dict(params or {})
    verb = str(payload.get("verb", ""))
    requested = payload.get("selector")
    matching: list[Any] = []
    for item in capabilities:
        if str(item.get("verb")) != verb:
            continue
        matching.append(item.get("selector"))
    return domain_ceiling_allows(matching, requested).included
