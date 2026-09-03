"""A-M5A — the `mhf.event/2` substrate migration (`ADR-0098`).

The migration's whole risk is that it is invisible when it goes wrong. A
`/1` preimage that gained a field, a hash chain that forked silently at the
version boundary, an orchestrator that got to claim kernel authority, a
deprecated kind that quietly still writes -- none of these break a green
suite by themselves, and all of them destroy the guarantees the ledger exists
to provide. Each gets a test.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from dataclasses import replace

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.ledger.events import (
    DEPRECATED_KINDS,
    EVENT_KINDS,
    READABLE_KINDS,
    WRITABLE_KINDS,
    EventEnvelope,
    parse_event_envelope,
)
from vanguard.packages.domain.ledger.reducer import reconstruct_state
from vanguard.packages.kernel.model import Event
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.ledger_emitter import (
    EVENT_SCHEMA_VERSION,
    DeprecatedKindError,
    LedgerEmitter,
    ROLE_AUTHORITY_SOURCES,
)

ROOT = Path(__file__).resolve().parents[2]

_LIVE_FOLDED = (
    "ActivationChanged", "ArtifactCreated", "CompetencePriorRecorded",
    "ConflictDetected", "EffectPreviewed", "EpisodeStateChanged",
    "EvidenceClaimProduced", "ObservationProduced",
)
_SEMANTIC = (
    "GoalDeclared", "PlanRevised", "StrategyChanged", "ProgressAssessed",
    "ContextCompacted",
)


def _envelope(seq: int, *, version: str, kind: str = "Heartbeat",
              prev: str | None = None) -> EventEnvelope:
    return EventEnvelope(
        schema_version=version, event_id=f"ev-{seq}", scope="episode",
        seq=str(seq), occurred_at="2026-08-25T00:00:00.000Z",
        recorded_at="2026-08-25T00:00:00.000Z", principal="agent-1",
        principal_role="episode", tenant_id="tenant-default",
        owner_id="owner-platform", confidentiality="internal",
        retention_class="extended", trainability="prohibited",
        redaction_status="none", payload={"kind": kind}, run_id="run-1",
        episode_id="ep-1", project_id="proj-1", principal_id="agent-1",
        harness_digest="sha256:" + "a" * 64, prev_digest=prev,
        mhf_kind=kind, mhf_branch_id="main",
        authority_source="kernel-capability" if version == "mhf.event/2" else None,
        policy_version="1" if version == "mhf.event/2" else None,
    )


def _emitter(store, **kwargs):
    return LedgerEmitter(
        store, episode_id="ep-1", project_id="proj-1", principal_id="agent-1",
        harness_digest="sha256:" + "a" * 64, **kwargs)


class TheV1PreimageIsUntouched(unittest.TestCase):
    """The migration must be invisible to every historical digest."""

    def test_a_v1_envelope_serialises_without_any_authority_key(self) -> None:
        wire = _envelope(1, version="mhf.event/1").to_mhf_dict()
        for key in ("authority_source", "policy_version",
                    "approval_reference", "capability_grant"):
            self.assertNotIn(key, wire)

    def test_a_v1_envelope_holding_authority_values_still_omits_them(self) -> None:
        """Adding them to the preimage would rewrite history to match today."""
        envelope = _envelope(1, version="mhf.event/1")
        envelope = replace(envelope, authority_source="kernel-capability",
                           policy_version="9")
        self.assertNotIn("authority_source", envelope.to_mhf_dict())

    def test_the_v1_digest_is_stable_against_a_pinned_value(self) -> None:
        wire = _envelope(1, version="mhf.event/1").to_mhf_dict(include_digest=False)
        # A literal, so the migration cannot move it silently.
        self.assertEqual(
            digest_of(wire),
            "sha256:5fb1173b8fa42103d16951ea8df1699b7dc55bfb43f3ac07934f6b446ec77434",
        )
        # And the preimage keys, in the order the contract froze.
        self.assertEqual(list(wire), [
            "schema_version", "event_id", "kind", "seq", "occurred_at",
            "run_id", "principal", "payload", "episode_id",
            "parent_episode_id", "project_id", "principal_id",
            "parent_principal_id", "harness_digest", "branch_id",
            "prev_digest", "causation_id", "correlation_id",
            "idempotency_key", "alertable",
        ])

    def test_the_v1_schema_file_is_still_pinned_to_version_one(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "mhf" / "event_envelope.schema.json").read_text())
        self.assertEqual(schema["properties"]["schema_version"]["const"], "mhf.event/1")


class TheV2EnvelopeCarriesAuthority(unittest.TestCase):
    def test_v2_adds_exactly_the_four_adr_fields(self) -> None:
        v1 = set(_envelope(1, version="mhf.event/1").to_mhf_dict(include_digest=False))
        v2 = set(_envelope(1, version="mhf.event/2").to_mhf_dict(include_digest=False))
        self.assertEqual(v2 - v1, {
            "authority_source", "policy_version",
            "approval_reference", "capability_grant"})

    def test_the_v2_schema_requires_the_non_nullable_pair(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "mhf" / "event_envelope_v2.schema.json").read_text())
        self.assertEqual(schema["properties"]["schema_version"]["const"], "mhf.event/2")
        self.assertIn("authority_source", schema["required"])
        self.assertIn("policy_version", schema["required"])

    def test_the_nullable_pair_is_nullable_and_the_other_pair_is_not(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "mhf" / "event_envelope_v2.schema.json").read_text())
        props = schema["properties"]
        self.assertEqual(props["authority_source"]["type"], "string")
        self.assertIn("null", props["approval_reference"]["type"])
        self.assertIn("null", props["capability_grant"]["type"])


class AuthorityComesFromTheRoleNotThePayload(unittest.TestCase):
    """`ADR-0098 Decision 2`: forged or inconsistent values are rejected."""

    def setUp(self) -> None:
        self.store = SqliteEventStore(":memory:")

    def test_the_writer_role_determines_the_authority_source(self) -> None:
        for role, expected in ROLE_AUTHORITY_SOURCES.items():
            with self.subTest(role=role):
                store = SqliteEventStore(":memory:")
                emitter = _emitter(store, role=role)
                envelope = emitter.emit_kind(
                    "Heartbeat", run_id="run-1", principal="agent-1")
                self.assertEqual(envelope.authority_source, expected)

    def test_an_orchestrator_cannot_claim_a_capability_grant(self) -> None:
        """The forgery case: a payload naming a grant does not make the
        orchestrator's append rest on one."""
        emitter = _emitter(self.store, role="orchestrator")
        envelope = emitter.emit_kind(
            "Heartbeat", run_id="run-1", principal="agent-1",
            payload={"grantId": "grant-stolen-1"})
        self.assertIsNone(envelope.capability_grant)
        self.assertEqual(envelope.authority_source, "orchestrator-policy")

    def test_the_kernel_may_bind_a_capability_grant(self) -> None:
        emitter = _emitter(self.store, role="kernel")
        envelope = emitter.emit_kind(
            "CapabilityGranted", run_id="run-1", principal="agent-1",
            payload={"grantId": "grant-real-1"})
        self.assertEqual(envelope.capability_grant, "grant-real-1")

    def test_an_orchestrator_cannot_claim_a_human_approval(self) -> None:
        emitter = _emitter(self.store, role="orchestrator")
        envelope = emitter.emit_kind(
            "Heartbeat", run_id="run-1", principal="agent-1",
            payload={"approvalId": "appr-stolen-1"})
        self.assertIsNone(envelope.approval_reference)

    def test_inapplicable_references_are_null_not_invented(self) -> None:
        emitter = _emitter(self.store, role="kernel")
        envelope = emitter.emit_kind("Heartbeat", run_id="run-1", principal="agent-1")
        self.assertIsNone(envelope.capability_grant)
        self.assertIsNone(envelope.approval_reference)
        self.assertTrue(envelope.authority_source)


class DeprecatedKindsAreReadableAndUnwritable(unittest.TestCase):
    def test_the_register_is_exactly_the_eight_adr_kinds(self) -> None:
        self.assertEqual(DEPRECATED_KINDS, frozenset({
            "ObservationRequested", "OperatorInvoked", "OperatorSelected",
            "CorrectionRecorded", "CandidateBuilt", "CandidateAttested",
            "CanaryPromoted", "RollbackTriggered"}))

    def test_every_deprecated_kind_remains_readable(self) -> None:
        for kind in DEPRECATED_KINDS:
            with self.subTest(kind=kind):
                self.assertIn(kind, READABLE_KINDS)
                self.assertNotIn(kind, WRITABLE_KINDS)

    def test_a_new_write_of_a_deprecated_kind_is_rejected(self) -> None:
        emitter = _emitter(SqliteEventStore(":memory:"), role="orchestrator")
        for kind in sorted(DEPRECATED_KINDS):
            with self.subTest(kind=kind):
                with self.assertRaises(DeprecatedKindError):
                    emitter.emit_kind(kind, run_id="run-1", principal="agent-1")

    def test_a_historical_deprecated_event_still_parses_and_folds(self) -> None:
        wire = _envelope(1, version="mhf.event/1", kind="OperatorInvoked").to_mhf_dict()
        parsed = parse_event_envelope(wire)
        self.assertEqual(parsed.mhf_kind or parsed.payload["kind"], "OperatorInvoked")
        self.assertIsNotNone(reconstruct_state([parsed]))


class TheGeneratedSchemaIsTheSoleVocabulary(unittest.TestCase):
    def test_v4_only_kinds_has_no_references_left(self) -> None:
        hits = []
        for path in (ROOT / "vanguard").rglob("*.py"):
            if "_V4_ONLY_KINDS" in path.read_text(encoding="utf-8"):
                hits.append(str(path.relative_to(ROOT)))
        # The one surviving mention is the comment recording its deletion.
        for hit in hits:
            body = (ROOT / hit).read_text(encoding="utf-8")
            self.assertNotIn("_V4_ONLY_KINDS = frozenset", body, hit)

    def test_event_kinds_derives_only_from_the_generated_schema(self) -> None:
        from vanguard.packages.domain.wire.types_gen import EventKind

        self.assertEqual(EVENT_KINDS, frozenset(k.value for k in EventKind))

    def test_the_eight_live_legacy_kinds_are_folded_in(self) -> None:
        for kind in _LIVE_FOLDED:
            with self.subTest(kind=kind):
                self.assertIn(kind, WRITABLE_KINDS)

    def test_the_five_semantic_kinds_are_allocated_and_writable(self) -> None:
        for kind in _SEMANTIC:
            with self.subTest(kind=kind):
                self.assertIn(kind, WRITABLE_KINDS)

    def test_no_sixth_semantic_kind_entered_without_reopening_the_adr(self) -> None:
        adr = (ROOT / "docs" / "backend" / "reference" / "events.md").read_text()
        for kind in _SEMANTIC:
            self.assertIn(kind, adr)


class MixedVersionChainsReplay(unittest.TestCase):
    """`prev_digest` continuity must survive the version boundary."""

    def test_the_chain_links_across_the_v1_to_v2_boundary(self) -> None:
        store = SqliteEventStore(":memory:")
        first = _envelope(0, version="mhf.event/1")
        first = replace(first, content_digest=digest_of(
            first.to_mhf_dict(include_digest=False)))
        store.append([first])

        emitter = _emitter(store, role="session")
        second = emitter.emit_kind("Heartbeat", run_id="run-1", principal="agent-1")
        self.assertEqual(second.schema_version, "mhf.event/2")
        self.assertEqual(second.prev_digest, first.content_digest,
                         "the hash chain forked at the version boundary")

    def test_a_mixed_chain_folds_to_a_state_in_a_fresh_reduction(self) -> None:
        store = SqliteEventStore(":memory:")
        first = _envelope(0, version="mhf.event/1")
        store.append([first])
        emitter = _emitter(store, role="session")
        emitter.emit_kind("Heartbeat", run_id="run-1", principal="agent-1")

        read = store.read(EventRange(project_id="proj-1"))
        envelopes = list(read.value or ())
        versions = {e.schema_version for e in envelopes}
        self.assertEqual(versions, {"mhf.event/1", "mhf.event/2"})
        state = reconstruct_state(envelopes)
        self.assertEqual(state.event_count, len(envelopes))

    def test_a_v1_event_reads_back_with_no_invented_authority(self) -> None:
        parsed = parse_event_envelope(_envelope(1, version="mhf.event/1").to_mhf_dict())
        self.assertIsNone(parsed.authority_source)
        self.assertIsNone(parsed.policy_version)

    def test_a_v2_event_round_trips_its_authority(self) -> None:
        wire = _envelope(1, version="mhf.event/2").to_mhf_dict()
        parsed = parse_event_envelope(wire)
        self.assertEqual(parsed.schema_version, "mhf.event/2")
        self.assertEqual(parsed.authority_source, "kernel-capability")


class RollbackIsExplicit(unittest.TestCase):
    def test_production_default_is_version_two(self) -> None:
        self.assertEqual(EVENT_SCHEMA_VERSION, "mhf.event/2")

    def test_a_caller_may_switch_the_writer_back_to_version_one(self) -> None:
        emitter = _emitter(SqliteEventStore(":memory:"), role="session",
                           writer_version="mhf.event/1")
        envelope = emitter.emit_kind("Heartbeat", run_id="run-1", principal="agent-1")
        self.assertEqual(envelope.schema_version, "mhf.event/1")
        self.assertNotIn("authority_source", envelope.to_mhf_dict())

    def test_an_unknown_writer_version_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            _emitter(SqliteEventStore(":memory:"), writer_version="mhf.event/3")


class SemanticKindsFoldAndDigest(unittest.TestCase):
    def test_each_semantic_kind_reduces_into_named_state(self) -> None:
        store = SqliteEventStore(":memory:")
        emitter = _emitter(store, role="orchestrator")
        emitter.emit_kind("GoalDeclared", run_id="run-1", principal="agent-1",
                          payload={"goalDigest": "sha256:goal"})
        emitter.emit_kind("PlanRevised", run_id="run-1", principal="agent-1",
                          payload={"planDigest": "sha256:plan"})
        emitter.emit_kind("StrategyChanged", run_id="run-1", principal="agent-1",
                          payload={"toStrategy": "depth-first"})
        emitter.emit_kind("ProgressAssessed", run_id="run-1", principal="agent-1",
                          payload={"assessment": "on-track"})
        emitter.emit_kind("ContextCompacted", run_id="run-1", principal="agent-1",
                          payload={"inputDigest": "sha256:a", "outputDigest": "sha256:b"})

        state = reconstruct_state(list(store.read(EventRange(project_id="proj-1")).value))
        self.assertEqual(len(state.goals), 1)
        self.assertEqual(state.goals[0]["goalDigest"], "sha256:goal")
        self.assertEqual(len(state.plan_revisions), 1)
        self.assertEqual(len(state.strategy_changes), 1)
        self.assertEqual(len(state.progress_assessments), 1)
        self.assertEqual(len(state.context_compactions), 1)
        self.assertEqual(state.unknown_events, ())

    def test_a_goal_never_carries_raw_text_into_the_ledger(self) -> None:
        """`ADR-0098 Decision 5`. The reducer keeps the digest and the
        optional artifact reference; it has nowhere to put prose."""
        store = SqliteEventStore(":memory:")
        emitter = _emitter(store, role="orchestrator")
        emitter.emit_kind("GoalDeclared", run_id="run-1", principal="agent-1",
                          payload={"goalDigest": "sha256:goal",
                                   "goalArtifact": "sha256:artifact"})
        state = reconstruct_state(list(store.read(EventRange(project_id="proj-1")).value))
        self.assertEqual(set(state.goals[0]),
                         {"seq", "occurredAt", "goalDigest", "goalArtifact",
                          "parentGoalDigest"})

    def test_semantic_state_changes_the_state_digest(self) -> None:
        """Folding into state but not into the digest would let two different
        histories collide, which is what RF-96 parity is meant to catch."""
        from vanguard.packages.domain.ledger.state import LedgerState

        empty = LedgerState()
        with_goal = LedgerState(goals=({"goalDigest": "sha256:goal"},))
        self.assertNotEqual(
            digest_of(empty.to_canonical_dict()),
            digest_of(with_goal.to_canonical_dict()))


class ResourceAlgebraIsUnchanged(unittest.TestCase):
    """`ADR-0098 Decision 6`."""

    def test_charged_millis_was_not_introduced(self) -> None:
        for path in (ROOT / "vanguard").rglob("*.py"):
            self.assertNotIn("charged_millis", path.read_text(encoding="utf-8"),
                             str(path))

    def test_the_additive_dimensions_are_exactly_four(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "mhf" / "trajectory.schema.json").read_text())
        cost = schema["$defs"]["CostVector"]
        self.assertEqual(set(cost["required"]),
                         {"usd_micros", "tokens", "bytes", "millis"})

    def test_depth_and_turns_are_not_cost_dimensions(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "mhf" / "trajectory.schema.json").read_text())
        cost = schema["$defs"]["CostVector"]
        self.assertNotIn("depth", cost["properties"])
        self.assertNotIn("turns", cost["properties"])


class FreshProcessMixedReplayParity(unittest.TestCase):
    """RF-96 for the migration: a mixed chain must fold identically in a
    process that never saw it written.

    In-process reduction shares the writer's imports, its module state and its
    caches, so it can agree with the writer for reasons that have nothing to
    do with what reached the disk. Only a second interpreter reading a
    file-backed WAL proves the substrate survives the process that made it.
    """

    def test_a_mixed_chain_reduces_to_the_same_digest_in_a_fresh_process(self) -> None:
        import subprocess
        import sys
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "mixed.sqlite")
            store = SqliteEventStore(db)
            first = _envelope(0, version="mhf.event/1")
            store.append([replace(first, content_digest=digest_of(
                first.to_mhf_dict(include_digest=False)))])
            emitter = _emitter(store, role="session")
            emitter.emit_kind("GoalDeclared", run_id="run-1", principal="agent-1",
                              payload={"goalDigest": "sha256:goal"})
            emitter.emit_kind("Heartbeat", run_id="run-1", principal="agent-1")

            local = reconstruct_state(
                list(store.read(EventRange(project_id="proj-1")).value))
            local_digest = digest_of(local.to_canonical_dict())

            script = (
                "import sys;sys.path.insert(0, %r)\n"
                "from vanguard.packages.adapters.stores.event_store import SqliteEventStore\n"
                "from vanguard.packages.domain.ledger.reducer import reconstruct_state\n"
                "from vanguard.packages.domain.canonicalisation.digest import digest_of\n"
                "from vanguard.packages.ports.event_store import EventRange\n"
                "s=SqliteEventStore(%r)\n"
                "e=list(s.read(EventRange(project_id='proj-1')).value)\n"
                "st=reconstruct_state(e)\n"
                "print(len(e));print(sorted({x.schema_version for x in e}));"
                "print(digest_of(st.to_canonical_dict()))\n"
            ) % (str(ROOT), db)
            out = subprocess.run([sys.executable, "-c", script], cwd=str(ROOT),
                                 capture_output=True, text=True, timeout=120)
            self.assertEqual(out.returncode, 0, out.stderr)
            count, versions, digest = out.stdout.strip().splitlines()

        self.assertEqual(int(count), 3)
        self.assertEqual(versions, "['mhf.event/1', 'mhf.event/2']",
                         "the fixture stopped being a mixed chain")
        self.assertEqual(digest, local_digest,
                         "a fresh process reduced the mixed chain differently")


if __name__ == "__main__":
    unittest.main()
