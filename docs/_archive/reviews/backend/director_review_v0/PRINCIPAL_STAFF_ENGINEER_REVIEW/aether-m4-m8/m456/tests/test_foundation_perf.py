import unittest
from aether_m456.runtime.context_store import ContextStore

L1 = "You are an autonomous coding agent.\n" * 8
L2 = '[{"name":"read","schema":{"a":1}}]' * 180      # ~5.9KB, real shape
BASE = [{"layer":"L1","role":"system","content":L1},
        {"layer":"L2","role":"system","content":L2},
        {"layer":"L4","role":"user","content":"Repair the value bug."}]

def turns(n):
    return [BASE + [{"layer":"L5","role":"user","content":f"tool result turn={i}"}]
            for i in range(n)]

class TestRamFix(unittest.TestCase):
    def test_identical_layers_stored_once(self):
        s = ContextStore()
        for t in turns(50): s.intern_turn(t)
        self.assertEqual(s._blobs[s.intern("L2","system",L2).digest], L2)
        # 3 shared bodies + 50 distinct L5 bodies
        self.assertEqual(s.stats()["unique_blobs"], 53)

    def test_material_reduction(self):
        s = ContextStore(); ts = turns(50)
        naive = sum(len(l["content"].encode()) for t in ts for l in t)
        for t in ts: s.intern_turn(t)
        self.assertGreater(naive / s.stored_bytes, 8.0)

class TestCpuFix(unittest.TestCase):
    def test_digest_cache_hits_on_repeat(self):
        s = ContextStore()
        for t in turns(50): s.intern_turn(t)
        # 53 unique bodies hashed once; the other 147 layer visits are hits
        self.assertEqual(s.stats()["digest_misses"], 53)
        self.assertGreater(s.stats()["hit_rate"], 0.7)

    def test_turn_digest_uses_refs_not_bodies(self):
        s = ContextStore()
        a = s.turn_digest(s.intern_turn(turns(2)[0]))
        b = s.turn_digest(s.intern_turn(turns(2)[0]))
        self.assertEqual(a, b)
        self.assertNotEqual(a, s.turn_digest(s.intern_turn(turns(2)[1])))

class TestReplayFidelity(unittest.TestCase):
    def test_rehydrate_is_byte_exact(self):
        s = ContextStore(); t = turns(1)[0]
        out = s.rehydrate(s.intern_turn(t))
        self.assertEqual([l["content"] for l in out], [l["content"] for l in t])
        self.assertEqual([l["layer"] for l in out], [l["layer"] for l in t])

    def test_never_evicts_within_episode(self):
        s = ContextStore()
        first = s.intern("L2","system",L2)
        for t in turns(200): s.intern_turn(t)
        self.assertEqual(s.resolve(first), L2)   # still resolvable after 200 turns
