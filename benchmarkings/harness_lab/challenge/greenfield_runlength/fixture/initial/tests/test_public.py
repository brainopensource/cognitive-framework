import unittest

from solution import decode, encode


class PublicTests(unittest.TestCase):
    def test_long_run_is_counted(self):
        self.assertEqual(encode("aaaa"), "4a")

    def test_short_run_is_literal(self):
        self.assertEqual(encode("ab"), "ab")
        self.assertEqual(encode("aab"), "aab")

    def test_roundtrip(self):
        self.assertEqual(decode(encode("aaaabbc")), "aaaabbc")

    def test_empty(self):
        self.assertEqual(encode(""), "")
        self.assertEqual(decode(""), "")


if __name__ == "__main__":
    unittest.main()
