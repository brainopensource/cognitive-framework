import unittest
from pathlib import Path

class TestGreenfieldApp(unittest.TestCase):
    def test_server_file_exists(self):
        server_path = Path("app/server.py")
        self.assertTrue(server_path.exists(), "app/server.py does not exist")

    def test_static_html_exists(self):
        index_path = Path("static/index.html")
        self.assertTrue(index_path.exists(), "static/index.html does not exist")
        content = index_path.read_text(encoding="utf-8")
        self.assertIn("<html>", content.lower())

if __name__ == "__main__":
    unittest.main()
