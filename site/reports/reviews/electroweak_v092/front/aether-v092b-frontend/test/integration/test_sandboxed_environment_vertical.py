"""All product environment verbs through the real rootless worker."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.environment.sandboxed import SandboxedEnvironmentAdapter
from vanguard.packages.adapters.sandbox.rootless import RootlessSandboxRunner
from vanguard.packages.adapters.sandbox.worker import WorkerProtocol
from vanguard.packages.ports.environment import EffectRequest, ObservationRequest


class TestSandboxedEnvironmentVertical(unittest.TestCase):
    def test_read_search_write_patch_and_process_are_one_worker_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspace"
            workspace.mkdir()
            (workspace / "src").mkdir()
            (workspace / "src/value.py").write_text("VALUE = 1\n", encoding="utf-8")
            bundle = root / "sealed-bundle"
            bundle.write_text("sealed", encoding="utf-8")
            worker = WorkerProtocol(RootlessSandboxRunner(workspace, evaluator_bundle=bundle))
            environment = SandboxedEnvironmentAdapter(worker, workspace, "test-environment")

            self.assertTrue(environment.profile().ok)
            self.assertTrue(environment.snapshot().ok)
            read = environment.observe(ObservationRequest(action="read", path="src/value.py"))
            self.assertTrue(read.ok)
            self.assertEqual(read.value.content, "VALUE = 1\n")
            search = environment.observe(ObservationRequest(action="search", pattern="VALUE"))
            self.assertTrue(search.ok)
            self.assertIn("src/value.py", search.value.output or "")

            write = environment.apply(EffectRequest(
                verb="fs.write", action="write",
                args={"path": "src/extra.txt", "content": "extra\n"},
            ))
            self.assertTrue(write.ok)
            self.assertEqual((workspace / "src/extra.txt").read_text(encoding="utf-8"), "extra\n")

            patch = "--- a/src/value.py\n+++ b/src/value.py\n@@ -1 +1 @@\n-VALUE = 1\n+VALUE = 2\n"
            preview = environment.preview(EffectRequest(
                verb="patch.apply", action="patch", patch=patch,
            ))
            self.assertTrue(preview.ok)
            applied = environment.apply(EffectRequest(
                verb="patch.apply", action="patch", patch=patch,
            ))
            self.assertTrue(applied.ok)
            self.assertEqual((workspace / "src/value.py").read_text(encoding="utf-8"), "VALUE = 2\n")

            tested = environment.apply(EffectRequest(
                verb="proc.exec", action="exec",
                command=["python3", "-c", "print('sandbox-ok')"],
            ))
            self.assertTrue(tested.ok)
            self.assertEqual(tested.value.exit_code, 0)
            self.assertIn("sandbox-ok", tested.value.output or "")


if __name__ == "__main__":
    unittest.main()
