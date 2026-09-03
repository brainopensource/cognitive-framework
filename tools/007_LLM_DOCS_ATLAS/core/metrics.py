"""Structural metrics for LDA (``lda metrics``).

Deterministic aggregate queries over the fact graph: fan-in/fan-out hubs,
module-level import cycles, largest files by symbol count, and documentation
coverage. Read-only; derives everything from existing relations.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, List, Set

MAX_CYCLES = 20


def _module_of(path: str) -> str:
    """Coarse module key: directory path (stable across file renames)."""
    parts = (path or "").replace("\\", "/").split("/")
    return "/".join(parts[:-1]) if len(parts) > 1 else (parts[0] if parts else "")


def _find_cycles(graph: Dict[str, Set[str]]) -> List[List[str]]:
    """Deterministic cycle enumeration (DFS with sorted iteration)."""
    cycles: List[List[str]] = []
    seen: Set[frozenset] = set()

    def dfs(start: str) -> None:
        if len(cycles) >= MAX_CYCLES:
            return
        stack: List[str] = []
        on_stack: Set[str] = set()
        visited: Set[str] = set()

        def walk(node: str) -> None:
            if len(cycles) >= MAX_CYCLES:
                return
            stack.append(node)
            on_stack.add(node)
            visited.add(node)
            for nxt in sorted(graph.get(node, ())):
                if nxt == start:
                    cycle = stack[:]
                    key = frozenset(cycle)
                    if key not in seen:
                        seen.add(key)
                        cycles.append(cycle)
                elif nxt not in visited:
                    walk(nxt)
            stack.pop()
            on_stack.discard(node)

        walk(start)

    for start in sorted(graph):
        dfs(start)
    return cycles


def compute_metrics(storage: Any, top_n: int = 10) -> Dict[str, Any]:
    """Aggregate structural metrics from the fact graph."""
    con = storage.get_connection()

    fan_in: Counter = Counter()
    fan_out: Counter = Counter()
    names: Dict[str, str] = {}
    module_imports: Dict[str, Set[str]] = defaultdict(set)
    file_symbols: Counter = Counter()

    for row in con.execute("SELECT id, name, file_path FROM symbols"):
        names[row["id"]] = f"{row['file_path']}#{row['name']}"
        file_symbols[row["file_path"]] += 1

    relation_total = 0
    for row in con.execute("SELECT source_id, target_id, kind FROM relations"):
        src, tgt, kind = row["source_id"], row["target_id"], row["kind"]
        relation_total += 1
        fan_out[src] += 1
        fan_in[tgt] += 1
        if kind == "imports":
            sm, tm = _module_of(names.get(src, src)), _module_of(names.get(tgt, tgt))
            if sm and tm and sm != tm:
                module_imports[sm].add(tm)

    top_fan_in = [
        {"symbol": names.get(sid, sid), "fan_in": n} for sid, n in fan_in.most_common(top_n)
    ]
    top_fan_out = [
        {"symbol": names.get(sid, sid), "fan_out": n} for sid, n in fan_out.most_common(top_n)
    ]
    cycles = _find_cycles(dict(module_imports))
    hub_files = [{"file": f, "symbols": n} for f, n in file_symbols.most_common(top_n)]

    total_symbols = len(names)
    documented = con.execute(
        "SELECT COUNT(*) AS n FROM symbols WHERE docstring IS NOT NULL AND docstring != ''"
    ).fetchone()[0]

    return {
        "totals": {
            "symbols": total_symbols,
            "relations": relation_total,
            "documented_symbols": documented,
            "documentation_ratio": round(documented / total_symbols, 3) if total_symbols else 0.0,
        },
        "top_fan_in": top_fan_in,
        "top_fan_out": top_fan_out,
        "hub_files": hub_files,
        "import_cycles": [
            {"modules": sorted(set(c)), "length": len(set(c))} for c in cycles
        ],
        "import_cycle_count": len(cycles),
    }


__all__ = ["compute_metrics"]
