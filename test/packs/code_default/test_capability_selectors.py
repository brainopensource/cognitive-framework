"""Pack/plugin capabilities must parse under the one domain selector algebra."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from simple_yaml import load  # noqa: E402

from vanguard.packages.adapters.sandbox.ceiling import ceiling_allows as host_ceiling_allows
from vanguard.packages.domain.selectors.resource_selector import (
    ceiling_allows,
    parse_selector,
)

PACK = ROOT / "packs" / "code-default"
_FS = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}
_FS_CHILD = {"kind": "fs", "root": "/workspace", "paths": ["/workspace/src/app.py"]}
_FS_ETC = {"kind": "fs", "root": "/etc", "paths": ["/etc"]}
_PROC = {"kind": "generic", "uriPattern": "proc://exec/allow/git,pytest,ruff,python3"}
_PROC_OTHER = {"kind": "generic", "uriPattern": "proc://exec/allow/id"}
_PLUGIN_FILES = (
    "plugins/fs.yaml",
    "plugins/ast-patch.yaml",
    "plugins/index.yaml",
    "plugins/terminal.yaml",
    "harness.yaml",
)


def _selectors(path: Path) -> list[dict]:
    data = load(path.read_text(encoding="utf-8"))
    caps = data.get("capabilities") or []
    return [item["selector"] for item in caps if isinstance(item, dict) and "selector" in item]


class PackCapabilitySelectorTests(unittest.TestCase):
    def test_declared_selectors_parse(self) -> None:
        for relative in _PLUGIN_FILES:
            path = PACK / relative
            with self.subTest(relative=relative):
                for selector in _selectors(path):
                    parsed = parse_selector(selector)
                    self.assertIn(parsed["kind"], ("fs", "generic"))
                    self.assertNotEqual(parsed["kind"], "proc")

    def test_fs_child_is_included_etc_is_not(self) -> None:
        decision = ceiling_allows((_FS,), _FS_CHILD)
        self.assertTrue(decision.included)
        self.assertFalse(ceiling_allows((_FS,), _FS_ETC).included)

    def test_proc_is_generic_literal_equality(self) -> None:
        self.assertTrue(ceiling_allows((_PROC,), _PROC).included)
        self.assertFalse(ceiling_allows((_PROC,), _PROC_OTHER).included)
        self.assertFalse(ceiling_allows((_PROC,), {"kind": "proc", "executable": "python3"}).included)

    def test_host_gate_matches_domain_and_stays_fail_closed(self) -> None:
        caps = ({"verb": "fs.read", "selector": _FS},)
        self.assertTrue(host_ceiling_allows("execute", {"verb": "fs.read", "selector": _FS_CHILD}, caps))
        self.assertFalse(host_ceiling_allows("execute", {"verb": "fs.read", "selector": _FS_ETC}, caps))
        self.assertFalse(host_ceiling_allows("execute", {"verb": "fs.read", "selector": _FS}, ()))
        proc_caps = ({"verb": "proc.exec", "selector": _PROC},)
        self.assertTrue(host_ceiling_allows(
            "execute", {"verb": "proc.exec", "selector": _PROC}, proc_caps))
        self.assertFalse(host_ceiling_allows(
            "execute", {"verb": "proc.exec", "selector": _PROC_OTHER}, proc_caps))


if __name__ == "__main__":
    unittest.main()
