"""Shared substitution contract for every active ModelPort implementation.

Owning contract: REQ-PORT-002 / TEST-PORT-002, ICD §4 ModelProvider, CT-33.
"""

from __future__ import annotations

import socket
import unittest
from typing import Callable
from unittest.mock import patch

from vanguard.packages.adapters.models import Cassette, CassettePlayer, FakeModel
from vanguard.packages.ports.event_store import Result
from vanguard.packages.ports.model import ModelPort


CONTEXT = {"blocks": [{"label": "L5", "content": "say hello"}]}
TOOLS = [{"name": "read", "schema": {"type": "object"}}]
SAMPLING = {"temperature": 0.0, "maxTokens": 32}
PROPOSAL = {
    "text": "I will read the file",
    "toolCalls": [{"id": "call_1", "name": "read", "arguments": {"path": "a.txt"}}],
}


def _cassette_model() -> ModelPort:
    cassette = Cassette()
    cassette.add_record(CONTEXT, TOOLS, SAMPLING, PROPOSAL)
    return CassettePlayer(cassette, match_mode="tape")


def _scripted_model() -> ModelPort:
    return FakeModel([PROPOSAL])


def _rate_limit_model() -> ModelPort:
    return FakeModel(
        [
            Result.fail(
                kind="instrument_error",
                message="provider returned HTTP 429",
                retryable=True,
            )
        ]
    )


class ModelPortContract(unittest.TestCase):
    """The same success and failure behaviour runs against cassette and scripted fakes."""

    def test_all_implementations_satisfy_contract(self) -> None:
        factories: tuple[tuple[str, Callable[[], ModelPort]], ...] = (
            ("cassette", _cassette_model),
            ("scripted", _scripted_model),
        )
        for name, factory in factories:
            with self.subTest(implementation=name):
                port = factory()
                result = port.propose(CONTEXT, TOOLS, SAMPLING)
                self.assertTrue(result.ok)
                self.assertIsNone(result.error)
                self.assertEqual(result.value, PROPOSAL)
                self.assertEqual(result.value["toolCalls"][0]["id"], "call_1")

                exhausted = port.propose(CONTEXT, TOOLS, SAMPLING)
                self.assertFalse(exhausted.ok)
                self.assertIsNone(exhausted.value)
                self.assertIsNotNone(exhausted.error)
                self.assertEqual(exhausted.error.kind, "instrument_error")
                self.assertNotEqual(exhausted.error.kind, "task_failure")

    def test_rate_limit_fixture_is_instrument_error(self) -> None:
        result = _rate_limit_model().propose(CONTEXT, TOOLS, SAMPLING)
        self.assertFalse(result.ok)
        self.assertIsNone(result.value)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error.kind, "instrument_error")
        self.assertTrue(result.error.retryable)
        self.assertNotEqual(result.error.kind, "task_failure")
        self.assertNotIn("task failure", result.error.message.lower())

    def test_fake_does_not_touch_the_network(self) -> None:
        with patch.object(socket, "socket", side_effect=AssertionError("no network")):
            result = _cassette_model().propose(CONTEXT, TOOLS, SAMPLING)
        self.assertTrue(result.ok)
        self.assertEqual(result.value, PROPOSAL)


if __name__ == "__main__":
    unittest.main()
