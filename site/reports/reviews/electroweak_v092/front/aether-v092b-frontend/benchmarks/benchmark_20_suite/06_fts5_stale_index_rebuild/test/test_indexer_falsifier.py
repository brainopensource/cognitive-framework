import unittest
from src.symbol_indexer import SymbolIndexer

class TestSymbolIndexer(unittest.TestCase):
    def test_delete_file_purges_fts_symbols(self):
        indexer = SymbolIndexer()
        indexer.index_file("kernel/dispatch.py", [
            {"name": "DispatchPipeline", "docstring": "Core 13-stage dispatch pipeline"}
        ])

        # Verify symbol found
        res = indexer.search("DispatchPipeline")
        self.assertEqual(len(res), 1)

        # Delete file
        indexer.delete_file("kernel/dispatch.py")

        # Falsifier Assertion: Search for deleted symbol must yield 0 results
        res_after = indexer.search("DispatchPipeline")
        self.assertEqual(
            len(res_after),
            0,
            f"FTS Zombie Hit: Deleted file symbols still present in search results: {res_after}"
        )

if __name__ == "__main__":
    unittest.main()
