"""M-5b material run: Graph Coloring non-coding domain through the unchanged substrate (WP-B1).

Executes the Graph Coloring task through `Runtime.execute_harness` on the canonical
composition path (manifest / plugin lifecycle, context policy, kernel dispatch, operator approval,
budget lease, ledger) and produces a candidate witness.
The witness is graded and signed by the exterior evaluator daemon under its own identity and key.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import unittest
from pathlib import Path

from vanguard.packages.adapters.evaluators.client import EvaluatorClient
from vanguard.packages.adapters.evaluators.daemon import DaemonConfig, EvaluatorDaemon
from vanguard.packages.adapters.evaluators.signing import VerdictSigner
from vanguard.packages.adapters.models.invocation import ProposalTranslator
from vanguard.packages.agency import RunTermination
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.formal_evidence import (
    TERMINAL_COMPLETED,
    build_bundle,
    verify_bundle,
)
from vanguard.packages.runtime.governance.approvals import OperatorSigner
from vanguard.packages.runtime.root import Runtime, TaskContext

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "packs" / "formal-graph-coloring"
ORACLE = ROOT / "vanguard/packages/adapters/evaluators/suites/formal_graph_coloring.py"
REGISTRY = json.loads((PACK / "tasks" / "registry.json").read_text(encoding="utf-8"))

_IMAGE = "sha256:" + "5b" * 32
_EVAL_KEY = b"m5b-material-evaluator-key-32byt"[:32]
_BOOTSTRAP = (
    "import sys;"
    f"sys.path.insert(0, {str(ROOT)!r});"
    "from vanguard.packages.adapters.evaluators.suites.formal_graph_coloring import main;"
    "sys.exit(main(sys.argv[1:]))"
)


class _ScriptedGraphColoringModel:
    """A generator, not a solver.

    Emits candidate assignment without self-grading.
    """

    def __init__(self, witness_text: str) -> None:
        self._witness = witness_text
        self._turn = -1

    def propose(self, context, tools, sampling):
        del context, sampling
        self._turn += 1
        if self._turn == 0:
            calls = [{"id": "c0", "name": "read", "arguments": {"path": "gc-001.graph.json"}}]
        elif self._turn == 1:
            calls = [
                {
                    "id": "c1",
                    "name": "witness",
                    "arguments": {"path": "witness.json", "content": self._witness},
                }
            ]
        else:
            return Result.success({"kind": "finish", "note": "witness written"})
        return ProposalTranslator.translate(
            {
                "text": "",
                "toolCalls": calls,
                "resolved_model": "scripted-graph-coloring-generator",
                "pricing_known": True,
                "usd_micros": 0,
            },
            tool_schemas=tools,
        )


class _SupervisorBoundOracle:
    def __init__(self, workspace: Path, witness_name: str) -> None:
        from vanguard.packages.adapters.evaluators.suites.formal_graph_coloring import (
            GraphColoringEvaluator,
        )
        from vanguard.packages.ports.evaluator import EvaluationProtocol

        self._inner = GraphColoringEvaluator(workspace)
        self._protocol = EvaluationProtocol(
            "formal-graph-coloring-v1",
            {"graph": "gc-001.graph.json", "witness": witness_name},
        )

    def evaluate(self, run_ref, protocol):
        del protocol
        return self._inner.evaluate(run_ref, self._protocol)


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


class MaterialGraphColoringRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.repo = self.base / "workspace"
        self.repo.mkdir()
        shutil.copyfile(
            PACK / "tasks" / "gc-001.graph.json", self.repo / "gc-001.graph.json"
        )
        self.sealed = self.base / "sealed-oracle"
        self.sealed.mkdir()
        shutil.copyfile(ORACLE, self.sealed / "formal_graph_coloring.py")
        self.socket_path = str(self.base / "eval.sock")
        self.signer = VerdictSigner(_EVAL_KEY, "m5b-gc-material-key")
        self.threads: list[threading.Thread] = []

    def tearDown(self) -> None:
        for thread in self.threads:
            thread.join(timeout=5)
        self.tmp.cleanup()

    def _run(self, witness_file: str):
        witness = (PACK / "tasks" / witness_file).read_text(encoding="utf-8")
        operator = OperatorSigner(b"m5b-material-approval-key")
        return Runtime.execute_harness(
            PACK / "manifest.json",
            TaskContext(
                brief="Produce a complete valid 3-coloring assignment for the graph.",
                repo_path=self.repo,
                run_id="m5b-gc-material",
                episode_id="m5b-gc-material-episode",
                principal="agent-1",
                max_turns=6,
            ),
            model=_ScriptedGraphColoringModel(witness),
            approver=lambda challenge: operator.approve(challenge, reviewer="operator"),
            approval_key=operator.public_bytes,
            verifier=_SupervisorBoundOracle(self.repo, "witness.json"),
            sandbox_mode="host-dev",
        )

    def _signed_verdict(self):
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        daemon = EvaluatorDaemon(
            DaemonConfig(
                socket_path=self.socket_path,
                image_digest=_IMAGE,
                workspace=str(self.repo),
                oracle_digests={
                    "formal_graph_coloring.py": _digest(
                        self.sealed / "formal_graph_coloring.py"
                    )
                },
                command=(
                    "python3",
                    "-c",
                    _BOOTSTRAP,
                    "--graph",
                    str(self.repo / "gc-001.graph.json"),
                    "--witness",
                    str(self.repo / "witness.json"),
                ),
                expected_uid=os.getuid(),
                timeout_seconds=30.0,
                verdict_private_key=_EVAL_KEY,
                verdict_key_id="m5b-gc-material-key",
                oracle_root=str(self.sealed),
                evidence_paths={
                    "formula": str(self.repo / "gc-001.graph.json"),
                    "witness": str(self.repo / "witness.json"),
                    "oracle": str(self.sealed / "formal_graph_coloring.py"),
                },
            )
        )
        thread = threading.Thread(target=daemon.serve_once, daemon=True)
        thread.start()
        self.threads.append(thread)
        for _ in range(200):
            if os.path.exists(self.socket_path):
                break
            time.sleep(0.01)
        from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef

        client = EvaluatorClient(
            socket_path=self.socket_path,
            expected_uid=os.getuid(),
            expected_image_digest=_IMAGE,
            timeout_seconds=30.0,
            expected_verdict_key_id="m5b-gc-material-key",
            expected_verdict_public_key=self.signer.public_bytes,
        )
        result = client.evaluate(
            RunRef("m5b-gc-material", episode_id="m5b-gc-material-episode"),
            EvaluationProtocol("formal-graph-coloring-v1"),
        )
        self.assertTrue(result.ok)
        return result.value

    def test_the_formal_pack_completes_through_the_canonical_composition(self) -> None:
        result = self._run("gc-001.witness.json")
        self.assertIs(result.terminal, RunTermination.COMPLETED, result.detail)
        self.assertEqual(
            [receipt.verb for receipt in result.receipts], ["fs.read", "patch.apply"]
        )
        self.assertTrue((self.repo / "witness.json").is_file())

    def test_the_privileged_write_went_through_operator_approval(self) -> None:
        result = self._run("gc-001.witness.json")
        kinds = [event.kind for event in result.events]
        self.assertIn("ApprovalRequested", kinds)
        self.assertNotIn("AuthorizationDenied", kinds)

    def test_the_run_produces_the_exact_pinned_witness_bytes(self) -> None:
        self._run("gc-001.witness.json")
        task = next(t for t in REGISTRY["tasks"] if t["id"] == "GC-001")
        self.assertEqual(
            _digest(self.repo / "witness.json"), task["positiveWitnessDigest"]
        )

    def test_the_material_run_yields_a_signed_promotable_bundle(self) -> None:
        result = self._run("gc-001.witness.json")
        verdict = self._signed_verdict()
        bundle = build_bundle(
            task_id="GC-001",
            pack_root=PACK,
            registry=REGISTRY,
            verdict=verdict,
            events=result.events,
            oracle_path=ORACLE,
            witness_path=self.repo / "witness.json",
            witness_role="positive",
            public_key=self.signer.public_bytes,
        )
        self.assertEqual(bundle.verdict, "pass")
        self.assertEqual(bundle.terminal_status, TERMINAL_COMPLETED)
        self.assertTrue(bundle.signed)
        self.assertTrue(bundle.promotable)
        self.assertTrue(verify_bundle(bundle, self.signer.public_bytes))

    def test_the_negative_vector_runs_and_is_signed_as_a_failure(self) -> None:
        result = self._run("gc-001.invalid-edge-conflict.json")
        self.assertIs(result.terminal, RunTermination.COMPLETED, result.detail)
        verdict = self._signed_verdict()
        bundle = build_bundle(
            task_id="GC-001",
            pack_root=PACK,
            registry=REGISTRY,
            verdict=verdict,
            events=result.events,
            oracle_path=ORACLE,
            witness_path=self.repo / "witness.json",
            witness_role="negative",
            public_key=self.signer.public_bytes,
        )
        self.assertEqual(bundle.verdict, "fail")
        self.assertTrue(bundle.signed)
        self.assertFalse(bundle.promotable)

    def test_the_in_run_verdict_and_the_daemon_verdict_agree(self) -> None:
        result = self._run("gc-001.witness.json")
        self.assertEqual(result.verdict.outcome, "claims", result.verdict.reason)
        self.assertEqual(result.verdict.claims[0]["status"], "passed")
        self.assertEqual(self._signed_verdict().binding["verdict"], "pass")

    def test_the_trajectory_is_terminal_and_reconstructible(self) -> None:
        result = self._run("gc-001.witness.json")
        terminal = [
            event for event in result.events if event.kind == "EpisodeCompleted"
        ]
        self.assertEqual(len(terminal), 1)
        trajectory = terminal[0].payload["trajectory"]
        self.assertEqual(trajectory["schema"], "mhf.trajectory/2")
        self.assertEqual(trajectory["episode_id"], "m5b-gc-material-episode")


class SubstrateDomainBlindnessForGraphColoring(unittest.TestCase):
    """The substrate remains completely domain-blind with respect to graph coloring."""

    def test_no_graph_coloring_vocabulary_appears_in_the_frozen_substrate(self) -> None:
        import re

        frozen = ("domain", "kernel", "ports", "agency/episode")
        pattern = re.compile(r"\b(graph_coloring|monochromatic|petersen)\b")
        offenders: list[str] = []
        for area in frozen:
            for path in (ROOT / "vanguard/packages" / area).rglob("*.py"):
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
                for match in set(pattern.findall(text)):
                    offenders.append(f"{path.relative_to(ROOT)}: {match}")
        self.assertEqual(sorted(offenders), [])


if __name__ == "__main__":
    unittest.main()
