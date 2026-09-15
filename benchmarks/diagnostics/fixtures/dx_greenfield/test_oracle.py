import unittest

from retry import retry


class TestRetry(unittest.TestCase):
    def test_first_success(self) -> None:
        self.assertEqual(retry(lambda: 7), 7)

    def test_retries_until_success(self) -> None:
        calls = []

        def flaky():
            calls.append(1)
            if len(calls) < 3:
                raise RuntimeError("not yet")
            return "ok"

        self.assertEqual(retry(flaky, attempts=3), "ok")
        self.assertEqual(len(calls), 3)

    def test_reraises_last(self) -> None:
        with self.assertRaises(RuntimeError):
            retry(lambda: (_ for _ in ()).throw(RuntimeError("x")), attempts=2)

    def test_rejects_zero_attempts(self) -> None:
        with self.assertRaises(ValueError):
            retry(lambda: 1, attempts=0)


if __name__ == "__main__":
    unittest.main()
