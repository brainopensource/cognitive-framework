import unittest

from solution import balances


class Oracle(unittest.TestCase):
    def test_whitespace_is_stripped(self):
        self.assertEqual(balances(["  alice > bob : 50 "]), {"alice": -50, "bob": 50})

    def test_three_party_chain(self):
        self.assertEqual(balances(["a>b:10", "b>c:10"]), {"a": -10, "b": 0, "c": 10})

    def test_zero_balance_account_is_present(self):
        self.assertIn("b", balances(["a>b:5", "b>c:5"]))

    def test_negative_amount_raises(self):
        with self.assertRaises(ValueError):
            balances(["a>b:-5"])

    def test_non_integer_amount_raises(self):
        with self.assertRaises(ValueError):
            balances(["a>b:1.5"])

    def test_empty_account_name_raises(self):
        with self.assertRaises(ValueError):
            balances(["  >b:5"])

    def test_extra_separator_raises(self):
        with self.assertRaises(ValueError):
            balances(["a>b>c:5"])


if __name__ == "__main__":
    unittest.main()
