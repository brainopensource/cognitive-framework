"""REQ-PORT-006 / TEST-PORT-006 — OpenRouter ModelPort adapter.

Cassette tests must pass without network. The optional live call is skipped
when `OPENROUTER_API_KEY` is unset. Trust-spine sources must not import this
adapter (`REQ-TRUST-001`).
"""

from __future__ import annotations

import ast
import os
import socket
import unittest
from pathlib import Path
from unittest.mock import patch

from vanguard.packages.adapters.models.cassette import Cassette
from vanguard.packages.adapters.models.openrouter import OpenRouterModel
from vanguard.packages.ports.event_store import Result


CONTEXT = {"blocks": [{"label": "L5", "content": "say hello"}]}
TOOLS = [{"name": "read", "schema": {"type": "object"}}]
SAMPLING = {"temperature": 0.0, "maxTokens": 8}
PROPOSAL = {"text": "hello from cassette", "toolCalls": []}
SECRET = "sk-test-secret-do-not-leak"


def _boom_transport(url: str, headers: dict[str, str], body: bytes) -> tuple[int, bytes]:
    raise AssertionError(f"network forbidden: {url}")


def _status_transport(status: int, payload: bytes):
    def transport(url: str, headers: dict[str, str], body: bytes) -> tuple[int, bytes]:
        del url, headers
        encoded = body.decode("utf-8", "replace")
        assert SECRET not in encoded
        return status, payload

    return transport


def _trust_openrouter_imports() -> list[str]:
    root = Path("test/trust")
    if not root.exists():
        return []
    offenders: list[str] = []
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            specs: list[str] = []
            if isinstance(node, ast.Import):
                specs.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    specs.append(node.module)
                specs.extend(alias.name for alias in node.names)
            for spec in specs:
                lowered = spec.lower()
                if "openrouter" in lowered:
                    offenders.append(f"{path.as_posix()}:{node.lineno}: {spec}")
    return offenders


class OpenRouterModelContract(unittest.TestCase):
    def test_cassette_replay_does_not_touch_the_network(self) -> None:
        cassette = Cassette()
        cassette.add_record(CONTEXT, TOOLS, SAMPLING, PROPOSAL)
        port = OpenRouterModel(cassette=cassette, mode="replay", transport=_boom_transport)
        with patch.object(socket, "socket", side_effect=AssertionError("no network")):
            result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertTrue(result.ok)
        self.assertEqual(result.value, PROPOSAL)

    def test_http_rate_limit_is_instrument_error_without_secret(self) -> None:
        port = OpenRouterModel(
            api_key_ref="OPENROUTER_API_KEY",
            transport=_status_transport(429, b'{"error":{"message":"rate limit"}}'),
            environ={"OPENROUTER_API_KEY": SECRET},
        )
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertFalse(result.ok)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error.kind, "instrument_error")
        self.assertTrue(result.error.retryable)
        self.assertNotIn(SECRET, result.error.message)
        dumped = Result.fail(
            result.error.kind, result.error.message, result.error.retryable
        )
        self.assertNotIn(SECRET, str(dumped))

    def test_adapter_holds_a_secret_reference_not_the_value(self) -> None:
        port = OpenRouterModel(
            api_key_ref="OPENROUTER_API_KEY",
            transport=_boom_transport,
            environ={"OPENROUTER_API_KEY": SECRET},
        )
        self.assertEqual(port.api_key_ref, "OPENROUTER_API_KEY")
        self.assertFalse(hasattr(port, "api_key"))
        self.assertNotIn(SECRET, vars(port).values())

    def test_trust_spine_sources_do_not_import_openrouter(self) -> None:
        self.assertEqual(_trust_openrouter_imports(), [])

    @unittest.skipUnless(
        os.environ.get("OPENROUTER_API_KEY"),
        "live OpenRouter skipped: key unset",
    )
    def test_optional_live_chat_completion(self) -> None:
        port = OpenRouterModel()
        result = port.propose(CONTEXT, TOOLS, SAMPLING)
        self.assertTrue(
            result.ok or (result.error is not None and result.error.kind == "instrument_error")
        )
        if result.error is not None:
            self.assertNotIn(os.environ["OPENROUTER_API_KEY"], result.error.message)


if __name__ == "__main__":
    unittest.main()
