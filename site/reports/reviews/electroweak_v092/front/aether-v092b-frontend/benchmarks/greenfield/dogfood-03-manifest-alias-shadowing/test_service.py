import unittest
from src.service import execute_service_action, resolve_verb_alias, UnresolvableVerbError

class TestService(unittest.TestCase):
    def test_execute_service_action(self):
        # Must resolve to valid granted verb (e.g. "run" -> "proc.exec")
        result = execute_service_action("run")
        self.assertEqual(result, "executed:proc.exec")

    def test_ungranted_alias_fails_closed(self):
        aliases = {"read": "fs.read"}
        with self.assertRaises(UnresolvableVerbError):
            resolve_verb_alias("ungranted_verb", aliases)

if __name__ == "__main__":
    unittest.main()
