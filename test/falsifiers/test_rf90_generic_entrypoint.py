"""RF-90 (ADR-0089): code, explain, and doctor share one entrypoint."""

from __future__ import annotations

import unittest

from vanguard.packages.runtime import coding_entrypoint


class RF90GenericEntrypointFalsifier(unittest.TestCase):
    def test_doctor_is_available_without_model_or_network(self) -> None:
        frame = coding_entrypoint.execute({"command": "doctor", "profile": "local"})
        self.assertEqual(frame["type"], "result")
        self.assertEqual(frame["result"]["phase"], "doctor")

    def test_code_and_explain_resolve_the_shared_manifest_entrypoint(self) -> None:
        self.assertEqual(coding_entrypoint._manifest("code").name, "manifest.json")
        self.assertEqual(coding_entrypoint._manifest("explain").name, "manifest.json")
        self.assertIn("vg-code-default", str(coding_entrypoint._manifest("code")))
        self.assertIn("vg-code-explain", str(coding_entrypoint._manifest("explain")))


if __name__ == "__main__":
    unittest.main()
