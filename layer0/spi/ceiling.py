"""Plugin-cell capability ceiling. Independent of the kernel grant tree (A-2)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = ["ceiling_allows"]

_HOST_METHODS = frozenset({"execute", "health", "compensate", "verbs", "quiesce", "init"})


def ceiling_allows(
    method: str,
    params: Mapping[str, Any] | None,
    capabilities: Sequence[Mapping[str, Any]],
) -> bool:
    if method not in _HOST_METHODS:
        return False
    if method != "execute":
        return True
    if not capabilities:
        return True
    payload = dict(params or {})
    verb = str(payload.get("verb", ""))
    selector = payload.get("selector")
    if not isinstance(selector, Mapping):
        selector = {}
    for item in capabilities:
        if str(item.get("verb")) != verb:
            continue
        parent = item.get("selector")
        if not isinstance(parent, Mapping):
            parent = {}
        if _selector_subset(selector, parent):
            return True
    return False


def _selector_subset(child: Mapping[str, Any], parent: Mapping[str, Any]) -> bool:
    child_kind = str(child.get("kind", ""))
    parent_kind = str(parent.get("kind", ""))
    if parent_kind and child_kind != parent_kind:
        return False
    if parent_kind == "fs" or child_kind == "fs":
        parent_root = str(parent.get("root", "")).rstrip("/")
        child_root = str(child.get("root", "")).rstrip("/")
        if not parent_root:
            return True
        if not child_root:
            return False
        return child_root == parent_root or child_root.startswith(parent_root + "/")
    for key, value in parent.items():
        if child.get(key) != value:
            return False
    return True
