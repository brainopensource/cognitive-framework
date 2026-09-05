"""Deterministic replay & cassette verification tests for native agent catalog.

Owning contract: VG-01 §4.1, VG-04 §8 / `CT-33`, GTS-13C T3.8, S8-B-01.

Invariants:
- Zero I/O and zero network access during cassette replay.
- Byte-identical reproduction: replaying a cassette reproduces exact recorded model proposals.
- Fail-closed behavior on cassette exhaustion or unknown requests (CT-33).
- Read-only agent (vg-code-explain) never attempts or produces mutating write effects.
- 5-step Lex protocol agent (vg-code-lex) executes full inspection -> edit -> verify sequence.
"""

from __future__ import annotations

import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from vanguard.packages.adapters.models.cassette import (
    Cassette,
    CassettePlayer,
    CassetteRecord,
    CassetteRecorder,
)
from vanguard.packages.agency import RunTermination
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.compose import TaskContext
from vanguard.packages.runtime.governance.approvals import OperatorSigner
from vanguard.packages.runtime.root import Runtime

ROOT_DIR = Path(__file__).resolve().parents[2]
CASSETTES_DIR = Path(__file__).resolve().parent / "cassettes"
MANIFESTS_DIR = ROOT_DIR / "vanguard" / "packages" / "agency" / "manifests"


class TestDeterministicCassetteReplay(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp.name)
        (self.workspace / "calc.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
        (self.workspace / "test_calc.py").write_text(
            "import unittest\nfrom calc import add\n\n"
            "class TestCalc(unittest.TestCase):\n"
            "    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n",
            encoding="utf-8",
        )
        self.signer = OperatorSigner(b"test-operator-held-approval-key")
        self.operator_key = self.signer.public_bytes
        self.approver = lambda challenge: self.signer.approve(challenge, reviewer="agent-1")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _load_cassette(self, filename: str) -> Cassette:
        path = CASSETTES_DIR / filename
        self.assertTrue(path.exists(), f"Cassette file not found: {path}")
        return Cassette.from_json(path.read_text(encoding="utf-8"))

    def test_vg_code_lex_replay_zero_io_and_byte_identical(self) -> None:
        """Task 1: Deterministic replay of vg-code-lex cassette with zero network I/O."""
        cassette = self._load_cassette("vg_code_lex.cassette.json")
        self.assertEqual(len(cassette.records), 5)
        initial_digest = cassette.digest()

        player = CassettePlayer(cassette, match_mode="tape")
        manifest_p = MANIFESTS_DIR / "vg-code-lex" / "manifest.json"

        task = TaskContext(
            brief="Fix addition bug in calc.py",
            repo_path=self.workspace,
            run_id="run-lex-replay-1",
            episode_id="ep-lex-replay-1",
            max_turns=10,
        )

        proposals_captured: list[dict] = []
        original_propose = player.propose

        def spy_propose(ctx, tools, sampling):
            res = original_propose(ctx, tools, sampling)
            if res.ok:
                proposals_captured.append(dict(res.value))
            return res

        player.propose = spy_propose  # type: ignore

        # Zero I/O assertion: socket creation raises immediately
        with patch.object(socket, "socket", side_effect=AssertionError("Network accessed during cassette replay!")):
            result = Runtime.execute_profiled(
                manifest_p,
                task,
                profile_id="ci",
                model=player,
                approver=self.approver,
                approval_key=self.operator_key,
            )

        self.assertEqual(str(getattr(result.terminal, "value", result.terminal)), "completed")
        self.assertEqual(len(proposals_captured), 5)

        # Verify byte-identical proposal reproduction matching cassette golden records
        for i, rec in enumerate(cassette.records):
            self.assertEqual(proposals_captured[i], rec.proposal)

        # Cassette integrity preserved
        self.assertEqual(cassette.digest(), initial_digest)

    def test_vg_code_explain_replay_zero_io_and_byte_identical(self) -> None:
        """Task 1: Deterministic replay of vg-code-explain cassette with zero network I/O."""
        cassette = self._load_cassette("vg_code_explain.cassette.json")
        self.assertEqual(len(cassette.records), 3)
        initial_digest = cassette.digest()

        player = CassettePlayer(cassette, match_mode="tape")
        manifest_p = MANIFESTS_DIR / "vg-code-explain" / "manifest.json"

        task = TaskContext(
            brief="Explain calculator module architecture",
            repo_path=self.workspace,
            run_id="run-explain-replay-1",
            episode_id="ep-explain-replay-1",
            max_turns=8,
        )

        proposals_captured: list[dict] = []
        original_propose = player.propose

        def spy_propose(ctx, tools, sampling):
            res = original_propose(ctx, tools, sampling)
            if res.ok:
                proposals_captured.append(dict(res.value))
            return res

        player.propose = spy_propose  # type: ignore

        with patch.object(socket, "socket", side_effect=AssertionError("Network accessed during cassette replay!")):
            result = Runtime.execute_profiled(
                manifest_p,
                task,
                profile_id="ci",
                model=player,
                approver=self.approver,
                approval_key=self.operator_key,
            )

        self.assertEqual(str(getattr(result.terminal, "value", result.terminal)), "completed")
        self.assertEqual(len(proposals_captured), 3)

        for i, rec in enumerate(cassette.records):
            self.assertEqual(proposals_captured[i], rec.proposal)

        # Verify explain agent did not perform any write or mutation effects
        verbs_in_receipts = {r.verb for r in result.receipts}
        self.assertTrue(verbs_in_receipts.issubset({"fs.read", "fs.search"}))
        self.assertNotIn("patch.apply", verbs_in_receipts)
        self.assertNotIn("fs.patch", verbs_in_receipts)
        self.assertNotIn("proc.exec", verbs_in_receipts)

        self.assertEqual(cassette.digest(), initial_digest)

    def test_cassette_replay_repeatable_across_multiple_runs(self) -> None:
        """Replaying the same cassette multiple times reproduces identical proposals and terminal states."""
        cassette = self._load_cassette("vg_code_explain.cassette.json")
        manifest_p = MANIFESTS_DIR / "vg-code-explain" / "manifest.json"

        runs_proposals: list[list[dict]] = []

        for run_idx in range(3):
            player = CassettePlayer(cassette, match_mode="tape")
            proposals: list[dict] = []
            orig_prop = player.propose

            def make_spy(collector):
                def _spy(ctx, tools, sampling):
                    r = orig_prop(ctx, tools, sampling)
                    if r.ok:
                        collector.append(dict(r.value))
                    return r
                return _spy

            player.propose = make_spy(proposals)  # type: ignore

            task = TaskContext(
                brief="Explain calculator module architecture",
                repo_path=self.workspace,
                run_id=f"run-rep-{run_idx}",
                episode_id=f"ep-rep-{run_idx}",
                max_turns=5,
            )
            result = Runtime.execute_profiled(
                manifest_p,
                task,
                profile_id="ci",
                model=player,
                approver=self.approver,
                approval_key=self.operator_key,
            )
            self.assertEqual(str(getattr(result.terminal, "value", result.terminal)), "completed")
            runs_proposals.append(proposals)

        self.assertEqual(runs_proposals[0], runs_proposals[1])
        self.assertEqual(runs_proposals[1], runs_proposals[2])

    def test_live_recording_and_subsequent_replay_parity(self) -> None:
        """Record live model interactions and replay them with 100% parity."""
        recorder = CassetteRecorder()
        
        # Simulate recording interactions
        p1 = {
            "kind": "effect",
            "action": "fs.read",
            "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
            "args": {"path": "calc.py"},
            "note": "reading calc.py",
        }
        p2 = {
            "kind": "finish",
            "note": "inspection done",
        }

        ctx1 = {"turn": 0, "brief": "inspect calc"}
        ctx2 = {"turn": 1, "brief": "inspect calc", "lastProgressSignal": "ok"}
        tools = [{"name": "fs.read"}]
        sampling = {"temperature": 0.0}

        recorder.record_interaction(ctx1, tools, sampling, p1)
        recorder.record_interaction(ctx2, tools, sampling, p2)

        raw_json = recorder.cassette.to_json()
        restored_cassette = Cassette.from_json(raw_json)
        self.assertEqual(len(restored_cassette.records), 2)
        self.assertEqual(restored_cassette.digest(), recorder.cassette.digest())

        # Playback in tape mode
        player_tape = CassettePlayer(restored_cassette, match_mode="tape")
        r1 = player_tape.propose(ctx1, tools, sampling)
        self.assertTrue(r1.ok)
        self.assertEqual(r1.value, p1)
        r2 = player_tape.propose(ctx2, tools, sampling)
        self.assertTrue(r2.ok)
        self.assertEqual(r2.value, p2)

        # Exhaustion returns instrument error (CT-33)
        r3 = player_tape.propose(ctx2, tools, sampling)
        self.assertFalse(r3.ok)
        self.assertEqual(r3.error.kind, "instrument_error")

    def test_cassette_exhaustion_or_unknown_digest_fails_closed(self) -> None:
        """CT-33: CassettePlayer returns typed instrument_error on tape exhaustion or unknown digest."""
        cassette = Cassette()
        cassette.add_record(
            context={"turn": 0},
            tools=[],
            sampling={},
            proposal={"kind": "finish", "note": "one and done"},
        )
        
        # Tape mode exhaustion
        player_tape = CassettePlayer(cassette, match_mode="tape")
        res1 = player_tape.propose({"turn": 0}, [], {})
        self.assertTrue(res1.ok)
        res2 = player_tape.propose({"turn": 1}, [], {})
        self.assertFalse(res2.ok)
        self.assertEqual(res2.error.kind, "instrument_error")
        self.assertIn("exhausted", res2.error.message.lower())

        # Digest mode unknown request
        player_digest = CassettePlayer(cassette, match_mode="digest")
        unknown = player_digest.propose({"turn": 99, "unknown": "prompt"}, [], {})
        self.assertFalse(unknown.ok)
        self.assertEqual(unknown.error.kind, "instrument_error")
        self.assertIn("no recorded cassette interaction", unknown.error.message.lower())


if __name__ == "__main__":
    unittest.main()
