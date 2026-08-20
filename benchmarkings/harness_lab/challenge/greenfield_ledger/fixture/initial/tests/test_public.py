import unittest

from solution import balances


class PublicTests(unittest.TestCase):
    def test_single_transfer(self):
        self.assertEqual(balances(["alice>bob:50"]), {"alice": -50, "bob": 50})

    def test_accumulates(self):
        self.assertEqual(balances(["a>b:10", "b>a:4"]), {"a": -6, "b": 6})

    def test_empty(self):
        self.assertEqual(balances([]), {})

    def test_bad_line_raises(self):
        with self.assertRaises(ValueError):
            balances(["nonsense"])


if __name__ == "__main__":
    unittest.main()
