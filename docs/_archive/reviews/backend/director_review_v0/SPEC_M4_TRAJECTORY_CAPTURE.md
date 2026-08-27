# SPEC_M4 — Scientific Trajectory Capture & Product Proof (M4-04 a–d, M4-05/RF-95)

Authority: ADR-0096-as-amended §5/§6.2bis/§8, ADR-0097 §2, `01_law/EVIDENCE.md` provenance rule,
milestones §M-4. Constraint in force: **no event-envelope change, no new event kind** before M-5a.
Everything below is payload-, profile-, and runtime-level.

Participants and layers: `agency/context` (protocol only) · `runtime` (all new mechanisms) ·
`adapters/stores` (existing blob stores) · `schemas/mhf` (payload schemas) · `packs/code-default`
(consumer, unchanged) · `test/*`.

---

## 1. New/changed files

| Action | Path | Content |
|---|---|---|
| create | `vanguard/packages/runtime/artifacts.py` | `ArtifactWriter`, `ArtifactWriteError`, `ArtifactRecord` |
| create | `vanguard/packages/agency/context/provenance.py` | `ProvenanceSink` protocol, `ContextSelectionRecord`, `CompactionRecord`, `NullProvenanceSink` |
| create | `vanguard/packages/runtime/provenance.py` | `LedgerProvenanceSink`, `CacheProvenanceRecorder` |
| create | `vanguard/packages/runtime/reproducibility.py` | `ReproducibilityVector`, `assess_reproducibility`, `REPRO_DOMAINS` |
| create | `schemas/mhf/artifact_created.schema.json` | `mhf.artifact-created/1` payload |
| create | `schemas/mhf/provenance_claim.schema.json` | `mhf.provenance-claim/1` payload |
| modify | `vanguard/packages/runtime/profiles.py` | `retention` axis (D-05) |
| modify | `vanguard/packages/runtime/ledger_emitter.py` | `artifact_writer` writer role; `ArtifactCreated` privileged ownership |
| modify | `vanguard/packages/agency/context/compiler.py` | inject `ProvenanceSink`; report selection + compaction |
| modify | `vanguard/packages/runtime/wiring.py`, `runtime/root.py` | construct blob store + writer + sink per profile; pass to engine/compiler |
| modify | `vanguard/packages/adapters/models/invocation.py` (and `cassette.py` seam) | cache-interaction recording hook |
| modify | `vanguard/packages/runtime/trajectory.py`, `schemas/mhf/trajectory.schema.json`, `runtime/trajectory_reader.py` | additive sections (§7) |
| modify | `lab/bench.py` | `bench_append_fold` baseline |
| no change | `ports/blob_store.py`, kernel, domain, envelope schema | — |

Forbidden: imports of `runtime.*` from `agency/*`; inlining blob content into any event payload;
new `EventKind` members; edits to `event_envelope.schema.json`; emitting via unauthorized roles.

---

## 2. ArtifactWriter (D-03)

State ownership: stateless facade over `BlobStorePort` (durable content) + `LedgerEmitter`
(durable fact). Mutable state: none. Concurrency: single-writer per episode (I-11); methods are
synchronous and idempotent per content digest.

```python
# vanguard/packages/runtime/artifacts.py
ARTIFACT_ROLES = frozenset({
    "prompt", "model_output", "context_bundle", "compaction_input",
    "compaction_output", "workspace_snapshot", "patch", "verification_report",
    "checkpoint_state",  # reserved for M-5a (D-13)
})

class ArtifactWriteError(RuntimeError):
    """Blob persisted-or-raise failed, or the ledger fact could not be appended.
    Raised only on durability failure; never swallowed (K-06 analogue)."""

@dataclass(frozen=True, slots=True)
class ArtifactRecord:
    artifact_id: str          # uuid7; identity of the *fact*, not the content
    digest: str               # "sha256:…" computed by the store (BlobStorePort law)
    role: str                 # ∈ ARTIFACT_ROLES
    schema_id: str            # e.g. "mhf.prompt/1", "text/plain;v=1"
    size_bytes: int
    retention_class: str      # resolved from ExecutionProfile.retention (§5)
    stored: bool              # False when retention == "digests-only" (digest recorded, bytes dropped)

class ArtifactWriter:
    """Sole production path from bytes to (blob store + ArtifactCreated event).

    Constructor deps: blob: BlobStorePort, emitter: RoleScopedEmitter(role="artifact_writer"),
                      retention: str, clock: Clock.
    """

    def write(
        self, data: bytes, *, role: str, schema_id: str,
        produced_by: Mapping[str, str],          # {"component": "...", "policy_id": "...", "policy_version": "..."}
        refs: Mapping[str, str] | None = None,   # correlation: episode_id/turn/effect idempotency_key…
    ) -> ArtifactRecord:
        """
        Behavior:
          1. digest ← blob.put(data) when retention != "digests-only", else local sha256 (no store).
          2. Emit ArtifactCreated (payload mhf.artifact-created/1, §2.1) via artifact_writer role.
          3. Return ArtifactRecord.
        Idempotency: same bytes ⇒ same digest; blob.put is content-addressed (dedup); a duplicate
          fact for the same (digest, role, episode) MAY be suppressed via an in-episode seen-set.
        Failure: ArtifactWriteError on blob failure (retention requires storage) or append failure.
          Partial state (blob stored, event failed) is tolerated: blobs without facts are garbage,
          facts without blobs are forbidden — order is therefore blob-first, event-second.
        Must not: mutate data; accept caller-supplied digests; emit under any other role.
        """
        ...

    def write_json(self, obj: Mapping[str, Any], **kw) -> ArtifactRecord:
        """JCS-canonicalise then write(); schema_id required in kw."""
        ...
```

### 2.1 `mhf.artifact-created/1` payload (authoritative causal fact)

| field | type | req | semantics / source of truth / validation |
|---|---|---|---|
| `artifactId` | uuid7 str | ✓ | fact identity; writer-generated |
| `digest` | `sha256:` str | ✓ | content identity; **store-computed**; regex-validated |
| `role` | enum ARTIFACT_ROLES | ✓ | consumer routing |
| `schemaId` | str | ✓ | content contract id |
| `sizeBytes` | int ≥ 0 | ✓ | measured |
| `retentionClass` | enum {digests-only, standard, full} | ✓ | resolved profile axis |
| `stored` | bool | ✓ | false ⇒ bytes intentionally not retained |
| `producedBy` | obj {component, policyId, policyVersion} | ✓ | provenance (0096 §6 payload-position rule) |
| `refs` | obj (str→str) | opt | correlation ids; CT-44 open map |

Versioning: `/1` frozen at M-4 close; changes require new minor payload version, never in-place.
Ledger emitter change: `WRITER_ROLES += {"artifact_writer"}`;
`PRIVILEGED_KIND_OWNERS["ArtifactCreated"] = frozenset({"artifact_writer"})` — from this change on,
no other role may append `ArtifactCreated` (authority test required).

---

## 3. ProvenanceSink protocol (D-04, agency side — zero runtime imports)

```python
# vanguard/packages/agency/context/provenance.py
@dataclass(frozen=True, slots=True)
class ContextSelectionRecord:
    policy_id: str; policy_version: str
    params_digest: str            # JCS digest of resolved selection parameters
    input_digest: str             # digest of candidate-layer bundle (pre-fit)
    output_digest: str            # digest of compiled context actually sent
    token_count: int; layer_counts: Mapping[str, int]
    turn_index: int

@dataclass(frozen=True, slots=True)
class CompactionRecord:
    strategy: str                 # COMPACTION_REGISTRY key
    params_digest: str
    input_digest: str; output_digest: str
    tokens_before: int; tokens_after: int; removed_tokens: int
    turn_index: int

class ProvenanceSink(Protocol):
    """Receives digests and small metadata. NEVER receives an obligation to store content —
    content storage is the runtime implementation's decision via ArtifactWriter."""
    def context_selected(self, rec: ContextSelectionRecord, *, input_bundle: bytes | None, output_bundle: bytes | None) -> None: ...
    def compacted(self, rec: CompactionRecord, *, input_bundle: bytes | None, output_bundle: bytes | None) -> None: ...

class NullProvenanceSink:  # default; keeps ContextCompiler dependency-free and tests unchanged
    ...
```

`ContextCompiler.__init__` gains `provenance: ProvenanceSink | None = None`; `compile()` computes
input/output digests via `domain.canonicalisation.digest.digest_of` and calls the sink once per
turn plus once per compaction pass. Invariants: sink failures MUST NOT abort compilation (log +
continue — provenance is evidence, not control flow); digests computed over JCS-canonical forms.

## 4. LedgerProvenanceSink + cache recorder (runtime side)

```python
# vanguard/packages/runtime/provenance.py
class LedgerProvenanceSink:
    """Constructor deps: writer: ArtifactWriter, emitter: RoleScopedEmitter(role="orchestrator"),
    retention: str, episode_id: str.
    Behavior per callback:
      - retention == "full": write input/output bundles as artifacts (roles context_bundle /
        compaction_input / compaction_output); collect ArtifactRecord digests.
      - retention == "standard": write output bundles only; input recorded as digest.
      - retention == "digests-only": no blobs; digests only.
      - Always emit ClaimRecorded with payload mhf.provenance-claim/1 (§4.1).
    Failure: swallow-and-log on artifact failure when retention permits degradation; append_intent
      failure raises (a run whose provenance ledger writes fail is not a scientific run)."""
    ...

class CacheProvenanceRecorder:
    """Wraps the model invocation path (adapters/models/invocation.py seam).
    record(cache_id, key_digest, source_artifact_digest, hit: bool, validated: bool, turn_index)
      → ClaimRecorded claimKind=cache_interaction.
    Applies to cassette/replay providers and any response cache; live-provider runs with no cache
      emit nothing (absence is meaningful and cheap)."""
    ...
```

### 4.1 `mhf.provenance-claim/1` payload

| field | type | req | semantics |
|---|---|---|---|
| `claimKind` | enum {context_selection, compaction, cache_interaction, reproducibility_at_run_close} | ✓ | discriminator |
| `policy` | obj {id, version, paramsDigest} | ✓ (except cache) | which policy, exactly |
| `inputDigest` / `outputDigest` | sha256 str | ✓/✓ (cache: keyDigest/sourceDigest) | material identity |
| `inputArtifacts` / `outputArtifacts` | array[sha256] | opt | present when blobs stored |
| `metrics` | obj (ints) | opt | tokensBefore/After, removedTokens, layerCounts… |
| `turnIndex` | int ≥ 0 | ✓ | correlation with trajectory turn |
| `vector` | obj (only reproducibility kind) | cond | six dimensions per §6 |
| `basis` | array[str] (repro kind) | cond | observable facts used (0096 §8.2) |

Emitted kind: existing `ClaimRecorded` (unprivileged today; emitted via orchestrator/session
facade). M-5a MAY migrate these to dedicated kinds under ADR-0098 — readers key on `claimKind`,
so migration is a writer-side change only.

## 5. ExecutionProfile.retention (D-05)

```python
retention: str = "standard"   # "digests-only" | "standard" | "full"
# __post_init__ additions:
#   retention ∉ domain → ExecutionProfileError
#   assurance_level == "hermetic" and retention != "full" → ExecutionProfileError
# to_dict(): add "retention" (enters profile_digest → D_R; RF-87 extension asserts presence)
# _narrow(): allowed override; may only narrow full→standard→digests-only
# PRESETS: product/local/sandboxed = "standard"; hermetic = "full"
```

## 6. Reproducibility vector (D-06, RF-100 capture) — Amendment A domains

```python
# vanguard/packages/runtime/reproducibility.py
REPRO_DOMAINS = {
  "state_reconstruction":    ("none", "from_checkpoint", "full_cold"),
  "semantic_replay":         ("unverified", "pinned_verified"),
  "external_reexecution":    ("unavailable", "degraded", "available"),
  "artifact_retention":      ("digests_only", "partial", "full"),
  "environment_capture":     ("none", "declared", "snapshot"),
  "provider_model_identity": ("unattributed", "attributed", "attested"),
}

@dataclass(frozen=True, slots=True)
class ReproducibilityVector:
    values: Mapping[str, str]; assessed_at: str; basis: tuple[str, ...]
    reducer_version: str; schema_versions: Mapping[str, str]

def assess_reproducibility(
    *, profile: EffectiveExecutionProfile, model_route: Mapping[str, Any],
    environment: Mapping[str, Any], artifact_index: Sequence[ArtifactRecord],
    pins: Mapping[str, str],            # from runtime/determinism.py
    wal_durable: bool,
) -> ReproducibilityVector:
    """Pure derivation, no I/O. Derivation table (normative):
      state_reconstruction: full_cold iff wal_durable else none  (from_checkpoint reserved M-5a)
      semantic_replay: pinned_verified iff pins complete (reducer+schemas) else unverified
      external_reexecution: available iff live attributable provider with stable route id;
                            degraded for cassette/replayed; unavailable for fake
      artifact_retention: maps profile.retention {digests-only→digests_only, standard→partial, full→full}
      environment_capture: snapshot iff environment carries snapshot digest; declared iff identity
                            fields present; else none
      provider_model_identity: attested iff signed attestation present; attributed iff provider+model
                            ids present; else unattributed
    The executing episode has no write access to this module's inputs beyond ordinary facts —
    the vector is computed by the runtime at EpisodeCompleted (0096 §8.3)."""
    ...
```

Recording: one `ClaimRecorded` `claimKind=reproducibility_at_run_close` immediately before the
terminal trajectory flush; embedded verbatim in the trajectory. Immutability: recomputation later
(`reproducibility_current`, M-5a) is a *new* claim; the run-close claim is never superseded in place.

## 7. Trajectory additive sections (D-07)

`assemble_trajectory(...)` gains keyword inputs `provenance_claims: Sequence[Mapping]`,
`artifact_index: Sequence[ArtifactRecord]`, `reproducibility: ReproducibilityVector | None` and
emits, additively and optionally, top-level members:

```json
"artifacts": [ {"artifactId","digest","role","schemaId","sizeBytes","stored"} … ],
"provenance": { "context": [...], "compaction": [...], "cache": [...] },
"reproducibility_at_run_close": { "values": {...6 dims...}, "assessed_at","basis",
                                   "reducer_version","schema_versions" }
```

`trajectory.schema.json`: add the three optional properties (no version bump; additive within
`mhf.trajectory/1`; reader tolerance already required). `TrajectoryReader.extract_variables`
exposes them for `diff_trajectories` (ablation tooling).

## 8. Sequence — instrumented turn (target)

```mermaid
sequenceDiagram
  participant E as EpisodeEngine
  participant C as ContextCompiler
  participant S as LedgerProvenanceSink
  participant W as ArtifactWriter
  participant B as BlobStore
  participant L as LedgerEmitter
  participant M as ModelAdapter
  participant K as Kernel
  E->>C: compile(spans, budget)
  C->>C: fit + compaction (strategy)
  C->>S: context_selected(rec, bundles)
  S->>W: write(bundle, role=context_bundle)
  W->>B: put(bytes) ⇒ digest
  W->>L: ArtifactCreated (artifact_writer)
  S->>L: ClaimRecorded {context_selection}
  C-->>E: compiled context
  E->>W: write(prompt, role=prompt); write later (model_output)
  E->>M: invoke(context)
  M->>S: cache_interaction (if cache path)
  E->>K: dispatch(EffectRequest)  %% unchanged S0–S12
  Note over E,L: EpisodeCompleted → assess_reproducibility → ClaimRecorded{repro} → trajectory flush
```

## 9. RF-95 execution protocol (M4-05)

Preconditions (all mechanically checkable): D-03…D-07 merged; `pytest test/falsifiers -k "rf100"`
green; frozen task + preregistered verifier committed under `benchmarks/`; `product` profile
resolves with `retention="standard"`; live attributable provider configured (no fake/cassette).
Execution: exactly one candidate via `tools/runners/run_rf95_product_proof.py` through
`Runtime.run_composed`. Evidence bundle: complete terminal `mhf.trajectory/1` **including**
artifacts/provenance/repro sections; non-empty workspace diff; passing verifier receipt; WAL file;
fresh-process reconstruction transcript (`test_resume_from_ledger` pattern executed against the
real WAL). Review: independent reviewer checklist (evidence bundle completeness, no manual event
repair, `D_R` contains profile with retention); Director closes M-4. Failure handling: any gap ⇒
gate stays NO-GO; the run is kept as evidence but not repaired.

## 10. Test plan (M-4)

| Test | Asserts |
|---|---|
| `test/runtime/test_artifact_writer.py` | blob-first/event-second ordering; digest from store; dedup; digests-only mode stores nothing but emits fact with `stored:false`; durability failure raises |
| emitter authority extension | only `artifact_writer` may append `ArtifactCreated`; others → `WriterAuthorityError` |
| `test/agency/test_context_provenance.py` | sink receives correct digests per turn/compaction; sink failure never aborts compile; NullSink default preserves legacy behavior byte-for-byte |
| `test/runtime/test_provenance_claims.py` | claim payloads validate against schema; retention modes store/skip bundles correctly; cache recorder emits on cassette hit |
| `test/contracts/test_provenance_payload_vectors.py` | JCS golden vectors for both payload schemas |
| `test/runtime/test_profile_retention.py` | retention in `to_dict`/`profile_digest`; hermetic⇒full; narrow-only override; RF-87 D_R presence |
| `test/falsifiers/test_rf100_reproducibility_vector.py` | derivation table cases; run-close claim immutable; vector present in trajectory; episode cannot author it |
| `test/runtime/test_trajectory_provenance_sections.py` | additive schema validity; reader extraction; old trajectories still parse |
| `lab/bench.py::bench_append_fold` | records baseline events/s and fold μs/event into `benchmarks/` artifact |

Definition of Done for M4-04: all above green in CI; sprint board bullets 1–4 flipped with
file/symbol evidence; no envelope/kind diff (`git diff schemas/mhf/event_envelope.schema.json` empty).
