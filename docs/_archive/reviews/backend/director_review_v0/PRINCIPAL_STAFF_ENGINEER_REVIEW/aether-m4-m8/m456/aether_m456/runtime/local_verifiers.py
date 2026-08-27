"""Row verifiers for the `local` profile (no bwrap, no live provider).

Each verifier derives from a canonical source or returns a typed reason.
None of them can be made to pass by assertion.
"""
from __future__ import annotations
from .evidence import Row, ABSENT, INVALID, UNVERIFIABLE, PRESENT_VALID

def row1_model(run):
    r = run.trajectory["model_routes_used"][0]
    if r["provider"] in ("fake", "scripted", "cassette", "mock", "lam"):
        return Row(1, UNVERIFIABLE, "trajectory.model_routes_used", run.trajectory_digest,
                   f"synthetic provider '{r['provider']}': no live invocation")
    if not r.get("model_fingerprint"):
        return Row(1, UNVERIFIABLE, "trajectory.model_routes_used", run.trajectory_digest,
                   r.get("fingerprint_unavailable_reason", "fingerprint_absent"))
    return Row(1, PRESENT_VALID, "trajectory.model_routes_used", run.trajectory_digest)

def row2_effect(run):
    ev = [e for e in run.events if e.kind == "EffectStarted"]
    if not ev: return Row(2, ABSENT, reason="no EffectStarted in range")
    e = ev[0]
    if e.payload.get("sinkClass") == "privileged" and not e.payload.get("grantId"):
        return Row(2, INVALID, "ledger.EffectStarted", run.events_digest,
                   "privileged effect without grant")
    return Row(2, PRESENT_VALID, "ledger.EffectStarted", run.events_digest)

def row3_fs(run):
    if not run.workspace_before or not run.workspace_after:
        return Row(3, ABSENT, reason="workspace digests not captured")
    if run.workspace_before == run.workspace_after:
        return Row(3, INVALID, "workspace.digests", run.workspace_after,
                   "no observable filesystem change")
    return Row(3, PRESENT_VALID, "workspace.digests", run.workspace_after)

def row4_sandbox(run):
    c = run.containment
    if c is None:
        return Row(4, ABSENT, reason="host backend: no containment attempted")
    if not c.get("verified"):
        return Row(4, UNVERIFIABLE, "containment.report", run.containment_digest,
                   c.get("visibility_mark", "probes_unverified"))
    return Row(4, PRESENT_VALID, "containment.report", run.containment_digest)

def row5_verdict(run):
    if run.verdict is None:
        return Row(5, ABSENT, reason=run.verdict_absence_reason or "no_evaluator_bound")
    if not run.verdict_signature_ok:
        return Row(5, INVALID, "evaluator.SignedVerdict", run.verdict_digest,
                   "ed25519 verification failed")
    return Row(5, PRESENT_VALID, "evaluator.SignedVerdict", run.verdict_digest)

def row6_wal(run):
    if run.journal_mode != "wal":
        return Row(6, INVALID, "store.pragma", run.events_digest,
                   f"journal_mode={run.journal_mode}, expected wal")
    if run.event_range["count"] != len(run.events):
        return Row(6, INVALID, "ledger.range", run.events_digest, "event range gap")
    return Row(6, PRESENT_VALID, "ledger.range", run.events_digest)

def row7_cold(run):
    if run.cold_report is None:
        return Row(7, ABSENT, reason="no fresh-process reconstruction attempted")
    if run.cold_report["state_digest"] != run.trajectory["state_digest"]:
        return Row(7, INVALID, "recovery.report", run.events_digest,
                   "folded state diverged")
    if run.cold_report.get("repeated_settled_effect"):
        return Row(7, INVALID, "recovery.report", run.events_digest,
                   "settled effect repeated")
    return Row(7, PRESENT_VALID, "recovery.report", run.events_digest)

def row8_trajectory(run):
    t = run.trajectory
    if t.get("schema") != "mhf.trajectory/1":
        return Row(8, INVALID, "trajectory", run.trajectory_digest, "wrong schema")
    if not t.get("turns"):
        return Row(8, INVALID, "trajectory", run.trajectory_digest, "no turns recorded")
    for turn in t["turns"]:                      # conserved cost, explicit status
        ms = turn["cost"]["measurement_status"]
        if any(v["status"] not in ("measured", "estimated", "unavailable")
               for v in ms.values()):
            return Row(8, INVALID, "trajectory", run.trajectory_digest,
                       "cost measurement status not explicit")
    return Row(8, PRESENT_VALID, "trajectory", run.trajectory_digest)

def row9_authority(run):
    if run.authority_path != "Runtime.run_composed":
        return Row(9, INVALID, "import_trace", run.trace_digest,
                   f"alternate driver: {run.authority_path}")
    return Row(9, PRESENT_VALID, "import_trace", run.trace_digest)

LOCAL_VERIFIERS = {1:row1_model,2:row2_effect,3:row3_fs,4:row4_sandbox,5:row5_verdict,
                   6:row6_wal,7:row7_cold,8:row8_trajectory,9:row9_authority}
