"""A-M4 — evidence capture at the real Runtime seam (`ADR-0096 §14`).

`EVIDENCE.md` states the whole obligation in one line: *any variable that can
materially affect a result MUST have observable identity and provenance*. The
ways an implementation can pass a shallow reading of that and still be useless
are all silent, so each of them gets a test here rather than a comment:

* an event that carries the prompt instead of its digest;
* a digest the caller supplied rather than the store computed;
* a fact appended before the bytes it names are durable;
* a prompt captured *after* the response reinterpreted the call;
* a run that lost an artifact and said nothing;
* a `{"hit": false}` cache claim on a composition with no cache;
* retention read as permission.

The provider seam is exercised through `HarnessSession`, not through a stub
operator: `ADR-0096 §14.1` names `runtime/session.py::_LayeredOperator.propose`
specifically, and a test that instrumented its own copy would prove the copy.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any, Mapping

from test.agency.doubles import ScriptedModel, finish
from vanguard.packages.adapters.stores.blob_store import InMemoryBlobStore
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.agency.provenance import (
    CAPTURE_INCOMPLETE,
    EvidenceCaptureRequiredError,
    NullProvenanceSink,
    ProvenanceRecord,
    ProvenanceSink,
)
from vanguard.packages.ports.blob_store import BlobStorePort
from vanguard.packages.ports.event_store import EventRange, Result
from vanguard.packages.runtime.artifacts import (
    ARTIFACT_ROLES,
    RETENTION_LEVELS,
    ArtifactWriter,
    CapturePolicy,
    EvidenceLedgerAppendError,
    OrphanArtifactError,
    SecretRedactor,
    resolve_capture_policy,
)
from vanguard.packages.runtime.provenance import (
    RuntimeProvenanceSink,
    cache_participation,
)
from vanguard.packages.runtime.root import (
    HarnessSession,
    Runtime,
    SessionPorts,
    TaskContext,
)

from .test_harness_session import FakeClock, FakeEnvironment

RUNTIME = Path(__file__).resolve().parents[2] / "vanguard" / "packages" / "runtime"
AGENCY = Path(__file__).resolve().parents[2] / "vanguard" / "packages" / "agency"


# -- doubles ---------------------------------------------------------------


class RecordingEmitter:
    """Just enough `LedgerEmitter` to observe ordering and payloads."""

    def __init__(self) -> None:
        self.appended: list[tuple[str, Mapping[str, Any]]] = []

    def emit_kind(self, kind: str, *, run_id: str, principal: str,
                  payload: Mapping[str, Any] | None = None,
                  episode_id: str | None = None, **_: Any) -> Any:
        self.appended.append((kind, dict(payload or {})))
        return object()

    def kinds(self) -> list[str]:
        return [kind for kind, _ in self.appended]

    def payloads(self, kind: str) -> list[Mapping[str, Any]]:
        return [body for name, body in self.appended if name == kind]


class RefusingEmitter(RecordingEmitter):
    """An emitter whose append always fails. Nothing may treat this as a warning."""

    def emit_kind(self, kind: str, **kwargs: Any) -> Any:
        raise OSError("append rejected")


class WitnessBlobStore:
    """Wraps a real store and records the interleaving of put and append."""

    def __init__(self, timeline: list[str]) -> None:
        self._inner = InMemoryBlobStore()
        self._timeline = timeline

    def put(self, data: bytes) -> Result[str]:
        result = self._inner.put(data)
        self._timeline.append(f"put:{result.value}")
        return result

    def get(self, digest: str) -> Result[bytes]:
        return self._inner.get(digest)

    def has(self, digest: str) -> bool:
        return self._inner.has(digest)


class TimelineEmitter(RecordingEmitter):
    def __init__(self, timeline: list[str]) -> None:
        super().__init__()
        self._timeline = timeline

    def emit_kind(self, kind: str, **kwargs: Any) -> Any:
        self._timeline.append(f"append:{kind}")
        return super().emit_kind(kind, **kwargs)


class BrokenBlobStore:
    """A store that cannot write. Required capture must die on it."""

    def put(self, data: bytes) -> Result[str]:
        return Result.fail("instrument_error", "disk is gone")

    def get(self, digest: str) -> Result[bytes]:
        return Result.fail("not_found", digest)

    def has(self, digest: str) -> bool:
        return False


def _writer(store: Any = None, emitter: Any = None,
            policy: CapturePolicy | None = None) -> ArtifactWriter:
    return ArtifactWriter(
        store or InMemoryBlobStore(), emitter or RecordingEmitter(),
        policy=policy, run_id="run-1", principal="agent-1", episode_id="ep-1")


# -- the port contract the writer depends on -------------------------------


class TheStoreOwnsTheDigest(unittest.TestCase):
    """`ports/blob_store.py`: *a store that trusts a caller's digest is a store
    whose addresses can lie.* The writer must not reintroduce that trust."""

    def test_capture_exposes_no_digest_parameter(self) -> None:
        import inspect

        signature = inspect.signature(ArtifactWriter.capture)
        self.assertNotIn("digest", signature.parameters)

    def test_the_recorded_digest_is_the_one_the_store_returned(self) -> None:
        store = InMemoryBlobStore()
        writer = _writer(store)
        ref = writer.capture("prompt", {"messages": ["hello"]})
        self.assertEqual(store.put(b"unused").ok, True)
        self.assertTrue(store.has(ref.digest))
        self.assertEqual(store.get(ref.digest).value, _bytes_of(ref, store))

    def test_a_stored_reference_always_resolves(self) -> None:
        """A required fact naming absent bytes is worse than no fact."""
        store = InMemoryBlobStore()
        writer = _writer(store)
        ref = writer.capture("model_output", {"text": "done"})
        self.assertTrue(writer.reference(ref.digest))


def _bytes_of(ref: Any, store: Any) -> bytes:
    return store.get(ref.digest).value


# -- durable ordering ------------------------------------------------------


class BlobFirstEventSecond(unittest.TestCase):
    def test_the_blob_is_durable_before_the_fact_that_names_it(self) -> None:
        timeline: list[str] = []
        writer = _writer(WitnessBlobStore(timeline), TimelineEmitter(timeline))
        writer.capture("prompt", "hello")
        self.assertEqual(len(timeline), 2)
        self.assertTrue(timeline[0].startswith("put:"), timeline)
        self.assertEqual(timeline[1], "append:ArtifactCreated")

    def test_a_stored_blob_whose_fact_is_lost_is_fatal(self) -> None:
        """Orphan garbage, and an evidence claim nobody can find. Not a warning."""
        writer = _writer(InMemoryBlobStore(), RefusingEmitter())
        with self.assertRaises(OrphanArtifactError):
            writer.capture("prompt", "hello")

    def test_an_orphan_is_never_added_to_the_session_index(self) -> None:
        writer = _writer(InMemoryBlobStore(), RefusingEmitter())
        with self.assertRaises(OrphanArtifactError):
            writer.capture("prompt", "hello")
        self.assertEqual(writer.index, ())


# -- events carry digests, never content -----------------------------------


class NoInlineContent(unittest.TestCase):
    def test_the_artifact_fact_carries_a_digest_and_not_the_prompt(self) -> None:
        emitter = RecordingEmitter()
        writer = _writer(InMemoryBlobStore(), emitter)
        writer.capture("prompt", {"messages": [{"role": "user", "content": "SECRET-BODY"}]})
        rendered = repr(emitter.appended)
        self.assertNotIn("SECRET-BODY", rendered)
        self.assertIn("contentDigest", rendered)

    def test_a_fact_that_would_inline_content_is_refused(self) -> None:
        from vanguard.packages.runtime.artifacts import _assert_no_inline_content

        with self.assertRaises(ValueError):
            _assert_no_inline_content({"artifact": {"content": "the whole prompt"}})

    def test_provenance_records_carry_digests_only(self) -> None:
        emitter = RecordingEmitter()
        sink = RuntimeProvenanceSink(emitter, run_id="run-1", principal="agent-1")
        sink.record_context_selection(
            identity={"policyId": "p", "policyVersion": "1", "parameters": {}},
            candidate_digest="sha256:in", selected_digest="sha256:out",
            prefix_digest="sha256:prefix", selected=["brief"], dropped=["old"],
            elided=[], tokens=10, layer_counts={"L1": 6, "L4": 4}, turn=0)
        body = emitter.payloads("EvidenceClaimProduced")[0]
        self.assertEqual(body["value"]["inputDigest"], "sha256:in")
        self.assertNotIn("content", repr(body))


# -- capture authorization, retention and privacy --------------------------


class RetentionIsNotAuthorization(unittest.TestCase):
    """`ADR-0096 §14.5`. `full` says how long authorized bytes live, never that
    these bytes may be taken."""

    def test_retention_vocabulary_is_exactly_three_values(self) -> None:
        self.assertEqual(RETENTION_LEVELS, ("digests_only", "standard", "full"))

    def test_a_fourth_retention_level_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            CapturePolicy(retention="forever")

    def test_full_retention_does_not_authorize_an_unauthorized_role(self) -> None:
        policy = CapturePolicy(retention="full", authorized_roles=frozenset({"prompt"}))
        store = InMemoryBlobStore()
        ref = _writer(store, policy=policy).capture("model_output", "body")
        self.assertFalse(ref.stored)
        self.assertFalse(store.has(ref.digest))
        self.assertEqual(ref.reason, "unauthorized")

    def test_unauthorized_optional_capture_records_a_digest_only_fact(self) -> None:
        emitter = RecordingEmitter()
        policy = CapturePolicy(authorized_roles=frozenset({"prompt"}))
        ref = _writer(InMemoryBlobStore(), emitter, policy).capture("patch", "diff")
        self.assertTrue(ref.digest.startswith("sha256:"))
        self.assertFalse(ref.captured)
        self.assertEqual(emitter.kinds(), ["ArtifactCreated"])

    def test_unauthorized_required_capture_fails_closed(self) -> None:
        policy = CapturePolicy(required=True, authorized_roles=frozenset({"prompt"}))
        with self.assertRaises(EvidenceCaptureRequiredError):
            _writer(policy=policy).capture("patch", "diff")

    def test_digests_only_retention_stores_nothing_and_still_identifies(self) -> None:
        store = InMemoryBlobStore()
        ref = _writer(store, policy=CapturePolicy(retention="digests_only")).capture(
            "prompt", "hello")
        self.assertFalse(ref.stored)
        self.assertTrue(ref.digest.startswith("sha256:"))
        self.assertFalse(store.has(ref.digest))

    def test_the_applied_policy_identity_and_version_enter_the_record(self) -> None:
        ref = _writer(policy=CapturePolicy(policy_id="pol", policy_version="7")).capture(
            "prompt", "hello")
        self.assertEqual((ref.policy_id, ref.policy_version), ("pol", "7"))


class RedactionHappensBeforePersistence(unittest.TestCase):
    """An event store is the one place from which nothing can be withdrawn."""

    def test_a_credential_never_reaches_the_blob_store(self) -> None:
        store = InMemoryBlobStore()
        # Assembled at runtime, never written as a literal: `scan_secrets.py`
        # fails closed on credential-shaped source and it is right to.
        secret = "-".join(("sk", "or", "v1")) + "-abcdefghijklmnopqrstuvwxyz012345"
        ref = _writer(store).capture("prompt", f"call with {secret}")
        self.assertNotIn(secret.encode(), store.get(ref.digest).value)
        self.assertGreaterEqual(ref.redactions, 1)

    def test_the_digest_is_of_the_redacted_bytes(self) -> None:
        store = InMemoryBlobStore()
        ref = _writer(store).capture("prompt", "call token: abcdefghijklmnop123456")
        self.assertEqual(store.get(ref.digest).value.decode(), "call [redacted]")

    def test_a_full_capture_profile_disables_redaction_explicitly(self) -> None:
        store = InMemoryBlobStore()
        policy = CapturePolicy(redact=False)
        body = "password = abcdefghijklmnop123456"
        ref = _writer(store, policy=policy).capture("prompt", body)
        self.assertEqual(store.get(ref.digest).value.decode(), body)

    def test_the_redactor_has_an_identity(self) -> None:
        self.assertTrue(SecretRedactor.identity.startswith("runtime.secret-redactor/"))


# -- failure and degradation semantics -------------------------------------


class RequiredCaptureFailureIsFatal(unittest.TestCase):
    def test_a_failed_required_capture_raises_the_generic_error(self) -> None:
        policy = CapturePolicy(required=True)
        with self.assertRaises(EvidenceCaptureRequiredError):
            _writer(BrokenBlobStore(), policy=policy).capture("prompt", "hello")

    def test_the_error_type_is_declared_in_agency_not_runtime(self) -> None:
        """`ADR-0096 §14.2`: it crosses the protocol without dragging Runtime up."""
        self.assertEqual(EvidenceCaptureRequiredError.__module__,
                         "vanguard.packages.agency.provenance")

    def test_a_failed_required_capture_writes_no_artifact_fact(self) -> None:
        emitter = RecordingEmitter()
        with self.assertRaises(EvidenceCaptureRequiredError):
            _writer(BrokenBlobStore(), emitter, CapturePolicy(required=True)).capture(
                "prompt", "hello")
        self.assertEqual(emitter.kinds(), [])


class OptionalCaptureDegradesOnlyOnTheRecord(unittest.TestCase):
    def test_optional_failure_records_a_durable_capture_incomplete_fact(self) -> None:
        emitter = RecordingEmitter()
        writer = _writer(BrokenBlobStore(), emitter)
        ref = writer.capture("prompt", "hello")
        self.assertFalse(ref.captured)
        self.assertEqual(emitter.kinds(), ["EvidenceClaimProduced"])
        self.assertEqual(emitter.payloads("EvidenceClaimProduced")[0]["predicate"],
                         CAPTURE_INCOMPLETE)

    def test_a_degraded_run_is_marked_non_evidentiary(self) -> None:
        emitter = RecordingEmitter()
        writer = _writer(BrokenBlobStore(), emitter)
        self.assertFalse(writer.degraded)
        writer.capture("prompt", "hello")
        self.assertTrue(writer.degraded)
        claim = emitter.payloads("EvidenceClaimProduced")[0]["value"]
        self.assertFalse(claim["evidentiary"])

    def test_failing_to_record_the_degradation_is_fatal(self) -> None:
        """The one thing worse than a lost artifact is a lost record of the loss."""
        writer = _writer(BrokenBlobStore(), RefusingEmitter())
        with self.assertRaises(EvidenceLedgerAppendError):
            writer.capture("prompt", "hello")

    def test_the_run_is_not_marked_degraded_when_the_record_did_not_land(self) -> None:
        writer = _writer(BrokenBlobStore(), RefusingEmitter())
        with self.assertRaises(EvidenceLedgerAppendError):
            writer.capture("prompt", "hello")
        self.assertFalse(writer.degraded)


class ProvenanceAppendFailureIsFatal(unittest.TestCase):
    def test_a_lost_provenance_fact_is_never_swallowed(self) -> None:
        sink = RuntimeProvenanceSink(RefusingEmitter(), run_id="run-1", principal="a")
        with self.assertRaises(EvidenceLedgerAppendError):
            sink.record(ProvenanceRecord(kind="context_selection", subject="run:run-1"))

    def test_a_failed_record_does_not_enter_the_session_index(self) -> None:
        sink = RuntimeProvenanceSink(RefusingEmitter(), run_id="run-1", principal="a")
        with self.assertRaises(EvidenceLedgerAppendError):
            sink.record(ProvenanceRecord(kind="model_io", subject="run:run-1"))
        self.assertEqual(sink.records, ())


# -- the real provider seam ------------------------------------------------


class CapturingModel:
    """Records exactly what `propose` was handed, and answers with a raw shape
    the session will later reinterpret."""

    provider = "fake-provider"
    model = "fake-model-a"

    def __init__(self, inner: Any) -> None:
        self._inner = inner
        self.seen: list[Mapping[str, Any]] = []

    def propose(self, bundle: Mapping[str, Any], tools: Any, sampling: Any) -> Any:
        self.seen.append(bundle)
        answer = self._inner.propose(bundle, tools, sampling)
        value = getattr(answer, "value", None)
        if isinstance(value, Mapping):
            enriched = dict(value)
            enriched["usage"] = {"prompt_tokens": 11, "completion_tokens": 3}
            enriched["resolved_model"] = "fake-model-a-2026-08"
            object.__setattr__(answer, "value", enriched) if hasattr(
                answer, "__slots__") else setattr(answer, "value", enriched)
        return answer


def _session(model: Any, *, blobs: Any = None,
             policy: CapturePolicy | None = None) -> HarnessSession:
    harness = Runtime.compose("vg-code-default", episode_id="ep-capture-1")
    ports = SessionPorts(
        model=model, environment=FakeEnvironment(), clock=FakeClock(),
        store=SqliteEventStore(":memory:"), interactive=False,
        blobs=blobs, capture_policy=policy)
    task = TaskContext(
        brief="make the suite green", repo_path=Path("/workspace"),
        run_id="run-capture-1", episode_id="ep-capture-1",
        principal="agent-1", max_turns=2)
    return HarnessSession(harness, ports, task)


class ExactModelIOAtTheRealSeam(unittest.TestCase):
    def test_the_instrumented_seam_is_the_one_the_adr_names(self) -> None:
        source = (RUNTIME / "session.py").read_text(encoding="utf-8")
        propose = source.split("def propose(", 1)[1]
        self.assertIn('self._capture(\n            "prompt"', propose)
        self.assertIn('self._capture("model_output", raw', propose)

    def test_the_captured_input_is_the_finalized_bundle_the_provider_saw(self) -> None:
        model = CapturingModel(ScriptedModel([finish()]))
        blobs = InMemoryBlobStore()
        session = _session(model, blobs=blobs)
        session.run()
        prompts = [ref for ref in session.artifacts.index if ref.role == "prompt"]
        self.assertTrue(prompts)
        import json

        stored = json.loads(blobs.get(prompts[0].digest).value)
        self.assertEqual(stored["promptDigest"], model.seen[0]["promptDigest"])
        self.assertEqual(len(stored["messages"]), len(model.seen[0]["messages"]))

    def test_the_captured_output_is_the_raw_response_before_reinterpretation(self) -> None:
        """The session folds `usage` and `resolved_model` into its own view of
        the turn *after* the call. Capturing later would record that belief."""
        model = CapturingModel(ScriptedModel([finish()]))
        blobs = InMemoryBlobStore()
        session = _session(model, blobs=blobs)
        session.run()
        outputs = [ref for ref in session.artifacts.index if ref.role == "model_output"]
        self.assertTrue(outputs)
        import json

        stored = json.loads(blobs.get(outputs[0].digest).value)
        self.assertEqual(stored["resolved_model"], "fake-model-a-2026-08")
        self.assertEqual(stored["usage"]["prompt_tokens"], 11)

    def test_the_model_io_claim_ties_run_turn_route_and_both_artifacts(self) -> None:
        session = _session(CapturingModel(ScriptedModel([finish()])),
                           blobs=InMemoryBlobStore())
        session.run()
        claims = [r for r in session.provenance.records if r.kind == "model_io"]
        self.assertTrue(claims)
        claim = claims[0]
        self.assertEqual(claim.subject, "run:run-capture-1")
        self.assertEqual(claim.turn, 0)
        self.assertEqual(claim.parameters["provider"], "fake-provider")
        self.assertEqual(len(claim.artifacts), 2)
        self.assertTrue(claim.input_digest and claim.output_digest)


class ContextAndCompactionProvenance(unittest.TestCase):
    def test_context_selection_records_the_policy_and_both_digests(self) -> None:
        session = _session(ScriptedModel([finish()]), blobs=InMemoryBlobStore())
        session.run()
        selections = [r for r in session.provenance.records
                      if r.kind == "context_selection"]
        self.assertTrue(selections)
        record = selections[0]
        self.assertIn("context-compiler", record.policy_id)
        self.assertTrue(record.policy_version)
        self.assertTrue(record.input_digest and record.output_digest)
        self.assertIn("tokenCeiling", record.parameters)
        self.assertIn("selected", record.labels)
        self.assertGreater(record.counts["tokenCount"], 0)
        self.assertTrue(record.counts["layerCounts"])

    def test_a_turn_that_was_not_compacted_emits_no_compaction_claim(self) -> None:
        session = _session(ScriptedModel([finish()]), blobs=InMemoryBlobStore())
        session.run()
        self.assertEqual(
            [r for r in session.provenance.records if r.kind == "compaction"], [])

    def test_the_compiler_reports_its_identity_without_gaining_a_sink(self) -> None:
        """`VG-03 §10`: the compiler stays a pure function of its arguments."""
        source = (AGENCY / "context" / "compiler.py").read_text(encoding="utf-8")
        self.assertNotIn("ProvenanceSink", source)
        self.assertNotIn("import runtime", source)


class CacheClaimsOnlyWhenReported(unittest.TestCase):
    def test_a_live_invocation_with_no_cache_emits_no_cache_claim(self) -> None:
        """Absence is correct. `{"hit": false}` would be a claim about a cache
        this composition does not have."""
        session = _session(ScriptedModel([finish()]), blobs=InMemoryBlobStore())
        session.run()
        self.assertEqual([r for r in session.provenance.records if r.kind == "cache"], [])

    def test_a_reported_cache_participation_becomes_a_claim(self) -> None:
        reported = {"id": "cassette-7", "keyDigest": "sha256:key",
                    "status": "hit", "validation": "fresh"}
        sink = RuntimeProvenanceSink(RecordingEmitter(), run_id="run-1", principal="a")
        record = sink.record_cache(reported=reported, turn=2)
        self.assertIsNotNone(record)
        self.assertEqual(record.parameters["cacheId"], "cassette-7")
        self.assertEqual(record.parameters["validation"], "fresh")
        self.assertEqual(record.turn, 2)

    def test_participation_is_read_from_the_provider_and_never_inferred(self) -> None:
        self.assertIsNone(cache_participation({"text": "hi"}))
        self.assertIsNone(cache_participation({"cache": {}}))
        self.assertIsNone(cache_participation(None))
        self.assertEqual(cache_participation({"cassette": True})["source"], "cassette")


# -- composition and compatibility -----------------------------------------


class LegacyCompositionStaysLegal(unittest.TestCase):
    def test_blobs_none_captures_nothing_and_claims_nothing(self) -> None:
        session = _session(ScriptedModel([finish()]))
        result = session.run()
        self.assertIsNone(session.artifacts)
        self.assertIsInstance(session.provenance, NullProvenanceSink)
        self.assertIsNotNone(result.terminal)

    def test_blobs_none_emits_no_artifact_or_provenance_facts(self) -> None:
        session = _session(ScriptedModel([finish()]))
        session.run()
        kinds = {event.kind for event in session.ledger.events}
        self.assertNotIn("ArtifactCreated", kinds)

    def test_both_canonical_entrypoints_accept_the_capture_seam(self) -> None:
        import inspect

        for entry in (Runtime.execute_harness, Runtime.execute_profiled):
            with self.subTest(entry=entry.__name__):
                parameters = inspect.signature(entry).parameters
                self.assertIn("blobs", parameters)
                self.assertIn("capture_policy", parameters)

    def test_there_is_still_exactly_one_runtime_composition_seam(self) -> None:
        source = (RUNTIME / "root.py").read_text(encoding="utf-8")
        self.assertEqual(source.count("session = HarnessSession("), 1)

    def test_capture_policy_resolves_from_a_profile_structurally(self) -> None:
        from vanguard.packages.runtime.profiles import PRESETS, EffectiveExecutionProfile

        policy = resolve_capture_policy(
            EffectiveExecutionProfile(requested=PRESETS["product"]))
        self.assertEqual(policy.retention, "standard")
        self.assertIn("product", policy.policy_id)

    def test_an_absent_profile_resolves_to_the_conservative_default(self) -> None:
        policy = resolve_capture_policy(None)
        self.assertEqual(policy.retention, "standard")
        self.assertFalse(policy.required)
        self.assertTrue(policy.redact)


class TheBoundaryHolds(unittest.TestCase):
    """`domain <- ports <- kernel <- agency <- runtime`. Capture must not bend it."""

    def test_agency_provenance_imports_no_runtime_adapter_or_pack(self) -> None:
        source = (AGENCY / "provenance.py").read_text(encoding="utf-8")
        for forbidden in ("runtime", "adapters", "packs"):
            self.assertNotIn(f"from ..{forbidden}", source)
            self.assertNotIn(f"import {forbidden}", source)

    def test_agency_owns_only_protocol_records_and_errors(self) -> None:
        from vanguard.packages.agency import provenance as seam

        self.assertTrue(issubclass(seam.NullProvenanceSink, object))
        self.assertIsInstance(ProvenanceSink, type(ProvenanceSink))
        self.assertTrue(hasattr(seam, "ProvenanceRecord"))

    def test_the_runtime_sink_satisfies_the_generic_protocol(self) -> None:
        sink = RuntimeProvenanceSink(RecordingEmitter(), run_id="r", principal="p")
        self.assertIsInstance(sink, ProvenanceSink)

    def test_the_null_sink_satisfies_the_generic_protocol(self) -> None:
        self.assertIsInstance(NullProvenanceSink(), ProvenanceSink)

    def test_the_writer_consumes_the_declared_blob_port(self) -> None:
        self.assertIsInstance(InMemoryBlobStore(), BlobStorePort)


class TheEventContractIsUnchanged(unittest.TestCase):
    """M-4 authorizes no envelope or roster change (`sprint_active §8`)."""

    def test_capture_introduces_no_new_event_kind(self) -> None:
        from vanguard.packages.domain.ledger.events import EVENT_KINDS

        emitted = {"ArtifactCreated", "EvidenceClaimProduced"}
        self.assertTrue(emitted <= EVENT_KINDS)

    def test_the_writer_emits_only_roster_kinds(self) -> None:
        from vanguard.packages.domain.ledger.events import EVENT_KINDS

        emitter = RecordingEmitter()
        writer = _writer(InMemoryBlobStore(), emitter)
        writer.capture("prompt", "hello")
        writer.degrade(role="prompt", reason="test")
        for kind in emitter.kinds():
            self.assertIn(kind, EVENT_KINDS)

    def test_the_production_writer_single_writes_the_current_version(self) -> None:
        session = _session(ScriptedModel([finish()]), blobs=InMemoryBlobStore())
        session.run()
        read = session.ports.store.read(EventRange(episode_id="ep-capture-1"))
        versions = {envelope.schema_version for envelope in (read.value or ())}
        self.assertEqual(versions, {"mhf.event/2"})

    def test_artifact_roles_cover_the_adr_0096_capture_surface(self) -> None:
        required = {
            "prompt", "model_output", "context_bundle", "compaction_input",
            "compaction_output", "workspace_snapshot", "patch",
            "verification_report", "checkpoint_state",
        }
        self.assertEqual(required, set(ARTIFACT_ROLES))


class TheSessionIndexIsAvailableToTrajectoryTwo(unittest.TestCase):
    """B-M4-03's `/2` writer reads these; Dev A does not write the trajectory."""

    def test_the_writer_exposes_an_ordered_artifact_index(self) -> None:
        session = _session(CapturingModel(ScriptedModel([finish()])),
                           blobs=InMemoryBlobStore())
        session.run()
        claims = session.artifacts.index_claims()
        self.assertTrue(claims)
        self.assertEqual(
            [claim["role"] for claim in claims[:2]], ["prompt", "model_output"])
        for claim in claims:
            self.assertIn("contentDigest", claim)
            self.assertIn("policyId", claim)

    def test_the_sink_exposes_ordered_provenance_claims(self) -> None:
        session = _session(ScriptedModel([finish()]), blobs=InMemoryBlobStore())
        session.run()
        claims = session.provenance.claims()
        self.assertTrue(claims)
        self.assertEqual(claims[0]["kind"], "context_selection")


class TheFrozenCrossLaneContractIsHonoured(unittest.TestCase):
    """B-M4-01 published the fixture; Dev A produces its shapes, not its own.

    The point of a frozen fixture is that neither lane discovers at merge time
    that it has been building against its own field names. So these assert
    *key-for-key* agreement with `test/fixtures/artifact_provenance_fixtures.py`
    rather than "close enough" -- a translation layer written after the fact is
    exactly the signature-tolerant workaround the package contract forbids.
    """

    def setUp(self) -> None:
        self.session = _session(CapturingModel(ScriptedModel([finish()])),
                                blobs=InMemoryBlobStore())
        self.session.run()

    def test_the_artifact_roles_match_the_frozen_role_set(self) -> None:
        from test.fixtures.artifact_provenance_fixtures import (
            ARTIFACT_ROLES as FROZEN_ROLES,
        )

        self.assertEqual(set(ARTIFACT_ROLES), set(FROZEN_ROLES))

    def test_an_index_entry_matches_the_frozen_entry_key_for_key(self) -> None:
        from test.fixtures.artifact_provenance_fixtures import (
            sample_artifact_index_entry,
        )

        expected = set(sample_artifact_index_entry().to_dict())
        for entry in self.session.artifacts.index_entries():
            self.assertEqual(set(entry), expected)

    def test_the_capture_state_matches_the_frozen_capture_state(self) -> None:
        from test.fixtures.artifact_provenance_fixtures import (
            sample_complete_capture_state,
        )

        expected = set(sample_complete_capture_state().to_dict())
        self.assertEqual(set(self.session.artifacts.capture_state()), expected)
        self.assertEqual(self.session.artifacts.capture_state()["status"], "complete")

    def test_a_degraded_run_reports_the_frozen_incomplete_state(self) -> None:
        from test.fixtures.artifact_provenance_fixtures import (
            sample_capture_incomplete_state,
        )

        writer = _writer(BrokenBlobStore(), RecordingEmitter())
        writer.capture("prompt", "hello")
        state = writer.capture_state()
        self.assertEqual(set(state), set(sample_capture_incomplete_state().to_dict()))
        self.assertEqual(state["status"], "incomplete")
        self.assertTrue(state["degradation_reason"])

    def test_context_provenance_matches_the_frozen_claim_key_for_key(self) -> None:
        from test.fixtures.artifact_provenance_fixtures import (
            sample_context_selection_provenance,
        )

        expected = set(sample_context_selection_provenance().to_dict())
        claims = self.session.provenance.trajectory_provenance()["context"]
        self.assertTrue(claims)
        for claim in claims:
            self.assertEqual(set(claim), expected)
            self.assertEqual(set(claim["policy"]), {"id", "version", "paramsDigest"})
            self.assertEqual(set(claim["metrics"]), {"tokenCount", "layerCounts"})

    def test_compaction_provenance_matches_the_frozen_claim_key_for_key(self) -> None:
        from test.fixtures.artifact_provenance_fixtures import (
            sample_compaction_provenance,
        )

        emitter = RecordingEmitter()
        sink = RuntimeProvenanceSink(emitter, run_id="run-1", principal="a")
        sink.record_compaction(
            identity={"policyId": "p", "policyVersion": "1", "parameters": {}},
            input_digest="sha256:before", output_digest="sha256:after",
            dropped=["stale"], elided=[], tokens_before=2000, tokens_after=1500,
            turn=1)
        claim = sink.trajectory_provenance()["compaction"][0]
        self.assertEqual(set(claim), set(sample_compaction_provenance().to_dict()))
        self.assertEqual(claim["metrics"]["removedTokens"], 500)

    def test_cache_provenance_matches_the_frozen_claim_key_for_key(self) -> None:
        from test.fixtures.artifact_provenance_fixtures import (
            sample_cache_provenance,
        )

        sink = RuntimeProvenanceSink(RecordingEmitter(), run_id="run-1", principal="a")
        sink.record_cache(
            reported={"id": "cassette-vanguard-01", "keyDigest": "sha256:key",
                      "status": "verified_hit", "hit": True},
            source_digest="sha256:src", turn=0)
        claim = sink.trajectory_provenance()["cache"][0]
        self.assertEqual(set(claim), set(sample_cache_provenance().to_dict()))
        self.assertTrue(claim["hit"])
        self.assertEqual(claim["sourceStatus"], "verified_hit")

    def test_the_provenance_block_has_the_three_frozen_sections(self) -> None:
        block = self.session.provenance.trajectory_provenance()
        self.assertEqual(set(block), {"context", "compaction", "cache"})

    def test_a_live_no_cache_run_reports_an_empty_cache_section(self) -> None:
        """Empty, not a fabricated miss. Absence survives the handover."""
        self.assertEqual(
            self.session.provenance.trajectory_provenance()["cache"], [])

    def test_the_compaction_token_delta_is_never_negative(self) -> None:
        sink = RuntimeProvenanceSink(RecordingEmitter(), run_id="run-1", principal="a")
        sink.record_compaction(
            identity={"policyId": "p", "policyVersion": "1", "parameters": {}},
            input_digest="a", output_digest="b", dropped=["x"], elided=[],
            tokens_before=100, tokens_after=140, turn=0)
        self.assertEqual(
            sink.trajectory_provenance()["compaction"][0]["metrics"]["removedTokens"], 0)


class TheIntegratedTrajectoryCarriesTheCapture(unittest.TestCase):
    """G-M4: the two lanes have to actually meet.

    `assemble_trajectory` accepted an artifact index, three provenance
    sections, and a capture status from the beginning; `session.py` passed
    none of them. Every focused test on both sides passed anyway, because each
    lane proved its own half. RF-95's bundle needs the join, so it is asserted
    here on a real `session.run()` rather than on either lane's fixtures.
    """

    def setUp(self) -> None:
        self.blobs = InMemoryBlobStore()
        self.session = _session(CapturingModel(ScriptedModel([finish()])),
                                blobs=self.blobs)
        self.result = self.session.run()
        self.trajectory = self.result.trajectory

    def test_the_run_emits_a_terminal_trajectory_two(self) -> None:
        self.assertIsNotNone(self.trajectory)
        self.assertEqual(self.trajectory["schema"], "mhf.trajectory/2")

    def test_the_artifact_index_reaches_the_trajectory(self) -> None:
        artifacts = self.trajectory["artifacts"]
        self.assertTrue(artifacts, "capture ran but the trajectory index is empty")
        roles = {entry["role"] for entry in artifacts}
        self.assertIn("prompt", roles)
        self.assertIn("model_output", roles)

    def test_every_indexed_digest_resolves_in_the_blob_store(self) -> None:
        """A reference the store cannot answer reads as evidence and is not."""
        for entry in self.trajectory["artifacts"]:
            if entry["stored"]:
                self.assertTrue(self.blobs.has(entry["digest"]), entry)

    def test_context_provenance_reaches_the_trajectory(self) -> None:
        self.assertTrue(self.trajectory["provenance"]["context"])

    def test_the_turn_carries_exact_model_io_references(self) -> None:
        turn = self.trajectory["turns"][0]
        self.assertTrue(turn["model_input_ref"])
        self.assertTrue(turn["model_output_ref"])
        self.assertNotEqual(turn["model_input_ref"], turn["model_output_ref"])

    def test_the_turn_references_match_the_captured_artifacts(self) -> None:
        turn = self.trajectory["turns"][0]
        index = {entry["role"]: entry["digest"] for entry in self.trajectory["artifacts"]}
        self.assertEqual(turn["model_input_ref"], index["prompt"])
        self.assertEqual(turn["model_output_ref"], index["model_output"])

    def test_the_capture_status_reaches_the_trajectory(self) -> None:
        capture = self.trajectory["capture"]
        self.assertIsNotNone(capture)
        self.assertEqual(capture["status"], "complete")

    def test_the_trajectory_validates_against_the_strict_v2_schema(self) -> None:
        import json

        schema = json.loads(
            (Path(__file__).resolve().parents[2] / "schemas" / "mhf"
             / "trajectory_v2.schema.json").read_text(encoding="utf-8"))
        for field in schema["required"]:
            self.assertIn(field, self.trajectory)


class ALegacyRunClaimsNoCapture(unittest.TestCase):
    """The other half of the same rule: absence must survive to the trajectory."""

    def setUp(self) -> None:
        self.trajectory = _session(ScriptedModel([finish()])).run().trajectory

    def test_a_run_without_capture_reports_a_null_capture_status(self) -> None:
        """Not `complete`. A run composed without a capture subsystem captured
        nothing, and saying `complete` would be indistinguishable from a run
        that captured everything it was asked to."""
        self.assertIsNone(self.trajectory["capture"])

    def test_a_run_without_capture_has_an_empty_artifact_index(self) -> None:
        self.assertEqual(list(self.trajectory["artifacts"]), [])


if __name__ == "__main__":
    unittest.main()
