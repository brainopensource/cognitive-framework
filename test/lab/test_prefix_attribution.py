import unittest

from tools.telemetry.prefix_attribution import attribute_call, prefix_miss_reason


class TestPrefixAttribution(unittest.TestCase):
    def test_l1_system_mutation_is_system_miss(self) -> None:
        previous = {"system": "v1", "tools": ["read"], "compact": "c1", "snip": "s1"}
        current = {"system": "v2", "tools": ["read"], "compact": "c1", "snip": "s1"}
        self.assertEqual(prefix_miss_reason(previous, current), "system")
        self.assertEqual(attribute_call(previous, current)["prefixMissReason"], "system")

    def test_unchanged_layers_are_a_hit(self) -> None:
        value = {"system": "v1", "tools": ["read"], "compact": "c1", "snip": "s1"}
        result = attribute_call(value, value)
        self.assertEqual(result["prefixMissReason"], "hit")
        self.assertTrue(result["cacheHit"])
