"""M-5b material run: a non-coding domain through the unchanged substrate (`B-M5B`).

This is the milestone's actual claim, executed rather than asserted. One
formal-SAT task runs through `Runtime.execute_harness` on the same composition
path the coding pack uses -- plugin lifecycle, context policy, kernel dispatch,
operator approval, budget lease, ledger -- and produces a witness. The witness
is then graded by the exterior evaluator **daemon**, under its own identity and
its own signature, and the two facts are bound into one evidence bundle.

What makes it evidence rather than a demo:

* **The substrate is untouched.** No SAT knowledge enters kernel, agency or
  runtime; the pack supplies prompts, tools and policies, and that is all.
  RF-98 checks this structurally; this run checks it behaviourally, by
  succeeding at all.
* **The pack cannot grade itself.** The generator writes an assignment. The
  daemon decides whether it holds. Those are different processes with
  different keys, and the runtime holds neither the search nor the private
  key.
* **Both axes are recorded.** The run's terminal status is folded from its own
  ledger, and a passing witness over an abandoned run is not promotable.

The negative vector runs the same way, because a pipeline that only ever
produces `pass` has not been shown to be able to produce `fail`.
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
PACK = ROOT / "packs" / "formal-sat"
ORACLE = ROOT / "vanguard/packages/adapters/evaluators/suites/formal_sat.py"
REGISTRY = json.loads((PACK / "tasks" / "registry.json").read_text(encoding="utf-8"))

_IMAGE = "sha256:" + "5b" * 32
_EVAL_KEY = b"m5b-material-evaluator-key-32byt"[:32]
_BOOTSTRAP = (
    "import sys;"
    f"sys.path.insert(0, {str(ROOT)!r});"
    "from vanguard.packages.adapters.evaluators.suites.formal_sat import main;"
    "sys.exit(main(sys.argv[1:]))"
)


class _ScriptedSatModel:
    """A generator, not a solver.

    It emits the candidate assignment and never checks it -- which is the
    point: if the model could grade its own witness the exterior-oracle claim
    would be empty. The proposals go through the ordinary
    `ProposalTranslator`, so the resource and scope come from the pack's own
    tool schemas rather than from anything this test invents.
    """

    def __init__(self, witness_text: str) -> None:
        self._witness = witness_text
        self._turn = -1

    def propose(self, context, tools, sampling):
        del context, sampling
        self._turn += 1
        if self._turn == 0:
            calls = [{"id": "c0", "name": "read", "arguments": {"path": "sat-001.cnf"}}]
        elif self._turn == 1:
            calls = [{"id": "c1", "name": "witness",
                      "arguments": {"path": "witness.json", "content": self._witness}}]
        else:
            return Result.success({"kind": "finish", "note": "witness written"})
        return ProposalTranslator.translate(
            {"text": "", "toolCalls": calls, "resolved_model": "scripted-sat-generator",
             "pricing_known": True, "usd_micros": 0},
            tool_schemas=tools)


class _SupervisorBoundOracle:
    """The exterior oracle with its task bound by the supervisor, not the run.

    The subject does not choose which formula it is graded against; that is
    fixed before the run starts. Binding it here rather than inside the oracle
    module keeps the registry's `oracleDigest` pin intact.
    """

    def __init__(self, workspace: Path, witness_name: str) -> None:
        from vanguard.packages.adapters.evaluators.suites.formal_sat import SatWitnessEvaluator
        from vanguard.packages.ports.evaluator import EvaluationProtocol

        self._inner = SatWitnessEvaluator(workspace)
        self._protocol = EvaluationProtocol(
            "formal-sat-v1", {"formula": "sat-001.cnf", "witness": witness_name})

    def evaluate(self, run_ref, protocol):
        del protocol
        return self._inner.evaluate(run_ref, self._protocol)


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


class MaterialSatRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.repo = self.base / "workspace"
        self.repo.mkdir()
        shutil.copyfile(PACK / "tasks" / "sat-001.cnf", self.repo / "sat-001.cnf")
        self.sealed = self.base / "sealed-oracle"
        self.sealed.mkdir()
        shutil.copyfile(ORACLE, self.sealed / "formal_sat.py")
        self.socket_path = str(self.base / "eval.sock")
        self.signer = VerdictSigner(_EVAL_KEY, "m5b-material-key")
        self.threads: list[threading.Thread] = []

    def tearDown(self) -> None:
        for thread in self.threads:
            thread.join(timeout=5)
        self.tmp.cleanup()

    # -- the run ---------------------------------------------------------

    def _run(self, witness_file: str):
        witness = (PACK / "tasks" / witness_file).read_text(encoding="utf-8")
        operator = OperatorSigner(b"m5b-material-approval-key")
        return Runtime.execute_harness(
            PACK / "manifest.json",
            TaskContext(brief="Produce a complete satisfying assignment for the formula.",
                        repo_path=self.repo, run_id="m5b-material",
                        episode_id="m5b-material-episode", principal="agent-1",
                        max_turns=6),
            model=_ScriptedSatModel(witness),
            approver=lambda challenge: operator.approve(challenge, reviewer="operator"),
            approval_key=operator.public_bytes,
            verifier=_SupervisorBoundOracle(self.repo, "witness.json"),
            sandbox_mode="host-dev",
        )

    # -- the signature ---------------------------------------------------

    def _signed_verdict(self):
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        daemon = EvaluatorDaemon(DaemonConfig(
            socket_path=self.socket_path, image_digest=_IMAGE,
            workspace=str(self.repo),
            oracle_digests={"formal_sat.py": _digest(self.sealed / "formal_sat.py")},
            command=("python3", "-c", _BOOTSTRAP,
                     "--formula", str(self.repo / "sat-001.cnf"),
                     "--witness", str(self.repo / "witness.json")),
            expected_uid=os.getuid(), timeout_seconds=30.0,
            verdict_private_key=_EVAL_KEY, verdict_key_id="m5b-material-key",
            oracle_root=str(self.sealed),
            evidence_paths={
                "formula": str(self.repo / "sat-001.cnf"),
                "witness": str(self.repo / "witness.json"),
                "oracle": str(self.sealed / "formal_sat.py"),
            },
        ))
        thread = threading.Thread(target=daemon.serve_once, daemon=True)
        thread.start()
        self.threads.append(thread)
        for _ in range(200):
            if os.path.exists(self.socket_path):
                break
            time.sleep(0.01)
        from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef

        client = EvaluatorClient(
            socket_path=self.socket_path, expected_uid=os.getuid(),
            expected_image_digest=_IMAGE, timeout_seconds=30.0,
            expected_verdict_key_id="m5b-material-key",
            expected_verdict_public_key=self.signer.public_bytes)
        result = client.evaluate(RunRef("m5b-material", episode_id="m5b-material-episode"),
                                 EvaluationProtocol("formal-sat-v1"))
        self.assertTrue(result.ok)
        return result.value

    # -- assertions ------------------------------------------------------

    def test_the_formal_pack_completes_through_the_canonical_composition(self) -> None:
        result = self._run("sat-001.witness.json")
        self.assertIs(result.terminal, RunTermination.COMPLETED, result.detail)
        self.assertEqual([receipt.verb for receipt in result.receipts],
                         ["fs.read", "patch.apply"])
        self.assertTrue((self.repo / "witness.json").is_file())

    def test_the_privileged_write_went_through_operator_approval(self) -> None:
        # A formal domain gets no shortcut past the trust spine: the witness
        # is a privileged mutation and is approved like any other.
        result = self._run("sat-001.witness.json")
        kinds = [event.kind for event in result.events]
        self.assertIn("ApprovalRequested", kinds)
        self.assertNotIn("AuthorizationDenied", kinds)

    def test_the_run_produces_the_exact_pinned_witness_bytes(self) -> None:
        self._run("sat-001.witness.json")
        task = next(t for t in REGISTRY["tasks"] if t["id"] == "SAT-001")
        self.assertEqual(_digest(self.repo / "witness.json"), task["positiveWitnessDigest"])

    def test_the_material_run_yields_a_signed_promotable_bundle(self) -> None:
        result = self._run("sat-001.witness.json")
        verdict = self._signed_verdict()
        bundle = build_bundle(task_id="SAT-001", pack_root=PACK, registry=REGISTRY,
                              verdict=verdict, events=result.events, oracle_path=ORACLE,
                              witness_path=self.repo / "witness.json",
                              witness_role="positive",
                              public_key=self.signer.public_bytes)
        self.assertEqual(bundle.verdict, "pass")
        self.assertEqual(bundle.terminal_status, TERMINAL_COMPLETED)
        self.assertTrue(bundle.signed)
        self.assertTrue(bundle.promotable)
        self.assertTrue(verify_bundle(bundle, self.signer.public_bytes))

    def test_the_negative_vector_runs_the_same_way_and_is_signed_as_a_failure(self) -> None:
        # A pipeline that has only ever produced `pass` has not been shown to
        # be capable of producing `fail`.
        result = self._run("sat-001.invalid-witness.json")
        self.assertIs(result.terminal, RunTermination.COMPLETED, result.detail)
        verdict = self._signed_verdict()
        bundle = build_bundle(task_id="SAT-001", pack_root=PACK, registry=REGISTRY,
                              verdict=verdict, events=result.events, oracle_path=ORACLE,
                              witness_path=self.repo / "witness.json",
                              witness_role="negative",
                              public_key=self.signer.public_bytes)
        self.assertEqual(bundle.verdict, "fail")
        self.assertTrue(bundle.signed)
        self.assertFalse(bundle.promotable)

    def test_the_in_run_verdict_and_the_daemon_verdict_agree(self) -> None:
        # Two independent readings of the same witness. If the in-run
        # evaluator and the daemon disagreed, one of them is not reading the
        # bytes it claims to.
        result = self._run("sat-001.witness.json")
        self.assertEqual(result.verdict.outcome, "claims", result.verdict.reason)
        self.assertEqual(result.verdict.claims[0]["status"], "passed")
        self.assertEqual(self._signed_verdict().binding["verdict"], "pass")

    def test_the_trajectory_is_terminal_and_reconstructible(self) -> None:
        result = self._run("sat-001.witness.json")
        terminal = [event for event in result.events if event.kind == "EpisodeCompleted"]
        self.assertEqual(len(terminal), 1)
        trajectory = terminal[0].payload["trajectory"]
        self.assertEqual(trajectory["schema"], "mhf.trajectory/2")
        self.assertEqual(trajectory["episode_id"], "m5b-material-episode")


class TheSubstrateLearnedNothingAboutSat(unittest.TestCase):
    """The generality claim is only as good as the kernel's ignorance."""

    def test_no_sat_vocabulary_appears_in_the_frozen_substrate(self) -> None:
        # Unambiguous domain vocabulary only. "clause" is deliberately absent
        # from this list: `kernel/provenance.py` uses it in its ordinary
        # logical sense ("Clause S1(e)"), and a token that flags correct code
        # trains readers to ignore the gate.
        import re

        frozen = ("domain", "kernel", "ports", "agency/episode")
        pattern = re.compile(r"\b(dimacs|cnf|satisfiab\w*|boolean assignment)\b")
        offenders: list[str] = []
        for area in frozen:
            for path in (ROOT / "vanguard/packages" / area).rglob("*.py"):
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
                for match in set(pattern.findall(text)):
                    offenders.append(f"{path.relative_to(ROOT)}: {match}")
        self.assertEqual(sorted(offenders), [])

    def test_the_pack_is_the_only_place_that_knows_the_domain(self) -> None:
        self.assertTrue((PACK / "system-prompt.txt").is_file())
        self.assertIn("formal-sat", REGISTRY["id"])


if __name__ == "__main__":
    unittest.main()
