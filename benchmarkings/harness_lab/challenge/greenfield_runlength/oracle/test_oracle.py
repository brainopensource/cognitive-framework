import unittest

from solution import decode, encode


class Oracle(unittest.TestCase):
    def test_multi_digit_counts(self):
        self.assertEqual(encode("z" * 12), "12z")
        self.assertEqual(decode("12z"), "z" * 12)

    def test_mixed_runs(self):
        self.assertEqual(encode("aaabbcccc"), "3abb4c")
        self.assertEqual(decode("3abb4c"), "aaabbcccc")

    def test_exactly_three_is_counted_two_is_not(self):
        self.assertEqual(encode("aaa"), "3a")
        self.assertEqual(encode("aa"), "aa")

    def test_digits_rejected(self):
        with self.assertRaises(ValueError):
            encode("a1b")

    def test_roundtrip_property(self):
        for sample in ("", "a", "ab", "aaabbbccc", "qqqqqqqqqqqqqqw", "abcabc"):
            self.assertEqual(decode(encode(sample)), sample)


if __name__ == "__main__":
    unittest.main()
