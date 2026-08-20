"""Fail-closed plugin-cell ceiling over the domain selector algebra (2.1-D)."""

from __future__ import annotations

import unittest

from vanguard.packages.adapters.sandbox.ceiling import ceiling_allows

_FS = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}
_CHILD = {"kind": "fs", "root": "/workspace", "paths": ["/workspace/src"]}
_OUTSIDE = {"kind": "fs", "root": "/etc", "paths": ["/etc"]}
_CAPS = ({"verb": "echo", "selector": _FS},)


class PluginCeilingTests(unittest.TestCase):
    def test_empty_capabilities_deny_execute(self) -> None:
        self.assertFalse(ceiling_allows("execute", {"verb": "echo", "selector": _FS}, ()))

    def test_non_host_method_denied(self) -> None:
        self.assertFalse(ceiling_allows("host.grant", {}, _CAPS))

    def test_health_not_gated_by_ceiling(self) -> None:
        self.assertTrue(ceiling_allows("health", {}, ()))

    def test_included_selector_allowed(self) -> None:
        self.assertTrue(ceiling_allows(
            "execute", {"verb": "echo", "selector": _CHILD}, _CAPS))

    def test_outside_selector_denied(self) -> None:
        self.assertFalse(ceiling_allows(
            "execute", {"verb": "echo", "selector": _OUTSIDE}, _CAPS))

    def test_unknown_verb_denied(self) -> None:
        self.assertFalse(ceiling_allows(
            "execute", {"verb": "proc.exec", "selector": _FS}, _CAPS))

    def test_no_private_subset_walk(self) -> None:
        import inspect
        from vanguard.packages.adapters.sandbox import ceiling as mod

        self.assertFalse(hasattr(mod, "_selector_subset"))
        self.assertNotIn("_selector_subset", inspect.getsource(mod))
        import layer0.spi.ceiling as shim

        self.assertFalse(hasattr(shim, "_selector_subset"))
        self.assertNotIn("def _selector_subset", inspect.getsource(shim))


if __name__ == "__main__":
    unittest.main()
