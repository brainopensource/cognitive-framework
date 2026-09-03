"""RF-90 (ADR-0089): code, explain, and doctor share one entrypoint."""

from __future__ import annotations

import unittest

from vanguard.packages.runtime import entrypoint


class RF90GenericEntrypointFalsifier(unittest.TestCase):
    def test_doctor_is_available_without_model_or_network(self) -> None:
        frame = entrypoint.execute({"command": "doctor"})
        self.assertEqual(frame["type"], "result")
        self.assertEqual(frame["result"]["phase"], "doctor")
        self.assertIsNotNone(frame["result"]["planDigest"])

    def test_code_and_explain_resolve_the_shared_manifest_entrypoint(self) -> None:
        self.assertEqual(entrypoint._manifest("code").name, "manifest.json")
        self.assertEqual(entrypoint._manifest("explain").name, "manifest.json")
        self.assertIn("vg-code-default", str(entrypoint._manifest("code")))
        self.assertIn("vg-code-explain", str(entrypoint._manifest("explain")))

    def test_code_with_fake_backend_executes_cleanly(self) -> None:
        frame = entrypoint.execute({
            "command": "code",
            "brief": "test brief",
            "workspace": ".",
            "fakeBackend": "greenfield-adaptive",
            "profile": "product",
        })
        self.assertEqual(frame["type"], "result")
        self.assertIn(frame["result"]["outcome"], {"completed", "abstained"})

    def test_resume_command_executes_without_explicit_brief(self) -> None:
        frame = entrypoint.execute({
            "command": "resume",
            "runId": "run-test-resume",
            "workspace": ".",
            "fakeBackend": "greenfield-adaptive",
            "profile": "product",
        })
        self.assertEqual(frame["type"], "result")
        self.assertIn(frame["result"]["outcome"], {"completed", "abstained"})


if __name__ == "__main__":
    unittest.main()
