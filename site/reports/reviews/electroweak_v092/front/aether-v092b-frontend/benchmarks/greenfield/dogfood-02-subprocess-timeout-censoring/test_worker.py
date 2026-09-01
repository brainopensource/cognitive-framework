import unittest
from src.worker import process_items

class TestWorker(unittest.TestCase):
    def test_process_items(self):
        self.assertEqual(process_items([1, 2, 3]), [2, 4, 6])

if __name__ == "__main__":
    unittest.main()
