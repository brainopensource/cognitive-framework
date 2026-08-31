# full_code_3manifestforge — Wave 5
## Repository Intelligence como Ferramentas do Modelo (`repo.*`)

> **Esta é a lacuna que impedia SWE-Bench Pro.** Até aqui o `CompositeIntelligence`
> era consumido apenas pelo *harness*, para montar mapa e contexto. O **modelo**
> só enxergava `fs.read` e `fs.search`, e portanto precisava reconstruir símbolo,
> dependência e mapeamento de teste na base do grep. Esta wave publica a
> intelligence como verbos de primeira classe.

**Regra de sink:** todo verbo `repo.*` é `observation`, nunca `privileged`.
Nada neste namespace escreve, executa ou muta. Retrieval que exige aprovação é
retrieval que o modelo vai pular.

### Sumário de mudanças

| Arquivo | Ação |
|---|---|
| `vanguard/packages/adapters/bindings/repo.py` | **NOVO** — provider e adapter |
| `vanguard/packages/adapters/bindings/base.py` | **DIFF** — registrar no `default()` |
| `vanguard/packages/adapters/bindings/__init__.py` | **DIFF** — reexportar |
| `vanguard/packages/runtime/wiring.py` | **DIFF** — `default_providers()` |
| `vg-code-max/{symbol,deps,tests,repomap}-tool.json` | **NOVOS** — schemas |
| `vg-code-max/manifest.json`, `vg-code-balanced/manifest.json` | **DIFF** — tools + capabilities |

---

## Cap. 5.1 — `vanguard/packages/adapters/bindings/repo.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **303 linhas**

Provider namespaced para o domínio `repo`. Toda falha vira **valor**, nunca exceção: o episode loop reduz sobre outcomes de adapter, e uma exceção escapando daqui terminaria o run como erro de instrumento por aquilo que é, em todo caso abaixo, um miss de retrieval recuperável.

```python
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
```

---

## Cap. 5.2 — DIFF `vanguard/packages/adapters/bindings/base.py`

Método `DomainBindingRegistry.default`:

```diff
     @classmethod
     def default(cls) -> "DomainBindingRegistry":
         from .code import CodeBindingProvider
+        from .repo import RepoBindingProvider
         from .table import TableBindingProvider
-        return cls([CodeBindingProvider(), TableBindingProvider()])
+        # `repo.*` is observation-only, so adding it to the default registry
+        # widens what a manifest *may* grant without widening what any
+        # existing manifest does grant: capabilities are still declared per
+        # harness, and a pack that names no `repo.` verb is unaffected.
+        return cls([CodeBindingProvider(), RepoBindingProvider(),
+                    TableBindingProvider()])
```

---

## Cap. 5.3 — DIFF `vanguard/packages/adapters/bindings/__init__.py`

```diff
 from .base import BindingProvider, DomainBindingRegistry
 from .code import CodeAdapterOutcome, CodeBindingProvider, CodeEffectAdapter
+from .repo import RepoAdapterOutcome, RepoBindingProvider, RepoEffectAdapter
 from .table import TableAdapterOutcome, TableBindingProvider, TableEffectAdapter
 
 __all__ = [
     "BindingProvider",
     "CodeAdapterOutcome",
     "CodeBindingProvider",
     "CodeEffectAdapter",
     "DomainBindingRegistry",
+    "RepoAdapterOutcome",
+    "RepoBindingProvider",
+    "RepoEffectAdapter",
     "TableAdapterOutcome",
     "TableBindingProvider",
     "TableEffectAdapter",
 ]
```

---

## Cap. 5.4 — DIFF `vanguard/packages/runtime/wiring.py`

**Sem este diff a composição falha fail-closed** com
`CompositionError: no adapter bound for ['repo.dependencies', 'repo.symbol', ...]`.
Isso é o comportamento correto do substrato: um harness que não pode ser
cabeado deve falhar na composição, não no meio do run.

Função `default_providers()`:

```diff
 def default_providers() -> tuple[Any, ...]:
     providers: list[Any] = [_StaticBindingProvider("code", DEFAULT_BINDINGS)]
+    try:
+        # Repository intelligence is observation-only, so registering it here
+        # widens what a manifest *may* declare without widening what any
+        # existing pack does declare. A harness that names no `repo.` verb
+        # resolves exactly as before.
+        from ..adapters.bindings.repo import RepoBindingProvider
+    except ImportError:  # pragma: no cover - the repo domain is optional
+        pass
+    else:
+        providers.append(_DomainProviderBridge(RepoBindingProvider()))
     try:
         from ..adapters.bindings.table import TableBindingProvider
     except ImportError:  # pragma: no cover - the table domain is optional
         return tuple(providers)
     providers.append(_DomainProviderBridge(TableBindingProvider()))
     return tuple(providers)
```

---

## Cap. 5.5 — Tool schemas (ARQUIVOS NOVOS)

As descrições são instruções operacionais, não rótulos. Cada uma diz ao modelo
**quando** usar a ferramenta e **por que ela é melhor** que a alternativa óbvia.

### `vanguard/packages/agency/manifests/vg-code-max/symbol-tool.json`

```json
{"name":"symbol","verb":"repo.symbol","description":"Find where a symbol (function, class, or method) is DEFINED and referenced. Use this instead of grepping for 'def name' or 'class name' — it parses the AST, so it never matches a comment or a string. Single action; do not emit parallel calls.","schema":{"type":"object","properties":{"name":{"type":"string","description":"Exact symbol name, case sensitive"}},"required":["name"],"additionalProperties":false}}
```

### `vanguard/packages/agency/manifests/vg-code-max/deps-tool.json`

```json
{"name":"deps","verb":"repo.dependencies","description":"List what a file imports, what imports it, and which files historically change alongside it. Use before widening a patch: a file with no import edge but high co-change is usually an interface partner. Single action; do not emit parallel calls.","schema":{"type":"object","properties":{"target":{"type":"string","description":"Workspace-relative file path"}},"required":["target"],"additionalProperties":false}}
```

### `vanguard/packages/agency/manifests/vg-code-max/tests-tool.json`

```json
{"name":"tests_for","verb":"repo.tests_for","description":"Find which tests cover a target file and get a runnable pytest command. Use this to pick a targeted test rather than running the whole suite. Single action; do not emit parallel calls.","schema":{"type":"object","properties":{"target":{"type":"string","description":"Workspace-relative file path"}},"required":["target"],"additionalProperties":false}}
```

### `vanguard/packages/agency/manifests/vg-code-max/repomap-tool.json`

```json
{"name":"repo_map","verb":"repo.map","description":"Get a compact map of the repository: languages, modules by size, entrypoints, test roots, and build system. Call this ONCE at the start of an unfamiliar task to orient before searching. Single action; do not emit parallel calls.","schema":{"type":"object","properties":{"paths":{"type":"array","items":{"type":"string"},"description":"Subtrees to cover; defaults to the whole workspace"},"max_entries":{"type":"integer","description":"Maximum modules to list"}},"additionalProperties":false}}
```

---

## Cap. 5.6 — DIFF manifests

### `vg-code-max/manifest.json`

```diff
     "tools": [
       "vg-code-default/read-tool.json",
       "vg-code-default/search-tool.json",
       "vg-code-lex/surgical-patch-tool.json",
       "vg-code-default/patch-tool.json",
-      "vg-code-default/test-tool.json"
+      "vg-code-default/test-tool.json",
+      "vg-code-max/symbol-tool.json",
+      "vg-code-max/deps-tool.json",
+      "vg-code-max/tests-tool.json",
+      "vg-code-max/repomap-tool.json"
     ],
```

```diff
   "capabilities": [
     ...
-    {"verb":"proc.exec","sink":"privileged", ... }
+    {"verb":"proc.exec","sink":"privileged", ... },
+    {"verb":"repo.symbol","sink":"observation",
+     "selector":{"kind":"fs","root":"/workspace","paths":["/workspace"]},"risk":"low"},
+    {"verb":"repo.dependencies","sink":"observation",
+     "selector":{"kind":"fs","root":"/workspace","paths":["/workspace"]},"risk":"low"},
+    {"verb":"repo.tests_for","sink":"observation",
+     "selector":{"kind":"fs","root":"/workspace","paths":["/workspace"]},"risk":"low"},
+    {"verb":"repo.map","sink":"observation",
+     "selector":{"kind":"fs","root":"/workspace","paths":["/workspace"]},"risk":"low"}
   ],
```

### `vg-code-balanced/manifest.json`

Idêntico, **exceto** que `repo.map` é omitido (o preset balanced não constrói
mapa completo) — apenas `symbol`, `deps`, `tests_for` e os três primeiros tools.

`vg-code-fast` **não recebe** nenhum verbo `repo.*`: o fast path existe para
pular exatamente esse custo.

---

## Cap. 5.7 — Bug encontrado e corrigido: `healthy` property vs método

A primeira versão declarava `healthy` como `@property`. O kernel chama
`adapter.healthy()` em `kernel/dispatch.py:151`. Uma property retornando `bool`
levanta `TypeError: 'bool' object is not callable` **exatamente no ponto em que
um adapter é checado para liveness** — ou seja, no primeiro despacho real.

```diff
-    @property
     def healthy(self) -> bool:
+        """Called as a method by `kernel/dispatch.py:151`.
+
+        Declared as a plain method, not a property: the kernel invokes
+        `adapter.healthy()`, and a property returning `bool` would raise
+        `'bool' object is not callable` at the one point in the run where an
+        adapter is being checked for liveness.
+        """
+        if self._intelligence is None:
+            return False
         available = getattr(self._intelligence, "available", None)
         try:
             return bool(available()) if callable(available) else True
         except Exception:  # noqa: BLE001 - health probes never raise upward
             return False
```

---

## Cap. 5.8 — Verificação executada

```
$ python3 -c "from vanguard.packages.adapters.bindings import DomainBindingRegistry; ..."
all verbs: ('fs.patch','fs.read','fs.search','fs.write','patch.apply','proc.exec',
            'repo.dependencies','repo.map','repo.search','repo.symbol','repo.tests_for',
            'table.patch','table.read')
repo.symbol supported: True
provider ns: repo
```

Execução real dos cinco verbos contra o repositório:

```
repo.symbol       healthy=True ok=True {'name':'CheckpointManager',
                    'definitions':[{'path':'vanguard/packages/runtime/checkpoints.py',...
repo.tests_for    healthy=True ok=True {'target':'.../checkpoints.py',
                    'direct':['test/runtime/test_evo11_chec...
repo.search       healthy=True ok=True {'hits':[{'path':'lab/m65_study.py','line':70,...
repo.dependencies healthy=True ok=True {'target':'.../session.py',
                    'imports':['..adapters.stores.repo_index',...
missing arg -> False  "missing required argument: name"
```

Composição dos três presets após o wiring:

```
vg-code-fast       tools=8  verbs=['fs.read','fs.search','patch.apply','proc.exec']
vg-code-balanced   tools=15 verbs=[...,'repo.dependencies','repo.symbol','repo.tests_for']
vg-code-max        tools=17 verbs=[...,'repo.dependencies','repo.map','repo.symbol','repo.tests_for']
                   sinks: repo.symbol=SinkClass.OBSERVATION
```

---

## Cap. 5.9 — Ordem de aplicação

1. Criar `adapters/bindings/repo.py` (Cap. 5.1, integral).
2. Aplicar diff em `adapters/bindings/base.py`.
3. Aplicar diff em `adapters/bindings/__init__.py`.
4. Aplicar diff em `runtime/wiring.py` — **obrigatório antes dos manifests**,
   senão a composição falha fail-closed.
5. Criar os quatro tool schemas.
6. Aplicar diffs de manifest em `vg-code-max` e `vg-code-balanced`.
7. Verificar: `Runtime.compose(...)` para os três presets.

---

## Cap. 5.10 — `vanguard/packages/apps/coding_max/artifacts.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **266 linhas**

Persistência de estado de engenharia (§34, §35, §39). `spec §39` é a regra que molda este módulo: *payloads grandes viram artifacts; eventos carregam hashes/referências*. Um mapa de repositório ou log de teste inline num evento colocaria megabytes num store append-only e tornaria o ledger ilegível.

**Por que `discoveries` é separado de `hypotheses`:** uma descoberta é evidência que sobrevive a um replan; uma hipótese é precisamente o que um replan pode descartar. Colapsar as duas é como um run fica re-derivando fatos que já pagou para aprender.

```python
"""Durable engineering state (`spec §34`, `§35`, `§39`).

`spec §39` is the rule that shapes this module: *large payloads become
artifacts; events carry hashes/references.* A repository map, a full test log,
or a context snapshot inlined into an event would put megabytes into an
append-only store and make the ledger unreadable.

So every payload here goes through the substrate's existing `ArtifactWriter`
(`runtime/artifacts.py`), which is already content-addressed, redacts secrets,
and refuses orphans. This module supplies only the *vocabulary* -- which roles
exist, what each carries, and how a checkpoint references them.

Nothing here writes to the event store. Emission stays where it already is.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of

__all__ = [
    "ArtifactRole",
    "EngineeringState",
    "StateWriter",
]


class ArtifactRole:
    """Roles this harness writes (`spec §34` reference names).

    Strings rather than an enum because `ArtifactWriter.capture` takes a role
    string and the substrate owns that vocabulary; introducing a parallel enum
    would create two spellings of the same concept.
    """

    TASK = "coding_max.task"
    PROFILE = "coding_max.profile"
    REPO_MAP = "coding_max.repo_map"
    PLAN = "coding_max.plan"
    TODO = "coding_max.todo"
    CONTEXT_SNAPSHOT = "coding_max.context"
    HYPOTHESES = "coding_max.hypotheses"
    DISCOVERIES = "coding_max.discoveries"
    FAILED_ATTEMPTS = "coding_max.failed_attempts"
    PATCH = "coding_max.patch"
    TEST_LOG = "coding_max.test_log"
    VERIFICATION = "coding_max.verification"
    REVIEW = "coding_max.review"
    CONTROLLER = "coding_max.controller"


@dataclass
class EngineeringState:
    """The durable working state of one coding run (`spec §34`).

    Held as references wherever the payload is large. `repo_map_ref` is a
    digest, not a map: restoring a run should not require re-reading a
    megabyte of derived structure to learn what file was being edited.
    """

    task: str = ""
    objective: str = ""
    profile_digest: str = ""
    repo_map_ref: str = ""
    plan_digest: str = ""
    todo_digest: str = ""
    hypotheses: tuple[str, ...] = ()
    discoveries: tuple[str, ...] = ()
    inspected_files: tuple[str, ...] = ()
    edited_files: tuple[str, ...] = ()
    failed_attempts: tuple[Mapping[str, Any], ...] = ()
    patch_refs: tuple[str, ...] = ()
    test_log_refs: tuple[str, ...] = ()
    verification_digest: str = ""
    failure_history: tuple[str, ...] = ()
    recovery_history: tuple[str, ...] = ()
    context_epoch: int = 0
    head: str = ""

    # -- mutation (append-only in spirit; the ledger is the real record) --

    def record_hypothesis(self, text: str) -> None:
        if text and text not in self.hypotheses:
            self.hypotheses = self.hypotheses + (text,)

    def record_discovery(self, text: str) -> None:
        """A fact learned about the repository.

        Kept distinct from a hypothesis on purpose: a discovery is evidence
        that survives a replan, while a hypothesis is precisely the thing a
        replan may discard. Collapsing them is how a run keeps re-deriving
        facts it already paid for.
        """
        if text and text not in self.discoveries:
            self.discoveries = self.discoveries + (text,)

    def record_edit(self, path: str) -> None:
        if path and path not in self.edited_files:
            self.edited_files = self.edited_files + (path,)

    def record_inspection(self, path: str) -> None:
        if path and path not in self.inspected_files:
            self.inspected_files = self.inspected_files + (path,)

    def record_failed_attempt(
        self, *, failure_class: str, detail: str, action: str = ""
    ) -> None:
        """`spec §34`: failed attempts are state, not noise.

        Without them a resumed run has no way to avoid repeating an approach
        that already failed, and `RecoveryPolicy`'s "never repeat a spent
        strategy" rule would silently reset at every checkpoint boundary.
        """
        self.failed_attempts = self.failed_attempts + ({
            "failureClass": failure_class, "detail": detail[:500],
            "action": action, "index": len(self.failed_attempts),
        },)
        if failure_class:
            self.failure_history = self.failure_history + (failure_class,)
        if action:
            self.recovery_history = self.recovery_history + (action,)

    # -- serialisation ---------------------------------------------------

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "objective": self.objective,
            "profileDigest": self.profile_digest,
            "repoMapRef": self.repo_map_ref,
            "planDigest": self.plan_digest,
            "todoDigest": self.todo_digest,
            "hypotheses": list(self.hypotheses),
            "discoveries": list(self.discoveries),
            "inspectedFiles": list(self.inspected_files),
            "editedFiles": list(self.edited_files),
            "failedAttempts": [dict(a) for a in self.failed_attempts],
            "patchRefs": list(self.patch_refs),
            "testLogRefs": list(self.test_log_refs),
            "verificationDigest": self.verification_digest,
            "failureHistory": list(self.failure_history),
            "recoveryHistory": list(self.recovery_history),
            "contextEpoch": self.context_epoch,
            "head": self.head,
        }

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())

    @classmethod
    def from_canonical_dict(cls, raw: Mapping[str, Any]) -> "EngineeringState":
        return cls(
            task=str(raw.get("task", "")),
            objective=str(raw.get("objective", "")),
            profile_digest=str(raw.get("profileDigest", "")),
            repo_map_ref=str(raw.get("repoMapRef", "")),
            plan_digest=str(raw.get("planDigest", "")),
            todo_digest=str(raw.get("todoDigest", "")),
            hypotheses=tuple(raw.get("hypotheses", []) or ()),
            discoveries=tuple(raw.get("discoveries", []) or ()),
            inspected_files=tuple(raw.get("inspectedFiles", []) or ()),
            edited_files=tuple(raw.get("editedFiles", []) or ()),
            failed_attempts=tuple(dict(a) for a in raw.get("failedAttempts", []) or ()),
            patch_refs=tuple(raw.get("patchRefs", []) or ()),
            test_log_refs=tuple(raw.get("testLogRefs", []) or ()),
            verification_digest=str(raw.get("verificationDigest", "")),
            failure_history=tuple(raw.get("failureHistory", []) or ()),
            recovery_history=tuple(raw.get("recoveryHistory", []) or ()),
            context_epoch=int(raw.get("contextEpoch", 0) or 0),
            head=str(raw.get("head", "")),
        )

    def render(self, *, max_chars: int = 2000) -> str:
        """Compact briefing for a resumed or replanned turn.

        This is what makes a long task survivable: the worker rejoins with the
        facts and the dead ends, not with a replay of every prior message.
        """
        lines: list[str] = ["# Engineering state"]
        if self.objective:
            lines.append(f"objective: {self.objective}")
        if self.head:
            lines.append(f"head: {self.head[:12]}")
        if self.discoveries:
            lines.append("\n## Established facts")
            lines += [f"  - {d}" for d in self.discoveries[:12]]
        if self.hypotheses:
            lines.append("\n## Open hypotheses")
            lines += [f"  - {h}" for h in self.hypotheses[:8]]
        if self.edited_files:
            lines.append(f"\nedited: {', '.join(self.edited_files[:12])}")
        if self.failed_attempts:
            lines.append("\n## Already tried and failed (do not repeat)")
            for attempt in self.failed_attempts[-6:]:
                lines.append(
                    f"  - [{attempt.get('failureClass')}] "
                    f"{attempt.get('action') or 'attempt'}: {attempt.get('detail')}")
        text = "\n".join(lines)
        if len(text) <= max_chars:
            return text
        return text[:max_chars].rsplit("\n", 1)[0] + "\n  … (state truncated)"


class StateWriter:
    """Persists engineering state through the substrate's `ArtifactWriter`.

    The writer is optional. On the legacy path (`artifacts is None`) every
    method is a no-op returning an empty reference, matching how
    `_LayeredOperator._capture` already behaves in `runtime/session.py`. A run
    without artifact capture must still run; it simply cannot be resumed.
    """

    def __init__(self, artifacts: Any = None) -> None:
        self._artifacts = artifacts
        self._refs: dict[str, str] = {}

    @property
    def available(self) -> bool:
        return self._artifacts is not None

    def capture(
        self,
        role: str,
        payload: Any,
        *,
        turn: int = 0,
        labels: Mapping[str, Any] | None = None,
    ) -> str:
        """Write one payload and return its reference digest."""
        if self._artifacts is None:
            return ""
        body = payload.to_canonical_dict() if hasattr(payload, "to_canonical_dict") \
            else payload
        try:
            ref = self._artifacts.capture(role, body, turn=turn, labels=dict(labels or {}))
        except Exception:  # noqa: BLE001 - a capture failure must not end a run
            return ""
        digest = str(getattr(ref, "digest", "") or getattr(ref, "content_digest", "") or "")
        if digest:
            self._refs[role] = digest
        return digest

    def capture_state(self, state: EngineeringState, *, turn: int = 0) -> str:
        return self.capture(
            ArtifactRole.CONTROLLER, state, turn=turn,
            labels={"stateDigest": state.digest(), "contextEpoch": state.context_epoch},
        )

    def capture_test_log(
        self, verification: Any, *, turn: int = 0
    ) -> str:
        """Test output is the single largest payload a coding run produces.

        Captured whole as an artifact and referenced by digest, so the event
        carries a pointer while the evidence stays recoverable in full --
        which is what `spec §57.10` means by reconstructable from artifacts.
        """
        return self.capture(
            ArtifactRole.TEST_LOG, verification, turn=turn,
            labels={"passed": bool(getattr(verification, "passed", False))},
        )

    def references(self) -> Mapping[str, str]:
        return dict(self._refs)
```

---

## Cap. 5.11 — Por que `failed_attempts` é estado durável

Sem persistir tentativas falhas, um run retomado não tem como evitar repetir
uma abordagem que já falhou — e a regra do `RecoveryPolicy` de *"nunca repetir
estratégia gasta"* silenciosamente reseta a cada fronteira de checkpoint.

```python
    def record_failed_attempt(self, *, failure_class: str, detail: str, action: str = "") -> None:
        self.failed_attempts = self.failed_attempts + ({
            "failureClass": failure_class, "detail": detail[:500],
            "action": action, "index": len(self.failed_attempts),
        },)
```

Isso alimenta o bloco `render()`, que é o que torna uma tarefa longa
sobrevivível: o worker reingressa com os **fatos e os becos sem saída**, não
com um replay de toda mensagem anterior.

```
## Already tried and failed (do not repeat)
  - [WRONG_FILE] expand_search: verification has failed repeatedly...
  - [BAD_PATCH] rollback_and_review: the patch did not apply to current state
```

---

## Cap. 5.12 — `StateWriter` degrada, nunca quebra

O writer é **opcional**. No caminho legado (`artifacts is None`) todo método é
no-op retornando referência vazia, espelhando como `_LayeredOperator._capture`
já se comporta em `runtime/session.py`. Um run sem captura de artifact ainda
precisa rodar; ele apenas não pode ser retomado.

```python
        try:
            ref = self._artifacts.capture(role, body, turn=turn, labels=dict(labels or {}))
        except Exception:  # noqa: BLE001 - a capture failure must not end a run
            return ""
```
