"""Contract and port conformance tests for 1-Forge (Reflexive Agentic Micro-Forge).

Verifies:
1. Port conformance with ModelPort (ports/model.py).
2. Port conformance with SandboxRunner (ports/sandbox.py).
3. Hexagonal boundary adherence (domain <- ports <- kernel <- agency <- runtime -> adapters).
4. Immutable Value Objects and RFC 8785 (JCS) deterministic serializability.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import tempfile
import unittest
from typing import Any, Mapping, Sequence

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.canonicalisation.jcs import canonicalise
from vanguard.packages.ports.event_store import Result
from vanguard.packages.ports.model import ModelPort
from vanguard.packages.ports.sandbox import (
    ContainmentReport,
    ProbeResult,
    SandboxReceipt,
    SandboxResult,
    SandboxRunner,
)
from vanguard.packages.agency.forge import (
    FORGE_PRESET_NAME,
    FORGE_SYSTEM_PROMPT,
    FORGE_TOOLS_SCHEMA,
    ForgeAdmissionGate,
    ForgeAtomicPatcher,
    ForgeConfig,
    ForgeContextCompiler,
    ForgeEngine,
    ForgeFacade,
    ForgeWorkingState,
    GoalContract,
    VerificationReceipt,
)


class MockModelPortDouble(ModelPort):
    """Compliant ModelPort test double."""

    def __init__(self, responses: Sequence[Mapping[str, Any]]) -> None:
        self._responses = list(responses)
        self._idx = 0
        self.recorded_contexts: list[Mapping[str, Any]] = []
        self.recorded_tools: list[Sequence[Mapping[str, Any]]] = []

    def propose(
        self,
        context: Mapping[str, Any],
        tools: Sequence[Mapping[str, Any]],
        sampling: Mapping[str, Any],
    ) -> Result[Mapping[str, Any]]:
        self.recorded_contexts.append(dict(context))
        self.recorded_tools.append(tools)
        if self._idx < len(self._responses):
            resp = self._responses[self._idx]
            self._idx += 1
            return Result.success(resp)
        return Result.success({
            "message": {"content": "Task finished", "tool_calls": []},
            "usage": {"prompt_tokens": 50, "completion_tokens": 10},
        })


class MockSandboxRunnerDouble(SandboxRunner):
    """Compliant SandboxRunner test double."""

    def __init__(self, exit_code: int = 0, stdout: str = "Ran 5 tests\n\nOK\n") -> None:
        self.exit_code = exit_code
        self.stdout = stdout
        self.executed_commands: list[Sequence[str]] = []

    def execute(self, argv: Sequence[str]) -> Result[SandboxResult]:
        self.executed_commands.append(list(argv))
        receipt = SandboxReceipt(exit_code=self.exit_code, stdout_digest=digest_of({"out": self.stdout}))
        containment = ContainmentReport(
            runtime="rootless-bwrap",
            runtime_version="0.9.0",
            namespace="user,pid,ipc,net",
            syscall_profile="strict",
            network_enforcement="deny_all",
            writable_mounts=("/workspace",),
            exposed_sockets=(),
            resource_limits={"max_rss_mb": 512, "timeout_seconds": 30},
            startup_probes=(ProbeResult(kind="mount", attempted="check", observed="isolated", verified=True),),
            attested_at="2026-08-31T00:00:00Z",
            contained=True,
            verified=True,
            visibility_mark="SEALED",
        )
        return Result.success(SandboxResult(receipt=receipt, containment=containment))


class TestForgePortContracts(unittest.TestCase):
    """Verify 1-Forge compliance with hexagonal port interfaces."""

    def test_model_port_interaction(self) -> None:
        """1-Forge must communicate via standard ModelPort proposal protocol."""
        model = MockModelPortDouble([
            {
                "message": {
                    "content": "Viewing file",
                    "tool_calls": [
                        {"function": {"name": "view_file", "arguments": {"path": "README.md"}}}
                    ],
                }
            }
        ])

        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "README.md").write_text("# Test Repo\n", encoding="utf-8")

            engine = ForgeFacade.create_engine(
                workspace_root=ws,
                model_port=model,
            )
            # Run 1 turn
            engine.max_turns = 1
            engine.run_episode(task_brief="Inspect README")

            self.assertEqual(len(model.recorded_contexts), 1)
            self.assertEqual(len(model.recorded_tools), 1)
            # Tool schemas provided must contain forge tools
            tool_names = [t.get("function", {}).get("name") for t in model.recorded_tools[0]]
            self.assertIn("view_file", tool_names)
            self.assertIn("edit_file", tool_names)
            self.assertIn("finish_task", tool_names)

    def test_sandbox_port_interaction(self) -> None:
        """1-Forge must execute commands through SandboxRunner port when configured."""
        sandbox = MockSandboxRunnerDouble(exit_code=0, stdout="Ran 3 tests\n\nOK\n")
        model = MockModelPortDouble([
            {
                "message": {
                    "content": "Running test suite",
                    "tool_calls": [
                        {"function": {"name": "run_command", "arguments": {"command": "pytest -q"}}}
                    ],
                }
            }
        ])

        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            engine = ForgeFacade.create_engine(
                workspace_root=ws,
                model_port=model,
                sandbox_runner=sandbox,
            )
            engine.max_turns = 1
            engine.run_episode(task_brief="Run tests in sandbox")

            self.assertEqual(len(sandbox.executed_commands), 1)
            self.assertEqual(sandbox.executed_commands[0], ["pytest", "-q"])

    def test_rfc8785_canonical_serialization(self) -> None:
        """Domain value contracts must produce RFC 8785 canonical JSON bytes and stable digests."""
        state = ForgeWorkingState(
            task_brief="Fix rate limiter lease recovery",
            active_hypothesis="Atomic CAS failure",
            confirmed_facts=("governor.py line 45 has bad comparison",),
            inspected_files=("src/governor.py", "src/rate_limiter.py"),
            changed_files=("src/governor.py",),
        )

        d1 = state.digest()
        d2 = digest_of(state.to_dict())
        self.assertEqual(d1, d2)
        self.assertTrue(d1.startswith("sha256:"))

        contract = GoalContract(
            task_digest=d1,
            mode="bugfix",
            required_checks=("workspace_changed", "verification_fresh"),
            required_files=("src/governor.py",),
        )
        c_bytes = canonicalise(contract.to_dict())
        self.assertIsInstance(c_bytes, str)
        self.assertEqual(contract.digest(), digest_of(contract.to_dict()))

    def test_hexagonal_boundary_compliance(self) -> None:
        """vanguard/packages/agency/forge must not import adapters or runtime directly."""
        forge_dir = Path(__file__).resolve().parents[2] / "vanguard" / "packages" / "agency" / "forge"
        self.assertTrue(forge_dir.is_dir())

        for py_file in forge_dir.glob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertNotIn("adapters", alias.name.split("."))
                        self.assertNotIn("runtime", alias.name.split("."))
                        self.assertNotIn("subprocess", alias.name.split("."))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.assertNotIn("adapters", node.module.split("."))
                        self.assertNotIn("runtime", node.module.split("."))
                        self.assertNotIn("subprocess", node.module.split("."))


if __name__ == "__main__":
    unittest.main()
