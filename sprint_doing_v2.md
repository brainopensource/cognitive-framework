Part 0 — Cross-cutting patterns (the foundation every phase builds on)

These six patterns appear in every milestone. If you get them wrong once, you rewrite everything later.

P1 — Event sourcing with content-addressed artifacts. Small durable causal facts live in the ledger; large bytes live in a blob store keyed by sha256. The
invariant is blob-first, event-second: never inline large content in an event, never accept a caller-supplied digest (recompute it), never let an event
reference an artifact that isn't durably present first.

P2 — Hexagonal direction. Dependency flow is strictly domain ← ports ← kernel ← agency ← runtime → adapters. Kernel is domain-blind and never imports
agency/runtime/adapters. Agency never imports runtime/adapters/packs. Any new upward import is an escalation trigger, not an implementation choice.

P3 — Capability attenuation (monotonic). A child scope can only lose capabilities relative to its parent. There is no "grant more than I have" operation.
This is what makes spawn safe.

P4 — Dual-read / single-write schema versioning. When a strict schema must change, freeze the old (/1), introduce /2, make readers read both, make
production writers write only /2. Never mutate /1 in place. New readers read old data; old validators do not accept new data.

P5 — Proof-honest reproducibility. Separate capability (can I in principle reconstruct?) from verification (did I actually execute a receipt proving it?).
WAL presence proves capability, not verification. Pins prove pinning, not semantic replay. A verified value requires an immutable run-bound receipt.

P6 — Falsification over happy-path testing. Every module ships a named falsifier (RF-XX) that actively tries to break the invariant. A green falsifier
means the attack failed. A weakening falsifier is itself a finding.

───

Part 1 — M-4: Evidence Runtime + Scientific Contracts

Goal: One useful, durable real-model coding run, with complete causal capture so every later milestone is measurable.

Exit gate: RF-95 accepted + independent review receipt.

1.1 Exact model I/O capture (C-01)

The single seam is runtime/session.py::_LayeredOperator.propose. Bind capture around the call, not inside the model adapter.

class _LayeredOperator:
      def propose(self, final_bundle: ContextBundle) -> ModelOutput:
          # 1. Capture input AFTER final assembly, BEFORE invocation (C-01)
          input_digest = sha256(JCS.canonicalize(final_bundle))
          input_ref = self.evidence.capture(
              role="prompt",
              bytes=final_bundle.serialize(),
              digest=input_digest,
              required=True,          # prompt is always required evidence
          )

          # 2. The real provider call — nothing evidence-related above this line
          raw = self.model.invoke(final_bundle)

          # 3. Capture raw structured output BEFORE downstream interpretation (C-01)
          output_digest = sha256(JCS.canonicalize(raw))
          output_ref = self.evidence.capture(
              role="model_output",
              bytes=raw.serialize(),
              digest=output_digest,
              required=True,
          )

          # 4. Emit a small causal fact pointing at the artifacts by digest
          self.ledger.append(ModelInvoked(
              input_digest=input_digest,
              output_digest=output_digest,
              input_ref=input_ref,
              output_ref=output_ref,
          ))
          return raw

Key: the evidence sink is injected as a protocol (P2), so the operator never imports a concrete store.

1.2 Fail-vs-degrade evidence semantics (C-02)

The core of the scientific contract. Evidence failure is fatal; optional artifact failure degrades but is durably recorded.

class EvidenceSink:
      def append_required(self, fact: EvidenceFact) -> None:
          try:
              self.ledger.append(fact)
          except LedgerError:
              # Fatal: propagate, terminate the evidentiary run (C-02)
              raise EvidenceCaptureRequiredError(fact) from None

      def capture(self, *, role, bytes, digest, required: bool) -> ArtifactRef:
          try:
              return self.blob_store.put(bytes, digest=digest)
          except BlobError:
              if required:
                  raise EvidenceCaptureRequiredError(role) from None
              # Degrade: durably record incompleteness FIRST (C-02)
              self.ledger.append(CaptureIncomplete(
                  role=role, digest=digest, reason="blob_store_failure",
              ))
              return DegradedArtifactRef(digest=digest, incomplete=True)

A degraded run is non_evidentiary and can never satisfy RF-95 or promotion evidence. The capture_incomplete fact must be appended before the degraded
outcome is returned, or the run is fatal.

1.3 Execution profile /2 + trajectory /2 (C-03)

# Dual-read
  class ProfileReader:
      def read(self, raw: dict) -> ExecutionProfile:
          v = raw.get("schema")
          if v == "mhf.execution-profile/1": return self._read_v1(raw)
          if v == "mhf.execution-profile/2": return self._read_v2(raw)
          raise UnknownSchemaError(v)

  # Single-write
  class ProfileWriter:
      def write(self, profile: ExecutionProfile) -> dict:
          return self._write_v2(profile)   # never emits /1

/2 adds: retention vocabulary (digests_only|standard|full), capture_required flag, content-capture/privacy policy identity, and identity/preimage behavior.
  Historical /1 identities are never rewritten.

1.4 RF-100 proof-honest reproducibility (C-04)

@dataclass(frozen=True)
  class Reconstruction:
      capability: Literal["none", "from_checkpoint", "full_cold"]
      verification: Literal["unverified", "verified"]

  def assess_reconstruction(run: RunEvidence) -> Reconstruction:
      cap = _derive_capability(run)          # from WAL, checkpoint, pins
      ver = "verified" if _has_executed_receipt(run) else "unverified"
      return Reconstruction(capability=cap, verification=ver)

  def _has_executed_receipt(run) -> bool:
      # immutable receipt bound to: run id, reducer/schema pins,
      # input-history/checkpoint digest, reconstructed output/state digest
      return run.receipt is not None and run.receipt.is_bound_to(run)

1.5 Falsifiers (what proves it)

- RF-95 — the live run itself (see §1.6). One real-model run, exactly one candidate, terminal trajectory /2, verifier receipt, workspace diff, WAL,
fresh-process reconstruction receipt.
- RF-100 — golden vectors where a "capability-only" state must render unverified.
- C-02 test — inject a blob-store failure and assert EvidenceCaptureRequiredError when required=True, and assert CaptureIncomplete precedes a
non-evidentiary outcome when required=False.
- Dual-read test — a /1 fixture reads correctly; a /2 writer never emits /1.

1.6 RF-95 execution (the operational close)

This is not code — it's the evidence assembly:

1. Preregister the exact live-provider candidate (task, model, profile /2, retention=standard, capture.required=true).
2. Run it once through Runtime.run_composed. Do not repair the trajectory on failure.
3. Produce the evidence bundle: model I/O digests, context/compaction/cache provenance, verifier receipt, workspace diff, WAL, fresh-process reconstruction
  receipt, reproducibility vector.
4. Independent review receipt (human).

───

Part 2 — M-5a: Event-Derived Agent

Goal: The agent becomes a projection. Semantic state reconstructible purely from events.

Exit gate: RF-96/97/99/100 green → immutable M-5A-BASE-v2 tag.

2.1 Event envelope /2 (C-03/C-05/C-06/C-07)

The envelope carries: event id, lineage, causation, ordering, writer authority fields. Semantic payload kinds (GoalDeclared, PlanCreated/Revised, Observed,
  Proposed, EffectSettled, ProgressAssessed, StrategyChanged, ContextCompacted, Evaluated, Concluded) are governed by ADR-0098.

# Additive budget dimensions are exactly these four (C-05)
  BUDGET_DIMS = ("usd_micros", "millis", "tokens", "bytes")
  STRUCTURAL_DIMS = ("depth", "turns")   # ceilings, not additive

  def reserve(parent: Budget, amount: Budget) -> Budget:
      for d in BUDGET_DIMS:
          assert parent[d] >= amount[d], f"budget breach: {d}"
          parent[d] -= amount[d]
      return amount

Goal event carries goalDigest + optional goalArtifact ref — never raw goal text (C-06).

2.2 AgentView — deterministic projection (P1/P2)

The reducer is a pure function. This is the heart of M-5a.

class AgentView:
      goal: GoalDigest
      plan: PlanState
      attempts: list[Attempt]
      settled_effects: list[EffectRef]
      budget: Budget
      strategy: Strategy
      terminal: TerminalStatus

      @staticmethod
      def fold(events: Iterable[Event], rv: str) -> "AgentView":
          state = AgentView.empty()
          for e in events:
              state = REDUCERS[rv][e.kind](state, e)   # pure, total, deterministic
          return state

AgentView is a projection, not a second source of truth. The canonical ledger reducer stays single; domains hold their own projections over it.

2.3 Checkpointed reconstruction

class CheckpointManager:
      def checkpoint(self, view: AgentView, offset: int) -> str:
          blob = JCS.canonicalize(view)
          digest = sha256(blob)
          self.blob_store.put(blob, digest=digest)
          self.ledger.append(CheckpointCreated(
              offset=offset, digest=digest,
              reducer_pin=self.reducer_version,
              schema_pin=self.schema_version,
          ))
          return digest

      def restore(self, digest: str) -> AgentView:
          blob = self.blob_store.get(digest)
          assert sha256(blob) == digest          # verify content (fail-closed)
          view = self._parse(blob, self.schema_version)   # verify version
          return view

      def cold_fold(self, digest: str) -> AgentView:
          # if a checkpoint pin mismatches current reducer, do NOT serve it
          # under new rules (RF-96: fail-to-cold-fold behavior)
          cp = self.ledger.lookup_checkpoint(digest)
          if cp.reducer_pin != self.reducer_version:
              return self._fold_from_scratch(self.ledger.all())
          return self.restore(digest)

2.4 RF-97 — automatic transitive TCB closure (C-08)

The TCB is not the kernel/ directory. It's the transitive executable import closure.

def compute_tcb(entry_modules: list[str]) -> frozenset[str]:
      visited: set[str] = set()
      queue = deque(entry_modules)
      while queue:
          mod = queue.popleft()
          if mod in visited: continue
          visited.add(mod)
          for dep in parse_imports(mod):
              if is_in_repo(dep):              # skip stdlib/3rd-party
                  queue.append(dep)
      return frozenset(visited)

  def measure(closure) -> int:
      return sum(loc(m) for m in closure)

Current known domain modules are regression assertions, not the discovery mechanism. The closure must be computed, not hard-coded, so unexpected
trust-surface growth fails the gate.

2.5 Falsifiers

- RF-96 — fresh-process reconstruction: a second process opens the ledger and rebuilds the same AgentView without any in-memory object.
- RF-97 — transitive closure + synthetic indirect-import test (a module imports B which imports C; C must be in the closure even though the entry only
names A).
- RF-99 — authority provenance/role consistency for event /2 (writer, reducer, schema all correct).
- RF-100 current — does not overclaim; budget contract rejects charged_millis and structural dims inside additive costs.

───

Part 3 — M-5b: Generality Falsifier (SAT/CNF)

Goal: Run a materially non-coding domain through the unchanged substrate and get a deterministic, independently checkable witness. Try to break the
abstraction.

Exit gate: full formal run + deterministic witness + RF-52/53 + RF-86 zero-semantic-diff + RF-98 neutrality.

3.1 The exterior oracle (no search, no self-grading)

The generator proposes a candidate assignment; only the exterior evaluator checks it. Oracle, formula, and witness vectors are digest-pinned.

class SatEvaluator:
      def evaluate(self, dimacs_digest: str, witness_bytes: bytes) -> Verdict:
          clauses = self._parse_dimacs(self._load_pinned(dimacs_digest))  # NO search
          assignment = self._parse_witness(witness_bytes)
          for i, clause in enumerate(clauses):
              if not clause.satisfied_by(assignment):
                  return self._sign(Verdict(fail=True, clause_index=i))
          return self._sign(Verdict(pass=True))

Two axes stay separate (per the ratified M-5b decision): the evaluator owns the evaluation axis; RunTermination owns the run axis. A witness that verifies
says nothing about whether the run finished. Evidence is promotable only when both are clean and the pass carries the daemon's Ed25519 signature. An
unsigned pass is just an assertion.

3.2 The pack frame

# packs/formal-sat/
  #   domain prompts/policies
  #   solver toolkit (as ordinary tools, not substrate logic)
  #   domain context/projections (domain-specific, allowed)
  #   fixed task set (digest-pinned DIMACS + witness vectors)

The pack runs through Runtime.execute_harness — the same composition, kernel dispatch, operator approval, and trajectory path the coding pack uses.

3.3 RF-86 zero-semantic-diff

# ci/rf86_gate.sh
  # diff domain, kernel, ports, runtime, agency/episode against M-5A-BASE-v2
  # fails closed when the tag does not resolve

Two binding rules (from the ratified decision):

1. M-5A-BASE-v2 must be created only after the substrate change lands. Creating it early makes the gate fire on the authorized change itself.
2. RF-86 must never be weakened — not by narrowing frozen paths, not by allowlisting a file, not by downgrading to a warning. A substrate change with no
ADR is the finding, not the tag.

3.4 Falsifiers

- RF-52/53 — the deterministic witness is independently checkable.
- RF-86 — zero semantic diff vs M-5A-BASE-v2.
- RF-98 — neutrality report (the SAT run adds no substrate semantics).
- Negative vector — the same pipeline signs fail for an unsatisfiable assignment.

A failed generality hypothesis is a valid scientific result; it must not be hidden by patching the substrate.

───

Part 4 — M-6: Recursive Delegation

Goal: agent.spawn becomes an ordinary capability-mediated effect creating nested execution lineages. The kernel stays verb-blind.

Exit gate: RF-55…RF-59 + nested-lineage demonstration bundle.

4.1 SpawnAdapter (capability attenuation + budget reservation)

class SpawnAdapter:
      def spawn(self, parent_scope, *, goal_digest, budget, capabilities, depth) -> LineageRef:
          # 1. Attenuate — child can only LOSE capabilities (P3, monotonic)
          child_caps = attenuate(parent_scope.capabilities, capabilities)

          # 2. Reserve budget across the four additive dims (C-05)
          child_budget = parent_scope.budget.reserve(budget)

          # 3. Enforce structural ceilings
          assert parent_scope.depth + 1 <= parent_scope.max_depth
          assert parent_scope.turns + 1 <= parent_scope.max_turns

          # 4. Emit spawn fact, return a lineage ref — do NOT instantiate an agent
          self.ledger.append(ChildSpawned(
              parent=parent_scope.lineage_id,
              child=child_id,
              goal_digest=goal_digest,
              budget=child_budget,
              capabilities=child_caps,
              depth=parent_scope.depth + 1,
          ))
          return LineageRef(child_id)

The critical discipline: spawn goes through generic S0–S12 dispatch. The kernel must not branch on the spawn verb and must not know child topology.

4.2 Budget conservation (four-dim additive)

def reserve(self, amount: Budget) -> Budget:
      # reservation is atomic across all four dims
      new = {d: self[d] for d in BUDGET_DIMS}
      for d in BUDGET_DIMS:
          if new[d] < amount[d]:
              raise BudgetBreachError(d, new[d], amount[d])
          new[d] -= amount[d]
      self.update(**new)
      return amount

  def release(self, amount: Budget) -> None:
      # release on child completion/abort (no leak)
      for d in BUDGET_DIMS:
          self[d] += amount[d]

depth and turns are structural, enforced independently, never folded into additive cost.

4.3 Kill-tree + cold recovery

def classify_lineage(ledger, lineage_id) -> LineageState:
      events = ledger.range(lineage_id)
      if _has_terminal(events): return COMPLETE
      if _has_interrupt(events): return INTERRUPTED
      if _has_waiting(events):   return WAITING
      return EXECUTABLE

The kill-tree drill: SIGKILL the parent mid-child, reopen the ledger, and assert the cold path returns UNDETERMINABLE — never a silent retry. Neither
parent nor child needs to survive as a process (P1/P2).

4.4 Falsifiers

- RF-55…RF-59 (conjunctive) — the authoritative allocation is in the ADR register, using four additive budget dims from C-05.
- Nested-lineage demonstration bundle — cold-reconstructible child tree.
- Idempotent subtree settlement — replaying settlement is exactly-once per command identity.

───

Part 5 — M-6.5: Adaptive Strategy / Meta-Control

Goal: Higher-order control as ordinary policy/reducer/plugin. Measure whether it actually helps.

◼ Connection dropped mid-response. Retrying (1/3); any partial reply above is incomplete.

✻ Thought for 17 seconds [ctrl+o to expand]

⠶ I'll lay out a complete, build-order development plan for the backend, grounded in the architecture and the correction set (C-01…C-12) I've already read.
This is the full HOW — pseudocode per module, invariants, falsifiers, and merge order. No docs, no git.

0. Governing architecture (recap)

domain ← ports ← kernel ← agency ← runtime → adapters
                          (apps/ is a client slot of runtime)

Frozen rules that every module below must obey:

- Events = durable causal facts (small, append-only, single-writer). Artifacts = content-addressed blobs (large). Projections = derived state, never second
  truth.
- Kernel is domain-blind, TCB <=1438 LOC, 13-stage S0–S12 dispatch. It must never learn "agent", "topology", "spawn", "metacognition".
- Additive resources exactly {usd_micros, millis, tokens, bytes}; depth/turns are structural ceilings.
- Schema versioning is strict: /1 frozen forever, new fields go to /2, readers dual-read, writers single-write /2.
- Evidence failure semantics: ledger append failure = fatal; required artifact failure = fatal; optional artifact failure = degrade but MUST durably record
  capture_incomplete (then the run is non-evidentiary).
- Two Seniors, one shared Contract Kit, merge at gates only.

───

1. Shared foundation (build first, before M-4)

1.1 Evidence failure contract (C-02)

This is a port-level error taxonomy, not runtime-only. Put it in ports/ so Agency can depend on it without importing Runtime.

# vanguard/packages/ports/evidence_errors.py
  class EvidenceCaptureError(Exception): ...
  class EvidenceCaptureRequiredError(EvidenceCaptureError):
      """Fatal. The evidentiary run must terminate; do not swallow."""
  class EvidenceCaptureDegraded(EvidenceCaptureError):
      """Optional capture failed but was durably recorded as incomplete."""

  # Protocol the runtime sink implements
  class EvidenceSink(Protocol):
      def append_event(self, event: Event) -> None: ...
      def put_artifact(self, role: str, payload: bytes, *,
                        required: bool) -> ArtifactRef:
          """required=True -> raise EvidenceCaptureRequiredError on failure.
              required=False -> raise EvidenceCaptureDegraded (caller records)."""

Rule for every sink implementation: append a capture_incomplete fact before returning the degraded outcome; if writing either the evidence fact or the
degradation fact fails, that is fatal. This single rule prevents "scientific evidence silently disappearing."

1.2 Artifact writer (C-01, C-06, C-12)

# vanguard/packages/runtime/artifacts.py
  class ArtifactWriter:
      def __init__(self, blob_store: BlobStorePort, policy: CapturePolicy): ...

      def write(self, role: ArtifactRole, payload: bytes, *,
                digest: bytes | None = None, required: bool = True) -> ArtifactRef:
          # 1. Resolve capture policy (retention != authorization, C-12)
          decision = self.policy.authorize(role, payload)  # capture|digest_only|deny
          if decision == "deny":
              if required:
                  raise EvidenceCaptureRequiredError(...)
              return self._digest_only(role, payload)      # SHA-256 identity only

          # 2. Redact secrets before persistence (C-12)
          clean = self.policy.redact(payload)

          # 3. Content-address; caller never supplies the authoritative digest (C-06)
          content_id = sha256(clean).digest()
          if digest is not None and digest != content_id:
              raise EvidenceCaptureRequiredError("digest mismatch")

          # 4. Blob-first, event-second durability
          self.blob_store.put(content_id, clean)
          return ArtifactRef(role=role, digest=content_id,
                              size=len(clean),
                              capture_policy=self.policy.identity())

Key invariants:

- No caller-supplied digest authority — the content hash is recomputed.
- No large content inline in events — events carry only ArtifactRef.
- Goal content is goalDigest + optional goalArtifact (C-06), never raw text in the ledger.

1.3 Provider-call capture seam (C-01)

The exact seam is runtime/session.py::_LayeredOperator.propose. Capture happens around it, not somewhere upstream where the bundle isn't final.

class _LayeredOperator:
      def propose(self, model: ModelPort, bundle: FinalBundle, ...):
          # BEFORE: bundle is final
          input_ref = self.sink.put_artifact("prompt", bundle.serialize(),
                                              required=True)
          started = monotonic_ns()
          raw = model.invoke(bundle)          # the real call
          # AFTER: raw structured output, before interpretation
          output_ref = self.sink.put_artifact("model_output", raw.serialize(),
                                              required=True)
          latency_ms = (monotonic_ns() - started) // 1_000_000
          self.sink.append_event(ModelInvoked(input_ref=input_ref,
                                              output_ref=output_ref,
                                              latency_ms=latency_ms))
          return self._interpret(raw)

Why here and not Agency: Agency owns generic context-provenance protocols only. The model/provider I/O fact is a Runtime concern. No Agency→Runtime import
may ever exist.

───

2. M-4 — Product proof + scientific trajectory capture

Exit: one useful real-model coding run (RF-95) with complete, proof-honest capture.

2.1 B-M4 — Scientific contracts & verification (Dev B)

2.1.1 mhf.execution-profile/2 (C-03, C-07)

Freeze /1. Add /2 with corrected semantics:

{
    "retention": { "enum": ["digests_only", "standard", "full"] },
    "capture": {
      "required": { "type": "boolean" },
      "policy_identity": { "type": "string" }
    },
    "identity": { "type": "string" }
  }

Reader: ExecutionProfileReader.read(raw) → try /2, fall back to /1 (never rewrite /1). Writer: single-write /2.

2.1.2 mhf.trajectory/2 (C-03, C-01)

Carry the new sections: artifact_index, provenance, reproducibility. Freeze /1. Reader dual-reads, writer single-writes /2.

2.1.3 RF-100 — proof-honest reproducibility (C-04)

@dataclass(frozen=True)
  class ReproducibilityVector:
      state_reconstruction_capability: Literal["none","from_checkpoint","full_cold"]
      state_reconstruction_verification: Literal["unverified","verified"]
      semantic_replay_capability: Literal["unpinned","pinned"]
      semantic_replay_verification: Literal["unverified","verified"]
      # other ratified dimensions

  def assess(run: Run) -> ReproducibilityVector:
      v = ReproducibilityVector(...)
      # "verified" is only set when a run-bound receipt exists:
      v.state_reconstruction_verification = (
          "verified" if run.reconstruction_receipt else "unverified")
      v.semantic_replay_verification = (
          "verified" if run.replay_receipt else "unverified")
      return v

WAL presence → full_cold capability but unverified. Pins → pinned but unverified. Only executed receipts flip to verified. This is the single most
important honesty gate: prerequisites ≠ proof.

2.1.4 Benchmark baseline

Freeze append/fold micro-benchmark (benchmarks/baseline_m4.json) — required input to M-5a's TCB/budget re-freeze.

2.2 A-M4 — Evidence runtime & causal capture (Dev A)

Implements §1.2/1.3 on the production path, plus:

- Context/compaction provenance — record compactor_id, source_range, input_digest, output_digest whenever context is compacted (VISION Cap. 17).
- Cache provenance — record cache_id, key, source_artifact, validation_result on hits; emit no claim on live no-cache runs.
- Wire all of it through the existing ledger_emitter.py and evaluator_gateway.py.

2.3 RF-95 gate (G-M4)

The single run. All preconditions: CV-003 receipt, A-M4 + B-M4 merged B→A, combined CI green, frozen live task + verifier, profile /2, retention=standard,
capture.required=true.

Evidence bundle: live-provider run, exactly one candidate, terminal trajectory/2, artifact index, model I/O capture, context/compaction/cache provenance,
verifier receipt, workspace diff, WAL, fresh-process reconstruction receipt, proof-honest reproducibility vector, independent review.

Failure = preserve evidence, no manual repair, no retry. Success → M-4 CLOSED.

───

3. M-5a — Event-derived agent (single substrate change window)

Exit: AgentView reconstruction from events; immutable M-5A-BASE-v2; RF-96/97/99/100.

3.1 A-M5A — Event substrate migration (Dev A)

- mhf.event/2 wire types; dual-read/single-write; emitter cutover; vocabulary generated from schema (A-4, I-8).
- Deprecated kinds: reject on write, still readable historically.
- Remove _V4_ONLY_KINDS. Old ledgers never rewritten. Mixed-version chains readable.

# migration invariant, enforced in emitter
  class EventWriter:
      def write(self, event: Event) -> None:
          assert event.schema_version == "/2"     # single-write /2
          if event.kind in DEPRECATED_KINDS:
              raise DeprecatedKindWrite(...)       # reject, never silent
          self.store.append(event)

3.2 B-M5A — Projection, checkpoints, falsifiers (Dev B)

3.2.1 Execution contracts (C-05)

@dataclass(frozen=True)
  class ExecutionScope:
      usd_micros: int; millis: int; tokens: int; bytes_: int  # additive
      depth: int; turns: int                                    # structural

  class BudgetLedger:
      def reserve(self, amt: ResourceDelta) -> None:
          # additive conservation across 4 dims; depth/turns enforced separately
          # reject charged_millis (C-05: removed from contract)

3.2.2 AgentView (C-06)

Deterministic fold over the ledger. Goal as goalDigest, plan, attempts, settled effects, budget, strategy, terminal status. Projection, not truth — the
single ledger reducer stays canonical.

def fold_agent_view(events: Iterable[Event]) -> AgentView:
      view = AgentView.empty()
      for e in events:
          view = REDUCERS[e.kind](view, e)   # pure, deterministic
      return view

3.2.3 Checkpoints (C-04, RF-96)

class CheckpointManager:
      def restore(self, checkpoint: Checkpoint) -> Projection:
          if not verify_digest(checkpoint): raise CorruptCheckpoint(...)
          if not verify_pins(checkpoint):    raise PinMismatch(...)  # cold-fold
          return fold_from(checkpoint.base, checkpoint.remaining)
      def cold_fold(self) -> Projection:
          return fold_from(LEDGER_START)     # fail-to-cold-fold path

RF-96: fresh-process reconstruction proves no process-local object is required (run the fold in a fresh interpreter/process, compare digest).

3.2.4 RF-97 — real TCB closure (C-08)

def transitive_trust_closure(roots: list[Module]) -> set[Path]:
      seen = set()
      queue = deque(roots)
      while queue:
          m = queue.popleft()
          seen.add(m.path)
          for dep in parse_imports(m):       # AST, in-repo executable deps only
              if dep not in seen:
                  queue.append(dep)
      return seen

  def measure_tcb() -> TcbMetrics:
      closure = transitive_trust_closure(PRODUCTION_KERNEL_MODULES)
      return TcbMetrics(loc=sum(count_lines(p) for p in closure),
                        closure=closure)

RF-97 fails on unexpected trust-surface growth, not just over-budget. The known domain modules are regression assertions, not a hard-coded allowlist.

3.2.5 RF-99

Verify authority provenance + role consistency for event/2 (writer-role matrix enforced).

3.3 G-M5A

Merge A→B, run full suite + migration + mixed replay + benchmark regression + Kernel semantic diff (must be zero) + schema/codegen + falsifiers. Then tag
exactly once: M-5A-BASE-v2 (never move M-5-BASE). This is the experimental control for M-5b/M-6.

───

4. M-5b — Formal generality falsifier (Dev B, parallel with M-6)

Exit: RF-86 zero-semantic-diff; deterministic SAT witness; RF-52/53; RF-98 neutrality.

OD-3 = SAT/CNF with complete-assignment witnesses. Exterior oracle checks every clause from pinned DIMACS + witness bytes; no search, generator cannot
self-grade.

# packs/formal-sat/
  class SatGenerator:
      def propose(self, formula: CnfFormula) -> Assignment: ...  # candidate only

  # exterior evaluator daemon (own Ed25519 key)
  class SatEvaluatorDaemon:
      def grade(self, formula_digest, witness_digest) -> SignedVerdict:
          f = load_dimacs(formula_digest)   # pinned
          w = load_witness(witness_digest)
          ok = all(clause_satisfied(c, w) for c in f.clauses)
          return sign(Verdict(pass=ok))     # deterministic, no self-grade

Run through Runtime.execute_harness (same composition/kernel/operator/ledger path as coding). Two axes stay separate: evaluator owns pass/fail,
RunTermination owns "did the run finish". A passing witness over an abandoned run is not promotable — evidence promotable only when both clean and signed.

RF-86 = diff domain,kernel,ports,runtime,agency/episode vs M-5A-BASE-v2. Fails closed if the tag doesn't resolve; never weakened.

If the formal domain requires a substrate change → raise counter-evidence, don't silently patch. A failed generality hypothesis is a valid result.

───

5. M-6 — Recursive delegation as nested lineages (Dev A, parallel with M-5b)

Exit: RF-55…RF-59; four-dim conservation; depth/turn limits; join/cancel/kill-tree recovery.

agent.spawn is an ordinary S0–S12 effect, not a Kernel verb. Kernel never branches on the verb or knows child topology.

# SpawnAdapter (runtime adapter, post-intent child creation)
  class SpawnAdapter:
      def on_spawn_intent(self, intent: SpawnIntent, parent: Lineage) -> ChildLineage:
          child_scope = attenuate(parent.scope, intent.budget,
                                  depth=parent.depth + 1)   # monotonic attenuation
          return ChildLineage(identity=new_id(), parent=parent.id,
                              goal=intent.goal_digest, scope=child_scope)

  # events
  ChildSpawned(lineage_id, parent_id, scope, budget_reservation)
  ChildReturned(lineage_id, result_ref, terminal_status)

Key mechanisms:

def reserve_budget(parent, child_scope) -> None:
      # reserve exactly the child's 4-dim budget from parent; release on return
      parent.budget -= child_scope.additive
      # depth/turns structural: parent.depth+1 <= parent.max_depth else reject

  def join(parent, child_id) -> DelegationResult:
      # idempotent subtree settlement: replay child lineage, fold terminal status
      # never return a raw conversation dump (only the result_ref + status)

  def recover_after_kill_tree(ledger) -> list[LineageStatus]:
      # SIGKILL parent mid-child -> cold path returns UNDETERMINABLE, never silent retry
      # classify each lineage: complete | interrupted | waiting | executable

Recovery is reclassification, not object resurrection (VISION Cap. 12).

Acceptance: 28 falsifiers (RF-55…59) + nested-lineage demo bundle with cold-reconstructible child tree.

───

6. M-6.5 — Adaptive strategy / meta-control

Exit: controller acts only through normal authority; measured improvement via paired runs.

OD-4 = confidence/calibration protocol. Metacognition is policy/reducer/plugin, never kernel primitive; passes S0–S12 like any proposer.

6.1 A-M65 — Meta-Control runtime (Dev A)

class MetaControllerSPI(Protocol):
      def consult(self, view: AgentView) -> list[StrategyDirective]: ...

  class GuardedConsult:
      def consult(self, controller, view) -> StrategyDirective | None:
          # guard: confidence record MUST declare contextEpoch and name a subject
          if not controller.ready(view.context_epoch):
              return None                          # stale -> no directive
          directive = controller.consult(view)
          # lower to normal proposal path (never direct store/model/kernel bypass)
          return self.lower(directive)

  # directive family: revise_plan | request_context | change_verification |
  #                   abandon_hypothesis | delegate | conclude

Every falsifier fails closed by raising, never degrading to an unattributable proposal. StrategyChanged records attribution; PlanRevised supersedes but
never deletes the prior plan (I preserves history).

Controller-off path must be bit-identical to baseline.

6.2 B-M65 — Confidence, progress & paired evaluation (Dev B)

@dataclass(frozen=True)
  class ConfidenceRecord:
      value: float
      context_epoch: int        # REQUIRED: the epoch it was computed at
      subject: str              # REQUIRED: names a view reference (e.g. "goal")

  def paired_study(tasks, provider) -> StudyVerdict:
      # McNemar exact + Holm correction + A/A floor check (M-18 comparability)
      if a_a_floor_is_degenerate(provider):   # deterministic provider -> floor 100%
          raise MeasurementRefused("M-07: degenerate A/A floor")
      ...

The blocker is the instrument, not the controller: a fully deterministic offline provider makes the A/A noise floor degenerate (100%), so M-07 refuses to
conclude. You need a stochastic attributable provider + deliberately-blocked tasks before a non-degenerate A/A floor exists. Negative result → controller
stays disabled-by-default and the milestone is scientifically successful if the hypothesis was honestly tested.

───

7. Delivery phasing & merge order

┌────────────┬──────────────────────────────────────────────────────┬────────────────────┬──────────────────────┐
│ Phase      │ Build (parallel)                                     │ Merge order        │ Gate                 │
├────────────┼──────────────────────────────────────────────────────┼────────────────────┼──────────────────────┤
│ Foundation │ evidence errors + ArtifactWriter + capture seam (§1) │ —                  │ unit tests           │
├────────────┼──────────────────────────────────────────────────────┼────────────────────┼──────────────────────┤
│ M-4        │ A-M4 ∥ B-M4                                          │ B → A → integrated │ RF-95                │
├────────────┼──────────────────────────────────────────────────────┼────────────────────┼──────────────────────┤
│ M-5a       │ A-M5A ∥ B-M5A                                        │ A → B → integrated │ M-5A-BASE-v2         │
├────────────┼──────────────────────────────────────────────────────┼────────────────────┼──────────────────────┤
│ M-5b ∥ M-6 │ B-M5B ∥ A-M6                                         │ either (disjoint)  │ RF-86 + RF-55…59     │
├────────────┼──────────────────────────────────────────────────────┼────────────────────┼──────────────────────┤
│ M-6.5      │ A-M65 ∥ B-M65                                        │ A → B study → gate │ paired-study verdict │
└────────────┴──────────────────────────────────────────────────────┴────────────────────┴──────────────────────┘

Sequencing rule: M-5a before M-5b's baseline (can't prove "zero semantic diff" while changing agent semantics). M-5b and M-6 diverge from M-5A-BASE-v2 and
never block each other.

───

8. Cross-cutting "SOTA" disciplines to bake in everywhere

1. Proof-honesty over ambition — every "verified" claim requires an executed, immutable, run-bound receipt (C-04). This is the north star.
2. Fail-closed at every boundary — evidence, capture authorization, schema, TCB, M-6.5 consultation. Never degrade silently.
3. Single-writer, single-reducer, single-source — one schema (A-4/I-8), one ledger reducer, projection is derived.
4. Determinism by construction — pure reducers, digest-pinned fixtures, golden vectors, fresh-process replay as the only replay proof (A-3, I-4).
5. Kernel = smallest possible — every feature lands outside it (packs/adapters/policies/plugins). If it can't, that's an architectural finding to escalate,
  not a hack.
6. Capability attenuation is monotonic — child scope ⊆ parent, budget reserved not duplicated, depth/turns structural.

───

The concrete next coding step on the critical path is §6.2's stochastic attributable provider + deliberately-blocked task set (unblocks M-6.5) and the M-7
effect-capture selector/timing fields (unblocks M-7) — but those are M-7 scope. Within M-4…M-6.5, the first line of code to write is the §1.1 evidence
failure contract + §1.2 ArtifactWriter, since everything downstream depends on correct capture.required/capture_incomplete semantics


# PROTOTYPE

M-4, M-5a, M-5b, M-6, M-6.5 from current state to 100/100, based on my audit of the actual code (kernel/dispatch.py, lab/m701_independence.py, lab/m65_study.py, runtime/paired_evaluation.py, runtime/meta_controller.py, tools/runners/run_rf95_product_proof.py) and the falsifiers.
Delivery Plan: M-4 → M-6.5 Closure
Guiding invariants (apply to every phase)
No kernel semantic changes. All work lives in runtime/, adapters/models/, lab/, packs/, test/.
Fail-closed evidence. A missing field is unknown, never a measurement (M-07 discipline). A degraded capture is non-evidentiary (C-02).
Hermetic CI always green; live paths are explicitly selected (OPENROUTER_API_KEY unset in test env — your shell currently exports it; unset before running suites).
Every claim ≤ its executed proof. Digest-pin everything; JCS canonicalization before hashing.
Escalation triggers (masterplan §6.3) apply: new event kind, schema mutation, kernel change → stop, escalate.
PHASE 1 — M-4 closure (~10% remaining)
Gap
RF-95 attempt 3 was authorized but requires new preregistration; the live run + independent review receipt are the only missing items. Code is green.
Step 1.1 — Fresh preregistration artifact
The preregistration schema exists (schemas/mhf/preregistration.schema.json). The runner (tools/runners/run_rf95_product_proof.py) already supports --dry-run qualification.
## Preregistration is a digest-pinned intent record created BEFORE the run.
@dataclass(frozen=True)
class Preregistration:
    manifest_digest: str        # sha256 of code-default manifest (JCS)
    profile_digest: str         # execution-profile /2 dict, JCS-pinned
    task_digest: str            # TaskContext brief + repo seed, pinned
    model_id: str               # e.g. "deepseek/deepseek-chat" — fixed, no fallback
    max_turns: int              # fixed, e.g. 20
    success_oracle: str         # exterior evaluator protocol name
    created_at: str             # ISO-8601
    def digest(self) -> str: return digest_of(jcs(self.to_dict()))
Rule: one candidate, one attempt. If the run fails, the bundle is preserved unrepaired; a retry requires a new preregistration digest (this is what "attempt 3, new preregistration required after D7" means mechanically).
Step 1.2 — Live execution with C-02 capture semantics
def execute_preregistered_run(prereg: Preregistration) -> EvidenceBundle:
    verify_dry_run_qualified(prereg)                  # hermetic gate first, always
    result = Runtime.execute_harness(
        manifest_path=CODE_DEFAULT,
        task_context=pinned_task(prereg),
        model=OpenRouterModel(model=prereg.model_id, stream=False),
        approver=sign_challenge,                      # human-in-loop approvals
        approval_key=OPERATOR_KEY,
    )
    bundle = EvidenceBundle.from_result(result)
    # C-02 triage — this ordering is mandatory:
    #   ledger append failure            -> fatal, no bundle
    #   artifact failure, required=true  -> fatal, no bundle
    #   artifact failure, required=false -> append capture_incomplete fact,
    #                                       mark run NON-EVIDENTIARY, keep bundle
    if bundle.has_capture_incomplete():
        bundle.evidentiary = False
    bundle.preregistration_digest = prereg.digest()   # binds run to intent
    bundle.seal()                                     # content-address, fsync
    return bundle
Step 1.3 — Acceptance checklist (DoD)
Dry-run qualified → live run executed exactly once against the pinned candidate.
Trajectory /2 embeds: ≥3 artifacts (prompt, model_output, context_bundle), context-selection + compaction provenance claims, cache-interaction claims, reproducibility_at_run_close vector.
Terminal outcome graded only by the exterior evaluator verdict (outcome=="claims" ∧ all claims hold) — never by an in-process suite run (the .passed bug class I fixed today).
Independent human review signs G-M4-05 → M-4 flips COMPLETE.
PHASE 2 — M-5a closure (~5%)
Gap
Only the immutable baseline tag. Implementation, ADR-0098, benchmark re-freeze are DONE.
Step 2.1 — Tag ceremony (procedural, not engineering)
preconditions (all must be true simultaneously):
  - full suite green hermetically      (currently 1,786 tests; 3 reds were env/Verdict-drift, now resolved)
  - static gates green                 (TCB ≤1438, boundaries, secrets, duplication, links)
  - RF-96 (cold reconstruction) green
  - RF-97 (transitive TCB closure) green
  - RF-99 (authority provenance) green
  - benchmarks/baseline_m4.json digest matches re-frozen values
then:
  - create annotated tag M-5A-BASE-v2 on the reviewed commit — exactly once, never moved
  - push; record tag digest in sprint board
Step 2.2 — Guard against drift after the freeze
## Add to CI (tooling lane, not kernel):
def test_substrate_frozen_at(tag):
    for pkg in ("domain", "kernel", "ports"):
        assert diff_tree(tag, f"vanguard/packages/{pkg}") == set(), \
            "substrate changed after M-5A-BASE-v2; successor ADR required"
DoD: tag resolves remotely; RF-98 historical comparison can locate its baseline.
PHASE 3 — M-5b closure (~15%)
Gap
SAT material run + daemon-signed pass/fail verdicts exist. RF-86 (zero-semantic-diff) and the RF-98 historical half are red-by-design until Phase 2's tag resolves.
Step 3.1 — RF-86 zero-semantic-diff job
RF86_SURFACES = ("domain", "kernel", "ports", "runtime", "agency/episode")

def rf86_zero_semantic_diff(base_tag: str = "M-5A-BASE-v2") -> Report:
    diffs = {}
    for surface in RF86_SURFACES:
        diffs[surface] = git_diff_stat(base_tag, f"vanguard/packages/{surface}")
        # Whitelist NOTHING. A docstring-only change is still a semantic-
        # surface diff under RF-86; keep the falsifier strict.
    semantic_diffs = {s: d for s, d in diffs.items() if d}
    return Report(passed=not semantic_diffs, detail=semantic_diffs)
    # If NOT passed: DO NOT patch. This is counter-evidence — the formal domain
    # exposed a substrate gap. Escalate under masterplan §15.2 falsification path.
Step 3.2 — RF-98 neutrality, historical half
tools/linters/check_kernel_neutrality.py already does the structural scan; add the historical comparator:
def rf98_historical(base_tag):
    base_report = neutralize_scan(at=base_tag)     # run scanner against tag worktree
    head_report = neutralize_scan(at="HEAD")
    # Kernel must be byte-identical in its verb-dispatch surface; agency/episode
    # must show no new domain tokens.
    assert base_report.kernel_dispatch_surface == head_report.kernel_dispatch_surface
    assert head_report.episode_domain_token_count == 0
Step 3.3 — Evidence binding (already built, verify it holds)
runtime/formal_evidence.py recomputes every pinned digest and folds the terminal axis from the ledger — meaning a passing witness over an abandoned run is rejected. Verify with an adversarial test:
def test_passing_witness_over_failed_run_is_not_promotable():
    bundle = fabricate_bundle(witness="sat", ledger_terminal="abandoned")
    assert formal_evidence.verify(bundle) == Result.fail("terminal-mismatch")
DoD: RF-86 green, RF-98 both halves green, SAT evidence bundle accepted → M-5b CLOSED. Generality is now supported empirically, not asserted.
PHASE 4 — M-6 closure (~10%, review/evidence only)
Implementation is complete (28 conjunctive falsifiers RF-55…59 green). What remains is assembling the acceptance package:
Step 4.1 — Demonstration bundle assembly
bundle/
├── lineage_demo/
│   ├── parent_trajectory.mhf.trajectory/2      # full parent episode
│   ├── child_tree.json                          # ChildSpawned/ChildReturned fold
│   ├── budget_conservation_proof.json           # Σ(child debits) == parent reservation
│   │                                            #   over usd_micros, millis, tokens, bytes
│   ├── kill_tree_recovery_transcript.json       # SIGKILL mid-subtree → fresh process
│   │                                            #   reconciles orphans via RecoveryScanner
│   └── depth_turn_enforcement.json              # structural ceilings violated → rejected
└── receipts/                                    # signed verdicts, digests
Step 4.2 — Conservation property (make it a checked invariant, not prose)
def rf57_four_dimensional_conservation(ledger):
    root_reserved  = sum_budgets(events("BudgetReserved", lineage=root))
    subtree_debits = sum_budgets(events(["BudgetCommitted", "BudgetReleased"]),
                                 lineage=all_descendants(root))
    for dim in ("usd_micros", "millis", "tokens", "bytes"):
        assert subtree_debits[dim] <= root_reserved[dim]          # additive, conserved
    # depth/turns are NOT additive — structural ceilings, independently enforced:
    assert max_depth(all_lineages) <= scope.depth_ceiling
    assert max_turns(any_episode)  <= scope.turn_ceiling
DoD: bundle + review checklist signed → M-6 CLOSED.
PHASE 5 — M-6.5 closure (~30% — the real engineering)
This is the only phase with substantial new backend code. The blocker is precise: the only fully-attributable offline provider is deterministic, so the A/A noise floor sits at 100% discordance-or-nothing and MEASUREMENT.md M-07 correctly refuses it (DegenerateFloorError); and on never-stalling tasks the controller emits no directive, making arms identical (ComparabilityError: declared axis unmoved).
You need two artifacts: (a) a stochastic-but-attributable provider, (b) a deliberately-blockable task set.
Step 5.1 — Stochastic Attributable Provider
Design principle: randomness must be reproducible per run (seed is recorded provenance) while producing genuine run-to-run variance (so paired arms differ).
class StochasticStallModel:
    """Wraps any ModelPort. Injects seeded, attributable stalls.

    Contract:
      - propose() output depends ONLY on (base_proposal, run_seed, turn_index)
      - the seed is written into invocation provenance -> attributable
      - stall behavior: with probability p_stall(turn), emit a regressive
        proposal (repeat previous action / wrong-direction patch) instead of
        the base proposal.
    """

    def __init__(self, base: ModelPort, run_seed: int, *,
                 p_stall: float = 0.35,
                 stall_decay: float = 0.9):        # stalls fade in later turns
        self._base, self._seed = base, run_seed
        self._p, self._decay = p_stall, stall_decay
        self.stalls: list[dict] = []               # telemetry, NOT ledger truth

    def propose(self, ctx: ProposalContext) -> Proposal:
        proposal = self._base.propose(ctx)
        rng = random.Random(f"{self._seed}:{ctx.turn_index}")   # derived stream
        p_t = self._p * (self._decay ** ctx.turn_index)
        if rng.random() < p_t:
            stalled = self._stall_variant(proposal, ctx, rng)
            self.stalls.append({"turn": ctx.turn_index,
                                "seed": self._seed,
                                "kind": stalled.stall_kind})
            return stalled                          # ordinary proposal; no new authority
        return proposal
Critical properties to unit-test:
Determinism under fixed seed: same (base, seed) → identical proposal sequence (hermetic, replayable).
Variance across seeds: distribution of outcomes over seeds ∈ [0, N) has 0 < discordance < 1.
Attributability: every deviation is recoverable from (seed, turn_index) — an auditor can explain why run k stalled.
No authority bypass: a stall variant is still parsed through the normal proposal path; kernel unchanged.
Step 5.2 — Deliberately-blocked task set
Tasks where the naive policy stalls deterministically-ish and the controller has a recoverable move. Three archetypes:
BLOCKED_TASKS = [
    # T1 "wrong-first-fix": the obvious patch fixes the symptom, breaks another
    #    suite. Recovery = directive 'revise_plan' → re-read failing output.
    BlockedTask(id="t1-wrong-first-fix",
                plant=PlantedBug(obvious_fix_breaks="test_downstream"),
                expected_directive_family={"revise_plan"}),
    # T2 "missing context": the bug cannot be located without reading a config
    #    file outside the initial context window.
    #    Recovery = directive 'request_context' → fetches the config.
    BlockedTask(id="t2-missing-context",
                plant=PlantedBug(hidden_dependency=".env.test"),
                expected_directive_family={"request_context"}),
    # T3 "flaky verification": first proc.exec fails nondeterministically;
    #    naive policy abandons; recovery = 'change_verification' → retry w/ isolate.
    BlockedTask(id="t3-flaky-verify",
                plant=FlakySuite(p_fail_first_attempt=0.5),
                expected_directive_family={"change_verification"}),
]
Generator must be fixed-seed and digest-pinned so both arms run byte-identical tasks (M-18 comparability):
def materialize_task_set(seed: int) -> TaskSetManifest:
    tasks = tuple(t.materialize(random.Random(f"{seed}:{t.id}")) for t in BLOCKED_TASKS)
    manifest = TaskSetManifest(tasks=tasks, seed=seed)
    manifest.digest = digest_of(jcs(manifest.to_dict()))
    return manifest
Step 5.3 — Paired study execution
Arms differ only in the declared treatment dimension controller_enabled:
def run_arm(manifest, *, controller_enabled: bool, seeds: range) -> list[RunMetrics]:
    runs = []
    for seed in seeds:
        model = StochasticStallModel(LamModelAdapter("lam/t0-vanguard-vertical"),
                                     run_seed=seed)
        controller = MetaController() if controller_enabled else None
        result = Runtime.execute_harness(
            MANIFEST_CODE_DEFAULT, materialize_task_set(seed).context,
            model=model, controller=controller,          # existing A-M65 hook
            verifier=_Verifier())
        runs.append(RunMetrics.from_ledger(result))       # reduced FROM LEDGER ONLY
    return runs
Metric reduction stays ledger-derived (already in runtime/paired_evaluation.py): success rate, wasted loops, repeated tool calls, cost (usd_micros), latency, signed-pass rate.
Step 5.4 — Statistics (already implemented; wire correctly)
report = run_study(
    baseline  = run_arm(manifest, controller_enabled=False, seeds=N_SEEDS),
    treatment = run_arm(manifest, controller_enabled=True,  seeds=N_SEEDS),
    declared_treatment_dimensions=["controller_enabled"],   # M-18 gate
    aa_floor_seeds=A_A_SEEDS,                               # both arms OFF
)
### Inside run_study (existing code):
###   1. assert_comparable()          -> raises ComparabilityError otherwise
###   2. aa_noise_floor(A, A)         -> raises DegenerateFloorError if 0% or 100%
###                                      With 5.1+5.2 the floor lands strictly inside (0,1)
###   3. mcnemar_exact(discordant)    -> exact p over discordant pairs only
###   4. holm_bonferroni(p-values)    -> family-wise correction across metrics
###   5. paired_bootstrap_ci(effect)  -> interval reported WITH p-value (M-04)
Step 5.5 — Falsifiers to add (hermetic)
Test
test_stall_provider_is_seed_reproducible
test_aa_floor_is_interior
test_blocked_task_elicits_directive
test_arms_comparable_except_declared_axis
test_no_kernel_diff_under_controller
test_confidence_records_are_epoch_bound
Step 5.6 — Decision semantics
Measured improvement (Holm-corrected significance + CI excluding null, no regression-budget breach) → report recommends enabling; default-enable remains a Leadership call.
No improvement → negative result recorded, controller stays disabled-by-default; milestone closes as scientifically successful (honest test of hypothesis).
DoD: non-degenerate A/A floor + paired verdict + signed report artifact → M-6.5 CLOSED either way.
Execution order & dependency graph
PHASE 1 (M-4 live RF-95)          ← needs API key + Director receipt (human gate)
   └─► PHASE 2 (tag M-5A-BASE-v2) ← one command once gates green
         ├─► PHASE 3 (RF-86/RF-98 → M-5b CLOSE)
         └─► PHASE 4 (M-6 evidence bundle → CLOSE)
PHASE 5 (M-6.5 instrument)        ← fully independent, start immediately, hermetic
Phases 3, 4, 5 can proceed in parallel once Phase 2 lands; Phase 5 needs nothing from anyone and is the largest pure-engineering block — that's where I'd start tomorrow.
One hygiene note: your shell currently exports a live OPENROUTER_API_KEY, which broke the trust-spine falsifier and leaked into a test log — treat that key as exposed and rotate it, and always run suites key-unset.