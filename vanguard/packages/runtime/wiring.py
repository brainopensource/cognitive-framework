"""Port bridges, binding table, and host-side scope (`2.2-C`).

The one evaluator constructor table lives here (`A-05`/`LT-4`). Binding a
judge anywhere else is a second judge.
"""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ..adapters.evaluators.client import EvaluatorClient
from ..adapters.evaluators.unavailable import UnavailableEvaluator
from ..kernel import (
    Constraints,
    Reservation,
    Scope,
    Span,
    Trust,
)
from ..ports.environment import EffectRequest as EnvironmentRequest
from ..ports.environment import ObservationRequest

_FAR_FUTURE = "2099-01-01T00:00:00.000Z"


class CompositionError(RuntimeError):
    """A harness that cannot be wired. Raised while composing, never later."""


@dataclass(frozen=True, slots=True)
class EffectBinding:
    """Verb → adapter factory. The whole of what composition knows about verbs."""

    factory: Callable[["BindingContext"], Any]
    carries_diff: bool = False


@dataclass(frozen=True, slots=True)
class BindingContext:
    """Everything a factory may see. Deliberately small."""

    verb: str
    environment: Any
    repo_path: Path
    emitter: Any = None
    parent_scope: Any = None
    clock: Any = None
    store: Any = None
    parent_episode_id: str | None = None
    max_depth: int = 4
    max_turns: int = 10
    run_child: Any = None
    lineage: tuple[str, ...] = ()
    ledger: Any = None

class _EnvironmentEffect:
    """`kernel.EffectAdapter` over an `EnvironmentAdapter` (`ICD §4`).

    One verb, one environment call, no coordination — which is exactly what
    `ports/kernel.py` says an effect adapter is. The `Result` → `AdapterOutcome`
    translation preserves the one distinction the kernel cannot recover later:
    a failure whose occurrence is *undeterminable* stays undeterminable
    (`F-22`), because resolving it either way manufactures evidence.
    """

    def __init__(self, name: str, environment: Any, call: str) -> None:
        self.name = name
        self._environment = environment
        self._call = call

    def healthy(self) -> bool:
        profile = self._environment.profile()
        return bool(profile.ok)

    def execute(self, request: Any) -> Any:
        from ..kernel import AdapterOutcome, Occurrence

        if self._call == "observe":
            result = self._environment.observe(_observation_of(request))
            occurred = Occurrence.OCCURRED
        else:
            result = self._environment.apply(_effect_of(request))
            occurred = Occurrence.OCCURRED if result.ok else Occurrence.UNDETERMINABLE
        if not result.ok:
            error = result.error
            kind = error.kind if error is not None else "instrument_error"
            return AdapterOutcome(
                "denied" if kind == "denied" else "error",
                # `Occurrence.NOT_OCCURRED` never existed on the enum -- the
                # members are OCCURRED / DID_NOT_OCCUR / UNDETERMINABLE. Every
                # denied, malformed or missing-target effect therefore raised
                # `AttributeError` inside the adapter, which S9 catches and
                # (correctly, given a raising adapter) records as
                # UNDETERMINABLE. So a *known* non-occurrence was reported as
                # unknown: fail-closed, unretryable, and the agent could not
                # learn that its own diff was malformed. That is what made the
                # RF-95 episode escalate instead of correcting itself.
                Occurrence.DID_NOT_OCCUR if kind in {"denied", "invalid_request", "not_found"}
                else occurred,
                {"usd_micros": 0},
                detail=error.message if error is not None else "",
            )
        value = result.value
        digest = getattr(value, "result_digest", None) or getattr(
            value, "metadata", {}).get("digest") or "sha256:" + "0" * 64
        detail = ""
        if hasattr(value, "content") and value.content is not None:
            detail = str(value.content)
        elif hasattr(value, "matches") and value.matches:
            detail = json.dumps(value.matches)
        elif hasattr(value, "files") and value.files:
            detail = json.dumps(value.files)
        elif hasattr(value, "output") and value.output is not None:
            detail = str(value.output)
        # `result.ok` means the *port call* succeeded, not that the command
        # did. An `EffectReceipt` reports `outcome="failed"` on a non-zero
        # exit, and collapsing that to `ok` made a failing test suite
        # indistinguishable from a passing one on the ledger -- which makes an
        # exterior oracle impossible to derive and every run unmeasurable.
        receipt_outcome = getattr(value, "outcome", None)
        status = "ok"
        if isinstance(receipt_outcome, str) and receipt_outcome not in {"", "ok"}:
            status = "error"
        exit_code = getattr(value, "exit_code", None)
        if isinstance(exit_code, int) and not isinstance(exit_code, bool):
            # Carried so a reader can tell *why* it failed without re-running.
            detail = f"[exit {exit_code}] {detail}" if detail else f"[exit {exit_code}]"
        return AdapterOutcome(status, Occurrence.OCCURRED, {"usd_micros": 1},
                              result_digest=digest, detail=detail)


def _observation_of(request: Any) -> ObservationRequest:
    """A kernel request read as an observation. `fs.read` → `read`."""
    action = request.action.split(".")[-1]
    return ObservationRequest(
        action=action,
        path=request.args.get("path"),
        pattern=request.args.get("pattern"),
        args=dict(request.args),
    )


def _effect_of(request: Any) -> EnvironmentRequest:
    """A kernel request read as an environment effect."""
    diff = request.args.get("diff") or request.args.get("patch")
    argv = request.args.get("argv") or request.args.get("command")
    return EnvironmentRequest(
        verb=request.action,
        action="patch" if diff else ("exec" if argv else "write"),
        args=dict(request.args),
        patch=diff,
        command=tuple(argv) if argv else None,
        idempotency_key=getattr(request, "idempotency_key", None),
    )



def _environment_observer(context: BindingContext) -> Any:
    return _EnvironmentEffect(context.verb, context.environment, "observe")


def _environment_effector(context: BindingContext) -> Any:
    return _EnvironmentEffect(context.verb, context.environment, "apply")


def _sandbox_effector(context: BindingContext) -> Any:
    """Compatibility binding for process verbs on the unified worker.

    The name is retained for manifest/test compatibility; the returned adapter
    is the same environment bridge used by filesystem effects, whose concrete
    worker is rootless Bubblewrap-bound at composition time.
    """
    return _environment_effector(context)


def _spawn_effector(context: BindingContext) -> Any:
    """M-6 mediated delegation adapter binding."""
    from .delegation import DelegationResult, SpawnAdapter

    emitter = context.emitter
    if emitter is None and context.ledger is not None:
        emitter = context.ledger.spawn_adapter()
    return SpawnAdapter(
        emitter=emitter,
        parent_scope=context.parent_scope,
        run_child=context.run_child or (
            lambda lineage: DelegationResult(
                ok=True,
                outcome="completed",
                terminal="ok",
                child_episode_id=lineage.child_episode_id,
                result_digest="sha256:" + "0" * 64,
            )
        ),
        clock=context.clock,
        store=context.store,
        parent_episode_id=context.parent_episode_id or "parent-ep",
        max_depth=context.max_depth,
        max_turns=context.max_turns,
        lineage=context.lineage,
    )


#: Verb → adapter. Adding a capability is a row here plus a manifest line
#: (`01 §2`, open/closed); the dispatcher and the loop never change to
#: accommodate one.
DEFAULT_BINDINGS: Mapping[str, EffectBinding] = {
    "fs.read": EffectBinding(_environment_observer),
    "fs.search": EffectBinding(_environment_observer),
    "fs.write": EffectBinding(_environment_effector),
    "patch.apply": EffectBinding(_environment_effector, carries_diff=True),
    "fs.patch": EffectBinding(_environment_effector, carries_diff=True),
    "proc.exec": EffectBinding(_sandbox_effector),
    "agent.spawn": EffectBinding(_spawn_effector),
}


# ---------------------------------------------------------------------------
# Namespaced binding resolution — ADR-0088 Decision 1.7
# ---------------------------------------------------------------------------
#
# A global coding-specific table cannot be the extension authority. Adding a
# domain is registering a provider, not editing a row that every other domain
# has to share. `DEFAULT_BINDINGS` survives as the *code* domain's own rows and
# nothing more: it is one provider among several, not the authority.


class _StaticBindingProvider:
    """One namespace whose verbs are already `EffectBinding` rows."""

    def __init__(self, namespace: str, table: Mapping[str, EffectBinding]) -> None:
        self._namespace = namespace
        self._table = dict(table)

    @property
    def namespace(self) -> str:
        return self._namespace

    @property
    def supported_verbs(self) -> tuple[str, ...]:
        return tuple(sorted(self._table))

    def binding(self, verb: str) -> EffectBinding:
        return self._table[verb]


class _DomainProviderBridge:
    """Adapts an `adapters.bindings` provider to the composition seam.

    The provider owns how a verb executes; composition only needs to know that
    the verb *can* be wired and with what factory. Keeping the bridge here means
    a domain adapter never has to know what an `EffectBinding` is.
    """

    #: Verbs whose approval is descriptor-bound to a diff. A provider may
    #: override by exposing `carries_diff(verb)`.
    _DIFF_SUFFIXES = (".patch", ".apply")

    def __init__(self, provider: Any) -> None:
        self._provider = provider

    @property
    def namespace(self) -> str:
        return self._provider.namespace

    @property
    def supported_verbs(self) -> tuple[str, ...]:
        return tuple(sorted(self._provider.supported_verbs))

    def binding(self, verb: str) -> EffectBinding:
        provider = self._provider
        declared = getattr(provider, "carries_diff", None)
        carries_diff = bool(declared(verb)) if callable(declared) else verb.endswith(
            self._DIFF_SUFFIXES)
        return EffectBinding(
            lambda context: provider.create_adapter(context.verb, context.environment),
            carries_diff=carries_diff,
        )


@dataclass(frozen=True, slots=True)
class BindingResolver:
    """Verb → adapter, resolved from namespaced providers (`ADR-0088 §1.7`).

    Resolution order is explicit rows, then providers in registration order. An
    unresolvable verb denies at composition: a harness that cannot be wired must
    never reach a run.
    """

    explicit: Mapping[str, EffectBinding] = field(default_factory=dict)
    providers: tuple[Any, ...] = ()

    def resolve(self, verb: str) -> EffectBinding | None:
        binding = self.explicit.get(verb)
        if binding is not None:
            return binding
        for provider in self.providers:
            if verb in provider.supported_verbs:
                return provider.binding(verb)
        return None

    def resolve_all(self, verbs: Sequence[str], *, harness: str) -> Mapping[str, EffectBinding]:
        resolved: dict[str, EffectBinding] = {}
        missing: list[str] = []
        for verb in verbs:
            binding = self.resolve(verb)
            if binding is None:
                missing.append(verb)
            else:
                resolved[verb] = binding
        if missing:
            raise CompositionError(
                f"{harness}: no adapter bound for {sorted(missing)}; a harness "
                "that cannot be wired must fail at composition")
        return resolved

    @property
    def namespaces(self) -> tuple[str, ...]:
        return tuple(provider.namespace for provider in self.providers)


def default_providers() -> tuple[Any, ...]:
    """The providers a production composition sees.

    Imported lazily so that composing a harness never depends on a domain
    adapter that this deployment does not ship.
    """
    providers: list[Any] = [_StaticBindingProvider("code", DEFAULT_BINDINGS)]
    try:
        from ..adapters.bindings.table import TableBindingProvider
    except ImportError:  # pragma: no cover - the table domain is optional
        return tuple(providers)
    providers.append(_DomainProviderBridge(TableBindingProvider()))
    return tuple(providers)


def default_resolver(explicit: Mapping[str, EffectBinding] | None = None) -> BindingResolver:
    return BindingResolver(dict(explicit or {}), default_providers())


#: Manifest evaluator name → constructor. Unknown names bind nothing.
#: There is no FakeEvaluator row: absence is inconclusive, not a pass (`M5`).
EVALUATOR_BINDINGS: Mapping[str, type] = {
    "coding-oracle@3": EvaluatorClient,
}


# ---------------------------------------------------------------------------
# The root
# ---------------------------------------------------------------------------


def _bwrap_path(*, which: Callable[[str], str | None] = shutil.which) -> str:
    """Locate rootless Bubblewrap on PATH.

    `N-06` requires containment, not a particular filesystem layout. Asking for
    an absolute path made composition a claim about one distribution: a host
    with bubblewrap under /nix/store, /usr/local/bin or /opt could not compose
    at all. The refusal names the remedy, because "required" without "install
    this" is a dead end for whoever hits it.
    """

    found = which("bwrap")
    if found is None:
        raise CompositionError(
            "rootless Bubblewrap is required for product effects, and no 'bwrap' "
            "was found on PATH. Install bubblewrap (Debian/Ubuntu: "
            "'apt install bubblewrap'; Fedora: 'dnf install bubblewrap'), or put "
            "an existing bwrap on PATH."
        )
    return found


def _reservation_for(budget: Mapping[str, int], effects: int) -> Reservation:
    """One dispatch's share of the frozen budget policy.

    `K-14` re-enters an approved request at S1, and that re-entry has to hold a
    reservation. Inventing one at the call site meant the manifest's ceilings
    did not govern the single dispatch a human had explicitly authorised.

    The share is the run ceiling divided by the effect count the policy itself
    declares, so a manifest that budgets 128 effects reserves 1/128th per
    dispatch. Reserving the *whole* ceiling would be equally derived and
    equally wrong: it denies the second effect of every run.

    A dimension the policy does not name reserves nothing rather than a guess.
    """

    share = max(int(effects), 1)
    return Reservation(
        usd_micros=int(budget.get("usd_micros", 0) or 0) // share,
        millis=int(budget.get("millis", 0) or 0) // share,
    )




def _ceiling_resources(harness: Harness) -> tuple[Mapping[str, Any], ...]:
    """The capability ceiling, as held resources (ADR-0074 §4 / 1.3-B).

    One resource per declared capability's *own* selector -- the manifest is
    the only ceiling this Wave has to intersect against (a separate plugin
    ceiling arrives with the registry in Wave 3; until then `intersect_ceilings`
    over `[harness]` is the identity). A verb that widens beyond its own
    declared selector -- `proc.exec`'s `generic` `proc://...` pattern, say --
    must not be silently covered by a blanket filesystem grant, or the
    classifier's `decide()` check (`domain/selectors/`) is comparing the
    request against authority the manifest never declared.
    """
    seen: dict[str, Mapping[str, Any]] = {}
    for selector_text in harness.capability_ceiling:
        seen.setdefault(selector_text, json.loads(selector_text))
    return tuple(seen.values())


def _scope_for(harness: Harness) -> Scope:
    """The authority surface, entirely from the manifest's declared ceiling."""
    if not harness.capability_ceiling:
        # F-07: empty ceiling authorizes nothing.
        return Scope(
            actions=frozenset(),
            resources=(),
            constraints=Constraints(
                expires_at=_FAR_FUTURE,
                max_uses=0,
                budget_usd_micros=0,
                max_bytes=0,
                risk_ceiling="low",
                max_depth=0,
                network_policy="deny",
            ),
            depth=0,
        )
    risks = tuple(harness.risk_of.values())
    ceiling = "critical" if "critical" in risks else ("high" if "high" in risks else "medium")
    return Scope(
        actions=frozenset(harness.verbs),
        resources=_ceiling_resources(harness),
        constraints=Constraints(
            expires_at=_FAR_FUTURE,
            max_uses=64,
            budget_usd_micros=harness.budget.get("usd_micros", 1_000_000),
            max_bytes=harness.budget.get("bytes", 8_388_608),
            risk_ceiling=ceiling,
            max_depth=4,
            network_policy="deny",
        ),
        depth=0,
    )


#: `TSK-CORE-003` / `K-31`: the declaration a span's trust comes from, made
#: once here rather than as a literal at each call site. `_span_for` is the
#: only place in this module that constructs a `Span`, so no call site can
#: independently judge -- and no call site can mint `Trust.OPERATOR` by
#: writing the enum member itself.
_SOURCE_CLASS_TRUST: Mapping[str, Trust] = {
    "operator_brief": Trust.OPERATOR,
    "tool_result": Trust.UNTRUSTED_EXTERNAL,
}


def _span_for(span_id: str, source_class: str) -> Span:
    return Span(span_id, _SOURCE_CLASS_TRUST[source_class], source_class)


def _operator_span() -> Span:
    """The brief is operator-authored, so it may justify capability widening
    (`M4`, `F-09`). Trust is set by source class at construction (`K-30`)."""
    return _span_for("brief-1", "operator_brief")


def _environment_map(environment: Any, harness: Harness) -> str:
    """L3. Stable within a task, so it is read once and never re-read mid-run."""
    profile = environment.profile()
    if not profile.ok or profile.value is None:
        return f"harness={harness.harness}"
    value = profile.value
    return (f"harness={harness.harness} environment={value.environment_id} "
            f"kind={value.kind} root={value.root} "
            f"capabilities={','.join(sorted(harness.verbs))}")



def _evaluator_from_manifest(harness: Harness, repo: Path) -> Any | None:
    """Bind the manifest's evaluator. Unknown names bind nothing — never a fake."""
    if not harness.evaluators:
        return None
    constructor = EVALUATOR_BINDINGS.get(harness.evaluators[0])
    if constructor is None:
        return None
    if constructor is not EvaluatorClient:
        return UnavailableEvaluator("unsupported_evaluator_binding")
    import base64

    socket_path = os.environ.get("VANGUARD_EVALUATOR_SOCKET")
    image_digest = os.environ.get("VANGUARD_EVALUATOR_IMAGE_DIGEST")
    key_id = os.environ.get("VANGUARD_EVALUATOR_VERDICT_KEY_ID")
    public_key_encoded = os.environ.get("VANGUARD_EVALUATOR_VERDICT_PUBLIC_KEY")
    if not socket_path or not image_digest or not key_id or not public_key_encoded:
        return UnavailableEvaluator("evaluator_peer_unavailable")
    try:
        public_key = base64.b64decode(public_key_encoded, validate=True)
    except Exception:
        return UnavailableEvaluator("evaluator_key_unavailable")
    return constructor(
        socket_path=socket_path,
        expected_uid=10002,
        expected_image_digest=image_digest,
        timeout_seconds=60.0,
        expected_verdict_key_id=key_id,
        expected_verdict_public_key=public_key,
    )

