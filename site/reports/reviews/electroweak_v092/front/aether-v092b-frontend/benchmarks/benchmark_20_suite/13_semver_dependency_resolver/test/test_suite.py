import unittest
from src.resolver import SemverResolver, ConflictError

class TestSemverResolver(unittest.TestCase):
    def test_diamond_dependency_resolution(self):
        resolver = SemverResolver()
        resolver.add_package("app", "1.0.0", {"libA": "^1.0.0", "libB": "^1.0.0"})
        resolver.add_package("libA", "1.0.0", {"shared": "^1.0.0"})
        resolver.add_package("libB", "1.0.0", {"shared": "^1.2.0"})
        resolver.add_package("shared", "1.0.0", {})
        resolver.add_package("shared", "1.2.0", {})
        resolver.add_package("shared", "1.3.0", {})

        plan = resolver.resolve("app", "1.0.0")
        self.assertEqual(plan["app"], "1.0.0")
        self.assertEqual(plan["shared"], "1.3.0")

    def test_conflict_error_raised(self):
        resolver = SemverResolver()
        resolver.add_package("app", "1.0.0", {"libA": "^1.0.0", "libB": "^1.0.0"})
        resolver.add_package("libA", "1.0.0", {"shared": "^1.0.0"})
        resolver.add_package("libB", "1.0.0", {"shared": "^2.0.0"})
        resolver.add_package("shared", "1.0.0", {})
        resolver.add_package("shared", "2.0.0", {})

        with self.assertRaises(ConflictError):
            resolver.resolve("app", "1.0.0")

if __name__ == "__main__":
    unittest.main()
