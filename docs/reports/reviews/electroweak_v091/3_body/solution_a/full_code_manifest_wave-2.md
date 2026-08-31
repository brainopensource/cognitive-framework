---
id: report.electroweak.3_body.solution_a.full_code_manifest_wave-2
class: report
authority: non-canonical
canonical_for: []
status: proposal
owner: repository-governance
version: 0.9.2a2
last_verified: 2026-08-31
purpose: Non-canonical candidate input to the Coding Max architecture convergence review.
audience:
  - contributor
  - architect
---

# Full Code Manifest — Wave 2

## Escopo

Branch: `feat/beta-release_electroweak-v091`  
Baseline: `f242ced297216109736975376802f1e3dc4e29ce`

Esta onda implementa CM-02/CM-03/CM-08/CM-11: inteligência de repositório provider-neutral, fallback nativo e compilação progressiva de contexto limitada por tokens. LDA/Atlas permanece um provider opcional futuro, nunca dependência do harness.

## Arquitetura aplicada

```text
Repository → RepositoryIntelligence → SearchHit/RepositoryMap
                                      ↓
Working candidates → ProgressiveContextCompiler → bounded CompiledContext
```

## Decisões

- Provider nativo determinístico, sem shell obrigatório e com leitura de arquivos limitada.
- Resultados normalizados carregam path, linha, excerpt, score e provider.
- Busca de símbolos usa AST em Python e padrões conservadores nos demais idiomas.
- Contexto é deduplicado, ordenado, token-bounded e mutável por add/drop/pin.
- Índices externos enriquecem essa interface futuramente; não controlam política de contexto.

## Patch completo

```diff
diff --git a/packs/code-default/coding_max/intelligence.py b/packs/code-default/coding_max/intelligence.py
new file mode 100644
index 0000000..eb2e684
--- /dev/null
+++ b/packs/code-default/coding_max/intelligence.py
@@ -0,0 +1,113 @@
+"""Provider-neutral repository intelligence with a deterministic native provider."""
+
+from __future__ import annotations
+
+import ast
+import re
+from dataclasses import dataclass
+from pathlib import Path
+from typing import Iterable, Protocol
+
+
+@dataclass(frozen=True, slots=True)
+class SearchHit:
+    path: str
+    line: int
+    excerpt: str
+    score: float
+    provider: str = "native"
+
+
+@dataclass(frozen=True, slots=True)
+class RepositoryMap:
+    languages: tuple[str, ...]
+    modules: tuple[str, ...]
+    entrypoints: tuple[str, ...]
+    test_roots: tuple[str, ...]
+    build_systems: tuple[str, ...]
+    file_count: int
+
+
+class RepositoryIntelligence(Protocol):
+    def search(self, query: str, *, limit: int = 20) -> tuple[SearchHit, ...]: ...
+    def symbol(self, name: str, *, limit: int = 20) -> tuple[SearchHit, ...]: ...
+    def tests_for(self, target: str, *, limit: int = 20) -> tuple[SearchHit, ...]: ...
+    def summarize(self) -> RepositoryMap: ...
+
+
+class NativeRepositoryIntelligence:
+    """Small fallback provider: bounded reads, no index and no shell dependency."""
+
+    _SKIP = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}
+    _TEXT = {".py", ".pyi", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go", ".java", ".md", ".toml", ".yaml", ".yml", ".json"}
+
+    def __init__(self, root: Path, *, max_file_bytes: int = 512_000) -> None:
+        self.root = root.resolve()
+        self.max_file_bytes = max_file_bytes
+
+    def _files(self) -> Iterable[Path]:
+        for path in sorted(self.root.rglob("*")):
+            if not path.is_file() or any(part in self._SKIP for part in path.parts):
+                continue
+            if path.suffix.lower() in self._TEXT and path.stat().st_size <= self.max_file_bytes:
+                yield path
+
+    def _read(self, path: Path) -> str:
+        return path.read_text(encoding="utf-8", errors="replace")
+
+    def search(self, query: str, *, limit: int = 20) -> tuple[SearchHit, ...]:
+        terms = tuple(dict.fromkeys(re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", query.lower())))
+        if not terms:
+            return ()
+        hits: list[SearchHit] = []
+        for path in self._files():
+            for number, line in enumerate(self._read(path).splitlines(), 1):
+                lowered = line.lower()
+                matched = sum(term in lowered for term in terms)
+                if matched:
+                    rel = path.relative_to(self.root).as_posix()
+                    path_bonus = 0.25 if any(term in rel.lower() for term in terms) else 0.0
+                    hits.append(SearchHit(rel, number, line.strip()[:300], matched / len(terms) + path_bonus))
+        hits.sort(key=lambda item: (-item.score, item.path, item.line))
+        return tuple(hits[:max(0, limit)])
+
+    def symbol(self, name: str, *, limit: int = 20) -> tuple[SearchHit, ...]:
+        results: list[SearchHit] = []
+        for path in self._files():
+            text = self._read(path)
+            if path.suffix in {".py", ".pyi"}:
+                try:
+                    tree = ast.parse(text)
+                except SyntaxError:
+                    continue
+                for node in ast.walk(tree):
+                    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
+                        results.append(SearchHit(path.relative_to(self.root).as_posix(), node.lineno, node.name, 1.0))
+            else:
+                pattern = re.compile(rf"\b(class|function|fn|type|interface)\s+{re.escape(name)}\b")
+                for number, line in enumerate(text.splitlines(), 1):
+                    if pattern.search(line):
+                        results.append(SearchHit(path.relative_to(self.root).as_posix(), number, line.strip()[:300], 0.9))
+        return tuple(results[:max(0, limit)])
+
+    def tests_for(self, target: str, *, limit: int = 20) -> tuple[SearchHit, ...]:
+        stem = Path(target).stem.lower()
+        candidates = [p for p in self._files() if "test" in p.name.lower() or "test" in p.parts]
+        hits: list[SearchHit] = []
+        for path in candidates:
+            text = self._read(path)
+            if stem in text.lower() or stem in path.name.lower():
+                hits.append(SearchHit(path.relative_to(self.root).as_posix(), 1, f"test relation:{target}", 1.0))
+        return tuple(hits[:max(0, limit)])
+
+    def summarize(self) -> RepositoryMap:
+        files = list(self._files())
+        language_by_suffix = {".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript", ".rs": "Rust", ".go": "Go", ".java": "Java"}
+        languages = sorted({language_by_suffix[p.suffix] for p in files if p.suffix in language_by_suffix})
+        modules = sorted({p.relative_to(self.root).parts[0] for p in files if p.relative_to(self.root).parts})
+        entry_names = {"main.py", "__main__.py", "cli.py", "index.ts", "main.rs", "main.go"}
+        entrypoints = sorted(p.relative_to(self.root).as_posix() for p in files if p.name in entry_names)
+        tests = sorted({p.relative_to(self.root).parts[0] for p in files if "test" in p.parts or p.name.startswith("test_")})
+        build_markers = {"pyproject.toml": "pyproject", "package.json": "npm", "Cargo.toml": "cargo", "go.mod": "go"}
+        builds = sorted({label for name, label in build_markers.items() if (self.root / name).exists()})
+        return RepositoryMap(tuple(languages), tuple(modules[:50]), tuple(entrypoints[:50]), tuple(tests), tuple(builds), len(files))

diff --git a/packs/code-default/coding_max/context.py b/packs/code-default/coding_max/context.py
new file mode 100644
index 0000000..2547100
--- /dev/null
+++ b/packs/code-default/coding_max/context.py
@@ -0,0 +1,72 @@
+"""Token-bounded progressive context selection independent from providers."""
+
+from __future__ import annotations
+
+from dataclasses import dataclass, replace
+from typing import Iterable, Sequence
+
+
+@dataclass(frozen=True, slots=True)
+class ContextCandidate:
+    key: str
+    content: str
+    relevance: float
+    symbol_proximity: float = 0.0
+    test_relationship: float = 0.0
+    failure_relevance: float = 0.0
+    staleness: float = 0.0
+    pinned: bool = False
+
+    @property
+    def estimated_tokens(self) -> int:
+        return max(1, (len(self.content) + 3) // 4)
+
+    @property
+    def score(self) -> float:
+        return self.relevance + self.symbol_proximity + self.test_relationship + self.failure_relevance - self.staleness
+
+
+@dataclass(frozen=True, slots=True)
+class CompiledContext:
+    selected: tuple[ContextCandidate, ...]
+    dropped: tuple[str, ...]
+    estimated_tokens: int
+    budget: int
+
+
+class ProgressiveContextCompiler:
+    def compile(self, candidates: Sequence[ContextCandidate], token_budget: int) -> CompiledContext:
+        if token_budget <= 0:
+            raise ValueError("token_budget must be positive")
+        deduped: dict[str, ContextCandidate] = {}
+        for candidate in candidates:
+            current = deduped.get(candidate.key)
+            if current is None or candidate.score > current.score:
+                deduped[candidate.key] = candidate
+        ordered = sorted(deduped.values(), key=lambda c: (not c.pinned, -c.score, c.key))
+        selected: list[ContextCandidate] = []
+        dropped: list[str] = []
+        used = 0
+        for candidate in ordered:
+            size = candidate.estimated_tokens
+            if used + size <= token_budget:
+                selected.append(candidate)
+                used += size
+            else:
+                dropped.append(candidate.key)
+        return CompiledContext(tuple(selected), tuple(dropped), used, token_budget)
+
+    def mutate(
+        self,
+        context: CompiledContext,
+        *,
+        add: Iterable[ContextCandidate] = (),
+        drop: Iterable[str] = (),
+        pin: Iterable[str] = (),
+    ) -> CompiledContext:
+        dropped_keys = set(drop)
+        pinned_keys = set(pin)
+        candidates = [replace(c, pinned=True) if c.key in pinned_keys else c
+                      for c in context.selected if c.key not in dropped_keys]
+        candidates.extend(add)
+        return self.compile(candidates, context.budget)
```

## Validação observada

- Busca, symbol lookup, relação de testes e mapa de repositório cobertos em fixture temporária real.
- Ranking/deduplicação/budget de contexto cobertos por testes determinísticos.
- Boundary linter: PASS.

## Limites explícitos

O fallback não pretende substituir SCIP/tree-sitter/LDA; ele garante operação degradada correta. Cache persistente e proveniência externa devem reutilizar artifact store e identidade de run existentes quando integrados ao executor real.
