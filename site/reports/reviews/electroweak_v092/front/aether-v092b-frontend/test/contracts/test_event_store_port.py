"""Shared substitution contract for every active EventStorePort implementation."""

from __future__ import annotations

import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from test.contracts.t3_ledger import _make_envelope
from vanguard.packages.adapters.stores import InMemoryEventStore, SqliteEventStore
from vanguard.packages.ports.event_store import EventRange, EventStorePort


@contextmanager
def _memory_store() -> Iterator[EventStorePort]:
    yield InMemoryEventStore()


@contextmanager
def _sqlite_store() -> Iterator[EventStorePort]:
    with tempfile.TemporaryDirectory() as directory:
        store = SqliteEventStore(Path(directory) / "events.sqlite3")
        try:
            yield store
        finally:
            store.close()


class EventStorePortContract(unittest.TestCase):
    """The same success and failure behaviour runs against fake and real."""

    def test_all_implementations_satisfy_contract(self) -> None:
        for name, factory in (("memory", _memory_store), ("sqlite", _sqlite_store)):
            with self.subTest(implementation=name), factory() as store:
                first = _make_envelope(
                    "0",
                    "EpisodeStarted",
                    {"taskSpec": {"name": "port-contract"}},
                    event_id="018faaaa-1111-7000-8000-000000000001",
                )
                second = _make_envelope(
                    "1",
                    "EpisodeCompleted",
                    {"outcome": "resolved"},
                    event_id="018faaaa-1111-7000-8000-000000000002",
                )

                appended = store.append([first, second])
                self.assertTrue(appended.ok)
                self.assertIsNone(appended.error)
                self.assertEqual([event.seq for event in store.read(EventRange()).value or ()], ["0", "1"])
                self.assertTrue((store.digest().value or "").startswith("sha256:"))

                conflict = store.append([second])
                self.assertFalse(conflict.ok)
                self.assertIsNone(conflict.value)
                self.assertIsNotNone(conflict.error)
                self.assertEqual(conflict.error.kind, "conflict")
                self.assertEqual(store.count(), 2)


if __name__ == "__main__":
    unittest.main()
