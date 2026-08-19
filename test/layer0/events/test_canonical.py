from __future__ import annotations

import unittest

from layer0.events.canonical import canonicalise, digest_of
from layer0.events.envelope import EnvelopeFactory
from layer0.spi.types_gen import EventKind


class CanonicalTests(unittest.TestCase):
    def test_jcs_orders_keys(self) -> None:
        text = canonicalise({"b": 1, "a": 2})
        self.assertEqual(text, '{"a":2,"b":1}')

    def test_digest_is_stable(self) -> None:
        self.assertEqual(digest_of({"x": 1}), digest_of({"x": 1}))

    def test_hash_chain_links_prev_digest(self) -> None:
        factory = EnvelopeFactory()
        first = factory.emit(EventKind.RUN_STARTED, run_id="r", principal="p")
        second = factory.emit(EventKind.EPISODE_STARTED, run_id="r", principal="p")
        self.assertIsNone(first.prev_digest)
        self.assertEqual(second.prev_digest, first.digest)
        self.assertEqual(second.seq, first.seq + 1)
        self.assertTrue(second.digest.startswith("sha256:"))
        self.assertNotEqual(first.digest, second.digest)
