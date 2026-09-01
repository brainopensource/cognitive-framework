"""M-5b: The Graph Coloring verdict must be signed by the EvaluatorDaemon, not asserted.

Verifies:
1. Verdict is produced by the real EvaluatorDaemon over a real Unix domain socket.
2. Ed25519 signature over JCS body.
3. Terminal truth folded from the ledger (RunTermination / EpisodeCompleted).
4. Both axes (run completion and evaluation pass) required for promotable evidence.
5. Negative vectors signed as failures and not promotable.
"""

from __future__ import annotations

import base64
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
from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef, Verdict
from vanguard.packages.runtime.formal_evidence import (
    TERMINAL_ABANDONED,
    TERMINAL_COMPLETED,
    build_bundle,
    terminal_status_from_events,
    verify_bundle,
)

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "packs" / "formal-graph-coloring"
ORACLE = ROOT / "vanguard/packages/adapters/evaluators/suites/formal_graph_coloring.py"
REGISTRY = json.loads((PACK / "tasks" / "registry.json").read_text(encoding="utf-8"))

_IMAGE = "sha256:" + "5b" * 32
_KEY = b"m5b-evaluator-private-key-32byte"

_BOOTSTRAP = (
    "import sys;"
    f"sys.path.insert(0, {str(ROOT)!r});"
    "from vanguard.packages.adapters.evaluators.suites.formal_graph_coloring import main;"
    "sys.exit(main(sys.argv[1:]))"
)


class _Event:
    def __init__(self, kind: str, **payload) -> None:
        self.kind = kind
        self.payload = {"kind": kind, **payload}
        self.reason = payload.get("reason", "")


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


class SignedGraphColoringVerdictTests(unittest.TestCase):
    """Real evaluator daemon, real UDS socket, real Ed25519 signatures."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.socket_path = str(base / "eval.sock")

        self.workspace = base / "workspace"
        self.workspace.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.workspace, check=True)
        for name in (
            "gc-001.graph.json",
            "gc-001.witness.json",
            "gc-001.invalid-edge-conflict.json",
        ):
            shutil.copyfile(PACK / "tasks" / name, self.workspace / name)

        self.sealed = base / "sealed-oracle"
        self.sealed.mkdir()
        shutil.copyfile(ORACLE, self.sealed / "formal_graph_coloring.py")

        self.signer = VerdictSigner(_KEY, "m5b-gc-key")
        self.threads: list[threading.Thread] = []

    def tearDown(self) -> None:
        for thread in self.threads:
            thread.join(timeout=5)
        self.tmp.cleanup()

    def _serve(self, witness: str, *, sign: bool = True) -> None:
        daemon = EvaluatorDaemon(
            DaemonConfig(
                socket_path=self.socket_path,
                image_digest=_IMAGE,
                workspace=str(self.workspace),
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
                    str(self.workspace / "gc-001.graph.json"),
                    "--witness",
                    str(self.workspace / witness),
                ),
                expected_uid=os.getuid(),
                timeout_seconds=30.0,
                verdict_private_key=_KEY if sign else None,
                verdict_key_id="m5b-gc-key",
                oracle_root=str(self.sealed),
                evidence_paths={
                    "formula": str(self.workspace / "gc-001.graph.json"),
                    "witness": str(self.workspace / witness),
                    "oracle": str(self.sealed / "formal_graph_coloring.py"),
                },
            )
        )
        thread = threading.Thread(target=daemon.serve_once, daemon=True)
        thread.start()
        self.threads.append(thread)
        for _ in range(200):
            if os.path.exists(self.socket_path):
                return
            time.sleep(0.01)
        self.fail("evaluator daemon did not bind its socket")

    def _evaluate(
        self, witness: str, *, sign: bool = True, expect_key: bool = True
    ) -> Verdict:
        self._serve(witness, sign=sign)
        client = EvaluatorClient(
            socket_path=self.socket_path,
            expected_uid=os.getuid(),
            expected_image_digest=_IMAGE,
            timeout_seconds=30.0,
            expected_verdict_key_id="m5b-gc-key" if expect_key else None,
            expected_verdict_public_key=self.signer.public_bytes if expect_key else None,
        )
        result = client.evaluate(
            RunRef("m5b-gc-run", episode_id="m5b-gc-episode"),
            EvaluationProtocol(
                "formal-graph-coloring-v1",
                {"graph": "gc-001.graph.json", "witness": witness},
            ),
        )
        self.assertTrue(result.ok)
        return result.value

    def _bundle(self, verdict: Verdict, *, completed: bool):
        events = [
            _Event("GoalDeclared"),
            _Event(
                "EpisodeCompleted",
                outcome="resolved" if completed else "abandoned",
            ),
        ]
        return build_bundle(
            task_id="GC-001",
            pack_root=PACK,
            registry=REGISTRY,
            verdict=verdict,
            events=events,
            oracle_path=ORACLE,
            witness_path=self.workspace
            / (
                "gc-001.witness.json"
                if verdict.binding and verdict.binding.get("verdict") == "pass"
                else "gc-001.invalid-edge-conflict.json"
            ),
            witness_role=(
                "positive"
                if verdict.binding and verdict.binding.get("verdict") == "pass"
                else "negative"
            ),
            public_key=self.signer.public_bytes,
        )

    def test_the_daemon_signs_a_verdict_the_runtime_cannot_forge(self) -> None:
        verdict = self._evaluate("gc-001.witness.json")
        self.assertIsNotNone(verdict.binding, verdict.reason)
        self.assertEqual(verdict.signer_key_id, "m5b-gc-key")
        self.assertTrue(
            VerdictSigner.verify(
                verdict.binding, verdict.signature, self.signer.public_bytes
            )
        )

    def test_tampered_signed_body_fails_verification(self) -> None:
        verdict = self._evaluate("gc-001.witness.json")
        forged = {
            **dict(verdict.binding),
            "verdict": "pass",
            "oracle_id": "forged-oracle",
        }
        self.assertFalse(
            VerdictSigner.verify(
                forged, verdict.signature, self.signer.public_bytes
            )
        )

    def test_unsigned_daemon_yields_inconclusive_and_not_promotable(self) -> None:
        verdict = self._evaluate("gc-001.witness.json", sign=False, expect_key=False)
        bundle = self._bundle(verdict, completed=True)
        self.assertFalse(bundle.signed)
        self.assertFalse(bundle.promotable)
        self.assertEqual(bundle.verdict, "inconclusive")

    def test_signed_pass_over_completed_run_is_promotable(self) -> None:
        bundle = self._bundle(self._evaluate("gc-001.witness.json"), completed=True)
        self.assertEqual(bundle.verdict, "pass")
        self.assertEqual(bundle.terminal_status, TERMINAL_COMPLETED)
        self.assertTrue(bundle.promotable)
        self.assertTrue(verify_bundle(bundle, self.signer.public_bytes))

    def test_abandoned_run_is_not_promotable_even_with_signed_pass(self) -> None:
        bundle = self._bundle(self._evaluate("gc-001.witness.json"), completed=False)
        self.assertEqual(bundle.verdict, "pass")
        self.assertEqual(bundle.terminal_status, TERMINAL_ABANDONED)
        self.assertFalse(bundle.promotable)

    def test_negative_vector_is_signed_as_failure(self) -> None:
        bundle = self._bundle(
            self._evaluate("gc-001.invalid-edge-conflict.json"), completed=True
        )
        self.assertEqual(bundle.verdict, "fail")
        self.assertTrue(bundle.signed)
        self.assertFalse(bundle.promotable)


if __name__ == "__main__":
    unittest.main()
