"""`BlobStorePort` + `IndexPort`, two implementations each (`S10-A-03`, `T10.2`).

These are the seams every future memory or retrieval feature needs, and their
absence is why `O-02` had nowhere to land. One implementation per port is an
interface nobody has tested against anything, so both are exercised through the
same assertions here.

The index is an **observation** source. It answers what is in the workspace; it
proposes nothing and ranks nothing on the agent's behalf. A retrieval component
that decided what the agent should look at next would be a second policy
wearing the word "index" (`A-05`, `AT-01`) — asserted below, not assumed.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.stores.blob_store import (
    FileBlobStore,
    InMemoryBlobStore,
)
from vanguard.packages.adapters.stores.repo_index import (
    FileRepoIndex,
    InMemoryRepoIndex,
)
from vanguard.packages.ports.blob_store import BlobStorePort
from vanguard.packages.ports.index import IndexPort, Symbol

SOURCE = '''"""A module."""


class Ledger:
    def total(self, rows):
        return sum(rows)


def parse(text):
    return text.split()
'''


class BothBlobStoresSatisfyThePort(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.stores = (InMemoryBlobStore(), FileBlobStore(Path(self._tmp.name) / "blobs"))

    def test_each_implementation_satisfies_the_protocol(self) -> None:
        for store in self.stores:
            with self.subTest(store=type(store).__name__):
                self.assertIsInstance(store, BlobStorePort)

    def test_a_blob_round_trips(self) -> None:
        for store in self.stores:
            with self.subTest(store=type(store).__name__):
                put = store.put(b"hello evidence")
                self.assertTrue(put.ok)
                self.assertEqual(store.get(put.value).value, b"hello evidence")

    def test_the_address_is_the_digest_of_the_content(self) -> None:
        """A store that trusts a caller's digest is one whose addresses lie."""

        import hashlib

        expected = "sha256:" + hashlib.sha256(b"payload").hexdigest()
        for store in self.stores:
            with self.subTest(store=type(store).__name__):
                self.assertEqual(store.put(b"payload").value, expected)

    def test_identical_bytes_get_one_address(self) -> None:
        for store in self.stores:
            with self.subTest(store=type(store).__name__):
                self.assertEqual(store.put(b"same").value, store.put(b"same").value)

    def test_different_bytes_get_different_addresses(self) -> None:
        for store in self.stores:
            with self.subTest(store=type(store).__name__):
                self.assertNotEqual(store.put(b"a").value, store.put(b"b").value)

    def test_an_absent_blob_is_a_typed_failure_not_an_exception(self) -> None:
        missing = "sha256:" + "0" * 64
        for store in self.stores:
            with self.subTest(store=type(store).__name__):
                result = store.get(missing)
                self.assertFalse(result.ok)
                self.assertEqual(result.error.kind, "not_found")
                self.assertFalse(store.has(missing))

    def test_a_malformed_digest_never_raises(self) -> None:
        for store in self.stores:
            with self.subTest(store=type(store).__name__):
                self.assertFalse(store.has("../../etc/passwd"))
                self.assertFalse(store.get("not-a-digest").ok)

    def test_the_file_store_survives_a_new_instance(self) -> None:
        """The real one is real: bytes outlive the object that wrote them."""

        root = Path(self._tmp.name) / "durable"
        digest = FileBlobStore(root).put(b"persisted").value
        self.assertEqual(FileBlobStore(root).get(digest).value, b"persisted")


class BothIndexesSatisfyThePort(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / "pkg").mkdir()
        (self.root / "pkg" / "ledger.py").write_text(SOURCE)
        (self.root / "README.md").write_text("# notes\n")

        real = FileRepoIndex()
        real.index(str(self.root))
        self.indexes = (
            InMemoryRepoIndex({"pkg/ledger.py": SOURCE, "README.md": "# notes\n"}),
            real,
        )

    def test_each_implementation_satisfies_the_protocol(self) -> None:
        for index in self.indexes:
            with self.subTest(index=type(index).__name__):
                self.assertIsInstance(index, IndexPort)

    def test_files_are_listed_workspace_relative_and_sorted(self) -> None:
        for index in self.indexes:
            with self.subTest(index=type(index).__name__):
                files = index.files().value
                self.assertIn("pkg/ledger.py", files)
                self.assertEqual(list(files), sorted(files))

    def test_a_prefix_filters_the_listing(self) -> None:
        for index in self.indexes:
            with self.subTest(index=type(index).__name__):
                self.assertEqual(list(index.files(prefix="pkg/").value),
                                 ["pkg/ledger.py"])

    def test_definitions_are_found_with_their_line(self) -> None:
        for index in self.indexes:
            with self.subTest(index=type(index).__name__):
                found = index.symbols(name="total").value
                self.assertEqual(len(found), 1)
                self.assertEqual(found[0].kind, "function")
                self.assertEqual(found[0].path, "pkg/ledger.py")
                self.assertEqual(found[0].line, 5)

    def test_classes_and_functions_are_distinguished(self) -> None:
        for index in self.indexes:
            with self.subTest(index=type(index).__name__):
                kinds = {s.name: s.kind for s in index.symbols().value}
                self.assertEqual(kinds.get("Ledger"), "class")
                self.assertEqual(kinds.get("parse"), "function")

    def test_no_match_is_an_empty_result_not_a_failure(self) -> None:
        for index in self.indexes:
            with self.subTest(index=type(index).__name__):
                result = index.symbols(name="nonexistent")
                self.assertTrue(result.ok)
                self.assertEqual(list(result.value), [])

    def test_symbols_are_values_not_handles(self) -> None:
        """Nothing can reach back through a symbol into the indexer."""

        for index in self.indexes:
            with self.subTest(index=type(index).__name__):
                symbol = index.symbols(name="parse").value[0]
                self.assertIsInstance(symbol, Symbol)
                with self.assertRaises(Exception):
                    symbol.name = "renamed"  # type: ignore[misc]

    def test_the_index_is_observation_only(self) -> None:
        """`A-05`: it answers questions; it never proposes or ranks."""

        for index in self.indexes:
            with self.subTest(index=type(index).__name__):
                for forbidden in ("propose", "rank", "select", "suggest",
                                  "dispatch", "execute"):
                    self.assertFalse(hasattr(index, forbidden),
                                     f"{forbidden!r} would make the index a second policy")

    def test_an_unreadable_root_is_a_typed_failure(self) -> None:
        result = FileRepoIndex().index(str(self.root / "does-not-exist"))
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "not_found")

    def test_querying_before_indexing_fails_rather_than_lying(self) -> None:
        """An empty listing and an unbuilt index are different facts."""

        fresh = FileRepoIndex()
        self.assertFalse(fresh.files().ok)
        self.assertFalse(fresh.symbols().ok)

    def test_a_binary_file_does_not_stop_the_walk(self) -> None:
        (self.root / "pkg" / "blob.py").write_bytes(b"\xff\xfe\x00binary")
        index = FileRepoIndex()
        result = index.index(str(self.root))
        self.assertTrue(result.ok)
        self.assertIn("pkg/ledger.py", index.files().value)


if __name__ == "__main__":
    unittest.main()
