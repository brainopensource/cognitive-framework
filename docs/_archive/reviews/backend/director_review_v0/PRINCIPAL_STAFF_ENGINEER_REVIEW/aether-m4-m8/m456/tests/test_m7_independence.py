import unittest
from aether_m456.runtime.independence import (EffectRef, selector_disjoint,
                                              independent, analyse)

def fs(*paths, sink="observation", idem=None, verb="fs.read"):
    return EffectRef(verb, sink, {"kind":"fs","root":"/workspace","paths":list(paths)}, idem)

class TestSelectorAlgebra(unittest.TestCase):
    def test_disjoint_paths(self):
        self.assertTrue(selector_disjoint({"kind":"fs","paths":["/a"]},
                                          {"kind":"fs","paths":["/b"]}))
    def test_same_path_overlaps(self):
        self.assertFalse(selector_disjoint({"kind":"fs","paths":["/a"]},
                                           {"kind":"fs","paths":["/a"]}))
    def test_parent_child_overlaps(self):
        self.assertFalse(selector_disjoint({"kind":"fs","paths":["/a"]},
                                           {"kind":"fs","paths":["/a/b/c.py"]}))
    def test_prefix_string_trap_is_not_overlap(self):
        # /workspace/foo vs /workspace/foobar must NOT overlap
        self.assertTrue(selector_disjoint({"kind":"fs","paths":["/workspace/foo"]},
                                          {"kind":"fs","paths":["/workspace/foobar"]}))
    def test_traversal_is_normalised(self):
        self.assertFalse(selector_disjoint({"kind":"fs","paths":["/a/b/../b"]},
                                           {"kind":"fs","paths":["/a/b"]}))
    def test_different_kinds_are_disjoint(self):
        self.assertTrue(selector_disjoint({"kind":"fs","paths":["/a"]},
                                          {"kind":"network","hosts":["x"]}))
    def test_unknown_kind_fails_closed(self):
        self.assertFalse(selector_disjoint({"kind":"quantum"}, {"kind":"quantum"}))
    def test_network_wildcard_fails_closed(self):
        self.assertFalse(selector_disjoint({"kind":"network","hosts":["*"]},
                                           {"kind":"network","hosts":["a.com"]}))

class TestIndependence(unittest.TestCase):
    def test_two_reads_on_disjoint_paths_are_independent(self):
        self.assertTrue(independent(fs("/workspace/a"), fs("/workspace/b")))
    def test_two_writers_never_independent_even_if_disjoint(self):
        a = fs("/workspace/a", sink="privileged", verb="patch.apply")
        b = fs("/workspace/b", sink="privileged", verb="patch.apply")
        self.assertFalse(independent(a, b))
    def test_shared_idempotency_key_blocks(self):
        self.assertFalse(independent(fs("/a", idem="k1"), fs("/b", idem="k1")))
    def test_read_and_write_on_same_file_blocked(self):
        self.assertFalse(independent(fs("/workspace/a"),
                                     fs("/workspace/a", sink="privileged")))

class TestReport(unittest.TestCase):
    def test_all_reads_disjoint_gives_high_fraction(self):
        r = analyse([fs(f"/workspace/f{i}") for i in range(6)])
        self.assertEqual(r.fraction, 1.0)
        self.assertIn("MAY be worth measuring", r.verdict())
    def test_all_writers_gives_zero_and_recommends_keeping_i11(self):
        r = analyse([fs(f"/workspace/f{i}", sink="privileged") for i in range(5)])
        self.assertEqual(r.independent_pairs, 0)
        self.assertIn("NOT justified", r.verdict())
        self.assertEqual(r.blocked_by_sink, 10)
    def test_empty_is_no_data_not_a_pass(self):
        self.assertIn("NO DATA", analyse([]).verdict())
    def test_counts_are_exhaustive(self):
        r = analyse([fs("/a"), fs("/a", sink="privileged"),
                     fs("/b", sink="privileged"), fs("/c", idem="k"), fs("/d", idem="k")])
        self.assertEqual(r.total_pairs,
            r.independent_pairs + r.blocked_by_sink + r.blocked_by_selector
            + r.blocked_by_idempotency)
