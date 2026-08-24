"""Authored ``mhf.manifest/2`` fixtures for the M-3C canonical-path falsifiers.

RF-78 and RF-79 probe the *public* composition boundary, so their fixtures are
real pack directories on disk rather than in-memory dicts: the defect under
test is that `Runtime.compose` cannot reach an authored `/2` pack at all, and a
fixture that bypassed the loader would hide exactly that.

Each builder writes a pack whose declared facts mirror a shipped legacy pack,
so RF-79 can compare the two ingress routes fact-for-fact.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

#: `vg-code-default` capability rows, as the legacy pack declares them.
CODE_CAPABILITIES: tuple[Mapping[str, Any], ...] = (
    {"verb": "fs.read", "sink": "observation", "risk": "low",
     "selector": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}},
    {"verb": "fs.search", "sink": "observation", "risk": "low",
     "selector": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}},
    {"verb": "patch.apply", "sink": "privileged", "risk": "medium",
     "selector": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}},
    {"verb": "proc.exec", "sink": "privileged", "risk": "high",
     "selector": {"kind": "generic",
                  "uriPattern": "proc://exec/allow/git,pytest,ruff,python3"}},
)

#: `vg-table-default` capability rows. The second domain exists to prove the
#: path is not coding-specific, so its verbs deliberately have no row in the
#: global `DEFAULT_BINDINGS` table (ADR-0088 Decision 1.7).
TABLE_CAPABILITIES: tuple[Mapping[str, Any], ...] = (
    {"verb": "table.read", "sink": "observation", "risk": "low",
     "selector": {"kind": "generic", "uriPattern": "table://read/*"}},
    {"verb": "table.patch", "sink": "privileged", "risk": "medium",
     "selector": {"kind": "generic", "uriPattern": "table://patch/*"}},
)

_BUDGET_POLICY = {"usdMicros": 1_000_000, "tokens": 200_000, "effects": 8}


def _component(kind: str, ref: str, *, interfaces: tuple[str, ...],
               ceiling: tuple[Mapping[str, Any], ...],
               config: str | Mapping[str, Any] = "config.json",
               isolation: str = "in_process") -> Mapping[str, Any]:
    return {
        "kind": kind,
        "ref": ref,
        "config": config,
        "ceiling": list(ceiling),
        "isolation": isolation,
        "interfaces": list(interfaces),
    }


def authored_v2(pack_id: str, capabilities: tuple[Mapping[str, Any], ...], *,
                oracle: str, system_prompt: str) -> Mapping[str, Any]:
    """One authored `/2` manifest declaring `pack_id`'s behaviour-affecting facts."""
    ceiling = tuple(row["selector"] for row in capabilities)
    return {
        "api": "mhf.manifest/2",
        "id": pack_id,
        "components": {
            "toolkit": _component("IToolkit", "toolkit.py",
                                  interfaces=("IToolkit",), ceiling=ceiling),
            "planner": _component("IPlanner", "planner.py",
                                  interfaces=("IPlanner",), ceiling=ceiling),
            "context": _component("IContextManager", "context-policy.json",
                                  interfaces=("IContextManager",), ceiling=ceiling),
        },
        "bindings": [
            {"from": "planner", "to": "toolkit", "interface": "IToolkit"},
            {"from": "planner", "to": "context", "interface": "IContextManager"},
        ],
        "entrypoints": {"IPlanner": {"component": "planner", "interface": "IPlanner"}},
        "ceiling": list(ceiling),
        "capabilities": [{"verb": row["verb"], "selector": row["selector"],
                          "sink": row["sink"], "risk": row["risk"]}
                         for row in capabilities],
        "budget": dict(_BUDGET_POLICY),
        "system_prompt": system_prompt,
        "evaluation": {"mode": "exterior", "oracle": oracle},
        "undeletable": False,
    }


def write_pack(base: Path, pack_id: str, manifest: Mapping[str, Any]) -> Path:
    """Materialise one pack directory and return it.

    Component files carry stable bytes: RF-78 asserts that a *changed* component
    moves `D_H`, which is only meaningful if the unchanged case is fixed.
    """
    pack = base / pack_id
    pack.mkdir(parents=True, exist_ok=True)
    (pack / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (pack / "toolkit.py").write_text("def call(verb, payload):\n    return payload\n",
                                     encoding="utf-8")
    (pack / "planner.py").write_text("def plan(state):\n    return state\n", encoding="utf-8")
    (pack / "context-policy.json").write_text(json.dumps({"maxTokens": 8000}), encoding="utf-8")
    (pack / "config.json").write_text(json.dumps({}), encoding="utf-8")
    (pack / "system-prompt.txt").write_text("You are a bounded agent.\n", encoding="utf-8")
    (pack / "budget-policy.json").write_text(json.dumps(_BUDGET_POLICY), encoding="utf-8")
    return pack


def code_pack(base: Path, pack_id: str = "rf-code-v2") -> Path:
    return write_pack(base, pack_id, authored_v2(
        pack_id, CODE_CAPABILITIES,
        oracle="coding-oracle@3", system_prompt="system-prompt.txt"))


def table_pack(base: Path, pack_id: str = "rf-table-v2") -> Path:
    return write_pack(base, pack_id, authored_v2(
        pack_id, TABLE_CAPABILITIES,
        oracle="tableworld-evaluator@1", system_prompt="system-prompt.txt"))


#: The component files both dialects name, so the twin pair differs only in
#: dialect and never in the bytes it points at. RF-79's `D_H` convergence claim
#: is only meaningful against identical underlying facts.
_TWIN_FILES: Mapping[str, str] = {
    "system-prompt.txt": "You are a bounded agent.\n",
    "context-policy.json": json.dumps({"maxTokens": 8000}),
    "toolkit.json": json.dumps({"name": "toolkit", "verb": "fs.read"}),
    "budget-policy.json": json.dumps(_BUDGET_POLICY),
}

#: legacy role -> authored `/2` component name and interface.
_TWIN_ROLES: Mapping[str, tuple[str, str, str]] = {
    "system_prompt": ("system_prompt", "system-prompt.txt", "IContextManager"),
    "context_policy": ("context_policy", "context-policy.json", "IContextManager"),
    "tools": ("tools", "toolkit.json", "IToolkit"),
}


def _write_twin_files(pack: Path) -> None:
    pack.mkdir(parents=True, exist_ok=True)
    for name, body in _TWIN_FILES.items():
        (pack / name).write_text(body, encoding="utf-8")


def legacy_twin(base: Path, pack_id: str = "rf-legacy-twin") -> Path:
    """A supported `mhf.harness/1` pack, written as the shipped packs are."""
    pack = base / pack_id
    _write_twin_files(pack)
    manifest = {
        "harness": pack_id,
        "components": {role: [f"{pack_id}/{filename}"]
                       for role, (_, filename, _) in _TWIN_ROLES.items()},
        "capabilities": [dict(row) for row in CODE_CAPABILITIES],
        "evaluators": ["coding-oracle@3"],
        "budgetPolicy": f"{pack_id}/budget-policy.json",
        "undeletable": False,
    }
    (pack / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return pack


def authored_twin(base: Path, pack_id: str = "rf-authored-twin") -> Path:
    """The authored `/2` statement of exactly the facts `legacy_twin` declares."""
    pack = base / pack_id
    _write_twin_files(pack)
    ceiling = tuple(row["selector"] for row in CODE_CAPABILITIES)
    manifest = {
        "api": "mhf.manifest/2",
        "id": pack_id,
        "components": {
            name: _component(interface, f"{pack_id}/{filename}",
                             interfaces=(interface,), ceiling=ceiling,
                             config=f"{pack_id}/{filename}")
            for name, filename, interface in _TWIN_ROLES.values()
        },
        "bindings": [],
        "entrypoints": {"IToolkit": {"component": "tools", "interface": "IToolkit"}},
        "ceiling": list(ceiling),
        "capabilities": [{"verb": row["verb"], "selector": row["selector"],
                          "sink": row["sink"], "risk": row["risk"]}
                         for row in CODE_CAPABILITIES],
        "budget": dict(_BUDGET_POLICY),
        "system_prompt": f"{pack_id}/system-prompt.txt",
        "evaluation": {"mode": "exterior", "oracle": "coding-oracle@3"},
        "undeletable": False,
    }
    (pack / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return pack


#: Facts both ingress routes must agree on after normalization, independent of
#: which dialect stated them.
TWIN_FACTS: Mapping[str, Any] = {
    "capabilities": tuple(sorted(
        (row["verb"], row["sink"], row["risk"]) for row in CODE_CAPABILITIES)),
    "evaluators": ("coding-oracle@3",),
}


def canonical_composition_type() -> type | None:
    """The one canonical composition value, or `None` while it does not exist.

    Returned rather than imported at module scope so the falsifier reports the
    *architectural* absence as a named red line instead of an import error.
    """
    try:  # pragma: no cover - exercised by whichever branch is live
        from vanguard.packages.domain.artifacts.manifest import (  # type: ignore[attr-defined]
            FrozenComposition,
        )
    except ImportError:
        return None
    return FrozenComposition
