"""T-11 / T-12 / T-13: resume episode_id, σ outside L3, packet identity."""

from __future__ import annotations

import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from test.agency.doubles import ScriptedModel, finish
from test.runtime.test_harness_session import FakeClock, FakeEnvironment, _ports
from vanguard.packages.agency.context import (
    ContextCompiler,
    ContextPacketError,
    Layer,
    build_context_packet,
    validate_resume_identity,
)
from vanguard.packages.runtime.app_service import ApplicationService, episode_id_from_events
from vanguard.packages.runtime.compose import TaskContext
from vanguard.packages.runtime.root import HarnessSession, Runtime
from vanguard.packages.runtime.task_state import fold_task_state
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.domain.ledger.events import WRITABLE_KINDS


def _event(kind: str, *, episode_id: str = "ep-original", **payload: object) -> SimpleNamespace:
    body = {"kind": kind, **payload}
    return SimpleNamespace(
        kind=kind, mhf_kind=kind, payload=body, episode_id=episode_id, run_id="run-1",
    )


class TestResumeIdentity(unittest.TestCase):
    def _session(self, model: object, *, episode_id: str = "ep-t107") -> HarnessSession:
        harness = Runtime.compose("vg-code-default", episode_id=episode_id)
        return HarnessSession(
            harness,
            _ports(model, FakeEnvironment()),
            TaskContext(
                brief="durability", repo_path=Path("/workspace"),
                run_id=f"run-{episode_id}", episode_id=episode_id,
                principal="agent-1", max_turns=4,
            ),
        )

    def test_selection_append_failure_makes_zero_model_calls(self) -> None:
        """T-107: selection evidence is a write-before-inference gate."""
        model = ScriptedModel([finish()])
        session = self._session(model, episode_id="ep-selection-failure")
        original = session.ledger.emit_kind

        def emit(kind: str, **kwargs: object):
            if kind == "ContextSelectionRecorded":
                raise OSError("selection store unavailable")
            return original(kind, **kwargs)

        with patch("vanguard.packages.runtime.session.WRITABLE_KINDS",
                   frozenset({"ContextSelectionRecorded"})), \
             patch.object(session.ledger, "emit_kind", side_effect=emit):
            session.run()
        self.assertEqual(model.calls, [])

    def test_selection_is_durable_before_the_first_model_call(self) -> None:
        """The selection fact carries the identity and final compiler count."""
        model = ScriptedModel([finish()])
        session = self._session(model, episode_id="ep-selection-recorded")
        kinds = WRITABLE_KINDS | frozenset({"ContextSelectionRecorded"})
        with patch("vanguard.packages.runtime.session.WRITABLE_KINDS", kinds), \
             patch("vanguard.packages.runtime.ledger_emitter.WRITABLE_KINDS", kinds):
            session.run()
        events = session.ports.store.read(EventRange(episode_id=session.task.episode_id))
        selection = next(
            item.payload for item in events.value
            if item.payload.get("kind") == "ContextSelectionRecorded")
        self.assertEqual(len(model.calls), 1)
        self.assertTrue(selection["prefixDigest"])
        self.assertTrue(selection["requestDigest"])
        self.assertGreaterEqual(selection["serializedTokens"], 0)
        self.assertEqual(selection["cursor"], 0)
        self.assertEqual(selection["behaviorIdentity"]["compositionDigest"],
                         session.harness.composition_digest)

    def test_recovery_append_failure_blocks_next_inference(self) -> None:
        """T-107: an unpersisted retry decision cannot lead to another call."""
        model = ScriptedModel(["not a proposal", finish()])
        session = self._session(model, episode_id="ep-recovery-failure")
        original = session.ledger.emit

        def emit(event: object):
            if getattr(event, "kind", "") == "EpisodeStateChanged":
                return None
            return original(event)

        with patch.object(session.ledger, "emit", side_effect=emit):
            session.run()
        self.assertEqual(len(model.calls), 1)

    def test_resume_rejects_changed_behavior_identity_before_model_call(self) -> None:
        model = ScriptedModel([finish()])
        harness = Runtime.compose("vg-code-default", episode_id="ep-identity-reject")
        session = HarnessSession(
            harness,
            _ports(model, FakeEnvironment()),
            TaskContext(
                brief="durability", repo_path=Path("/workspace"),
                run_id="run-identity-reject", episode_id="ep-identity-reject",
                principal="agent-1", max_turns=4,
                resume_state={
                    "recoveryState": {},
                    "selectionPolicyIdentity": {
                        "behaviorIdentity": {"compositionDigest": "foreign"},
                    },
                },
            ),
        )
        with self.assertRaises(ContextPacketError):
            session.run()
        self.assertEqual(model.calls, [])

    def test_episode_id_from_events_preserves_ledger_identity(self) -> None:
        events = [
            _event("EpisodeStarted", brief="continue", episodeId="ep-original"),
            _event("ProposalProduced", action="fs.read"),
        ]
        self.assertEqual(episode_id_from_events(events, run_id="run-1"), "ep-original")
        self.assertNotEqual(episode_id_from_events(events, run_id="run-1"), "episode-run-1")

    def test_resume_task_uses_original_episode_id(self) -> None:
        events = [
            _event("EpisodeStarted", brief="continue the work", episodeId="ep-original",
                   maxTurns=8, interactive=True, harness="vg-code-default"),
        ]
        captured: dict[str, object] = {}

        class _Exec:
            terminal = SimpleNamespace(value="completed")
            telemetry = SimpleNamespace(turns=0)
            run_digest = "sha256:" + "c" * 64
            detail = "mocked"
            events = ()

        def _fake_execute(manifest, task, **kwargs):
            captured["episode_id"] = task.episode_id
            captured["resume_state"] = task.resume_state
            result = _Exec()
            result.events = events
            return result

        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            state = workspace / ".vanguard"
            state.mkdir()
            (state / "events.sqlite3").write_bytes(b"")
            app = ApplicationService(workspace=workspace)
            with patch.object(type(app), "_manifest_path_for_resume", return_value=Path("x")), \
                 patch("vanguard.packages.runtime.app_service.SqliteEventStore") as store_cls, \
                 patch("vanguard.packages.runtime.app_service.Runtime.execute_profiled", side_effect=_fake_execute):
                store = store_cls.return_value
                store.read.return_value = SimpleNamespace(ok=True, value=events)
                result = app.resume(run_id="run-1", model=object(), state_dir=state)
        self.assertEqual(captured["episode_id"], "ep-original")
        self.assertEqual(result.episode_id, "ep-original")

    def test_sigma_is_not_dumped_into_frozen_l3(self) -> None:
        harness = Runtime.compose("vg-code-default", episode_id="ep-session-1")
        sigma = fold_task_state(
            [_event("EpisodeStarted", brief="make the suite green"),
             _event("DeadEndRecorded", attempt="wrong file", reason="no match")],
            objective="make the suite green",
        ).to_canonical_dict()
        task = TaskContext(
            brief="make the suite green",
            repo_path=Path("/workspace"),
            run_id="run-session-1",
            episode_id="ep-session-1",
            principal="agent-1",
            max_turns=4,
            resume_state=sigma,
        )
        session = HarnessSession(
            harness, _ports(ScriptedModel([finish()]), FakeEnvironment()), task,
        )
        compiler: ContextCompiler = session.operator._compiler
        prefix = "\n".join(block.text for block in compiler._prefix)
        self.assertNotIn("Durable Coding Task State", prefix)
        self.assertNotIn("wrong file", prefix)
        _, compiled = session.operator._assembler.assemble({}, 0)
        l4 = "\n".join(block.text for block in compiled.layer_blocks(Layer.TASK))
        self.assertIn("wrong file", l4)
        prefix_before = compiled.prefix_digest
        session.operator._assembler.set_task_state({**sigma, "nextAction": "write"})
        _, compiled_after = session.operator._assembler.assemble({}, 1)
        self.assertEqual(compiled_after.prefix_digest, prefix_before)
        self.assertNotEqual(compiled_after.digest, compiled.digest)

    def test_validate_resume_identity_fails_on_policy_mismatch(self) -> None:
        packet = build_context_packet(
            task_digest="sha256:t",
            repository_snapshot="sha256:r",
            provider="index",
            provider_version="1",
            query_digest="sha256:q",
            budget_tokens=100,
            repository_identity="sha256:repo",
            selection_policy_identity={"policy": "stable"},
            index_snapshot_digest="sha256:idx",
        )
        validate_resume_identity(
            packet,
            repository_identity="sha256:repo",
            index_snapshot_digest="sha256:idx",
            selection_policy_identity={"policy": "stable"},
        )
        with self.assertRaises(ContextPacketError):
            validate_resume_identity(
                packet,
                repository_identity="sha256:repo",
                index_snapshot_digest="sha256:idx",
                selection_policy_identity={"policy": "other"},
            )


if __name__ == "__main__":
    unittest.main()
