import unittest
from types import SimpleNamespace as NS
from aether_m456.runtime.evidence import (EvidenceAuditor, Row, ABSENT, INVALID,
                                          UNVERIFIABLE, PRESENT_VALID)
from aether_m456.runtime.local_verifiers import LOCAL_VERIFIERS
from aether_m456.runtime.context_store import ContextStore as LayerInterner

TRAJ={"schema":"mhf.trajectory/1","state_digest":"sha256:st",
      "model_routes_used":[{"provider":"fake","model":"f","model_fingerprint":None,
                            "fingerprint_unavailable_reason":"provider_did_not_report"}],
      "turns":[{"cost":{"measurement_status":{"usd_micros":{"status":"measured"}}}}]}

def run(**o):
    d=dict(trajectory=TRAJ,trajectory_digest="sha256:tj",
      events=[NS(kind="EffectStarted",payload={"sinkClass":"privileged","grantId":"g1"})],
      events_digest="sha256:ev",event_range={"count":1},
      workspace_before="sha256:a",workspace_after="sha256:b",
      containment=None,containment_digest=None,verdict=None,
      verdict_absence_reason="no_evaluator_bound",verdict_signature_ok=False,
      verdict_digest=None,journal_mode="wal",cold_report=None,
      authority_path="Runtime.run_composed",trace_digest="sha256:tr",
      lineage={"run_id":"r1"})
    d.update(o); return NS(**d)

LOCAL=NS(id="local",assurance_level="recorded")
HERM =NS(id="hermetic",assurance_level="hermetic")
AUD=EvidenceAuditor(LOCAL_VERIFIERS)

def good():
    return run(trajectory={**TRAJ,"model_routes_used":[{"provider":"openrouter",
               "model":"x","model_fingerprint":"fp"}]},
        containment={"verified":True},containment_digest="sha256:c",
        verdict={"o":"pass"},verdict_signature_ok=True,verdict_digest="sha256:v",
        cold_report={"state_digest":"sha256:st","repeated_settled_effect":False})

class TestLocalProfileIsHonest(unittest.TestCase):
    def test_local_run_is_never_promotable(self):
        self.assertFalse(AUD.audit(run(),LOCAL).promotion_eligible)
    def test_local_still_derives_five_rows(self):
        b=AUD.audit(run(),LOCAL)
        self.assertEqual(sorted(n for n,r in b.rows.items() if r.promotable),[2,3,6,8,9])
    def test_fake_provider_is_unverifiable_not_absent(self):
        self.assertEqual(AUD.audit(run(),LOCAL).rows[1].state,UNVERIFIABLE)
    def test_every_non_promotable_row_carries_a_reason(self):
        for r in AUD.audit(run(),LOCAL).rows.values():
            if not r.promotable: self.assertTrue(r.reason)

class TestFailClosed(unittest.TestCase):
    def test_privileged_effect_without_grant_is_invalid(self):
        r=run(events=[NS(kind="EffectStarted",payload={"sinkClass":"privileged","grantId":None})])
        self.assertEqual(AUD.audit(r,HERM).rows[2].state,INVALID)
    def test_non_wal_journal_is_invalid(self):
        self.assertEqual(AUD.audit(run(journal_mode="delete"),HERM).rows[6].state,INVALID)
    def test_unchanged_workspace_is_invalid(self):
        r=run(workspace_before="sha256:a",workspace_after="sha256:a")
        self.assertEqual(AUD.audit(r,HERM).rows[3].state,INVALID)
    def test_alternate_driver_is_invalid(self):
        self.assertEqual(AUD.audit(run(authority_path="lab_driver.main"),HERM).rows[9].state,INVALID)
    def test_diverged_cold_state_is_invalid(self):
        r=run(cold_report={"state_digest":"sha256:OTHER","repeated_settled_effect":False})
        self.assertEqual(AUD.audit(r,HERM).rows[7].state,INVALID)
    def test_repeated_settled_effect_is_invalid(self):
        r=run(cold_report={"state_digest":"sha256:st","repeated_settled_effect":True})
        self.assertEqual(AUD.audit(r,HERM).rows[7].state,INVALID)
    def test_unsigned_verdict_is_invalid(self):
        r=run(verdict={"o":"pass"},verdict_signature_ok=False,verdict_digest="sha256:v")
        self.assertEqual(AUD.audit(r,HERM).rows[5].state,INVALID)
    def test_throwing_verifier_denies(self):
        def boom(_): raise RuntimeError("x")
        b=EvidenceAuditor({**LOCAL_VERIFIERS,4:boom}).audit(run(),HERM)
        self.assertEqual(b.rows[4].state,INVALID)
    def test_missing_verifier_is_absent(self):
        b=EvidenceAuditor({k:v for k,v in LOCAL_VERIFIERS.items() if k!=5}).audit(good(),HERM)
        self.assertEqual(b.rows[5].state,ABSENT)

class TestPromotion(unittest.TestCase):
    def test_all_nine_valid_promotes(self):
        self.assertTrue(AUD.audit(good(),HERM).promotion_eligible)
    def test_one_bad_row_blocks_promotion(self):
        r=good(); r.journal_mode="delete"
        b=AUD.audit(r,HERM)
        self.assertFalse(b.promotion_eligible); self.assertIn("6",b.unattributable_reason)

class TestLayerInterning(unittest.TestCase):
    def test_replay_is_exact(self):
        it=LayerInterner(); ref=it.intern("L2","system","X"*5926)
        self.assertEqual(it.resolve(ref),"X"*5926)
    def test_duplicate_layers_stored_once(self):
        it=LayerInterner()
        for _ in range(50): it.intern("L2","system","X"*5926)
        self.assertEqual(it.stored_bytes,5926)
