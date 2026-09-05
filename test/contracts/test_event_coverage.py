"""E-COV: every event kind the production `LedgerEmitter` can legally write
is present in the canonical event catalog (SPEC §1.2, ADR-0076 §6).

M-2 (2026-08-20, Tech Lead): `domain/ledger/events.EVENT_KINDS` had drifted
from `runtime/ledger_emitter.PRIVILEGED_KIND_OWNERS` and the kinds real
call sites actually emit -- `VerdictRecorded`, `EffectFailed`,
`BudgetExhausted`, `CapabilityAttenuated`, `TurnStarted` and others were
legal for `LedgerEmitter` to write but absent from the catalog, so
`reduce_event` silently misfiled them into `unknown_events`. This is not a
brittle fixed-count check (a count regresses the instant a legitimate kind
is added) -- it asserts the one direction that must always hold: everything
production can actually or legally write is a *subset* of the catalog.
"""
from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_TOOLS = str(ROOT / "tools")
_LINTERS = str(ROOT / "tools" / "linters")
for _p in (_LINTERS, _TOOLS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from check_event_coverage import (  # noqa: E402
    UNPRODUCED_ALLOWLIST,
    check as run_event_coverage_check,
    emitting_call_sites,
    production_emittable_kinds,
)

from vanguard.packages.domain.ledger.events import (  # noqa: E402
    EVENT_KINDS,
    WRITABLE_KINDS,
    EventEnvelope,
)
from vanguard.packages.domain.ledger.reducer import initial_state, reduce_event  # noqa: E402
from vanguard.packages.runtime.ledger_emitter import PRIVILEGED_KIND_OWNERS  # noqa: E402

# Kinds deliberately not reduced into LedgerState (e.g. advisory markers,
# pre-decision requests, triggers, or Phase-2 pipeline markers).
# Every kind in EVENT_KINDS must either be folded or named here explicitly.
UNFOLDED_ALLOWLIST = frozenset({
    "AuthorizationRequested",  # Pre-decision advisory request; decision is AuthorizationDenied/CapabilityGranted
    "CanaryPromoted",          # Phase-2 release pipeline marker
    "CandidateAttested",       # Phase-2 candidate release pipeline
    "CandidateBuilt",          # Phase-2 candidate release pipeline
    "CheckpointCreated",       # Snapshot/checkpoint marker
    "ClaimRecorded",           # Evidence claim legacy synonym (EvidenceClaimProduced is folded)
    "CompetencePriorRecorded", # Prior competence distribution (Phase-2)
    "CorrectionRecorded",      # Phase-2 human/supervisor feedback marker
    "EvaluationRequested",     # Exterior evaluator trigger envelope
    "InvalidationChecked",     # Cache/competence invalidation check
    "KernelAlarm",             # Advisory paging/health alarm
    "ObservationRequested",    # Observation trigger request
    "OperatorInvoked",         # Phase-2 operator invocation
    "OperatorSelected",        # Phase-2 operator selection
    "ProposalRejected",        # Planner proposal rejection notification
    "ReflectionProduced",      # Agent reflective log trace
    "RollbackTriggered",       # Phase-2 rollback notification
    "RunCompleted",            # Outer run completed marker (EpisodeCompleted is folded)
    "RunStarted",              # Outer run started marker (EpisodeStarted is folded)
})


class WritableKindsHaveProducersOrAreAllowlisted(unittest.TestCase):
    """E-COV, the other direction: catalogued kinds must be *written*.

    The original check only asserted `emittable <= EVENT_KINDS`, so a kind
    could be catalogued, reduced, projected and rendered by a client while
    nothing ever emitted it. The reader looks correct and the feature is
    simply invisible -- which is exactly what happened to `GoalDeclared`,
    `TurnStarted` and `ContextCompacted` (the last with five readers).
    """

    def test_every_writable_kind_has_a_producer_or_is_allowlisted(self) -> None:
        unproduced = sorted(WRITABLE_KINDS - emitting_call_sites() - UNPRODUCED_ALLOWLIST)
        self.assertEqual(
            unproduced, [],
            f"writable kinds nothing emits and nothing excuses: {unproduced}")

    def test_allowlist_contains_no_produced_kind(self) -> None:
        # Anti-rot. Once a kind gains a producer its entry must be deleted,
        # or the allowlist silently becomes a graveyard the way the deleted
        # `EMITTER_SITES` registry did.
        stale = sorted(UNPRODUCED_ALLOWLIST & emitting_call_sites())
        self.assertEqual(stale, [], f"allowlisted kinds that now have producers: {stale}")

    def test_allowlist_is_a_subset_of_writable_kinds(self) -> None:
        # A typo'd entry would otherwise excuse nothing while looking
        # deliberate, and the missing producer stays invisible.
        unknown = sorted(UNPRODUCED_ALLOWLIST - WRITABLE_KINDS)
        self.assertEqual(unknown, [], f"allowlist entries that are not writable kinds: {unknown}")

    def test_the_two_allowlists_answer_different_questions(self) -> None:
        # `UNFOLDED_ALLOWLIST` is about the reducer, this one is about the
        # producer. They legitimately overlap, so neither may be derived from
        # the other -- assert only that both are real catalog subsets.
        self.assertTrue(UNFOLDED_ALLOWLIST <= EVENT_KINDS)
        self.assertTrue(UNPRODUCED_ALLOWLIST <= EVENT_KINDS)

    def test_producer_axis_excludes_the_writer_authority_table(self) -> None:
        # `production_emittable_kinds()` unions `PRIVILEGED_KIND_OWNERS`. If
        # the producer check were built on it, granting a kind an owner would
        # satisfy "has a producer" with no emitter anywhere.
        self.assertTrue(emitting_call_sites() <= production_emittable_kinds())
        masked = set(PRIVILEGED_KIND_OWNERS) - emitting_call_sites()
        self.assertTrue(
            masked, "expected the authority table to name kinds no call site emits")

    def test_check_reports_an_unproduced_kind(self) -> None:
        # The falsifier's falsifier: drop a real gap's excuse and the linter
        # must fail. Without this, a check that can never fail looks green.
        import check_event_coverage as module

        original = module.UNPRODUCED_ALLOWLIST
        # Pick a currently-allowlisted kind rather than naming one: each wave
        # deletes entries as it implements them, and a hard-coded kind turns
        # this into a false green the moment that kind gains a producer.
        victim = sorted(original)[0]
        try:
            module.UNPRODUCED_ALLOWLIST = original - {victim}
            errors = run_event_coverage_check()
        finally:
            module.UNPRODUCED_ALLOWLIST = original
        self.assertTrue(any(victim in err for err in errors), errors)


class ProductionEmittableKindsAreCatalogued(unittest.TestCase):
    """Production-emittable kinds ⊆ `EVENT_KINDS` (subset, never equality)."""

    def test_every_privileged_owner_kind_is_catalogued(self) -> None:
        missing = sorted(set(PRIVILEGED_KIND_OWNERS) - EVENT_KINDS)
        self.assertEqual(missing, [], f"writer-authorised kinds absent from EVENT_KINDS: {missing}")

    def test_every_production_emittable_kind_is_catalogued(self) -> None:
        missing = sorted(production_emittable_kinds() - EVENT_KINDS)
        self.assertEqual(missing, [], f"production-emittable kinds absent from EVENT_KINDS: {missing}")

    def test_m2_named_kinds_are_catalogued(self) -> None:
        # The five kinds the Tech Lead's M-2 blocker named as missing.
        for kind in (
            "VerdictRecorded",
            "EffectFailed",
            "BudgetExhausted",
            "CapabilityAttenuated",
            "TurnStarted",
        ):
            self.assertIn(kind, EVENT_KINDS, f"{kind} must be in the canonical catalog (M-2)")

    def test_wave3_plugin_lifecycle_kinds_are_catalogued(self) -> None:
        # Wave 3 depends on this vocabulary already existing (M-2 blocker note).
        for kind in (
            "PluginResolved",
            "PluginActivated",
            "PluginQuiesced",
            "PluginRetired",
            "PluginFaulted",
        ):
            self.assertIn(kind, EVENT_KINDS)

    def test_kind_never_legitimately_writable_stays_out(self) -> None:
        # The CLI streaming wire protocol (ADR-0062, `runtime/service/`) is a
        # distinct bounded context; its kinds must never enter the ledger
        # catalog (test/kernel/test_event_kinds_writer.py holds the other
        # half of this guarantee at the writer/parse boundary).
        self.assertNotIn("RunFailed", EVENT_KINDS)

    def test_check_event_coverage_tool_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "linters" / "check_event_coverage.py")],
            cwd=ROOT, text=True, capture_output=True, check=False,
            env={**os.environ},
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class CataloguedKindsAreFoldedOrAllowlisted(unittest.TestCase):
    """M-2 gate: catalogued ⇒ folded or explicitly allowlisted (no silent else)."""

    def _envelope(self, seq: int, kind: str, payload: dict) -> EventEnvelope:
        payload_with_kind = dict(payload)
        payload_with_kind["kind"] = kind
        return EventEnvelope(
            schema_version="vg.4",
            event_id=f"018f0000-0000-7000-8000-{seq:012d}",
            scope="episode",
            seq=str(seq),
            occurred_at="2026-08-20T00:00:00.000Z",
            recorded_at="2026-08-20T00:00:00.000Z",
            principal="agent-1",
            principal_role="episode",
            tenant_id="tenant-1",
            owner_id="owner-1",
            confidentiality="internal",
            retention_class="standard",
            trainability="prohibited",
            redaction_status="none",
            run_id="run-test",
            episode_id="ep-test",
            payload=payload_with_kind,
        )

    def test_allowlist_is_disjoint_and_subset_of_catalog(self) -> None:
        extra = UNFOLDED_ALLOWLIST - EVENT_KINDS
        self.assertEqual(extra, frozenset(), f"UNFOLDED_ALLOWLIST contains non-catalog kinds: {extra}")

    def test_every_catalogued_kind_is_either_folded_or_allowlisted(self) -> None:
        unhandled_silently = []
        dummy_payloads = {
            "PluginResolved": {"plugin_id": "p1"},
            "PluginActivated": {"plugin_id": "p1"},
            "PluginQuiesced": {"plugin_id": "p1"},
            "PluginRetired": {"plugin_id": "p1"},
            "PluginFaulted": {"plugin_id": "p1", "reason": "fault"},
            "VerdictRecorded": {
                "signedVerdict": {
                    "evaluation_request_id": "req-1",
                    "verdict": "pass",
                    "signature": "sig",
                }
            },
            "EffectStarted": {"descriptorDigest": "d1", "sinkClass": "fs"},
            "EffectCompleted": {"descriptorDigest": "d1", "outcome": "ok"},
            "EffectFailed": {"descriptorDigest": "d1", "error": "failed"},
            "EffectRejected": {"descriptorDigest": "d1", "reason": "denied"},
            "EffectPreviewed": {"descriptorDigest": "d1"},
            "EffectReconciled": {"descriptorDigest": "d1"},
            "BudgetReserved": {"leaseId": "l1", "dimensions": {"usd_micros": 100}},
            "BudgetCommitted": {"leaseId": "l1", "debits": {"usd_micros": 50}},
            "BudgetReleased": {"leaseId": "l1"},
            "BudgetExhausted": {"leaseId": "l1", "debits": {"usd_micros": 100}},
            "CapabilityGranted": {"grantId": "g1", "actions": ["fs.read"]},
            "CapabilityAttenuated": {"grantId": "g2", "parentGrantId": "g1", "actions": ["fs.read"]},
            "CapabilityRevoked": {"grantId": "g1"},
            "TurnStarted": {"turn": 1},
            "EpisodeStarted": {},
            "EpisodeStateChanged": {"toState": "active"},
            "EpisodeCompleted": {"outcome": "resolved"},
            "ArtifactCreated": {"id": "art-1", "kind": "M"},
            "ActivationChanged": {"artifactId": "art-1", "toStatus": "active"},
            "EvidenceClaimProduced": {"claimId": "cl-1", "subject": "s", "predicate": "p"},
            "ApprovalRequested": {"approvalId": "ap-1", "reason": "r"},
            "ApprovalResolved": {"approvalId": "ap-1", "resolution": "approved"},
            "Heartbeat": {"leaseId": "l1"},
            "ConflictDetected": {"resource": "res"},
            "RunRecovered": {"recoveredBy": "agent-1"},
            "RunAborted": {"reason": "aborted"},
            "AuthorizationDenied": {"reason": "denied"},
            "ObservationProduced": {"snapshot": "snap"},
            "ProposalProduced": {"toolCalls": []},
            # ADR-0090. Both kinds left UNFOLDED_ALLOWLIST when the fold landed,
            # but neither got a dummy payload, so the loop fed them `{}` and the
            # branch skipped an event it could not identify -- passing this test
            # while folding nothing. The reducer now denies an unidentifiable
            # child event, so these payloads are what exercises the real fold.
            "ChildSpawned": {"parentEpisodeId": "ep-test", "childEpisodeId": "ep-child",
                             "authority": ["fs.read"], "depth": 1,
                             "lineage": ["ep-test"], "settledIntentKey": "intent-1"},
            "ChildReturned": {"childEpisodeId": "ep-child", "outcome": "completed",
                              "terminal": "ok", "cost": {"usd_micros": 1},
                              "settledIntentKey": "intent-1"},
        }

        # Kinds whose fold legitimately denies without a predecessor. Seeding it
        # is not a relaxation: `ChildReturned` MUST reject an orphan return
        # (ADR-0090), so the only honest way to exercise its fold is to give it
        # the spawn it is closing.
        prerequisites = {
            "ChildReturned": ("ChildSpawned", dummy_payloads["ChildSpawned"]),
        }

        for seq, kind in enumerate(sorted(EVENT_KINDS), 1):
            if kind in UNFOLDED_ALLOWLIST:
                continue
            payload = dummy_payloads.get(kind, {})
            state = initial_state("run-test", "ep-test")
            prerequisite = prerequisites.get(kind)
            if prerequisite is not None:
                state = reduce_event(state, self._envelope(seq, *prerequisite))
                seq += 1
            env = self._envelope(seq, kind, payload)
            state = reduce_event(state, env)
            if state.unknown_events:
                unhandled_silently.append(kind)

        self.assertEqual(
            unhandled_silently,
            [],
            f"Kinds in EVENT_KINDS silently falling into unknown_events (need fold rule or allowlist): {unhandled_silently}",
        )

    def test_effect_failed_closes_inflight_effect_cleanly(self) -> None:
        s0 = initial_state("run-1", "ep-1")
        e_start = self._envelope(1, "EffectStarted", {"descriptorDigest": "d-fail", "sinkClass": "fs"})
        s1 = reduce_event(s0, e_start)
        self.assertEqual(s1.effects["d-fail"].status, "started")

        e_fail = self._envelope(2, "EffectFailed", {"descriptorDigest": "d-fail", "error": "io_error"})
        s2 = reduce_event(s1, e_fail)
        self.assertEqual(s2.effects["d-fail"].status, "failed")
        self.assertEqual(s2.effects["d-fail"].outcome, "io_error")
        self.assertEqual(s2.unknown_events, ())

    def test_effect_rejected_closes_inflight_effect_cleanly(self) -> None:
        s0 = initial_state("run-1", "ep-1")
        e_start = self._envelope(1, "EffectStarted", {"descriptorDigest": "d-rej", "sinkClass": "fs"})
        s1 = reduce_event(s0, e_start)
        e_rej = self._envelope(2, "EffectRejected", {"descriptorDigest": "d-rej", "reason": "policy_denial"})
        s2 = reduce_event(s1, e_rej)
        self.assertEqual(s2.effects["d-rej"].status, "rejected")
        self.assertEqual(s2.effects["d-rej"].outcome, "policy_denial")
        self.assertEqual(s2.unknown_events, ())

    def test_turn_started_records_episode_transition(self) -> None:
        s0 = initial_state("run-1", "ep-1")
        e_start = self._envelope(1, "EpisodeStarted", {})
        s1 = reduce_event(s0, e_start)
        e_turn = self._envelope(2, "TurnStarted", {"turn": 1})
        s2 = reduce_event(s1, e_turn)
        self.assertEqual(s2.episode.status, "active")
        self.assertEqual(s2.unknown_events, ())
        transitions = s2.episode.state_transitions
        self.assertTrue(any("TurnStarted:1" in (t[2] or "") for t in transitions))

    def test_capability_attenuated_records_child_grant(self) -> None:
        s0 = initial_state("run-1", "ep-1")
        e_grant = self._envelope(1, "CapabilityGranted", {"grantId": "g-parent", "actions": ["fs.read", "fs.write"]})
        s1 = reduce_event(s0, e_grant)
        e_att = self._envelope(2, "CapabilityAttenuated", {"grantId": "g-child", "parentGrantId": "g-parent", "actions": ["fs.read"]})
        s2 = reduce_event(s1, e_att)
        self.assertIn("g-child", s2.grants)
        self.assertEqual(s2.grants["g-child"]["parentGrantId"], "g-parent")
        self.assertEqual(s2.grants["g-child"]["actions"], ["fs.read"])
        self.assertEqual(s2.unknown_events, ())

    def test_budget_exhausted_records_debits_and_lease_state(self) -> None:
        s0 = initial_state("run-1", "ep-1")
        e_res = self._envelope(1, "BudgetReserved", {"leaseId": "l-1", "dimensions": {"usd_micros": 1000}})
        s1 = reduce_event(s0, e_res)
        e_exh = self._envelope(2, "BudgetExhausted", {"leaseId": "l-1", "debits": {"usd_micros": 1000}})
        s2 = reduce_event(s1, e_exh)
        self.assertEqual(s2.cumulative_budget_debits.get("usd_micros"), 1000)
        self.assertTrue(s2.leases["l-1"].is_released)
        self.assertEqual(s2.unknown_events, ())

    def test_plugin_lifecycle_walk_records_state_transitions(self) -> None:
        s = initial_state("run-1", "ep-1")
        events = [
            self._envelope(1, "PluginResolved", {"plugin_id": "echo", "manifest_digest": "sha256:111"}),
            self._envelope(2, "PluginActivated", {"plugin_id": "echo"}),
            self._envelope(3, "PluginQuiesced", {"plugin_id": "echo"}),
            self._envelope(4, "PluginRetired", {"plugin_id": "echo"}),
            self._envelope(5, "PluginFaulted", {"plugin_id": "faulty", "reason": "crashed"}),
        ]
        final = s
        for env in events:
            final = reduce_event(final, env)

        self.assertEqual(final.unknown_events, ())
        self.assertIn("echo", final.plugins)
        self.assertEqual(final.plugins["echo"].status, "retired")
        self.assertIn("faulty", final.plugins)
        self.assertEqual(final.plugins["faulty"].status, "faulted")
        self.assertEqual(final.plugins["faulty"].reason, "crashed")


if __name__ == "__main__":
    unittest.main()
