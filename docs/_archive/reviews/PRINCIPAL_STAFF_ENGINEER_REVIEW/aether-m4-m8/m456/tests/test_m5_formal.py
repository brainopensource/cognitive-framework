import unittest
from types import SimpleNamespace as NS
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from aether_m456.runtime.memo import memo_key, MEMO_FIELDS, WitnessMemo, MemoEntry
from aether_m456.adapters.formal_env import FormalEnvironment
from aether_m456.adapters.formal_oracle import FormalOracle

BASE = dict(obligation="x+0=x", input_digests=["sha256:aa"], environment_digest="sha256:e",
            checker_identity="z3-4.13", toolchain_version="1.2.0",
            assurance_level="hermetic", policy_version="v3")

class TestMemoSoundness(unittest.TestCase):
    def test_key_is_stable(self):
        self.assertEqual(memo_key(**BASE), memo_key(**BASE))
    def test_every_field_changes_the_key(self):
        k = memo_key(**BASE)
        for f in MEMO_FIELDS:
            self.assertNotEqual(memo_key(**{**BASE, f:"MUTATED"}), k, f)
    def test_missing_field_raises(self):
        with self.assertRaises(ValueError):
            memo_key(**{k:v for k,v in BASE.items() if k!="assurance_level"})
    def test_memo_is_bounded(self):
        m=WitnessMemo(capacity=2)
        for i in range(5): m.put(f"k{i}", MemoEntry("d","r","unsat"))
        self.assertEqual(len(m._d),2)

class Solver:
    def __init__(s): s.calls=0
    def solve(s,g): s.calls+=1; return NS(status="unsat",proof=b"(proof (trans a b))",millis=12)

def ctx(**o):
    d=dict(environment_digest="sha256:e",assurance_level="hermetic",
           policy_version="v3",run_id="r1"); d.update(o); return NS(**d)

class TestFormalEnvironment(unittest.TestCase):
    def setUp(self):
        self.s=Solver(); self.e=FormalEnvironment(self.s,checker_identity="z3-4.13",toolchain="1.2.0")
        self.req=NS(verb="formal.check",args={"goal":"x+0=x","inputs":["sha256:aa"]})
    def test_memo_avoids_second_solve(self):
        self.e.execute(self.req,ctx()); r=self.e.execute(self.req,ctx())
        self.assertTrue(r.memo_hit); self.assertEqual(self.s.calls,1)
    def test_assurance_change_misses_memo(self):
        self.e.execute(self.req,ctx()); self.e.execute(self.req,ctx(assurance_level="recorded"))
        self.assertEqual(self.s.calls,2)
    def test_cost_never_fabricates_zero_tokens(self):
        r=self.e.execute(self.req,ctx())
        self.assertIsNone(r.cost.tokens); self.assertTrue(r.cost.tokens_reason)

class Checker:
    def check(s,t,p): return t=="x+0=x" and p==b"(proof (trans a b))"

class TestExteriorOracle(unittest.TestCase):
    def setUp(self):
        self.o=FormalOracle(Ed25519PrivateKey.generate(),"oracle-1",Checker())
        self.rr=NS(D_X="sha256:x",D_H="sha256:h",D_R="sha256:r",run_id="r1",episode_id="e1",
                   preregistration_digest="sha256:pre",proof_bytes=b"(proof (trans a b))")
        self.pr=NS(theorem="x+0=x",task_digest="sha256:t",oracle_digest="sha256:o",
                   preregistration_digest="sha256:pre",name="replay/1")
    def test_valid_proof_signs_pass(self):
        v=self.o.evaluate(self.rr,self.pr)
        self.assertEqual(v.body["outcome"],"pass")
        self.assertTrue(v.verify(self.o.public_key))
    def test_tampered_body_fails_verification(self):
        v=self.o.evaluate(self.rr,self.pr); v.body["outcome"]="TAMPERED"
        self.assertFalse(v.verify(self.o.public_key))
    def test_foreign_key_does_not_verify(self):
        v=self.o.evaluate(self.rr,self.pr)
        self.assertFalse(v.verify(Ed25519PrivateKey.generate().public_key()))
    def test_posthoc_preregistration_is_invalid(self):
        rr=NS(**{**self.rr.__dict__,"preregistration_digest":"sha256:LATER"})
        self.assertEqual(self.o.evaluate(rr,self.pr).body["outcome"],"invalid")
    def test_bogus_proof_fails(self):
        rr=NS(**{**self.rr.__dict__,"proof_bytes":b"(bogus)"})
        self.assertEqual(self.o.evaluate(rr,self.pr).body["outcome"],"fail")
