"""Independence and disjointness algebra for ResourceSelectors (M-7 / ADR-0083).

Pure algebraic domain operations to partition concurrent candidate actions into
independent non-conflicting groups without violating sequential execution invariant I-11.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

from .resource_selector import SelectorError, parse_selector


def _fs_paths_overlap(p1: str, p2: str) -> bool:
    """Check if two filesystem paths have a hierarchical or equality overlap."""
    n1 = p1.rstrip("/")
    n2 = p2.rstrip("/")
    if n1 == n2:
        return True
    if n1.startswith(n2 + "/"):
        return True
    if n2.startswith(n1 + "/"):
        return True
    return False


def _disjoint_parsed(s1: Mapping[str, Any], s2: Mapping[str, Any]) -> bool:
    kind1 = s1.get("kind")
    kind2 = s2.get("kind")

    # Cross-kind resources operate on disjoint subsystems
    if kind1 != kind2:
        return True

    if kind1 == "fs":
        root1 = s1.get("root", "")
        root2 = s2.get("root", "")
        if not _fs_paths_overlap(root1, root2):
            return True
        paths1 = s1.get("paths", [root1])
        paths2 = s2.get("paths", [root2])
        for p1 in paths1:
            for p2 in paths2:
                if _fs_paths_overlap(p1, p2):
                    return False
        return True

    if kind1 == "network":
        hosts1 = set(s1.get("hosts", ()))
        hosts2 = set(s2.get("hosts", ()))
        if hosts1.isdisjoint(hosts2):
            return True
        ports1 = set(s1.get("ports", ()))
        ports2 = set(s2.get("ports", ()))
        if ports1 and ports2 and ports1.isdisjoint(ports2):
            return True
        return False

    if kind1 == "secret":
        refs1 = set(s1.get("refs", ()))
        refs2 = set(s2.get("refs", ()))
        return refs1.isdisjoint(refs2)

    if kind1 == "git":
        if s1.get("repo") != s2.get("repo"):
            return True
        refs1 = set(s1.get("refs", ()))
        refs2 = set(s2.get("refs", ()))
        return refs1.isdisjoint(refs2)

    if kind1 == "table":
        if s1.get("table") != s2.get("table"):
            return True
        return False

    if kind1 == "browser":
        if s1.get("origin") != s2.get("origin"):
            return True
        acc1 = s1.get("accountRef")
        acc2 = s2.get("accountRef")
        if acc1 and acc2 and acc1 != acc2:
            return True
        return False

    if kind1 == "generic":
        return s1.get("uriPattern") != s2.get("uriPattern")

    return False


def disjoint(s1: Any, s2: Any) -> bool:
    """Determine if two ResourceSelectors are mutually disjoint (conflict-free).
    
    Total: returns False on unparseable or invalid inputs (fail-closed).
    """
    try:
        parsed1 = parse_selector(s1)
        parsed2 = parse_selector(s2)
    except (SelectorError, TypeError, ValueError):
        return False
    return _disjoint_parsed(parsed1, parsed2)


def are_independent(selectors_a: Iterable[Any], selectors_b: Iterable[Any]) -> bool:
    """Determine whether two sets of ResourceSelectors are pairwise independent."""
    list_a = tuple(selectors_a)
    list_b = tuple(selectors_b)
    for a in list_a:
        for b in list_b:
            if not disjoint(a, b):
                return False
    return True


def compute_independence_groups(
    requests: Sequence[Mapping[str, Any] | Any],
) -> tuple[tuple[int, ...], ...]:
    """Partition a list of requests into maximal independent (non-conflicting) groups.
    
    Returns tuple of index tuples representing parallelizable waves under M-7.
    """
    if not requests:
        return ()

    def _get_resource(req: Any) -> Any:
        if hasattr(req, "resource"):
            return getattr(req, "resource")
        if isinstance(req, Mapping):
            return req.get("resource") or req.get("selector")
        return req

    n = len(requests)
    adj: dict[int, set[int]] = {i: set() for i in range(n)}
    for i in range(n):
        res_i = _get_resource(requests[i])
        for j in range(i + 1, n):
            res_j = _get_resource(requests[j])
            if not disjoint(res_i, res_j):
                adj[i].add(j)
                adj[j].add(i)

    unassigned = set(range(n))
    waves: list[tuple[int, ...]] = []
    while unassigned:
        current_wave: list[int] = []
        for candidate in sorted(unassigned):
            if all(candidate not in adj[assigned] for assigned in current_wave):
                current_wave.append(candidate)
        for c in current_wave:
            unassigned.remove(c)
        waves.append(tuple(current_wave))

    return tuple(waves)
