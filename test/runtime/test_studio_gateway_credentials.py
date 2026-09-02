"""Credential status, provider probe, and launch-payload fidelity.

These cover the three defects behind "I saved the key and nothing happened":
the pane had no authority to ask about the key, "Test Connection" made no
call, and a launch dropped the operator's model and profile on the floor.
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from vanguard.packages.adapters.models.credential_probe import (
    credential_status,
    probe_provider,
)
from vanguard.packages.runtime.service.inbox import ServiceInboxStore
from vanguard.packages.runtime.service.service import RuntimeService
from vanguard.packages.runtime.service.studio_gateway import create_gateway


def _write_env(root: Path, body: str, mode: int = 0o600) -> Path:
    env_path = root / ".env"
    env_path.write_text(body, encoding="utf-8")
    env_path.chmod(mode)
    return env_path


class TestCredentialStatus(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tempdir.name)

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def test_missing_env_file_reports_missing_with_a_remedy(self) -> None:
        status = credential_status(self.root)
        self.assertEqual(status["state"], "MISSING")
        self.assertEqual(status["keyRef"], "OPENROUTER_API_KEY")
        self.assertIn("chmod 600", status["remedy"])

    def test_permissive_mode_is_denied_not_missing(self) -> None:
        """The operator's actual situation: a key present but unreadable.

        Collapsing this into MISSING sends them to add a key they already
        added.
        """
        _write_env(self.root, "OPENROUTER_API_KEY=sk-live-value\n", mode=0o644)
        status = credential_status(self.root)
        self.assertEqual(status["state"], "DENIED")
        self.assertIn("permissive", status["detail"])

    def test_empty_value_is_invalid(self) -> None:
        _write_env(self.root, "OPENROUTER_API_KEY=\n")
        status = credential_status(self.root)
        self.assertEqual(status["state"], "INVALID")

    def test_well_formed_key_is_configured(self) -> None:
        _write_env(self.root, "OPENROUTER_API_KEY=sk-or-v1-testvalue\n")
        status = credential_status(self.root)
        self.assertEqual(status["state"], "CONFIGURED")
        self.assertEqual(status["remedy"], "")

    def test_status_never_carries_the_secret(self) -> None:
        secret = "sk-or-v1-do-not-leak-me"
        _write_env(self.root, f"OPENROUTER_API_KEY={secret}\n")
        self.assertNotIn(secret, json.dumps(credential_status(self.root)))


class TestProviderProbe(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tempdir.name)
        _write_env(self.root, "OPENROUTER_API_KEY=sk-or-v1-testvalue\n")

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def _probe(self, status_code: int, body: bytes = b"{}"):
        captured: dict[str, object] = {}

        def transport(url, headers, payload, timeout):
            captured["url"] = url
            captured["headers"] = headers
            captured["payload"] = json.loads(payload.decode("utf-8"))
            return status_code, {}, body

        return probe_provider(self.root, transport=transport), captured

    def test_probe_requests_exactly_one_token(self) -> None:
        """A liveness check must not be able to run up a bill."""
        _result, captured = self._probe(200)
        self.assertEqual(captured["payload"]["max_tokens"], 1)

    def test_probe_sends_the_key_as_a_bearer_token(self) -> None:
        _result, captured = self._probe(200)
        self.assertEqual(captured["headers"]["Authorization"], "Bearer sk-or-v1-testvalue")

    def test_success(self) -> None:
        result, _ = self._probe(200)
        self.assertTrue(result["ok"])
        self.assertEqual(result["state"], "CONFIGURED")

    def test_rejected_key_is_invalid_not_unreachable(self) -> None:
        result, _ = self._probe(401)
        self.assertFalse(result["ok"])
        self.assertEqual(result["state"], "INVALID")

    def test_no_credit_is_distinguished_from_a_bad_key(self) -> None:
        result, _ = self._probe(402)
        self.assertEqual(result["state"], "EXHAUSTED")

    def test_rate_limited(self) -> None:
        result, _ = self._probe(429)
        self.assertEqual(result["state"], "RATE_LIMITED")

    def test_provider_error_message_is_surfaced(self) -> None:
        body = json.dumps({"error": {"message": "no such model"}}).encode("utf-8")
        result, _ = self._probe(404, body)
        self.assertIn("no such model", result["detail"])

    def test_transport_failure_is_reported_not_raised(self) -> None:
        def transport(url, headers, payload, timeout):
            raise OSError("network unreachable")

        result = probe_provider(self.root, transport=transport)
        self.assertFalse(result["ok"])
        self.assertEqual(result["state"], "UNREACHABLE")

    def test_probe_does_not_call_the_provider_without_a_usable_key(self) -> None:
        """No key means no request. A 401 costs nothing but tells you less."""
        (self.root / ".env").unlink()
        calls: list[str] = []

        def transport(url, headers, payload, timeout):
            calls.append(url)
            return 200, {}, b"{}"

        result = probe_provider(self.root, transport=transport)
        self.assertEqual(calls, [])
        self.assertEqual(result["state"], "MISSING")


class TestGatewayCredentialRoutes(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self._tempdir.name)
        self.workspace = self.temp_path / "workspace"
        self.workspace.mkdir(parents=True)
        self.inbox = ServiceInboxStore(self.temp_path / "service.db")
        self.service = RuntimeService(self.inbox)
        self.server = create_gateway(
            host="127.0.0.1", port=0, workspace_root=self.workspace, service=self.service
        )
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        time.sleep(0.05)

    def tearDown(self) -> None:
        self.server.is_running = False
        self.server.shutdown()
        self.server.server_close()
        self._tempdir.cleanup()

    def _get(self, path: str):
        with urllib.request.urlopen(f"{self.base_url}{path}", timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def test_credentials_route_reports_missing_key(self) -> None:
        body = self._get("/api/credentials")
        self.assertEqual(body["state"], "MISSING")
        self.assertEqual(body["keyRef"], "OPENROUTER_API_KEY")

    def test_credentials_route_reports_a_configured_key(self) -> None:
        _write_env(self.workspace, "OPENROUTER_API_KEY=sk-or-v1-testvalue\n")
        body = self._get("/api/credentials")
        self.assertEqual(body["state"], "CONFIGURED")

    def test_credentials_route_never_returns_the_secret(self) -> None:
        secret = "sk-or-v1-never-in-a-response"
        _write_env(self.workspace, f"OPENROUTER_API_KEY={secret}\n")
        with urllib.request.urlopen(f"{self.base_url}/api/credentials", timeout=5) as response:
            self.assertNotIn(secret, response.read().decode("utf-8"))


class TestLaunchPayloadFidelity(unittest.TestCase):
    """The launch route is a transport; it must not lose the operator's intent."""

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self._tempdir.name)
        self.workspace = self.temp_path / "workspace"
        (self.workspace / "packs" / "code-default").mkdir(parents=True)
        (self.workspace / "packs" / "code-default" / "harness.yaml").write_text(
            "id: test\n", encoding="utf-8"
        )

        self.captured: list[dict] = []
        outer = self

        class RecordingService(RuntimeService):
            def execute_command(self, frame):
                outer.captured.append(dict(frame["command"]["payload"]))
                return {
                    "version": "vg.4",
                    "frameType": "receipt",
                    "receipt": {"status": "completed", "result": {"runId": "r1"}},
                }

        self.inbox = ServiceInboxStore(self.temp_path / "service.db")
        self.service = RecordingService(self.inbox)
        self.server = create_gateway(
            host="127.0.0.1", port=0, workspace_root=self.workspace, service=self.service
        )
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        time.sleep(0.05)

    def tearDown(self) -> None:
        self.server.is_running = False
        self.server.shutdown()
        self.server.server_close()
        self._tempdir.cleanup()

    def _launch(self, payload: dict) -> dict:
        request = urllib.request.Request(
            f"{self.base_url}/api/runs/launch",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            response.read()
        return self.captured[-1]

    def test_model_and_profile_reach_the_service(self) -> None:
        sent = self._launch(
            {
                "brief": "do a thing",
                "profileId": "code-default",
                "model": "deepseek/deepseek-v4-flash-0731",
                "episodeId": "ep-1",
            }
        )
        self.assertEqual(sent["model"], "deepseek/deepseek-v4-flash-0731")
        self.assertEqual(sent["profileId"], "code-default")
        self.assertEqual(sent["episodeId"], "ep-1")

    def test_manifest_resolves_to_a_real_pack_file(self) -> None:
        """`_cmd_StartRun` only spawns a worker for a manifest that exists."""
        sent = self._launch({"brief": "do a thing", "profileId": "code-default"})
        self.assertTrue(Path(sent["manifestPath"]).is_file(), sent["manifestPath"])

    def test_bare_harness_yaml_default_is_not_propagated(self) -> None:
        sent = self._launch({"brief": "do a thing", "manifestPath": "harness.yaml"})
        self.assertNotEqual(sent["manifestPath"], "harness.yaml")
        self.assertTrue(Path(sent["manifestPath"]).is_file())

    def test_explicit_relative_manifest_resolves_against_the_workspace(self) -> None:
        sent = self._launch(
            {"brief": "b", "manifestPath": "packs/code-default/harness.yaml"}
        )
        self.assertEqual(
            Path(sent["manifestPath"]),
            self.workspace / "packs" / "code-default" / "harness.yaml",
        )


if __name__ == "__main__":
    unittest.main()
