"""Contract tests for the offline LAM ModelPort adapter."""

from __future__ import annotations

import unittest

from vanguard.packages.adapters.models.lam import LamModelAdapter


TOOLS = (
    {"name": "read", "verb": "fs.read"},
    {"name": "patch", "verb": "patch.apply"},
    {"name": "test", "verb": "proc.exec"},
)


class LamModelAdapterContract(unittest.TestCase):
    def setUp(self) -> None:
        self.model = LamModelAdapter("lam/t0-vanguard-vertical")
        self.context = {
            "layers": [
                {"layer": "L1", "role": "system", "content": "Use typed tools."},
                {"layer": "L4", "role": "user", "content": "Repair the value."},
            ],
        }

    def test_read_patch_test_finish_advances_from_observations(self) -> None:
        first = self.model.propose(self.context, TOOLS, {})
        self.assertTrue(first.ok)
        self.assertEqual(first.value["action"], "fs.read")

        self.context["layers"].append({"layer": "L5", "role": "user", "content": "read receipt: VALUE = 1"})
        second = self.model.propose(self.context, TOOLS, {})
        self.assertTrue(second.ok)
        self.assertEqual(second.value["action"], "patch.apply")
        self.assertIsNone(second.value["reservation"])

        self.context["layers"].append({"layer": "L5", "role": "user", "content": "patch receipt: applied"})
        third = self.model.propose(self.context, TOOLS, {})
        self.assertTrue(third.ok)
        self.assertEqual(third.value["action"], "proc.exec")

        self.context["layers"].append({"layer": "L5", "role": "user", "content": "test receipt: passed"})
        fourth = self.model.propose(self.context, TOOLS, {})
        self.assertTrue(fourth.ok)
        self.assertEqual(fourth.value["kind"], "finish")

    def test_unknown_scenario_is_typed_instrument_error(self) -> None:
        result = LamModelAdapter("lam/does-not-exist").propose(self.context, TOOLS, {})
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "instrument_error")


if __name__ == "__main__":
    unittest.main()
