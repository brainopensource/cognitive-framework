"""LAM (LLM API Mock) — stateless OpenAI-compatible chat completions.

Owning idea: tools/002_LLM_API_MOCK. A harness CI accelerator that replays
recorded agentic coding cascades (system + tools + tool observations) in
milliseconds, with the same JSON shape OpenRouter would return.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAM = ROOT / "tools" / "002_LLM_API_MOCK"


class LamImport(unittest.TestCase):
    def test_engine_module_exists(self) -> None:
        self.assertTrue((LAM / "engine.py").is_file(), "tools/002_LLM_API_MOCK/engine.py must exist")


class StatelessTurnAdvance(unittest.TestCase):
    def setUp(self) -> None:
        import sys

        sys.path.insert(0, str(LAM))
        from engine import LamEngine

        self.engine = LamEngine.from_directory(LAM / "scenarios")

    def test_tier1_calculator_turn0_calls_view_file(self) -> None:
        body = {
            "model": "lam/t1-calculator",
            "messages": [
                {"role": "system", "content": "You are OpenCode."},
                {
                    "role": "user",
                    "content": "Fix the bug in src/calculator.py where calculate_value(A, B) fails tests for formula (A + B) * B.",
                },
            ],
            "tools": [{"type": "function", "function": {"name": "view_file"}}],
        }
        result = self.engine.complete(body)
        message = result["choices"][0]["message"]
        self.assertEqual(result["choices"][0]["finish_reason"], "tool_calls")
        self.assertEqual(message["tool_calls"][0]["function"]["name"], "view_file")
        args = json.loads(message["tool_calls"][0]["function"]["arguments"])
        self.assertEqual(args["path"], "src/calculator.py")

    def test_tier1_advances_on_tool_observation_count_not_session_state(self) -> None:
        """Stateless: two independent engines with the same history must agree."""
        history = [
            {"role": "system", "content": "You are OpenCode."},
            {"role": "user", "content": "Fix the bug in src/calculator.py where calculate_value(A, B) fails tests for formula (A + B) * B."},
            {
                "role": "assistant",
                "content": "inspect",
                "tool_calls": [
                    {
                        "id": "call_view_001",
                        "type": "function",
                        "function": {"name": "view_file", "arguments": '{"path": "src/calculator.py"}'},
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call_view_001",
                "name": "view_file",
                "content": "def calculate_value(A, B):\n    return (A + B) + B\n",
            },
        ]
        import sys

        sys.path.insert(0, str(LAM))
        from engine import LamEngine

        a = LamEngine.from_directory(LAM / "scenarios")
        b = LamEngine.from_directory(LAM / "scenarios")
        first = a.complete({"model": "lam/t1-calculator", "messages": history})
        second = b.complete({"model": "lam/t1-calculator", "messages": history})
        self.assertEqual(first["choices"][0]["message"]["tool_calls"][0]["function"]["name"], "edit_file")
        self.assertEqual(
            first["choices"][0]["message"]["tool_calls"],
            second["choices"][0]["message"]["tool_calls"],
        )

    def test_tier1_stop_after_tests_pass(self) -> None:
        messages = [
            {"role": "system", "content": "You are OpenCode."},
            {"role": "user", "content": "Fix the bug in src/calculator.py where calculate_value(A, B) fails tests for formula (A + B) * B."},
            {"role": "assistant", "tool_calls": [{"id": "a", "type": "function", "function": {"name": "view_file", "arguments": "{}"}}]},
            {"role": "tool", "tool_call_id": "a", "content": "file"},
            {"role": "assistant", "tool_calls": [{"id": "b", "type": "function", "function": {"name": "edit_file", "arguments": "{}"}}]},
            {"role": "tool", "tool_call_id": "b", "content": "ok"},
            {"role": "user", "content": "Verification test runner output:\n$ pytest test_calculator.py\n3 passed"},
        ]
        result = self.engine.complete({"model": "lam/t1-calculator", "messages": messages})
        self.assertEqual(result["choices"][0]["finish_reason"], "stop")
        self.assertIn("usage", result)
        self.assertGreater(result["usage"]["total_tokens"], 0)

    def test_five_tiers_are_registered(self) -> None:
        ids = {scenario.id for scenario in self.engine.scenarios}
        self.assertTrue(any(s.startswith("t1-") for s in ids))
        self.assertTrue(any(s.startswith("t2-") for s in ids))
        self.assertTrue(any(s.startswith("t3-") for s in ids))
        self.assertTrue(any(s.startswith("t4-") for s in ids))
        self.assertTrue(any(s.startswith("t5-") for s in ids))

    def test_tier5_has_more_turns_than_tier1(self) -> None:
        max_t5 = max(len(s.turns) for s in self.engine.scenarios if s.id.startswith("t5-"))
        min_t1 = min(len(s.turns) for s in self.engine.scenarios if s.id.startswith("t1-"))
        self.assertGreater(max_t5, min_t1)

    def test_unknown_model_is_instrument_error_not_a_guess(self) -> None:
        with self.assertRaises(KeyError):
            self.engine.complete({"model": "lam/does-not-exist", "messages": []})


class ServerIntegrationAndEvidenceTests(unittest.TestCase):
    """Test unified LAM HTTP server, evidence labels, and release admission refusal."""

    def test_unified_server_openai_and_ollama_endpoints(self) -> None:
        import threading
        import urllib.request
        import sys
        sys.path.insert(0, str(LAM))
        from server import create_server

        server = create_server(host="127.0.0.1", port=8991, scenario_dir=LAM / "scenarios")
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        try:
            # 1. Health check
            req = urllib.request.Request("http://127.0.0.1:8991/health")
            with urllib.request.urlopen(req) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(data["status"], "ok")
                self.assertEqual(data["mode"], "replay")
                self.assertEqual(data["evidence_label"], "lam-replay")
                self.assertEqual(resp.headers.get("X-Evidence-Label"), "lam-replay")

            # 2. OpenAI wire (/v1/chat/completions)
            req_body = json.dumps({
                "model": "lam/t1-calculator",
                "messages": [{"role": "user", "content": "fix calculator"}],
            }).encode("utf-8")
            req = urllib.request.Request(
                "http://127.0.0.1:8991/v1/chat/completions",
                data=req_body,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req) as resp:
                self.assertEqual(resp.status, 200)
                self.assertEqual(resp.headers.get("X-Evidence-Label"), "lam-replay")
                data = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(data["choices"][0]["finish_reason"], "tool_calls")
                self.assertEqual(data["choices"][0]["message"]["tool_calls"][0]["function"]["name"], "view_file")

            # 3. Ollama wire (/api/chat)
            req_body_ollama = json.dumps({
                "model": "lam/t1-calculator",
                "messages": [{"role": "user", "content": "fix calculator"}],
            }).encode("utf-8")
            req = urllib.request.Request(
                "http://127.0.0.1:8991/api/chat",
                data=req_body_ollama,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req) as resp:
                self.assertEqual(resp.status, 200)
                self.assertEqual(resp.headers.get("X-Evidence-Label"), "lam-replay")
                data = json.loads(resp.read().decode("utf-8"))
                self.assertTrue(data.get("done"))
                self.assertIn("message", data)

            # 4. Unknown model return 404
            req_body_unknown = json.dumps({
                "model": "unknown-nonexistent-model",
                "messages": [{"role": "user", "content": "hello"}],
            }).encode("utf-8")
            req = urllib.request.Request(
                "http://127.0.0.1:8991/v1/chat/completions",
                data=req_body_unknown,
                headers={"Content-Type": "application/json"},
            )
            with self.assertRaises(urllib.error.HTTPError) as err:
                urllib.request.urlopen(req)
            self.assertEqual(err.exception.code, 404)

        finally:
            server.shutdown()
            server.server_close()

    def test_recorder_schema_and_proxy_usage(self) -> None:
        import sys
        import tempfile
        import sqlite3
        sys.path.insert(0, str(LAM))
        from recorder import MockRecorder

        with tempfile.NamedTemporaryFile(suffix=".sqlite") as tf:
            rec = MockRecorder(tf.name)
            rec.record_call(
                request_sha256="req123",
                scenario_key="test-key",
                tier=1,
                requested_turn=0,
                returned_turn=0,
                reply_sha256="rep123",
                evidence_label="ollama-live",
                tokens=100,
                prompt_tokens=60,
                completion_tokens=40,
                cost_usd=0.0015,
                millis=120,
            )
            with sqlite3.connect(tf.name) as conn:
                cur = conn.execute("SELECT evidence_label, tokens, prompt_tokens, completion_tokens, cost_usd FROM mock_calls")
                row = cur.fetchone()
                self.assertEqual(row[0], "ollama-live")
                self.assertEqual(row[1], 100)
                self.assertEqual(row[2], 60)
                self.assertEqual(row[3], 40)
                self.assertAlmostEqual(row[4], 0.0015)

    def test_select_model_lam_port(self) -> None:
        from vanguard.packages.runtime.model_selection import select_model, ModelUnavailable

        # Probe passes
        selected = select_model("lam", probe=lambda url: True, model_name="lam/t1-calculator")
        self.assertEqual(selected.port, "lam")
        self.assertEqual(selected.label, "lam:lam/t1-calculator")
        self.assertEqual(selected.model.provider, "lam")
        self.assertEqual(selected.model.mode, "replay")

        # Probe fails closed
        with self.assertRaises(ModelUnavailable):
            select_model("lam", probe=lambda url: False)

    def test_release_admission_refuses_lam_replay(self) -> None:
        from vanguard.packages.runtime.root import _validate_release_inputs, SessionPorts, TaskContext
        from vanguard.packages.domain.canonicalisation.digest import digest_of

        task_context = TaskContext(
            brief="Fix bug in calculator",
            repo_path="/tmp",
            run_id="run-1",
            episode_id="ep-1",
            preregistration={
                "api": "mhf.preregistration/1",
                "preregistration_digest": "",
                "task_digest": digest_of({"task": "Fix bug in calculator"}),
                "oracle_id": "eval-1",
                "oracle_digest": "dig-oracle",
                "evaluator_key_id": "key-1",
                "evaluator_public_key": "pk-1",
                "protocol": "jsonrpc-2.0",
                "subject_digest": "sub-1",
                "created_at": "2026-08-24T00:00:00Z",
                "metadata": {},
            },
        )
        pre = dict(task_context.preregistration)
        pre_id = {k: pre[k] for k in (
            "api", "task_digest", "oracle_id", "oracle_digest",
            "evaluator_key_id", "evaluator_public_key", "protocol",
            "subject_digest", "created_at", "metadata"
        )}
        pre["preregistration_digest"] = digest_of(pre_id)
        task_context = TaskContext(
            brief=task_context.brief,
            repo_path=task_context.repo_path,
            run_id=task_context.run_id,
            episode_id=task_context.episode_id,
            preregistration=pre,
        )

        class FakeLamModel:
            provider = "lam"
            mode = "replay"

        class DummyEnv:
            containment_report = type("Report", (), {"verified": True, "contained": True, "runtime": "bubblewrap-rootless"})()

        ports = SessionPorts(
            model=FakeLamModel(),
            environment=DummyEnv(),
            clock=None,
            store=None,
        )

        with self.assertRaises(ValueError) as caught:
            _validate_release_inputs(ports, task_context, pre, expected_oracle="eval-1")
        self.assertIn("live non-fake/non-cassette", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

