import unittest
from dataclasses import replace
from types import SimpleNamespace as NS
from aether_m456.runtime.attenuate import AgentContext, attenuate, AttenuationError
from aether_m456.runtime.spawn_adapter import SpawnAdapter, OCCURRED, DID_NOT_OCCUR, UNDETERMINABLE

def parent():
    return AgentContext("root", frozenset({"fs.read","patch.apply"}),
        {"usd_micros":1000,"tokens":5000,"turns":10,"spawns":2})

class Ledger:
    def __init__(s): s.events=[]; s._s={}
    def emit(s,k,**kw): s.events.append((k,kw))
    def settled(s,k): return s._s.get(k)
    def settle(s,k,r): s._s[k]=r
class Engine:
    def __init__(s): s.runs=0
    def run(s,c): s.runs+=1; return NS(terminal="completed",cost={"usd_micros":50})

def intent(**o):
    d=dict(verb="agent.spawn",idempotency_key="i1",parent_ctx=parent(),
           requested_authority=frozenset({"fs.read"}),budget_share={"usd_micros":400},
           child_id="c1"); d.update(o); return NS(**d)

class TestRF55Attenuation(unittest.TestCase):
    def test_child_authority_is_subset(self):
        c = attenuate(parent(), frozenset({"fs.read"}), {"usd_micros":400}, "c1")
        self.assertTrue(c.authority <= parent().authority)
    def test_escalation_denied(self):
        with self.assertRaises(AttenuationError):
            attenuate(parent(), parent().authority | {"proc.exec"}, {"usd_micros":1}, "c2")
    def test_budget_cannot_be_minted(self):
        with self.assertRaises(AttenuationError):
            attenuate(parent(), frozenset({"fs.read"}), {"usd_micros":99999}, "c3")
    def test_cycle_denied(self):
        with self.assertRaises(AttenuationError):
            attenuate(parent(), frozenset({"fs.read"}), {"usd_micros":1}, "root")
    def test_depth_bounded(self):
        with self.assertRaises(AttenuationError):
            attenuate(replace(parent(),depth=4), frozenset({"fs.read"}), {"usd_micros":1}, "c4")
    def test_spawn_storm_denied(self):
        p = replace(parent(), budget={**parent().budget,"spawns":0})
        with self.assertRaises(AttenuationError):
            attenuate(p, frozenset({"fs.read"}), {"usd_micros":1}, "c5")

class TestRF26Recovery(unittest.TestCase):
    def test_settled_spawn_never_repeats(self):
        L,E = Ledger(),Engine(); a=SpawnAdapter(L,E,lambda c:"ABSENT")
        i=intent(); a.on_authorised_intent(i); a.on_authorised_intent(i)
        self.assertEqual(E.runs,1)
    def test_lifecycle_events_emitted(self):
        L,E=Ledger(),Engine(); SpawnAdapter(L,E,lambda c:"ABSENT").on_authorised_intent(intent())
        self.assertEqual([k for k,_ in L.events],["ChildSpawned","ChildReturned"])
    def test_cold_reconciliation_is_fail_closed(self):
        L,E=Ledger(),Engine()
        for probe,exp in [("FOUND",OCCURRED),("ABSENT",DID_NOT_OCCUR),("AMBIGUOUS",UNDETERMINABLE)]:
            a=SpawnAdapter(L,E,lambda c,p=probe:p)
            self.assertEqual(a.reconcile_cold(intent()),exp)
