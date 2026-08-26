"""M-5b: the SAT verdict must be *signed by the evaluator daemon*, not asserted.

`test_rf52_rf53_formal_witness.py` proves the oracle cannot be talked into
agreeing.  This file proves the surviving agreement is attributable.  The gap
between them is the whole difference between "our code said pass" and
"evidence a second reader can check":

* the verdict is produced by the real `EvaluatorDaemon` over a real Unix
  socket, running the pinned exterior oracle under its own identity;
* the signature is Ed25519 over the daemon's JCS body, and the runtime that
  reads it holds no private key with which to forge one;
* the run's terminal axis (`completed` / `abandoned`) is folded from the
  ledger, never inferred from the witness holding.

The last point is the one this file exists to defend.  An abandoned run whose
witness happens to verify is *not* an M-5b result, and the bundle must say so.
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
PACK = ROOT / "packs" / "formal-sat"
ORACLE = ROOT / "vanguard/packages/adapters/evaluators/suites/formal_sat.py"
REGISTRY = json.loads((PACK / "tasks" / "registry.json").read_text(encoding="utf-8"))

_IMAGE = "sha256:" + "5b" * 32
_KEY = b"m5b-evaluator-private-key-32byte"

# The oracle is a package module (relative imports), so the executed argv
# bootstraps it from the repository rather than copying it out of its package.
# Its *bytes* are still pinned twice over: by the registry digest, and by the
# daemon's immutability probe against the sealed oracle mount below.
_BOOTSTRAP = (
    "import sys;"
    f"sys.path.insert(0, {str(ROOT)!r});"
    "from vanguard.packages.adapters.evaluators.suites.formal_sat import main;"
    "sys.exit(main(sys.argv[1:]))"
)


class _Event:
    def __init__(self, kind: str, **payload) -> None:
        self.kind = kind
        self.payload = {"kind": kind, **payload}
        self.reason = payload.get("reason", "")


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


class SignedSatVerdictTests(unittest.TestCase):
    """One real daemon, one real socket, one real signature per assertion."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.socket_path = str(base / "eval.sock")

        # Workspace: the evaluated subject.  It carries the pinned formula and
        # both witness vectors; nothing here can grade anything.
        self.workspace = base / "workspace"
        self.workspace.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.workspace, check=True)
        for name in ("sat-001.cnf", "sat-001.witness.json", "sat-001.invalid-witness.json"):
            shutil.copyfile(PACK / "tasks" / name, self.workspace / name)

        # Sealed oracle mount: the immutable grader the daemon probes.
        self.sealed = base / "sealed-oracle"
        self.sealed.mkdir()
        shutil.copyfile(ORACLE, self.sealed / "formal_sat.py")

        self.signer = VerdictSigner(_KEY, "m5b-eval-key")
        self.threads: list[threading.Thread] = []

    def tearDown(self) -> None:
        for thread in self.threads:
            thread.join(timeout=5)
        self.tmp.cleanup()

    # -- harness ---------------------------------------------------------

    def _serve(self, witness: str, *, sign: bool = True) -> None:
        # The oracle argv is fixed by the evaluator's supervisor before the
        # subject is ever consulted; the run cannot choose its own grader
        # invocation. That is why it lives in `DaemonConfig`, not in the
        # request the client sends.
        daemon = EvaluatorDaemon(DaemonConfig(
            socket_path=self.socket_path,
            image_digest=_IMAGE,
            workspace=str(self.workspace),
            oracle_digests={"formal_sat.py": _digest(self.sealed / "formal_sat.py")},
            command=("python3", "-c", _BOOTSTRAP,
                     "--formula", str(self.workspace / "sat-001.cnf"),
                     "--witness", str(self.workspace / witness)),
            expected_uid=os.getuid(),
            timeout_seconds=30.0,
            verdict_private_key=_KEY if sign else None,
            verdict_key_id="m5b-eval-key",
            oracle_root=str(self.sealed),
            evidence_paths={
                "formula": str(self.workspace / "sat-001.cnf"),
                "witness": str(self.workspace / witness),
                "oracle": str(self.sealed / "formal_sat.py"),
            },
        ))
        thread = threading.Thread(target=daemon.serve_once, daemon=True)
        thread.start()
        self.threads.append(thread)
        for _ in range(200):
            if os.path.exists(self.socket_path):
                return
            time.sleep(0.01)
        self.fail("evaluator daemon did not bind its socket")

    def _evaluate(self, witness: str, *, sign: bool = True, expect_key: bool = True) -> Verdict:
        self._serve(witness, sign=sign)
        client = EvaluatorClient(
            socket_path=self.socket_path,
            expected_uid=os.getuid(),
            expected_image_digest=_IMAGE,
            timeout_seconds=30.0,
            expected_verdict_key_id="m5b-eval-key" if expect_key else None,
            expected_verdict_public_key=self.signer.public_bytes if expect_key else None,
        )
        result = client.evaluate(
            RunRef("m5b-run", episode_id="m5b-episode"),
            EvaluationProtocol("formal-sat-v1",
                               {"formula": "sat-001.cnf", "witness": witness}),
        )
        self.assertTrue(result.ok)
        return result.value

    # -- the evidence ----------------------------------------------------

    def test_the_daemon_signs_a_verdict_the_runtime_cannot_forge(self) -> None:
        verdict = self._evaluate("sat-001.witness.json")
        self.assertIsNotNone(verdict.binding, verdict.reason)
        self.assertEqual(verdict.signer_key_id, "m5b-eval-key")
        self.assertTrue(VerdictSigner.verify(
            verdict.binding, verdict.signature, self.signer.public_bytes))

    def test_a_tampered_signed_body_fails_verification(self) -> None:
        verdict = self._evaluate("sat-001.witness.json")
        forged = {**dict(verdict.binding), "verdict": "pass", "oracle_id": "something-else"}
        self.assertFalse(VerdictSigner.verify(
            forged, verdict.signature, self.signer.public_bytes))

    def test_an_unsigned_daemon_yields_inconclusive_and_no_bundle_pass(self) -> None:
        # No signer provisioned: the daemon must not emit a pass anyone could
        # ledger. Fail-closed is the only correct behaviour here.
        verdict = self._evaluate("sat-001.witness.json", sign=False, expect_key=False)
        bundle = self._bundle(verdict, completed=True)
        self.assertFalse(bundle.signed)
        self.assertFalse(bundle.promotable)
        self.assertEqual(bundle.verdict, "inconclusive")

    # -- the bundle ------------------------------------------------------

    def _bundle(self, verdict: Verdict, *, completed: bool):
        events = [
            _Event("GoalDeclared"),
            _Event("EpisodeCompleted",
                   outcome="resolved" if completed else "abandoned"),
        ]
        return build_bundle(
            task_id="SAT-001", pack_root=PACK, registry=REGISTRY,
            verdict=verdict, events=events, oracle_path=ORACLE,
            witness_path=self.workspace / (
                "sat-001.witness.json" if verdict.binding and
                verdict.binding.get("verdict") == "pass"
                else "sat-001.invalid-witness.json"),
            witness_role=("positive" if verdict.binding and
                          verdict.binding.get("verdict") == "pass" else "negative"),
            public_key=self.signer.public_bytes,
        )

    def test_a_signed_pass_over_a_completed_run_is_promotable(self) -> None:
        bundle = self._bundle(self._evaluate("sat-001.witness.json"), completed=True)
        self.assertEqual(bundle.verdict, "pass")
        self.assertEqual(bundle.terminal_status, TERMINAL_COMPLETED)
        self.assertTrue(bundle.promotable)
        self.assertTrue(verify_bundle(bundle, self.signer.public_bytes))

    def test_an_abandoned_run_is_not_promotable_even_with_a_signed_pass(self) -> None:
        # The two axes do not merge. A witness that verifies says nothing
        # about whether the run that produced it finished.
        bundle = self._bundle(self._evaluate("sat-001.witness.json"), completed=False)
        self.assertEqual(bundle.verdict, "pass")
        self.assertEqual(bundle.terminal_status, TERMINAL_ABANDONED)
        self.assertFalse(bundle.promotable)

    def test_the_negative_vector_is_signed_as_a_failure_not_omitted(self) -> None:
        bundle = self._bundle(self._evaluate("sat-001.invalid-witness.json"), completed=True)
        self.assertEqual(bundle.verdict, "fail")
        self.assertTrue(bundle.signed)
        self.assertFalse(bundle.promotable)

    def test_the_bundle_records_the_bytes_that_were_actually_graded(self) -> None:
        bundle = self._bundle(self._evaluate("sat-001.witness.json"), completed=True)
        task = next(t for t in REGISTRY["tasks"] if t["id"] == "SAT-001")
        self.assertEqual(bundle.formula_digest, task["formulaDigest"])
        self.assertEqual(bundle.witness_digest, task["positiveWitnessDigest"])
        self.assertEqual(bundle.oracle_digest, REGISTRY["oracleDigest"])
        self.assertEqual(bundle.digest(), bundle.digest())

    def test_a_wrong_public_key_does_not_verify_the_bundle(self) -> None:
        bundle = self._bundle(self._evaluate("sat-001.witness.json"), completed=True)
        other = VerdictSigner(b"a-different-evaluator-key-32byte!"[:32], "other")
        self.assertFalse(verify_bundle(bundle, other.public_bytes))


class DriftedPinsRefuseToProduceEvidence(unittest.TestCase):
    """A bundle recording a digest for bytes it did not grade is worse than none."""

    def _verdict(self) -> Verdict:
        body = {"verdict": "pass", "key_id": "k", "nonce": "n"}
        signer = VerdictSigner(_KEY, "k")
        return Verdict(outcome="claims", claims=({"status": "passed"},),
                       signature=signer.sign(body), signer_key_id="k", binding=body)

    def test_a_drifted_formula_digest_raises(self) -> None:
        registry = json.loads(json.dumps(REGISTRY))
        registry["tasks"][0]["formulaDigest"] = "sha256:" + "0" * 64
        with self.assertRaises(ValueError):
            build_bundle(task_id="SAT-001", pack_root=PACK, registry=registry,
                         verdict=self._verdict(), events=(), oracle_path=ORACLE,
                         witness_path=PACK / "tasks/sat-001.witness.json",
                         witness_role="positive",
                         public_key=VerdictSigner(_KEY, "k").public_bytes)

    def test_a_drifted_oracle_digest_raises(self) -> None:
        registry = json.loads(json.dumps(REGISTRY))
        registry["oracleDigest"] = "sha256:" + "0" * 64
        with self.assertRaises(ValueError):
            build_bundle(task_id="SAT-001", pack_root=PACK, registry=registry,
                         verdict=self._verdict(), events=(), oracle_path=ORACLE,
                         witness_path=PACK / "tasks/sat-001.witness.json",
                         witness_role="positive",
                         public_key=VerdictSigner(_KEY, "k").public_bytes)

    def test_an_unknown_task_raises(self) -> None:
        with self.assertRaises(ValueError):
            build_bundle(task_id="SAT-999", pack_root=PACK, registry=REGISTRY,
                         verdict=self._verdict(), events=(), oracle_path=ORACLE,
                         witness_path=PACK / "tasks/sat-001.witness.json",
                         witness_role="positive",
                         public_key=VerdictSigner(_KEY, "k").public_bytes)


class TerminalTruthIsFoldedNotAsserted(unittest.TestCase):
    def test_a_run_with_no_terminal_event_is_abandoned(self) -> None:
        self.assertEqual(terminal_status_from_events([_Event("GoalDeclared")]),
                         TERMINAL_ABANDONED)

    def test_resolved_and_abstained_fold_to_completed(self) -> None:
        for outcome in ("resolved", "completed", "abstained"):
            self.assertEqual(
                terminal_status_from_events([_Event("EpisodeCompleted", outcome=outcome)]),
                TERMINAL_COMPLETED, outcome)

    def test_every_other_termination_keeps_its_own_name(self) -> None:
        for outcome in ("abandoned", "budget_exhausted", "instrument_error", "cancelled"):
            self.assertEqual(
                terminal_status_from_events([_Event("EpisodeCompleted", outcome=outcome)]),
                outcome)

    def test_the_last_terminal_event_wins(self) -> None:
        # A run that aborted and was then recovered ends where it ended.
        events = [_Event("RunAborted", outcome="abandoned"),
                  _Event("RunRecovered", outcome="resolved")]
        self.assertEqual(terminal_status_from_events(events), TERMINAL_COMPLETED)


if __name__ == "__main__":
    unittest.main()
