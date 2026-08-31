"""Repository-intelligence binding provider (`repo.*` verbs).

Without this module the harness can reason about a repository but the *model*
cannot ask it anything: the manifest only exposes `fs.read` and `fs.search`,
so symbol lookup, dependency edges, and test mapping stay invisible to the
worker. This provider closes that gap by publishing them as ordinary verbs.

Every verb here is an **observation**, never a privileged effect. Nothing in
this file writes, executes, or mutates; the sink class in the manifest is
`observation` and the adapter refuses any verb outside its declared set. That
is what keeps a retrieval tool from becoming a second, unaudited path to the
filesystem.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of

__all__ = ["RepoAdapterOutcome", "RepoBindingProvider", "RepoEffectAdapter"]

#: Verbs this provider owns. Kept explicit rather than derived so that adding
#: a capability is a deliberate edit reviewers can see in a diff.
_SUPPORTED_VERBS: tuple[str, ...] = (
    "repo.search",
    "repo.symbol",
    "repo.dependencies",
    "repo.tests_for",
    "repo.map",
)

#: Output ceiling per call. A retrieval verb that can return a megabyte is a
#: context-budget bug waiting to happen; large results become artifacts.
_MAX_INLINE_CHARS = 12_000


@dataclass(frozen=True, slots=True)
class RepoAdapterOutcome:
    """Result envelope matching the shape `CodeEffectAdapter` returns."""

    ok: bool
    verb: str
    value: Mapping[str, Any] = field(default_factory=dict)
    detail: str = ""
    digest: str = ""
    elapsed_ms: int = 0
    truncated: bool = False

    @property
    def actual_cost(self) -> Mapping[str, int]:
        """Observations cost time and bytes, never money or effects."""
        payload = str(self.value)
        return {"millis": self.elapsed_ms, "bytes_": len(payload.encode("utf-8"))}

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok, "verb": self.verb, "value": dict(self.value),
            "detail": self.detail, "digest": self.digest,
            "elapsedMs": self.elapsed_ms, "truncated": self.truncated,
        }


class RepoEffectAdapter:
    """Adapter for one `repo.*` verb over a `RepositoryIntelligence`.

    The intelligence object is supplied by the composition root, not built
    here. Constructing a provider inside an adapter would let a tool call
    decide which repository it reads, which is precisely the authority the
    manifest selector is supposed to hold.
    """

    def __init__(self, verb: str, intelligence: Any, *, call_type: str = "observe") -> None:
        if verb not in _SUPPORTED_VERBS:
            raise ValueError(f"verb {verb!r} is not a repo intelligence verb")
        self.name = verb
        self.verb = verb
        self.call_type = call_type
        self._intelligence = intelligence

    def healthy(self) -> bool:
        """Called as a method by `kernel/dispatch.py:151`.

        Declared as a plain method, not a property: the kernel invokes
        `adapter.healthy()`, and a property returning `bool` would raise
        `'bool' object is not callable` at the one point in the run where an
        adapter is being checked for liveness.
        """
        if self._intelligence is None:
            return False
        available = getattr(self._intelligence, "available", None)
        try:
            return bool(available()) if callable(available) else True
        except Exception:  # noqa: BLE001 - health probes never raise upward
            return False

    def execute(self, request: Any) -> RepoAdapterOutcome:
        """Dispatch one verb. Every failure becomes a value, never an exception.

        The episode loop reduces over adapter outcomes; an exception escaping
        here would end the run as an instrument error for what is, in every
        case below, a recoverable retrieval miss.
        """
        started = time.monotonic()
        args = _arguments_of(request)
        try:
            handler = {
                "repo.search": self._search,
                "repo.symbol": self._symbol,
                "repo.dependencies": self._dependencies,
                "repo.tests_for": self._tests_for,
                "repo.map": self._map,
            }[self.verb]
            value, truncated = handler(args)
            ok = True
            detail = ""
        except KeyError as exc:
            value, truncated, ok = {}, False, False
            detail = f"missing required argument: {exc.args[0]}"
        except Exception as exc:  # noqa: BLE001 - isolation is the contract
            value, truncated, ok = {}, False, False
            detail = f"{type(exc).__name__}: {exc}"[:300]

        elapsed = int((time.monotonic() - started) * 1000)
        return RepoAdapterOutcome(
            ok=ok, verb=self.verb, value=value, detail=detail,
            digest=digest_of({"verb": self.verb, "value": _jsonable(value)}),
            elapsed_ms=elapsed, truncated=truncated,
        )

    # -- verb handlers ---------------------------------------------------

    def _search(self, args: Mapping[str, Any]) -> tuple[Mapping[str, Any], bool]:
        from ...apps.coding_max.intelligence.protocol import SearchQuery

        pattern = _required(args, "pattern")
        query = SearchQuery(
            pattern=str(pattern),
            path=str(args.get("path") or "."),
            glob=str(args["glob"]) if args.get("glob") else None,
            regex=bool(args.get("regex", True)),
            case_sensitive=bool(args.get("case_sensitive", False)),
            max_results=_bounded_int(args.get("max_results"), default=30, high=100),
            context_lines=_bounded_int(args.get("context_lines"), default=2, high=8),
        )
        result = self._intelligence.search(query)
        payload = {
            "hits": [
                {"path": hit.path, "line": hit.line, "text": hit.text}
                for hit in result.hits
            ],
            "paths": list(result.paths),
            "provider": result.provenance.provider,
            "cached": result.provenance.cached,
        }
        return _clip(payload, result.truncated)

    def _symbol(self, args: Mapping[str, Any]) -> tuple[Mapping[str, Any], bool]:
        name = str(_required(args, "name"))
        result = self._intelligence.symbol(name)
        payload = {
            "name": name,
            "definitions": [
                {"path": d.path, "line": d.line, "kind": d.kind.value,
                 "signature": d.signature, "doc": d.docstring_head}
                for d in result.definitions
            ],
            "references": [
                {"path": r.path, "line": r.line, "text": r.text}
                for r in result.references[:30]
            ],
            "provider": result.provenance.provider,
        }
        return _clip(payload, False)

    def _dependencies(self, args: Mapping[str, Any]) -> tuple[Mapping[str, Any], bool]:
        target = str(_required(args, "target"))
        result = self._intelligence.dependencies(target)
        payload = {
            "target": target,
            "imports": list(result.imports),
            "importedBy": list(result.imported_by),
            "external": list(result.external),
            "provider": result.provenance.provider,
        }
        return _clip(payload, False)

    def _tests_for(self, args: Mapping[str, Any]) -> tuple[Mapping[str, Any], bool]:
        target = str(_required(args, "target"))
        result = self._intelligence.tests_for(target)
        payload = {
            "target": target,
            "direct": list(result.direct),
            "sibling": list(result.sibling),
            "commandHint": result.command_hint,
            "provider": result.provenance.provider,
        }
        return _clip(payload, False)

    def _map(self, args: Mapping[str, Any]) -> tuple[Mapping[str, Any], bool]:
        from ...apps.coding_max.repo_map import build_repository_map

        symbols = args.get("focus_symbols") or ()
        repo_map = build_repository_map(
            self._intelligence,
            focus_symbols=tuple(str(s) for s in symbols)[:8],
        )
        rendered = repo_map.render(max_chars=_MAX_INLINE_CHARS // 2)
        return {"map": rendered, "digest": repo_map.digest(),
                "head": repo_map.head, "dirty": repo_map.dirty}, False


class RepoBindingProvider:
    """Namespaced provider for the `repo` domain."""

    def __init__(self, intelligence_factory: Any = None) -> None:
        # A factory rather than an instance: the registry is a process-level
        # singleton while intelligence is per-workspace, so binding one
        # workspace's index into the global registry would leak it across runs.
        self._factory = intelligence_factory

    @property
    def namespace(self) -> str:
        return "repo"

    @property
    def supported_verbs(self) -> tuple[str, ...]:
        return _SUPPORTED_VERBS

    def create_adapter(self, verb: str, environment: Any, **kwargs: Any) -> RepoEffectAdapter:
        if verb not in _SUPPORTED_VERBS:
            raise ValueError(f"Verb {verb!r} not supported by RepoBindingProvider")
        intelligence = kwargs.get("intelligence")
        if intelligence is None:
            intelligence = self._build(environment)
        return RepoEffectAdapter(verb, intelligence)

    def _build(self, environment: Any) -> Any:
        """Derive intelligence from the environment's workspace root."""
        if self._factory is not None:
            return self._factory(environment)
        from ...apps.coding_max.intelligence.composite import CompositeIntelligence

        root = (getattr(environment, "repo_path", None)
                or getattr(environment, "working_dir", None)
                or getattr(environment, "root", None)
                or Path.cwd())
        return CompositeIntelligence(Path(str(root)))


# -- helpers -------------------------------------------------------------


def _arguments_of(request: Any) -> Mapping[str, Any]:
    for attribute in ("args", "arguments", "payload", "params"):
        value = getattr(request, attribute, None)
        if isinstance(value, Mapping):
            return value
    return request if isinstance(request, Mapping) else {}


def _required(args: Mapping[str, Any], key: str) -> Any:
    if key not in args or args[key] in (None, ""):
        raise KeyError(key)
    return args[key]


def _bounded_int(value: Any, *, default: int, high: int, low: int = 1) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(low, min(high, parsed))


def _clip(payload: Mapping[str, Any], truncated: bool) -> tuple[Mapping[str, Any], bool]:
    """Bound inline size, dropping list tails rather than corrupting structure.

    Truncating the serialised string would hand the model malformed JSON; the
    lists are shortened instead so the result stays a valid, if partial, answer.
    """
    rendered = str(payload)
    if len(rendered) <= _MAX_INLINE_CHARS:
        return payload, truncated
    clipped = dict(payload)
    for key, value in list(clipped.items()):
        if isinstance(value, list) and len(value) > 5:
            clipped[key] = value[: max(5, len(value) // 4)]
    clipped["_truncated"] = True
    return clipped, True


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
