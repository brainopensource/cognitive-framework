import unittest
from src.service import get_config_val

class TestService(unittest.TestCase):
    def test_get_config_val(self):
        cfg = {"API_KEY": "secret-123", "PORT": "8080"}
        self.assertEqual(get_config_val(cfg, "API_KEY"), "secret-123")
        self.assertEqual(get_config_val(cfg, "PORT"), "8080")

if __name__ == "__main__":
    unittest.main()
