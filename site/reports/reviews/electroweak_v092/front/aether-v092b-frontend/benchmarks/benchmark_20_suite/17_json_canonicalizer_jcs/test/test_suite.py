import unittest
from src.jcs import canonicalize, canonical_digest

class TestJCS(unittest.TestCase):
    def test_canonical_ordering_and_digest(self):
        obj = {"z": 100, "a": [3, 2, 1], "m": {"b": True, "a": None}}
        canon_bytes = canonicalize(obj)
        expected = b'{"a":[3,2,1],"m":{"a":null,"b":true},"z":100}'
        self.assertEqual(canon_bytes, expected)

        digest = canonical_digest(obj)
        self.assertEqual(len(digest), 64)

if __name__ == "__main__":
    unittest.main()
