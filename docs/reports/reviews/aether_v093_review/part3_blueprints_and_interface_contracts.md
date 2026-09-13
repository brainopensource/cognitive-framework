---
id: aether-v093-review-part3-interface-blueprints
class: report
authority: non-canonical
canonical_for: []
status: living
owner: architecture-review
version: "0.9.3"
last_verified: 2026-09-11
supersedes: []
superseded_by: null
---

# Concrete Code Blueprints & Interface Contracts

> [!IMPORTANT]
> **Implementation Status & Lifecycle Classification (Current Head: `2989d57d` / September 2026)**:  
> This document specifies Python reference algorithms and interface contracts. The table below standardizes the operational lifecycle status of each blueprint:
>
> | Blueprint Component | Production Owner | Lifecycle Status | Existing Production Integration |
> |---|---|:---:|---|
> | **MemoryView & Snapshot Values** (§2) | [`domain/`](../../../../vanguard/packages/domain/) | **`[DONE - INTEGRATED]`** | Delivered in [`domain/task_state.py`](../../../../vanguard/packages/domain/task_state.py) via `T-100` (Schema `aether.memory-view/1`, JCS canonicalization). |
> | **Prefix Stability & Eviction** (§3) | [`agency/context/`](../../../../vanguard/packages/agency/context/) | **`[DONE - INTEGRATED]`** | Delivered in [`compiler.py`](../../../../vanguard/packages/agency/context/compiler.py) and [`compaction.py`](../../../../vanguard/packages/agency/context/compaction.py) via `T-104`, `T-77` (Schema `aether.context-policy/2`). |
> | **Finite Recovery Controller** (§4) | [`agency/episode/`](../../../../vanguard/packages/agency/episode/) | **`[DONE - INTEGRATED]`** | Delivered in [`protocol_recovery.py`](../../../../vanguard/packages/agency/episode/protocol_recovery.py) via `T-106` (Schema `aether.recovery-state/1`). |
> | **Transaction Preflight & Checks** (§5) | [`adapters/environment/`](../../../../vanguard/packages/adapters/environment/) | **`[DONE - INTEGRATED]`** | Delivered in [`transaction.py`](../../../../vanguard/packages/adapters/environment/transaction.py); atomic multi-file preflight passes 5/5 tests. |
> | **Exact String Replace (`str_replace`)** (§5) | [`adapters/environment/`](../../../../vanguard/packages/adapters/environment/) | **`[NEXT - TODO]`** | Tracked as [`T-78`](../../../execution/main/tasks.md#L819) (`str_replace_exact.py`) under MS-CHANGE. |
> | **Virtual CAS Workspace & Promotion** (§5) | [`ports/`](../../../../vanguard/packages/ports/), [`adapters/`](../../../../vanguard/packages/adapters/) | **`[PROPOSAL - EXPERIMENTAL]`** | Prototype algorithms for `CAS-01` ([`T-112`–`T-116`](../../../execution/main/tasks.md#L281-L309)); gated on MS-CONTROL closure. |
> | **Controller Coding FSM** (§6) | [`packs/code-default/`](../../../../packs/code-default/) | **`[DONE - INTEGRATED]`** | Outcome-driven phase progression implemented across [`EpisodeEngine`](../../../../vanguard/packages/agency/episode/engine.py). |
> | **Attenuated Read-Only Delegation** (§6) | [`agency/`](../../../../vanguard/packages/agency/), [`runtime/`](../../../../vanguard/packages/runtime/) | **`[PROPOSAL - EXPERIMENTAL]`** | Prototype delegation logic for `DEL-01` ([`T-117`–`T-118`](../../../execution/main/tasks.md#L316-L323)); gated on MS-CONTROL closure. |

## 1. Implementation boundary

These blueprints implement the decisions in [Part 1](part1_modular_hardware_architecture.md) and [Part 2](part2_benchmark_mastery_and_topologies.md): one durable controller, bounded context, immutable evidence, safe candidate edits, and optional attenuated specialists. They are executable reference algorithms, not claims that the integrations are already deployed. The inspected HEAD was `8b7b642cf4d67ea06161590fc9e1af76d2b0cbe2` (reconciled through candidate `2989d57d4d38c01eecdb7a5fbb6f125077f00e59`).

All Python fences concatenate in document order into one Python 3.10+ reference module. Imports are shared deliberately. During production integration, split definitions by the ownership table above; do not copy the combined module into a lower layer. Ellipses appear only in abstract protocol methods. External effects are explicit dependencies, not empty implementations disguised as working storage, authorization, or execution.

No kernel additions are proposed. Scope types are imported only by the agency section, never by public port definitions. Runtime owns event admission and composition; it does not execute subprocesses. Syntax inspection remains a pack-side operation. Storage and verification protocols below specify behavioral obligations beyond structural typing, and require adapter conformance before production activation.

## 2. Working memory: canonical values and evidence [DONE - INTEGRATED IN PRODUCTION]

Reuse [SemanticTaskState](../../../../vanguard/packages/domain/task_state.py) rather than inventing another authoritative blackboard. Freeze its canonical bytes at a verified event cursor: the existing dataclass contains mappings, so a shallow frozen wrapper alone would not prevent mutation through nested dictionaries. The runtime reducer constructs this snapshot; a model may propose updates but cannot directly declare verified facts or change remaining budgets.

Evidence carries an artifact reference and subject identity. Text is an optional bounded display body; eviction never deletes the underlying artifact. Current-subject evidence may enter the prompt, while stale evidence remains available for historical reasoning through explicit retrieval. Tool interactions are indivisible groups, preserving action/result correspondence during eviction.

```python
from __future__ import annotations

import ast
import base64
import json
from dataclasses import asdict, dataclass, replace
from enum import Enum
from pathlib import PurePosixPath
from typing import Any, Callable, Mapping, Protocol, Sequence

from vanguard.packages.domain.canonicalisation.jcs import canonical_bytes
from vanguard.packages.domain.canonicalisation.digest import digest_bytes, digest_of
from vanguard.packages.domain.task_state import SemanticTaskState


def natural(value: Any) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("expected nonnegative integer")
    return value


@dataclass(frozen=True)
class Evidence:
    key: str
    subject: str
    artifact: str
    finding: str
    body: str = ""

    def __post_init__(self) -> None:
        if not all((self.key, self.subject, self.artifact, self.finding)):
            raise ValueError("evidence requires identity and finding")


@dataclass(frozen=True)
class Interaction:
    key: str
    action: str
    result: str
    artifact: str


@dataclass(frozen=True)
class MemoryView:
    task_bytes: bytes
    cursor: int
    evidence: tuple[Evidence, ...] = ()

    def __post_init__(self) -> None:
        natural(self.cursor)
        task = SemanticTaskState.from_mapping(json.loads(self.task_bytes))
        if canonical_bytes(task.to_canonical_dict()) != self.task_bytes:
            raise ValueError("task snapshot is not canonical")
        if len({e.key for e in self.evidence}) != len(self.evidence):
            raise ValueError("duplicate evidence key")

    @classmethod
    def capture(cls, task: SemanticTaskState, cursor: int,
                evidence: Sequence[Evidence] = ()) -> MemoryView:
        return cls(canonical_bytes(task.to_canonical_dict()), cursor,
                   tuple(evidence))

    def encode(self) -> bytes:
        return canonical_bytes({
            "schema": "aether.memory-view/1", "cursor": self.cursor,
            "task": json.loads(self.task_bytes),
            "evidence": [asdict(e) for e in self.evidence],
        })

    @classmethod
    def decode(cls, payload: bytes, expected_digest: str) -> MemoryView:
        if digest_bytes(payload) != expected_digest:
            raise ValueError("memory digest mismatch")
        raw = json.loads(payload)
        if raw["schema"] != "aether.memory-view/1":
            raise ValueError("unsupported memory schema")
        view = cls(canonical_bytes(raw["task"]), natural(raw["cursor"]),
                   tuple(Evidence(**item) for item in raw["evidence"]))
        if view.encode() != payload:
            raise ValueError("noncanonical or unknown memory fields")
        return view


def critical_state(view: MemoryView) -> dict[str, Any]:
    task = SemanticTaskState.from_mapping(json.loads(view.task_bytes))
    return {
        "objective": task.objective, "constraints": list(task.constraints),
        "plan": list(task.plan), "next_action": task.next_action,
        "modified_files": list(task.modified_files),
        "failure": task.failure_class, "verification": dict(task.last_verification),
        "verification_plan": list(task.verification_plan),
        "settled_effects": list(task.settled_effects),
        "remaining_budgets": dict(task.remaining_budgets),
        "requirements": list(task.completion_requirements),
        "invariants": list(task.settled_invariants),
        "hypotheses": list(task.hypotheses),
        "state_ref": digest_bytes(view.encode()), "cursor": view.cursor,
    }
```

The snapshot includes the complete existing task value: dead ends, discoveries, task DAG, recovery history, and route decisions survive serialization even when not all are displayed. `critical_state()` is a projection, not a writeback format. The caller selects relevant dead ends into source-bound evidence before compilation. If mandatory state cannot fit, compilation refuses instead of deleting a requirement. In production, loading also verifies the cursor's lineage and reducer version through the existing checkpoint machinery; a matching blob digest alone is not authorization.

## 3. Prefix stability, serialization, and bounded eviction [DONE - INTEGRATED IN PRODUCTION]

Freeze tool order as well as schema-key order. Static bytes identify a composition epoch; tool additions or changed system instructions require recomposition. Mutable facts follow that prefix. `PromptCodec` is implemented by the model adapter so budgeting counts the actual request representation, including native tool schemas and message overhead. Its `count()` must provide an exact count or a documented upper bound for the selected model, not a generic character heuristic.

The selection algorithm first removes stale evidence, then compacts result bodies, then drops low-priority evidence and oldest complete interactions. Evidence is supplied in descending priority. The newest action/result pair is retained; an oversized irreducible pair causes refusal and must be replaced upstream by a structured receipt. Hysteresis limits repeated compaction, but mandatory state can exceed the low watermark as long as it fits the hard ceiling.

```python
@dataclass(frozen=True)
class Prefix:
    system: str
    environment: str
    tools_json: bytes

    @classmethod
    def build(cls, system: str, environment: str,
              tools: Sequence[Mapping[str, Any]], cards: str = "") -> Prefix:
        if len(cards) > 4096:
            raise ValueError("capability prefix exceeds W12-A")
        names = [str(tool["name"]) for tool in tools]
        if len(set(names)) != len(names):
            raise ValueError("duplicate tool name")
        ordered = sorted((dict(t) for t in tools), key=lambda t: t["name"])
        env = environment + ("\n" + cards if cards else "")
        return cls(system, env, canonical_bytes(ordered))

    def encode(self) -> bytes:
        return canonical_bytes({"system": self.system,
                                "environment": self.environment,
                                "tools": json.loads(self.tools_json)})


class PromptCodec(Protocol):
    def encode(self, prefix: Prefix, dynamic: bytes) -> bytes: ...
    def count(self, request: bytes) -> int: ...


@dataclass(frozen=True)
class LayeredJsonCodec:
    counter: Callable[[bytes], int]

    def encode(self, prefix: Prefix, dynamic: bytes) -> bytes:
        if canonical_bytes(json.loads(dynamic)) != dynamic:
            raise ValueError("dynamic context must be canonical JSON")
        return b'{"static":' + prefix.encode() + b',"dynamic":' + dynamic + b'}'

    def count(self, request: bytes) -> int:
        return natural(self.counter(request))


@dataclass(frozen=True)
class ContextBudget:
    window: int
    output: int
    safety: int
    recovery: int

    @property
    def usable(self) -> int:
        for value in (self.window, self.output, self.safety, self.recovery):
            natural(value)
        result = self.window - self.output - self.safety - self.recovery
        if result <= 0:
            raise ValueError("no usable input budget")
        return result


@dataclass(frozen=True)
class PromptPacket:
    request: bytes
    tokens: int
    prefix_digest: str
    state_digest: str
    omitted: tuple[str, ...]


def compile_packet(prefix: Prefix, view: MemoryView, subject: str,
                   turns: Sequence[Interaction], budget: ContextBudget,
                   codec: PromptCodec) -> PromptPacket:
    if len({turn.key for turn in turns}) != len(turns):
        raise ValueError("duplicate interaction key")
    critical = critical_state(view)
    notes = [e for e in view.evidence if e.subject == subject]
    recent = list(turns)
    omitted = ["stale:" + e.key for e in view.evidence if e.subject != subject]

    def render() -> tuple[bytes, int]:
        dynamic = canonical_bytes({"task": critical,
            "evidence": [asdict(e) for e in notes],
            "interactions": [asdict(t) for t in recent]})
        request = codec.encode(prefix, dynamic)
        return request, natural(codec.count(request))

    request, size = render()
    ceiling = budget.usable
    target = ceiling * 60 // 100 if size > ceiling * 80 // 100 else ceiling
    for index in range(len(notes) - 1, -1, -1):
        if size <= target:
            break
        if notes[index].body:
            omitted.append("body:" + notes[index].key)
            notes[index] = replace(notes[index], body="")
            request, size = render()
    for index in range(max(0, len(recent) - 1)):
        if size <= target:
            break
        item = recent[index]
        recent[index] = replace(item, result="Result artifact: " + item.artifact)
        omitted.append("result:" + item.key)
        request, size = render()
    while size > target and notes:
        omitted.append("evidence:" + notes.pop().key)
        request, size = render()
    while size > target and len(recent) > 1:
        omitted.append("interaction:" + recent.pop(0).key)
        request, size = render()
    if size > ceiling:
        raise ValueError("CONTEXT_BUDGET_EXCEEDED: irreducible state")
    return PromptPacket(request, size, digest_bytes(prefix.encode()),
                        digest_bytes(view.encode()), tuple(omitted))
```

The codec must serialize the same frozen prefix identically across requests, preserve untrusted-content boundaries, and attach provider-specific cache controls only where supported. Do not concatenate untrusted evidence into system instructions. The algorithms intentionally contain no vendor retention constants; adapter configuration and cache telemetry remain governed by the provider documentation cited in Part 1. A prefix digest proves reproducible inputs, not a cache hit. Track actual reported cached tokens separately.

`LayeredJsonCodec` supplies a concrete deterministic wire envelope for a local adapter that consumes structured JSON context. Static content precedes dynamic content even though ordinary alphabetical JSON-key sorting would put `dynamic` first. Its injected counter measures that representation. Remote model adapters must implement `PromptCodec` using their actual message/tool dialect and tokenizer; counting this intermediate envelope and then expanding it into a different provider request would violate the budget contract. The compiler remains unchanged when the serializer is replaced.

This compiler performs repeated exact counts for correctness. Bound the number and body size of input records before calling it; a production optimization may maintain cached costs, but must recount the final request. Its finite loops cannot make model calls or silently spend additional inference budget. Record the packet's digest and omission manifest through the existing runtime emitter before inference so context selection is attributable.

## 4. Recovery: finite decisions across restart [DONE - INTEGRATED IN PRODUCTION]

Extend [protocol recovery](../../../../vanguard/packages/agency/episode/protocol_recovery.py), which already has semantic fingerprints and persisted retry counters. The following pure controller is a proposed bounded policy value to merge into that schema, not a second engine. It detects repeated outcomes and short cycles without treating transcript growth as progress. `progress_key` is produced from verified task facts, excluding clocks, model prose, and receipt identifiers. The workspace digest belongs in the attempt fingerprint; the progress key should not count repeatedly toggling the same patch as a new accomplishment.

```python
class RecoveryAction(str, Enum):
    CONTINUE = "continue"
    WAIT = "wait"
    REGROUND = "reground"
    REPLAN = "replan"
    CONSULT = "consult"
    STOP = "stop"


@dataclass(frozen=True)
class Attempt:
    fingerprint: str
    outcome: str
    progress_key: str
    failure: str = ""
    pending_operation: str = ""

    def __post_init__(self) -> None:
        if not all((self.fingerprint, self.outcome, self.progress_key)):
            raise ValueError("attempt requires semantic identities")
        if self.failure not in {"", "permission", "permanent", "budget",
                                "transient", "protocol", "patch", "verification",
                                "context", "tool"}:
            raise ValueError("unknown failure classification")


@dataclass(frozen=True)
class Recovery:
    history: tuple[Attempt, ...] = ()
    errors: tuple[tuple[str, int], ...] = ()
    interventions: int = 0
    decisions: int = 0

    def __post_init__(self) -> None:
        natural(self.interventions)
        natural(self.decisions)
        if len(self.history) > 12 or len(dict(self.errors)) != len(self.errors):
            raise ValueError("invalid bounded recovery state")
        for kind, count in self.errors:
            Attempt("validation", "validation", "validation", kind)
            natural(count)

    def encode(self) -> bytes:
        return canonical_bytes(asdict(self))

    @classmethod
    def decode(cls, payload: bytes) -> Recovery:
        raw = json.loads(payload)
        state = cls(tuple(Attempt(**a) for a in raw["history"]),
                    tuple((str(k), natural(v)) for k, v in raw["errors"]),
                    natural(raw["interventions"]), natural(raw["decisions"]))
        if len(state.history) > 12 or state.encode() != payload:
            raise ValueError("invalid recovery snapshot")
        return state


@dataclass(frozen=True)
class RecoveryStep:
    state: Recovery
    action: RecoveryAction
    reason: str
    delay_ms: int = 0


def recover(state: Recovery, attempt: Attempt, remaining_ms: int,
            remaining_turns: int, jitter: float) -> RecoveryStep:
    natural(remaining_ms)
    natural(remaining_turns)
    if not 0.0 <= jitter <= 1.0:
        raise ValueError("jitter must be in [0, 1]")
    errors = dict(state.errors)
    if attempt.failure:
        errors[attempt.failure] = errors.get(attempt.failure, 0) + 1
    updated = replace(state, errors=tuple(sorted(errors.items())),
                      decisions=state.decisions + 1)
    if remaining_turns == 0 or remaining_ms == 0:
        return RecoveryStep(updated, RecoveryAction.STOP, "budget exhausted")
    if attempt.failure in {"permission", "permanent", "budget"}:
        return RecoveryStep(updated, RecoveryAction.STOP, attempt.failure)
    if attempt.failure == "transient":
        number = errors["transient"]
        delay = int(min(8000, 500 * 2 ** min(number - 1, 4)) * (0.5 + jitter / 2))
        if number > 3 or delay >= remaining_ms:
            return RecoveryStep(updated, RecoveryAction.STOP, "transport limit")
        return RecoveryStep(updated, RecoveryAction.WAIT, "transient", delay)
    if attempt.pending_operation and not attempt.failure:
        return RecoveryStep(updated, RecoveryAction.WAIT, "poll existing handle",
                            min(1000, remaining_ms))
    history = (state.history + (attempt,))[-12:]
    updated = replace(updated, history=history)
    window = history[-6:]
    keys = [(a.fingerprint, a.outcome, a.progress_key) for a in window]
    repeated = keys.count(keys[-1]) >= 3
    cycle = any(len(keys) >= 2 * n and keys[-n:] == keys[-2 * n:-n]
                for n in (2, 3))
    unchanged = len(window) == 6 and len({a.progress_key for a in window}) == 1
    if not (attempt.failure or repeated or cycle or unchanged):
        return RecoveryStep(updated, RecoveryAction.CONTINUE, "observed progress")
    level = state.interventions
    actions = (RecoveryAction.REGROUND, RecoveryAction.REPLAN, RecoveryAction.CONSULT)
    action = actions[level] if level < len(actions) else RecoveryAction.STOP
    updated = replace(updated, interventions=level + 1)
    return RecoveryStep(updated, action, attempt.failure or "semantic stall")
```

The intervention allowance is cumulative for a task, including after restart or model switching. Its conservative three-step default is an explicit policy parameter to calibrate, not a universal optimum. Each decision must be durably appended before another request or effect; storage failure stops execution. The scheduler supplies jitter and persists the selected delay/deadline, so replay reuses a decision rather than resampling it. A pending operation requires a separate persisted deadline and budget charging; this function never grants unlimited polling.

`CONSULT` requests a bounded change of strategy, not more authority. If no consultation budget exists, the caller transitions to stop. Verification failures trigger regrounding or replanning immediately; they do not receive transport backoff. Provider failures with unknown usage retain their reservations until reconciliation. On terminal exhaustion the candidate manager below leaves the active subject intact.

## 5. Multi-file editing: immutable candidates and atomic promotion [HYBRID: PREFLIGHT DONE; CAS PROPOSAL]

Refine Part 2's isolated-candidate design into a versioned workspace. A complete tree manifest includes regular files and directories, including modes and empty directories. Symlinks and special files are deliberately unsupported in this initial adapter contract and must be rejected during capture. Candidate preparation changes immutable values only. Failed verification therefore requires no destructive inverse edits: the active version remains byte-for-byte the baseline.

This is an extension path for the existing [transaction adapter](../../../../vanguard/packages/adapters/environment/transaction.py), not a claim that its current sequential `os.replace()` loop has these guarantees. A normal user checkout requires a separate locked export/journal operation after candidate acceptance; do not claim atomic publication to arbitrary host paths. The framework workspace must resolve its active version from the ledger-backed branch head for this algorithm to provide atomic visibility.

```python
@dataclass(frozen=True)
class Node:
    path: str
    data: bytes | None
    mode: int = 0o644

    def __post_init__(self) -> None:
        path = PurePosixPath(self.path)
        if (not self.path or path.is_absolute() or ".." in path.parts
                or ".git" in path.parts or "\\" in self.path
                or "\x00" in self.path or str(path) != self.path
                or self.path == "."):
            raise ValueError("unsafe or noncanonical path")
        if type(self.mode) is not int or not 0 <= self.mode <= 0o777:
            raise ValueError("unsupported mode")

    def wire(self) -> dict[str, Any]:
        return {"path": self.path, "mode": self.mode,
                "data": None if self.data is None else
                base64.b64encode(self.data).decode("ascii")}


@dataclass(frozen=True)
class Tree:
    nodes: tuple[Node, ...]

    def __post_init__(self) -> None:
        table = {node.path: node for node in self.nodes}
        if len(table) != len(self.nodes):
            raise ValueError("duplicate path")
        for node in self.nodes:
            for parent in PurePosixPath(node.path).parents:
                if str(parent) != ".":
                    entry = table.get(str(parent))
                    if entry is None or entry.data is not None:
                        raise ValueError("missing or non-directory parent")

    def encode(self) -> bytes:
        return canonical_bytes([n.wire() for n in sorted(self.nodes,
                                                       key=lambda n: n.path)])

    @classmethod
    def decode(cls, payload: bytes) -> Tree:
        raw = json.loads(payload)
        tree = cls(tuple(Node(n["path"], None if n["data"] is None else
                              base64.b64decode(n["data"], validate=True), n["mode"])
                         for n in raw))
        if tree.encode() != payload:
            raise ValueError("noncanonical tree")
        return tree


@dataclass(frozen=True)
class Edit:
    path: str
    expected: str | None
    replacement: Node | None


def stage(before: Tree, edits: Sequence[Edit]) -> Tree:
    if not edits or len({e.path for e in edits}) != len(edits):
        raise ValueError("empty or duplicate edit set")
    table = {n.path: n for n in before.nodes}
    for edit in edits:
        Node(edit.path, None)
        old = table.get(edit.path)
        actual = None if old is None else digest_of(old.wire())
        if actual != edit.expected:
            raise ValueError("PATCH_PREIMAGE_MISMATCH")
        if edit.replacement is None:
            if old is None:
                raise ValueError("cannot delete absent path")
            del table[edit.path]
        else:
            node = edit.replacement
            if node.path != edit.path:
                raise ValueError("replacement path mismatch")
            if node.data is not None and node.path.endswith(".py"):
                ast.parse(node.data, filename=node.path)
            table[edit.path] = node
    return Tree(tuple(table.values()))


class SnapshotBlobs(Protocol):
    def put(self, payload: bytes) -> str: ...
    def get(self, digest: str) -> bytes: ...


@dataclass(frozen=True)
class Check:
    argv: tuple[str, ...]
    cwd: str
    environment_digest: str
    timeout_ms: int
    minimum_tests: int = 1

    def __post_init__(self) -> None:
        natural(self.minimum_tests)
        if not self.argv or not self.environment_digest or self.timeout_ms <= 0:
            raise ValueError("incomplete verification command")
        if self.cwd != ".":
            Node(self.cwd, None)


@dataclass(frozen=True)
class CheckReceipt:
    command_digest: str
    subject: str
    exit_code: int
    collected: int
    timed_out: bool
    artifact: str

    def accepts(self, check: Check, subject: str) -> bool:
        return (self.command_digest == digest_of(asdict(check))
                and self.subject == subject and self.exit_code == 0
                and not self.timed_out and self.collected >= check.minimum_tests
                and bool(self.artifact))


class CandidateVerifier(Protocol):
    def run(self, subject: str, check: Check) -> CheckReceipt: ...


class PromotionLedger(Protocol):
    def head(self, branch: str) -> str: ...
    def committed(self, transaction: str) -> str | None: ...
    def promote(self, transaction: str, branch: str, expected: str,
                candidate: str, receipts: tuple[CheckReceipt, ...]) -> bool: ...


@dataclass(frozen=True)
class TransactionResult:
    transaction: str
    candidate: str
    disposition: str


def transact(branch: str, baseline: str, edits: Sequence[Edit],
             checks: Sequence[Check], blobs: SnapshotBlobs,
             verifier: CandidateVerifier, ledger: PromotionLedger) -> TransactionResult:
    if not branch or not checks:
        raise ValueError("branch and verification required")
    original = blobs.get(baseline)
    if digest_bytes(original) != baseline:
        raise ValueError("corrupt baseline")
    candidate = stage(Tree.decode(original), edits).encode()
    subject = digest_bytes(candidate)
    transaction = digest_of({"branch": branch, "baseline": baseline,
                             "candidate": subject,
                             "checks": [asdict(c) for c in checks]})
    prior = ledger.committed(transaction)
    if prior is not None:
        if prior != subject:
            raise ValueError("transaction identity conflict")
        return TransactionResult(transaction, subject, "already_committed")
    if ledger.head(branch) != baseline:
        return TransactionResult(transaction, subject, "conflict")
    if blobs.put(candidate) != subject:
        raise ValueError("blob store violated content identity")
    receipts: list[CheckReceipt] = []
    for check in checks:
        receipt = verifier.run(subject, check)
        receipts.append(receipt)
        if not receipt.accepts(check, subject):
            return TransactionResult(transaction, subject, "rejected")
    committed = ledger.promote(transaction, branch, baseline, subject, tuple(receipts))
    return TransactionResult(transaction, subject,
                             "committed" if committed else "conflict")
```

`SnapshotBlobs.put()` must durably persist immutable content before returning, and `get()` must enforce authorized access. The initial implementation stores complete tree manifests; larger deployments can replace inline file bodies with existing CAS references without changing the promotion algorithm. Capture is bounded by repository byte limits. Exact byte-span or strict diff frontends must produce this complete edit set; stale or ambiguous patches never invoke a permissive rewrite fallback.

`CandidateVerifier` runs the named command in a sandbox materialized from the candidate, with no writable access to the active branch, sibling workspaces, snapshot store, or ledger. The source subject is immutable; generated outputs use scratch mounts. It must record command and environment identity, collect output artifacts, and honor cancellation and deadlines. Compilation/build checks may explicitly set `minimum_tests=0`; test-policy checks require positive collection. The pack supplies this policy, never the model's proposed receipt.

`PromotionLedger.promote()` is the atomic boundary: inside the existing single-writer transaction, check idempotency, compare branch head to `expected`, authenticate verifier receipts, verify the required check set, and append a commit event containing old/new subjects and evidence. It must not maintain a second independently writable head. The branch head is an event projection, updated transactionally or recomputed from events. The verifier and ledger bindings are trusted runtime dependencies; model-supplied dataclasses are not accepted as authenticated receipts.

Before promotion, exceptions, cancellation, failed assertions, and budget exhaustion leave the active head unchanged; immutable failed candidates can be retained for diagnosis. After successful promotion, a lost reply is reconciled with `committed(transaction)`, not an inverse write. A later rollback is a new compare-and-append operation targeting the old snapshot, preserving history and refusing to overwrite a concurrently advanced head. Process restart never reruns settled effects blindly. This gives a precise fail-closed guarantee while acknowledging that durability, isolated execution, and atomic compare-and-append require qualified concrete adapters.

## 6. Controller FSM and attenuated delegation [HYBRID: CONTROLLER DONE; SPECIALISTS PROPOSAL]

Retain the public `IPlanner` SPI. The following coding phase reducer sits behind it: proposals request actions, but only typed, fresh observations advance phases. In the integration, an accepted candidate transaction means all configured targeted and broader checks passed; `COMPLETE` still needs requirement coverage and generic completion admission. Greenfield tasks enter through baseline/harness establishment instead of requiring an invented failing test.

```python
class Phase(str, Enum):
    DISCOVER = "discover"
    PLAN = "plan"
    EDIT = "edit"
    VERIFY = "verify"
    COMPLETE = "complete"
    STOP = "stop"


@dataclass(frozen=True)
class Control:
    phase: Phase = Phase.DISCOVER
    candidate: str = ""


def advance(control: Control, event: str, subject: str = "",
            requirements_met: bool = False) -> Control:
    if control.phase in {Phase.COMPLETE, Phase.STOP}:
        raise ValueError("terminal controller")
    if event == "exhausted":
        return replace(control, phase=Phase.STOP)
    if event == "failed":
        return Control(Phase.PLAN)
    if control.phase is Phase.DISCOVER and event == "baseline_ready":
        return Control(Phase.PLAN)
    if control.phase is Phase.PLAN and event == "plan_admitted":
        return Control(Phase.EDIT)
    if control.phase is Phase.EDIT and event == "candidate_staged" and subject:
        return Control(Phase.VERIFY, subject)
    if (control.phase is Phase.VERIFY and event == "transaction_committed"
            and subject == control.candidate and requirements_met):
        return Control(Phase.COMPLETE, subject)
    raise ValueError("invalid or stale phase transition")


class PlannerPolicy(Protocol):
    def propose(self, control: Control, memory: MemoryView,
                allowed_actions: tuple[str, ...]) -> bytes: ...


class SpawnGateway(Protocol):
    def reserve_and_spawn(self, identity: str, request: bytes) -> str: ...
    def reconcile(self, identity: str) -> str | None: ...


# Agency-owned imports; never move these into ports or domain modules.
from vanguard.packages.kernel.attenuation import Scope, attenuate


def delegate_readonly(parent: Scope, requested: Scope, role: str,
                      task: str, inputs: tuple[str, ...], call_id: str,
                      read_verbs: frozenset[str], gateway: SpawnGateway) -> str:
    if not all((role, task, call_id)) or not inputs:
        raise ValueError("incomplete specialist contract")
    if not requested.actions or not requested.actions <= read_verbs:
        raise PermissionError("specialist may only use declared read verbs")
    result = attenuate(parent, requested)
    if result.granted is None:
        raise PermissionError(str(result.denial))
    scope = result.granted
    request = canonical_bytes({
        "role": role, "task": task, "inputs": list(inputs),
        "output_schema": "aether.specialist-findings/1",
        "scope": {"actions": sorted(scope.actions),
                  "resources": list(scope.resources),
                  "constraints": asdict(scope.constraints),
                  "depth": scope.depth, "sealed": True},
    })
    identity = digest_of({"call_id": call_id, "request": digest_bytes(request)})
    prior = gateway.reconcile(identity)
    return prior if prior is not None else gateway.reserve_and_spawn(identity, request)
```

`read_verbs` is composition-owned, derived from reviewed effect classifications, not inferred from tool names or supplied by a model. The gateway revalidates wire values, parent grant binding, current expiry/revocation, and resources before canonical spawn. `attenuate()` checks scope inclusion; it does not reserve aggregate sibling budgets or issue executable grants. `reserve_and_spawn()` must idempotently record the child intent and reserve additive dimensions from the parent governor before dispatch. Unknown dispatch outcomes remain reserved and are reconciled through the same identity; an exception must not automatically refund potentially spent resources.

The parent is the sole mutating controller. Specialists return artifact-bound findings, proposed hypotheses, and limitations; they cannot change the parent task projection, certify completion, or promote snapshots. The existing planner adapter decodes `PlannerPolicy.propose()` through the current proposal dialect, then uses kernel dispatch. JSON bytes are a transport boundary, not an authorization bypass. Preserve complete grant attenuation at dispatch even if the offered tool set was already narrowed in the prompt.

## 7. Integration and falsification obligations [REFERENCE & VERIFIED STATUS]

These algorithms intentionally separate pure policy from external mechanisms. Integrate memory capture through the existing task-state fold, prompt selection through `ContextCompiler`, recovery through `ProtocolRecoveryState`, transactions through the environment adapter, and phase decisions through the code pack. Preserve existing schema readers when adding fields. Version behavior-affecting policies in the composition identity and record every selection or transition through the runtime's single emitter.

Qualification must cover canonical round trips, stale evidence eviction, exact final budgeting, invariant-prefix stability, semantic cycles across restart, exhausted retry allowances, and stale completion rejection. Transaction tests must show that a failure on the second file or second verifier leaves the baseline active, creates/deletes preserve the full manifest, concurrent promotion loses the compare-and-append race cleanly, and a lost successful reply reconciles without duplicate publication. Fault-inject durable blob writes and the commit boundary; in-memory doubles cannot prove crash durability.

Use existing suites as integration anchors: `test.contracts.test_semantic_task_state`, `test.agency.test_context_compiler`, `test.agency.test_protocol_recovery`, `test.runtime.test_atomic_multi_file_transaction`, and `test.agency.test_episode_spawn`. New snapshot-adapter tests must additionally verify filesystem capture, mode preservation, rejection of symlinks, and read-only verification mounts. Required invariants remain boundary flow, I-7, I-6, N-06, and the 1,438-LOC kernel ceiling. The planned kernel delta is zero; blueprint execution alone does not certify a future implementation or benchmark score.

### Validation performed for this report

The five Python blocks were extracted, concatenated, parsed with Python 3.10 grammar, and executed through the test-runner skill under a 30-second timeout. Twelve behavioral tests passed, including memory round trips, prefix ordering, bounded eviction, latest-result retention, recovery persistence, bounded backoff, stale preimages, a second-file syntax failure, second-verifier failure, interrupted verification, stale/empty verification, promotion replay/conflict, directory/mode preservation, phase freshness, and delegation denial. These tests use in-memory effect doubles; they establish algorithm behavior, not disk-crash durability or provider caching.

Direct document metadata, local-link, boundary, TCB, domain-blindness, and isolation-policy checks passed. The kernel remains 1,386 logical LOC. `just check` and `just verify` could not start because `just` is unavailable; Markdown lint could not load its installed `fast-glob` dependency. No production code or existing report was changed. The integration suites named above are required future falsifiers, not additional suites claimed as executed for this report.
