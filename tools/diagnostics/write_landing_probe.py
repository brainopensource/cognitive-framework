"""T-130 — hermetic write-landing seam diagnostic.

RUN-13 asks one question and this module refuses to answer any other: when a
capable model spends turns on a coding task and zero files change, *which seam
on the product route dropped the write?*

The route exercised here is the shipped one, entered at
``runtime.entrypoint.execute`` through :mod:`benchmarks.product_path`:

    entrypoint.execute -> runtime.root.Runtime -> runtime.session.HarnessSession
    -> agency.episode.EpisodeEngine -> model adapter + dialect normalization
    -> tool admission / capability grant -> patch transaction + candidate
    workspace -> completion admission -> exterior oracle -> reconciliation

Forge and BaaC are *not* substituted anywhere in this file.

RUN-12 is honoured absolutely: the only model is :class:`ProviderTapeModel`,
which serves recorded provider-format bodies from an in-memory cassette and
normalizes them with the very translator the shipped OpenRouter and LAM
adapters call (``ProposalTranslator.translate``, cf.
``adapters/models/openrouter.py:1250`` and ``adapters/models/lam.py:131``).
Zero provider calls, zero USD, zero tokens, no network, no Ollama.

RUN-10 is honoured absolutely: nothing here imports a product module in order
to change it. The probe is an observer. It names no repair site, and it makes
no claim about ``entrypoint.py``.

The instrument correlates, in ONE trace per turn:
  * the raw provider body the model returned,
  * the tool declarations that were actually offered on that turn,
  * the normalized proposal identity (or the typed normalization failure),
  * the ledger's grant / dispatch / rejection / approval events,
  * the filesystem postimage of the candidate workspace,
  * and an exterior-oracle re-observation of that same tree.

A "just run a fake tape" probe would see none of that; that is why the ledger
is read back out of the durable store rather than trusted from projections.

Usage (repository root, package-relative so ``benchmarks`` resolves)::

    python3 -m tools.diagnostics.write_landing_probe [packet.json]
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from benchmarks.product_path import execute_product
from vanguard.packages.adapters.models.invocation import ProposalTranslator
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.ports.event_store import EventRange, Result

__all__ = [
    "SEAMS",
    "Seam",
    "TurnRecord",
    "ProbeTrace",
    "ProviderTapeModel",
    "tree_digest",
    "exterior_oracle_digest",
    "attribute",
    "run_probe",
    "positive_control",
    "negative_control",
    "FIXTURES",
    "fixture_dir",
    "materialize",
    "canonical_write_tape",
    "run_all",
]

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "benchmarks" / "diagnostics" / "fixtures"

#: Ignored when digesting a candidate tree: harness state, not candidate code.
_EXCLUDED_DIRS = frozenset({".vanguard", ".git", "__pycache__", ".venv"})


# --------------------------------------------------------------------------
# Seam vocabulary. Order IS the attribution order: the first seam whose
# evidence fires is the answer, and later seams are never allowed to overwrite
# an earlier one.
# --------------------------------------------------------------------------

class Seam(str):
    """A seam label. A plain string subclass so traces stay JSON-serialisable."""


SEAM_RESOURCE_EXHAUSTION = Seam("resource_exhaustion_before_first_valid_action")
SEAM_NO_CANONICAL_TOOL = Seam("no_canonical_tool_emitted")
SEAM_MALFORMED_CALL = Seam("undeclared_or_malformed_tool_call")
SEAM_POLICY_DENIAL = Seam("capability_or_policy_denial")
SEAM_PATCH_REJECTED = Seam("patch_transaction_rejected_or_partial")
SEAM_WRONG_WORKSPACE = Seam("wrong_candidate_workspace")
SEAM_STALE_TREE = Seam("stale_tree_observed_by_oracle")
SEAM_PATCHLESS_COMPLETION = Seam("patchless_completion_admitted")
SEAM_NOT_REPRODUCED = Seam("NOT_REPRODUCED")

#: The eight discrimination classes T-130 fixes, in attribution order.
SEAMS: tuple[Seam, ...] = (
    SEAM_RESOURCE_EXHAUSTION,
    SEAM_NO_CANONICAL_TOOL,
    SEAM_MALFORMED_CALL,
    SEAM_POLICY_DENIAL,
    SEAM_PATCH_REJECTED,
    SEAM_WRONG_WORKSPACE,
    SEAM_STALE_TREE,
    SEAM_PATCHLESS_COMPLETION,
)


# --------------------------------------------------------------------------
# Tree identity. Two independent walkers on purpose: the candidate-side digest
# and the exterior-oracle digest must be computed by code that does not share
# a cached listing, or "the oracle saw a stale tree" is unobservable.
# --------------------------------------------------------------------------

def _relevant(path: Path, base: Path) -> bool:
    rel = path.relative_to(base)
    return not any(part in _EXCLUDED_DIRS for part in rel.parts)


def tree_digest(base: Path) -> str:
    """Digest of the candidate workspace as the harness leaves it."""
    entries: list[str] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file() or not _relevant(path, base):
            continue
        rel = path.relative_to(base).as_posix()
        entries.append(f"{rel}:{hashlib.sha256(path.read_bytes()).hexdigest()}")
    return "sha256:" + hashlib.sha256("\n".join(entries).encode()).hexdigest()


def exterior_oracle_digest(base: Path) -> tuple[str, dict[str, str]]:
    """Re-observe the submitted tree from outside, without reusing the walk.

    Returns the digest and the per-file map, so a divergence can be reported
    as named files rather than as two opaque hashes.
    """
    observed: dict[str, str] = {}
    stack = [base]
    while stack:
        current = stack.pop()
        for child in sorted(current.iterdir()):
            if child.name in _EXCLUDED_DIRS:
                continue
            if child.is_dir():
                stack.append(child)
            elif child.is_file():
                observed[child.relative_to(base).as_posix()] = hashlib.sha256(
                    child.read_bytes()).hexdigest()
    joined = "\n".join(f"{k}:{v}" for k, v in sorted(observed.items()))
    return "sha256:" + hashlib.sha256(joined.encode()).hexdigest(), observed


# --------------------------------------------------------------------------
# The model. Provider-format in, canonical proposal out, everything recorded.
# --------------------------------------------------------------------------

@dataclass
class TurnRecord:
    """Everything observable about one model turn, captured at the seam."""

    turn: int
    offered_tools: tuple[str, ...]
    offered_tool_names: tuple[str, ...]
    tool_choice: str | None
    raw: Any
    normalized: Mapping[str, Any] | None = None
    normalization_error: str | None = None
    emitted_action: str | None = None
    emitted_kind: str | None = None
    had_tool_call: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "turn": self.turn,
            "offeredToolVerbs": list(self.offered_tools),
            "offeredToolNames": list(self.offered_tool_names),
            "toolChoice": self.tool_choice,
            "raw": self.raw,
            "normalized": dict(self.normalized) if self.normalized else None,
            "normalizationError": self.normalization_error,
            "emittedKind": self.emitted_kind,
            "emittedAction": self.emitted_action,
            "hadProviderToolCall": self.had_tool_call,
        }


class ProviderTapeModel:
    """A ``ModelPort`` that replays provider bodies through real normalization.

    The tape holds OpenAI-shaped chat-completion bodies — the wire form the
    shipped adapters receive. Each turn is lowered to the adapter's
    intermediate ``{"text", "toolCalls"}`` proposal and then handed to
    ``ProposalTranslator.translate`` with the *tool schemas the engine actually
    offered on that turn*, which is the only way the declared-name/verb seam is
    observable at all.

    Exhausting the tape is a typed ``instrument_error``, never a task verdict
    (ICD §4).
    """

    def __init__(self, bodies: Sequence[Mapping[str, Any]], *, name: str = "probe-tape") -> None:
        self._bodies = list(bodies)
        self._cursor = 0
        self.name = name
        self.turns: list[TurnRecord] = []
        self.exhausted = False

    # -- ModelPort ---------------------------------------------------------
    def propose(self, context: Any, tools: Any, sampling: Any) -> Result:
        schemas = [dict(t) for t in (tools or ())]
        verbs = tuple(str(t.get("verb") or "") for t in schemas)
        names = tuple(str(t.get("name") or "") for t in schemas)
        choice = None
        if isinstance(sampling, Mapping):
            choice = sampling.get("toolChoice")
        index = self._cursor
        if self._cursor >= len(self._bodies):
            self.exhausted = True
            self.turns.append(TurnRecord(
                turn=index, offered_tools=verbs, offered_tool_names=names,
                tool_choice=choice, raw=None,
                normalization_error="tape exhausted: no recorded turn remains",
            ))
            return Result.fail(
                kind="instrument_error",
                message="probe tape exhausted: no more recorded provider bodies",
            )
        body = self._bodies[self._cursor]
        self._cursor += 1

        record = TurnRecord(
            turn=index, offered_tools=verbs, offered_tool_names=names,
            tool_choice=choice, raw=json.loads(json.dumps(body, default=str)),
        )
        self.turns.append(record)

        raw_proposal = _lower_provider_body(body)
        record.had_tool_call = bool(raw_proposal and raw_proposal.get("toolCalls"))
        if raw_proposal is None:
            record.normalization_error = "provider body carried no choices/message"
            return Result.fail(kind="instrument_error",
                               message=record.normalization_error)
        translated = ProposalTranslator.translate(raw_proposal, tool_schemas=schemas)
        if not getattr(translated, "ok", False):
            error = getattr(translated, "error", None)
            record.normalization_error = (
                f"{getattr(error, 'kind', 'instrument_error')}: "
                f"{getattr(error, 'message', 'normalization failed')}")
            return Result.fail(kind=str(getattr(error, "kind", "instrument_error")),
                               message=str(getattr(error, "message", "normalization failed")))
        canonical = dict(translated.value)
        record.normalized = canonical
        record.emitted_kind = str(canonical.get("kind") or "")
        record.emitted_action = canonical.get("action")
        return Result.success(canonical)


def _lower_provider_body(body: Mapping[str, Any]) -> dict[str, Any] | None:
    """Lower an OpenAI-shaped body to the adapter's intermediate proposal.

    This mirrors ``adapters/models/lam.py`` rather than reimplementing
    anything: the provider envelope is unwrapped, and every downstream
    decision is the shipped translator's.
    """
    choices = body.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    message = choices[0].get("message")
    if not isinstance(message, Mapping):
        return None
    calls: list[dict[str, Any]] = []
    for raw in message.get("tool_calls") or ():
        if not isinstance(raw, Mapping):
            continue
        function = raw.get("function")
        function = function if isinstance(function, Mapping) else raw
        calls.append({
            "id": raw.get("id"),
            "name": function.get("name", ""),
            "arguments": function.get("arguments", {}),
        })
    return {
        "text": str(message.get("content") or ""),
        "toolCalls": calls,
        "resolved_model": "probe-tape",
        "pricing_known": True,
        "usd_micros": 0,
    }


def provider_body(
    *, name: str | None = None, arguments: Mapping[str, Any] | None = None,
    content: str = "",
) -> dict[str, Any]:
    """Build one OpenAI-shaped provider body for the tape."""
    message: dict[str, Any] = {"role": "assistant", "content": content}
    if name is not None:
        message["tool_calls"] = [{
            "id": f"call_{name}",
            "type": "function",
            "function": {"name": name, "arguments": json.dumps(dict(arguments or {}))},
        }]
    return {"id": "probe", "object": "chat.completion",
            "choices": [{"index": 0, "message": message, "finish_reason": "tool_calls"}]}


# --------------------------------------------------------------------------
# Ledger readback. Projections are a summary; the durable event stream is the
# evidence, so grant/dispatch/approval correlation is read back from sqlite.
# --------------------------------------------------------------------------

_LEDGER_KINDS_OF_INTEREST = (
    "ProposalProduced", "CapabilityGranted", "CapabilityDenied",
    "EffectDispatched", "EffectApplied", "EffectFailed", "EffectRejected",
    "ApprovalRequested", "ApprovalResolved", "PatchApplied",
    "TurnStarted", "RunTerminated", "VerdictRecorded",
)


def read_ledger(store_path: Path, run_id: str) -> list[dict[str, Any]]:
    """Read the durable event stream for one run, newest-last."""
    if not store_path.exists():
        return []
    store = SqliteEventStore(str(store_path))
    try:
        read = store.read(EventRange(run_id=run_id))
        if not getattr(read, "ok", False):
            return []
        rows: list[dict[str, Any]] = []
        for env in read.value or ():
            payload = getattr(env, "payload", {}) or {}
            kind = payload.get("kind") if isinstance(payload, Mapping) else None
            kind = kind or getattr(env, "mhf_kind", "") or getattr(env, "kind", "")
            rows.append({"kind": str(kind), "seq": str(getattr(env, "seq", "")),
                         "payload": _jsonable(payload)})
        return rows
    finally:
        close = getattr(store, "close", None)
        if callable(close):
            close()


def _jsonable(value: Any) -> Any:
    try:
        return json.loads(json.dumps(value, default=str))
    except Exception:  # pragma: no cover - defensive only
        return str(value)


# --------------------------------------------------------------------------
# Traces and attribution.
# --------------------------------------------------------------------------

@dataclass
class ProbeTrace:
    """One correlated trace: model side, ledger side, filesystem, oracle."""

    label: str
    fixture: str
    run_id: str | None
    workspace: str
    preimage_digest: str
    candidate_digest: str
    oracle_digest: str
    oracle_files: dict[str, str]
    changed_files: tuple[str, ...]
    terminal_outcome: str
    terminal_detail: str
    turns_consumed: int
    model_turns: list[TurnRecord] = field(default_factory=list)
    projections: list[dict[str, Any]] = field(default_factory=list)
    ledger: list[dict[str, Any]] = field(default_factory=list)
    seam: Seam | None = None
    seam_evidence: list[str] = field(default_factory=list)
    secondary_seams: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "fixture": self.fixture,
            "runId": self.run_id,
            "workspace": self.workspace,
            "preimageTreeDigest": self.preimage_digest,
            "candidateTreeDigest": self.candidate_digest,
            "oracleObservedTreeDigest": self.oracle_digest,
            "changedFiles": list(self.changed_files),
            "terminalAdmissionDisposition": self.terminal_outcome,
            "terminalDetail": self.terminal_detail,
            "turnsConsumed": self.turns_consumed,
            "modelTurns": [t.to_dict() for t in self.model_turns],
            "projections": self.projections,
            "ledgerKinds": [row["kind"] for row in self.ledger],
            "seam": str(self.seam) if self.seam else None,
            "seamEvidence": list(self.seam_evidence),
            "independentSecondarySeams": list(self.secondary_seams),
        }


def _ledger_kinds(trace: ProbeTrace) -> list[str]:
    return [row["kind"] for row in trace.ledger]


def _projection_kinds(trace: ProbeTrace) -> list[str]:
    return [str(p.get("kind")) for p in trace.projections if isinstance(p, Mapping)]


def _mutating_turns(trace: ProbeTrace) -> list[TurnRecord]:
    return [t for t in trace.model_turns if t.emitted_kind == "effect"]


def attribute(trace: ProbeTrace) -> ProbeTrace:
    """Attribute the trace to its FIRST failing seam.

    Independent later causes are retained separately in
    ``secondary_seams`` — never collapsed into the headline attribution.
    """
    evidence: list[str] = []
    seam: Seam | None = None
    ledger_kinds = _ledger_kinds(trace)
    projection_kinds = _projection_kinds(trace)
    landed = trace.candidate_digest != trace.preimage_digest

    # 1. Resource exhaustion before any valid action reached dispatch.
    exhausted_first = (
        trace.model_turns
        and trace.model_turns[0].normalization_error
        and "exhausted" in trace.model_turns[0].normalization_error
    )
    no_dispatch = not any(k in ledger_kinds for k in
                          ("EffectDispatched", "EffectApplied", "EffectRejected",
                           "EffectFailed", "CapabilityGranted"))
    if exhausted_first or (no_dispatch and trace.turns_consumed == 0
                           and trace.terminal_outcome == "budget_exhausted"):
        seam = SEAM_RESOURCE_EXHAUSTION
        evidence.append(
            f"no valid action reached dispatch; turns={trace.turns_consumed}, "
            f"terminal={trace.terminal_outcome!r}")

    # 2/3. Normalization: did any turn survive dialect normalization at all?
    if seam is None:
        first = trace.model_turns[0] if trace.model_turns else None
        if first is not None and first.normalization_error and not first.had_tool_call:
            # The provider body carried prose and no tool call at all: the
            # model never emitted a canonical action for this route to admit.
            seam = SEAM_NO_CANONICAL_TOOL
            evidence.append(
                "turn 0 carried no provider tool call; normalization returned "
                f"{first.normalization_error}")
            evidence.append(
                f"offered tool names={list(first.offered_tool_names)} "
                f"verbs={list(first.offered_tools)}")
        elif first is not None and first.normalization_error:
            # A tool call that the shipped translator could not lower, or one
            # that named something the offered declarations do not carry.
            seam = SEAM_MALFORMED_CALL
            evidence.append(
                f"turn 0 failed dialect normalization: {first.normalization_error}")
            evidence.append(
                f"offered tool names={list(first.offered_tool_names)} "
                f"verbs={list(first.offered_tools)}")
        elif trace.model_turns and not _mutating_turns(trace):
            seam = SEAM_NO_CANONICAL_TOOL
            kinds = [t.emitted_kind for t in trace.model_turns]
            evidence.append(
                f"no turn normalized to a mutating effect; kinds={kinds}")
            evidence.append(
                "offered verbs on turn 0="
                f"{list(trace.model_turns[0].offered_tools)}")

    # 4. Capability / policy denial on an otherwise well-formed effect.
    if seam is None and ("EffectRejected" in ledger_kinds
                         or "CapabilityDenied" in ledger_kinds
                         or "rejected by policy" in json.dumps(trace.projections)):
        seam = SEAM_POLICY_DENIAL
        attempted = [t.emitted_action for t in _mutating_turns(trace)]
        evidence.append(
            f"effect rejected before application; attempted actions={attempted}")
        evidence.append(
            "offered verbs on turn 0="
            f"{list(trace.model_turns[0].offered_tools) if trace.model_turns else []}")

    # 5. The transaction was admitted but did not land whole.
    if seam is None and _mutating_turns(trace) and not landed:
        seam = SEAM_PATCH_REJECTED
        evidence.append(
            "a mutating effect was admitted but the candidate tree is byte-identical "
            f"to the preimage ({trace.preimage_digest})")
        evidence.append(f"ledger kinds={ledger_kinds}")

    # 6. Something landed, but not in the tree the run was pointed at.
    if seam is None and _mutating_turns(trace) and landed and not trace.changed_files:
        seam = SEAM_WRONG_WORKSPACE
        evidence.append(
            "the tree digest moved but no file under the submitted workspace changed")

    # 7. The exterior oracle did not observe the submitted tree.
    if seam is None and trace.oracle_digest != trace.candidate_digest:
        seam = SEAM_STALE_TREE
        evidence.append(
            f"candidate={trace.candidate_digest} but oracle observed "
            f"{trace.oracle_digest}")

    # 8. Completion admitted with no source change at all.
    if seam is None and trace.terminal_outcome == "completed" and not landed:
        seam = SEAM_PATCHLESS_COMPLETION
        evidence.append(
            "terminal disposition is 'completed' with an unchanged candidate tree")

    if seam is None:
        seam = SEAM_NOT_REPRODUCED
        evidence.append(
            f"write landed atomically and the oracle observed the identical tree "
            f"({trace.candidate_digest}); changed={list(trace.changed_files)}")

    # Independent later causes, reported separately (never merged into the
    # headline seam). These are observations, not a second narrative.
    secondary: list[dict[str, Any]] = []
    if seam is not SEAM_STALE_TREE and trace.oracle_digest != trace.candidate_digest:
        secondary.append({"seam": str(SEAM_STALE_TREE),
                          "evidence": "oracle digest differs from candidate digest"})
    if (seam is not SEAM_PATCHLESS_COMPLETION
            and trace.terminal_outcome == "completed" and not landed):
        secondary.append({"seam": str(SEAM_PATCHLESS_COMPLETION),
                          "evidence": "completed with an unchanged tree"})
    later_norm = [t for t in trace.model_turns[1:] if t.normalization_error
                  and "exhausted" not in t.normalization_error]
    if seam is not SEAM_MALFORMED_CALL and later_norm:
        secondary.append({
            "seam": str(SEAM_MALFORMED_CALL),
            "evidence": f"later turns failed normalization: "
                        f"{[t.normalization_error for t in later_norm]}",
        })
    if seam is not SEAM_POLICY_DENIAL and "EffectRejected" in ledger_kinds and landed:
        secondary.append({"seam": str(SEAM_POLICY_DENIAL),
                          "evidence": "an effect was rejected on a run that also landed a write"})
    # A finish that normalized cleanly but did not terminate the run was
    # refused by completion admission. That is a *completion* observation, not
    # a write-landing seam, and it is recorded separately rather than allowed
    # to contaminate the write attribution.
    finish_turns = [t for t in trace.model_turns if t.emitted_kind == "finish"]
    if finish_turns and trace.terminal_outcome != "completed":
        secondary.append({
            "seam": "completion_admission_refused_finish",
            "evidence": (
                f"a finish normalized on turn {finish_turns[0].turn} but the run "
                f"terminated as {trace.terminal_outcome!r} ({trace.terminal_detail}); "
                "the write itself had already landed"
                if landed else
                f"a finish normalized on turn {finish_turns[0].turn} but the run "
                f"terminated as {trace.terminal_outcome!r}"),
        })
    if "error" in projection_kinds and seam is SEAM_NOT_REPRODUCED:
        secondary.append({"seam": "non_fatal_error_projection",
                          "evidence": json.dumps(
                              [p for p in trace.projections
                               if isinstance(p, Mapping) and p.get("kind") == "error"])})

    trace.seam = seam
    trace.seam_evidence = evidence
    trace.secondary_seams = secondary
    return trace


# --------------------------------------------------------------------------
# Fixtures. P0-FIB is the existing L0 smoke task; the other two are authored
# fresh here precisely so no T-51 L2 holdout member is ever touched.
# --------------------------------------------------------------------------

FIXTURES: Mapping[str, Path] = {
    "P0-FIB": ROOT / "benchmarks" / "ladder" / "l0_triad" / "p0_fib",
    "DX-MULTI": FIXTURE_ROOT / "dx_multifile",
    "DX-GREEN": FIXTURE_ROOT / "dx_greenfield",
}

#: Fixtures authored by this row. Never a holdout member.
FRESH_FIXTURES: tuple[str, ...] = ("DX-MULTI", "DX-GREEN")


def fixture_dir(fixture: str) -> Path:
    try:
        return FIXTURES[fixture]
    except KeyError as exc:  # pragma: no cover - programming error
        raise KeyError(f"unknown probe fixture {fixture!r}") from exc


def materialize(fixture: str, workspace: Path) -> str:
    """Copy the fixture into a candidate workspace; return the brief."""
    source = fixture_dir(fixture)
    workspace.mkdir(parents=True, exist_ok=True)
    for path in sorted(source.iterdir()):
        if path.is_file():
            (workspace / path.name).write_bytes(path.read_bytes())
    return (source / "TASK.md").read_text(encoding="utf-8").strip()


#: The write each fixture must land, as `{relative path: content}`.
EXPECTED_WRITES: Mapping[str, Mapping[str, str]] = {
    "P0-FIB": {
        "fibonacci.py":
            "import sys\n\n\n"
            "def fibonacci(n: int) -> int:\n"
            "    if n < 0:\n"
            "        raise ValueError('n must be non-negative')\n"
            "    a, b = 0, 1\n"
            "    for _ in range(n):\n"
            "        a, b = b, a + b\n"
            "    return a\n\n\n"
            "if __name__ == '__main__':\n"
            "    print(fibonacci(int(sys.argv[1])))\n",
    },
    "DX-MULTI": {
        "formatter.py":
            "def format_row(row: dict) -> str:\n"
            "    return f\"{row['key']}={row['value']}\"\n",
        "ledger.py":
            '"""Ledger row parsing (formatter now lives in formatter.py)."""\n\n'
            "from formatter import format_row\n\n"
            "__all__ = ['parse_row', 'format_row']\n\n\n"
            "def parse_row(line: str) -> dict:\n"
            "    key, _, value = line.partition('=')\n"
            "    return {'key': key.strip(), 'value': value.strip()}\n",
    },
    "DX-GREEN": {
        "retry.py":
            "def retry(fn, attempts: int = 3):\n"
            "    if attempts < 1:\n"
            "        raise ValueError('attempts must be >= 1')\n"
            "    last = None\n"
            "    for _ in range(attempts):\n"
            "        try:\n"
            "            return fn()\n"
            "        except Exception as exc:\n"
            "            last = exc\n"
            "    raise last\n",
    },
}


def canonical_write_tape(
    fixture: str, *, tool_name: str = "patch", finish: bool = True,
) -> list[dict[str, Any]]:
    """A provider tape that writes every expected file, then finishes.

    ``tool_name`` is deliberately a parameter: the declared tool *name* and its
    canonical *verb* differ on this route, and a probe that hardcoded one of
    them could not see the seam between them.
    """
    bodies = [
        provider_body(name=tool_name, arguments={"path": path, "content": content},
                      content=f"Writing {path}.")
        for path, content in EXPECTED_WRITES[fixture].items()
    ]
    if finish:
        bodies.append(provider_body(
            name="finish", arguments={"summary": f"{fixture} write submitted"}))
    return bodies


# --------------------------------------------------------------------------
# The run.
# --------------------------------------------------------------------------

def run_probe(
    label: str,
    fixture: str,
    workspace: Path,
    bodies: Sequence[Mapping[str, Any]],
    *,
    preset: str = "balanced",
    max_turns: int = 8,
    store_path: Path | None = None,
    brief: str | None = None,
) -> ProbeTrace:
    """Drive the real product route once and return an attributed trace."""
    resolved_brief = brief if brief is not None else materialize(fixture, workspace)
    if brief is not None:
        materialize(fixture, workspace)
    preimage = tree_digest(workspace)
    preimage_files = exterior_oracle_digest(workspace)[1]
    store = store_path or (workspace.parent / f"{label}-events.sqlite3")

    model = ProviderTapeModel(bodies, name=label)
    frame = execute_product(
        workspace=workspace,
        brief=resolved_brief,
        preset=preset,
        model=model,
        profile_id="local",
        interactive=False,
        max_turns=max_turns,
        store_path=store,
    )
    receipt = frame.get("result") or {}
    candidate = tree_digest(workspace)
    oracle_digest, oracle_files = exterior_oracle_digest(workspace)
    changed = tuple(sorted(
        path for path in set(preimage_files) | set(oracle_files)
        if preimage_files.get(path) != oracle_files.get(path)))

    trace = ProbeTrace(
        label=label,
        fixture=fixture,
        run_id=receipt.get("runId"),
        workspace=str(workspace),
        preimage_digest=preimage,
        candidate_digest=candidate,
        oracle_digest=oracle_digest,
        oracle_files=oracle_files,
        changed_files=changed,
        terminal_outcome=str(receipt.get("outcome") or "unknown"),
        terminal_detail=str(receipt.get("detail") or ""),
        turns_consumed=int(receipt.get("turns") or 0),
        model_turns=list(model.turns),
        projections=[dict(p) for p in (receipt.get("projections") or ())
                     if isinstance(p, Mapping)],
        ledger=read_ledger(Path(store), str(receipt.get("runId") or "")),
    )
    return attribute(trace)


# --------------------------------------------------------------------------
# MANDATORY controls. Without both, a "no seam identified" result is a
# statement about this instrument, not about the product.
# --------------------------------------------------------------------------

def positive_control(workspace: Path) -> ProbeTrace:
    """A known-good synthetic write MUST land and MUST be observed identically.

    Passing means: the tree changed, the changed set is exactly the expected
    file, and the exterior-oracle digest equals the candidate digest.
    """
    return run_probe(
        "positive-control", "P0-FIB", workspace,
        canonical_write_tape("P0-FIB"),
    )


def positive_control_passed(trace: ProbeTrace) -> bool:
    return (
        trace.candidate_digest != trace.preimage_digest
        and trace.oracle_digest == trace.candidate_digest
        and set(trace.changed_files) == set(EXPECTED_WRITES["P0-FIB"])
        and trace.seam == SEAM_NOT_REPRODUCED
    )


#: Injected seam failures and the seam each MUST be attributed to. Every
#: injection lives in the probe's own tape; no product source is touched to
#: produce one, and each is driven through the same real product route.
NEGATIVE_INJECTIONS: tuple[tuple[str, Seam, str], ...] = (
    ("undeclared-verb", SEAM_MALFORMED_CALL,
     "a well-formed tool call naming a verb the offered declarations do not carry"),
    ("no-tool-call", SEAM_NO_CANONICAL_TOOL,
     "a prose-only provider body with no tool call at all"),
    ("empty-tape", SEAM_RESOURCE_EXHAUSTION,
     "the model is exhausted before it can emit a first valid action"),
)


def _injection_tape(injection: str) -> list[dict[str, Any]]:
    if injection == "undeclared-verb":
        return [
            provider_body(name="fs.write",
                          arguments={"path": "fibonacci.py", "content": "x = 1\n"},
                          content="Injected undeclared-verb write."),
            provider_body(name="finish", arguments={"summary": "injected"}),
        ]
    if injection == "no-tool-call":
        return [provider_body(content="I have written fibonacci.py for you.")]
    if injection == "empty-tape":
        return []
    raise KeyError(f"unknown injection {injection!r}")


def negative_control(root: Path) -> list[tuple[str, Seam, ProbeTrace]]:
    """Injected seam failures MUST each be attributed to that exact seam.

    One injection would only prove the probe can say one word. Three prove it
    discriminates: an undeclared call, a missing call and pre-action
    exhaustion are three different seams and must not collapse into one
    narrative.
    """
    results: list[tuple[str, Seam, ProbeTrace]] = []
    for name, expected, _why in NEGATIVE_INJECTIONS:
        trace = run_probe(f"negative-{name}", "P0-FIB", root / name,
                          _injection_tape(name))
        results.append((name, expected, trace))
    return results


def negative_control_passed(results: Sequence[tuple[str, Seam, ProbeTrace]]) -> bool:
    return all(
        trace.seam == expected
        and trace.candidate_digest == trace.preimage_digest
        for _name, expected, trace in results
    )


# --------------------------------------------------------------------------
# Diagnostic packet.
# --------------------------------------------------------------------------

def run_all(root: Path) -> dict[str, Any]:
    """Run both controls and the three required traces; return the packet."""
    root.mkdir(parents=True, exist_ok=True)
    positive = positive_control(root / "positive")
    negative = negative_control(root / "negative")
    controls_ok = positive_control_passed(positive) and negative_control_passed(negative)

    traces: list[ProbeTrace] = []
    for label, fixture in (("L0", "P0-FIB"), ("multi-file", "DX-MULTI"),
                           ("greenfield", "DX-GREEN")):
        traces.append(run_probe(
            label, fixture, root / label.replace("-", "_"),
            canonical_write_tape(fixture)))

    return {
        "schema": "t130.write-landing-probe/1",
        "controls": {
            "positive": positive.to_dict(),
            "positivePassed": positive_control_passed(positive),
            "negative": [
                {"injection": name, "expectedSeam": str(expected),
                 "observedSeam": str(trace.seam), "trace": trace.to_dict()}
                for name, expected, trace in negative
            ],
            "negativePassed": negative_control_passed(negative),
            "bothPassed": controls_ok,
        },
        "traces": [t.to_dict() for t in traces],
        "attributions": {t.label: str(t.seam) for t in traces},
        "instrumentStatus": (
            "valid" if controls_ok else
            "INCONCLUSIVE INSTRUMENT — a 'no seam identified' result from this "
            "run is a statement about the probe, not about the product"),
        "providerCalls": 0,
        "usdSpent": 0.0,
    }


def _cli(destination: str | None = None) -> int:  # pragma: no cover - manual use
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        packet = run_all(Path(tmp) / "probe")
    text = json.dumps(packet, indent=2, default=str)
    if destination:
        Path(destination).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0 if packet["controls"]["bothPassed"] else 1


if __name__ == "__main__":  # pragma: no cover
    import sys as _sys

    raise SystemExit(_cli(_sys.argv[1] if len(_sys.argv) > 1 else None))
