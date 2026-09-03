import unittest
from columnar import ColumnarTable

class TestColumnarTable(unittest.TestCase):
    def test_columnar_vector_filtering(self):
        table = ColumnarTable({
            "id": [1, 2, 3, 4, 5],
            "age": [20, 35, 45, 18, 50],
            "role": ["user", "admin", "admin", "user", "admin"]
        })
        res = table.query("age", lambda x: x >= 35)
        self.assertEqual(res["id"], [2, 3, 5])
        self.assertEqual(res["role"], ["admin", "admin", "admin"])

if __name__ == "__main__":
    unittest.main()
